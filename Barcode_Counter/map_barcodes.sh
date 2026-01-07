#!/bin/bash
#SBATCH --job-name=map_FitAssay
#SBATCH --output=SlurmFiles/map_%A_%a.out
#SBATCH --error=logs/error_%A_%a.err
#SBATCH --nodes=1
#SBATCH --cpus-per-task=16
#SBATCH --time=24:00:00
#SBATCH --mem=32G
#SBATCH --mail-user=mfl8805@nyu.edu
#SBATCH --mail-type=END

# Unload modules
module purge

# Load modules
module load python/intel/3.8.6
module load bowtie2/2.4.4
module load biopython/intel/1.74
module load blast+/2.15.0

python /scratch/cgsb/abreu/Software/BarcodeCounter/BarcodeCounter2-master_11162021update/barcodeCounter.py \
-fastqDir /scratch/mfl8805/Coexistence_Assays/Barcode_Counter/rawData/ \
-outputDir /scratch/mfl8805/Coexistence_Assays/Barcode_Counter/BarcodeCounts/ \
-templateSeq /scratch/mfl8805/Coexistence_Assays/Barcode_Counter/Template.txt \
-sample /scratch/mfl8805/Coexistence_Assays/Barcode_Counter/Samples.txt \
-multiBCFasta /scratch/mfl8805/Coexistence_Assays/Barcode_Counter/Primers.fasta \
-pairedEnd \
-numThreads 16 \
-skipSplitFastq \
-barcodeList /scratch/mfl8805/Coexistence_Assays/Barcode_Counter/CoexAssay_BClist.fa \
-useBowtie2 \
-readLength 108 \
-remapBarcodes
