#param_net.py
####################### Populations
from moose_nerp.prototypes.util import NamedList
from moose_nerp.prototypes.ttables import TableSet
from moose_nerp.prototypes import util as _util

neur_distr=NamedList('neur_distr', 'neuronname spacing percent')

netname='/gp'
confile='gp_connect'
outfile='gp_out'

spacing=54e-6 #pv+: 54e-6, npas1+: 60e-6 measured from Fig. 2 Hernandez Parvabinum+ Neurons and Npas1+ Neurons 2015
#0,1,2 refer to x, y and z
grid={}
grid[0]={'xyzmin':0,'xyzmax':100e-6,'inc':spacing}
grid[1]={'xyzmin':0,'xyzmax':100e-6,'inc':spacing}
grid[2]={'xyzmin':0,'xyzmax':0,'inc':0}

#Do not include a neuron type in pop_dict if the proto not created
neuron1pop=neur_distr(neuronname='proto', spacing=grid,percent=0.52) #Hernandez Parvabinum+ Neurons and Npas1+ Neurons 2015
neuron2pop=neur_distr(neuronname='arky', spacing=grid,percent=0.48)
pop_dict={'proto':neuron1pop,'arky': neuron2pop}

chanvarSPN = {
    'KDr': 0.04,
    'KvF': 0.04,
    'KvS': 0.04,
    'Kv3': 0.04,
    'KCNQ': 0.04,
    'NaS': 0.04,
    'NaF': 0.0,
    'Ca': 0.04,
    'HCN1': 0.04,
    'HCN2': 0.04,
    'BKCa': 0.04,
    'SKCa': 0.04,
}
chanvar={'proto':chanvarSPN, 'arky':chanvarSPN}

####################### Connections
connect=NamedList('connect','synapse pre post space_const=None probability=None')
ext_connect=NamedList('ext_connect','synapse pre post postsyn_fraction')
# add post_location to both of these - optionally specify e.g. prox vs distal for synapses

tt_Ctx_SPN = TableSet('CtxSPN', 'Ctx_4x4',syn_per_tt=2)
tt_Thal_SPN = TableSet('ThalSPN', 'Thal_4x4',syn_per_tt=2)

MSNconnSpaceConst=125e-6
##FSIconnSpaceConst=200e-6
neuron1pre_neuron1post=connect(synapse='gaba', pre='proto', post='proto', space_const=MSNconnSpaceConst)
neuron1pre_neuron2post=connect(synapse='gaba', pre='proto', post='arky', space_const=MSNconnSpaceConst)
neuron2pre_neuron1post=connect(synapse='gaba', pre='arky', post='proto', space_const=MSNconnSpaceConst)
neuron2pre_neuron2post=connect(synapse='gaba', pre='arky', post='arky', space_const=MSNconnSpaceConst)
ctx_neuron1post=ext_connect(synapse='ampa',pre=tt_Ctx_SPN,post='proto', postsyn_fraction=0.5)
thal_neuron1post=ext_connect(synapse='ampa',pre=tt_Thal_SPN,post='proto', postsyn_fraction=0.5)
ctx_neuron2post=ext_connect(synapse='ampa',pre=tt_Ctx_SPN,post='arky', postsyn_fraction=0.5)
thal_neuron2post=ext_connect(synapse='ampa',pre=tt_Thal_SPN,post='arky', postsyn_fraction=0.5)

#one dictionary for each post-synaptic neuron class
proto={}
arky={}
connect_dict={}
##Collect the above connections into dictionaries organized by post-syn neuron, and synapse type
proto['gaba']={'proto': neuron1pre_neuron1post, 'arky': neuron2pre_neuron1post}#, 'FSI': FSIpre_D1post}
proto['ampa']={'extern1': ctx_neuron1post, 'extern2': thal_neuron1post}
connect_dict['proto']=proto
arky['gaba']={'arky': neuron1pre_neuron2post, 'arky': neuron2pre_neuron2post}#, 'FSI': FSIpre_D2post}
arky['ampa']={'extern1': ctx_neuron2post, 'extern2': thal_neuron2post}
connect_dict['arky']=arky

# m/sec - GABA and the Basal Ganglia by Tepper et al
cond_vel=0.8
mindelay=1e-3
