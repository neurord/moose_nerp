
*relative
*cartesian
*asymmetric

*set_global RA 4.0 
//change Cm to account for no spines - make 3x higher?
*set_global CM 0.03 
*set_global RM 2.8
*set_global EREST_ACT -80e-3
*set_global ELEAK -50e-3

*start_cell
soma none 14.000 0 0 14.000
   primdend1 soma 9 4.5 0 1.7
   primdend2 soma 9 -4.5 0 1.7
   primdend3 soma 4.5 9 0 1.7
   primdend4 soma 4.5 -9 0 1.7

   secdend11 primdend1 12 0 0 1.4
   secdend12 primdend1 11 5 0 1.4
   secdend21 primdend2 12 0 0 1.4
   secdend22 primdend2 11 -5 0 1.4
   secdend31 primdend3 0 12 0 1.4
   secdend32 primdend3 5 11 0 1.4
   secdend41 primdend4 0 -12 0 1.4 
   secdend42 primdend4 5 -11 0 1.4

tertdend1_1 secdend11 18  0  0  0.8
tertdend1_2 . 17 7 0 0.79 
tertdend2_1 secdend11 18  0  0  0.8
tertdend2_2 . 17 7 0 0.79 

tertdend3_1 secdend12 18  0  0  0.8
tertdend3_2 . 17 7 0 0.79 
tertdend4_1 secdend12 18  0  0  0.8
tertdend4_2 . 17 7 0 0.79 

tertdend5_1 secdend21 18  0  0  0.8
tertdend5_2 . 17 7 0 0.79 
tertdend6_1 secdend21 18  0  0  0.8
tertdend6_2 . 17 7 0 0.79 

tertdend7_1 secdend22 18  0  0  0.8
tertdend7_2 . 17 7 0 0.79 
tertdend8_1 secdend22 18  0  0  0.8
tertdend8_2 . 17 7 0 0.79 

tertdend9_1 secdend31 18  0  0  0.8
tertdend9_2 . 17 7 0 0.79 
tertdend10_1 secdend31 18  0  0  0.8
tertdend10_2 . 17 7 0 0.79 

tertdend11_1 secdend32 18  0  0  0.8
tertdend11_2 . 17 7 0 0.79 
tertdend12_1 secdend32 18  0  0  0.8
tertdend12_2 . 17 7 0 0.79 

tertdend13_1 secdend41 18  0  0  0.8
tertdend13_2 . 17 7 0 0.79 
tertdend14_1 secdend41 18  0  0  0.8
tertdend14_2 . 17 7 0 0.79 

tertdend15_1 secdend42 18  0  0  0.8
tertdend15_2 . 17 7 0 0.79 
tertdend16_1 secdend42 18  0  0  0.8
tertdend16_2 . 17 7 0 0.79 
