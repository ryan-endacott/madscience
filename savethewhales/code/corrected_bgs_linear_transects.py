#!/usr/bin/env python3
"""
Corrected BGS Linear Transect Analysis
Replicates NOAA methodology using BGS API for proper hypothesis testing
"""

import requests
import csv
import time
import math
from datetime import datetime
from typing import List, Tuple, Dict, Optional

# Test sites with corrected transect methodology
TEST_SITES = [
    # Known stranding hotspots
    {
        "name": "Cape Cod, USA", 
        "lat": 41.70, "lon": -70.00, 
        "type": "hotspot",
        "noaa_gradient": +1.93,
        "transect_direction": "east_west",  # Longitude changes
        "seaward_direction": "west"  # Ocean is to the west
    },
    {
        "name": "Farewell Spit, NZ", 
        "lat": -40.50, "lon": 172.70, 
        "type": "hotspot",
        "noaa_gradient": -2.27,
        "transect_direction": "east_west",
        "seaward_direction": "west"
    },
    {
        "name": "Tasmania, Australia", 
        "lat": -42.10, "lon": 147.00, 
        "type": "hotspot",
        "noaa_gradient": +1.29,
        "transect_direction": "east_west",
        "seaward_direction": "east"  # Ocean is to the east
    },
    
    # Control sites
    {
        "name": "Dutch Wadden Sea", 
        "lat": 53.40, "lon": 6.00, 
        "type": "control",
        "noaa_gradient": -2.55,
        "transect_direction": "north_south",  # Latitude changes
        "seaward_direction": "north"  # Ocean is to the north
    },
    {
        "name": "Matagorda-Padre, TX", 
        "lat": 28.30, "lon": -96.30, 
        "type": "control",
        "noaa_gradient": +2.56,
        "transect_direction": "east_west",
        "seaward_direction": "east"
    },
    {
        "name": "Banc d'Arguin, Mauritania", 
        "lat": 20.20, "lon": -16.30, 
        "type": "control",
        "noaa_gradient": +1.41,
        "transect_direction": "east_west",
        "seaward_direction": "west"
    }
]

class CorrectedBGSLinearTransects:
    """BGS API with corrected linear transect methodology matching NOAA"""
    
    def __init__(self):
        self.base_url = "https://geomag.bgs.ac.uk/web_service/GMModels/igrf/14/"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Scientific-Research-Whale-Stranding-Corrected/1.0'
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
    
    def create_linear_transect(self, site: Dict) -> List[Tuple[float, float, str]]:
        """Create linear transect points matching NOAA methodology"""
        
        # 15km total distance, 4 points (A, B, C, D) at 5km intervals
        step_km = 5.0
        total_distance = 15.0
        
        # Convert km to degrees (approximate)
        if site["transect_direction"] == "east_west":
            # Longitude changes
            step_degrees = step_km / (111.32 * math.cos(math.radians(site["lat"])))
            
            if site["seaward_direction"] == "west":
                # A is west (seaward), D is east (landward)
                points = [
                    (site["lat"], site["lon"] - 1.5 * step_degrees, "A (Seaward)"),
                    (site["lat"], site["lon"] - 0.5 * step_degrees, "B"),
                    (site["lat"], site["lon"] + 0.5 * step_degrees, "C"),
                    (site["lat"], site["lon"] + 1.5 * step_degrees, "D (Landward)")
                ]
            else:
                # A is east (seaward), D is west (landward)
                points = [
                    (site["lat"], site["lon"] + 1.5 * step_degrees, "A (Seaward)"),
                    (site["lat"], site["lon"] + 0.5 * step_degrees, "B"),
                    (site["lat"], site["lon"] - 0.5 * step_degrees, "C"),
                    (site["lat"], site["lon"] - 1.5 * step_degrees, "D (Landward)")
                ]
        else:
            # Latitude changes
            step_degrees = step_km / 111.32
            
            if site["seaward_direction"] == "north":
                # A is north (seaward), D is south (landward)
                points = [
                    (site["lat"] + 1.5 * step_degrees, site["lon"], "A (Seaward)"),
                    (site["lat"] + 0.5 * step_degrees, site["lon"], "B"),
                    (site["lat"] - 0.5 * step_degrees, site["lon"], "C"),
                    (site["lat"] - 1.5 * step_degrees, site["lon"], "D (Landward)")
                ]
            else:
                # A is south (seaward), D is north (landward)
                points = [
                    (site["lat"] - 1.5 * step_degrees, site["lon"], "A (Seaward)"),
                    (site["lat"] - 0.5 * step_degrees, site["lon"], "B"),
                    (site["lat"] + 0.5 * step_degrees, site["lon"], "C"),
                    (site["lat"] + 1.5 * step_degrees, site["lon"], "D (Landward)")
                ]
        
        return points
    
    def calculate_linear_gradient(self, measurements: List[Dict]) -> Optional[Dict]:
        """Calculate gradient using linear transect (A to D) methodology"""
        if len(measurements) < 4:
            return None
        
        # Sort by position along transect (A, B, C, D)
        measurements = sorted(measurements, key=lambda x: x.get('point_label', ''))
        
        # Linear gradient: (Field_D - Field_A) / 15km
        field_a = measurements[0]['total_intensity']  # Seaward
        field_d = measurements[3]['total_intensity']  # Landward
        
        gradient = (field_d - field_a) / 15.0  # nT/km
        
        return {
            'gradient_nt_per_km': gradient,
            'field_seaward': field_a,
            'field_landward': field_d,
            'field_difference': field_d - field_a,
            'gradient_direction': 'landward' if gradient > 0 else 'seaward',
            'measurement_count': len(measurements)
        }
    
    def process_site(self, site: Dict) -> Dict:
        """Process a site with corrected linear transect methodology"""
        print(f"\nProcessing {site['name']}...")
        print(f"  Expected NOAA gradient: {site['noaa_gradient']:+.2f} nT/km")
        
        # Generate linear transect points
        points = self.create_linear_transect(site)
        
        print(f"  Transect direction: {site['transect_direction']}")
        print(f"  Seaward direction: {site['seaward_direction']}")
        
        # Collect measurements with rate limiting
        measurements = []
        for i, (lat, lon, label) in enumerate(points):
            print(f"    {label}: {lat:.4f}, {lon:.4f}")
            
            data = self.get_magnetic_field(lat, lon)
            if data:
                data['point_label'] = label
                measurements.append(data)
            
            # Rate limiting: 1 second between requests
            time.sleep(1)
        
        # Calculate gradient
        gradient_data = self.calculate_linear_gradient(measurements)
        
        result = {
            'site_name': site['name'],
            'site_type': site['type'],
            'center_lat': site['lat'],
            'center_lon': site['lon'],
            'noaa_gradient': site['noaa_gradient'],
            'measurements_collected': len(measurements),
            'timestamp': datetime.now().isoformat(),
            'transect_direction': site['transect_direction'],
            'seaward_direction': site['seaward_direction']
        }
        
        if gradient_data:
            result.update(gradient_data)
            
            # Compare with NOAA
            bgs_gradient = gradient_data['gradient_nt_per_km']
            noaa_gradient = site['noaa_gradient']
            difference = abs(bgs_gradient - noaa_gradient)
            
            print(f"  → BGS gradient: {bgs_gradient:+.2f} nT/km")
            print(f"  → NOAA gradient: {noaa_gradient:+.2f} nT/km")
            print(f"  → Difference: {difference:.2f} nT/km")
            print(f"  → Match: {'✅ GOOD' if difference < 1.0 else '⚠️ POOR'}")
            
            result['comparison_difference'] = difference
            result['match_quality'] = 'good' if difference < 1.0 else 'poor'
        
        return result

def main():
    """Main execution function"""
    harvester = CorrectedBGSLinearTransects()
    results = []
    
    print("=" * 60)
    print("CORRECTED BGS LINEAR TRANSECT ANALYSIS")
    print("Replicating NOAA methodology with BGS API")
    print("=" * 60)
    
    # Process all sites
    for site in TEST_SITES:
        try:
            result = harvester.process_site(site)
            results.append(result)
            
        except Exception as e:
            print(f"Error processing {site['name']}: {e}")
            continue
    
    # Save results to CSV
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
    output_file = f"data/corrected_bgs_linear_transects_{timestamp}.csv"
    
    if results:
        fieldnames = list(results[0].keys())
        
        with open(output_file, 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
        
        print(f"\n📊 Results saved to {output_file}")
        
        # Analysis summary
        good_matches = sum(1 for r in results if r.get('match_quality') == 'good')
        total_sites = len(results)
        
        print(f"\n🔍 VALIDATION SUMMARY:")
        print(f"Sites with good BGS-NOAA match: {good_matches}/{total_sites}")
        print(f"Methodology validation: {'✅ SUCCESS' if good_matches >= total_sites * 0.7 else '❌ NEEDS WORK'}")
        
        # Gradient comparison
        print(f"\n📈 GRADIENT COMPARISON:")
        for result in results:
            if 'gradient_nt_per_km' in result:
                print(f"{result['site_name'][:20]:<20} | BGS: {result['gradient_nt_per_km']:+6.2f} | NOAA: {result['noaa_gradient']:+6.2f} | Δ: {result['comparison_difference']:5.2f}")
    
    else:
        print("❌ No results collected!")

if __name__ == "__main__":
    main() 