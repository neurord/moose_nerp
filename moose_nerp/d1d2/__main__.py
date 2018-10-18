# -*- coding:utf-8 -*-

######## SPneuronSim.py ############
## Code to create two SP neuron classes
##      using dictionaries for channels and synapses
##      calcium based learning rule/plasticity function, optional
##      spines, optionally with ion channels and synpases
##      Synapses to test the plasticity function, optional
##      used to tune parameters and channel kinetics (but using larger morphology)

from moose_nerp import d1d2 as model

# options to be passed as **kwargs for main simulation function
options = {}

# Optionally set logging level; default is INFO
options['logging_level'] = model.logging.DEBUG

# Options related to overriding the default values in
# standard_options.standard_options()
options['default_injection_current'] = [-0.2e-9,0.26e-9]
options['default_stim'] = 'inject'
options['default_stim_loc'] = model.NAME_SOMA

# Options for overriding param_sim parameters after calling parse_args()
options['save'] = 0
options['plot_channels'] = 0

# Other possible options:
# options['plot_comps'] # Defaults to model.NAME_SOMA;
# options['fname'] # Set by default

# Main
model.create_model_sim.main(model, **options)
