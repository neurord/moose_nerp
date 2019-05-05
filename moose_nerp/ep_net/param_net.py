#param_net.py
####################### Populations
from moose_nerp.prototypes.util import NamedList
from moose_nerp.prototypes.ttables import TableSet
from moose_nerp.prototypes import util as _util
from moose_nerp.prototypes.syn_proto import ShortTermPlasParams,SpikePlasParams

neur_distr=NamedList('neur_distr', 'neuronname spacing percent')

netname='/epnet'
confile='ep_connect'
outfile='ep_out'

spacing=60e-6 #need value and reference
#
#0,1,2 refer to x, y and z
grid={}
grid[0]={'xyzmin':0,'xyzmax':100e-6,'inc':spacing}
grid[1]={'xyzmin':0,'xyzmax':100e-6,'inc':spacing}
grid[2]={'xyzmin':0,'xyzmax':0,'inc':0}

#Do not include a neuron type in pop_dict if the the prototype does not exist
#Change neuronname to cellType
neuron1pop=neur_distr(neuronname='ep', spacing=grid,percent=1.0) 

#Change pop_dict to popParams
pop_dict={'ep':neuron1pop}

chanSTD = {
    'KDr': 0.0397,
    'Kv3': 0.0386,
    'KvS': 0.0743,
    'KvF': 0.0173,
    'BKCa': 0.0238,
    'SKCa': 0.145,
    'HCN1': 0.1225,
    'HCN2': 0.253,
    'Ca': 0.0836,
    'NaF': 0.0635,
    'NaS': 0.115,
}
chanvar={'ep':chanSTD}

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
#if using multiple sets of time tables, these values should sum to 1

dend_location=NamedList('dend_location','mindist=0 maxdist=1 maxprob=None half_dist=None steep=0 postsyn_fraction=None')

#probability for intrinsic is the probability of connecting pre and post.
connect=NamedList('connect','synapse pre post num_conns=2 space_const=None probability=None dend_loc=None stp=None')
ext_connect=NamedList('ext_connect','synapse pre post dend_loc=None stp=None weight=1')

#tables of extrinsic inputs
#first string is name of the table in moose, and 2nd string is name of external file
tt_STN = TableSet('tt_STN', 'ep_net/STN_lognorm',syn_per_tt=2)
#tt_STN = TableSet('tt_STN', 'stptest2tr',syn_per_tt=2)
tt_str = TableSet('tt_str', 'ep_net/SPN_lognorm',syn_per_tt=2)
tt_GPe = TableSet('tt_GPe', 'ep_net/GPe_lognorm',syn_per_tt=2)
#tt_GPe = TableSet('tt_GPe', 'stptest4tr',syn_per_tt=2)

#description of intrinsic inputs
ConnSpaceConst=125e-6
ep_distr=dend_location(mindist=30e-6,maxdist=100e-6,postsyn_fraction=1,half_dist=50e-6,steep=1)
neur1pre_neur1post=connect(synapse='gaba', pre='ep', post='gaba', probability=0.5,dend_loc=ep_distr)#need reference for no internal connections

#description of synapse and dendritic location of extrinsic inputs
GPe_distr=dend_location(mindist=0,maxdist=60e-6,half_dist=30e-6,steep=-1)
str_distr=dend_location(mindist=30e-6,maxdist=1000e-6,postsyn_fraction=1,half_dist=100e-6,steep=1)
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
ext1_neur1post=ext_connect(synapse='ampa',pre=tt_STN,post='ep', dend_loc=STN_distr)# need reference
ext2_neur1post=ext_connect(synapse='gaba',pre=tt_GPe,post='ep', dend_loc=GPe_distr,stp=GPe_plas,weight=2)
ext3_neur1post=ext_connect(synapse='gaba',pre=tt_str,post='ep', dend_loc=str_distr,stp=str_plas)

#Collect all connection information into dictionaries
#1st create one dictionary for each post-synaptic neuron class
ep={}
#connections further organized by synapse type
#the dictionary key for tt must have 'extern' in it
ep['gaba']={'extern2': ext2_neur1post, 'extern3': ext3_neur1post}#, 'ep':neur1pre_neur1post}
ep['ampa']={'extern1': ext1_neur1post}

#Then, collect the post-synaptic dictionaries into a single dictionary.
#for NetPyne correspondance: change connect_dict to connParams
connect_dict={}
connect_dict['ep']=ep

# m/sec - GABA and the Basal Ganglia by Tepper et al
cond_vel=0.8 #conduction velocity
mindelay=1e-3
