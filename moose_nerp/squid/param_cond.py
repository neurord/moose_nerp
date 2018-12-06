# Generated from npzfile: Sriramsagarsquid-squid-squid_experimentaltau_z.npz of fit number: 1
# Contains maximal conductances, name of .p file(neuron morphology file), and some other parameters
import numpy as np

from moose_nerp.prototypes import util as _util

if False: # param_sim.Config['ghkYN']:
    ghKluge=0.35e-6
else:
    ghKluge=1

ConcOut=2e-3     # default for GHK is 2e-3
Temp=30         # Celsius, needed for GHK objects, some channels

neurontypes = None


# NOTE: Morph file is neuron shape file (*.p) in the model root directory.
#morph_file = {'squid':'squid.p'} # Single compartment Squid morphology model.
morph_file = {'squid':'squid_10C.p'} # ten compartments Squid morphology model.
NAME_SOMA='axon' # Parent compartment to simulate squid axon where NAME_SOMA is application variable.

#CONDUCTANCES

# helper variables to index the Conductance and synapses with distance
#axon cylindrical so x,y=0,0, 1e-6 means parent compartment only for spherical.
prox = (0,1e-3) # Length Range of the proximal dendrite from center of soma.
dist = (1e-3, 100e-3)
# Channel conductances declaration for the squid axon.
_squid = _util.NamedDict(
    'squid',
    K={prox: 375.03539122514456, dist: 528.0073725807185},  # Potassium channel g_bar to the squid axon surface.
    Na={prox: 1239.4810169236575, dist: 1349.8902763186481}, # Sodium channel g_bar to the squid axon surface.
    Krp={prox: 1, dist: 3},
    SKCa={prox: .01, dist: .01}
    )

# Channel conductances
Condset  = _util.NamedDict(
    'Condset',
    squid = _squid,
)
