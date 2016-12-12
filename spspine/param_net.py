#param_net.py
####################### Populations
from spspine.util import NamedList
neur_distr=NamedList('neur_distr', 'neuronname spacing percent')

netname='/striatum'
spacing=25e-6
#0,1,2 refer to x, y and z
grid={}
grid[0]={'xyzmin':0,'xyzmax':50e-6,'inc':spacing}
grid[1]={'xyzmin':0,'xyzmax':50e-6,'inc':spacing}
grid[2]={'xyzmin':0,'xyzmax':0,'inc':0}


#This won't work if the single neuron of these types is not created
D1pop=neur_distr(neuronname='D1', spacing=grid,percent=0.49)
D2pop=neur_distr(neuronname='D2', spacing=grid,percent=0.49)
FSIpop=neur_distr(neuronname='FSI', spacing=grid,percent=0.02)
#pop_dict={'D1':D1pop,'D2': D2pop, 'FSI': FSIpop}
pop_dict={'D1':D1pop,'D2': D2pop}

####################### Connections
connect=NamedList('connect','synapse pre post space_const')
# want to add postsyn_location - specifies e.g. prox vs distal for synapses - but make it optional
# want to add probability - none distant dependent alternative to space_const, and
#fraction_duplicate - referring to external/time table connections

MSNconnSpaceConst=95e-6
FSIconnSpaceConst=200e-6
D1pre_D1post=connect(synapse='gaba', pre='D1', post='D1', space_const=MSNconnSpaceConst)
D1pre_D2post=connect(synapse='gaba', pre='D1', post='D2', space_const=MSNconnSpaceConst)
D2pre_D1post=connect(synapse='gaba', pre='D2', post='D1', space_const=MSNconnSpaceConst)
D2pre_D2post=connect(synapse='gaba', pre='D2', post='D2', space_const=MSNconnSpaceConst)
FSIpre_D1post=connect(synapse='gaba', pre='FSI', post='D1', space_const=FSIconnSpaceConst)
FSIpre_D2post=connect(synapse='gaba', pre='FSI', post='D2', space_const=FSIconnSpaceConst)
FSIpre_FSIpost=connect(synapse='gaba', pre='FSI', post='FSI', space_const=FSIconnSpaceConst)
#glu_D1post=connect(synapse='glu',pre='timetable',post='D1', fraction_duplicate=0.1)
#glu_D2post=connect(synapse='glu',pre='timetable',post='D2', fraction_duplicate=0.1)
#glu_FSI=connect(synapse='glu',pre='timetable',post='FSI', fraction_duplicate=0.2)

#change pre='timetable' for external to specify the file with time tables?  But what if same set of time tables?
#one dictionary for each post-synaptic neuron class
D1={}
D2={}
FSI={}
connect_dict={}
##Collect the above connections into dictionaries organized by post-syn neuron, and synapse type
D1['gaba']={'D1': D1pre_D1post, 'D2': D2pre_D1post}#, 'FSI': FSIpre_D1post}
#D1['glu']={'extern': glu_D1post}
connect_dict['D1']=D1
D2['gaba']={'D1': D1pre_D2post, 'D2': D2pre_D2post}#, 'FSI': FSIpre_D2post}
#D2['glu']={'extern': glu_D2post}
connect_dict['D2']=D2
FSI['gaba']={'FSI': FSIpre_FSIpost}
#FSI['glu']={'extern': glu_FSI}
#connect_dict['FSI']=FSI

# m/sec - GABA and the Basal Ganglia by Tepper et al
cond_vel=0.8
mindelay=1e-3

infile='A4B4jit1ms'
confile='NetConn'+infile
outfile='MSNout'+infile
