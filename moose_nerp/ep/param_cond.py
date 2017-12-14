#Do not define EREST_ACT or ELEAK here - they are in the .p file
# Contains maximal conductances, name of .p file, and some other parameters
# such as whether to use GHK, or whether to have real spines

import numpy as np

from moose_nerp.prototypes import util as _util

#if ghkYesNo=0 then ghk not implemented
#Note that you can use GHK without a calcium pool, it uses a default of 5e-5 Cin
if False: # param_sim.Config['ghkYN']:
    ghKluge=0.35e-6
else:
    ghKluge=1

#using 0.035e-9 makes NMDA calcium way too small, using single Tau calcium
ConcOut=2e-3     # default for GHK is 2e-3
Temp=30         # Celsius, needed for GHK objects, some channels

_neurontypes = None
def neurontypes(override=None):
    "Query or set names of neurontypes of each neuron created"
    global _neurontypes
    if override is None:
        return _neurontypes if _neurontypes is not None else sorted(Condset.keys())
    else:
        if any(key not in Condset.keys() for key in override):
            raise ValueError('unknown neuron types requested')
        _neurontypes = override

morph_file = {'ep':'EP_41compA.p'}
NAME_SOMA='soma'

#CONDUCTANCES

# helper variables to index the Conductance and synapses with distance
#soma spherical so x,y=0,0, 1e-6 means prox=soma
prox = (0,1e-6)
#med =  (0,50e-6)
dist = (1e-6, 1000e-6)
axon = (0.,1., 'axon')

_ep = _util.NamedDict(
    'ep',
    KDr={prox: 0.61, dist: 1.92, axon: 95.7}, #KDr is Kv2
    Kv3={prox: 318, dist: 81.5, axon: 0.68},  
    KvS={prox: 4.75, dist: 4.6, axon: 195},  
    NaF={prox: 4483, dist: 33.2, axon: 4597}, 
    NaS={prox: 1.04, dist: 0.3, axon: 0.3},
    Ca={prox: 0.0077, dist: 0.06, axon: 0},  
    HCN1={prox: 0.16, dist: 0.16, axon: 0}, 
    HCN2={prox: 0.30, dist: 0.30, axon: 0}, 
    SKCa={prox: 1.94, dist: 0.15, axon: 0},  
    BKCa={prox: 4.48, dist: 0.1, axon: 0}, 
)


Condset  = _util.NamedDict(
    'Condset',
    ep = _ep,
)
