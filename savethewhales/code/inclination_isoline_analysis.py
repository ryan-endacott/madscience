#!/usr/bin/env python3
"""
Inclination Isoline Geometry Analysis

Tests the "inclino-bathymetric focusing" hypothesis:
  At stranding hotspots, do magnetic inclination isolines run more PARALLEL
  to the coastline than at control sites?

If isolines are parallel to coast → whales following a target inclination
swim ALONG the coast → potential navigation trap.

If isolines cross coast at steep angles → whales navigate toward/away
from shore freely → easy escape.

Metric: angle between inclination isoline direction and coastline direction.
  - 0° = isolines parallel to coast (TRAPPING geometry)
  - 90° = isolines perpendicular to coast (ESCAPE geometry)

Method:
  1. Compute 2D inclination gradient vector at each site (dI/dlat, dI/dlon)
  2. Isoline direction = perpendicular to gradient
  3. Coast direction = perpendicular to transect direction (from site definitions)
  4. Compute angle between isoline direction and coast direction
  5. Compare hotspots vs controls
  6. Generate contour maps for visual verification
"""

import math
import csv
import json
import numpy as np
import ppigrf
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from datetime import datetime
from typing import Dict, List, Tuple


# ============================================================
# SITE DEFINITIONS (same as transect analysis)
# ============================================================

TEST_SITES = [
    # ---- STRANDING HOTSPOTS ----
    {"name": "Farewell Spit, NZ", "lat": -40.51, "lon": 172.77,
     "type": "hotspot", "transect_direction": "north_south",
     "seaward_direction": "north"},
    {"name": "Cape Cod (Wellfleet), USA", "lat": 41.93, "lon": -70.03,
     "type": "hotspot", "transect_direction": "east_west",
     "seaward_direction": "west"},
    {"name": "Golden Bay, NZ", "lat": -40.78, "lon": 172.85,
     "type": "hotspot", "transect_direction": "north_south",
     "seaward_direction": "north"},
    {"name": "Chatham Islands, NZ", "lat": -43.95, "lon": -176.55,
     "type": "hotspot", "transect_direction": "east_west",
     "seaward_direction": "east"},
    {"name": "Orkney (Sanday), Scotland", "lat": 59.25, "lon": -2.57,
     "type": "hotspot", "transect_direction": "east_west",
     "seaward_direction": "east"},
    {"name": "Norfolk, UK", "lat": 52.90, "lon": 1.30,
     "type": "hotspot", "transect_direction": "east_west",
     "seaward_direction": "east"},
    {"name": "Prince Edward Island, Canada", "lat": 46.51, "lon": -63.42,
     "type": "hotspot", "transect_direction": "north_south",
     "seaward_direction": "north"},
    {"name": "Tasmania (west coast), Australia", "lat": -42.18, "lon": 145.33,
     "type": "hotspot", "transect_direction": "east_west",
     "seaward_direction": "west"},

    # ---- CONTROL SITES ----
    {"name": "Dutch Wadden Sea", "lat": 53.41, "lon": 6.12,
     "type": "control", "transect_direction": "north_south",
     "seaward_direction": "north"},
    {"name": "Matagorda-Padre Island, TX", "lat": 27.85, "lon": -97.17,
     "type": "control", "transect_direction": "east_west",
     "seaward_direction": "east"},
    {"name": "Banc d'Arguin, Mauritania", "lat": 20.22, "lon": -16.28,
     "type": "control", "transect_direction": "east_west",
     "seaward_direction": "west"},
    {"name": "Norwegian Coast (Tromso)", "lat": 69.60, "lon": 18.90,
     "type": "control", "transect_direction": "east_west",
     "seaward_direction": "west"},
    {"name": "Portuguese Coast", "lat": 41.10, "lon": -8.60,
     "type": "control", "transect_direction": "east_west",
     "seaward_direction": "west"},
    {"name": "South African Coast (False Bay)", "lat": -34.40, "lon": 18.40,
     "type": "control", "transect_direction": "north_south",
     "seaward_direction": "south"},
    {"name": "Japanese Coast (Choshi)", "lat": 35.70, "lon": 140.85,
     "type": "control", "transect_direction": "east_west",
     "seaward_direction": "east"},
]


def compute_inclination(lon: float, lat: float,
                        ref_date: datetime = datetime(2010, 1, 1)) -> float:
    """Compute IGRF-14 magnetic inclination at a point."""
    Be, Bn, Bu = ppigrf.igrf(lon, lat, 0, ref_date)
    Be, Bn, Bu = float(np.squeeze(Be)), float(np.squeeze(Bn)), float(np.squeeze(Bu))
    H = math.sqrt(Be**2 + Bn**2)
    I = math.degrees(math.atan2(-Bu, H))
    return I


def compute_inclination_grid(center_lat: float, center_lon: float,
                              half_extent_deg: float = 1.0,
                              n_points: int = 41) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Compute inclination on a 2D grid around a center point."""
    lats = np.linspace(center_lat - half_extent_deg,
                       center_lat + half_extent_deg, n_points)
    lons = np.linspace(center_lon - half_extent_deg,
                       center_lon + half_extent_deg, n_points)

    lon_grid, lat_grid = np.meshgrid(lons, lats)
    incl_grid = np.zeros_like(lon_grid)

    ref_date = datetime(2010, 1, 1)
    for i in range(n_points):
        for j in range(n_points):
            incl_grid[i, j] = compute_inclination(lon_grid[i, j], lat_grid[i, j], ref_date)

    return lat_grid, lon_grid, incl_grid


def compute_gradient_2d(site: Dict, step_km: float = 5.0) -> Dict:
    """
    Compute 2D inclination gradient at a site using central differences.
    Returns gradient components in geographic coordinates (dI/dN, dI/dE)
    in deg/km, plus the isoline direction.
    """
    lat, lon = site['lat'], site['lon']

    # Step sizes in degrees
    dlat = step_km / 111.32
    dlon = step_km / (111.32 * math.cos(math.radians(lat)))

    # Central differences
    I_N = compute_inclination(lon, lat + dlat)
    I_S = compute_inclination(lon, lat - dlat)
    I_E = compute_inclination(lon + dlon, lat)
    I_W = compute_inclination(lon - dlon, lat)

    dI_dN = (I_N - I_S) / (2 * step_km)  # deg/km northward
    dI_dE = (I_E - I_W) / (2 * step_km)  # deg/km eastward

    # Gradient magnitude and direction
    grad_mag = math.sqrt(dI_dN**2 + dI_dE**2)
    grad_azimuth = math.degrees(math.atan2(dI_dE, dI_dN))  # degrees from north, CW positive

    # Isoline direction = perpendicular to gradient (two possibilities, take one)
    isoline_azimuth = (grad_azimuth + 90) % 360

    return {
        'dI_dN': dI_dN,
        'dI_dE': dI_dE,
        'grad_magnitude': grad_mag,
        'grad_azimuth': grad_azimuth,
        'isoline_azimuth': isoline_azimuth,
    }


def coast_azimuth(site: Dict) -> float:
    """
    Estimate coastline azimuth from transect definition.
    Coast runs perpendicular to the transect direction.
    """
    if site['transect_direction'] == 'north_south':
        # Transect runs N-S, coast runs approximately E-W
        return 90.0  # East
    else:
        # Transect runs E-W, coast runs approximately N-S
        return 0.0  # North


def angle_between_azimuths(az1: float, az2: float) -> float:
    """
    Compute the acute angle between two azimuths (0-90°).
    Handles the fact that isolines have no inherent direction
    (parallel in both directions).
    """
    diff = abs(az1 - az2) % 360
    if diff > 180:
        diff = 360 - diff
    if diff > 90:
        diff = 180 - diff
    return diff


def analyze_site(site: Dict) -> Dict:
    """Full analysis for one site."""
    name = site['name']

    # 2D gradient
    grad = compute_gradient_2d(site)

    # Coast direction
    coast_az = coast_azimuth(site)

    # Angle between isoline and coast
    iso_coast_angle = angle_between_azimuths(grad['isoline_azimuth'], coast_az)

    result = {
        'site_name': name,
        'site_type': site['type'],
        'lat': site['lat'],
        'lon': site['lon'],
        'inclination_at_center': compute_inclination(site['lon'], site['lat']),
        'grad_dI_dN_deg_per_km': round(grad['dI_dN'], 8),
        'grad_dI_dE_deg_per_km': round(grad['dI_dE'], 8),
        'grad_magnitude_deg_per_km': round(grad['grad_magnitude'], 8),
        'grad_azimuth_deg': round(grad['grad_azimuth'], 2),
        'isoline_azimuth_deg': round(grad['isoline_azimuth'], 2),
        'coast_azimuth_deg': coast_az,
        'isoline_coast_angle_deg': round(iso_coast_angle, 2),
    }

    return result


def generate_contour_maps(sites: List[Dict], results: List[Dict]):
    """Generate inclination contour maps for all sites."""
    n_sites = len(sites)
    cols = 3
    rows = math.ceil(n_sites / cols)

    fig, axes = plt.subplots(rows, cols, figsize=(6 * cols, 5 * rows))
    axes = axes.flatten()

    for idx, (site, result) in enumerate(zip(sites, results)):
        ax = axes[idx]

        # Compute grid (smaller extent for faster computation)
        lat_grid, lon_grid, incl_grid = compute_inclination_grid(
            site['lat'], site['lon'], half_extent_deg=0.5, n_points=21
        )

        # Contour plot
        n_contours = 15
        cs = ax.contour(lon_grid, lat_grid, incl_grid, levels=n_contours,
                        colors='blue', linewidths=0.8, alpha=0.7)
        ax.clabel(cs, inline=True, fontsize=6, fmt='%.2f°')

        # Mark site center
        ax.plot(site['lon'], site['lat'], 'r*', markersize=12, zorder=5)

        # Draw gradient arrow (points toward steepest inclination increase)
        grad_scale = 0.3  # visual scale
        grad = result
        dx = grad['grad_dI_dE_deg_per_km'] / grad['grad_magnitude_deg_per_km'] * grad_scale
        dy = grad['grad_dI_dN_deg_per_km'] / grad['grad_magnitude_deg_per_km'] * grad_scale
        ax.annotate('', xy=(site['lon'] + dx, site['lat'] + dy),
                    xytext=(site['lon'], site['lat']),
                    arrowprops=dict(arrowstyle='->', color='red', lw=2))

        # Draw coast direction line
        coast_az_rad = math.radians(result['coast_azimuth_deg'])
        cx = math.sin(coast_az_rad) * grad_scale
        cy = math.cos(coast_az_rad) * grad_scale
        ax.plot([site['lon'] - cx, site['lon'] + cx],
                [site['lat'] - cy, site['lat'] + cy],
                'g-', linewidth=3, alpha=0.6, label='Coast')

        # Title with key metric
        angle = result['isoline_coast_angle_deg']
        color = 'red' if angle < 30 else ('orange' if angle < 60 else 'green')
        ax.set_title(f"{site['name']}\n"
                     f"({site['type'].upper()}) "
                     f"Iso-Coast angle: {angle:.1f}°",
                     fontsize=9, color=color, fontweight='bold')

        ax.set_xlabel('Longitude')
        ax.set_ylabel('Latitude')
        ax.set_aspect(1.0 / math.cos(math.radians(site['lat'])))

    # Hide unused axes
    for idx in range(n_sites, len(axes)):
        axes[idx].set_visible(False)

    plt.tight_layout()
    plt.savefig('data/inclination_isoline_maps.png', dpi=150, bbox_inches='tight')
    print(f"Contour maps saved to data/inclination_isoline_maps.png")
    plt.close()


def main():
    print("=" * 60)
    print("  INCLINATION ISOLINE GEOMETRY ANALYSIS")
    print("  Testing: do isolines run parallel to coast at hotspots?")
    print(f"  Model: IGRF-14 via ppigrf | Date: 2010-01-01")
    print(f"  Run: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 60)

    results = []
    for site in TEST_SITES:
        r = analyze_site(site)
        results.append(r)
        angle = r['isoline_coast_angle_deg']
        tag = "PARALLEL" if angle < 30 else ("OBLIQUE" if angle < 60 else "PERPENDICULAR")
        print(f"  {r['site_name']:<35} {r['site_type']:<9} "
              f"angle={angle:5.1f}°  [{tag}]  "
              f"I={r['inclination_at_center']:+.2f}°  "
              f"|∇I|={r['grad_magnitude_deg_per_km']:.6f}")

    # ---- Save results ----
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
    csv_file = f"data/inclination_isoline_analysis_{timestamp}.csv"
    json_file = f"data/inclination_isoline_analysis_{timestamp}.json"

    fieldnames = sorted(results[0].keys())
    with open(csv_file, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    with open(json_file, 'w') as f:
        json.dump({
            'metadata': {
                'model': 'IGRF-14',
                'hypothesis': 'Inclination isolines parallel to coast create navigation traps',
                'metric': 'Acute angle between isoline direction and coastline direction',
                'interpretation': '0° = parallel (trapping), 90° = perpendicular (escape)',
                'reference_date': '2010-01-01',
                'run_date': datetime.now().isoformat(),
            },
            'results': results,
        }, f, indent=2)

    print(f"\nResults saved to {csv_file}")
    print(f"Results saved to {json_file}")

    # ---- Statistical analysis ----
    hotspots = [r for r in results if r['site_type'] == 'hotspot']
    controls = [r for r in results if r['site_type'] == 'control']

    h_angles = [r['isoline_coast_angle_deg'] for r in hotspots]
    c_angles = [r['isoline_coast_angle_deg'] for r in controls]

    h_mean = sum(h_angles) / len(h_angles)
    c_mean = sum(c_angles) / len(c_angles)
    h_var = sum((x - h_mean)**2 for x in h_angles) / max(len(h_angles) - 1, 1)
    c_var = sum((x - c_mean)**2 for x in c_angles) / max(len(c_angles) - 1, 1)
    h_sd = math.sqrt(h_var)
    c_sd = math.sqrt(c_var)

    se = math.sqrt(h_var / len(h_angles) + c_var / len(c_angles))
    t_stat = (h_mean - c_mean) / se if se > 0 else 0
    df = len(h_angles) + len(c_angles) - 2

    print(f"\n{'='*60}")
    print("  RESULTS")
    print("=" * 60)

    print(f"\n  Isoline-Coast Angle (0°=parallel/trapping, 90°=perpendicular/escape):")
    print(f"\n  HOTSPOTS (n={len(h_angles)}):")
    for r in hotspots:
        print(f"    {r['site_name']:<35} {r['isoline_coast_angle_deg']:5.1f}°")
    print(f"    {'Mean:':<35} {h_mean:5.1f}° (SD={h_sd:.1f})")

    print(f"\n  CONTROLS (n={len(c_angles)}):")
    for r in controls:
        print(f"    {r['site_name']:<35} {r['isoline_coast_angle_deg']:5.1f}°")
    print(f"    {'Mean:':<35} {c_mean:5.1f}° (SD={c_sd:.1f})")

    print(f"\n  --- Statistical Test ---")
    print(f"  Hotspot mean: {h_mean:.1f}°  Control mean: {c_mean:.1f}°")
    print(f"  Difference: {h_mean - c_mean:+.1f}°")
    print(f"  Welch's t = {t_stat:.3f}  (df~{df})")
    print(f"  |t| > 2.16 → p < 0.05")

    significant = abs(t_stat) > 2.16

    print(f"\n{'='*60}")
    print("  INTERPRETATION")
    print("=" * 60)

    if significant and h_mean < c_mean:
        print(f"\n  *** HYPOTHESIS SUPPORTED ***")
        print(f"  Hotspots have significantly MORE PARALLEL isolines")
        print(f"  (mean {h_mean:.1f}° vs {c_mean:.1f}°, t={t_stat:.3f})")
        print(f"  This is consistent with magnetic navigation trapping.")
    elif significant and h_mean > c_mean:
        print(f"\n  *** HYPOTHESIS CONTRADICTED ***")
        print(f"  Hotspots have MORE PERPENDICULAR isolines (opposite of prediction)")
        print(f"  (mean {h_mean:.1f}° vs {c_mean:.1f}°, t={t_stat:.3f})")
    else:
        print(f"\n  Isoline-coast angle is NOT significantly different (t={t_stat:.3f})")
        print(f"  Hotspot mean={h_mean:.1f}°, Control mean={c_mean:.1f}°")
        print(f"  At IGRF resolution, isoline geometry does NOT distinguish")
        print(f"  stranding sites from controls.")
        print(f"\n  NOTE: IGRF captures only large-scale field (>~3000km wavelength).")
        print(f"  Local crustal anomalies (10-100km scale) could create the")
        print(f"  isoline curvature predicted by the hypothesis but are invisible")
        print(f"  to IGRF. Testing with aeromagnetic survey data would be needed.")

    # ---- Also compute gradient magnitude comparison ----
    h_mags = [r['grad_magnitude_deg_per_km'] for r in hotspots]
    c_mags = [r['grad_magnitude_deg_per_km'] for r in controls]
    hm_mean = sum(h_mags) / len(h_mags)
    cm_mean = sum(c_mags) / len(c_mags)

    print(f"\n  --- Supplementary: Gradient Magnitude ---")
    print(f"  Hotspot mean |∇I| = {hm_mean:.6f} deg/km")
    print(f"  Control mean |∇I| = {cm_mean:.6f} deg/km")
    print(f"  (For reference only — magnitude wasn't the hypothesis)")

    # ---- Generate contour maps ----
    print(f"\n  Generating contour maps...")
    generate_contour_maps(TEST_SITES, results)

    print(f"\n{'='*60}")
    return results


if __name__ == "__main__":
    results = main()
