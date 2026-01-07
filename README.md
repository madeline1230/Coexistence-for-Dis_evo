# ILLUMINA SEQUENCE 
# RUN INFORMATION:
- Coexistance Assay Plates 1 and 2
- MLY 48 MLY 58 AND DTY 30 check FOR DIVERSITY
- SALT vs Galatose mutatant validation comparison against FACS machine, P4E1,P4E2,P4E3 strains
# This Coexistance Assay was done to check for preliminary coexistance of possible mutant strains. 

There are 13 pairs to be checked 
1. P3 B3(HF)/ P3 H1(N)    EXPECTED TO COEXIST BY BOTH MODELS
2. P3 C1(HF)/ P3 G7(N)    EXPECTED TO COEXIST BY BOTH MODELS
3. P3 B3(HF)/ P3 G7(N)    EXPECTED TO COEXIST BY GFP STRAINVS ANCESOR FACS
4. P2 B1(HF)/ P3 H5(N)    H/N extremes
5. P2 B1(HF)/ P4 G6(N)    H/N extremes
6. P3 C2(HF)/ P4 G6(N)    H/N extremes
7. P3 C2(HF)/ P3 H5(N)    H/N extremes
8. P4 F2(GAL)/P3 D9(N)    Previous Glu/Gal used 
9. P4 F2(GAL)/P3 A7(GLU)
10. P4 F2(GAL)/P5 F8(GLU)
11. P4 C11(GAL)/P3 D9(GLU)
12. P4 C11(GAL)/P5 F8(GLU)
13. P4 C11(GAL)/P3 A7(GLU)
    
- 3 timepoints were collected
  - day 1
  - day 3
  - day 6
  - 
## 96 well plate
PAIRS
12  pairs were place in static and subdivided conditions in a 96 well plate

1. P3 B3/ P3 H1
3. P3 B3/ P3 G7
4. P2 B1/ P3 H5
5. B1/ P4 G6
6. P3 C2/ P4 G6
7. P3 C2/ P3 H5
8. P4 F2/P3 D9
9. P4 F2/P3 A7
10. P4 F2/P5 F8
11. P4 C11/P3 D9
12. P4 C11/P5 F8
13. P4 C11/P3 A7

### Timepoint 1 PELLET COLLECTION
Static enviroment in row A and B of day 1 were collected in each in its respective well (Plate 1-ROW A AND B)
Subdivided enviromen in row D and E were combined for each respoective strain pair and were place (Plate 1-ROW C)
### Timepoint 3 PELLET COLLECTION
Static enviroment in row A and B of day 3 were collected in each in its respective well (Plate 1-ROW D and E)
Subdivided enviromen in row D and E  of day 3 were combined for each respective strain pair and were place (Plate 1-ROW F)
### Timepoint 6 PELLET COLLECTION
Static enviroment in row A and B of day 6 were collected in each in its respective well (Plate 1-ROW G and H)
Subdivided enviroment R1 in row D and E  of day 6 were combine, strain pair were place its respective well (Plate 2-ROW A)
Subdivided enviroment R2 in row G and H  of day 6 were combine, strain pair were place its respective well (Plate 2-ROW B)

## 12 channel well
PAIRS
3 pairs: 2 which are being tested on 96 well plate and 1 which is just on the 12 channel well
1. P3 B3/ P3 H1
    a. Replicate 1: P3 B3 was place at 80% and P3H1 was place at 20% ratio
    b. Replicate 2: P3H1 was place at 80% and P3B3 was place at 20% ratio
3. P3 C1/ P3 G7
   a. Replicate 1: P3 C1 was place at 80% and P3G7 was place at 20% ratio
    b. Replicate 2: P3G7 was place at 80% and P3 C1 was place at 20% ratio
8. P4 F2/ P3 D9
   a. Replicate 1: P4 F2 was place at 80% and P3 D9 was place at 20% ratio
    b. Replicate 2: P3 D9 was place at 80% and P4 F2 was place at 20% ratio

## PELLET COLLECTION 
For the 12 channel well pellet collection the break down is as follows 
### Plate 2
1. Pair 1: used Rows C1-E6, F7,F8,F9,F10
2. pair 2: used Rows C7-E12, G7,G8,G9,G10
3. Pair 8: used Rows F1-H-6, H7,H8,H9,H10
4. 
### Timepoint 1 PELLET COLLECTION
Static enviroment and Subdivided enviroment were saved for both replicates with out combining them. 
ex: for pair one Subdivided R1 is on C5 (subH),C6(subN) and r2 is on F7(subH), and f8(subN)
### Timepoint 3 PELLET COLLECTION
Static enviroment both replicates were collected but only r1 of subdivided enviroment were collected.
### Timepoint 6 PELLET COLLECTION
Same as timepoint 1 were all replicates were collected for static and subdivided enviroment. 
   
## Data Analysis
1. Go to Barcode_Counter
2. To take a look at the data please download Barcode_counts_clean.CVS
3. If you would like to ulize the rawdata, do the following
   - Edit-demultiplex.sh with your email and your pathway. ex: scratch/mfl8805/Coexistance_Assays/Barcode_Counter
   - Please do not change the template and the primers file
   - For a full breakdown of the Plate mapping go to Abreu Drive-> Experiments->coexistance Assays->Coexitance Pairs_prelimnary assays
4. After Demultiplex is completed, you can run map_barcode.sh: this will count all the barcodes for a particular sample
5. the file CoexAssay_BClist.fa, contains the barcodes for each strain that is used including Mutant vs Ancestor comparison in N or Gal for 3 samples.
6. Note that the ML ( MLY's check is not included in this demultiplexing run. However the information to demultiplex is there 
  
   
