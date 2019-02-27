#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
Test script for evaluating plasticity2 function, which uses a calium based
2-amplitude, 2-duration thresholds for potentiation and depression
'''
from __future__ import print_function, division

import moose
import numpy as np
from matplotlib import pyplot as plt


simtime = 1.0 # sim duration in seconds
dt =  10e-6 # simulation time step
nsteps = int(simtime/dt+1) # number of sim steps

time = np.linspace(0.0, simtime, nsteps+1) # Time vector

# "Calcium" input test vector; step function to meet LTD threshold, then LTP threhold
xarr = np.ones(len(time))
xarr[0:int(len(time)/3)]=0 # First 1/3 of vector is 0
xarr[int(len(time)/3):int(2*len(time)/3)]=.45e-3 # Second 1/3 between LTD/LTP thresholds
xarr[int(2*len(time)/3):]=2e-3 # Last 1/3 above LTP threshold

# Stimulus tables allow you to store sequences of numbers which
# are delivered via the 'output' message at each time step. This
# is a placeholder and in real scenario you will be using any
# sourceFinfo that sends out a double value.
input_x = moose.StimulusTable('/xtab')
input_x.vector = xarr
input_x.startTime = 0.0
input_x.stepPosition = xarr[0]
input_x.stopTime = simtime

cal = input_x # to work with cal/CaMSG variables in plasticity function below
CaMSG = 'output'

# Test synapse
sh = moose.SimpleSynHandler('sh')
sh.synapse.num=1
################################################################################
###  Plasticity Function

# First Function object: detect calcium level/duration compared to amplitude thresholds.
# if calcium meets LTD threshold, accumulate duration above LTD as negative value;
# if it meets LTP threshold, accumulate duration above LTP as positive value;
# else return 0

NAME_DUR = 'CaThreshDurAccumulator'
durname = NAME_DUR#comp.path+'/'+NAME_DUR
dur=moose.Function(durname)
# Set expression constants
dur.c['LTP_amp_thresh'] = 0.46e-3 # TODO: Change to a parameter
dur.c['LTD_amp_thresh'] = 0.2e-3 # TODO: Change to a parameter
dur.c['dt'] = dt # TODO: Put simdt variable here
dur.x.num = 2 # Required?

# Expression: x0 is calcium input; x1 is input from self
# Accumulates value by dt (positive for LTP, negative for LTD)
dur.expr = '( (x0 >= LTP_amp_thresh) && (x1 >= 0) ) * (x1+dt) + ( (x0 >= LTD_amp_thresh && x0 < LTP_amp_thresh) && (x1 <= 0) ) * (x1-dt)'
# Connect calcium input to variable x0
moose.connect(cal,CaMSG,dur.x[0],'input')
# Connect dur value output to variable x1 of itself
moose.connect(dur,'valueOut',dur.x[1],'input')


#######################
#Second Function object: Calculate plasticity. Uses equations from Asia's code/paper
plasname='PLAS'#comp.path+'/'+NAME_PLAS
plas=moose.Function(plasname)
# Constants:
plas.c['LTP_dur_thresh'] = 0.002 # TODO: Parameterize
plas.c['LTD_dur_thresh'] = 0.032 # TODO: Parameterize
plas.c['LTP_amp_thresh'] = 0.46e-3 # TODO: Parameterize
plas.c['LTD_amp_thresh'] = 0.2e-3 # TODO: Parameterize
plas.c['LTP_gain'] = 1100 # TODO: Parameterize
plas.c['LTD_gain'] = 4500 # TODO: Parameterize
min_weight = 0.0
max_weight = 2.0
plas.c['min_weight'] = min_weight
plas.c['max_weight'] = max_weight
plas.c['max_change'] = (max_weight - min_weight)/1000.0
plas.c['dt'] = dt # TODO: Put simdt variable here


# Expression: x0 is input from duration accumulator; x1 is calcium concentration amplitude
# Current synaptic weight as input y0

# Note: due to complexity of expression strings, the final expression is built up
# from separate expression strings

# max change: compute change based on level of calcium above threshold, but limit to the max_change value
max_change_LTP_expr =        'min( ( (x1-LTP_amp_thresh) * (LTP_gain) * dt ), max_change)'
max_change_LTD_expr = '(-1) * min( ( (x1-LTD_amp_thresh) * (LTD_gain) * dt ), max_change)'

# Normalize the synaptic weight on a range from min to max weight
norm_expr_LTP = 'sqrt( 1 - ( (y0 - min_weight)/(max_weight - min_weight) ) )'
norm_expr_LTD = 'sqrt(     ( (y0 - min_weight)/(max_weight - min_weight) ) )'

# LTP condition: If x0 input from duration accumulator is above LTP threshold, change weight accordingly:
# limit the total weight to the max weight parameter
LTPexpr = '(x0 > LTP_dur_thresh) * min(y0 +  {} * {}, max_weight)'.format(max_change_LTP_expr, norm_expr_LTP)
##LTPexpr = '(x0 > LTP_dur_thresh) * 3'# For Testing

# LTD condition: If x0 input from duration accumulator is above LTD threshold, change weight accordingly:
# limit the total weight to the min weight parameter
LTDexpr = '(x0 < (-1*LTD_dur_thresh) ) * max(y0 + {} * {}, min_weight)'.format(max_change_LTD_expr, norm_expr_LTD)
#LTDexpr = '2 * (x0 < -1*LTD_dur_thresh) + (0 * x1)'#Testing

# If neither LTP or LTD thresholds are met, don't change weight; maintain current weight (y0 variable)
nochange_expr = '(y0) * ( (x0 > -LTD_dur_thresh) && (x0 < LTP_dur_thresh) )'
#nochange_expr = '(5) * ( (x0 > -LTD_dur_thresh) && (x0 < LTP_dur_thresh) )'#Testing

# Annoyingly, have to force first 2 timesteps to initial synaptic weight value of 1 so
# moose.reinit doesn't cause the output of plas expression to force synaptic weight
# to go to zero (Since synaptic weight is both an input to the expression and its output).
# Note: recent github commit to Moose may fix this; it adds Function variable "doEvalAtReinit".
# But I have't updated to it yet so haven't tried testing it.
# Expression is an if-then-else statemet with syntax ((condition) ? (Value if True) : (Value if False))
initial_value_expr = '(t<2*dt) ? (1) : '

# Put the expression all together:
plas.expr = '{} ({} + {} + {})'.format(initial_value_expr, LTPexpr, LTDexpr, nochange_expr)

# Connect Duration accumululator output to variable x0
moose.connect(dur,'valueOut',plas.x[0],'input')
# Connect calcium amplitude to variable x1
moose.connect(cal,CaMSG,plas.x[1],'input')
# Get the current synaptic weight of the synapse as variable y0
moose.connect(plas,'requestOut',sh.synapse[0],'getWeight')
# Output the updated weight computed by plasticity function to the synapse
moose.connect(plas,'valueOut',sh.synapse[0],'setWeight')

################################################################################


# data recording
for ii in range(32):
    moose.setClock(ii, dt)

# plasticity function output table
result = moose.Table('/result')
moose.connect(result, 'requestOut', plas, 'getValue')

# "calcium" input table from stimulus table:
x_rec = moose.Table('/xrec')
moose.connect(x_rec, 'requestOut', input_x, 'getOutputValue')

# table for synaptic weight value of synapse
weighttable = moose.Table('/weight')
moose.connect(weighttable, 'requestOut', sh.synapse[0], 'getWeight')

# Table for duration accumulator Function:
durtable = moose.Table('/dur')
moose.connect(durtable, 'requestOut', dur, 'getValue')

moose.reinit()

# Alternative to setting intial value expression above; set synapse weight
# to intial value after moose.reinit(), i.e.:
# sh.synapse[0].weight = 1

moose.start(simtime)

plt.ion()
plt.plot(time,x_rec.vector*1E3, label='calcium (microMolar)')
plt.plot(time,result.vector, label='Plasticity Function Output')
plt.plot(time,weighttable.vector, linestyle = '--', label='Synaptic Weight')
plt.plot(time,durtable.vector, label='Duration Accumulator')

plt.legend()

plt.tight_layout()
plt.show()
