#!/usr/bin/env python3
"""
Whale Stranding Risk Model — Prototype

Computes a monthly stranding risk score for Farewell Spit, NZ by combining:
1. Seasonality (historical month frequency)
2. SST anomaly (warmer = more prey nearshore?)
3. Wind conditions (onshore wind stress)
4. Chlorophyll (proxy for prey/productivity)

Validates against 20 historical stranding events (1993-2026).

Data sources (all free, no auth):
- SST: NOAA OISST v2.1 via ERDDAP
- Chlorophyll: MODIS Aqua monthly via ERDDAP
- Wind: ASCAT monthly via ERDDAP (2009-present)
- Stranding events: compiled from Wikipedia, DOC NZ
"""

import requests
import json
import csv
import math
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from typing import Dict, List, Optional


# ============================================================
# FAREWELL SPIT PARAMETERS
# ============================================================

SITE = {
    'name': 'Farewell Spit, NZ',
    'lat': -40.51,
    'lon': 172.77,
    'lat_range': (-41.0, -40.0),
    'lon_range': (172.0, 173.5),
}

# Historical stranding events (pilot whale, >=5 animals)
STRANDING_EVENTS = [
    # (year, month, count)
    (1993, 11, 90), (1995, 1, 30), (1996, 2, 34), (1998, 12, 28),
    (2005, 12, 123), (2005, 12, 49), (2006, 1, 5),
    (2011, 2, 70), (2012, 1, 90), (2012, 11, 28),
    (2014, 1, 13), (2015, 2, 198), (2017, 2, 416),
    (2022, 2, 49), (2022, 3, 36), (2024, 12, 40),
    (2025, 2, 49), (2026, 1, 15),
]

# Months with strandings (for validation)
STRANDING_MONTHS = set((y, m) for y, m, _ in STRANDING_EVENTS)


def fetch_erddap_monthly(dataset_id: str, variable: str,
                          time_start: str, time_end: str,
                          lat_range: tuple, lon_range: tuple,
                          server: str = "https://coastwatch.pfeg.noaa.gov/erddap") -> List[Dict]:
    """Fetch monthly data from ERDDAP griddap."""
    url = (f"{server}/griddap/{dataset_id}.json?"
           f"{variable}[({time_start}):1:({time_end})]"
           f"[({lat_range[0]}):1:({lat_range[1]})]"
           f"[({lon_range[0]}):1:({lon_range[1]})]")

    resp = requests.get(url, timeout=60)
    resp.raise_for_status()
    data = resp.json()
    cols = data['table']['columnNames']
    return [dict(zip(cols, row)) for row in data['table']['rows']]


def fetch_sst_monthly(year_start: int = 2003, year_end: int = 2025) -> Dict[tuple, float]:
    """Fetch monthly mean SST from OISST. Returns {(year, month): mean_sst}."""
    print("  Fetching SST data...", flush=True)
    result = {}

    for year in range(year_start, year_end + 1):
        for month in range(1, 13):
            day = 15
            date_str = f"{year}-{month:02d}-{day:02d}T12:00:00Z"

            try:
                url = (f"https://coastwatch.pfeg.noaa.gov/erddap/griddap/"
                       f"ncdcOisst21Agg_LonPM180.json?"
                       f"sst[({date_str}):1:({date_str})]"
                       f"[(0.0):1:(0.0)]"
                       f"[({SITE['lat_range'][0]}):1:({SITE['lat_range'][1]})]"
                       f"[({SITE['lon_range'][0]}):1:({SITE['lon_range'][1]})]")
                resp = requests.get(url, timeout=15)
                if resp.status_code == 200:
                    data = resp.json()
                    vals = [r[-1] for r in data['table']['rows']
                            if r[-1] is not None]
                    if vals:
                        result[(year, month)] = np.mean(vals)
            except Exception:
                pass

    print(f"  Got SST for {len(result)} months")
    return result


def fetch_chlorophyll_monthly(year_start: int = 2003, year_end: int = 2025) -> Dict[tuple, float]:
    """Fetch monthly mean chlorophyll from MODIS."""
    print("  Fetching chlorophyll data...", flush=True)
    result = {}

    for year in range(year_start, year_end + 1):
        for month in range(1, 13):
            date_str = f"{year}-{month:02d}-16T00:00:00Z"

            try:
                url = (f"https://coastwatch.pfeg.noaa.gov/erddap/griddap/"
                       f"erdMH1chlamday.json?"
                       f"chlorophyll[({date_str}):1:({date_str})]"
                       f"[({SITE['lat_range'][0]}):1:({SITE['lat_range'][1]})]"
                       f"[({SITE['lon_range'][0]}):1:({SITE['lon_range'][1]})]")
                resp = requests.get(url, timeout=15)
                if resp.status_code == 200:
                    data = resp.json()
                    vals = [r[-1] for r in data['table']['rows']
                            if r[-1] is not None]
                    if vals:
                        result[(year, month)] = np.mean(vals)
            except Exception:
                pass

    print(f"  Got chlorophyll for {len(result)} months")
    return result


def compute_seasonality_score(month: int) -> float:
    """Historical probability of stranding by month (from all Farewell Spit events)."""
    month_counts = {}
    for _, m, _ in STRANDING_EVENTS:
        month_counts[m] = month_counts.get(m, 0) + 1

    total = sum(month_counts.values())
    return month_counts.get(month, 0) / total


def compute_risk_scores(sst_data: Dict, chl_data: Dict) -> List[Dict]:
    """Compute monthly risk scores and compare to actual strandings."""

    # Compute monthly climatology for SST and chlorophyll
    sst_by_month = {}
    chl_by_month = {}
    for (y, m), v in sst_data.items():
        sst_by_month.setdefault(m, []).append(v)
    for (y, m), v in chl_data.items():
        chl_by_month.setdefault(m, []).append(v)

    sst_clim = {m: np.mean(vals) for m, vals in sst_by_month.items()}
    chl_clim = {m: np.mean(vals) for m, vals in chl_by_month.items()}

    results = []
    all_years = sorted(set(y for y, _ in sst_data.keys()))

    for year in all_years:
        for month in range(1, 13):
            # Seasonality score (0-1)
            season = compute_seasonality_score(month)

            # SST anomaly (warmer than average for this month)
            sst = sst_data.get((year, month))
            sst_anom = (sst - sst_clim.get(month, sst)) if sst else 0
            # Normalize: positive anomaly → higher risk
            sst_score = max(0, min(1, 0.5 + sst_anom / 4.0))

            # Chlorophyll anomaly (higher than average → more prey)
            chl = chl_data.get((year, month))
            chl_anom = (chl - chl_clim.get(month, chl)) if chl else 0
            chl_score = max(0, min(1, 0.5 + chl_anom / 2.0))

            # Combined risk score (weighted)
            risk = (0.50 * season +
                    0.25 * sst_score +
                    0.25 * chl_score)

            had_stranding = (year, month) in STRANDING_MONTHS

            results.append({
                'year': year,
                'month': month,
                'season_score': round(season, 4),
                'sst': round(sst, 2) if sst else None,
                'sst_anomaly': round(sst_anom, 3) if sst else None,
                'sst_score': round(sst_score, 4),
                'chlorophyll': round(chl, 4) if chl else None,
                'chl_anomaly': round(chl_anom, 4) if chl else None,
                'chl_score': round(chl_score, 4),
                'risk_score': round(risk, 4),
                'had_stranding': had_stranding,
            })

    return results


def evaluate_model(results: List[Dict]):
    """Evaluate model performance."""
    stranding_scores = [r['risk_score'] for r in results if r['had_stranding']]
    non_stranding_scores = [r['risk_score'] for r in results if not r['had_stranding']]

    if not stranding_scores or not non_stranding_scores:
        print("  Insufficient data for evaluation")
        return

    s_mean = np.mean(stranding_scores)
    n_mean = np.mean(non_stranding_scores)
    s_sd = np.std(stranding_scores)
    n_sd = np.std(non_stranding_scores)

    # Welch's t-test
    se = math.sqrt(s_sd**2/len(stranding_scores) + n_sd**2/len(non_stranding_scores))
    t = (s_mean - n_mean) / se if se > 0 else 0

    print(f"\n  Stranding months:     mean risk = {s_mean:.3f} (SD={s_sd:.3f}, n={len(stranding_scores)})")
    print(f"  Non-stranding months: mean risk = {n_mean:.3f} (SD={n_sd:.3f}, n={len(non_stranding_scores)})")
    print(f"  Welch's t = {t:.3f}  ({'**SIGNIFICANT**' if abs(t) > 2.0 else 'not significant'})")

    # Simple ROC-like metric: what % of stranding months are above median risk?
    median_risk = np.median([r['risk_score'] for r in results])
    above_median = sum(1 for s in stranding_scores if s > median_risk)
    print(f"  Stranding months above median risk: {above_median}/{len(stranding_scores)} ({100*above_median/len(stranding_scores):.0f}%)")

    # Best threshold
    all_scores = sorted(set(r['risk_score'] for r in results))
    best_f1 = 0
    best_thresh = 0
    for thresh in all_scores:
        tp = sum(1 for r in results if r['risk_score'] >= thresh and r['had_stranding'])
        fp = sum(1 for r in results if r['risk_score'] >= thresh and not r['had_stranding'])
        fn = sum(1 for r in results if r['risk_score'] < thresh and r['had_stranding'])
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0
        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
        if f1 > best_f1:
            best_f1 = f1
            best_thresh = thresh
            best_stats = (tp, fp, fn, precision, recall)

    tp, fp, fn, prec, rec = best_stats
    print(f"\n  Best threshold: {best_thresh:.3f}")
    print(f"  Precision: {prec:.2f}, Recall: {rec:.2f}, F1: {best_f1:.2f}")
    print(f"  True positives: {tp}, False positives: {fp}, False negatives: {fn}")


def plot_results(results: List[Dict]):
    """Generate visualization of risk scores vs actual strandings."""
    fig, axes = plt.subplots(3, 1, figsize=(14, 10), sharex=True)

    years = [r['year'] + (r['month'] - 0.5) / 12 for r in results]
    risks = [r['risk_score'] for r in results]
    strandings = [r['had_stranding'] for r in results]

    # Risk score over time
    ax = axes[0]
    ax.fill_between(years, risks, alpha=0.3, color='orange', label='Risk score')
    ax.plot(years, risks, color='orange', linewidth=0.5)
    for i, (y, r, s) in enumerate(zip(years, risks, strandings)):
        if s:
            ax.axvline(y, color='red', alpha=0.5, linewidth=1.5)
    ax.set_ylabel('Risk Score')
    ax.set_title('Farewell Spit Stranding Risk Model — Prototype')
    ax.legend(['Risk score', 'Actual stranding'])

    # SST
    ax = axes[1]
    sst_vals = [r.get('sst') for r in results]
    ax.plot(years, sst_vals, color='blue', linewidth=0.8)
    ax.set_ylabel('SST (°C)')

    # Chlorophyll
    ax = axes[2]
    chl_vals = [r.get('chlorophyll') for r in results]
    ax.plot(years, chl_vals, color='green', linewidth=0.8)
    ax.set_ylabel('Chl-a (mg/m³)')
    ax.set_xlabel('Year')

    plt.tight_layout()
    plt.savefig('data/stranding_risk_farewell_spit.png', dpi=150, bbox_inches='tight')
    print("  Plot saved to data/stranding_risk_farewell_spit.png")
    plt.close()


def main():
    print("=" * 60)
    print("  STRANDING RISK MODEL — FAREWELL SPIT PROTOTYPE")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 60)

    # Fetch environmental data
    sst_data = fetch_sst_monthly(2003, 2024)
    chl_data = fetch_chlorophyll_monthly(2003, 2024)

    # Compute risk scores
    print("\n  Computing risk scores...")
    results = compute_risk_scores(sst_data, chl_data)

    # Save results
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
    csv_file = f"data/stranding_risk_scores_{timestamp}.csv"
    fieldnames = sorted(results[0].keys())
    with open(csv_file, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)
    print(f"  Results saved to {csv_file}")

    # Evaluate
    print("\n" + "=" * 60)
    print("  MODEL EVALUATION")
    print("=" * 60)
    evaluate_model(results)

    # Plot
    print("\n  Generating plots...")
    plot_results(results)

    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()
