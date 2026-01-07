#!/usr/bin/env python3
"""
Script to rename fastq files from GRN6V format to simplified CoexP format with R1/R2
Original: 000000000-GRN6V_l01_n01_CoexP1_1__A1.fastq.gz -> New: CoexP1_A1_R1.fastq.gz
Original: 000000000-GRN6V_l01_n02_CoexP1_1__A1.fastq.gz -> New: CoexP1_A1_R2.fastq.gz
"""

import os
import re
import shutil
import argparse
from pathlib import Path


def rename_fastq_files(fastq_dir, output_dir=None, dry_run=False, use_symlinks=False):
    """
    Rename fastq files from GRN6V format to simplified CoexP format with R1/R2
    
    Parameters:
    fastq_dir (str): Directory containing fastq files
    output_dir (str): Output directory for renamed files (optional, defaults to same as input)
    dry_run (bool): If True, only show what would be renamed without actually renaming
    use_symlinks (bool): If True, create symlinks instead of copying files
    """
    
    fastq_path = Path(fastq_dir)
    
    if not fastq_path.exists():
        print(f"Error: Directory {fastq_dir} does not exist")
        return
    
    # Set output directory
    if output_dir:
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
    else:
        output_path = fastq_path
    
    # Pattern to match the original file format including n01/n02 for R1/R2
    pattern = re.compile(r'000000000-GRN6V_l01_n0([12])_([^_]+)_\d+__([^.]+)\.fastq\.gz')
    
    files_to_rename = []
    
    # Find all matching files
    for file_path in fastq_path.glob("*.fastq.gz"):
        match = pattern.match(file_path.name)
        if match:
            read_num = match.group(1)      # 1 or 2
            project_name = match.group(2)  # e.g., "CoexP1"
            sample_name = match.group(3)   # e.g., "A1"
            
            # ZERO-PAD THE WELL NUMBERS
            well_match = re.match(r'([A-Z]+)(\d+)', sample_name)
            if well_match:
                letter = well_match.group(1)
                number = well_match.group(2).zfill(2)  # Zero-pad to 2 digits
                sample_name_padded = f"{letter}{number}"
            else:
                sample_name_padded = sample_name
            
            # Create new filename with R1/R2 and zero-padded well numbers
            new_name = f"{project_name}_{sample_name_padded}_R{read_num}.fastq.gz"
            new_path = output_path / new_name
            
            files_to_rename.append((file_path, new_path))
        
    if not files_to_rename:
        print("No files matching the expected pattern found.")
        print("Expected pattern: 000000000-GRN6V_l01_n0[1-2]_[project]_[number]__[sample].fastq.gz")
        return
    
    # Sort by sample name and read number for cleaner output
    files_to_rename.sort(key=lambda x: (x[1].name.split('_')[1], x[1].name))
    
    print(f"Found {len(files_to_rename)} files to rename:")
    if output_dir:
        print(f"Output directory: {output_path}")
        if use_symlinks:
            print("Mode: Creating symlinks")
        else:
            print("Mode: Copying files")
    else:
        print("Mode: Renaming in place")
    print("-" * 80)
    
    success_count = 0
    error_count = 0
    
    for old_path, new_path in files_to_rename:
        if dry_run:
            action = "symlink" if use_symlinks and output_dir else "rename/copy"
            print(f"Would {action}: {old_path.name} -> {new_path.name}")
        else:
            try:
                # Check if new filename already exists
                if new_path.exists() or new_path.is_symlink():
                    print(f"Warning: {new_path.name} already exists, skipping {old_path.name}")
                    error_count += 1
                    continue
                
                # Perform the operation based on mode
                if output_dir:
                    if use_symlinks:
                        # Create symlink
                        new_path.symlink_to(old_path.absolute())
                        print(f"Symlinked: {old_path.name} -> {new_path.name}")
                    else:
                        # Copy file
                        shutil.copy2(old_path, new_path)
                        print(f"Copied: {old_path.name} -> {new_path.name}")
                else:
                    # Rename in place
                    old_path.rename(new_path)
                    print(f"Renamed: {old_path.name} -> {new_path.name}")
                
                success_count += 1
                
            except Exception as e:
                print(f"Error processing {old_path.name}: {e}")
                error_count += 1
    
    print("-" * 80)
    if dry_run:
        print(f"Dry run complete. {len(files_to_rename)} files would be processed.")
    else:
        print(f"Processing complete. {success_count} files processed successfully.")
        if error_count > 0:
            print(f"{error_count} files had errors.")


def main():
    parser = argparse.ArgumentParser(
        description="Rename fastq files from GRN6V format to CoexP format with R1/R2",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Dry run to see what would be renamed
  python rename.py /path/to/fastq/files --dry-run
  
  # Rename files in place
  python rename.py /path/to/fastq/files
  
  # Copy files with new names to output directory
  python rename.py /path/to/fastq/files --output-dir /path/to/output
  
  # Create symlinks with new names to output directory
  python rename.py /path/to/fastq/files --output-dir /path/to/output --symlinks
  
File format expected:
  000000000-GRN6V_l01_n01_CoexP1_1__A1.fastq.gz -> CoexP1_A1_R1.fastq.gz
  000000000-GRN6V_l01_n02_CoexP1_1__A1.fastq.gz -> CoexP1_A1_R2.fastq.gz
        """
    )
    
    parser.add_argument(
        "fastq_dir", 
        help="Directory containing fastq files to rename"
    )
    
    parser.add_argument(
        "--output-dir", "-o",
        help="Output directory for renamed files (if not specified, renames in place)"
    )
    
    parser.add_argument(
        "--symlinks", "-s",
        action="store_true",
        help="Create symlinks instead of copying (only works with --output-dir)"
    )
    
    parser.add_argument(
        "--dry-run", 
        action="store_true",
        help="Show what would be renamed without actually renaming files"
    )
    
    args = parser.parse_args()
    
    if args.symlinks and not args.output_dir:
        print("Warning: --symlinks requires --output-dir. Ignoring --symlinks flag.")
        args.symlinks = False
    
    rename_fastq_files(args.fastq_dir, args.output_dir, args.dry_run, args.symlinks)


if __name__ == "__main__":
    main()