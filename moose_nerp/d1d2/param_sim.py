from argparse import Namespace
from .param_cond import NAME_SOMA
import logging

param_sim = Namespace()

# Options for setting up stim paradigm
param_sim.stim_loc = NAME_SOMA
param_sim.stim_paradigm = 'inject'
param_sim.injection_current = [-0.2e-9, 0.26e-9]
param_sim.injection_delay = 0.1
param_sim.injection_width = 0.4
param_sim.simtime = 0.35

param_sim.neuron_type = None # 'D1' or 'D2', or None for both

param_sim.logging_level = logging.WARNING
param_sim.save = True

param_sim.simdt = 1e-05
param_sim.hsolve = True

param_sim.plotcomps = [NAME_SOMA]

param_sim.fname = None

param_sim.plot_vm = True
param_sim.plotdt = 0.0002

param_sim.plot_activation = None
param_sim.plot_calcium = True
param_sim.plot_channels = 0
param_sim.plot_current = None
param_sim.plot_current_label = 'Cond, S'
param_sim.plot_current_message = 'getGk'
param_sim.plot_netvm = None
param_sim.plot_network = None
param_sim.plot_synapse = None
param_sim.plot_synapse_label = 'Cond, nS'
param_sim.plot_synapse_message = 'getGk'
