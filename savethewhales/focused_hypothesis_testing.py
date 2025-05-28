#!/usr/bin/env python3
"""
Focused Hypothesis Testing with Expanded Magnetic Field Dataset
Test specific predictions of the Magnetic Barrier Hypothesis
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix
import warnings
warnings.filterwarnings('ignore')

class FocusedHypothesisTester:
    def __init__(self):
        self.enhanced_data = None
        self.literature_data = None
        self.combined_data = None
        
    def load_all_data(self):
        """Load both enhanced and literature datasets"""
        print("Loading all available magnetic field data...")
        
        try:
            self.enhanced_data = pd.read_csv('enhanced_magnetic_analysis.csv')
            self.literature_data = pd.read_csv('literature_magnetic_data.csv')
            print(f"Loaded {len(self.enhanced_data)} enhanced measurements")
            print(f"Loaded {len(self.literature_data)} literature-derived measurements")
        except FileNotFoundError as e:
            print(f"Error loading data: {e}")
            return None
        
        # Create combined dataset for analysis
        self.combined_data = self.literature_data.copy()
        
        # Add stranding classification
        self.combined_data['Has_Strandings'] = self.combined_data['Type'].apply(
            lambda x: 1 if x in ['control', 'hotspot'] else 0
        )
        
        # Add risk categories based on gradient
        def categorize_risk(gradient):
            if gradient > 15:
                return 'VERY_HIGH'
            elif gradient > 5:
                return 'HIGH'
            elif gradient > 0:
                return 'MEDIUM'
            elif gradient > -5:
                return 'LOW'
            else:
                return 'VERY_LOW'
        
        self.combined_data['Risk_Category'] = self.combined_data['Estimated_Gradient'].apply(categorize_risk)
        
        return self.combined_data
    
    def test_threshold_hypothesis(self):
        """Test the hypothesis that there's a critical gradient threshold for strandings"""
        print("\n" + "="*60)
        print("TESTING THRESHOLD HYPOTHESIS")
        print("="*60)
        
        df = self.combined_data
        
        # Test multiple threshold values
        thresholds = np.arange(-5, 25, 0.5)
        accuracies = []
        sensitivities = []
        specificities = []
        
        for threshold in thresholds:
            predicted = (df['Estimated_Gradient'] > threshold).astype(int)
            actual = df['Has_Strandings']
            
            # Calculate metrics
            tp = ((predicted == 1) & (actual == 1)).sum()
            tn = ((predicted == 0) & (actual == 0)).sum()
            fp = ((predicted == 1) & (actual == 0)).sum()
            fn = ((predicted == 0) & (actual == 1)).sum()
            
            accuracy = (tp + tn) / len(df) if len(df) > 0 else 0
            sensitivity = tp / (tp + fn) if (tp + fn) > 0 else 0
            specificity = tn / (tn + fp) if (tn + fp) > 0 else 0
            
            accuracies.append(accuracy)
            sensitivities.append(sensitivity)
            specificities.append(specificity)
        
        # Find optimal threshold
        best_idx = np.argmax(accuracies)
        optimal_threshold = thresholds[best_idx]
        best_accuracy = accuracies[best_idx]
        
        print(f"OPTIMAL THRESHOLD ANALYSIS:")
        print(f"• Optimal gradient threshold: {optimal_threshold:.1f} nT/km")
        print(f"• Maximum accuracy: {best_accuracy:.1%}")
        print(f"• Sensitivity at optimal: {sensitivities[best_idx]:.1%}")
        print(f"• Specificity at optimal: {specificities[best_idx]:.1%}")
        
        # Test specific thresholds of interest
        test_thresholds = [0, 5, 10, 15, 20]
        print(f"\nTHRESHOLD PERFORMANCE COMPARISON:")
        
        for thresh in test_thresholds:
            predicted = (df['Estimated_Gradient'] > thresh).astype(int)
            actual = df['Has_Strandings']
            accuracy = (predicted == actual).mean()
            
            # Confusion matrix
            tp = ((predicted == 1) & (actual == 1)).sum()
            tn = ((predicted == 0) & (actual == 0)).sum()
            fp = ((predicted == 1) & (actual == 0)).sum()
            fn = ((predicted == 0) & (actual == 1)).sum()
            
            print(f"• Threshold {thresh:2.0f} nT/km: Accuracy {accuracy:.1%} (TP:{tp}, TN:{tn}, FP:{fp}, FN:{fn})")
        
        return {
            'optimal_threshold': optimal_threshold,
            'best_accuracy': best_accuracy,
            'thresholds': thresholds,
            'accuracies': accuracies,
            'sensitivities': sensitivities,
            'specificities': specificities
        }
    
    def test_regional_patterns(self):
        """Test for regional patterns in magnetic gradients and strandings"""
        print("\n" + "="*60)
        print("TESTING REGIONAL PATTERNS")
        print("="*60)
        
        df = self.combined_data
        
        # Define regions based on coordinates
        def assign_region(row):
            lat, lon = row['Latitude'], row['Longitude']
            
            if lat > 50:
                return 'Arctic/Subarctic'
            elif lat > 30:
                if -100 < lon < -60:
                    return 'North_Atlantic_West'
                elif -30 < lon < 30:
                    return 'North_Atlantic_East'
                else:
                    return 'North_Pacific'
            elif lat > -30:
                return 'Tropical'
            else:
                if 140 < lon < 180:
                    return 'South_Pacific_West'
                else:
                    return 'South_Pacific_East'
        
        df['Region'] = df.apply(assign_region, axis=1)
        
        # Analyze by region
        regional_stats = df.groupby('Region').agg({
            'Estimated_Gradient': ['mean', 'std', 'count'],
            'Has_Strandings': ['sum', 'mean']
        }).round(2)
        
        print("REGIONAL ANALYSIS:")
        print(regional_stats)
        
        # Test for significant differences between regions
        regions = df['Region'].unique()
        if len(regions) > 1:
            region_gradients = [df[df['Region'] == region]['Estimated_Gradient'].values 
                              for region in regions]
            
            # ANOVA test
            f_stat, p_value = stats.f_oneway(*region_gradients)
            print(f"\nREGIONAL DIFFERENCES:")
            print(f"• ANOVA F-statistic: {f_stat:.3f}")
            print(f"• P-value: {p_value:.3f}")
            print(f"• Significant regional differences: {'YES' if p_value < 0.05 else 'NO'}")
        
        return regional_stats
    
    def test_new_zealand_anomaly(self):
        """Specifically test the New Zealand anomaly (extremely high gradients)"""
        print("\n" + "="*60)
        print("TESTING NEW ZEALAND ANOMALY")
        print("="*60)
        
        df = self.combined_data
        
        # Identify New Zealand sites
        nz_sites = df[df['Location'].str.contains('NZ|New Zealand', case=False, na=False)]
        other_sites = df[~df['Location'].str.contains('NZ|New Zealand', case=False, na=False)]
        
        if len(nz_sites) > 0 and len(other_sites) > 0:
            nz_gradients = nz_sites['Estimated_Gradient']
            other_gradients = other_sites['Estimated_Gradient']
            
            # Statistical comparison
            t_stat, p_value = stats.ttest_ind(nz_gradients, other_gradients)
            
            print(f"NEW ZEALAND vs REST OF WORLD:")
            print(f"• NZ sites mean gradient: {nz_gradients.mean():.2f} ± {nz_gradients.std():.2f} nT/km")
            print(f"• Other sites mean gradient: {other_gradients.mean():.2f} ± {other_gradients.std():.2f} nT/km")
            print(f"• Difference: {nz_gradients.mean() - other_gradients.mean():.2f} nT/km")
            print(f"• T-statistic: {t_stat:.3f}")
            print(f"• P-value: {p_value:.3f}")
            print(f"• Statistically significant: {'YES' if p_value < 0.05 else 'NO'}")
            
            # Effect size (Cohen's d)
            pooled_std = np.sqrt(((len(nz_gradients)-1)*nz_gradients.var() + 
                                 (len(other_gradients)-1)*other_gradients.var()) / 
                                (len(nz_gradients) + len(other_gradients) - 2))
            cohens_d = (nz_gradients.mean() - other_gradients.mean()) / pooled_std
            print(f"• Effect size (Cohen's d): {cohens_d:.2f}")
            
            # Interpretation
            if abs(cohens_d) > 0.8:
                effect_size = "LARGE"
            elif abs(cohens_d) > 0.5:
                effect_size = "MEDIUM"
            elif abs(cohens_d) > 0.2:
                effect_size = "SMALL"
            else:
                effect_size = "NEGLIGIBLE"
            
            print(f"• Effect size interpretation: {effect_size}")
            
            return {
                'nz_mean': nz_gradients.mean(),
                'other_mean': other_gradients.mean(),
                'p_value': p_value,
                'cohens_d': cohens_d,
                'effect_size': effect_size
            }
        
        return None
    
    def test_predictive_model(self):
        """Build and test a predictive model for stranding risk"""
        print("\n" + "="*60)
        print("TESTING PREDICTIVE MODEL")
        print("="*60)
        
        df = self.combined_data.copy()
        
        # Prepare features
        X = df[['Estimated_Gradient', 'Latitude', 'Longitude']].values
        y = df['Has_Strandings'].values
        
        # Fit logistic regression
        model = LogisticRegression(random_state=42)
        model.fit(X, y)
        
        # Predictions
        y_pred = model.predict(X)
        y_prob = model.predict_proba(X)[:, 1]
        
        # Model performance
        accuracy = (y_pred == y).mean()
        
        print(f"PREDICTIVE MODEL RESULTS:")
        print(f"• Model accuracy: {accuracy:.1%}")
        print(f"• Feature coefficients:")
        print(f"  - Gradient: {model.coef_[0][0]:.3f}")
        print(f"  - Latitude: {model.coef_[0][1]:.3f}")
        print(f"  - Longitude: {model.coef_[0][2]:.3f}")
        
        # Feature importance (absolute coefficients)
        feature_names = ['Gradient', 'Latitude', 'Longitude']
        importance = np.abs(model.coef_[0])
        importance_normalized = importance / importance.sum()
        
        print(f"• Feature importance:")
        for name, imp in zip(feature_names, importance_normalized):
            print(f"  - {name}: {imp:.1%}")
        
        # Confusion matrix
        tn, fp, fn, tp = confusion_matrix(y, y_pred).ravel()
        print(f"• Confusion Matrix:")
        print(f"  - True Negatives: {tn}")
        print(f"  - False Positives: {fp}")
        print(f"  - False Negatives: {fn}")
        print(f"  - True Positives: {tp}")
        
        # Predict risk for each site
        df['Predicted_Risk'] = y_prob
        df['Predicted_Stranding'] = y_pred
        
        print(f"\nHIGHEST RISK SITES (by model):")
        high_risk = df.nlargest(5, 'Predicted_Risk')[['Location', 'Estimated_Gradient', 'Predicted_Risk', 'Has_Strandings']]
        for _, row in high_risk.iterrows():
            actual = "STRANDINGS" if row['Has_Strandings'] else "NO STRANDINGS"
            print(f"• {row['Location']}: {row['Predicted_Risk']:.1%} risk ({actual})")
        
        return {
            'model': model,
            'accuracy': accuracy,
            'feature_importance': dict(zip(feature_names, importance_normalized)),
            'predictions': df[['Location', 'Predicted_Risk', 'Predicted_Stranding']]
        }
    
    def test_literature_consistency(self):
        """Test consistency between measured and literature-derived values"""
        print("\n" + "="*60)
        print("TESTING LITERATURE CONSISTENCY")
        print("="*60)
        
        df = self.combined_data
        
        # Compare measured vs estimated values for overlapping regions
        measured_sites = df[df['Source'] == 'Measured']
        literature_sites = df[df['Source'] != 'Measured']
        
        print(f"DATA SOURCE COMPARISON:")
        print(f"• Measured sites: {len(measured_sites)}")
        print(f"• Literature-derived sites: {len(literature_sites)}")
        
        # Compare gradient distributions
        if len(measured_sites) > 0 and len(literature_sites) > 0:
            measured_gradients = measured_sites['Estimated_Gradient']
            literature_gradients = literature_sites['Estimated_Gradient']
            
            # Statistical comparison
            t_stat, p_value = stats.ttest_ind(measured_gradients, literature_gradients)
            
            print(f"• Measured sites mean: {measured_gradients.mean():.2f} ± {measured_gradients.std():.2f} nT/km")
            print(f"• Literature sites mean: {literature_gradients.mean():.2f} ± {literature_gradients.std():.2f} nT/km")
            print(f"• Statistical difference: p = {p_value:.3f}")
            
            # Check for outliers in each dataset
            measured_outliers = measured_sites[np.abs(measured_sites['Estimated_Gradient'] - measured_gradients.mean()) > 2*measured_gradients.std()]
            literature_outliers = literature_sites[np.abs(literature_sites['Estimated_Gradient'] - literature_gradients.mean()) > 2*literature_gradients.std()]
            
            print(f"• Measured outliers: {len(measured_outliers)}")
            if len(measured_outliers) > 0:
                for _, row in measured_outliers.iterrows():
                    print(f"  - {row['Location']}: {row['Estimated_Gradient']:.1f} nT/km")
            
            print(f"• Literature outliers: {len(literature_outliers)}")
            if len(literature_outliers) > 0:
                for _, row in literature_outliers.iterrows():
                    print(f"  - {row['Location']}: {row['Estimated_Gradient']:.1f} nT/km")
        
        return {
            'measured_mean': measured_gradients.mean() if len(measured_sites) > 0 else None,
            'literature_mean': literature_gradients.mean() if len(literature_sites) > 0 else None,
            'consistency_p_value': p_value if len(measured_sites) > 0 and len(literature_sites) > 0 else None
        }
    
    def create_comprehensive_test_visualization(self, threshold_results, nz_results, model_results):
        """Create comprehensive visualization of all hypothesis tests"""
        print("\nCreating comprehensive test visualizations...")
        
        fig, axes = plt.subplots(2, 3, figsize=(18, 12))
        
        df = self.combined_data
        
        # 1. Threshold analysis
        ax1 = axes[0, 0]
        ax1.plot(threshold_results['thresholds'], threshold_results['accuracies'], 'b-', linewidth=2, label='Accuracy')
        ax1.plot(threshold_results['thresholds'], threshold_results['sensitivities'], 'r--', linewidth=2, label='Sensitivity')
        ax1.plot(threshold_results['thresholds'], threshold_results['specificities'], 'g--', linewidth=2, label='Specificity')
        ax1.axvline(threshold_results['optimal_threshold'], color='orange', linestyle=':', linewidth=2, label=f"Optimal ({threshold_results['optimal_threshold']:.1f})")
        ax1.set_xlabel('Gradient Threshold (nT/km)')
        ax1.set_ylabel('Performance Metric')
        ax1.set_title('Threshold Performance Analysis')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # 2. Gradient vs stranding scatter
        ax2 = axes[0, 1]
        colors = ['red' if x == 1 else 'blue' for x in df['Has_Strandings']]
        sizes = [100 if 'NZ' in loc else 60 for loc in df['Location']]
        ax2.scatter(df['Estimated_Gradient'], df['Latitude'], c=colors, s=sizes, alpha=0.7, edgecolors='black')
        ax2.axvline(threshold_results['optimal_threshold'], color='orange', linestyle='--', alpha=0.7)
        ax2.set_xlabel('Magnetic Gradient (nT/km)')
        ax2.set_ylabel('Latitude')
        ax2.set_title('Gradient vs Location (Red=Strandings, Blue=No Strandings)')
        
        # 3. Regional comparison
        ax3 = axes[0, 2]
        regional_means = df.groupby('Region')['Estimated_Gradient'].mean().sort_values(ascending=False)
        ax3.bar(range(len(regional_means)), regional_means.values, color='skyblue', edgecolor='black')
        ax3.set_xticks(range(len(regional_means)))
        ax3.set_xticklabels(regional_means.index, rotation=45, ha='right')
        ax3.set_ylabel('Mean Gradient (nT/km)')
        ax3.set_title('Mean Gradient by Region')
        
        # 4. New Zealand anomaly
        ax4 = axes[1, 0]
        nz_data = df[df['Location'].str.contains('NZ', case=False, na=False)]['Estimated_Gradient']
        other_data = df[~df['Location'].str.contains('NZ', case=False, na=False)]['Estimated_Gradient']
        ax4.boxplot([other_data, nz_data], labels=['Rest of World', 'New Zealand'])
        ax4.set_ylabel('Magnetic Gradient (nT/km)')
        ax4.set_title('New Zealand Anomaly')
        if nz_results:
            ax4.text(0.05, 0.95, f"p = {nz_results['p_value']:.3f}\nCohen's d = {nz_results['cohens_d']:.2f}", 
                    transform=ax4.transAxes, bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
        
        # 5. Model predictions
        ax5 = axes[1, 1]
        predictions = model_results['predictions']
        scatter = ax5.scatter(df['Estimated_Gradient'], predictions['Predicted_Risk'], 
                             c=df['Has_Strandings'], cmap='RdBu_r', s=80, alpha=0.7, edgecolors='black')
        ax5.set_xlabel('Magnetic Gradient (nT/km)')
        ax5.set_ylabel('Predicted Stranding Risk')
        ax5.set_title('Model Predictions vs Actual Gradients')
        plt.colorbar(scatter, ax=ax5, label='Actual Strandings')
        
        # 6. Summary statistics
        ax6 = axes[1, 2]
        ax6.axis('off')
        
        summary_text = "HYPOTHESIS TEST SUMMARY\n" + "="*25 + "\n\n"
        summary_text += f"Optimal Threshold: {threshold_results['optimal_threshold']:.1f} nT/km\n"
        summary_text += f"Threshold Accuracy: {threshold_results['best_accuracy']:.1%}\n\n"
        
        summary_text += f"Model Accuracy: {model_results['accuracy']:.1%}\n"
        summary_text += f"Gradient Importance: {model_results['feature_importance']['Gradient']:.1%}\n\n"
        
        if nz_results:
            summary_text += f"NZ Anomaly: {nz_results['effect_size']}\n"
            summary_text += f"NZ vs Others: p = {nz_results['p_value']:.3f}\n\n"
        
        summary_text += f"Total Sites: {len(df)}\n"
        summary_text += f"Stranding Sites: {df['Has_Strandings'].sum()}\n"
        summary_text += f"Control Sites: {len(df) - df['Has_Strandings'].sum()}\n"
        
        ax6.text(0.05, 0.95, summary_text, transform=ax6.transAxes, fontsize=11,
                verticalalignment='top', fontfamily='monospace',
                bbox=dict(boxstyle='round', facecolor='lightgray', alpha=0.8))
        
        plt.tight_layout()
        plt.savefig('focused_hypothesis_testing.png', dpi=300, bbox_inches='tight')
        print("Hypothesis testing visualization saved as 'focused_hypothesis_testing.png'")
        
        return fig

def main():
    """Run focused hypothesis testing"""
    print("FOCUSED HYPOTHESIS TESTING - MAGNETIC BARRIER HYPOTHESIS")
    print("="*65)
    
    tester = FocusedHypothesisTester()
    
    # Load all available data
    combined_data = tester.load_all_data()
    if combined_data is None:
        return None
    
    # Run hypothesis tests
    threshold_results = tester.test_threshold_hypothesis()
    regional_results = tester.test_regional_patterns()
    nz_results = tester.test_new_zealand_anomaly()
    model_results = tester.test_predictive_model()
    consistency_results = tester.test_literature_consistency()
    
    # Create comprehensive visualization
    tester.create_comprehensive_test_visualization(threshold_results, nz_results, model_results)
    
    # Save results
    results_summary = {
        'threshold': threshold_results,
        'regional': regional_results.to_dict() if regional_results is not None else None,
        'new_zealand': nz_results,
        'model': {k: v for k, v in model_results.items() if k != 'model'},  # Exclude model object
        'consistency': consistency_results
    }
    
    # Save to file
    import json
    with open('hypothesis_test_results.json', 'w') as f:
        json.dump(results_summary, f, indent=2, default=str)
    
    print(f"\nResults saved to 'hypothesis_test_results.json'")
    
    return tester, results_summary

if __name__ == "__main__":
    tester, results = main() 