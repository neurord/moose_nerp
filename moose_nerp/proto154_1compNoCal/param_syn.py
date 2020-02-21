from moose_nerp.prototypes.util import NamedList, NamedDict
from moose_nerp.prototypes.syn_proto import SynChannelParams, MgParams

from . import param_cond

#Parameters for inhibitory synpases:
#Erev, tau1, tau2  (SI units)

#C is concentration of Mg, A is 1/eta and B is 1/gamma,
#Rebekah's:
#These params are too insensitive to voltage
#mgparams={'A':(1/18.0), 'B':(1/99.0), 'C': 1.4}
#Classic (allows significant calcium at resting potential):
#mgparams={'A':(1/3.57), 'B':(1/62.0), 'C': 1.4}
#Intermediate
_NMDA_MgParams = MgParams(A = 1/6.0,
                           B = 1/80.0,
                           C = 1.4)

#Dieter Jaeger uses 0.25e-9 for gaba
_SynGaba = SynChannelParams(Erev = -80e-3,
                             tau1 = 1e-3,
                             tau2 = 12e-3,
                             Gbar = 0.25e-9,
                             var=0.05)
_SynAMPA = SynChannelParams(Erev = 0,
                             tau1 = 1e-3,
                             tau2 = 3e-3,
                             Gbar = 0.15e-9,
                             var=0.05,
                             spinic = True)
_SynNMDA = SynChannelParams(Erev = 0,
                             tau1 = 10e-3,
                             tau2 = 30e-3,
                             Gbar = 0.15e-9,
                             var=0.05,
                             MgBlock = _NMDA_MgParams,
                             spinic = True,
                             NMDA=True,
                             nmdaCaFrac = 0.05
)

#these glutmate Gbar produce 1-2 mV EPSPs (depending on Vm, ~1 mV at -70)
#gaba Gbar of 0.5e-9 produces 1-2 mV IPSPs
#nmdaCaFra fraction of nmda current carried by calcium
#Note that since Ca reversal produces ~2x driving potential,
#need to make this half of typical value.  Default is 0.02 in Moose

SYNAPSE_TYPES = NamedDict(
    'SYNAPSE_TYPES',
    ampa = _SynAMPA,
    gaba = _SynGaba,
    nmda = _SynNMDA,
)
#These will be used by synconn in connect.py, since AMPA and NMDA synapses usually go together
#for same reason, the next lines only list ampa and gaba, and nmda are created the same as ampa
NAME_AMPA='ampa'
NAME_NMDA='nmda'

# number of synapses at each distance
_gaba = {param_cond.prox:30}
_ampa= {param_cond.prox:60}

NumSyn={'proto':{'gaba':_gaba,
        'ampa':_ampa}}
