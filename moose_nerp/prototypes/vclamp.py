import moose
from moose_nerp import d1patchsample2 as model
from moose_nerp.prototypes import create_model_sim
from moose_nerp.prototypes import spatiotemporalInputMapping as im

model.spineYN = True
model.calYN = True
model.synYN = True
model.SpineParams.explicitSpineDensity=1e6
model.param_syn._SynNMDA.Gbar = 10e-09
model.param_syn._SynAMPA.Gbar = .5e-09

for chan in ['NaF','KaF','Krp','KaS','Kir','SKCa','BKCa','CaCC']:
    for k,v in model.Condset.D1[chan].items():
        model.Condset.D1[chan][k]=0.0
for chan in ['CaL13',
            'CaL12',
            'CaR',
            'CaT',
            'CaN',
            ]:
    for k,v in model.Condset.D1[chan].items():
        model.Condset.D1[chan][k]=0*v
model.plas = {}

#model.Condset.D1.NaF[model.param_cond.dist]=0
model.param_syn.SYNAPSE_TYPES.nmda.MgBlock.C=1
create_model_sim.setupOptions(model)
param_sim = model.param_sim
model.syn, model.neurons = create_model_sim.cell_proto.neuronclasses(model)
simpaths=['/'+neurotype for neurotype in create_model_sim.util.neurontypes(model.param_cond)]
# Fix calculation of B parameter in CaConc if using hsolve

for c in moose.wildcardFind('/D1/##[ISA=CompartmentBase]'):
    #print(c.Rm)
    c.Em = -60e-3
    c.initVm = -60e-3
    c.Rm = 2.5*c.Rm     
    #print(c.Rm)

create_model_sim.clocks.assign_clocks(simpaths, param_sim.simdt, param_sim.plotdt,
                    param_sim.hsolve, model.param_cond.NAME_SOMA)

if model.param_sim.hsolve and model.calYN:
    create_model_sim.calcium.fix_calcium(create_model_sim.util.neurontypes(model.param_cond), model)


create_model_sim.setupOutput(model)
soma = moose.element(model.neurons['D1'][0].path + '/' + model.NAME_SOMA)

inputs = im.exampleClusteredDistal(model,nInputs = 1)
im.createTimeTables(inputs,model,n_per_syn=1)


#def vclamp_demo(simtime=50.0, dt=1e-2):
"""
Demonstration of voltage clamping in a neuron.
"""
simtime = 0.4#dt = 1e-2

## It is good practice to modularize test elements inside a container
container = moose.Neutral('/vClampDemo')
## Create a compartment with properties of a squid giant axon
comp = soma
# Create and setup the voltage clamp object
clamp = moose.VClamp('/vClampDemo/vclamp')
dt = model.param_sim.simdt
## The defaults should work fine
# clamp.mode = 2
clamp.tau = 10*dt
clamp.ti = dt
# clamp.td = 0
clamp.gain = comp.Cm / dt
## Setup command voltage time course
command = moose.PulseGen('/vClampDemo/command')
command.baseLevel = -80e-3
command.delay[0] = .25
command.width[0] = .2
command.level[0] = 40e-3#40e-3#50.0e-3
command.delay[1] = 1e9#.05
moose.connect(command, 'output', clamp, 'commandIn')
## Connect the Voltage Clamp to the compartemnt
moose.connect(clamp, 'currentOut', comp, 'injectMsg')
moose.connect(comp, 'VmOut', clamp, 'sensedIn')
## setup stimulus recroding - this is the command pulse
stimtab = moose.Table('/vClampDemo/vclamp_command')
moose.connect(stimtab, 'requestOut', command, 'getOutputValue')
## Set up Vm recording
vmtab = moose.Table('/vClampDemo/vclamp_Vm')
moose.connect(vmtab, 'requestOut', comp, 'getVm')
## setup command potential recording - this is the filtered input
## to PID controller
commandtab = moose.Table('/vClampDemo/vclamp_filteredcommand')
moose.connect(commandtab, 'requestOut', clamp, 'getCommand')
## setup current recording
Imtab = moose.Table('/vClampDemo/vclamp_inject')
moose.connect(Imtab, 'requestOut', clamp, 'getCurrent')
# Scheduling
#moose.setClock(0, dt)
#moose.setClock(1, dt)
#moose.setClock(2, dt)
#moose.setClock(3, dt)
#moose.useClock(0, '%s/##[TYPE=Compartment]' % (container.path), 'init')
#moose.useClock(0, '%s/##[TYPE=PulseGen]' % (container.path), 'process')
#moose.useClock(1, '%s/##[TYPE=Compartment]' % (container.path), 'process')
#moose.useClock(2, '%s/##[TYPE=HHChannel]' % (container.path), 'process')
#moose.useClock(2, '%s/##[TYPE=VClamp]' % (container.path), 'process')
#moose.useClock(3, '%s/##[TYPE=Table]' % (container.path), 'process')
moose.reinit()
print(('RC filter in VClamp:: tau:', clamp.tau))
print(('PID controller in VClamp:: ti:', clamp.ti, 'td:', clamp.td, 'gain:', clamp.gain))
moose.start(simtime)
print(('Finished simulation for %g seconds' % (simtime)))

from matplotlib import pyplot as plt
import numpy as np
tseries = np.linspace(0, simtime, len(vmtab.vector))
plt.subplot(211)
plt.title('Membrane potential and clamp voltage')
plt.plot(tseries, vmtab.vector, 'g-', label='Vm (mV)')
plt.plot(tseries, commandtab.vector, 'b-', label='Filtered command (mV)')
plt.plot(tseries, stimtab.vector, 'r-', label='Command (mV)')
plt.xlabel('Time (ms)')
plt.ylabel('Voltage (mV)')
plt.legend()
# print len(commandtab.vector)
plt.subplot(212)
plt.title('Current through clamp circuit')
# plot(tseries, stimtab.vector, label='stimulus (uA)')
plt.plot(tseries, Imtab.vector, label='injected current (uA)')
plt.xlabel('Time (ms)')
plt.ylabel('Current (uA)')
plt.legend()
plt.show()