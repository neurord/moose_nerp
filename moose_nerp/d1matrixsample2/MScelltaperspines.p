//UNITS: micros for x,y,d dia, SI otherwise
*relative     
*cartesian     
*asymmetric     
*lambda_warn     
     
*set_global RA 1.921  //ohm-meters
//change Cm to account for no spines - make 3x higher?
*set_global CM 0.03 //Farads/meters squared
*set_global RM 4.8448 //ohm-meters squared
*set_global EREST_ACT -86e-3 //Volts
*set_global ELEAK -0.07920 //Volts
     
*start_cell     
*cylindrical     
soma none 11.3137 0 0 22.6274
     
primdend1 soma 12 0 0 2.25
primdend2 soma 12 0 0 2.25
primdend3 soma 12 0 0 2.25
primdend4 soma 12 0 0 2.25
     
secdend11 primdend1 14 0 0 1.417
secdend12 primdend1 14 0 0 1.417
secdend21 primdend2 14 0 0 1.417
secdend22 primdend2 14 0 0 1.417
secdend31 primdend3 14 0 0 1.417
secdend32 primdend3 14 0 0 1.417
secdend41 primdend4 14 0 0 1.417
secdend42 primdend4 14 0 0 1.417
     
tertdend1_1 secdend11 18 0 0 0.893
tertdend1_2 . 18 0 0 0.834
tertdend1_3 . 18 0 0 0.774
tertdend1_4 . 18 0 0 0.715
tertdend1_5 . 18 0 0 0.656
tertdend1_6 . 18 0 0 0.597
tertdend1_7 . 18 0 0 0.537
tertdend1_8 . 18 0 0 0.478
tertdend1_9 . 18 0 0 0.419
tertdend1_10 . 18 0 0 0.359
tertdend1_11 . 18 0 0 0.3
     
tertdend2_1 secdend11 18 0 0 0.893
tertdend2_2 . 18 0 0 0.834
tertdend2_3 . 18 0 0 0.774
tertdend2_4 . 18 0 0 0.715
tertdend2_5 . 18 0 0 0.656
tertdend2_6 . 18 0 0 0.597
tertdend2_7 . 18 0 0 0.537
tertdend2_8 . 18 0 0 0.478
tertdend2_9 . 18 0 0 0.419
tertdend2_10 . 18 0 0 0.359
tertdend2_11 . 18 0 0 0.3
     
tertdend3_1 secdend12 18 0 0 0.893
tertdend3_2 . 18 0 0 0.834
tertdend3_3 . 18 0 0 0.774
tertdend3_4 . 18 0 0 0.715
tertdend3_5 . 18 0 0 0.656
tertdend3_6 . 18 0 0 0.597
tertdend3_7 . 18 0 0 0.537
tertdend3_8 . 18 0 0 0.478
tertdend3_9 . 18 0 0 0.419
tertdend3_10 . 18 0 0 0.359
tertdend3_11 . 18 0 0 0.3
     
tertdend4_1 secdend12 18 0 0 0.893
tertdend4_2 . 18 0 0 0.834
tertdend4_3 . 18 0 0 0.774
tertdend4_4 . 18 0 0 0.715
tertdend4_5 . 18 0 0 0.656
tertdend4_6 . 18 0 0 0.597
tertdend4_7 . 18 0 0 0.537
tertdend4_8 . 18 0 0 0.478
tertdend4_9 . 18 0 0 0.419
tertdend4_10 . 18 0 0 0.359
tertdend4_11 . 18 0 0 0.3
     
tertdend5_1 secdend21 18 0 0 0.893
tertdend5_2 . 18 0 0 0.834
tertdend5_3 . 18 0 0 0.774
tertdend5_4 . 18 0 0 0.715
tertdend5_5 . 18 0 0 0.656
tertdend5_6 . 18 0 0 0.597
tertdend5_7 . 18 0 0 0.537
tertdend5_8 . 18 0 0 0.478
tertdend5_9 . 18 0 0 0.419
tertdend5_10 . 18 0 0 0.359
tertdend5_11 . 18 0 0 0.3
     
tertdend6_1 secdend21 18 0 0 0.893
tertdend6_2 . 18 0 0 0.834
tertdend6_3 . 18 0 0 0.774
tertdend6_4 . 18 0 0 0.715
tertdend6_5 . 18 0 0 0.656
tertdend6_6 . 18 0 0 0.597
tertdend6_7 . 18 0 0 0.537
tertdend6_8 . 18 0 0 0.478
tertdend6_9 . 18 0 0 0.419
tertdend6_10 . 18 0 0 0.359
tertdend6_11 . 18 0 0 0.3
     
tertdend7_1 secdend22 18 0 0 0.893
tertdend7_2 . 18 0 0 0.834
tertdend7_3 . 18 0 0 0.774
tertdend7_4 . 18 0 0 0.715
tertdend7_5 . 18 0 0 0.656
tertdend7_6 . 18 0 0 0.597
tertdend7_7 . 18 0 0 0.537
tertdend7_8 . 18 0 0 0.478
tertdend7_9 . 18 0 0 0.419
tertdend7_10 . 18 0 0 0.359
tertdend7_11 . 18 0 0 0.3
     
tertdend8_1 secdend22 18 0 0 0.893
tertdend8_2 . 18 0 0 0.834
tertdend8_3 . 18 0 0 0.774
tertdend8_4 . 18 0 0 0.715
tertdend8_5 . 18 0 0 0.656
tertdend8_6 . 18 0 0 0.597
tertdend8_7 . 18 0 0 0.537
tertdend8_8 . 18 0 0 0.478
tertdend8_9 . 18 0 0 0.419
tertdend8_10 . 18 0 0 0.359
tertdend8_11 . 18 0 0 0.3
     
tertdend9_1 secdend31 18 0 0 0.893
tertdend9_2 . 18 0 0 0.834
tertdend9_3 . 18 0 0 0.774
tertdend9_4 . 18 0 0 0.715
tertdend9_5 . 18 0 0 0.656
tertdend9_6 . 18 0 0 0.597
tertdend9_7 . 18 0 0 0.537
tertdend9_8 . 18 0 0 0.478
tertdend9_9 . 18 0 0 0.419
tertdend9_10 . 18 0 0 0.359
tertdend9_11 . 18 0 0 0.3
     
tertdend10_1 secdend31 18 0 0 0.893
tertdend10_2 . 18 0 0 0.834
tertdend10_3 . 18 0 0 0.774
tertdend10_4 . 18 0 0 0.715
tertdend10_5 . 18 0 0 0.656
tertdend10_6 . 18 0 0 0.597
tertdend10_7 . 18 0 0 0.537
tertdend10_8 . 18 0 0 0.478
tertdend10_9 . 18 0 0 0.419
tertdend10_10 . 18 0 0 0.359
tertdend10_11 . 18 0 0 0.3
     
tertdend11_1 secdend32 18 0 0 0.893
tertdend11_2 . 18 0 0 0.834
tertdend11_3 . 18 0 0 0.774
tertdend11_4 . 18 0 0 0.715
tertdend11_5 . 18 0 0 0.656
tertdend11_6 . 18 0 0 0.597
tertdend11_7 . 18 0 0 0.537
tertdend11_8 . 18 0 0 0.478
tertdend11_9 . 18 0 0 0.419
tertdend11_10 . 18 0 0 0.359
tertdend11_11 . 18 0 0 0.3
     
tertdend12_1 secdend32 18 0 0 0.893
tertdend12_2 . 18 0 0 0.834
tertdend12_3 . 18 0 0 0.774
tertdend12_4 . 18 0 0 0.715
tertdend12_5 . 18 0 0 0.656
tertdend12_6 . 18 0 0 0.597
tertdend12_7 . 18 0 0 0.537
tertdend12_8 . 18 0 0 0.478
tertdend12_9 . 18 0 0 0.419
tertdend12_10 . 18 0 0 0.359
tertdend12_11 . 18 0 0 0.3
     
tertdend13_1 secdend41 18 0 0 0.893
tertdend13_2 . 18 0 0 0.834
tertdend13_3 . 18 0 0 0.774
tertdend13_4 . 18 0 0 0.715
tertdend13_5 . 18 0 0 0.656
tertdend13_6 . 18 0 0 0.597
tertdend13_7 . 18 0 0 0.537
tertdend13_8 . 18 0 0 0.478
tertdend13_9 . 18 0 0 0.419
tertdend13_10 . 18 0 0 0.359
tertdend13_11 . 18 0 0 0.3
     
tertdend14_1 secdend41 18 0 0 0.893
tertdend14_2 . 18 0 0 0.834
tertdend14_3 . 18 0 0 0.774
tertdend14_4 . 18 0 0 0.715
tertdend14_5 . 18 0 0 0.656
tertdend14_6 . 18 0 0 0.597
tertdend14_7 . 18 0 0 0.537
tertdend14_8 . 18 0 0 0.478
tertdend14_9 . 18 0 0 0.419
tertdend14_10 . 18 0 0 0.359
tertdend14_11 . 18 0 0 0.3
     
tertdend15_1 secdend42 18 0 0 0.893
tertdend15_2 . 18 0 0 0.834
tertdend15_3 . 18 0 0 0.774
tertdend15_4 . 18 0 0 0.715
tertdend15_5 . 18 0 0 0.656
tertdend15_6 . 18 0 0 0.597
tertdend15_7 . 18 0 0 0.537
tertdend15_8 . 18 0 0 0.478
tertdend15_9 . 18 0 0 0.419
tertdend15_10 . 18 0 0 0.359
tertdend15_11 . 18 0 0 0.3
     
tertdend16_1 secdend42 18 0 0 0.893
tertdend16_2 . 18 0 0 0.834
tertdend16_3 . 18 0 0 0.774
tertdend16_4 . 18 0 0 0.715
tertdend16_5 . 18 0 0 0.656
tertdend16_6 . 18 0 0 0.597
tertdend16_7 . 18 0 0 0.537
tertdend16_8 . 18 0 0 0.478
tertdend16_9 . 18 0 0 0.419
tertdend16_10 . 18 0 0 0.359
tertdend16_11 . 18 0 0 0.3
