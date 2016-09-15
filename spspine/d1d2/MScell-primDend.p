
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
soma none 16.000 0 0 16.000
primdend1 soma 9 4.5 0 2.5
primdend2 soma 9 -4.5 0 2.5
primdend3 soma 4.5 9 0 2.5
primdend4 soma 4.5 -9 0 2.5
