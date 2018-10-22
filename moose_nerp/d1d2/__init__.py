from __future__ import print_function, division
from .param_chan import (VMIN, VMAX, VDIVS, CAMIN, CAMAX, CADIVS,
                         qfactNaF,
                         Channels)
from .param_cond import (ghKluge,
                         neurontypes,
                         ConcOut, Temp,
                         morph_file,
                         Condset,
                         NAME_SOMA)
from .param_spine import SpineParams
from .param_syn import (SYNAPSE_TYPES,
                        NumSyn,
                        DesensitizationParams,
)

from . import param_ca_plas as CaPlasticityParams
from .param_stim import Stimulation
import logging

from moose_nerp.prototypes import (create_model_sim,
                                   constants)

#calcium: include or exclude calcium concentration dynamics, single tau
#synYN:No point adding synapses unless they receive inputs
#plasYN:include or exclude plasticity based on calcium

plasYN = False
desenYN = False
ghkYN = False #note that if ghkYN=0, make sure that ghKluge = 1
spineYN = False
synYN = False
calYN = True

# Putting here for now for testing, but could create a separate .py file
# called "defaults.py" or something, and just import it here. If so, could also
# set plasYN, desenYN, ghkYN, spineYN, synYN, and calYN in defaults.py rather
# than here in __init__.py
defaults = {}
defaults['logging_level'] = logging.DEBUG
defaults['default_injection_current'] = [-0.2e-9, 0.26e-9]
defaults['default_stim'] = 'inject'
defaults['default_stim_loc'] = NAME_SOMA
defaults['save'] = 0
defaults['plot_channels'] = 0
