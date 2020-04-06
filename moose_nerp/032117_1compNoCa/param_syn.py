from moose_nerp.prototypes.util import NamedList, NamedDict
from moose_nerp.prototypes.syn_proto import SynChannelParams, MgParams

from . import param_cond

#Parameters for synpases (SI units):
#Erev (Volts), tau1 & tau2 (sec) 
#Gbar units: Siemens/meter squared
#C is concentration of Mg in mM, A is 1/eta and B is 1/gamma,

#These params are too insensitive to voltage
#mgparams={'A':(1/18.0), 'B':(1/99.0), 'C': 1.4}
#Classic (allows significant calcium at resting potential):
#mgparams={'A':(1/3.57), 'B':(1/62.0), 'C': 1.4}
#Intermediate
_NMDA_MgParams = MgParams(A = 1/6.0,
                           B = 1/80.0,
                           C = 1.4)

#Lavian Eur J Neurosci: Egaba=-75 mV, amp ~1mV at -60 mV
_SynGaba = SynChannelParams(Erev = -75e-3,
                             tau1 = 0.5e-3,
                             tau2 = 10e-3,
                             Gbar = 1.5e-9,
                             var=0.05)
#may need two time constants of decay to match Lavian
#Use 1.5e-9 for str and 3e-9 for GPe?
_SynAMPA = SynChannelParams(Erev = 0,
                             tau1 = 1e-3,
                             tau2 = 3e-3,
                             Gbar = 0.25e-9,
                             var=0.05,
                             spinic = True)
_SynNMDA = SynChannelParams(Erev = 0,
                             tau1 = 10e-3,
                             tau2 = 30e-3,
                             Gbar = 0.252e-9,
                             var=0.05,
                             MgBlock = _NMDA_MgParams,
                             spinic = True,
                             NMDA=True,
                             nmdaCaFrac = 0.05
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

#These will be used by synconn in connect.py, since AMPA and NMDA synapses usually go together
#for same reason, the next lines only list ampa and gaba, and nmda are created the same as ampa
NAME_AMPA='ampa'
NAME_NMDA='nmda'

# number of synapses at each distance
_gaba = {param_cond.prox:3, param_cond.dist:1}
_ampa= {param_cond.prox:1, param_cond.dist:2}
#CHANGE FROM 3 TO 2 on 7/26 to obtain ~20 Hz firing rate in response to in vivo like synaptic inputs

NumSyn={'ep':{'gaba':_gaba,
        'ampa':_ampa}}
