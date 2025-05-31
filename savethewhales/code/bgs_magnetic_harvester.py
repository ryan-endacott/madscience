#!/usr/bin/env python3
"""
BGS Magnetic Field Data Harvester
Validates the "Magnetic Uphill Trap" hypothesis across 15 global sites
Using UK BGS Geomagnetic API for IGRF-14 data
"""

import requests
import csv
import time
import math
from datetime import datetime
from typing import List, Tuple, Dict, Optional

# Test sites: mix of known stranding hotspots and control locations
TEST_SITES = [
    # Known stranding hotspots (expect positive gradients)
    ("Farewell Spit, NZ", -40.5, 172.8, "hotspot"),
    ("Cape Cod, USA", 41.7, -70.0, "hotspot"), 
    ("Tasmania, Australia", -40.8, 144.7, "hotspot"),
    ("Norfolk, UK", 52.9, 1.3, "hotspot"),
    ("Golden Bay, NZ", -40.7, 172.7, "hotspot"),
    ("Chatham Islands, NZ", -43.9, -176.5, "hotspot"),
    ("Prince Edward Island, Canada", 46.5, -63.8, "hotspot"),
    ("Orkney Islands, Scotland", 59.0, -3.0, "hotspot"),
    
    # Control sites (expect negative gradients or no strandings)
    ("Dutch Wadden Sea", 53.4, 6.2, "control"),
    ("Norwegian Coast", 69.6, 18.9, "control"),
    ("Chilean Coast", -33.6, -71.6, "control"), 
    ("Portuguese Coast", 41.1, -8.6, "control"),
    ("South African Coast", -34.4, 18.4, "control"),
    ("Japanese Coast", 35.7, 140.1, "control"),
    ("Brazilian Coast", -23.0, -43.2, "control"),
]

class BGSMagneticHarvester:
    """Harvests magnetic field data from BGS API with proper rate limiting"""
    
    def __init__(self):
        self.base_url = "https://geomag.bgs.ac.uk/web_service/GMModels/igrf/14/"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Scientific-Research-Whale-Stranding-Study/1.0'
        })
        
    def get_magnetic_field(self, lat: float, lon: float, date: str = "2010-01-01") -> Optional[Dict]:
        """Get magnetic field data for a single point"""
        params = {
            'latitude': lat,
            'longitude': lon,
            'date': date,
            'altitude': 0,
            'format': 'json'
        }
        
        try:
            response = self.session.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            field = data["geomagnetic-field-model-result"]["field-value"]
            
            return {
                'total_intensity': field["total-intensity"]["value"],
                'inclination': field["inclination"]["value"], 
                'vertical_intensity': field["vertical-intensity"]["value"],
                'latitude': lat,
                'longitude': lon
            }
            
        except requests.RequestException as e:
            print(f"API Error for {lat}, {lon}: {e}")
            return None
        except KeyError as e:
            print(f"Data parsing error for {lat}, {lon}: {e}")
            return None
    
    def generate_transect_points(self, center_lat: float, center_lon: float, 
                               distance_km: float = 50) -> List[Tuple[float, float]]:
        """Generate 8 points around the site for gradient calculation"""
        points = []
        
        # Convert distance to degrees (rough approximation)
        lat_offset = distance_km / 111.0  # 1 degree lat ≈ 111 km
        lon_offset = distance_km / (111.0 * math.cos(math.radians(center_lat)))
        
        # 8 points: 4 cardinal + 4 diagonal directions
        offsets = [
            (lat_offset, 0),      # North
            (-lat_offset, 0),     # South  
            (0, lon_offset),      # East
            (0, -lon_offset),     # West
            (lat_offset/1.4, lon_offset/1.4),    # NE
            (-lat_offset/1.4, lon_offset/1.4),   # SE
            (-lat_offset/1.4, -lon_offset/1.4),  # SW
            (lat_offset/1.4, -lon_offset/1.4),   # NW
        ]
        
        for lat_off, lon_off in offsets:
            points.append((center_lat + lat_off, center_lon + lon_off))
            
        return points
    
    def calculate_gradient(self, measurements: List[Dict]) -> Optional[Dict]:
        """Calculate magnetic gradient from transect measurements"""
        if len(measurements) < 4:
            return None
            
        # Find seaward vs landward points (simplified approach)
        # Sort by distance from center and compare outer vs inner
        center_lat = sum(m['latitude'] for m in measurements) / len(measurements)
        center_lon = sum(m['longitude'] for m in measurements) / len(measurements)
        
        # Calculate distances and sort
        for m in measurements:
            m['distance'] = math.sqrt((m['latitude'] - center_lat)**2 + 
                                    (m['longitude'] - center_lon)**2)
        
        measurements.sort(key=lambda x: x['distance'])
        
        # Compare inner vs outer points for gradient
        inner_points = measurements[:4]
        outer_points = measurements[4:]
        
        if not outer_points:
            outer_points = measurements[2:]
            inner_points = measurements[:2]
        
        inner_avg = sum(m['total_intensity'] for m in inner_points) / len(inner_points)
        outer_avg = sum(m['total_intensity'] for m in outer_points) / len(outer_points)
        
        # Positive gradient = field increases toward shore (landward)
        gradient = inner_avg - outer_avg
        
        return {
            'gradient_nt_per_km': gradient / 50.0,  # Normalize to per km
            'inner_field_avg': inner_avg,
            'outer_field_avg': outer_avg,
            'measurement_count': len(measurements)
        }
    
    def process_site(self, site_name: str, lat: float, lon: float, site_type: str) -> Dict:
        """Process a complete site with transect measurements"""
        print(f"Processing {site_name}...")
        
        # Generate transect points
        points = self.generate_transect_points(lat, lon)
        
        # Collect measurements with rate limiting
        measurements = []
        for i, (point_lat, point_lon) in enumerate(points):
            print(f"  Point {i+1}/8: {point_lat:.3f}, {point_lon:.3f}")
            
            data = self.get_magnetic_field(point_lat, point_lon)
            if data:
                measurements.append(data)
            
            # Rate limiting: 1 second between requests
            time.sleep(1)
        
        # Calculate gradient
        gradient_data = self.calculate_gradient(measurements)
        
        result = {
            'site_name': site_name,
            'center_lat': lat,
            'center_lon': lon,
            'site_type': site_type,
            'measurements_collected': len(measurements),
            'timestamp': datetime.now().isoformat()
        }
        
        if gradient_data:
            result.update(gradient_data)
        
        return result

def main():
    """Main execution function"""
    harvester = BGSMagneticHarvester()
    results = []
    
    print("BGS Magnetic Field Data Harvester")
    print("Testing Magnetic Uphill Trap Hypothesis")
    print("=" * 50)
    
    # Process all sites
    for site_name, lat, lon, site_type in TEST_SITES:
        try:
            result = harvester.process_site(site_name, lat, lon, site_type)
            results.append(result)
            
            # Print immediate result
            if 'gradient_nt_per_km' in result:
                gradient = result['gradient_nt_per_km']
                status = "POSITIVE (landward-rising)" if gradient > 0 else "NEGATIVE (seaward-declining)"
                print(f"  → Gradient: {gradient:.2f} nT/km ({status})")
            else:
                print(f"  → Could not calculate gradient")
            
            print()
            
        except Exception as e:
            print(f"Error processing {site_name}: {e}")
            continue
    
    # Save results to CSV
    output_file = "data/bgs_magnetic_survey_2025-05-31.csv"
    
    if results:
        fieldnames = list(results[0].keys())
        
        with open(output_file, 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
        
        print(f"Results saved to {output_file}")
        
        # Quick analysis summary
        hotspot_gradients = [r['gradient_nt_per_km'] for r in results 
                           if r.get('site_type') == 'hotspot' and 'gradient_nt_per_km' in r]
        control_gradients = [r['gradient_nt_per_km'] for r in results 
                           if r.get('site_type') == 'control' and 'gradient_nt_per_km' in r]
        
        print("\nQuick Analysis:")
        print(f"Hotspot sites with positive gradients: {sum(1 for g in hotspot_gradients if g > 0)}/{len(hotspot_gradients)}")
        print(f"Control sites with negative gradients: {sum(1 for g in control_gradients if g < 0)}/{len(control_gradients)}")
        
        if hotspot_gradients:
            print(f"Average hotspot gradient: {sum(hotspot_gradients)/len(hotspot_gradients):.2f} nT/km")
        if control_gradients:
            print(f"Average control gradient: {sum(control_gradients)/len(control_gradients):.2f} nT/km")
    
    else:
        print("No results collected!")

if __name__ == "__main__":
    main() 