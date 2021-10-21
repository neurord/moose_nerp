
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

