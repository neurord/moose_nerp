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
neuron1pop=neur_distr(neuronname='proto', spacing=grid,percent=0.60) #Table 2 Hernandez Parvabinum+ Neurons and arky Neurons 2015
#calculated from percent composition of PV+=proto, Npas1+/FoxP2+=Npas, Lhx6=arky
neuron2pop=neur_distr(neuronname='Npas', spacing=grid,percent=0.25)
neuron3pop=neur_distr(neuronname='Lhx6', spacing=grid,percent=0.15)
pop_dict={'proto':neuron1pop,'Npas': neuron2pop,'Lhx6':neuron3pop}

#from arky140F - loc _0, unless CV close to 1
chanSTD_arky = {
    'KDr': 0.0397,
    'Kv3': 0.0386,
    'KvS': 0.0743,
    'KvF': 0.0173,
    #'KCNQ': 0.0267,
    #'BKCa': 0.0238,
    #'SKCa': 0.295,
    #'HCN1': 0.2454,
    'HCN2': 0.253,
    #'Ca': 0.1671,
    'NaF': 0.0635,
    #'NaS': 0.215,
}
#from proto154 - loc _0, unless CV close to 1
chanSTD_proto = {
    'KDr': 0.0487,
    'Kv3': 0.0177,
    'KvS': 0.0306,
    'KvF': 0.0114,
    #'HCN1': 0.139,
    'HCN2': 0.175,
    #'KCNQ': 0.068,
    #'Ca': .0384,
    'NaF': 0.0302,
    #'NaS': 0.1308,
    #'BKCa': 0.0496,
    #'SKCa': 0.2048,
}
chanvar={'proto':chanSTD_proto, 'Npas':chanSTD_arky, 'Lhx6':chanSTD_arky}

####################### Connections
#for improved NetPyne correspondance: change synapse to synMech, change pre to source
#Two types of probabilities controlling the connections
#A. probability of connecting two different neurons.  NamedList('connect'Parameters include
#A1. constant probability
#A2. space_const: allows distance dependent connection, where distance is measured between pre- and post-synaptic neuron's cell bodies
#A3. num_conns allows a single pre-synaptic cell to make more than one connection on the post-synaptic cell
#B. dend_loc, which controls the dendritic location of post-synaptic target as follows
#mindist, maxdist, half_dist, steep  are alternatives to postsyn_fraction 
#connect_prob=0 if dist<mindist
#connect_prob=0 if dist>maxdist
#connect_prob = probability if dist between mindist and maxdist, or
#if half_dist is defined:
#for steep>0: connect_prob=1 if dist>maxdist and 0 if dist<mindist 
#connect_prob=(dist-mindist)^steep/((dist-mindist)^steep+half_dist^steep)
#make steep<0 to switch slope and have connect_prob=1 if dist<mindist and 0 if dist>maxdist
#do not use steep (or set to zero) to have constant connection probability between min and maxdist

#Intrinsic (within network) connections specified using NamedList('connect'
#Extrinsic (external time table) connections specified using NamedList('ext_connect'
#post syn fraction: what fraction of synapse is contacted by time tables specified in pre 

dend_location=NamedList('dend_location','mindist=0 maxdist=1 maxprob=None half_dist=None steep=0 postsyn_fraction=None')

#probability for intrinsic is the probability of connecting pre and post.
connect=NamedList('connect','synapse pre post num_conns=2 space_const=None probability=None dend_loc=None stp=None weight=1')
ext_connect=NamedList('ext_connect','synapse pre post dend_loc=None stp=None weight=1')

#tables of extrinsic inputs
#first string is name of the table in moose, and 2nd string is name of external file
tt_STN = TableSet('tt_STN', 'gp_net/STN_lognorm_freq18.0',syn_per_tt=2)

#description of intrinsic inputs
ConnSpaceConst=500e-6
neur1pre_neur1post=connect(synapse='gaba', pre='proto', post='proto', space_const=ConnSpaceConst)#internal post syn fraction in 10% Shink Smith 1995
neur1pre_neur2post=connect(synapse='gaba', pre='proto', post='Npas', space_const=ConnSpaceConst)
neur1pre_neur3post=connect(synapse='gaba', pre='proto', post='Lhx6', space_const=ConnSpaceConst)
neur2pre_neur1post=connect(synapse='gaba', pre='Npas', post='proto', space_const=ConnSpaceConst)
neur2pre_neur2post=connect(synapse='gaba', pre='Npas', post='Npas', space_const=ConnSpaceConst)
neur2pre_neur3post=connect(synapse='gaba', pre='Npas', post='Lhx6', space_const=ConnSpaceConst)
neur3pre_neur1post=connect(synapse='gaba', pre='Lhx6', post='proto', space_const=ConnSpaceConst)
neur3pre_neur2post=connect(synapse='gaba', pre='Lhx6', post='Npas', space_const=ConnSpaceConst)
neur3pre_neur3post=connect(synapse='gaba', pre='Lhx6', post='Lhx6', space_const=ConnSpaceConst)

#description of synapse and dendritic location of extrinsic inputs
STN_distr=dend_location(postsyn_fraction=0.5)
ext2_neur1post=ext_connect(synapse='ampa',pre=tt_STN,post='proto', dend_loc=STN_distr)# Corbit Whalen 2016 Table 2 connectivity parameters: Chumhma 2011, Shink Smith 1995, Miguelez 2012 
#ext1_neur1post=ext_connect(synapse='gaba',pre=tt_Str_SPN,post='proto', dend_loc=Str_distr)#ext1 = Str
ext2_neur2post=ext_connect(synapse='ampa',pre=tt_STN,post='Npas', dend_loc=STN_distr)#ext2 STN
#ext1_neur2post=ext_connect(synapse='gaba',pre=tt_Str_SPN,post='Npas', dend_loc=Str_distr)
ext2_neur3post=ext_connect(synapse='ampa',pre=tt_STN,post='Lhx6', dend_loc=STN_distr)#ext2 STN

#Collect all connection information into dictionaries
#1st create one dictionary for each post-synaptic neuron class
proto={}
Npas={}
Lhx6={}
#connections further organized by synapse type
#the dictionary key for tt must have 'extern' in it
proto['gaba']={'proto': neur1pre_neur1post, 'Npas': neur2pre_neur1post,'Lhx6': neur3pre_neur1post}
#proto['gaba']={'proto': neur1pre_neur1post, 'Npas': neur2pre_neur1post, 'extern': ext1_neur1post}
proto['ampa']={'extern': ext2_neur1post}
Npas['gaba']={'proto': neur1pre_neur2post, 'Npas': neur2pre_neur2post, 'Lhx6': neur3pre_neur2post}
#Npas['gaba']={'proto': neur1pre_neur2post, 'Npas': neur2pre_neur2post, 'extern': ext1_neur2post}
Npas['ampa']={'extern': ext2_neur2post}
Lhx6['gaba']={'proto': neur1pre_neur3post, 'Npas': neur2pre_neur3post, 'Lhx6': neur3pre_neur3post}
#Npas['gaba']={'proto': neur1pre_neur2post, 'Npas': neur2pre_neur2post, 'extern': ext1_neur2post}
Lhx6['ampa']={'extern': ext2_neur3post}

#Then, collect the post-synaptic dictionaries into a single dictionary.
#for NetPyne correspondance: change connect_dict to connParams
connect_dict={'proto': proto,'Npas':Npas,'Lhx6':Lhx6}

# m/sec - GABA and the Basal Ganglia by Tepper et al
cond_vel={'proto':0.8,'Npas':0.8, 'Lhx6':0.8} #conduction velocity
mindelay={'proto':1e-3,'Npas':1e-3,'Lhx6':1e-3}
