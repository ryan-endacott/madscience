#!/usr/bin/env python3
"""
Crustal Magnetic Anomaly Analysis at Whale Stranding Sites

Uses EMAG2v3 data (~3.7km resolution) to test whether local crustal
magnetic anomalies create navigation traps at stranding hotspots.

This is the analysis that IGRF could NOT do — IGRF only sees the smooth
core field at >3000km wavelength. EMAG2v3 captures the crustal anomalies
from volcanic rocks, mineral deposits, and geological structures at
2-arc-minute (~3.7km) resolution.

Key metrics:
1. Anomaly variability (standard deviation) — more complex field = harder navigation
2. Anomaly gradient magnitude — steeper gradients = stronger navigational cues/confusion
3. Gradient direction relative to coastline — do anomaly gradients push toward shore?
4. Anomaly contour curvature — do contours create funnels toward shore?
"""

import json
import math
import csv
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from datetime import datetime
from typing import Dict, List


def load_site_data(json_path: str = "data/external/emag2v3_site_extracts.json") -> List[Dict]:
    with open(json_path) as f:
        return json.load(f)


def points_to_grid(points: List[Dict], center_lat: float, center_lon: float,
                   extent_deg: float = 1.0) -> tuple:
    """Convert scattered points to a regular grid via nearest-neighbor."""
    if not points:
        return None, None, None

    lats = sorted(set(round(p['lat'], 4) for p in points))
    lons = sorted(set(round(p['lon'], 4) for p in points))

    lat_arr = np.array(lats)
    lon_arr = np.array(lons)

    grid = np.full((len(lats), len(lons)), np.nan)
    lat_idx = {round(l, 4): i for i, l in enumerate(lats)}
    lon_idx = {round(l, 4): i for i, l in enumerate(lons)}

    for p in points:
        li = lat_idx.get(round(p['lat'], 4))
        lo = lon_idx.get(round(p['lon'], 4))
        if li is not None and lo is not None:
            grid[li, lo] = p['anomaly_nT']

    return lat_arr, lon_arr, grid


def compute_gradient_stats(lat_arr, lon_arr, grid, center_lat, center_lon,
                           coast_azimuth_deg: float) -> Dict:
    """Compute gradient statistics from the anomaly grid."""
    if grid is None or np.all(np.isnan(grid)):
        return {}

    # Grid spacing in km
    dlat_km = 111.32 * (lat_arr[1] - lat_arr[0]) if len(lat_arr) > 1 else 3.7
    dlon_km = 111.32 * math.cos(math.radians(center_lat)) * (lon_arr[1] - lon_arr[0]) if len(lon_arr) > 1 else 3.7

    # Compute gradients (nT/km)
    grad_lat, grad_lon = np.gradient(grid, dlat_km, dlon_km)

    # Gradient magnitude
    grad_mag = np.sqrt(grad_lat**2 + grad_lon**2)

    # Mask NaN
    valid_mag = grad_mag[~np.isnan(grad_mag)]
    valid_anom = grid[~np.isnan(grid)]

    if len(valid_mag) == 0:
        return {}

    # Focus on inner region (±0.5° from center) for site-specific stats
    lat_mask = (lat_arr >= center_lat - 0.5) & (lat_arr <= center_lat + 0.5)
    lon_mask = (lon_arr >= center_lon - 0.5) & (lon_arr <= center_lon + 0.5)
    inner = grid[np.ix_(lat_mask, lon_mask)]
    inner_grad_mag = grad_mag[np.ix_(lat_mask, lon_mask)]
    inner_valid = inner[~np.isnan(inner)]
    inner_grad_valid = inner_grad_mag[~np.isnan(inner_grad_mag)]

    # Gradient direction at center (average of inner region)
    inner_grad_lat = grad_lat[np.ix_(lat_mask, lon_mask)]
    inner_grad_lon = grad_lon[np.ix_(lat_mask, lon_mask)]
    mean_grad_lat = np.nanmean(inner_grad_lat)
    mean_grad_lon = np.nanmean(inner_grad_lon)
    grad_azimuth = math.degrees(math.atan2(mean_grad_lon, mean_grad_lat)) % 360

    # Angle between anomaly gradient and coast-perpendicular
    # Coast-perpendicular = coast_azimuth + 90
    coast_perp = (coast_azimuth_deg + 90) % 360
    grad_coast_angle = abs(grad_azimuth - coast_perp) % 360
    if grad_coast_angle > 180:
        grad_coast_angle = 360 - grad_coast_angle
    if grad_coast_angle > 90:
        grad_coast_angle = 180 - grad_coast_angle

    # Anomaly "complexity" — how much the field varies locally
    # High complexity = more confusing for navigation
    return {
        'anomaly_mean_nT': round(float(np.nanmean(inner_valid)), 2) if len(inner_valid) > 0 else None,
        'anomaly_std_nT': round(float(np.nanstd(inner_valid)), 2) if len(inner_valid) > 0 else None,
        'anomaly_range_nT': round(float(np.nanmax(inner_valid) - np.nanmin(inner_valid)), 2) if len(inner_valid) > 0 else None,
        'gradient_mean_nT_per_km': round(float(np.nanmean(inner_grad_valid)), 4) if len(inner_grad_valid) > 0 else None,
        'gradient_max_nT_per_km': round(float(np.nanmax(inner_grad_valid)), 4) if len(inner_grad_valid) > 0 else None,
        'gradient_std_nT_per_km': round(float(np.nanstd(inner_grad_valid)), 4) if len(inner_grad_valid) > 0 else None,
        'mean_grad_azimuth_deg': round(grad_azimuth, 2),
        'grad_coast_angle_deg': round(grad_coast_angle, 2),
        'n_inner_points': int(len(inner_valid)),
    }


def get_coast_azimuth(site: Dict) -> float:
    """Get coast direction from site name (same logic as isoline analysis)."""
    # Sites with N-S transects have E-W coasts (azimuth ~90°)
    ns_sites = ["Farewell Spit", "Golden Bay", "Prince Edward", "Dutch Wadden", "South Africa"]
    for ns in ns_sites:
        if ns in site['name']:
            return 90.0
    return 0.0  # E-W transects have N-S coasts


def generate_anomaly_maps(sites: List[Dict], results: List[Dict]):
    """Generate crustal anomaly maps with gradient arrows for all sites."""
    n = len(sites)
    cols = 3
    rows = math.ceil(n / cols)

    fig, axes = plt.subplots(rows, cols, figsize=(7 * cols, 5.5 * rows))
    axes = axes.flatten()

    for idx, (site, result) in enumerate(zip(sites, results)):
        ax = axes[idx]
        points = site['points']
        if not points:
            ax.text(0.5, 0.5, 'No data', transform=ax.transAxes, ha='center')
            continue

        lat_arr, lon_arr, grid = points_to_grid(
            points, site['center_lat'], site['center_lon'])

        if grid is None:
            continue

        # Plot anomaly field
        vmax = max(abs(np.nanmin(grid)), abs(np.nanmax(grid)))
        vmax = min(vmax, 300)  # Cap for better color contrast
        im = ax.pcolormesh(lon_arr, lat_arr, grid,
                           cmap='RdBu_r', vmin=-vmax, vmax=vmax,
                           shading='auto')

        # Add contour lines
        try:
            cs = ax.contour(lon_arr, lat_arr, grid, levels=15,
                           colors='black', linewidths=0.5, alpha=0.5)
            ax.clabel(cs, inline=True, fontsize=5, fmt='%.0f')
        except Exception:
            pass

        # Mark center
        ax.plot(site['center_lon'], site['center_lat'],
                'k*', markersize=10, zorder=5)

        # Gradient arrows (subsample)
        dlat_km = 111.32 * (lat_arr[1] - lat_arr[0]) if len(lat_arr) > 1 else 3.7
        dlon_km = 111.32 * math.cos(math.radians(site['center_lat'])) * (lon_arr[1] - lon_arr[0]) if len(lon_arr) > 1 else 3.7
        grad_lat, grad_lon = np.gradient(grid, dlat_km, dlon_km)

        step = max(1, len(lat_arr) // 8)
        lat_sub = lat_arr[::step]
        lon_sub = lon_arr[::step]
        U = grad_lon[::step, ::step]
        V = grad_lat[::step, ::step]
        ax.quiver(lon_sub, lat_sub, U, V, scale=200, alpha=0.4,
                  color='black', width=0.003)

        plt.colorbar(im, ax=ax, label='Anomaly (nT)', shrink=0.8)

        # Title
        std = result.get('anomaly_std_nT', '?')
        gmax = result.get('gradient_max_nT_per_km', '?')
        color = 'red' if site['type'] == 'hotspot' else 'green'
        ax.set_title(f"{site['name']}\n"
                     f"({site['type'].upper()}) "
                     f"σ={std} nT, ∇max={gmax} nT/km",
                     fontsize=9, color=color, fontweight='bold')
        ax.set_xlabel('Lon')
        ax.set_ylabel('Lat')
        ax.set_aspect(1.0 / math.cos(math.radians(site['center_lat'])))

    for idx in range(n, len(axes)):
        axes[idx].set_visible(False)

    plt.tight_layout()
    outpath = 'data/crustal_anomaly_maps.png'
    plt.savefig(outpath, dpi=150, bbox_inches='tight')
    print(f"Maps saved to {outpath}")
    plt.close()


def main():
    print("=" * 60)
    print("  CRUSTAL MAGNETIC ANOMALY ANALYSIS")
    print("  EMAG2v3 data — 2 arc-minute (~3.7km) resolution")
    print(f"  Run: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 60)

    sites = load_site_data()
    results = []

    for site in sites:
        coast_az = get_coast_azimuth(site)
        lat_arr, lon_arr, grid = points_to_grid(
            site['points'], site['center_lat'], site['center_lon'])

        stats = compute_gradient_stats(
            lat_arr, lon_arr, grid,
            site['center_lat'], site['center_lon'],
            coast_az)

        result = {
            'site_name': site['name'],
            'site_type': site['type'],
            'center_lat': site['center_lat'],
            'center_lon': site['center_lon'],
            'n_data_points': len(site['points']),
            'coast_azimuth_deg': coast_az,
            **stats,
        }
        results.append(result)

        std = stats.get('anomaly_std_nT', 'N/A')
        rng = stats.get('anomaly_range_nT', 'N/A')
        gmax = stats.get('gradient_max_nT_per_km', 'N/A')
        print(f"  {site['name']:<35} {site['type']:<9} "
              f"σ={str(std):>7} nT  range={str(rng):>7} nT  "
              f"∇max={str(gmax):>7} nT/km")

    # Save results
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
    csv_file = f"data/crustal_anomaly_analysis_{timestamp}.csv"
    json_file = f"data/crustal_anomaly_analysis_{timestamp}.json"

    fieldnames = sorted(set().union(*(r.keys() for r in results)))
    with open(csv_file, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    with open(json_file, 'w') as f:
        json.dump({
            'metadata': {
                'data_source': 'EMAG2v3 (Meyer et al. 2017)',
                'doi': '10.7289/V5H70CVX',
                'resolution': '2 arc-minutes (~3.7km)',
                'analysis_region': '±1° around each site, stats from ±0.5°',
                'run_date': datetime.now().isoformat(),
            },
            'results': results,
        }, f, indent=2)

    print(f"\nResults saved to {csv_file}")

    # ---- Statistical comparison ----
    hotspots = [r for r in results if r['site_type'] == 'hotspot']
    controls = [r for r in results if r['site_type'] == 'control']

    print(f"\n{'='*60}")
    print("  STATISTICAL COMPARISON: HOTSPOTS vs CONTROLS")
    print("=" * 60)

    metrics = [
        ('anomaly_std_nT', 'Anomaly variability (σ)', 'nT'),
        ('anomaly_range_nT', 'Anomaly range', 'nT'),
        ('gradient_mean_nT_per_km', 'Mean gradient magnitude', 'nT/km'),
        ('gradient_max_nT_per_km', 'Max gradient magnitude', 'nT/km'),
        ('gradient_std_nT_per_km', 'Gradient variability', 'nT/km'),
        ('grad_coast_angle_deg', 'Gradient-coast angle', '°'),
    ]

    for key, label, unit in metrics:
        h_vals = [r[key] for r in hotspots if r.get(key) is not None]
        c_vals = [r[key] for r in controls if r.get(key) is not None]

        if not h_vals or not c_vals:
            continue

        h_mean = sum(h_vals) / len(h_vals)
        c_mean = sum(c_vals) / len(c_vals)
        h_var = sum((x - h_mean)**2 for x in h_vals) / max(len(h_vals) - 1, 1)
        c_var = sum((x - c_mean)**2 for x in c_vals) / max(len(c_vals) - 1, 1)
        h_sd = math.sqrt(h_var)
        c_sd = math.sqrt(c_var)

        se = math.sqrt(h_var/len(h_vals) + c_var/len(c_vals)) if (h_var + c_var) > 0 else 1
        t = (h_mean - c_mean) / se if se > 0 else 0
        sig = "**" if abs(t) > 2.16 else ""

        print(f"\n  {label} ({unit}):")
        print(f"    Hotspots: {h_mean:.2f} (SD={h_sd:.2f}, n={len(h_vals)})")
        print(f"    Controls: {c_mean:.2f} (SD={c_sd:.2f}, n={len(c_vals)})")
        print(f"    t = {t:.3f} {sig}")

    # Generate maps
    print(f"\n  Generating anomaly maps...")
    generate_anomaly_maps(sites, results)

    print(f"\n{'='*60}")
    print("  DONE")
    print("=" * 60)


if __name__ == "__main__":
    main()
