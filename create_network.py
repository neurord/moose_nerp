#CreateNetwork.py

"""\
Sets up time tables, then connects them after creating population
"""
from __future__ import print_function, division
import moose
from param_sim import printinfo, simtime
from param_cond import neurontypes
import param_ca_plas as parcal
import param_net as parnet
import plasticity as plas
from param_syn import GLU,GABA

#Debugging not yet finished for these functions
import extern_conn as conn
import pop_funcs as pop
#Note that the code actually allows different timetabs to D1 and D2, and different D1 and D2 morphology


def CreateNetwork(inputpath,calYN,plasYN,single,spineheads,synarray,MSNsyn,neuron):
    #First, extract number of synapses per compartment for glu and gaba
    numglu = {}
    numgaba = {}
    for ntype in neurontypes:
        numglu[ntype] = synarray[ntype][:,GLU] 
        numgaba[ntype] = synarray[ntype][:,GABA]
    if printinfo:
        print("synarray", ntype, synarray[ntype])

    indata=moose.Neutral(inputpath)
    inpath=indata.path
    totaltt=0
    startt=0
    if single:
        #Create one of each neuron type, add synaptic inputs
        MSNpop=[]
        for ntype in neurontypes:
            #First, determine how many synaptic inputs, and whether connection to spine
            totaltt += len(spineheads[ntype]) if len(spineheads) else synarray[ntype].sum(axis=0)[GLU]
            print("totaltt GLU", ntype, totaltt)
        #Second, read in the spike time tables
        timetab=conn.alltables(parnet.infile,inpath,totaltt,simtime)
        #Third, assign the timetables to synapses for each neuron
        for ntype in neurontypes:
            startt=conn.addinput(timetab,MSNsyn[ntype],['ampa','nmda'],[neuron[ntype]['cell'].path],numglu[ntype],startt)
    else:
        #Create network of neurons
        MSNpop = pop.create_population(moose.Neutral(parnet.netname), neurontypes, netsizeX,netsizeY,spacing)
        #First, determine how many synaptic inputs (assume not spines for network)
        totaltt=sum(sum(numglu[neurontypes[i]])*len(MSNpop['pop'][i]) for i in range(len(MSNpop['pop'])))
        print("totaltt GLU", ntype, totaltt)
        #Second, read in the spike time tables
        timetab=conn.alltables(parnet.infile,inpath,totaltt,simtime)
        #Third, assign the timetables to synapses for each neuron, but don't re-use uniq
        for ii,ntype in zip(range(len(neurontypes)), neurontypes):
            startt=conn.addinput(timetab,MSNsyn[ntype],['ampa', 'nmda'],MSNpop['pop'][ii],numglu[ntype],startt)
        #Fourth, intrinsic connections, from all spikegens to each population
        #Different conn probs between populations is indicated in SpaceConst
        ######### Add FS['spikegen'] to MSNpop['spikegen'] once FS added to network
        for ii,ntype in zip(range(len(neurontypes)), neurontypes):
            connect=pop.connect_neurons(MSNpop['spikegen'],MSNpop['pop'][ii],MSNsyn[ntype]['gaba'],parnet.SpaceConst[ntype],numgaba[ntype],ntype)
        
        #Last, save/write out the list of connections and location of each neuron
        locationlist=[]
        for neurlist in MSNpop['pop']:
            for jj in range(len(neurlist)):
                neur=moose.element(neurlist[jj]+'/soma')
                neurname = neurlist[jj].split('/')[neurnameNum]
                locationlist.append([neurname,neur.x,neur.y])
        savez(parnet.confile,conn=connect,loc=locationlist)

    ##### Synaptic Plasticity, requires calcium
    #### Array of SynPlas has ALL neurons of a single type in one big array.  Might want to change this
    if (calYN==1 and plasYN==1):
        #rolled back code because didn't know how to add loop over nnum (synchronized to ntype) in single line
        SynPlas={}
        if (single==1):
            for ntype in neurontypes:
                SynPlas[ntype]=plas.addPlasticity(MSNsyn[ntype]['ampa'],parcal.highThresh,parcal.lowThresh,parcal.highfactor,parcal.lowfactor,[],parcal.caName)
        else:
            for nnum,ntype in zip(range(len(neurontypes)),neurontypes):
                SynPlas[ntype]=plas.addPlasticity(MSNsyn[ntype]['ampa'],parcal.highThresh,parcal.lowThresh,parcal.highfactor,parcal.lowfactor,MSNpop['pop'][nnum],parcal.caName)
    else:
        SynPlas=[]
    return MSNpop, SynPlas
