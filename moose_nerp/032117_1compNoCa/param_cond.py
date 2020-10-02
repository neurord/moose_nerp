# Generated from npzfile: pchan_120617_162938.npz of fit number: 6583
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
morph_file = {'ep':'EP_93comp_162938_ep_6583.p'}
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
    KDr={prox: 40.72418803210975, dist: 15.281021142616872, axon: 54.17521010980912}, #KDr is Kv2
    Kv3={prox: 894.296110564778, dist: 320.5199679796315, axon: 545.0279818514284},  
    KvS={prox: 2.6809614156561015, dist: 13.284569545389955, axon: 20.250942471815257},  
    KvF={prox: 16.52422175199889, dist: 5.728087116287962, axon: 2.9237873704641246},  
    NaF={prox: 463.54289871619443, dist: 44.792343245965654, axon: 3333.775290658194}, 
    NaS={prox: 9.989552104855122, dist: 0.15181497997116822, axon: 8.240459761630305},
    Ca={prox: 0.013112098865593962, dist: 1.5914295903786322, axon: 0},  
    HCN1={prox: 0.6535629583013801, dist: 0.034112443425029226, axon: 0}, 
    HCN2={prox: 3.4854628178634406, dist: 3.815174011992935, axon: 0}, 
    SKCa={prox: 2.289940602646903, dist: 1.2098490677740237, axon: 0},  
    BKCa={prox: 4.158820279828881, dist: 8.057287727080345, axon: 0}, 
)

Condset  = _util.NamedDict(
    'Condset',
    ep = _ep,
)

#Kv3 produces the early, fast transient AHP, if cond is high enough
