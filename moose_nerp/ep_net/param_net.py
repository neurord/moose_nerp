#param_net.py
####################### Populations
from moose_nerp.prototypes.util import NamedList
from moose_nerp.prototypes.ttables import TableSet
from moose_nerp.prototypes import util as _util
from moose_nerp.prototypes.syn_proto import ShortTermPlasParams,SpikePlasParams
from moose_nerp.prototypes.connect import dend_location,connect,ext_connect 

neur_distr=NamedList('neur_distr', 'neuronname spacing percent')

netname='/epnet'
confile='ep_connect'
outfile='ep_out'

spacing=60e-6 #need value and reference
#
#0,1,2 refer to x, y and z
grid={}
grid[0]={'xyzmin':0,'xyzmax':300e-6,'inc':spacing}
grid[1]={'xyzmin':0,'xyzmax':300e-6,'inc':spacing}
grid[2]={'xyzmin':300e-6,'xyzmax':300e-6,'inc':0}

#Do not include a neuron type in pop_dict if the the prototype does not exist
#Change neuronname to cellType
neuron1pop=neur_distr(neuronname='ep', spacing=grid,percent=1.0) 

#Change pop_dict to popParams
pop_dict={'ep':neuron1pop}

chanSTD = {
    'KDr': 0.02,
    'Kv3': 0.0196,
    'KvS': 0.0373,
    'KvF': 0.0083,
    'BKCa': 0.012,
    'SKCa': 0.075,
    'HCN1': 0.0625,
    'HCN2': 0.123,
    'Ca': 0.0436,
    'NaF': 0.0335,
    'NaS': 0.055,
}
chanvar={'ep':chanSTD}

####################### Connections

TWO_STR_INPUTS=0 #Change value to 1 to add second set of striatal time tables
#tables of extrinsic inputs
#first string is name of the table in moose, and 2nd string is name of external file
#tt_STN = TableSet('tt_STN', 'ep_net/STN_InhomPoisson',syn_per_tt=2)
tt_STN = TableSet('tt_STN', 'ep_net/STN_lognorm',syn_per_tt=2)
tt_str = TableSet('tt_str', 'ep_net/SPN_lognorm',syn_per_tt=2)
#tt_str = TableSet('tt_str', 'ep_net/str_InhomPoisson_freq4.0_osc1.8',syn_per_tt=2)
#tt_str = TableSet('tt_str', 'ep_net/str_InhomPoisson_freq4.0_osc1.8_theta10.0',syn_per_tt=2)
if TWO_STR_INPUTS:
    #tt_str2 = TableSet('tt_str2', 'ep_net/str_InhomPoisson_freq4.0_osc5.0',syn_per_tt=2)
    tt_str2 = TableSet('tt_str2', 'ep_net/str_InhomPoisson_freq4.0_osc5.0_theta5.0',syn_per_tt=2)
#tt_GPe = TableSet('tt_GPe', 'ep_net/GPe_InhomPoisson',syn_per_tt=2)
tt_GPe = TableSet('tt_GPe', 'ep_net/GPe_lognorm',syn_per_tt=2)

#description of intrinsic inputs
ConnSpaceConst=125e-6
ep_distr=dend_location(mindist=30e-6,maxdist=100e-6,postsyn_fraction=1,half_dist=50e-6,steep=1)
neur1pre_neur1post=connect(synapse='gaba', pre='ep', post='gaba', probability=0.5,dend_loc=ep_distr)#need reference for no internal connections

#description of synapse and dendritic location of extrinsic inputs
GPe_distr=dend_location(mindist=0,maxdist=60e-6,half_dist=30e-6,steep=-1)
if TWO_STR_INPUTS:
    str_distr=dend_location(mindist=30e-6,maxdist=1000e-6,postsyn_fraction=0.5,half_dist=100e-6,steep=1)
else:
    str_distr=dend_location(mindist=30e-6,maxdist=1000e-6,postsyn_fraction=1.0,half_dist=100e-6,steep=1)
STN_distr=dend_location(postsyn_fraction=0.9)
#STN_depress=SpikePlasParams(change_per_spike=0.9,change_tau=1.0,change_operator='*')
#STN_facil= SpikePlasParams(change_per_spike=0.6,change_tau=0.4,change_operator='+')
#STN_plas=ShortTermPlasParams(facil=STN_facil, depress=STN_depress)

#short term plasticity
#params from Lavian Eur J Neurosci, except GPe change_tau is faster to match data
GPe_depress=SpikePlasParams(change_per_spike=0.9,change_tau=0.6,change_operator='*')
GPe_plas=ShortTermPlasParams(depress=GPe_depress)
str_facil=SpikePlasParams(change_per_spike=0.6,change_tau=0.4,change_operator='+')
str_plas=ShortTermPlasParams(facil=str_facil)

#specify extrinsic inputs.  If two different gaba inputs have different amplitudes,
#may need to assign synaptic weight a different value for each
ext1_neur1post=ext_connect(synapse='ampa',pre=tt_STN,post='ep', dend_loc=STN_distr,weight=1.0)# need reference
ext2_neur1post=ext_connect(synapse='gaba',pre=tt_GPe,post='ep', dend_loc=GPe_distr,stp=GPe_plas,weight=2.0)
ext3_neur1post=ext_connect(synapse='gaba',pre=tt_str,post='ep', dend_loc=str_distr,stp=str_plas,weight=1.0)
if TWO_STR_INPUTS:
    ext4_neur1post=ext_connect(synapse='gaba',pre=tt_str2,post='ep', dend_loc=str_distr,stp=str_plas,weight=1.0)

#Collect all connection information into dictionaries
#1st create one dictionary for each post-synaptic neuron class
ep={}
#connections further organized by synapse type
#the dictionary key for tt must have 'extern' in it
if TWO_STR_INPUTS:
   ep['gaba']={'extern2': ext2_neur1post, 'extern3': ext3_neur1post, 'extern4': ext4_neur1post}
else:
    ep['gaba']={'extern2': ext2_neur1post, 'extern3': ext3_neur1post}#, 'ep':neur1pre_neur1post}
ep['ampa']={'extern1': ext1_neur1post}

#Then, collect the post-synaptic dictionaries into a single dictionary.
#for NetPyne correspondance: change connect_dict to connParams
connect_dict={}
connect_dict['ep']=ep

# m/sec - GABA and the Basal Ganglia by Tepper et al
cond_vel={'ep':0.8} #conduction velocity
mindelay={'ep':1e-3}
