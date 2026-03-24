#!/usr/bin/env python3
"""
BGS IGRF-14 Linear Transect Analysis v2 — Local Computation

Computes IGRF-14 magnetic field values locally using ppigrf, then runs
15km linear seaward-to-landward transects at whale stranding hotspots
and control sites.

This resolves the NOAA vs BGS methodology mismatch from May 2025 by:
1. Using the same linear transect geometry as NOAA (15km, 4 points, perpendicular to coast)
2. Using the authoritative IGRF-14 model (same as BGS API)
3. Computing locally — no API needed, no rate limits, reproducible
4. Capturing both total intensity AND inclination gradients
"""

import math
import csv
import json
import numpy as np
import ppigrf
from datetime import datetime
from typing import Dict, List, Tuple, Optional


# ============================================================
# SITE DEFINITIONS
# ============================================================

TEST_SITES = [
    # ---- STRANDING HOTSPOTS ----
    {
        "name": "Farewell Spit, NZ",
        "lat": -40.51, "lon": 172.77,
        "type": "hotspot",
        "strandings": "30+ mass events, world's largest hotspot",
        "transect_direction": "north_south",
        "seaward_direction": "north",
    },
    {
        "name": "Cape Cod (Wellfleet), USA",
        "lat": 41.93, "lon": -70.03,
        "type": "hotspot",
        "strandings": "Regular mass strandings",
        "transect_direction": "east_west",
        "seaward_direction": "west",
    },
    {
        "name": "Golden Bay, NZ",
        "lat": -40.78, "lon": 172.85,
        "type": "hotspot",
        "strandings": "Adjacent to Farewell Spit, frequent events",
        "transect_direction": "north_south",
        "seaward_direction": "north",
    },
    {
        "name": "Chatham Islands, NZ",
        "lat": -43.95, "lon": -176.55,
        "type": "hotspot",
        "strandings": "Multiple mass strandings",
        "transect_direction": "east_west",
        "seaward_direction": "east",
    },
    {
        "name": "Orkney (Sanday), Scotland",
        "lat": 59.25, "lon": -2.57,
        "type": "hotspot",
        "strandings": "77 pilot whales, 2023",
        "transect_direction": "east_west",
        "seaward_direction": "east",
    },
    {
        "name": "Norfolk, UK",
        "lat": 52.90, "lon": 1.30,
        "type": "hotspot",
        "strandings": "Historical stranding hotspot",
        "transect_direction": "east_west",
        "seaward_direction": "east",
    },
    {
        "name": "Prince Edward Island, Canada",
        "lat": 46.51, "lon": -63.42,
        "type": "hotspot",
        "strandings": "Documented mass strandings",
        "transect_direction": "north_south",
        "seaward_direction": "north",
    },
    {
        "name": "Tasmania (west coast), Australia",
        "lat": -42.18, "lon": 145.33,
        "type": "hotspot",
        "strandings": "Multiple events, Macquarie Harbour area",
        "transect_direction": "east_west",
        "seaward_direction": "west",
    },

    # ---- CONTROL SITES ----
    {
        "name": "Dutch Wadden Sea",
        "lat": 53.41, "lon": 6.12,
        "type": "control",
        "strandings": "No pilot whale mass strandings",
        "transect_direction": "north_south",
        "seaward_direction": "north",
    },
    {
        "name": "Matagorda-Padre Island, TX",
        "lat": 27.85, "lon": -97.17,
        "type": "control",
        "strandings": "Zero pilot whale mass strandings",
        "transect_direction": "east_west",
        "seaward_direction": "east",
    },
    {
        "name": "Banc d'Arguin, Mauritania",
        "lat": 20.22, "lon": -16.28,
        "type": "control",
        "strandings": "Zero pilot whale mass strandings",
        "transect_direction": "east_west",
        "seaward_direction": "west",
    },
    {
        "name": "Norwegian Coast (Tromso)",
        "lat": 69.60, "lon": 18.90,
        "type": "control",
        "strandings": "No mass strandings",
        "transect_direction": "east_west",
        "seaward_direction": "west",
    },
    {
        "name": "Portuguese Coast",
        "lat": 41.10, "lon": -8.60,
        "type": "control",
        "strandings": "No mass strandings",
        "transect_direction": "east_west",
        "seaward_direction": "west",
    },
    {
        "name": "South African Coast (False Bay)",
        "lat": -34.40, "lon": 18.40,
        "type": "control",
        "strandings": "No mass strandings",
        "transect_direction": "north_south",
        "seaward_direction": "south",
    },
    {
        "name": "Japanese Coast (Choshi)",
        "lat": 35.70, "lon": 140.85,
        "type": "control",
        "strandings": "No mass strandings",
        "transect_direction": "east_west",
        "seaward_direction": "east",
    },
]


def compute_field(lon: float, lat: float,
                  ref_date: datetime = datetime(2010, 1, 1)) -> Dict:
    """Compute IGRF-14 magnetic field at a point. Returns dict with F, I, D, H, Z."""
    Be, Bn, Bu = ppigrf.igrf(lon, lat, 0, ref_date)
    Be, Bn, Bu = float(np.squeeze(Be)), float(np.squeeze(Bn)), float(np.squeeze(Bu))

    H = math.sqrt(Be**2 + Bn**2)
    F = math.sqrt(Be**2 + Bn**2 + Bu**2)
    I = math.degrees(math.atan2(-Bu, H))  # Bu=up, Z=down=-Bu
    D = math.degrees(math.atan2(Be, Bn))

    return {
        'F': round(F, 2),
        'I': round(I, 4),
        'D': round(D, 4),
        'H': round(H, 2),
        'Z': round(-Bu, 2),
        'lat': lat,
        'lon': lon,
    }


def create_transect(site: Dict, transect_km: float = 15.0,
                    n_points: int = 4) -> List[Tuple[float, float, str]]:
    """Create linear transect: A (seaward) to D (landward), centered on site."""
    step_km = transect_km / (n_points - 1)
    labels = [chr(65 + i) for i in range(n_points)]  # A, B, C, D

    offsets_km = [
        -transect_km / 2 + i * step_km for i in range(n_points)
    ]

    points = []
    for offset_km, label in zip(offsets_km, labels):
        if site["transect_direction"] == "east_west":
            deg_per_km = 1.0 / (111.32 * math.cos(math.radians(site["lat"])))
            if site["seaward_direction"] == "west":
                lat, lon = site["lat"], site["lon"] + offset_km * deg_per_km
            else:
                lat, lon = site["lat"], site["lon"] - offset_km * deg_per_km
        else:  # north_south
            deg_per_km = 1.0 / 111.32
            if site["seaward_direction"] == "north":
                lat, lon = site["lat"] - offset_km * deg_per_km, site["lon"]
            else:
                lat, lon = site["lat"] + offset_km * deg_per_km, site["lon"]
        points.append((lat, lon, label))

    return points


def linear_regression(xs, ys):
    """Simple OLS: returns (slope, r_squared)."""
    n = len(xs)
    x_mean = sum(xs) / n
    y_mean = sum(ys) / n
    ss_xy = sum((x - x_mean) * (y - y_mean) for x, y in zip(xs, ys))
    ss_xx = sum((x - x_mean)**2 for x in xs)
    ss_yy = sum((y - y_mean)**2 for y in ys)
    slope = ss_xy / ss_xx if ss_xx > 0 else 0
    r_sq = (ss_xy**2 / (ss_xx * ss_yy)) if (ss_xx * ss_yy) > 0 else 0
    return slope, r_sq


def process_site(site: Dict, transect_km: float = 15.0) -> Dict:
    """Run transect for one site and compute gradients."""
    name = site["name"]
    print(f"\n{'='*55}")
    print(f"  {name} ({site['type'].upper()})")
    print(f"  Center: ({site['lat']:.4f}, {site['lon']:.4f})")
    print(f"  Transect: {transect_km}km {site['transect_direction']}, "
          f"seaward={site['seaward_direction']}")

    points = create_transect(site, transect_km)
    measurements = []

    for lat, lon, label in points:
        field = compute_field(lon, lat)
        field['label'] = label
        measurements.append(field)
        tag = "(Seaward)" if label == 'A' else "(Landward)" if label == chr(64 + len(points)) else ""
        print(f"    {label} {tag:>10}: ({lat:.4f}, {lon:.4f})  "
              f"F={field['F']:.1f}  I={field['I']:.3f}°")

    # Gradients: seaward (A) to landward (D)
    sea = measurements[0]
    land = measurements[-1]

    f_diff = land['F'] - sea['F']
    i_diff = land['I'] - sea['I']
    f_gradient = f_diff / transect_km
    i_gradient = i_diff / transect_km

    # Linear regression through all points
    distances = [i * (transect_km / (len(measurements) - 1)) for i in range(len(measurements))]
    f_slope, f_r2 = linear_regression(distances, [m['F'] for m in measurements])
    i_slope, i_r2 = linear_regression(distances, [m['I'] for m in measurements])

    result = {
        'site_name': name,
        'site_type': site['type'],
        'center_lat': site['lat'],
        'center_lon': site['lon'],
        'transect_km': transect_km,
        'transect_direction': site['transect_direction'],
        'seaward_direction': site['seaward_direction'],
        'F_seaward': sea['F'],
        'F_landward': land['F'],
        'F_diff_nT': round(f_diff, 2),
        'F_gradient_nT_per_km': round(f_gradient, 4),
        'F_regression_slope': round(f_slope, 4),
        'F_regression_r2': round(f_r2, 6),
        'I_seaward': sea['I'],
        'I_landward': land['I'],
        'I_diff_deg': round(i_diff, 4),
        'I_gradient_deg_per_km': round(i_gradient, 6),
        'I_regression_slope': round(i_slope, 6),
        'I_regression_r2': round(i_r2, 6),
        'gradient_direction': 'landward' if f_gradient > 0 else 'seaward',
    }

    sign = "+" if f_gradient > 0 else ""
    print(f"  --> F gradient: {sign}{f_gradient:.4f} nT/km  "
          f"(diff: {sign}{f_diff:.1f} nT, R²={f_r2:.4f})")
    sign_i = "+" if i_gradient > 0 else ""
    print(f"  --> I gradient: {sign_i}{i_gradient:.6f} deg/km  "
          f"(diff: {sign_i}{i_diff:.4f}°)")

    return result


def main():
    print("=" * 60)
    print("  IGRF-14 LINEAR TRANSECT ANALYSIS")
    print("  Local computation via ppigrf (no API needed)")
    print("  15km seaward-to-landward, 4 points, IGRF-14 model")
    print(f"  Reference date: 2010-01-01")
    print(f"  Run date: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 60)

    results = []
    for site in TEST_SITES:
        result = process_site(site)
        results.append(result)

    # ---- Multi-scale analysis ----
    # Also run at 5km and 50km to test scale sensitivity
    print("\n\n" + "=" * 60)
    print("  SCALE SENSITIVITY ANALYSIS")
    print("  Same sites at 5km, 15km, 50km transect lengths")
    print("=" * 60)

    scale_results = []
    for scale in [5.0, 15.0, 50.0]:
        for site in TEST_SITES:
            r = process_site(site, transect_km=scale)
            r['scale_km'] = scale
            scale_results.append(r)

    # ---- Save results ----
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")

    # Main results (15km)
    csv_file = f"data/igrf14_linear_transects_{timestamp}.csv"
    json_file = f"data/igrf14_linear_transects_{timestamp}.json"

    fieldnames = sorted(set().union(*(r.keys() for r in results)))
    with open(csv_file, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    with open(json_file, 'w') as f:
        json.dump({
            'metadata': {
                'model': 'IGRF-14',
                'library': 'ppigrf 2.1.0',
                'transect_km': 15.0,
                'n_points': 4,
                'reference_date': '2010-01-01',
                'run_date': datetime.now().isoformat(),
            },
            'results': results,
        }, f, indent=2)

    # Scale sensitivity results
    scale_csv = f"data/igrf14_scale_sensitivity_{timestamp}.csv"
    scale_fields = sorted(set().union(*(r.keys() for r in scale_results)))
    with open(scale_csv, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=scale_fields)
        writer.writeheader()
        writer.writerows(scale_results)

    print(f"\nResults saved to {csv_file}")
    print(f"Results saved to {json_file}")
    print(f"Scale analysis saved to {scale_csv}")

    # ---- Analysis ----
    print("\n" + "=" * 60)
    print("  15km TRANSECT RESULTS SUMMARY")
    print("=" * 60)

    hotspots = [r for r in results if r['site_type'] == 'hotspot']
    controls = [r for r in results if r['site_type'] == 'control']

    print(f"\n{'Site':<35} {'Type':<9} {'F grad':>10} {'I grad':>12} {'Dir':<9}")
    print("-" * 80)
    for r in results:
        print(f"{r['site_name']:<35} {r['site_type']:<9} "
              f"{r['F_gradient_nT_per_km']:+10.4f} "
              f"{r['I_gradient_deg_per_km']:+12.6f} "
              f"{r['gradient_direction']:<9}")

    h_f = [r['F_gradient_nT_per_km'] for r in hotspots]
    c_f = [r['F_gradient_nT_per_km'] for r in controls]
    h_i = [r['I_gradient_deg_per_km'] for r in hotspots]
    c_i = [r['I_gradient_deg_per_km'] for r in controls]

    def stats(vals):
        n = len(vals)
        mean = sum(vals) / n
        var = sum((x - mean)**2 for x in vals) / max(n - 1, 1)
        return mean, math.sqrt(var), n

    h_f_mean, h_f_sd, h_f_n = stats(h_f)
    c_f_mean, c_f_sd, c_f_n = stats(c_f)
    h_i_mean, h_i_sd, h_i_n = stats(h_i)
    c_i_mean, c_i_sd, c_i_n = stats(c_i)

    print(f"\n--- Total Intensity (F) Gradient ---")
    print(f"  Hotspots: mean={h_f_mean:+.4f} nT/km  SD={h_f_sd:.4f}  n={h_f_n}")
    print(f"  Controls: mean={c_f_mean:+.4f} nT/km  SD={c_f_sd:.4f}  n={c_f_n}")

    # Welch's t-test
    se_f = math.sqrt(h_f_sd**2/h_f_n + c_f_sd**2/c_f_n) if (h_f_sd + c_f_sd) > 0 else 1
    t_f = (h_f_mean - c_f_mean) / se_f
    df_f = h_f_n + c_f_n - 2
    print(f"  Welch's t = {t_f:.3f}  (df~{df_f}, |t|>2.16 ~ p<0.05)")

    print(f"\n--- Inclination (I) Gradient ---")
    print(f"  Hotspots: mean={h_i_mean:+.6f} deg/km  SD={h_i_sd:.6f}  n={h_i_n}")
    print(f"  Controls: mean={c_i_mean:+.6f} deg/km  SD={c_i_sd:.6f}  n={c_i_n}")

    se_i = math.sqrt(h_i_sd**2/h_i_n + c_i_sd**2/c_i_n) if (h_i_sd + c_i_sd) > 0 else 1
    t_i = (h_i_mean - c_i_mean) / se_i
    print(f"  Welch's t = {t_i:.3f}  (df~{df_f}, |t|>2.16 ~ p<0.05)")

    # Scale sensitivity summary
    print(f"\n\n{'='*60}")
    print("  SCALE SENSITIVITY SUMMARY")
    print("=" * 60)
    for scale in [5.0, 15.0, 50.0]:
        sr = [r for r in scale_results if r.get('scale_km') == scale]
        sh = [r for r in sr if r['site_type'] == 'hotspot']
        sc = [r for r in sr if r['site_type'] == 'control']
        hm = sum(r['F_gradient_nT_per_km'] for r in sh) / len(sh) if sh else 0
        cm = sum(r['F_gradient_nT_per_km'] for r in sc) / len(sc) if sc else 0
        hi = sum(r['I_gradient_deg_per_km'] for r in sh) / len(sh) if sh else 0
        ci = sum(r['I_gradient_deg_per_km'] for r in sc) / len(sc) if sc else 0
        print(f"\n  {scale:.0f}km transects:")
        print(f"    F gradient: hotspots={hm:+.4f}  controls={cm:+.4f}  diff={hm-cm:+.4f}")
        print(f"    I gradient: hotspots={hi:+.6f}  controls={ci:+.6f}  diff={hi-ci:+.6f}")

    # Key conclusions
    print(f"\n\n{'='*60}")
    print("  INTERPRETATION")
    print("=" * 60)

    if abs(t_f) > 2.16:
        print(f"\n  Total intensity gradient IS significantly different (t={t_f:.3f})")
        if h_f_mean > c_f_mean:
            print("  Hotspots have HIGHER F gradients (field rises more steeply landward)")
        else:
            print("  Hotspots have LOWER F gradients")
    else:
        print(f"\n  Total intensity gradient is NOT significantly different (t={t_f:.3f})")
        print("  F gradient alone does NOT distinguish stranding sites from controls.")

    if abs(t_i) > 2.16:
        print(f"\n  Inclination gradient IS significantly different (t={t_i:.3f})")
        if h_i_mean > c_i_mean:
            print("  Hotspots have STEEPER inclination increase landward")
        else:
            print("  Hotspots have STEEPER inclination decrease landward")
    else:
        print(f"\n  Inclination gradient is NOT significantly different (t={t_i:.3f})")
        print("  Inclination gradient alone does NOT distinguish stranding sites.")

    print("\n" + "=" * 60)
    return results, scale_results


if __name__ == "__main__":
    results, scale_results = main()
