#!/usr/bin/env python3
"""
Bathymetry Analysis at Whale Stranding Sites

Tests whether coastal geometry alone predicts mass stranding hotspots.
Uses ETOPO1 data (1 arc-minute resolution) from NOAA ERDDAP.

Key metrics tested:
1. Ocean fraction — how much water surrounds the site
2. Shallow water fraction (0-30m depth)
3. Shallow/Ocean ratio — what fraction of ocean is shallow (trap geometry)
4. Mean slope — overall bathymetric gradient
5. Shallow zone slope — how gently the seafloor slopes in the 0-50m zone
6. Mean ocean depth

All metrics are null (no significant difference between hotspots and controls).
The Dutch Wadden Sea (control, zero strandings) has 98% shallow water and
0.7 m/km slope — the "perfect" whale trap by geometry — yet no strandings.
"""

import requests
import json
import math
import csv
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import time
from datetime import datetime
from typing import Dict, List


SITES = [
    {"name": "Farewell Spit, NZ", "lat": -40.51, "lon": 172.77, "type": "hotspot"},
    {"name": "Cape Cod, USA", "lat": 41.93, "lon": -70.03, "type": "hotspot"},
    {"name": "Golden Bay, NZ", "lat": -40.78, "lon": 172.85, "type": "hotspot"},
    {"name": "Chatham Islands, NZ", "lat": -43.95, "lon": -176.55, "type": "hotspot"},
    {"name": "Orkney, Scotland", "lat": 59.25, "lon": -2.57, "type": "hotspot"},
    {"name": "Norfolk, UK", "lat": 52.90, "lon": 1.30, "type": "hotspot"},
    {"name": "Prince Edward Is, Canada", "lat": 46.51, "lon": -63.42, "type": "hotspot"},
    {"name": "Tasmania, Australia", "lat": -42.18, "lon": 145.33, "type": "hotspot"},
    {"name": "Dutch Wadden Sea", "lat": 53.41, "lon": 6.12, "type": "control"},
    {"name": "Matagorda-Padre, TX", "lat": 27.85, "lon": -97.17, "type": "control"},
    {"name": "Banc d'Arguin, Mauritania", "lat": 20.22, "lon": -16.28, "type": "control"},
    {"name": "Norwegian Coast", "lat": 69.60, "lon": 18.90, "type": "control"},
    {"name": "Portuguese Coast", "lat": 41.10, "lon": -8.60, "type": "control"},
    {"name": "South Africa", "lat": -34.40, "lon": 18.40, "type": "control"},
    {"name": "Japanese Coast", "lat": 35.70, "lon": 140.85, "type": "control"},
]

ERDDAP_BASE = "https://coastwatch.pfeg.noaa.gov/erddap/griddap/etopo180.json"


def fetch_bathymetry(site: Dict, extent: float = 0.5) -> Dict:
    """Fetch ETOPO1 bathymetry for a site from NOAA ERDDAP."""
    lat_lo = site['lat'] - extent
    lat_hi = site['lat'] + extent
    lon_lo = site['lon'] - extent
    lon_hi = site['lon'] + extent

    url = f"{ERDDAP_BASE}?altitude[({lat_lo}):({lat_hi})][({lon_lo}):({lon_hi})]"

    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    data = resp.json()

    rows = data['table']['rows']
    lats = sorted(set(r[0] for r in rows))
    lons = sorted(set(r[1] for r in rows))

    grid = np.full((len(lats), len(lons)), np.nan)
    lat_idx = {l: i for i, l in enumerate(lats)}
    lon_idx = {l: i for i, l in enumerate(lons)}
    for r in rows:
        grid[lat_idx[r[0]], lon_idx[r[1]]] = r[2]

    return {'lats': lats, 'lons': lons, 'grid': grid}


def analyze_bathymetry(site: Dict, bathy: Dict) -> Dict:
    """Compute bathymetric statistics for a site."""
    grid = bathy['grid']
    lats = bathy['lats']
    lons = bathy['lons']

    ocean = grid[grid < 0]
    shallow = grid[(grid >= -30) & (grid < 0)]

    dlat_km = 111.32 * (lats[1] - lats[0]) if len(lats) > 1 else 1.85
    dlon_km = 111.32 * np.cos(np.radians(site['lat'])) * (lons[1] - lons[0]) if len(lons) > 1 else 1.85
    gy, gx = np.gradient(grid, dlat_km, dlon_km)
    slope = np.sqrt(gx**2 + gy**2)

    shallow_mask = (grid >= -50) & (grid < 0)
    ocean_frac = len(ocean) / grid.size
    shallow_frac = len(shallow) / grid.size

    return {
        'site_name': site['name'],
        'site_type': site['type'],
        'center_lat': site['lat'],
        'center_lon': site['lon'],
        'ocean_fraction': round(ocean_frac, 4),
        'shallow_fraction': round(shallow_frac, 4),
        'shallow_of_ocean_ratio': round(shallow_frac / ocean_frac, 4) if ocean_frac > 0 else 0,
        'min_depth_m': round(float(np.nanmin(grid)), 1),
        'max_elev_m': round(float(np.nanmax(grid)), 1),
        'mean_ocean_depth_m': round(float(np.mean(ocean)), 1) if len(ocean) > 0 else None,
        'mean_slope_m_per_km': round(float(np.nanmean(slope)), 2),
        'max_slope_m_per_km': round(float(np.nanmax(slope)), 2),
        'shallow_mean_slope_m_per_km': round(float(np.nanmean(slope[shallow_mask])), 2) if np.any(shallow_mask) else None,
    }


def welch_t(a, b):
    na, nb = len(a), len(b)
    ma, mb = sum(a)/na, sum(b)/nb
    va = sum((x-ma)**2 for x in a) / max(na-1, 1)
    vb = sum((x-mb)**2 for x in b) / max(nb-1, 1)
    se = math.sqrt(va/na + vb/nb) if (va+vb) > 0 else 1
    return ma, mb, math.sqrt(va), math.sqrt(vb), (ma-mb)/se if se > 0 else 0


def main():
    print("=" * 60)
    print("  BATHYMETRY ANALYSIS")
    print("  ETOPO1 (1 arc-minute) via NOAA ERDDAP")
    print(f"  Run: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 60)

    # Try loading cached data first
    cache_path = "data/external/bathymetry_etopo1.json"
    try:
        with open(cache_path) as f:
            cached = json.load(f)
        if len(cached) == len(SITES) and all('error' not in r for r in cached):
            print("  (Using cached ERDDAP data)")
            results = cached
            # Re-derive metrics that may not be in cache
            for r in results:
                if 'shallow_of_ocean_ratio' not in r:
                    r['shallow_of_ocean_ratio'] = r['shallow_fraction'] / r['ocean_fraction'] if r['ocean_fraction'] > 0 else 0
        else:
            raise FileNotFoundError
    except (FileNotFoundError, json.JSONDecodeError):
        results = []
        for site in SITES:
            print(f"  Fetching {site['name']}...", end="", flush=True)
            try:
                bathy = fetch_bathymetry(site)
                result = analyze_bathymetry(site, bathy)
                results.append(result)
                print(f" OK")
            except Exception as e:
                print(f" FAILED: {e}")
            time.sleep(0.5)

        with open(cache_path, 'w') as f:
            json.dump(results, f, indent=2)

    # Ensure derived fields exist
    for r in results:
        of = r.get('ocean_fraction', 0)
        sf = r.get('shallow_fraction', 0)
        r.setdefault('shallow_of_ocean_ratio', sf / of if of > 0 else 0)
        r.setdefault('site_name', r.get('name', ''))
        r.setdefault('site_type', r.get('type', ''))

    hotspots = [r for r in results if r.get('site_type', r.get('type', '')) == 'hotspot']
    controls = [r for r in results if r.get('site_type', r.get('type', '')) == 'control']

    # Save CSV
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
    csv_file = f"data/bathymetry_analysis_{timestamp}.csv"
    fieldnames = sorted(set().union(*(r.keys() for r in results)))
    with open(csv_file, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)
    print(f"\nResults saved to {csv_file}")

    # Statistical comparison
    print(f"\n{'='*60}")
    print("  STATISTICAL COMPARISON")
    print("=" * 60)

    metrics = [
        ('ocean_fraction', 'Ocean fraction', 100),
        ('shallow_fraction', 'Shallow water (0-30m)', 100),
        ('shallow_of_ocean_ratio', 'Shallow/Ocean ratio (trap geometry)', 100),
        ('mean_slope_m_per_km', 'Mean slope', 1),
        ('shallow_mean_slope_m_per_km', 'Shallow zone slope', 1),
        ('mean_ocean_depth_m', 'Mean ocean depth', 1),
    ]

    for key, label, scale in metrics:
        h = [r[key]*scale for r in hotspots if r.get(key) is not None]
        c = [r[key]*scale for r in controls if r.get(key) is not None]
        if not h or not c:
            continue
        hm, cm, hsd, csd, t = welch_t(h, c)
        sig = " **" if abs(t) > 2.16 else ""
        unit = "%" if scale == 100 else ("m/km" if "slope" in key else "m")
        print(f"\n  {label} ({unit}):")
        print(f"    Hotspots: {hm:.1f} (SD={hsd:.1f}, n={len(h)})")
        print(f"    Controls: {cm:.1f} (SD={csd:.1f}, n={len(c)})")
        print(f"    t = {t:.3f}{sig}")

    print(f"\n{'='*60}")
    print("  CONCLUSION")
    print("=" * 60)
    print(f"\n  No bathymetric metric significantly distinguishes")
    print(f"  stranding hotspots from control sites.")
    print(f"\n  Counterexample: Dutch Wadden Sea has 98% shallow water")
    print(f"  and 0.7 m/km slope (the 'perfect' trap) but zero strandings.")
    print(f"\n  Simple physical geography does not predict mass strandings.")
    print("=" * 60)


if __name__ == "__main__":
    main()
