#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Strain Competition Analyzer with Plate Map Integration
Uses plate map to automatically assign experimental conditions to barcode count data
@author: madelinelucas
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

class PlateMapStrainAnalyzer:
    def __init__(self, barcode_file, platemap_file):
        """
        Initialize analyzer with barcode counts and plate map
        
        Parameters:
        -----------
        barcode_file : str
            Path to CSV file with barcode counts (columns: BCID, CoexP1_A1, CoexP1_A2, etc.)
        platemap_file : str
            Path to CSV file with plate map (columns: PLATE, WELL, condition info)
        """
        self.barcode_file = barcode_file
        self.platemap_file = platemap_file
        
        # Load data
        self.barcode_data = pd.read_csv(barcode_file)
        self.plate_map = self._load_plate_map()
        
        # Define strain pairs
        self.strain_pairs = {
            'Pair1': ['P3_B3', 'P3_H1'], 'Pair2': ['P3_C1', 'P3_G7'], 
            'Pair3': ['P3_B3', 'P3_G7'], 'Pair4': ['P2_B1', 'P3_H5'],
            'Pair5': ['P2_B1', 'P4_G6'], 'Pair6': ['P3_C2', 'P4_G6'],
            'Pair7': ['P3_C2', 'P3_H5'], 'Pair8': ['P4_F2', 'P3_D9'],
            'Pair9': ['P4_F2', 'P3_A7'], 'Pair10': ['P4_F2', 'P5_F8'],
            'Pair11': ['P4_C11', 'P3_D9'], 'Pair12': ['P4_C11', 'P5_F8'],
            'Pair13': ['P4_C11', 'P3_A7']
        }
        
        # Strain colors for consistent plotting
        self.strain_colors = {
            'P3B3': '#FF6B6B',   'P3H1': '#4ECDC4',   'P3C1': '#45B7D1',
            'P3G7': '#96CEB4',   'P2B1': '#FFEAA7',   'P3H5': '#DDA0DD',
            'P4G6': '#98D8C8',   'P3C2': '#F7DC6F',   'P4F2': '#BB8FCE',
            'P3D9': '#85C1E9',   'P3A7': '#F8C471',   'P5F8': '#82E0AA',
            'P4C11': '#F1948A'
        }
    
    def _load_plate_map(self):
    df = pd.read_csv(self.platemap_file)
    plate_map = {}
    
        for _, row in df.iterrows():
            plate = row['PLATE']
            well = row['WELL']
            condition_str = row[df.columns[2]]  # Third column
            
            parts = condition_str.strip().split('_')
            key = f"P{plate}_{well}"
            
            # Handle special cases (SALT, GAL)
            if len(parts) > 1 and parts[1] in ['SALT', 'GAL']:
                plate_map[key] = {
                    'type': 'pair',
                    'pair': parts[2].replace('P', '') if len(parts) > 2 else 'Unknown',
                    'condition': parts[1],
                    'replicate': parts[3] if len(parts) > 3 else '1',
                    'timepoint': '1'
                }
            elif len(parts) >= 5:
                # Check if it's control (C_) or pair (P_)
                if parts[0] == 'C':
                    # TREAT CONTROLS AS PAIRS for plotting
                    plate_map[key] = {
                        'type': 'pair',  # Changed from 'control' to 'pair'
                        'pair': parts[1],  # Use control_id as pair number
                        'condition': parts[2],
                        'replicate': parts[3] if len(parts) > 3 else '1',
                        'timepoint': parts[4] if len(parts) > 4 else '1'
                    }
                elif parts[0] == 'P':
                    plate_map[key] = {
                        'type': 'pair',
                        'pair': parts[1],
                        'condition': parts[2],
                        'replicate': parts[3],
                        'timepoint': parts[4] if len(parts) > 4 else '1'
                    }
        
        return plate_map
    
    def _get_strain_color(self, barcode):
        """Get color for a strain"""
        if barcode in self.strain_colors:
            return self.strain_colors[barcode]
        # Fallback colors
        fallback_colors = ['#85D4E3', '#D7BDE2', '#A3E4D7', '#FAD7A0', '#AED6F1']
        return fallback_colors[hash(barcode) % len(fallback_colors)]
    
    def _parse_column_name(self, col_name):
        """
        Parse column names like 'CoexP2_E8' to extract plate and well
        
        Returns: {'plate': 2, 'well': 'E8'} or None
        """
        if col_name == 'BCID':
            return None
        
        # Match pattern: CoexP[plate]_[well]
        match = re.match(r'CoexP(\d+)_([A-H]\d+)', col_name)
        if match:
            return {
                'plate': int(match.group(1)),
                'well': match.group(2)
            }
        return None
    
    def process_all_data(self):
        """
        Process all barcode data using the plate map
        
        Returns: DataFrame with columns:
        - barcode: strain barcode
        - frequency: read count
        - pair: pair number
        - condition: experimental condition
        - timepoint: timepoint
        - replicate: replicate number
        """
        all_data = []
        
        # Get barcode column (first column)
        barcode_col = self.barcode_data.columns[0]
        
        # Process each sample column
        for col in self.barcode_data.columns[1:]:
            # Parse column name to get plate and well
            parsed = self._parse_column_name(col)
            if not parsed:
                continue
            
            # Look up this well in the plate map
            key = f"P{parsed['plate']}_{parsed['well']}"
            if key not in self.plate_map:
                print(f"Warning: {key} not found in plate map")
                continue
            
            metadata = self.plate_map[key]
            
            # Skip controls if you only want pairs
            if metadata['type'] != 'pair':
                continue
            
            # Get barcode frequencies for this sample
            sample_data = self.barcode_data[[barcode_col, col]].copy()
            sample_data = sample_data[sample_data[col] > 0]  # Only non-zero counts
            
            # Add metadata to each barcode
            for _, row in sample_data.iterrows():
                try:
                    timepoint = int(metadata['timepoint'])
                except (ValueError, KeyError):
                    # Skip samples with invalid timepoints
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
        """
        Create competition plot for a specific pair
        
        Parameters:
        -----------
        pair_number : int or str
            Pair number (e.g., 1 for Pair1)
        """
        # Get all data
        df = self.process_all_data()
        
        # Filter to this pair
        pair_str = str(pair_number)
        pair_data = df[df['pair'] == pair_str].copy()
        
        if pair_data.empty:
            print(f"No data found for Pair {pair_number}")
            return
        
        # Get strain names for this pair
        pair_key = f'Pair{pair_number}'
        if pair_key not in self.strain_pairs:
            print(f"Pair {pair_number} not defined in strain_pairs")
            return
        
        strain_1, strain_2 = self.strain_pairs[pair_key]
        expected_strain_1 = strain_1.replace('_', '')
        expected_strain_2 = strain_2.replace('_', '')
        
        # Get unique conditions
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
        
        fig.suptitle(f'Pair {pair_number}: {strain_1} vs {strain_2}', 
                     fontweight='bold', fontsize=16)
        
        # Plot each condition
        for i, condition in enumerate(conditions):
            if i >= len(axes_flat):
                break
            
            ax = axes_flat[i]
            cond_data = pair_data[pair_data['condition'] == condition].copy()
            
            # Group and normalize to two-strain system
            grouped = cond_data.groupby(['timepoint', 'replicate', 'barcode'])['frequency'].sum().reset_index()
            
            # Normalize each timepoint-replicate to just the two paired strains
            for tp in grouped['timepoint'].unique():
                for rep in grouped['replicate'].unique():
                    mask = (grouped['timepoint'] == tp) & (grouped['replicate'] == rep)
                    tp_rep_data = grouped[mask]
                    
                    # Get frequencies for the two main strains
                    s1_freq = tp_rep_data[tp_rep_data['barcode'] == expected_strain_1]['frequency'].sum()
                    s2_freq = tp_rep_data[tp_rep_data['barcode'] == expected_strain_2]['frequency'].sum()
                    
                    total = s1_freq + s2_freq
                    
                    if total > 0:
                        # Normalize: A/(A+B) and B/(A+B)
                        grouped.loc[mask & (grouped['barcode'] == expected_strain_1), 'frequency'] = s1_freq / total
                        grouped.loc[mask & (grouped['barcode'] == expected_strain_2), 'frequency'] = s2_freq / total
                        # Set others to 0
                        grouped.loc[mask & (~grouped['barcode'].isin([expected_strain_1, expected_strain_2])), 'frequency'] = 0
            
            # Plot the two main strains
            for barcode in [expected_strain_1, expected_strain_2]:
                strain_data = grouped[grouped['barcode'] == barcode]
                if strain_data.empty:
                    continue
                
                color = self._get_strain_color(barcode)
                
                # Plot each replicate
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
            
            # Set x-axis based on actual timepoints
            timepoints = sorted(grouped['timepoint'].unique())
            ax.set_xticks(timepoints)
            ax.set_xlim(min(timepoints) - 0.5, max(timepoints) + 0.5)
            
            ax.set_ylim(0, 1.05)
            ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: f'{y:.2f}'))
            ax.axhline(y=0.5, color='gray', linestyle=':', alpha=0.5, linewidth=1)
            
            ax.legend(loc='lower left', frameon=True, fancybox=True,
                     shadow=True, framealpha=0.9)
        
        # Hide empty subplots
        for idx in range(len(conditions), len(axes_flat)):
            axes_flat[idx].set_visible(False)
        
        plt.tight_layout()
        plt.savefig(f'Pair{pair_number}_competition.png', dpi=300, bbox_inches='tight')
        plt.show()
        print(f"Plot saved as Pair{pair_number}_competition.png")
    
    def analyze_all_pairs(self):
        """Generate plots for all pairs"""
        for pair_key in self.strain_pairs.keys():
            pair_num = pair_key.replace('Pair', '')
            print(f"\nProcessing {pair_key}...")
            self.create_pair_plot(pair_num)
    
    def export_processed_data(self, output_file='processed_competition_data.csv'):
        """Export all processed data to CSV"""
        df = self.process_all_data()
        df.to_csv(output_file, index=False)
        print(f"Data exported to {output_file}")
        return df
    
    def get_pair_summary(self, pair_number):
        """Get summary statistics for a pair"""
        df = self.process_all_data()
        pair_str = str(pair_number)
        pair_data = df[df['pair'] == pair_str]
        
        if pair_data.empty:
            print(f"No data for Pair {pair_number}")
            return None
        
        print(f"\n=== Pair {pair_number} Summary ===")
        print(f"Conditions: {sorted(pair_data['condition'].unique())}")
        print(f"Timepoints: {sorted(pair_data['timepoint'].unique())}")
        print(f"Replicates: {sorted(pair_data['replicate'].unique())}")
        print(f"Barcodes detected: {sorted(pair_data['barcode'].unique())}")
        print(f"Total samples: {len(pair_data)}")
        
        return pair_data


def main():
    """Example usage"""
    
    # File paths - UPDATE THESE
    barcode_file = "Coexistence_Assays/Data Analysis/barcodecounts_clean.csv"
    platemap_file = "Coexistence_Assays/Data Analysis/Coexistance_Assay_plate_map.csv"
    
    # Initialize analyzer
    analyzer = PlateMapStrainAnalyzer(barcode_file, platemap_file)
    
    # Analyze all pairs
    analyzer.analyze_all_pairs()
    
    # Export processed data
    analyzer.export_processed_data()
    
    # Or analyze specific pair
    # analyzer.create_pair_plot(1)
    
    # Get summary for specific pair
    # analyzer.get_pair_summary(1)


if __name__ == "__main__":
    main()
