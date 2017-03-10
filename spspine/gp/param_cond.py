#Do not define EREST_ACT or ELEAK here - they are in the .p file
# Contains maximal conductances, name of .p file, and some other parameters
# such as whether to use GHK, or whether to have real spines

import numpy as np

from spspine import util as _util

#if ghkYesNo=0 then ghk not implemented
#Note that you can use GHK without a calcium pool, it uses a default of 5e-5 Cin
if False: # param_sim.Config['ghkYN']:
    ghKluge=0.35e-6
else:
    ghKluge=1

#using 0.035e-9 makes NMDA calcium way too small, using single Tau calcium
ConcOut=2e-3     # default for GHK is 2e-3
Temp=30         # Celsius, needed for GHK objects, some channels

def neurontypes():
    "Names of neurontypes of each neuron created"
    return sorted(Condset.keys())

####These numbers are used with split to extract channel and compartment names
compNameNum=2

#will eventually use different morphologies also
morph_file = {'proto':'GP1_41comp.p','arky':'GP_arky_41comp.p'}
NAME_SOMA='soma'

#CONDUCTANCES
#Kdr is Kv2
# helper variables to index the Conductance and synapses with distance
#soma spherical so x,y=0,0, 1e-6 means prox=soma
prox = (0,1e-6)
#med =  (0,50e-6)
dist = (1e-6, 1000e-6)
axon = (0.,1., 'axon')
# check Gbar vlues for NaS,Hva,SK and Ca
# _proto for prototypical GP neuron
_proto = _util.NamedDict(
    'proto',
    KDr = {prox:320,dist:64, axon:640},
    Kv3 = {prox:640, dist:128,axon:1280},#, med:38.4},
    KvF = {prox:20,dist:20,axon:200 },#, med: 48},
    KvS = {prox:12, dist:12,axon:120},#, med: 100
    NaF = {prox:2500, dist:40,axon:5000},#, med: 100
    HCN1 = {prox:0.2, dist:0.2,axon:0},#, med: 0
    HCN2 = {prox:0.5, dist:0.5,axon:0}, #med: 0,
    KCNQ = {prox:0.4, dist:0.4,axon:0.4},#, med: 2.512
    NaS = {prox:1,  dist:1,axon:40},#med: 251.2,
    Ca = {prox:0.1, dist:0.02,axon:0},#med: 0,
    SKCa = {prox:7.14, dist:0.6,axon:0},# med: 0,
    BKCa={prox:0.1, dist:0.1,axon:0},# med: 10,
)
_arky = _util.NamedDict(
    'arky',
    KDr = {prox:320,dist:64,axon:640 },#, med:40.2},
    Kv3 = {prox:640 , dist:128,axon:1280 },#, med:38.4},
    KvF = {prox:160,dist:160,axon:1600 },#, med: 48},
    KvS = {prox:240, dist:240,axon:2400},#, med: 100
    NaF = {prox:2500, dist:40,axon:5000},#, med: 100
    HCN1 = {prox:0.2, dist:0.2,axon:0},#, med: 0
    HCN2 = {prox:0.25, dist:0.25,axon:0}, #med: 0,
    KCNQ = {prox:0.4, dist:0.4,axon:0.4},#, med: 2.512
    NaS = {prox: 1,  dist:1,axon:40},#med: 251.2,
    Ca = {prox:2, dist:0.15,axon:0},#med: 0,
    SKCa = {prox:50, dist:4,axon:0},# med: 0,
    BKCa={prox:0.1, dist:0.1,axon:0},# med: 10,
)
chanvar = _util.NamedDict(
    'chanvar',
    KDr=0.04,
    Kv3=0.04,
    KvF=0.04,
    Kvs=0.04,
    NaF=0.0,
    HCN1=0.04,
    HCN2=0.04,
    KCNQ=0.04,
    NaS = 0.04,
    SKCa= 0.04,
    Ca = 0.04,
    BKCa=0.04
)

Condset  = _util.NamedDict(
    'Condset',
    proto = _proto,
    arky=_arky,
)
