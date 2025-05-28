#!/usr/bin/env python3
"""
Plot Whale Stranding Research Coordinates on World Map
Visual verification of lat/lng coordinates
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Circle
import matplotlib.patches as mpatches

def create_world_map():
    """Create a world map with our coordinates plotted"""
    
    # Load our data
    df = pd.read_csv('literature_magnetic_data.csv')
    
    # Create figure
    fig, ax = plt.subplots(1, 1, figsize=(16, 10))
    
    # Simple world map outline (basic continents)
    # This is a simplified approach - we'll plot coastlines manually
    
    # Plot world boundaries (simplified)
    world_lons = np.array([-180, 180, 180, -180, -180])
    world_lats = np.array([-90, -90, 90, 90, -90])
    ax.plot(world_lons, world_lats, 'k-', linewidth=0.5, alpha=0.3)
    
    # Add some basic continent outlines (very simplified)
    # North America (rough outline)
    na_lons = np.array([-170, -50, -50, -170, -170])
    na_lats = np.array([70, 70, 20, 20, 70])
    ax.fill(na_lons, na_lats, color='lightgray', alpha=0.3, label='Land (approximate)')
    
    # Europe/Asia (rough)
    eu_lons = np.array([-10, 180, 180, -10, -10])
    eu_lats = np.array([70, 70, 30, 30, 70])
    ax.fill(eu_lons, eu_lats, color='lightgray', alpha=0.3)
    
    # Australia/NZ region
    au_lons = np.array([110, 180, 180, 110, 110])
    au_lats = np.array([-10, -10, -50, -50, -10])
    ax.fill(au_lons, au_lats, color='lightgray', alpha=0.3)
    
    # Africa
    af_lons = np.array([-20, 50, 50, -20, -20])
    af_lats = np.array([40, 40, -40, -40, 40])
    ax.fill(af_lons, af_lats, color='lightgray', alpha=0.3)
    
    # South America
    sa_lons = np.array([-90, -30, -30, -90, -90])
    sa_lats = np.array([15, 15, -60, -60, 15])
    ax.fill(sa_lons, sa_lats, color='lightgray', alpha=0.3)
    
    # Color coding for different types
    colors = {
        'control': 'red',
        'hotspot': 'orange', 
        'inverse': 'blue'
    }
    
    # Plot each location
    for _, row in df.iterrows():
        lat = row['Latitude']
        lon = row['Longitude']
        location_type = row['Type']
        location = row['Location']
        gradient = row['Estimated_Gradient']
        
        color = colors.get(location_type, 'gray')
        
        # Size based on gradient magnitude
        size = max(50, abs(gradient) * 10)
        
        # Plot point
        ax.scatter(lon, lat, c=color, s=size, alpha=0.8, 
                  edgecolors='black', linewidth=1, zorder=5)
        
        # Add label
        ax.annotate(f'{location}\n({lat:.1f}, {lon:.1f})\n{gradient:.1f} nT/km', 
                   (lon, lat), xytext=(5, 5), textcoords='offset points',
                   fontsize=8, ha='left', va='bottom',
                   bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8))
    
    # Formatting
    ax.set_xlim(-180, 180)
    ax.set_ylim(-90, 90)
    ax.set_xlabel('Longitude (°E)', fontsize=12)
    ax.set_ylabel('Latitude (°N)', fontsize=12)
    ax.set_title('Whale Stranding Research Locations\nCoordinate Verification Map', fontsize=14, fontweight='bold')
    
    # Add grid
    ax.grid(True, alpha=0.3)
    ax.set_xticks(np.arange(-180, 181, 30))
    ax.set_yticks(np.arange(-90, 91, 30))
    
    # Legend
    legend_elements = [
        mpatches.Patch(color='red', label='Control Sites (Known Strandings)'),
        mpatches.Patch(color='orange', label='Hotspot Sites (Literature)'),
        mpatches.Patch(color='blue', label='Inverse Sites (No Strandings)'),
        mpatches.Patch(color='lightgray', alpha=0.3, label='Land (Approximate)')
    ]
    ax.legend(handles=legend_elements, loc='upper left', bbox_to_anchor=(0.02, 0.98))
    
    # Add note about coordinate verification
    ax.text(0.02, 0.02, 
           'COORDINATE VERIFICATION:\n' +
           '• Check if points are in expected geographic regions\n' +
           '• Verify coastal locations are actually coastal\n' +
           '• Look for obvious outliers or impossible locations\n' +
           '• Point size = magnetic gradient magnitude',
           transform=ax.transAxes, fontsize=9,
           bbox=dict(boxstyle='round,pad=0.5', facecolor='lightyellow', alpha=0.9),
           verticalalignment='bottom')
    
    plt.tight_layout()
    plt.savefig('coordinate_verification_map.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    return fig, ax

def create_regional_maps():
    """Create detailed regional maps for key areas"""
    
    df = pd.read_csv('literature_magnetic_data.csv')
    
    # Define regions
    regions = {
        'New Zealand': {
            'bounds': (165, 180, -48, -34),
            'locations': df[df['Location'].str.contains('NZ|New Zealand', na=False)]
        },
        'Cape Cod Area': {
            'bounds': (-72, -68, 40, 43),
            'locations': df[df['Location'].str.contains('MA|Cape Cod', na=False)]
        },
        'North Atlantic': {
            'bounds': (-10, 10, 55, 65),
            'locations': df[df['Location'].str.contains('Scotland|Orkney|Shetland', na=False)]
        },
        'West Africa': {
            'bounds': (-20, -10, 15, 25),
            'locations': df[df['Location'].str.contains('Mauritania', na=False)]
        }
    }
    
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    axes = axes.flatten()
    
    colors = {'control': 'red', 'hotspot': 'orange', 'inverse': 'blue'}
    
    for i, (region_name, region_data) in enumerate(regions.items()):
        ax = axes[i]
        bounds = region_data['bounds']
        locations = region_data['locations']
        
        # Set map bounds
        ax.set_xlim(bounds[0], bounds[1])
        ax.set_ylim(bounds[2], bounds[3])
        
        # Add coastline approximation (simple rectangle for now)
        ax.add_patch(plt.Rectangle((bounds[0], bounds[2]), 
                                  bounds[1]-bounds[0], bounds[3]-bounds[2],
                                  fill=False, edgecolor='gray', linewidth=1))
        
        # Plot locations
        for _, row in locations.iterrows():
            lat = row['Latitude']
            lon = row['Longitude']
            location_type = row['Type']
            location = row['Location']
            gradient = row['Estimated_Gradient']
            
            color = colors.get(location_type, 'gray')
            size = max(100, abs(gradient) * 20)
            
            ax.scatter(lon, lat, c=color, s=size, alpha=0.8, 
                      edgecolors='black', linewidth=1, zorder=5)
            
            ax.annotate(f'{location}\n{gradient:.1f} nT/km', 
                       (lon, lat), xytext=(5, 5), textcoords='offset points',
                       fontsize=10, ha='left', va='bottom',
                       bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.9))
        
        ax.set_title(f'{region_name} Region', fontsize=12, fontweight='bold')
        ax.set_xlabel('Longitude (°E)')
        ax.set_ylabel('Latitude (°N)')
        ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('regional_coordinate_maps.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    return fig, axes

def coordinate_sanity_check():
    """Perform basic sanity checks on coordinates"""
    
    df = pd.read_csv('literature_magnetic_data.csv')
    
    print("COORDINATE SANITY CHECK")
    print("="*50)
    
    issues = []
    
    for _, row in df.iterrows():
        location = row['Location']
        lat = row['Latitude']
        lon = row['Longitude']
        
        # Basic range checks
        if not (-90 <= lat <= 90):
            issues.append(f"❌ {location}: Invalid latitude {lat}")
        if not (-180 <= lon <= 180):
            issues.append(f"❌ {location}: Invalid longitude {lon}")
        
        # Regional sanity checks
        if 'NZ' in location or 'New Zealand' in location:
            if not (165 <= lon <= 180 and -48 <= lat <= -34):
                issues.append(f"⚠️  {location}: Not in New Zealand region")
        
        if 'MA' in location or 'Cape Cod' in location:
            if not (-72 <= lon <= -68 and 40 <= lat <= 43):
                issues.append(f"⚠️  {location}: Not in Massachusetts region")
        
        if 'Scotland' in location:
            if not (-8 <= lon <= 0 and 55 <= lat <= 62):
                issues.append(f"⚠️  {location}: Not in Scotland region")
        
        if 'Mauritania' in location:
            if not (-20 <= lon <= -10 and 15 <= lat <= 25):
                issues.append(f"⚠️  {location}: Not in Mauritania region")
        
        if 'TX' in location or 'Texas' in location:
            if not (-107 <= lon <= -93 and 25 <= lat <= 37):
                issues.append(f"⚠️  {location}: Not in Texas region")
        
        # Ocean vs land checks
        if 'Sea' in location or 'Bay' in location or 'Spit' in location:
            # These should be coastal - hard to check without detailed coastline data
            pass
    
    if issues:
        print("POTENTIAL ISSUES FOUND:")
        for issue in issues:
            print(f"  {issue}")
    else:
        print("✅ All coordinates pass basic sanity checks")
    
    print(f"\nTotal locations checked: {len(df)}")
    print(f"Issues found: {len(issues)}")
    
    return issues

def main():
    """Run coordinate verification with maps"""
    
    print("WHALE STRANDING COORDINATE VERIFICATION")
    print("="*50)
    
    # Sanity check first
    issues = coordinate_sanity_check()
    
    print(f"\nCreating world map...")
    create_world_map()
    
    print(f"Creating regional maps...")
    create_regional_maps()
    
    print(f"\n✅ Maps saved as:")
    print(f"  - coordinate_verification_map.png")
    print(f"  - regional_coordinate_maps.png")
    
    print(f"\nVISUAL VERIFICATION CHECKLIST:")
    print(f"1. Do New Zealand points appear near South Island?")
    print(f"2. Are Cape Cod points on the Massachusetts coast?")
    print(f"3. Are Scotland points north of England?")
    print(f"4. Is Mauritania point on West African coast?")
    print(f"5. Are any points in obviously wrong locations (middle of ocean, wrong continent)?")
    
    return issues

if __name__ == "__main__":
    main() 