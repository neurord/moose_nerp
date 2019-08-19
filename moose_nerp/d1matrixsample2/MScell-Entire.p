
*relative
*cartesian
*asymmetric

*set_global RA 3.2599
//change Cm to account for no spines - make 3x higher?
*set_global CM 0.030612
*set_global RM 0.2135
*set_global EREST_ACT -80e-3
*set_global ELEAK -80e-3

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
tertdend1_3 . 17 7 0 0.78 
tertdend1_4 . 17 7 0 0.77
tertdend1_5 . 17 7 0 0.76 
tertdend1_6 . 17 7 0 0.75 
tertdend1_7 . 17 7 0 0.74
tertdend1_8 . 17 7 0 0.73
tertdend1_9 . 17 7 0 0.72 
tertdend1_10 . 17 7 0 0.71 
tertdend1_11 . 17 7 0 0.70
tertdend2_1 secdend11 0 18  0  0.8
tertdend2_2 . 7 17 0 0.79 
tertdend2_3 . 7 17 0 0.78 
tertdend2_4 . 7 17 0 0.77 
tertdend2_5 . 7 17 0 0.76 
tertdend2_6 . 7 17 0 0.75 
tertdend2_7 . 7 17 0 0.74
tertdend2_8 . 7 17 0 0.73
tertdend2_9 . 7 17 0 0.72 
tertdend2_10 . 7 17 0 0.71 
tertdend2_11 . 7 17 0 0.70

tertdend3_1 secdend12 18  0  0  0.8
tertdend3_2 . 17 7 0 0.79 
tertdend3_3 . 17 7 0 0.78 
tertdend3_4 . 17 7 0 0.77 
tertdend3_5 . 17 7 0 0.76 
tertdend3_6 . 17 7 0 0.75 
tertdend3_7 . 17 7 0 0.74
tertdend3_8 . 17 7 0 0.73
tertdend3_9 . 17 7 0 0.72 
tertdend3_10 . 17 7 0 0.71 
tertdend3_11 . 17 7 0 0.70
tertdend4_1 secdend12 0 18   0  0.8
tertdend4_2 . 17 7 0 0.79 
tertdend4_3 . 17 7 0 0.78 
tertdend4_4 . 17 7 0 0.77 
tertdend4_5 . 7 17 0 0.76 
tertdend4_6 . 7 17 0 0.75 
tertdend4_7 . 7 17 0 0.74
tertdend4_8 . 7 17 0 0.73
tertdend4_9 . 7 17 0 0.72 
tertdend4_10 . 7 17 0 0.71 
tertdend4_11 . 7 17 0 0.70

tertdend5_1 secdend21 18  0  0  0.8
tertdend5_2 . 17 7 0 0.79 
tertdend5_3 . 17 7 0 0.78
tertdend5_4 . 17 7 0 0.77
tertdend5_5 . 17 7 0 0.76 
tertdend5_6 . 17 7 0 0.75 
tertdend5_7 . 17 7 0 0.74
tertdend5_8 . 17 7 0 0.73
tertdend5_9 . 17 7 0 0.72 
tertdend5_10 . 17 7 0 0.71 
tertdend5_11 . 17 7 0 0.70
tertdend6_1 secdend21 0 18   0  0.8
tertdend6_2 . 17 7 0 0.79 
tertdend6_3 . 17 7 0 0.78 
tertdend6_4 . 17 7 0 0.77 
tertdend6_5 . 7 17 0 0.76 
tertdend6_6 . 7 17 0 0.75 
tertdend6_7 . 7 17 0 0.74
tertdend6_8 . 7 17 0 0.73
tertdend6_9 . 7 17 0 0.72 
tertdend6_10 . 7 17 0 0.71 
tertdend6_11 . 7 17 0 0.70

tertdend7_1 secdend22 18  0  0  0.8
tertdend7_2 . 17 7 0 0.79 
tertdend7_3 . 17 7 0 0.78 
tertdend7_4 . 17 7 0 0.77 
tertdend7_5 . 17 7 0 0.76 
tertdend7_6 . 17 7 0 0.75 
tertdend7_7 . 17 7 0 0.74
tertdend7_8 . 17 7 0 0.73
tertdend7_9 . 17 7 0 0.72 
tertdend7_10 . 17 7 0 0.71 
tertdend7_11 . 17 7 0 0.70
tertdend8_1 secdend22 0 18   0  0.8
tertdend8_2 . 17 7 0 0.79 
tertdend8_3 . 17 7 0 0.78 
tertdend8_4 . 17 7 0 0.77 
tertdend8_5 . 7 17 0 0.76 
tertdend8_6 . 7 17 0 0.75 
tertdend8_7 . 7 17 0 0.74
tertdend8_8 . 7 17 0 0.73
tertdend8_9 . 7 17 0 0.72 
tertdend8_10 . 7 17 0 0.71 
tertdend8_11 . 7 17 0 0.70

tertdend9_1 secdend31 18  0  0  0.8
tertdend9_2 . 17 7 0 0.79 
tertdend9_3 . 17 7 0 0.78
tertdend9_4 . 17 7 0 0.77
tertdend9_5 . 17 7 0 0.76 
tertdend9_6 . 17 7 0 0.75 
tertdend9_7 . 17 7 0 0.74
tertdend9_8 . 17 7 0 0.73
tertdend9_9 . 17 7 0 0.72 
tertdend9_10 . 17 7 0 0.71 
tertdend9_11 . 17 7 0 0.70
tertdend10_1 secdend31 0 18  0  0.8
tertdend10_2 . 17 7 0 0.79 
tertdend10_3 . 17 7 0 0.78
tertdend10_4 . 17 7 0 0.77
tertdend10_5 . 7 17 0 0.76 
tertdend10_6 . 7 17 0 0.75 
tertdend10_7 . 7 17 0 0.74
tertdend10_8 . 7 17 0 0.73
tertdend10_9 . 7 17 0 0.72 
tertdend10_10 . 7 17 0 0.71 
tertdend10_11 . 7 17 0 0.70

tertdend11_1 secdend32 18  0  0  0.8
tertdend11_2 . 17 7 0 0.79 
tertdend11_3 . 17 7 0 0.78
tertdend11_4 . 17 7 0 0.77
tertdend11_5 . 17 7 0 0.76 
tertdend11_6 . 17 7 0 0.75 
tertdend11_7 . 17 7 0 0.74
tertdend11_8 . 17 7 0 0.73
tertdend11_9 . 17 7 0 0.72 
tertdend11_10 . 17 7 0 0.71 
tertdend11_11 . 17 7 0 0.70
tertdend12_1 secdend32 0 18  0  0.8
tertdend12_2 . 17 7 0 0.79 
tertdend12_3 . 17 7 0 0.78
tertdend12_4 . 17 7 0 0.77
tertdend12_5 . 7 17 0 0.76 
tertdend12_6 . 7 17 0 0.75 
tertdend12_7 . 7 17 0 0.74
tertdend12_8 . 7 17 0 0.73
tertdend12_9 . 7 17 0 0.72 
tertdend12_10 . 7 17 0 0.71 
tertdend12_11 . 7 17 0 0.70

tertdend13_1 secdend41 18  0  0  0.8
tertdend13_2 . 17 7 0 0.79 
tertdend13_3 . 17 7 0 0.78
tertdend13_4 . 17 7 0 0.77
tertdend13_5 . 17 7 0 0.76 
tertdend13_6 . 17 7 0 0.75 
tertdend13_7 . 17 7 0 0.74
tertdend13_8 . 17 7 0 0.73
tertdend13_9 . 17 7 0 0.72 
tertdend13_10 . 17 7 0 0.71 
tertdend13_11 . 17 7 0 0.70
tertdend14_1 secdend41 0 18  0  0.8
tertdend14_2 . 17 7 0 0.79 
tertdend14_3 . 17 7 0 0.78 
tertdend14_4 . 17 7 0 0.77 
tertdend14_5 . 7 17 0 0.76 
tertdend14_6 . 7 17 0 0.75 
tertdend14_7 . 7 17 0 0.74
tertdend14_8 . 7 17 0 0.73
tertdend14_9 . 7 17 0 0.72 
tertdend14_10 . 7 17 0 0.71 
tertdend14_11 . 7 17 0 0.70
 
tertdend15_1 secdend42 18  0  0  0.8
tertdend15_2 . 17 7 0 0.79 
tertdend15_3 . 17 7 0 0.78
tertdend15_4 . 17 7 0 0.77
tertdend15_5 . 17 7 0 0.76 
tertdend15_6 . 17 7 0 0.75 
tertdend15_7 . 17 7 0 0.74
tertdend15_8 . 17 7 0 0.73
tertdend15_9 . 17 7 0 0.72 
tertdend15_10 . 17 7 0 0.71 
tertdend15_11 . 17 7 0 0.70
tertdend16_1 secdend42 0 18  0  0.8
tertdend16_2 . 17 7 0 0.79 
tertdend16_3 . 17 7 0 0.78
tertdend16_4 . 17 7 0 0.77
tertdend16_5 . 7 17 0 0.76 
tertdend16_6 . 7 17 0 0.75 
tertdend16_7 . 7 17 0 0.74
tertdend16_8 . 7 17 0 0.73
tertdend16_9 . 7 17 0 0.72 
tertdend16_10 . 7 17 0 0.71 
tertdend16_11 . 7 17 0 0.70
