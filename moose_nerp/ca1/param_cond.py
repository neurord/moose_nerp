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

#can use different morphologies for different neuron types
morph_file = {'CA1':'out_ri04_v3.p'}
NAME_SOMA='soma'
#CONDUCTANCES

# helper variables to index the Conductance and synapses with distance
inclu = (0, 1000e-6)

_CA1 = _util.NamedDict(
    'CA1',
    Kdr =  {inclu: 70.0},
    Kadist = {inclu: 200.0},
    Kaprox = {inclu: 200.0},
    Na = {inclu: 140.0},
)


Condset  = _util.NamedDict(
    'Condset',
    CA1 = _CA1,

)
