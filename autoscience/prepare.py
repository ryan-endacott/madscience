#!/usr/bin/env python3
"""
AutoScience Data Preparation

Loads cached environmental data and computes derived features
(lags, anomalies, rates of change) for the hypothesis evaluator.
"""

import json
import numpy as np
from typing import Dict, List, Tuple


# Stranding events at Farewell Spit (year, month) during data coverage period
STRANDING_EVENTS = {
    (2005, 12), (2006, 1), (2011, 2), (2012, 1), (2012, 11),
    (2014, 1), (2015, 2), (2017, 2), (2022, 2), (2022, 3), (2024, 12),
}

# Base variables in the cache
BASE_VARS = ['sst', 'chlorophyll', 'wind_u', 'wind_v', 'wind_speed', 'wind_direction']


def load_cache(path: str = "../savethewhales/data/external/autoscience_cache.json") -> Dict:
    with open(path) as f:
        return json.load(f)


def compute_features(cache: Dict) -> List[Dict]:
    """
    Compute all features for each month.
    Returns a list of dicts, one per month, with:
    - Base variables (sst, chlorophyll, wind_*)
    - Lags (sst_lag1, sst_lag2, sst_lag3, etc.)
    - Monthly climatology anomalies (sst_anom, chlorophyll_anom, etc.)
    - Rates of change (sst_delta, chlorophyll_delta, etc.)
    - Month number and season flags
    - Whether a stranding occurred
    """
    monthly = cache['monthly']
    keys = sorted(monthly.keys())  # "2003-01", "2003-02", ...

    # First pass: compute climatology (monthly means)
    climatology = {}
    for var in BASE_VARS:
        by_month = {}
        for k in keys:
            month = int(k.split('-')[1])
            val = monthly[k].get(var)
            if val is not None:
                by_month.setdefault(month, []).append(val)
        climatology[var] = {m: np.mean(vals) for m, vals in by_month.items()}

    # Second pass: build feature vectors
    records = []
    for i, k in enumerate(keys):
        year = int(k.split('-')[0])
        month = int(k.split('-')[1])

        record = {
            'key': k,
            'year': year,
            'month': month,
            'had_stranding': (year, month) in STRANDING_EVENTS,
        }

        # Season features
        record['is_summer'] = 1.0 if month in (11, 12, 1, 2, 3) else 0.0
        record['month_sin'] = np.sin(2 * np.pi * month / 12)
        record['month_cos'] = np.cos(2 * np.pi * month / 12)

        # Seasonality risk (historical frequency)
        month_strand_count = sum(1 for y, m in STRANDING_EVENTS if m == month)
        record['season_risk'] = month_strand_count / len(STRANDING_EVENTS)

        # Base variables
        for var in BASE_VARS:
            val = monthly[k].get(var)
            record[var] = val

            # Anomaly from climatology
            if val is not None and month in climatology[var]:
                record[f'{var}_anom'] = val - climatology[var][month]
            else:
                record[f'{var}_anom'] = None

        # Derived wind features
        u = record.get('wind_u')
        v = record.get('wind_v')
        if u is not None and v is not None:
            # Northerly component (positive = wind FROM north = pushing into Golden Bay)
            record['wind_northerly'] = -v  # negative v = wind from north
            # Onshore component for Farewell Spit (north-facing coast)
            record['wind_onshore'] = -v  # same as northerly for this site

        # Lags (1, 2, 3 months back)
        for lag in [1, 2, 3]:
            if i >= lag:
                prev_key = keys[i - lag]
                for var in BASE_VARS:
                    prev_val = monthly[prev_key].get(var)
                    record[f'{var}_lag{lag}'] = prev_val
                    # Lagged anomaly
                    if prev_val is not None:
                        prev_month = int(prev_key.split('-')[1])
                        if prev_month in climatology[var]:
                            record[f'{var}_anom_lag{lag}'] = prev_val - climatology[var][prev_month]
                        else:
                            record[f'{var}_anom_lag{lag}'] = None
                    else:
                        record[f'{var}_anom_lag{lag}'] = None

                    # Lagged wind derived features
                    prev_u = monthly[prev_key].get('wind_u')
                    prev_v = monthly[prev_key].get('wind_v')
                    if prev_u is not None and prev_v is not None:
                        record[f'wind_northerly_lag{lag}'] = -prev_v
                        record[f'wind_onshore_lag{lag}'] = -prev_v
            else:
                for var in BASE_VARS:
                    record[f'{var}_lag{lag}'] = None
                    record[f'{var}_anom_lag{lag}'] = None
                record[f'wind_northerly_lag{lag}'] = None
                record[f'wind_onshore_lag{lag}'] = None

        # Rate of change (current - previous month)
        if i >= 1:
            prev_key = keys[i - 1]
            for var in BASE_VARS:
                curr = monthly[k].get(var)
                prev = monthly[prev_key].get(var)
                if curr is not None and prev is not None:
                    record[f'{var}_delta'] = curr - prev
                else:
                    record[f'{var}_delta'] = None
        else:
            for var in BASE_VARS:
                record[f'{var}_delta'] = None

        # Multi-month averages (2-month and 3-month trailing)
        for window in [2, 3]:
            if i >= window - 1:
                for var in ['sst', 'chlorophyll', 'wind_speed', 'wind_northerly']:
                    if var == 'wind_northerly':
                        vals = []
                        for j in range(window):
                            prev_v = monthly[keys[i - j]].get('wind_v')
                            if prev_v is not None:
                                vals.append(-prev_v)
                    else:
                        vals = [monthly[keys[i - j]].get(var)
                                for j in range(window)]
                        vals = [v for v in vals if v is not None]
                    if vals:
                        record[f'{var}_avg{window}m'] = np.mean(vals)
                    else:
                        record[f'{var}_avg{window}m'] = None

        records.append(record)

    return records


def get_feature_names(records: List[Dict]) -> List[str]:
    """Get all numeric feature names."""
    skip = {'key', 'year', 'month', 'had_stranding'}
    names = set()
    for r in records:
        for k, v in r.items():
            if k not in skip and isinstance(v, (int, float)) and v is not None:
                names.add(k)
    return sorted(names)


if __name__ == "__main__":
    cache = load_cache()
    records = compute_features(cache)

    print(f"Total months: {len(records)}")
    print(f"Stranding months: {sum(1 for r in records if r['had_stranding'])}")
    print(f"Features per month: {len(get_feature_names(records))}")
    print(f"\nAvailable features:")
    for f in get_feature_names(records):
        vals = [r[f] for r in records if r.get(f) is not None]
        if vals:
            print(f"  {f:<30} n={len(vals):>3}  range=[{min(vals):.3f}, {max(vals):.3f}]")
