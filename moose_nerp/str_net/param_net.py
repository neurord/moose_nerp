#param_net.py
####################### Populations
from moose_nerp.prototypes.util import NamedList
from moose_nerp.prototypes.ttables import TableSet
from moose_nerp.prototypes import util as _util

neur_distr=NamedList('neur_distr', 'neuronname spacing percent')

netname='/striatum'
confile='striatum_connect'
outfile='striatum_out'

spacing=25e-6
#0,1,2 refer to x, y and z
grid={}
grid[0]={'xyzmin':0,'xyzmax':100e-6,'inc':spacing}
grid[1]={'xyzmin':0,'xyzmax':100e-6,'inc':spacing}
grid[2]={'xyzmin':0,'xyzmax':0,'inc':0}

#Do not include a neuron type in pop_dict if the proto not created
D1pop=neur_distr(neuronname='D1', spacing=grid,percent=0.49)
D2pop=neur_distr(neuronname='D2', spacing=grid,percent=0.49)
FSIpop=neur_distr(neuronname='FSI', spacing=grid,percent=0.02)
pop_dict={
          'D1':D1pop,
          #'D2': D2pop,
          #'FSI': FSIpop,
          }

chanvarSPN = {
    'Krp': 0.04,
    'KaF': 0.04,
    'KaS': 0.04,
    'Kir': 0.04,
    'CaL13': 0.04,
    'CaL12': 0.04,
    'CaR': 0.04,
    'CaN': 0.04,
    'CaT': 0.04,
    'NaF': 0.0,
    'BKCa': 0.04,
    'SKCa': 0.04,
}
chanvar={
         'D1':chanvarSPN,
         #'D2':chanvarSPN,
        }

####################### Connections
dend_location=NamedList('dend_location','mindist=0 maxdist=1 maxprob=None half_dist=None steep=0 postsyn_fraction=None')
connect=NamedList('connect','synapse pre post num_conns=2 space_const=None probability=None dend_loc=None stp=None')
ext_connect=NamedList('ext_connect','synapse pre post dend_loc=None stp=None')

# add post_location to both of these - optionally specify e.g. prox vs distal for synapses

#list of time tables that provide extrinsic connections.  Each tt connected to syn_per_tt synapses
tt_Ctx_SPN = TableSet('CtxSPN', 'FullTrialHigherVariability',syn_per_tt=2)
#tt_Thal_SPN = TableSet('ThalSPN', 'Thal_4x4',syn_per_tt=2)
tt_FSI_SPN = TableSet('FSISPN','FSITrains_n-30_f-11-Hz_tmax-25-s_corr-0',syn_per_tt=8)
tt_LTSI_SPN = TableSet('LTSISPN','LTSITrains_n-100_f-8-Hz_tmax-25-s_corr-0',syn_per_tt=2)


distr=dend_location(mindist=0e-6,maxdist=400e-6,postsyn_fraction=.1)#,half_dist=50e-6,steep=1)
FSI_distr = dend_location(mindist=0e-6,maxdist=80e-6,postsyn_fraction=1)
LTSI_distr = dend_location(mindist=80e-6,maxdist=400e-6,postsyn_fraction=.25)

MSNconnSpaceConst=125e-6
FSIconnSpaceConst=200e-6
#connectins between network neurons (intrinsic connections)
D1pre_D1post=connect(synapse='gaba', pre='D1', post='D1', space_const=MSNconnSpaceConst)
D1pre_D2post=connect(synapse='gaba', pre='D1', post='D2', space_const=MSNconnSpaceConst)
D2pre_D1post=connect(synapse='gaba', pre='D2', post='D1', space_const=MSNconnSpaceConst)
D2pre_D2post=connect(synapse='gaba', pre='D2', post='D2', space_const=MSNconnSpaceConst)
FSIpre_D1post=connect(synapse='gaba', pre='FSI', post='D1', space_const=FSIconnSpaceConst)
FSIpre_D2post=connect(synapse='gaba', pre='FSI', post='D2', space_const=FSIconnSpaceConst)
FSIpre_FSIpost=connect(synapse='gaba', pre='FSI', post='FSI', space_const=FSIconnSpaceConst)
#time table input (extrinsic connections)
ctx_D1post=ext_connect(synapse='ampa',pre=tt_Ctx_SPN,post='D1', dend_loc = distr)
#thal_D1post=ext_connect(synapse='ampa',pre=tt_Thal_SPN,post='D1', dend_loc = distr)
ctx_D2post=ext_connect(synapse='ampa',pre=tt_Ctx_SPN,post='D2', dend_loc = distr)
#thal_D2post=ext_connect(synapse='ampa',pre=tt_Thal_SPN,post='D2', dend_loc = distr)
#glu_FSI=connect(synapse='ampa',pre='timetable',post='FSI',)
FSIextern_D1post = ext_connect(synapse='gaba', pre=tt_FSI_SPN, post='D1', dend_loc = FSI_distr)
FSIextern_D2post = ext_connect(synapse='gaba', pre=tt_FSI_SPN, post='D2', dend_loc = FSI_distr)

LTSIextern_D1post = ext_connect(synapse='gaba', pre=tt_LTSI_SPN, post='D1', dend_loc = LTSI_distr)
LTSIextern_D2post = ext_connect(synapse='gaba', pre=tt_LTSI_SPN, post='D2', dend_loc = LTSI_distr)



#one dictionary for each post-synaptic neuron class
D1={}
D2={}
FSI={}
connect_dict={}
##Collect the above connections into dictionaries organized by post-syn neuron, and synapse type
#D1['gaba']={'D1': D1pre_D1post, 'D2': D2pre_D1post}#, 'FSI': FSIpre_D1post}
D1['ampa'] = {
              'extern1': ctx_D1post,
              #'extern2': thal_D1post
             }
D1['gaba'] = {
              'FSIextern': FSIextern_D1post,
              'LTSIextern': LTSIextern_D1post,
             }

connect_dict['D1']=D1
#D2['gaba']={'D1': D1pre_D2post, 'D2': D2pre_D2post}#, 'FSI': FSIpre_D2post}
#D2['ampa']={'extern1': ctx_D2post, 'extern2': thal_D2post}
#connect_dict['D2']=D2
#FSI['gaba']={'FSI': FSIpre_FSIpost}
#FSI['ampa']={'extern': glu_FSI}
#connect_dict['FSI']=FSI

# m/sec - GABA and the Basal Ganglia by Tepper et al
cond_vel=0.8
mindelay=0e-3
