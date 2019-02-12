# Generated from npzfile: fitep-ep-pchan_032717_162938.npz of fit number: 5722
#Do not define EREST_ACT or ELEAK here - they are in the .p file
# Contains maximal conductances, name of .p file, and some other parameters
# such as whether to use GHK, or whether to have real spines

import numpy as np

from moose_nerp.prototypes import util as _util

#if ghkYN=False then ghk not implemented
#Note that you can use GHK without a calcium pool, it uses a default of 5e-5 Cin
if False: # param_sim.Config['ghkYN']:
    ghKluge=0.35e-6
else:
    ghKluge=1
#using 0.035e-9 makes NMDA calcium way too small, using single Tau calcium

ConcOut=2e-3     # mM, default for GHK is 2e-3
Temp=30         # Celsius, needed for GHK objects, some channels

neurontypes = None
morph_file = {'ep':'EP_41compB_162938_ep_5722.p'}
NAME_SOMA='soma'

#CONDUCTANCES

# helper variables to index the Conductance and synapses with distance
# UNITS: meters
#soma spherical so x,y=0,0, 1e-6 means prox=soma
prox = (0,1e-6)
#med =  (0,50e-6)
dist = (1e-6, 1000e-6)
axon = (0.,1., 'axon')
#If using swc files for morphology, specify structure using: _1 as soma, _2 as apical dend, _3 as basal dend and _4 as axon

#CONDUCTANCE VALUES - UNITS of Siemens/meter squared
_ep = _util.NamedDict(
    'ep',
    KDr={prox: 87.20822921957834, dist: 7.003738121181193, axon: 222.9499419622778}, #KDr is Kv2
    Kv3={prox: 822.9783849138091, dist: 221.47346536550566, axon: 571.7413459607062},  
    KvS={prox: 1.2607614689487021, dist: 7.293988599249282, axon: 11.588543676550637},  
    KvF={prox: 17.105185611864304, dist: 17.275681005861088, axon: 6.439718525745909},  
    NaF={prox: 160.5098624216612, dist: 48.689751257426, axon: 3661.324423541809}, 
    NaS={prox: 5.899554971319288, dist: 9.924256975928728, axon: 4.446831864899851},
    Ca={prox: 0.8198658465772009, dist: 0.0013341233044197568, axon: 0},  
    HCN1={prox: 4.194450733328087, dist: 4.025948508906228, axon: 0}, 
    HCN2={prox: 2.7286797690191666, dist: 4.550548190296555, axon: 0}, 
    SKCa={prox: 2.00460422036248, dist: 0.36314594357834923, axon: 0},  
    BKCa={prox: 11.64588674353397, dist: 2.29946179927898, axon: 0}, 
)

Condset  = _util.NamedDict(
    'Condset',
    ep = _ep,
)

#Kv3 produces the early, fast transient AHP, if cond is high enough
