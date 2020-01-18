#param_net.py

from moose_nerp.prototypes.ttables import TableSet
from moose_nerp.prototypes.syn_proto import ShortTermPlasParams,SpikePlasParams
from moose_nerp.prototypes.util import NamedList
from moose_nerp.prototypes.connect import dend_location,connect,ext_connect 

confile='bg_connect'
outfile='bg_out'

###############
#three types of distributions
####################### Connections
even_distr=dend_location(postsyn_fraction=0.5)
proximal_distr= dend_location(mindist=0e-6,maxdist=80e-6,postsyn_fraction=1)
distal_distr=dend_location(mindist=50e-6,maxdist=400e-6,postsyn_fraction=.1)#,half_dist=50e-6,steep=1)

##connections between regions
#Inputs to ep/SNr from Striatum/D1 and GPe/proto
connect_dict={'ep':{'gaba':{}}}
connect_dict['ep']['gaba']['proto']=connect(synapse='gaba', pre='proto', post='ep', probability=0.2)
connect_dict['ep']['gaba']['Lhx6']=connect(synapse='gaba', pre='Lhx6', post='ep', probability=0.2)
connect_dict['ep']['gaba']['D1']=connect(synapse='gaba', pre='D1', post='ep', probability=0.5)

#Inputs from striatum to GPe
connect_dict['Npas']={'gaba':{}}
connect_dict['Npas']['gaba']['D2']=connect(synapse='gaba', pre='D2', post='Npas', probability=0.5)
connect_dict['Lhx6']={'gaba':{}}
connect_dict['Lhx6']['gaba']['D2']=connect(synapse='gaba', pre='D2', post='Lhx6', probability=0.5)
connect_dict['proto']={'gaba':{}}
connect_dict['proto']['gaba']['D2']=connect(synapse='gaba', pre='D2', post='proto', probability=0.5)

#Inputs from GPe back to Striatum
connect_dict['D2']={'gaba':{}}
connect_dict['D2']['gaba']['Npas']=connect(synapse='gaba', pre='Npas', post='D2', probability=0.5)
connect_dict['D1']={'gaba':{}}
connect_dict['D1']['gaba']['Npas']=connect(synapse='gaba', pre='Npas', post='D1', probability=0.5)
connect_dict['FSI']={'gaba':{}}
connect_dict['FSI']['gaba']['Lhx6']=connect(synapse='gaba', pre='Lhx6', post='FSI', probability=0.5)

########## Delete these connections that are defined in the other net_modules
# e.g., extrinsic connections that are now replaced by other network connections
connect_delete={}
connect_delete={'ep':{'gaba':['extern2','extern3']}}
#once STN neurons provided:
#connect_delete['ep']['ampa']='extern'
#connect_delete['proto']={'ampa':'extern'}
#connect_delete['Lhx6']={'ampa':'extern'}
#connect_delete['Npas']={'ampa':'extern'}

mindelay={}
cond_vel={}

 
