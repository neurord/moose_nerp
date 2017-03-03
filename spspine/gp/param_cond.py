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
prox = (0,1e-6)
#med =  (0,50e-6)
dist = (1e-6, 1000e-6)
# check Gbar vlues for NaS,Hva,SK and Ca
# _proto for prototypical GP neuron
_proto = _util.NamedDict(
    'proto',
    KDr = {prox:0,dist:0, },#, med:40.2},
    Kv3 = {prox:0, dist:0},#, med:38.4},
    KvF = {prox:0,dist:0 },#, med: 48},
    KvS = {prox:00, dist:00},#, med: 100
    NaF = {prox:00, dist:00},#, med: 100
    HCN1 = {prox:0.1, dist:0.1},#, med: 0
    HCN2 = {prox:0.5, dist:0.5}, #med: 0,
    KCNQ = {prox:0, dist:0},#, med: 2.512
    NaS = {prox:0,  dist:0},#med: 251.2,
    Ca = {prox:0, dist:0},#med: 0,
    SKCa = {prox:00 , dist:0},# med: 0,
    BKCa={prox:0, dist:0},# med: 10,
)
_arky = _util.NamedDict(
    'arky',
    KDr = {prox:0,dist:0 },#, med:40.2},
    Kv3 = {prox:0 , dist:0 },#, med:38.4},
    KvF = {prox:0,dist:0 },#, med: 48},
    KvS = {prox:0, dist:0},#, med: 100
    NaF = {prox:0, dist:0},#, med: 100
    HCN1 = {prox:0.1, dist:0.1},#, med: 0
    HCN2 = {prox:0.5, dist:0.5}, #med: 0,
    KCNQ = {prox:0, dist:0},#, med: 2.512
    NaS = {prox: 0,  dist:0},#med: 251.2,
    Ca = {prox:0, dist:0},#med: 0,
    SKCa = {prox:0, dist:0},# med: 0,
    BKCa={prox:0, dist:0},# med: 10,
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
)

Condset  = _util.NamedDict(
    'Condset',
    proto = _proto,
    arky=_arky,
)
