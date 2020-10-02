# Generated from npzfile: pchan_032117_162938.npz of fit number: 8080
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

ConcOut=2     # mM, default for GHK is 2
Temp=30         # Celsius, needed for GHK objects, some channels

neurontypes = None
morph_file = {'ep':'EP_93comp_162938_ep_8080.p'}
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
    KDr={prox: 4.770646343567948, dist: 11.580858134398845, axon: 195.0403867814316}, #KDr is Kv2
    Kv3={prox: 736.8216998732888, dist: 1402.900645554406, axon: 729.2217379045869},  
    KvS={prox: 9.625003609239965, dist: 14.816596591818115, axon: 1.5141050650221697},  
    KvF={prox: 10.067142050937445, dist: 7.8844967404188235, axon: 16.175716784730458},  
    NaF={prox: 181.05412302395015, dist: 151.40473183042286, axon: 18391.466370001686}, 
    NaS={prox: 4.978184560770554, dist: 6.763970102779737, axon: 7.136171989201076},
    Ca={prox: 0.15508085299411955, dist: 0.108440912242796829, axon: 0},  
    HCN1={prox: 0.08583627688169095, dist: 0.44055539373336716, axon: 0}, 
    HCN2={prox: 0.47365915156951843, dist: 0.5262383869994962, axon: 0}, 
    SKCa={prox: 0.43383651241744997, dist: 0.4505619092332097, axon: 0},  
    BKCa={prox: 6.968570081935845, dist: 5.931895239981525, axon: 0}, 
)

Condset  = _util.NamedDict(
    'Condset',
    ep = _ep,
)

#Kv3 produces the early, fast transient AHP, if cond is high enough
