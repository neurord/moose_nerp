#param_net.py
####################### Populations
from moose_nerp.prototypes.util import NamedList
from moose_nerp.prototypes.ttables import TableSet
from moose_nerp.prototypes import util as _util

neur_distr=NamedList('neur_distr', 'neuronname spacing percent')

netname='/gp'
confile='gp_connect'
outfile='gp_out'

spacing=54e-6 #Fig. 2 Hernandez Parvabinum+ Neurons and Npas1+ Neurons 2015
#pv+: 54e-6 n=41, npas1+: 60e-6 n=33, calculated by measuring distance between neuron pairs and calculating mean 
#0,1,2 refer to x, y and z
grid={}
grid[0]={'xyzmin':0,'xyzmax':100e-6,'inc':spacing}
grid[1]={'xyzmin':0,'xyzmax':100e-6,'inc':spacing}
grid[2]={'xyzmin':0,'xyzmax':0,'inc':0}

#Do not include a neuron type in pop_dict if the proto not created
neuron1pop=neur_distr(neuronname='proto', spacing=grid,percent=0.54) #Table 2 Hernandez Parvabinum+ Neurons and Npas1+ Neurons 2015
#calculated from percent composition of PV+=proto, Npas1+/FoxP2+=arky
neuron2pop=neur_distr(neuronname='arky', spacing=grid,percent=0.46)
pop_dict={'proto':neuron1pop,'arky': neuron2pop}

#from arky140F - loc _0, unless CV close to 1
chanSTD_arky = {
    'KDr': 0.0397,
    'Kv3': 0.0386,
    'KvS': 0.0743,
    'KvF': 0.0173,
    'KCNQ': 0.0267,
    'BKCa': 0.0238,
    'SKCa': 0.295,
    'HCN1': 0.2454,
    'HCN2': 0.253,
    'Ca': 0.1671,
    'NaF': 0.0635,
    'NaS': 0.215,
}
#from proto154 - loc _0, unless CV close to 1
chanSTD_proto = {
    'KDr': 0.0487,
    'Kv3': 0.0177,
    'KvS': 0.0306,
    'KvF': 0.0114,
    'HCN1': 0.139,
    'HCN2': 0.175,
    'KCNQ': 0.068,
    'Ca': .0384,
    'NaF': 0.0302,
    'NaS': 0.1308,
    'BKCa': 0.0496,
    'SKCa': 0.2048,
}
chanvar={'proto':chanSTD_arky, 'arky':chanSTD_proto}

####################### Connections
connect=NamedList('connect','synapse pre post space_const=None probability=None')
ext_connect=NamedList('ext_connect','synapse pre post postsyn_fraction')
# add post_location to both of these - optionally specify e.g. prox vs distal for synapses

#first string is name of the table in moose, and 2nd string is name of external file
tt_STN = TableSet('tt_STN', 'Ctx_4x4',syn_per_tt=2)
tt_Str_SPN = TableSet('tt_Str', 'Thal_4x4',syn_per_tt=2)

ConnSpaceConst=125e-6

neur1pre_neur1post=connect(synapse='gaba', pre='proto', post='proto', space_const=ConnSpaceConst)#internal post syn fraction in 10% Shink Smith 1995
neur1pre_neur2post=connect(synapse='gaba', pre='proto', post='arky', space_const=ConnSpaceConst)
neur2pre_neur1post=connect(synapse='gaba', pre='arky', post='proto', space_const=ConnSpaceConst)
neur2pre_neur2post=connect(synapse='gaba', pre='arky', post='arky', space_const=ConnSpaceConst)
#post syn fraction: what fraction of synapse is contacted by time tables specified in pre 
ext2_neur1post=ext_connect(synapse='ampa',pre=tt_STN,post='proto', postsyn_fraction=1.0)#change ctx to Str MSN, Corbit Whalen 2016 Table 2 connectivity parameters: Chumhma 2011, Shink Smith 1995, Miguelez 2012 
ext1_neur1post=ext_connect(synapse='gaba',pre=tt_Str_SPN,post='proto', postsyn_fraction=0.33)#ext1 = Str
ext2_neur2post=ext_connect(synapse='ampa',pre=tt_STN,post='arky', postsyn_fraction=1.0)#ext2 STN
ext1_neur2post=ext_connect(synapse='gaba',pre=tt_Str_SPN,post='arky', postsyn_fraction=0.33)
#one dictionary for each post-synaptic neuron class
proto={}
arky={}
connect_dict={}
##Collect the above connections into dictionaries organized by post-syn neuron, and synapse type
#the dictionary key for tt must have 'extern' in it
proto['gaba']={'proto': neur1pre_neur1post, 'arky': neur2pre_neur1post, 'extern': ext1_neur1post}
proto['ampa']={'extern': ext2_neur1post}
connect_dict['proto']=proto
arky['gaba']={'proto': neur1pre_neur2post, 'arky': neur2pre_neur2post, 'extern': ext1_neur2post}
arky['ampa']={'extern': ext2_neur2post}
connect_dict['arky']=arky

# m/sec - GABA and the Basal Ganglia by Tepper et al
cond_vel=0.8 #conduction velocity
mindelay=1e-3
