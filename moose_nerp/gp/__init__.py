from .param_chan import (VMIN, VMAX, VDIVS, CAMIN, CAMAX, CADIVS,
                         qfactNaF,
                         Channels)
from .param_cond import (ghKluge,
                         neurontypes,
                         ConcOut, Temp,
                         morph_file,
                         Condset)
from .param_spine import SpineParams
from .param_syn import (SYNAPSE_TYPES,
                        NumSyn)
from . import param_ca_plas as CaPlasticityParams
from .param_stim import Stimulation

#calcium: include or exclude calcium concentration dynamics, single tau
#synYN:No point adding synapses unless they receive inputs
#plasYN:include or exclude plasticity based on calcium
#calcium, spines and synapses are copied from d1d2.
#Need to edit them if added to GP neuron
calYN = True
plasYN = False
ghkYN = False
spineYN = False
synYN = False

#note that if ghkYN=0, make sure that ghKluge = 1
