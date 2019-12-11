#param_net.py

from moose_nerp.prototypes.ttables import TableSet
from moose_nerp.prototypes.syn_proto import ShortTermPlasParams,SpikePlasParams
from moose_nerp.prototypes.util import NamedList

#need to put these Namedlists somewhere in prototypes
from moose_nerp.gp_net.param_net import dend_location, connect

netname='/bg'
confile='bg_connect'
outfile='bg_out'

###############
#three types of distributions
even_distr=dend_location(postsyn_fraction=0.5)
proximal_distr= dend_location(mindist=0e-6,maxdist=80e-6,postsyn_fraction=1)
distal_distr=dend_location(mindist=50e-6,maxdist=400e-6,postsyn_fraction=.1)#,half_dist=50e-6,steep=1)

##connections between regions
connect_dict={'ep':{'gaba':{}}}
connect_dict['ep']['gaba']['proto']=connect(synapse='gaba', pre='proto', post='ep', probability=0.5,dend_loc=proximal_distr)
#use npas for testing only.  Change to lhx6 when those are added to gp_net
connect_dict['ep']['gaba']['Npas']=connect(synapse='gaba', pre='Npas', post='ep', probability=0.5,dend_loc=proximal_distr)

#these are not used because not imported in init and not part of connect_dict
npas_to_FSI_gaba=connect(synapse='gaba', pre='Npas', post='FSI', probability=0.5,dend_loc=proximal_distr)
lhx6_to_D1_gaba=connect(synapse='gaba', pre='Lhx6', post='D1', probability=0.5,dend_loc=proximal_distr)
lhx6_to_D2_gaba=connect(synapse='gaba', pre='Lhx6', post='D2', probability=0.5,dend_loc=proximal_distr)
D2_to_proto_gaba=connect(synapse='gaba', pre='D2', post='proto', probability=0.5,dend_loc=distal_distr)
D2_to_lhx6_gaba=connect(synapse='gaba', pre='D2', post='Lhx6', probability=0.5,dend_loc=distal_distr)
D2_to_npas_gaba=connect(synapse='gaba', pre='D2', post='Npas', probability=0.5,dend_loc=distal_distr)


############## All of these inputs get created
#tables of extrinsic inputs from gp_net
#first string is name of the table in moose, and 2nd string is name of external file
tt_STN = TableSet('tt_STN', 'gp_net/STN2000_lognorm_freq18.0',syn_per_tt=2)
#tt_Str_SPN = TableSet('tt_Str', 'Thal_4x4',syn_per_tt=2)

#tables of extrinsic inputs from ep_net
TWO_STR_INPUTS=0 #Change value to 1 to add second set of striatal time tables
tt_STN = TableSet('tt_STN', 'ep_net/STN_InhomPoisson_freq18_osc0.6',syn_per_tt=2)
tt_str = TableSet('tt_str', 'ep_net/str_InhomPoisson_freq4.0_osc0.2',syn_per_tt=2)
tt_GPe = TableSet('tt_GPe', 'ep_net/GPe_InhomPoisson_freq29.3_osc2.0',syn_per_tt=2)
if TWO_STR_INPUTS:
    tt_str2 = TableSet('tt_str2', 'ep_net/str_InhomPoisson_freq4.0_osc0.2',syn_per_tt=2)

