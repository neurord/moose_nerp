from moose_nerp.prototypes.util import NamedList, NamedDict
from moose_nerp.prototypes.syn_proto import SynChannelParams, MgParams, DesensitizationParams

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
desenYN =  0
_NMDA_MgParams = MgParams(A = 1/18.0,
                           B = 1/99.0,
                           C = 1.4)

#Sriram uses 0.109e-9 for AMPA and 0.9e-9 for Gaba
_SynGaba = SynChannelParams(Erev = -60e-3,
                             tau1 = 0.25e-3,
                             tau2 = 3.75e-3,
                             Gbar = 0.2e-9,
                            nmdaCaFrac = 0.0,
                             var=0.05)

SynGabaNPY = SynChannelParams(Erev = -60e-3, #NPY
                             tau1 = 0.25e-3,
                             tau2 = 80.75e-3,
                             Gbar = 0.5e-9,
                              nmdaCaFrac = 0.0,
                             var=0.05)

_SynAMPA = SynChannelParams(Erev = 5e-3,
                             tau1 = 1.1e-3,
                             tau2 = 2.0e-3,
                            Gbar = 2e-9,
                            var=0.05,
                            nmdaCaFrac = 0.001,
                             spinic = True)
_SynNMDA = SynChannelParams(Erev = 5e-3,
                             tau1 = 1.1e-3,
                             tau2 = 37.5e-3,
                             Gbar = 2e-9,
                             var=0,#0.05,
                             MgBlock = _NMDA_MgParams,
                             spinic = True,
                             NMDA=True,
                             nmdaCaFrac = 0.05,
)

#nmdaCaFra fraction of nmda current carried by calcium
#Note that since Ca reversal produces ~2x driving potential,
#need to make this half of typical value.  Default is 0.02 in Moose

SYNAPSE_TYPES = NamedDict(
    'SYNAPSE_TYPES',
    ampa = _SynAMPA,
    gaba = _SynGaba,
    nmda = _SynNMDA,
)
DesensitizationParams = NamedDict('Synapse_desensitization',gaba = None, nmda=None, ampa=DesensitizationParams(dep_per_spike=0.39,dep_tau=0.8))

#These will be used by synconn in connect.py, since AMPA and NMDA synapses usually go together
#for same reason, the next lines only list ampa and gaba, and nmda are created the same as ampa
NAME_AMPA='ampa'
NAME_NMDA='nmda'


# number of synapses at each distance
_gaba = {param_cond.prox:4, param_cond.med:4, param_cond.dist:4}
_ampa= {param_cond.prox:1, param_cond.med:2, param_cond.dist:3}

NumSyn={'gaba':_gaba,
        'ampa':_ampa}
