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
calYN = False #True #Flag to set for simulation of Calcium chracteristics of neuron.
plasYN = False #Flag to set for simulation of Plasticity of neuron.
ghkYN = False #Flag to set for GHK channel conductances currents simulation.
spineYN = False #Flag to set for Dendritic Spine simulation
synYN = False #Flag to set for simulation of synapses.

#note that if ghkYN=0, make sure that ghKluge = 1


