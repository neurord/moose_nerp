#param_net.py

from moose_nerp.prototypes.ttables import TableSet
from moose_nerp.prototypes.syn_proto import ShortTermPlasParams,SpikePlasParams
from moose_nerp.prototypes.util import NamedList
from moose_nerp.prototypes.connect import dend_location,connect,ext_connect 

confile='bg_connect'
outfile='bg_out'

#changes to number of synapses; multiply by NumSyn
#  - increases number of external inputs
# - increases available synapses (fixes synchan_shortage) for intrinsic connections
change_syn={'proto':{'gaba':3},'Lhx6':{'gaba':3},'Npas':{'gaba':3},'ep':{'ampa':2.0,'gaba':3},'D1':{'gaba':3},'D2':{'gaba':3}}
merge_connect=True
##########################
'''
Two methods for merging different networks
A. use connect_dict from other populations(moose_nerp network packages), but with modifications
    set merge_connect = True
    update change_weight to update the synaptic strength of connections
    update change_prob to update the connection probability
B. do not use connect_dict from other populations (moose_nerp network packages)
   set merge_connect = False
   all connections must be specified in connect_dict
Possibly A should be replaced with C: read in and update network modules here?
'''

#New external time tables - (filename, syn_per_tt)
tt_Ctx=TableSet('CtxSPN', 'bg_net/Ctx10000_exp_freq10.0',syn_per_tt=4)
tt_STN=TableSet('tt_STN','bg_net/STN2000_lognorm_freq18.0',syn_per_tt=4)

ttable_replace={}

ttable_replace={'ep': {'ampa':{'extern1':tt_STN}}}

ttable_replace['proto']={'ampa':{'extern':tt_STN}}
ttable_replace['Npas']={'ampa':{'extern':tt_STN}}
ttable_replace['Lhx6']={'ampa':{'extern':tt_STN}}

ttable_replace['D1']={'ampa':{'extern1':tt_Ctx}}
ttable_replace['D2']={'ampa':{'extern1':tt_Ctx}}
ttable_replace['FSI']={'ampa':{'extern':tt_Ctx}}

#######################################
#three types of distributions
####################### Connections
even_distr=dend_location(postsyn_fraction=0.5)
proximal_distr= dend_location(mindist=0e-6,maxdist=80e-6,postsyn_fraction=1)
distal_distr=dend_location(mindist=50e-6,maxdist=400e-6,postsyn_fraction=.1)#,half_dist=50e-6,steep=1)

##connections between regions
#Inputs to ep/SNr from Striatum/D1 and GPe/proto.  Weight = 0.33 because Gbar=1.5 nA for multi-comp model
connect_dict={}

##### Note that number of inputs = probability * number of presyn neurons. Thus,
## if increase presyn neurons, will increase inputs
connect_dict={'ep':{'gaba':{}}}
connect_dict['ep']['gaba']['proto']=connect(synapse='gaba', pre='proto', post='ep', probability=0.2,weight=1)
#PSP amp proto to ep: 2.5 mV
connect_dict['ep']['gaba']['Lhx6']=connect(synapse='gaba', pre='Lhx6', post='ep', probability=0.2,weight=1)
#PSP amp 2.8, 6.3 mV
connect_dict['ep']['gaba']['D1']=connect(synapse='gaba', pre='D1', post='ep', probability=0.2,weight=1)
#PSP amp D1 to ep: 3.1, 4.5 mV - still too big?

#Inputs from striatum to GPe
D2_to_GPe=0.02
#Input resistance.  Npas: 360 MOhm, proto: 280 Mohm, Lhx6: 300 Mohm
connect_dict['Npas']={'gaba':{}}
connect_dict['Npas']['gaba']['D2']=connect(synapse='gaba', pre='D2', post='Npas', probability=D2_to_GPe)
#PSP amp d2 to Npas: 3.4, 5.1mV at -58, 1 mV at -65
connect_dict['Lhx6']={'gaba':{}}
connect_dict['Lhx6']['gaba']['D2']=connect(synapse='gaba', pre='D2', post='Lhx6', probability=D2_to_GPe)
#PSP amp D2 to Lhx6: 4.1,6.9 at -58, ~2 mV at -66
connect_dict['proto']={'gaba':{}}
connect_dict['proto']['gaba']['D2']=connect(synapse='gaba', pre='D2', post='proto', probability=D2_to_GPe)
#PSP amp d2 to proto: -6.7, 4, 4 mV at ~-51

#Inputs from GPe back to Striatum
#PSP ranges from 0.5-1.3 mV to SPNs; Gsyn=0.2 nS.  If vclamp in Corbit was at rest, e.g. ~-80 mV with ~20 mV driving potential, that yields 4 pA current
#Corbit values: 0 +/0 40 pA (possibly with optogenetic activation of multiple synapses?)
#For FSIs: 565 pA +/- 560 pA; weight=3 with 0.4 nS Gsyn yields 1.2,2.2,3 mV depolarizations; should be 6x the current
#input resistance: D1: 140 MOhm, D2: 160 MOhm, FSI: 90 (-50 pA), or 170 MOhm (-100 pA) - these are a bit low
connect_dict['D2']={'gaba':{}}
connect_dict['D2']['gaba']['Npas']=connect(synapse='gaba', pre='Npas', post='D2', probability=0.5)
connect_dict['D1']={'gaba':{}}
connect_dict['D1']['gaba']['Npas']=connect(synapse='gaba', pre='Npas', post='D1', probability=0.5)
connect_dict['FSI']={'gaba':{}}
connect_dict['FSI']['gaba']['Lhx6']=connect(synapse='gaba', pre='Lhx6', post='FSI', probability=0.5,weight=3)

#Note: AMPA strength=2.2-2.4 (SPN), 2.5-3 (EP), 1.2 (Npas),1.6-1.8(Lhx6), 1.2 (proto during firing)

##################### These are only used if connect_merge==True ##################
########## Delete these connections that are defined in the other net_modules
# e.g., extrinsic connections that are now replaced by other network connections
connect_delete={}

connect_delete={'ep':{'gaba':['extern2','extern3']}}
#once STN neurons provided:
#connect_delete['ep']['ampa']='extern'
#connect_delete['proto']={'ampa':'extern'}
#connect_delete['Lhx6']={'ampa':'extern'}
#connect_delete['Npas']={'ampa':'extern'}
#delete intra striatal connections to measure strength of individual GPe inputs
'''
connect_delete['D1']={'gaba':['D1','D2','FSI']}
connect_delete['D2']={'gaba':['D1','D2','FSI']}
connect_delete['FSI']={'gaba':['FSI']}
connect_delete['proto']={'gaba':['proto','Npas','Lhx6']}
connect_delete['Npas']={'gaba':['proto','Npas','Lhx6']}
connect_delete['Lhx6']={'gaba':['proto','Npas','Lhx6']}
'''

######### change weight of synapses, e.g. to add asymmetry as measured in striatum,
#also to prevent proto from preventing all firing

change_weight={'D1':{'gaba':{'D2':('weight',1.2),'D1':('weight',0.8)}},
               'D2':{'gaba':{'D2':('weight',1.0),'D1':('weight',1.0)}},
               'ep':{'ampa':{'extern1':('weight',2.0)}}}

############ change connection probability 
#example of tuples needed to change connection probability between neurons
#use multiplicative factor for space constant, since those are such small numbers
#>1 would decrease connections, <1 would increase connections
#use actual value for probability of connection
#The following compensate for very high firing frequency when increasing network size
#could also decrease weight of ampa synapses

change_prob={'proto':{'gaba':{'proto':('space',0.5),'Lhx6':('space',0.6),'Npas':('space',0.6)}},
             'Lhx6':{'gaba':{'proto':('space',0.5),'Lhx6':('space',0.6),'Npas':('space',0.6)}},
             'Npas':{'gaba':{'proto':('space',0.5),'Lhx6':('space',0.6),'Npas':('space',0.6)}}}

mindelay={}
cond_vel={}

'''
For external connections, the total number of synapses from each set of time tables to post-synaptic cell =
number of synapses*probability (or postsyn_fraction for dend_location)
If multiple sets of time tables, need to ensure sum of probabilities <= 1
To change effect on post-synaptic cell, increase or decrease NumSyn, synaptic conductance, probability, or  firing rate of input tt

for internal connections, , the total number of synapses from each pre-synaptic neuron type to post-synaptic cell =
number of synapses*probability (or postsyn_fraction for dend_location)
If multiple types of pre-synaptic neurons, need to ensure sum of probabilities <= 1
To change effect on post-synaptic cell, increase or decrease NumSyn,, synaptic conductance or probability
'''
