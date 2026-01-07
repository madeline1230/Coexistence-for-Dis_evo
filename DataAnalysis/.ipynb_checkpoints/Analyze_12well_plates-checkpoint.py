#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
12-Well Plate Strain Competition Analyzer
Analyzes pairs 1, 2, and 8 from 12-well plate data (C_ format)
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import re
import warnings
warnings.filterwarnings('ignore')

# Clean matplotlib styling
plt.style.use('default')
plt.rcParams.update({
    'font.size': 11,
    'axes.titlesize': 13,
    'axes.labelsize': 11,
    'legend.fontsize': 9,
    'figure.titlesize': 15,
    'axes.spines.top': False,
    'axes.spines.right': False,
    'axes.grid': True,
    'grid.alpha': 0.3,
    'figure.facecolor': 'white',
    'axes.facecolor': 'white'
})

class TwelveWellAnalyzer:
    def __init__(self, barcode_file, platemap_file):
        self.barcode_file = barcode_file
        self.platemap_file = platemap_file
        
        # Load data
        self.barcode_data = pd.read_csv(barcode_file)
        self.plate_map = self._load_plate_map()
        
        # Define strain pairs (just the 12-well ones)
        self.strain_pairs = {
            'Pair1': ['P3_B3', 'P3_H1'],
            'Pair2': ['P3_C1', 'P3_G7'], 
            'Pair8': ['P4_F2', 'P3_D9']
        }
        
        # Strain colors
        self.strain_colors = {
            'P3B3': '#FF6B6B',   'P3H1': '#4ECDC4',   
            'P3C1': '#45B7D1',   'P3G7': '#96CEB4',   
            'P4F2': '#BB8FCE',   'P3D9': '#85C1E9'
        }
    
    def _load_plate_map(self):
        """Load plate map - focuses on C_ (control/12-well) entries"""
        df = pd.read_csv(self.platemap_file)
        plate_map = {}
        
        for _, row in df.iterrows():
            plate = row['PLATE']
            well = row['WELL']
            condition_str = str(row[df.columns[2]]).strip()
            
            parts = condition_str.split('_')
            key = f"P{plate}_{well}"
            
            # Only load C_ entries (12-well plate data)
            if len(parts) >= 5 and parts[0] == 'C':
                plate_map[key] = {
                    'pair': parts[1],
                    'condition': parts[2],
                    'replicate': parts[3],
                    'timepoint': parts[4]
                }
        
        print(f"Loaded {len(plate_map)} wells from 12-well plates")
        return plate_map
    
    def _get_strain_color(self, barcode):
        if barcode in self.strain_colors:
            return self.strain_colors[barcode]
        return '#999999'  # Gray fallback
    
    def _parse_column_name(self, col_name):
        """Parse column names like 'CoexP2_C1'"""
        if col_name == 'BCID':
            return None
        match = re.match(r'CoexP(\d+)_([A-H]\d+)', col_name)
        if match:
            return {'plate': int(match.group(1)), 'well': match.group(2)}
        return None
    
    def process_all_data(self):
        """Process barcode data with plate map metadata"""
        all_data = []
        barcode_col = self.barcode_data.columns[0]
        
        for col in self.barcode_data.columns[1:]:
            parsed = self._parse_column_name(col)
            if not parsed:
                continue
            
            key = f"P{parsed['plate']}_{parsed['well']}"
            if key not in self.plate_map:
                continue
            
            metadata = self.plate_map[key]
            
            # Get barcode frequencies for this sample
            sample_data = self.barcode_data[[barcode_col, col]].copy()
            sample_data = sample_data[sample_data[col] > 0]
            
            for _, row in sample_data.iterrows():
                try:
                    timepoint = int(metadata['timepoint'])
                except (ValueError, KeyError):
                    continue
                    
                all_data.append({
                    'barcode': row[barcode_col],
                    'frequency': row[col],
                    'pair': metadata['pair'],
                    'condition': metadata['condition'],
                    'timepoint': timepoint,
                    'replicate': metadata['replicate']
                })
        
        return pd.DataFrame(all_data)
    
    def create_pair_plot(self, pair_number):
        """Create competition plot for a specific pair"""
        df = self.process_all_data()
        pair_str = str(pair_number)
        pair_data = df[df['pair'] == pair_str].copy()
        
        if pair_data.empty:
            print(f"No data found for Pair {pair_number}")
            return
        
        pair_key = f'Pair{pair_number}'
        if pair_key not in self.strain_pairs:
            print(f"Pair {pair_number} not defined")
            return
        
        strain_1, strain_2 = self.strain_pairs[pair_key]
        expected_strain_1 = strain_1.replace('_', '')
        expected_strain_2 = strain_2.replace('_', '')
        
        conditions = sorted(pair_data['condition'].unique())
        
        # Setup subplots
        n_cond = len(conditions)
        if n_cond <= 4:
            fig, axes = plt.subplots(2, 2, figsize=(14, 10))
            axes_flat = axes.flatten()
        else:
            rows = int(np.ceil(n_cond / 3))
            fig, axes = plt.subplots(rows, 3, figsize=(16, 5*rows))
            axes_flat = axes.flatten() if rows > 1 else [axes]
        
        fig.suptitle(f'Pair {pair_number}: {strain_1} vs {strain_2} (12-well plate)', 
                     fontweight='bold', fontsize=16)
        
        # Plot each condition
        for i, condition in enumerate(conditions):
            if i >= len(axes_flat):
                break
            
            ax = axes_flat[i]
            cond_data = pair_data[pair_data['condition'] == condition].copy()
            
            # Group and normalize
            grouped = cond_data.groupby(['timepoint', 'replicate', 'barcode'])['frequency'].sum().reset_index()
            
            # Two-strain normalization
            for tp in grouped['timepoint'].unique():
                for rep in grouped['replicate'].unique():
                    mask = (grouped['timepoint'] == tp) & (grouped['replicate'] == rep)
                    tp_rep_data = grouped[mask]
                    
                    s1_freq = tp_rep_data[tp_rep_data['barcode'] == expected_strain_1]['frequency'].sum()
                    s2_freq = tp_rep_data[tp_rep_data['barcode'] == expected_strain_2]['frequency'].sum()
                    total = s1_freq + s2_freq
                    
                    if total > 0:
                        grouped.loc[mask & (grouped['barcode'] == expected_strain_1), 'frequency'] = s1_freq / total
                        grouped.loc[mask & (grouped['barcode'] == expected_strain_2), 'frequency'] = s2_freq / total
                        grouped.loc[mask & (~grouped['barcode'].isin([expected_strain_1, expected_strain_2])), 'frequency'] = 0
            
            # Plot both strains
            for barcode in [expected_strain_1, expected_strain_2]:
                strain_data = grouped[grouped['barcode'] == barcode]
                if strain_data.empty:
                    continue
                
                color = self._get_strain_color(barcode)
                
                for rep in sorted(strain_data['replicate'].unique()):
                    rep_data = strain_data[strain_data['replicate'] == rep].sort_values('timepoint')
                    
                    if not rep_data.empty:
                        linestyle = '-' if rep == '1' else '--'
                        alpha = 0.9 if rep == '1' else 0.7
                        label = f'{barcode}' + (f' (R{rep})' if len(strain_data['replicate'].unique()) > 1 else '')
                        
                        ax.plot(rep_data['timepoint'], rep_data['frequency'],
                               marker='o', linewidth=3, markersize=8, color=color,
                               linestyle=linestyle, alpha=alpha, label=label,
                               markeredgecolor='white', markeredgewidth=0.5)
            
            # Style subplot
            ax.set_xlabel('Timepoint', fontweight='bold')
            ax.set_ylabel('Relative Frequency', fontweight='bold')
            ax.set_title(condition, fontweight='bold', pad=15)
            
            timepoints = sorted(grouped['timepoint'].unique())
            if timepoints:
                ax.set_xticks(timepoints)
                ax.set_xlim(min(timepoints) - 0.5, max(timepoints) + 0.5)
            
            ax.set_ylim(0, 1.05)
            ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: f'{y:.2f}'))
            ax.axhline(y=0.5, color='gray', linestyle=':', alpha=0.5, linewidth=1)
            ax.legend(loc='best', frameon=True, fancybox=True, shadow=True, framealpha=0.9)
        
        # Hide empty subplots
        for idx in range(len(conditions), len(axes_flat)):
            axes_flat[idx].set_visible(False)
        
        plt.tight_layout()
        plt.savefig(f'Images/Pair{pair_number}_competition.png', dpi=300, bbox_inches='tight')
        plt.show()
        print(f"Plot saved as Images/12well_Pair{pair_number}_competition.png")
    
    def analyze_all_12well_pairs(self):
        """Analyze all three 12-well pairs"""
        for pair_num in [1, 2, 8]:
            print(f"\nProcessing Pair {pair_num}...")
            self.create_pair_plot(pair_num)
    
    def export_processed_data(self, output_file='12well_competition_data.csv'):
        """Export processed data"""
        df = self.process_all_data()
        df.to_csv(output_file, index=False)
        print(f"Data exported to {output_file}")
        return df


def main():
    """Run analysis"""
    # File paths
    barcode_file = "barcodecounts_clean.csv"
    platemap_file = "Coexistance_Assay_plate_map.csv"
    
    # Initialize analyzer
    analyzer = TwelveWellAnalyzer(barcode_file, platemap_file)
    
    # Analyze all 12-well pairs
    analyzer.analyze_all_12well_pairs()
    
    # Export data
    analyzer.export_processed_data()


if __name__ == "__main__":
    main()