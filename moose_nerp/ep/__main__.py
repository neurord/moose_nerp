# -*- coding:utf-8 -*-

########  ############
## Code to create entopeduncular neuron
##      using dictionaries for channels and synapses
##      calcium based learning rule/plasticity function, optional
##      spines, optionally with ion channels and synpases
##      Synapses to test the plasticity function, optional
##      used to tune parameters and channel kinetics (but using larger morphology)

from __future__ import print_function, division
from moose_nerp import ep as model
'''Evaluates moose_nerp/ca1/__init__.py to load all the parameters, e.g.
param_sim.py, param_ca_plas.py, param_chan.py, param_cond.py, param_sim.py, etc.
into the model namespace. These parameters are then accessible by, e.g.,
`model.param_sim.fname`.
'''

from moose_nerp.prototypes import create_model_sim
'''Imports functions for setting up and simulating model. These take the `model`
namespace as argument, and append variables to this namespace. Thus, after
running a simulation, the output tables would be accessible as model.vmtab,
model.catab, etc.'''

# Parameter overrides can be specified:

# This function sets up the options specified in param_sim or passed from
# command line:
create_model_sim.setupOptions(model)

# This function creates the neuron(s) in Moose:
create_model_sim.setupNeurons(model)

# This function sets up the Output options, e.g. saving, graph tables, etc.
create_model_sim.setupOutput(model)

# This function sets up the stimulation in Moose, e.g. pulsegen for current
# injection or synaptic stimulation:
create_model_sim.setupStim(model)

# There is also a convenience function, `create_model_sim.setupAll(model)` that
# would sequentially call the above four functions: setupOptions, setupNeurons,
# setupOutput, and setupStim

# This function runs all the specified simulations, plotting and saving them
# as specified:
#create_model_sim.runAll(model,printParams=False)

# Alternative function to create_model_sim.runAll, that runs a simulation a few
# steps at a time and then updates a plot, to show the live simulation results.
# This is an example of modifying, expanding, or customizing code:
#   `create_model_sim.stepRunPlot(model)`

# Note that customizations should be added to 'create_model_sim' to make them
# available to any model, by adding new functions or expanding existing functions
# with new options that do not alter the current state of the functions unless
# the new options are explicitly called.

#specify presyn as tt explicitly and test.
import moose
import numpy as np
from moose_nerp.prototypes import plasticity
from moose_nerp import ep_net as net

simtime=model.param_sim.simtime
#simtime=5
tt1=moose.TimeTable('tt1hz')
tt5=moose.TimeTable('tt5hz')
tt10=moose.TimeTable('tt10hz')
tt20=moose.TimeTable('tt20hz')
tt40=moose.TimeTable('tt40hz')
tt1.vector=[0.5+n/1.0 for n in range(int(simtime*1))]
tt5.vector=[0.5+n/5.0 for n in range(int(simtime*5))]
tt10.vector=[0.5+n/10.0 for n in range(10)]
tt20.vector=[0.5+n/20.0 for n in range(20)]
tt40.vector=[0.5+n/40.0 for n in range(40)]

tt=tt10
synchan=moose.element('/ep[0]/p0b1[0]/gaba[0]/') #gp synchan
#synchan=moose.element('/ep[0]/p0b1b1b1[0]/gaba[0]/')#str synchan
sh=moose.element(synchan.path+'/SH')
sh.numSynapses=1
moose.connect(tt,'eventOut', sh.synapse[0], 'addSpike')

stp_params=net.param_net.GPe_plas
#stp_params=net.param_net.Str_plas
simdt =  model.param_sim.simdt
plasticity.ShortTermPlas(sh.synapse[0],0,stp_params,simdt,tt,'eventOut')
#for ii in range(32):
#    moose.setClock(ii, simdt)

#evaluate result:
deptab = moose.Table('/deptab')
dep0=moose.element(synchan.path+'/dep0')
moose.connect(deptab, 'requestOut', dep0, 'getValue')
plas_tab = moose.Table('/plastab')
plas=moose.element(synchan.path+'/stp0')
moose.connect(plas_tab, 'requestOut', plas, 'getValue')
syn_tab=moose.Table('/syntab')
moose.connect(syn_tab,'requestOut',synchan,'getGk')

create_model_sim.runAll(model,printParams=False)

#moose.reinit()
#moose.start(simtime)

from matplotlib import pyplot as plt
plt.ion()
plt.figure()
numpts=len(plas_tab.vector)
time=np.arange(0,simdt*numpts,simdt)
plt.plot(time[0:numpts],deptab.vector,label='dep')
plt.plot(time[0:numpts],plas_tab.vector+0.1,label='plas+0.1')
plt.plot(time[0:numpts],syn_tab.vector*1e9,label='Gk*1e9')
plt.legend()


