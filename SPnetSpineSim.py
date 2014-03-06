######## SPnetSpineSim.py ############
## Code to create SP neuron using dictionaries for channels and synapses
## This allows multiple channels to be added with minimal change to the code
## Can use ghk for calcium permeable channels if ghkYesNo=1
## Optional calcium concentration in compartments (calcium=1)
## Optional synaptic plasticity based on calcium (plasyesno=1)
## Spines are optional (spineYN=1), but not allowed for network
## The graphs won't work for multiple spines per compartment
## Assumes spine head has name 'head', cell body called 'soma',
## nmda channel = 'nmda', MgBlock called 'mgblock', likewise for 'ampa' and 'gaba'
## calcium channels begin with 'Ca' and potassium dependent calcium channels end with 'KCa'.
## Also assumes that single neuron element tree is '/neurtype/compartment', and
## network element tree is '/network/neurtype/compartment'

import sys
sys.path.append('./')
import os
os.environ['NUMPTHREADS'] = '1'
from pylab import *
import numpy as np
import matplotlib.pyplot as plt
from string import *

import moose
from moose import utils

from SPcondParamSpine import *
from SPchanParam import *
from SynParamSpine import *
from CaPlasParam import *
from NetParams import *
execfile('ChanGhkProtoLib.py')
execfile('PlotChannel2.py')
execfile('CaFuncSpine.py')
execfile('makeSpine.py')
execfile('CellProtoSpine.py')
execfile('SynProtoSpine.py')
execfile('ExtConnSpine.py')
execfile('CaPlasFunc.py')
execfile('injectfunc.py')

############ Parameters for simulation control #################
#determines whether to print various statements
printinfo=0
# set single=1 to create a single neuron of each type with synaptic input
single=0
#calcium and plasyesno are originally defined in CaPlasParam.py
calcium=0
plasyesno=0
#can't do plasticity without calcium
if not calcium:
    plasyesno=0
#ghkYesNo and spineYN are originally defined in SPcondparams.py
#note that if ghkYesNo=0, make sure that ghKluge = 1
#Also, if you are creating network (single=0) probably shouldn't create spines
if not single:
    spineYN=0
    #put all the synaptic channels in the dendrite.  Lists in SynParamSpine.py
    DendSynChans=list(set(DendSynChans+SpineSynChans))
    SpineSynChans=[]
#Which parts of the simulation should be shown?
# plotnet=0 plots all comps from single neuron, plotnet=1 plots soma from all neurons
plotnet=1
showgraphs=1
# graphsyn, graphplas indicate whether to plot the synaptic inputs or plasticity functions
graphsyn=0
Synmsg='get_Gk'  # make this get_Ik to plot current
SynLabel='Cond, nS' #make this 'Curr, nA' for current
graphplas=1
#to prevent you from plotting plasticity if not created:
if not plasyesno:
    graphplas=0

#whether to plot the various ion channel activation and inactivation curves
pltchan=0
pltpow=0

#showclocks=1 will show which elements are assigned to which clock
showclocks=0

#simulation time and current injection
simtime = 4.0
curr1=0.01e-9
curr2=0.1e-9
currinc=0.1e-9
delay=0.1
width=0.3
###dt and solver
plotdt = 0.2e-3
simdt = 2.0e-5 #try 2x simdt since using hsolve
hsolve=1

if single:
    title1 = 'single'
else:
    title1 = 'network'
    execfile('PopFuncsSpine.py')


################### Clocks.  Note that there are no default clocks ##########
inited = False
def assign_clocks(model_container_list, dataName, inname, simdt, plotdt,hsolve):
    global inited
   # `inited` is for avoiding double scheduling of the same object
    if not inited:
        print 'SimDt=%g, PlotDt=%g' % (simdt, plotdt)

        moose.setClock(0, simdt)
        moose.setClock(1, simdt)
        moose.setClock(2, simdt)
        moose.setClock(3, simdt)
        moose.setClock(4, simdt)
        moose.setClock(5, simdt)
        moose.setClock(6, plotdt)
        for path in model_container_list:
            print 'Scheduling elements under:', path
            if hsolve:
                print "USING HSOLVE"
                hsolve = moose.HSolve( '%s/hsolve' % (path))
                moose.useClock( 1, '%s/hsolve' % (path), 'process' )
                hsolve.dt=simdt
            moose.useClock(0, '%s/##[ISA=Compartment]' % (path), 'init')
            moose.useClock(1, '%s/##[ISA=Compartment],%s/##[TYPE=CaConc]' % (path,path), 'process')
            moose.useClock(2, '%s/##[TYPE=SynChan],%s/##[TYPE=HHChannel]' % (path,path), 'process')
            moose.useClock(3, '%s/##[TYPE=Func],%s/##[TYPE=MgBlock],%s/##[TYPE=GHK]' % (path,path,path), 'process')
            moose.useClock(4, '%s/##[TYPE=SpikeGen]' % (path), 'process')
        moose.useClock(5, '%s/##[TYPE=TimeTable],/##[TYPE=PulseGen]' % (inname), 'process')
        moose.useClock(6, '%s/##[TYPE=Table]' % (dataName), 'process')
        inited = True
    moose.reinit()

#################################-----------create the model

##create 2 neuron prototypes with synapses and calcium
[MSNsyn,neuron,pathlist,capools,synarray]=neuronclasses(pltchan,pltpow,calcium,1,spineYN,ghkYesNo)

#For synaptic input: extract number of synapses for glu and gaba
numglu=[]
numgaba=[]
for ntype in neurontypes:
    numsynarray=np.array(synarray[ntype])
    skip=np.shape(numsynarray)[1]
    numglu.append(numsynarray.flatten()[GLU:size(numsynarray):skip])
    numgaba.append(numsynarray.flatten()[GABA:size(numsynarray):skip])

##synaptic input: read in tables (create timetab - only as many as needed)
## assign timetables to synapses
indata=moose.Neutral('/input')
inpath=indata.path
networkname='/network'
totaltt=0
if single:
    totaltt=sum(numglu)
    #read in the spike time tables
    timetab=alltables(infile,inpath,totaltt)
    #assign the timetables to synapses for each neuron, but don't re-use uniq
    startt=0
    for ii,ntype in zip(range(len(neurontypes)), neurontypes):
        startt=addinput(timetab,MSNsyn[ntype],['ampa','nmda'],simtime,[neuron[ntype]['cell'].path],numglu[ii],startt)
else:
    #create population
    MSNpop = create_population(moose.Neutral(networkname), neurontypes, netsizeX,netsizeY,spacing)
    totaltt=sum(sum(numglu[i])*len(MSNpop['pop'][i]) for i in range(len(MSNpop['pop'])))
    #read in the spike time tables
    timetab=alltables(infile,inpath,totaltt)
    #assign the timetables to synapses for each neuron, but don't re-use uniq
    #this structure actually allows different timetabs to D1 and D2, and different D1 and D2 morphology
    startt=0
    for ii,ntype in zip(range(len(neurontypes)), neurontypes):
        startt=addinput(timetab,MSNsyn[ntype],['ampa', 'nmda'],simtime,MSNpop['pop'][ii],numglu[ii],startt)
    #intrinsic connections, from all spikegens to each population
    #Different conn probs between populations is indicated in SpaceConst
    ######### Add FS['spikegen'] to MSNpop['spikegen'] once FS added to network
    for ii,ntype in zip(range(len(neurontypes)), neurontypes):
        conn=connect_neurons(MSNpop['spikegen'],MSNpop['pop'][ii],MSNsyn[ntype]['gaba'],SpaceConst[ntype],numgaba[ii],ntype)
    #need to save/write out the list of connections and location of each neuron
    locationlist=[]
    for neurlist in MSNpop['pop']:
        for jj in range(len(neurlist)):
            neur=moose.element(neurlist[jj]+'/soma')
            neurname=neurlist[jj][rfind(neurlist[jj],'/')+1:]
            locationlist.append([neurname,neur.x,neur.y])
    savez(confile,conn=conn,loc=locationlist)

##### Synaptic Plasticity
#### Array of SynPlas has ALL neurons of a single type in one big array.  Might want to change this
#### Don't implement this unless calcium exists
if calcium and plasyesno:
    SynPlas[ntype] = addPlasticity(MSNsyn[ntype]['ampa'],
                                   highThresh, lowThresh, highfactor, lowfactor,
                                   [] if single else MSNpop['pop'][nnum])

#------------------Current Injection
pg=setupinj(delay,width,curr1)

##############--------------output elements
data = moose.Neutral('/data')
spiketab=[]
##spike generators created automatically for network, but not for single
if not single:
    for neur in MSNpop['cells']:
        underscore=find(neur.path,'_')
        spikenum=int(neur.path[underscore+1:])
        ntype=neur.path[underscore-2:underscore]
        sg=moose.element(neur.path+'/soma/spikegen')
        spiketab.append(moose.Table('/data/outspike%d_%s' % (spikenum,ntype)))
        print ntype,spikenum,neur.path,sg.path,spiketab[spikenum].path
        m=moose.connect(sg, 'event', spiketab[spikenum],'spike')
#
if showgraphs:
    execfile('NetgraphSpine.py')
    vmtab,syntab,catab,plastab,plasCumtab,spcatab = graphtables(single,plotnet,graphplas,calcium,spineYN)
#
########## clocks are critical
## these function needs to be tailored for each simulation
## if things are not working, you've probably messed up here.
if single:
    simpath=['/'+neurontype for neurotype in neurontypes]
else:
    simpath=[networkname]
assign_clocks(simpath,'/data', inpath, simdt, plotdt,hsolve)

#Make sure elements have been assigned clocks
tk = moose.element('/clock/tick')
if showclocks:
    for ii in range(3,5):
        print 'Elements on tick ', ii
        for e in tk.neighbours['proc%s' % (ii)]:
            print ' ->', e.path

################### Actually run the simulation
for inj in arange(curr1,curr2,currinc):
    pg.firstLevel = inj
    moose.reinit()
    moose.start(simtime)
    #
    ######Now create the graphs
    if showgraphs:
        graphs(vmtab,syntab,catab,plastab,plasCumtab,spcatab,graphsyn,graphplas,calcium,spineYN)
    plt.show()
    #
###################### Write the spiketable (only for the final sim) to a file
if not single:
    outvmfile='Vm'+outspikefile
    print "SPIKE FILE", outspikefile, "VM FILE", outvmfile
    outspiketab=list()
    outVmtab=list()
    for tabindex in range(len(neurontypes)):
        outspiketab.append([])
        outVmtab.append([])
        for neurname in MSNpop['pop'][tabindex]:
            underscore=find(neurname,'_')
            neurnum=int(neurname[underscore+1:])
            ntype=neurname[underscore-2:underscore]
            print neurname,"is", neurontypes[tabindex],"=",ntype,"num=",neurnum,spiketab[neurnum].path,vmtab[neurnum].path
            outspiketab[tabindex].append(insert(spiketab[neurnum].vec,0, neurnum))
            outVmtab[tabindex].append(insert(vmtab[neurnum].vec,0, neurnum))
    savez(outspikefile,D1=outspiketab[0],D2=outspiketab[1])
    savez(outvmfile,D1=outVmtab[0],D2=outVmtab[1])
