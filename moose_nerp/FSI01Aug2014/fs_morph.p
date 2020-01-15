//cell parameter file 
// co-ordinate mode
*relative
*cartesian
*asymmetric
*lambda_warn

// specifying constants, SI units
// Plenz D, Aertsen A. Neuroscience. 1996 Feb;70(4):861-91
// J Neurosci 1994,14:4613-4638 says Cm=0.007-0.008, Rm 120-200kOhm*cm^2 ???
*set_global RM 0.95 //ohm*m^2 //Avrama decreased from 3 to 2 fix timeconstants
*set_global CM 0.01056 //farads/m^2
*set_global RA 1.74  //ohm*m
*set_global EREST_ACT -0.060 //?? relative to zero??
*set_global ELEAK -0.03887  // resting, Volts, was -65mV before

*start_cell 
   soma   none  40  0  0 20 


