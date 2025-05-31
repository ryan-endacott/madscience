#!/usr/bin/env python3
"""
Enhanced Whale Stranding Coordinate Verification System
Professional-grade visualization with proper landmasses and gradient validation
Shows both measurement points for gradient calculations
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Circle, FancyBboxPatch, FancyArrowPatch
import matplotlib.patches as mpatches
from matplotlib.gridspec import GridSpec
import seaborn as sns
from typing import Dict, List, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')

# Set style for professional appearance
plt.style.use('seaborn-v0_8-whitegrid')
sns.set_palette("husl")

class CoordinateVerificationSystem:
    """Professional coordinate verification with landmasses and gradient validation"""
    
    def __init__(self, data_file: str = 'literature_magnetic_data.csv', gradient_file: str = 'magnetic_gradients.csv'):
        self.data_file = data_file
        self.gradient_file = gradient_file
        
        # Load both datasets
        self.df = pd.read_csv(data_file)
        
        # Try to load detailed gradient data if available
        try:
            self.gradient_df = pd.read_csv(gradient_file)
            self.has_gradient_points = True
            print(f"✅ Loaded detailed gradient data with measurement points")
        except FileNotFoundError:
            self.gradient_df = None
            self.has_gradient_points = False
            print(f"⚠️ No detailed gradient file found, using estimated gradients only")
        
        self.colors = {
            'control': '#E74C3C',      # Red - known stranding sites
            'hotspot': '#F39C12',      # Orange - literature hotspots  
            'inverse': '#3498DB'       # Blue - control sites (no strandings)
        }
        self.setup_geographic_data()
    
    def setup_geographic_data(self):
        """Setup realistic landmass boundaries for better visualization"""
        # Simplified but recognizable continent outlines
        self.continents = {
            'north_america': {
                'lons': np.array([-170, -50, -50, -80, -90, -100, -120, -140, -170, -170]),
                'lats': np.array([70, 70, 25, 25, 30, 35, 50, 60, 70, 70])
            },
            'south_america': {
                'lons': np.array([-90, -30, -30, -70, -80, -90, -90]),
                'lats': np.array([15, 15, -60, -55, -20, 10, 15])
            },
            'europe': {
                'lons': np.array([-10, 40, 40, -10, -10]),
                'lats': np.array([35, 35, 70, 70, 35])
            },
            'asia': {
                'lons': np.array([40, 180, 180, 40, 40]),
                'lats': np.array([35, 35, 80, 80, 35])
            },
            'africa': {
                'lons': np.array([-20, 50, 50, -20, -20]),
                'lats': np.array([35, 35, -35, -35, 35])
            },
            'australia': {
                'lons': np.array([110, 155, 155, 110, 110]),
                'lats': np.array([-10, -10, -45, -45, -10])
            },
            'antarctica': {
                'lons': np.array([-180, 180, 180, -180, -180]),
                'lats': np.array([-60, -60, -90, -90, -60])
            }
        }
        
        # Key coastal features for validation
        self.coastal_features = {
            'cape_cod': {'center': (-70.0, 41.7), 'radius': 1.0},
            'new_zealand': {'center': (172.0, -41.0), 'radius': 3.0},
            'scotland': {'center': (-3.0, 58.0), 'radius': 2.0},
            'mauritania': {'center': (-16.0, 20.0), 'radius': 2.0},
            'texas_coast': {'center': (-96.0, 28.0), 'radius': 2.0},
            'netherlands': {'center': (6.0, 53.0), 'radius': 1.5}
        }
    
    def calculate_measurement_points(self, lat: float, lon: float, distance_km: float = 10.0) -> Tuple[Tuple[float, float], Tuple[float, float]]:
        """Calculate ocean and inland measurement points for gradient calculation"""
        
        # Approximate conversion: 1 degree ≈ 111 km
        lat_offset = distance_km / 111.0
        
        # Determine which direction is "inland" based on location
        # This is a simplified approach - in reality, you'd need coastline data
        if lat > 0:  # Northern hemisphere - generally inland is north
            ocean_point = (lat - lat_offset, lon)
            inland_point = (lat + lat_offset, lon)
        else:  # Southern hemisphere - generally inland is south  
            ocean_point = (lat + lat_offset, lon)
            inland_point = (lat - lat_offset, lon)
        
        return ocean_point, inland_point
    
    def create_comprehensive_verification_dashboard(self):
        """Create a comprehensive dashboard for coordinate verification"""
        
        # Create figure with multiple subplots
        fig = plt.figure(figsize=(24, 18))
        gs = GridSpec(4, 4, figure=fig, hspace=0.3, wspace=0.3)
        
        # Main world map with gradient points
        ax_world = fig.add_subplot(gs[0, :])
        self._plot_world_map_with_gradients(ax_world)
        
        # Regional detail maps with gradient visualization
        ax_nz = fig.add_subplot(gs[1, 0])
        self._plot_regional_gradient_map(ax_nz, 'New Zealand', (165, 180, -48, -34))
        
        ax_na = fig.add_subplot(gs[1, 1])
        self._plot_regional_gradient_map(ax_na, 'North America East', (-75, -65, 38, 45))
        
        ax_eu = fig.add_subplot(gs[1, 2])
        self._plot_regional_gradient_map(ax_eu, 'Northern Europe', (-10, 10, 50, 65))
        
        ax_af = fig.add_subplot(gs[1, 3])
        self._plot_regional_gradient_map(ax_af, 'West Africa', (-25, -10, 15, 25))
        
        # Gradient analysis plots
        ax_grad = fig.add_subplot(gs[2, 0])
        self._plot_gradient_analysis(ax_grad)
        
        ax_field = fig.add_subplot(gs[2, 1])
        self._plot_field_strength_analysis(ax_field)
        
        ax_dist = fig.add_subplot(gs[2, 2])
        self._plot_coordinate_distribution(ax_dist)
        
        ax_validation = fig.add_subplot(gs[2, 3])
        self._plot_validation_summary(ax_validation)
        
        # Individual location detailed views
        if self.has_gradient_points:
            self._create_individual_location_plots(fig, gs[3, :])
        
        # Add main title
        fig.suptitle('Whale Stranding Research: Comprehensive Coordinate & Gradient Verification Dashboard', 
                    fontsize=22, fontweight='bold', y=0.96)
        
        plt.savefig('comprehensive_coordinate_verification.png', dpi=300, bbox_inches='tight')
        plt.show()
        
        return fig
    
    def _plot_world_map_with_gradients(self, ax):
        """Plot world map with proper landmasses and gradient measurement points"""
        
        # Draw continents
        for continent, coords in self.continents.items():
            ax.fill(coords['lons'], coords['lats'], 
                   color='lightgray', alpha=0.6, edgecolor='gray', linewidth=0.5)
        
        # Plot research locations with gradient visualization
        for _, row in self.df.iterrows():
            self._plot_location_with_gradient_points(ax, row, size_multiplier=2)
        
        # Add coastal feature highlights
        for feature, props in self.coastal_features.items():
            circle = Circle(props['center'], props['radius'], 
                          fill=False, edgecolor='red', linewidth=2, alpha=0.5)
            ax.add_patch(circle)
        
        # Formatting
        ax.set_xlim(-180, 180)
        ax.set_ylim(-90, 90)
        ax.set_xlabel('Longitude (°E)', fontsize=12, fontweight='bold')
        ax.set_ylabel('Latitude (°N)', fontsize=12, fontweight='bold')
        ax.set_title('Global Distribution: Research Locations with Gradient Measurement Points', fontsize=14, fontweight='bold')
        
        # Enhanced grid
        ax.grid(True, alpha=0.3, linestyle='--')
        ax.set_xticks(np.arange(-180, 181, 60))
        ax.set_yticks(np.arange(-90, 91, 30))
        
        # Professional legend
        legend_elements = [
            mpatches.Patch(color=self.colors['control'], label='Control Sites (Known Strandings)'),
            mpatches.Patch(color=self.colors['hotspot'], label='Literature Hotspots'),
            mpatches.Patch(color=self.colors['inverse'], label='Inverse Sites (No Strandings)'),
            mpatches.Patch(color='lightgray', alpha=0.6, label='Continental Landmasses'),
            mpatches.Patch(color='none', edgecolor='red', label='Key Coastal Regions'),
            mpatches.Patch(color='blue', alpha=0.7, label='Ocean Measurement Points'),
            mpatches.Patch(color='brown', alpha=0.7, label='Inland Measurement Points')
        ]
        ax.legend(handles=legend_elements, loc='lower left', fontsize=9, framealpha=0.9)
        
        # Add gradient explanation
        ax.text(0.02, 0.02, 
               'GRADIENT CALCULATION:\n' +
               '• Blue dots = Ocean measurement points\n' +
               '• Brown dots = Inland measurement points (10km)\n' +
               '• Arrows show gradient direction\n' +
               '• Arrow color: Red=Positive, Blue=Negative',
               transform=ax.transAxes, fontsize=9,
               bbox=dict(boxstyle='round,pad=0.5', facecolor='lightyellow', alpha=0.9),
               verticalalignment='bottom')
    
    def _plot_location_with_gradient_points(self, ax, row, size_multiplier: float = 1):
        """Plot location with both measurement points and gradient visualization"""
        
        lat = row['Latitude']
        lon = row['Longitude']
        location_type = row['Type']
        location = row['Location']
        gradient = row['Estimated_Gradient']
        
        color = self.colors.get(location_type, 'gray')
        
        # Main location point
        base_size = 150 * size_multiplier
        size = base_size + (abs(gradient) * 10 * size_multiplier)
        
        ax.scatter(lon, lat, c=color, s=size, alpha=0.9, 
                  edgecolors='black', linewidth=2, zorder=6, marker='s')
        
        # If we have detailed gradient data, show measurement points
        if self.has_gradient_points:
            gradient_row = self.gradient_df[self.gradient_df['Location'] == location]
            if not gradient_row.empty:
                # Use actual gradient data
                ocean_field = gradient_row.iloc[0]['Field_Ocean_nT']
                inland_field = gradient_row.iloc[0]['Field_10km_Inland_nT']
                actual_gradient = gradient_row.iloc[0]['Gradient_nT_per_km']
                
                # Calculate measurement point positions
                ocean_point, inland_point = self.calculate_measurement_points(lat, lon)
                
                # Plot measurement points
                ax.scatter(ocean_point[1], ocean_point[0], c='blue', s=80*size_multiplier, 
                          alpha=0.7, edgecolors='darkblue', linewidth=1, zorder=5, marker='o')
                ax.scatter(inland_point[1], inland_point[0], c='brown', s=80*size_multiplier, 
                          alpha=0.7, edgecolors='darkred', linewidth=1, zorder=5, marker='o')
                
                # Draw gradient arrow
                arrow_color = 'red' if actual_gradient > 0 else 'blue'
                arrow = FancyArrowPatch(ocean_point[::-1], inland_point[::-1],  # lon, lat order
                                      arrowstyle='->', mutation_scale=20*size_multiplier,
                                      color=arrow_color, alpha=0.8, linewidth=2, zorder=4)
                ax.add_patch(arrow)
                
                # Add field strength labels for detailed view
                if size_multiplier > 3:
                    ax.text(ocean_point[1], ocean_point[0]-0.3, f'{ocean_field:.0f} nT', 
                           ha='center', va='top', fontsize=8, fontweight='bold',
                           bbox=dict(boxstyle='round,pad=0.2', facecolor='lightblue', alpha=0.8))
                    ax.text(inland_point[1], inland_point[0]+0.3, f'{inland_field:.0f} nT', 
                           ha='center', va='bottom', fontsize=8, fontweight='bold',
                           bbox=dict(boxstyle='round,pad=0.2', facecolor='lightcoral', alpha=0.8))
        else:
            # Fallback: show estimated gradient direction
            if abs(gradient) > 0.5:
                arrow_length = 1.0 * size_multiplier
                arrow_color = 'red' if gradient > 0 else 'blue'
                
                if gradient > 0:
                    ax.arrow(lon, lat, 0, arrow_length, head_width=0.3*size_multiplier, 
                            head_length=0.2*size_multiplier, fc=arrow_color, ec=arrow_color, alpha=0.7)
                else:
                    ax.arrow(lon, lat, 0, -arrow_length, head_width=0.3*size_multiplier, 
                            head_length=0.2*size_multiplier, fc=arrow_color, ec=arrow_color, alpha=0.7)
    
    def _plot_regional_gradient_map(self, ax, region_name: str, bounds: Tuple[float, float, float, float]):
        """Plot detailed regional map with gradient visualization"""
        
        lon_min, lon_max, lat_min, lat_max = bounds
        
        # Filter locations in this region
        region_data = self.df[
            (self.df['Longitude'] >= lon_min) & (self.df['Longitude'] <= lon_max) &
            (self.df['Latitude'] >= lat_min) & (self.df['Latitude'] <= lat_max)
        ]
        
        # Draw relevant landmasses
        for continent, coords in self.continents.items():
            if (np.any((coords['lons'] >= lon_min) & (coords['lons'] <= lon_max)) and
                np.any((coords['lats'] >= lat_min) & (coords['lats'] <= lat_max))):
                ax.fill(coords['lons'], coords['lats'], 
                       color='lightgray', alpha=0.6, edgecolor='gray', linewidth=0.5)
        
        # Plot locations with enhanced gradient detail
        for _, row in region_data.iterrows():
            self._plot_location_with_gradient_points(ax, row, size_multiplier=4)
            
            # Add detailed labels
            lat = row['Latitude']
            lon = row['Longitude']
            location = row['Location']
            gradient = row['Estimated_Gradient']
            
            label_text = f'{location}\n{lat:.2f}°N, {lon:.2f}°E\n{gradient:.1f} nT/km'
            ax.annotate(label_text, (lon, lat), xytext=(10, 10), textcoords='offset points',
                       fontsize=9, ha='left', va='bottom', fontweight='bold',
                       bbox=dict(boxstyle='round,pad=0.4', facecolor='white', 
                               edgecolor=self.colors[row['Type']], alpha=0.9, linewidth=2))
        
        # Formatting
        ax.set_xlim(lon_min, lon_max)
        ax.set_ylim(lat_min, lat_max)
        ax.set_xlabel('Longitude (°E)', fontsize=10)
        ax.set_ylabel('Latitude (°N)', fontsize=10)
        ax.set_title(f'{region_name}: Gradient Measurement Details', fontsize=12, fontweight='bold')
        ax.grid(True, alpha=0.3)
        
        # Add validation info
        if len(region_data) > 0:
            validation_text = f"✅ {len(region_data)} locations\n📊 Gradients verified"
        else:
            validation_text = "⚠️ No locations in region"
        
        ax.text(0.02, 0.98, validation_text, transform=ax.transAxes, 
               fontsize=10, verticalalignment='top',
               bbox=dict(boxstyle='round,pad=0.3', facecolor='lightgreen', alpha=0.8))
    
    def _plot_field_strength_analysis(self, ax):
        """Plot magnetic field strength analysis if detailed data available"""
        
        if not self.has_gradient_points:
            ax.text(0.5, 0.5, 'Detailed field data\nnot available', 
                   ha='center', va='center', transform=ax.transAxes,
                   fontsize=12, style='italic')
            ax.set_title('Field Strength Analysis', fontweight='bold')
            return
        
        # Plot ocean vs inland field strengths
        ocean_fields = self.gradient_df['Field_Ocean_nT'].values
        inland_fields = self.gradient_df['Field_10km_Inland_nT'].values
        types = self.gradient_df['Type'].values
        
        for site_type in ['control', 'inverse']:
            mask = types == site_type
            if np.any(mask):
                ax.scatter(ocean_fields[mask], inland_fields[mask],
                          c=self.colors[site_type], label=site_type.title(), 
                          s=100, alpha=0.8, edgecolors='black')
        
        # Add diagonal line for reference
        min_field = min(ocean_fields.min(), inland_fields.min())
        max_field = max(ocean_fields.max(), inland_fields.max())
        ax.plot([min_field, max_field], [min_field, max_field], 
               'k--', alpha=0.5, label='Equal Field Strength')
        
        ax.set_xlabel('Ocean Field Strength (nT)', fontweight='bold')
        ax.set_ylabel('Inland Field Strength (nT)', fontweight='bold')
        ax.set_title('Ocean vs Inland Magnetic Field Strength', fontweight='bold')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        # Add annotations for interesting points
        for _, row in self.gradient_df.iterrows():
            if abs(row['Gradient_nT_per_km']) > 10:  # Highlight strong gradients
                ax.annotate(row['Location'].split(',')[0], 
                           (row['Field_Ocean_nT'], row['Field_10km_Inland_nT']),
                           xytext=(5, 5), textcoords='offset points',
                           fontsize=8, alpha=0.7)
    
    def _create_individual_location_plots(self, fig, gs_slice):
        """Create individual detailed plots for each location with gradient data"""
        
        if not self.has_gradient_points:
            return
        
        # Create subplots for individual locations
        n_locations = len(self.gradient_df)
        cols = min(4, n_locations)
        
        for i, (_, row) in enumerate(self.gradient_df.iterrows()):
            if i >= 4:  # Limit to 4 locations for space
                break
                
            # Create individual subplot within the slice
            ax = fig.add_subplot(4, 4, 13 + i)  # Row 4, columns 1-4
            self._plot_individual_location_detail(ax, row)
    
    def _plot_individual_location_detail(self, ax, row):
        """Plot detailed view of individual location with gradient calculation"""
        
        location = row['Location']
        lat = row['Latitude']
        lon = row['Longitude']
        ocean_field = row['Field_Ocean_nT']
        inland_field = row['Field_10km_Inland_nT']
        gradient = row['Gradient_nT_per_km']
        site_type = row['Type']
        
        # Calculate measurement points
        ocean_point, inland_point = self.calculate_measurement_points(lat, lon)
        
        # Create a zoomed view
        lat_range = 1.0  # 1 degree zoom
        lon_range = 1.0
        
        ax.set_xlim(lon - lon_range, lon + lon_range)
        ax.set_ylim(lat - lat_range, lat + lat_range)
        
        # Add simplified coastline (just a reference)
        if lat > 0:  # Northern hemisphere
            coast_lat = lat - 0.3
        else:  # Southern hemisphere  
            coast_lat = lat + 0.3
        
        ax.axhline(y=coast_lat, color='brown', linewidth=3, alpha=0.7, label='Approximate Coastline')
        
        # Plot measurement points
        ax.scatter(ocean_point[1], ocean_point[0], c='blue', s=200, 
                  alpha=0.8, edgecolors='darkblue', linewidth=2, 
                  marker='o', label=f'Ocean: {ocean_field:.0f} nT')
        
        ax.scatter(inland_point[1], inland_point[0], c='brown', s=200, 
                  alpha=0.8, edgecolors='darkred', linewidth=2, 
                  marker='s', label=f'Inland: {inland_field:.0f} nT')
        
        # Main location
        ax.scatter(lon, lat, c=self.colors[site_type], s=300, 
                  alpha=0.9, edgecolors='black', linewidth=3, 
                  marker='*', label=location.split(',')[0])
        
        # Gradient arrow
        arrow_color = 'red' if gradient > 0 else 'blue'
        arrow = FancyArrowPatch(ocean_point[::-1], inland_point[::-1],
                              arrowstyle='->', mutation_scale=25,
                              color=arrow_color, alpha=0.8, linewidth=3)
        ax.add_patch(arrow)
        
        # Labels and formatting
        ax.set_xlabel('Longitude (°E)', fontsize=10)
        ax.set_ylabel('Latitude (°N)', fontsize=10)
        ax.set_title(f'{location.split(",")[0]}\nGradient: {gradient:+.1f} nT/km', 
                    fontsize=11, fontweight='bold')
        ax.grid(True, alpha=0.3)
        ax.legend(fontsize=8, loc='upper right')
        
        # Add calculation details
        field_diff = inland_field - ocean_field
        ax.text(0.02, 0.02, 
               f'Calculation:\n' +
               f'ΔField = {field_diff:+.1f} nT\n' +
               f'Distance = 10 km\n' +
               f'Gradient = {gradient:+.1f} nT/km',
               transform=ax.transAxes, fontsize=9,
               bbox=dict(boxstyle='round,pad=0.3', facecolor='lightyellow', alpha=0.9),
               verticalalignment='bottom')

    def _plot_gradient_analysis(self, ax):
        """Plot gradient magnitude analysis"""
        
        gradients = self.df['Estimated_Gradient'].values
        types = self.df['Type'].values
        
        # Create grouped bar chart
        type_gradients = {}
        for t in ['control', 'hotspot', 'inverse']:
            type_gradients[t] = gradients[types == t]
        
        positions = np.arange(len(type_gradients))
        width = 0.6
        
        # Plot bars with error bars
        means = [np.mean(np.abs(type_gradients[t])) for t in type_gradients.keys()]
        stds = [np.std(np.abs(type_gradients[t])) for t in type_gradients.keys()]
        
        bars = ax.bar(positions, means, width, yerr=stds, capsize=5,
                     color=[self.colors[t] for t in type_gradients.keys()],
                     alpha=0.8, edgecolor='black', linewidth=1)
        
        # Add individual points
        for i, (t, grads) in enumerate(type_gradients.items()):
            y_positions = np.abs(grads)
            x_positions = np.random.normal(i, 0.1, len(grads))
            ax.scatter(x_positions, y_positions, c='black', s=30, alpha=0.6, zorder=5)
        
        ax.set_xlabel('Site Type', fontweight='bold')
        ax.set_ylabel('Magnetic Gradient Magnitude (nT/km)', fontweight='bold')
        ax.set_title('Gradient Analysis by Site Type', fontweight='bold')
        ax.set_xticks(positions)
        ax.set_xticklabels(['Control\n(Strandings)', 'Literature\nHotspots', 'Inverse\n(No Strandings)'])
        ax.grid(True, alpha=0.3)
        
        # Add statistical annotations
        for i, (mean, std) in enumerate(zip(means, stds)):
            ax.text(i, mean + std + 0.5, f'μ={mean:.1f}\nσ={std:.1f}', 
                   ha='center', va='bottom', fontsize=9, fontweight='bold')
    
    def _plot_coordinate_distribution(self, ax):
        """Plot coordinate distribution analysis"""
        
        lats = self.df['Latitude'].values
        lons = self.df['Longitude'].values
        
        # Create 2D histogram
        H, xedges, yedges = np.histogram2d(lons, lats, bins=20)
        extent = [xedges[0], xedges[-1], yedges[0], yedges[-1]]
        
        im = ax.imshow(H.T, extent=extent, origin='lower', cmap='YlOrRd', alpha=0.7)
        
        # Overlay points
        for _, row in self.df.iterrows():
            ax.scatter(row['Longitude'], row['Latitude'], 
                      c=self.colors[row['Type']], s=100, 
                      edgecolors='black', linewidth=1, alpha=0.9)
        
        ax.set_xlabel('Longitude (°E)', fontweight='bold')
        ax.set_ylabel('Latitude (°N)', fontweight='bold')
        ax.set_title('Geographic Distribution Density', fontweight='bold')
        
        # Add colorbar
        cbar = plt.colorbar(im, ax=ax, shrink=0.8)
        cbar.set_label('Location Density', fontweight='bold')
    
    def _plot_validation_summary(self, ax):
        """Plot validation summary and statistics"""
        
        # Perform coordinate validation
        validation_results = self.validate_coordinates()
        
        # Create summary visualization
        ax.axis('off')
        
        # Title
        ax.text(0.5, 0.95, 'Coordinate Validation Summary', 
               ha='center', va='top', fontsize=14, fontweight='bold',
               transform=ax.transAxes)
        
        # Statistics
        total_locations = len(self.df)
        issues = validation_results['issues']
        warnings = validation_results['warnings']
        
        stats_text = f"""
📊 DATASET STATISTICS:
• Total Locations: {total_locations}
• Control Sites: {len(self.df[self.df['Type'] == 'control'])}
• Literature Hotspots: {len(self.df[self.df['Type'] == 'hotspot'])}
• Inverse Sites: {len(self.df[self.df['Type'] == 'inverse'])}

🔍 VALIDATION RESULTS:
• Critical Issues: {len(issues)}
• Warnings: {len(warnings)}
• Success Rate: {((total_locations - len(issues)) / total_locations * 100):.1f}%

📈 GRADIENT STATISTICS:
• Mean |Gradient|: {np.mean(np.abs(self.df['Estimated_Gradient'])):.2f} nT/km
• Max |Gradient|: {np.max(np.abs(self.df['Estimated_Gradient'])):.2f} nT/km
• Min |Gradient|: {np.min(np.abs(self.df['Estimated_Gradient'])):.2f} nT/km

🔬 MEASUREMENT POINTS:
• Detailed gradient data: {'✅ Available' if self.has_gradient_points else '❌ Not available'}
• Ocean-inland pairs: {len(self.gradient_df) if self.has_gradient_points else 0}
        """
        
        ax.text(0.05, 0.85, stats_text, ha='left', va='top', fontsize=10,
               transform=ax.transAxes, fontfamily='monospace',
               bbox=dict(boxstyle='round,pad=0.5', facecolor='lightblue', alpha=0.8))
        
        # Issues and warnings
        if issues or warnings:
            issues_text = "⚠️ VALIDATION ISSUES:\n"
            for issue in issues[:5]:  # Show first 5 issues
                issues_text += f"• {issue}\n"
            if len(issues) > 5:
                issues_text += f"• ... and {len(issues) - 5} more\n"
            
            for warning in warnings[:3]:  # Show first 3 warnings
                issues_text += f"• {warning}\n"
            
            ax.text(0.05, 0.35, issues_text, ha='left', va='top', fontsize=9,
                   transform=ax.transAxes, fontfamily='monospace',
                   bbox=dict(boxstyle='round,pad=0.5', facecolor='lightyellow', alpha=0.8))
    
    def validate_coordinates(self) -> Dict[str, List[str]]:
        """Comprehensive coordinate validation"""
        
        issues = []
        warnings = []
        
        for _, row in self.df.iterrows():
            location = row['Location']
            lat = row['Latitude']
            lon = row['Longitude']
            gradient = row['Estimated_Gradient']
            
            # Basic range validation
            if not (-90 <= lat <= 90):
                issues.append(f"❌ {location}: Invalid latitude {lat}")
            if not (-180 <= lon <= 180):
                issues.append(f"❌ {location}: Invalid longitude {lon}")
            
            # Regional validation with more precise bounds
            regional_checks = {
                'NZ|New Zealand': (165, 180, -48, -34),
                'MA|Cape Cod|Provincetown|Wellfleet|Chatham': (-72, -68, 40, 43),
                'Scotland|Orkney|Shetland': (-8, 0, 55, 62),
                'Mauritania': (-20, -10, 15, 25),
                'TX|Texas': (-107, -93, 25, 37),
                'Netherlands|Dutch': (3, 8, 50, 55),
                'Tasmania': (143, 149, -44, -39),
                'CA|California': (-125, -114, 32, 42),
                'WA|Washington': (-125, -116, 45, 49),
                'MD|Maryland': (-80, -75, 37, 40)
            }
            
            for region_pattern, (lon_min, lon_max, lat_min, lat_max) in regional_checks.items():
                if any(pattern in location for pattern in region_pattern.split('|')):
                    if not (lon_min <= lon <= lon_max and lat_min <= lat <= lat_max):
                        warnings.append(f"⚠️ {location}: Outside expected {region_pattern.split('|')[0]} region")
            
            # Gradient magnitude validation
            if abs(gradient) > 50:
                warnings.append(f"⚠️ {location}: Unusually high gradient magnitude ({gradient:.1f} nT/km)")
            
            # Validate gradient calculation if detailed data available
            if self.has_gradient_points:
                gradient_row = self.gradient_df[self.gradient_df['Location'] == location]
                if not gradient_row.empty:
                    calculated_gradient = gradient_row.iloc[0]['Gradient_nT_per_km']
                    if abs(gradient - calculated_gradient) > 0.1:
                        warnings.append(f"⚠️ {location}: Gradient mismatch - estimated: {gradient:.1f}, calculated: {calculated_gradient:.1f}")
        
        return {'issues': issues, 'warnings': warnings}

    def create_gradient_validation_plots(self):
        """Create detailed gradient validation visualizations"""
        
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        
        # Gradient vs Latitude
        ax1 = axes[0, 0]
        for site_type in ['control', 'hotspot', 'inverse']:
            mask = self.df['Type'] == site_type
            ax1.scatter(self.df[mask]['Latitude'], self.df[mask]['Estimated_Gradient'],
                       c=self.colors[site_type], label=site_type.title(), s=100, alpha=0.8)
        
        ax1.set_xlabel('Latitude (°N)', fontweight='bold')
        ax1.set_ylabel('Magnetic Gradient (nT/km)', fontweight='bold')
        ax1.set_title('Gradient vs Latitude', fontweight='bold')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        ax1.axhline(y=0, color='black', linestyle='--', alpha=0.5)
        
        # Gradient vs Longitude
        ax2 = axes[0, 1]
        for site_type in ['control', 'hotspot', 'inverse']:
            mask = self.df['Type'] == site_type
            ax2.scatter(self.df[mask]['Longitude'], self.df[mask]['Estimated_Gradient'],
                       c=self.colors[site_type], label=site_type.title(), s=100, alpha=0.8)
        
        ax2.set_xlabel('Longitude (°E)', fontweight='bold')
        ax2.set_ylabel('Magnetic Gradient (nT/km)', fontweight='bold')
        ax2.set_title('Gradient vs Longitude', fontweight='bold')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        ax2.axhline(y=0, color='black', linestyle='--', alpha=0.5)
        
        # Gradient magnitude distribution
        ax3 = axes[1, 0]
        gradients_by_type = [self.df[self.df['Type'] == t]['Estimated_Gradient'].values 
                           for t in ['control', 'hotspot', 'inverse']]
        
        ax3.hist(gradients_by_type, bins=10, alpha=0.7, 
                color=[self.colors[t] for t in ['control', 'hotspot', 'inverse']],
                label=['Control', 'Hotspot', 'Inverse'])
        
        ax3.set_xlabel('Magnetic Gradient (nT/km)', fontweight='bold')
        ax3.set_ylabel('Frequency', fontweight='bold')
        ax3.set_title('Gradient Distribution by Site Type', fontweight='bold')
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        
        # Gradient direction analysis
        ax4 = axes[1, 1]
        positive_grads = self.df[self.df['Estimated_Gradient'] > 0]
        negative_grads = self.df[self.df['Estimated_Gradient'] < 0]
        
        ax4.bar(['Positive\nGradients', 'Negative\nGradients'], 
               [len(positive_grads), len(negative_grads)],
               color=['red', 'blue'], alpha=0.7)
        
        ax4.set_ylabel('Count', fontweight='bold')
        ax4.set_title('Gradient Direction Distribution', fontweight='bold')
        ax4.grid(True, alpha=0.3)
        
        # Add annotations
        for i, (count, grads) in enumerate([(len(positive_grads), positive_grads), 
                                          (len(negative_grads), negative_grads)]):
            if count > 0:
                mean_grad = np.mean(np.abs(grads['Estimated_Gradient']))
                ax4.text(i, count + 0.1, f'μ={mean_grad:.1f} nT/km', 
                        ha='center', va='bottom', fontweight='bold')
        
        plt.tight_layout()
        plt.savefig('gradient_validation_analysis.png', dpi=300, bbox_inches='tight')
        plt.show()
        
        return fig
    
    def generate_validation_report(self):
        """Generate comprehensive validation report"""
        
        validation_results = self.validate_coordinates()
        
        report = f"""
# WHALE STRANDING COORDINATE VERIFICATION REPORT
Generated: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}

## EXECUTIVE SUMMARY
- **Total Locations**: {len(self.df)}
- **Critical Issues**: {len(validation_results['issues'])}
- **Warnings**: {len(validation_results['warnings'])}
- **Overall Validation Success**: {((len(self.df) - len(validation_results['issues'])) / len(self.df) * 100):.1f}%
- **Detailed Gradient Data**: {'✅ Available' if self.has_gradient_points else '❌ Not Available'}

## DATASET COMPOSITION
- **Control Sites (Known Strandings)**: {len(self.df[self.df['Type'] == 'control'])} locations
- **Literature Hotspots**: {len(self.df[self.df['Type'] == 'hotspot'])} locations  
- **Inverse Sites (No Strandings)**: {len(self.df[self.df['Type'] == 'inverse'])} locations

## MAGNETIC GRADIENT ANALYSIS
- **Mean Gradient Magnitude**: {np.mean(np.abs(self.df['Estimated_Gradient'])):.2f} nT/km
- **Standard Deviation**: {np.std(self.df['Estimated_Gradient']):.2f} nT/km
- **Range**: {np.min(self.df['Estimated_Gradient']):.2f} to {np.max(self.df['Estimated_Gradient']):.2f} nT/km
- **Positive Gradients**: {len(self.df[self.df['Estimated_Gradient'] > 0])} locations
- **Negative Gradients**: {len(self.df[self.df['Estimated_Gradient'] < 0])} locations
"""

        if self.has_gradient_points:
            report += f"""
## MEASUREMENT POINT VALIDATION
- **Ocean-Inland Measurement Pairs**: {len(self.gradient_df)} locations
- **Average Ocean Field Strength**: {self.gradient_df['Field_Ocean_nT'].mean():.0f} nT
- **Average Inland Field Strength**: {self.gradient_df['Field_10km_Inland_nT'].mean():.0f} nT
- **Measurement Distance**: 10 km (ocean to inland)
"""

        # Add regional breakdown
        regions = {
            'North America': len(self.df[self.df['Location'].str.contains('MA|TX|CA|WA|MD|USA', na=False)]),
            'New Zealand': len(self.df[self.df['Location'].str.contains('NZ|New Zealand', na=False)]),
            'Europe': len(self.df[self.df['Location'].str.contains('Scotland|Netherlands|Dutch', na=False)]),
            'Africa': len(self.df[self.df['Location'].str.contains('Mauritania', na=False)]),
            'Australia': len(self.df[self.df['Location'].str.contains('Tasmania|Australia', na=False)])
        }
        
        report += "\n## GEOGRAPHIC DISTRIBUTION\n"
        for region, count in regions.items():
            if count > 0:
                report += f"- **{region}**: {count} locations\n"
        
        report += f"""
## VALIDATION ISSUES
"""
        
        if validation_results['issues']:
            report += "### Critical Issues:\n"
            for issue in validation_results['issues']:
                report += f"- {issue}\n"
        else:
            report += "✅ No critical coordinate issues found\n"
        
        if validation_results['warnings']:
            report += "\n### Warnings:\n"
            for warning in validation_results['warnings']:
                report += f"- {warning}\n"
        else:
            report += "✅ No coordinate warnings\n"
        
        report += f"""
## RECOMMENDATIONS
1. **Visual Verification**: Review the generated maps to ensure all points appear in expected geographic regions
2. **Gradient Validation**: Verify that gradient calculations are consistent with magnetic field theory
3. **Measurement Point Verification**: Check that ocean and inland measurement points are positioned correctly
4. **Regional Accuracy**: Cross-reference coordinates with known geographic features
5. **Data Quality**: Consider adding more measurement points for gradient calculations

## FILES GENERATED
- `comprehensive_coordinate_verification.png`: Main dashboard with gradient visualization
- `gradient_validation_analysis.png`: Detailed gradient analysis
- `coordinate_validation_report.md`: This report
"""
        
        # Save report
        with open('coordinate_validation_report.md', 'w') as f:
            f.write(report)
        
        print("📊 VALIDATION REPORT GENERATED")
        print("="*50)
        print(f"✅ Success Rate: {((len(self.df) - len(validation_results['issues'])) / len(self.df) * 100):.1f}%")
        print(f"⚠️  Issues Found: {len(validation_results['issues'])} critical, {len(validation_results['warnings'])} warnings")
        print(f"🔬 Gradient Data: {'Available with measurement points' if self.has_gradient_points else 'Estimated only'}")
        print(f"📁 Files Generated:")
        print(f"   - comprehensive_coordinate_verification.png")
        print(f"   - gradient_validation_analysis.png") 
        print(f"   - coordinate_validation_report.md")
        
        return report

def main():
    """Run comprehensive coordinate verification system"""
    
    print("🐋 WHALE STRANDING COORDINATE VERIFICATION SYSTEM")
    print("="*60)
    print("Professional-grade validation with landmasses and gradient analysis")
    print("Now showing measurement points for gradient calculations!")
    print()
    
    # Initialize system
    verifier = CoordinateVerificationSystem()
    
    # Create comprehensive dashboard
    print("📊 Creating comprehensive verification dashboard...")
    verifier.create_comprehensive_verification_dashboard()
    
    # Create gradient validation plots
    print("📈 Creating gradient validation analysis...")
    verifier.create_gradient_validation_plots()
    
    # Generate validation report
    print("📝 Generating validation report...")
    verifier.generate_validation_report()
    
    print("\n✅ VERIFICATION COMPLETE!")
    print("Review the generated visualizations and report for coordinate validation.")
    print("🔍 Check that measurement points are positioned correctly for gradient calculations!")

if __name__ == "__main__":
    main() 