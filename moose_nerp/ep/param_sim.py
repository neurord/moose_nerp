from argparse import Namespace
from .param_cond import NAME_SOMA
import logging

param_sim = Namespace()

# Options for setting up stim paradigm
#param_sim.stim_loc = NAME_SOMA
param_sim.stim_paradigm = 'inject'
param_sim.injection_current = [0e-12,25e-12, 50e-12,75e-12,100e-12,150e-12,200e-12,-100e-12,-200e-12 ] #[-200e-12,-100e-12, 50e-12,150e-12]
param_sim.injection_delay = 0.1
param_sim.injection_width = 0.3
param_sim.simtime = 1.0

param_sim.neuron_type = None

param_sim.logging_level = logging.INFO

param_sim.save = False #True # save to hdf5
param_sim.save_txt = False # True # Save text files

#smaller than previous to improve stability
param_sim.simdt = 1e-06
param_sim.hsolve = True

param_sim.plotcomps = [NAME_SOMA]

param_sim.fname = None # `None` uses default specified by stim paradigm

param_sim.plot_vm = True
param_sim.plotdt = 0.0001

param_sim.plot_activation = False #None
param_sim.plot_calcium = True #False
param_sim.plot_channels = False #['NaS','NaF'] # True for all channels, or name of channel or list of names of channels for individual
param_sim.plotgate = 'NaF' #TODO: Use this
param_sim.plot_current = False #True #None
param_sim.plot_current_label = 'Cond, S'
param_sim.plot_current_message = 'getGk'
param_sim.plot_netvm = False #None
param_sim.plot_network = False #None
param_sim.plot_synapse = False #None
param_sim.plot_synapse_label = 'Cond, nS'
param_sim.plot_synapse_message = 'getGk'
