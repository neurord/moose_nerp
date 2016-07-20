"""\
Sets up time tables, then connects them after creating population
"""
from __future__ import print_function, division
import moose
from param_sim import printinfo, simtime
from param_cond import neurontypes
import param_ca_plas as parcal
import param_net
import plasticity as plas
from param_syn import GLU,GABA
from spspine import extern_conn

#Debugging not yet finished for these functions
import pop_funcs as pop
#Note that the code actually allows different timetabs to D1 and D2, and different D1 and D2 morphology


def CreateNetwork(inputpath,calYN,plasYN,single,spineheads,synarray,MSNsyn,neuron):
    #First, extract number of synapses per compartment for glu and gaba
    if synarray:
        numglu = {ntype:synarray[ntype][:,GLU] for ntype in neurontypes}
        numgaba = {ntype:synarray[ntype][:,GABA] for ntype in neurontypes}
    else:
        numglu = {ntype:[] for ntype in neurontypes}
        numgaba = {ntype:[] for ntype in neurontypes}
    if printinfo:
        print("synarray", synarray)

    indata=moose.Neutral(inputpath)
    inpath=indata.path
    startt=0
    if single:
        #Create one of each neuron type, add synaptic inputs
        MSNpop=[]
        totaltt=0
        for ntype in neurontypes:
            #First, determine how many synaptic inputs, and whether connection to spine
            if spineheads:
                totaltt += len(spineheads[ntype])
            elif synarray:
                totaltt += synarray[ntype].sum(axis=0)[GLU]
        print("totaltt GLU", ntype, totaltt)
        #Second, read in the spike time tables
        timetab=extern_conn.alltables(param_net.infile,inpath,totaltt,simtime)
        #Third, assign the timetables to synapses for each neuron
        for ntype in neurontypes:
            synapses = MSNsyn[ntype] if synarray else {'ampa':[], 'nmda':[]}
            neuronpaths = [neuron[ntype]['cell'].path]
            startt=extern_conn.addinput(timetab,synapses,['ampa','nmda'], neuronpaths, numglu[ntype], startt)
    else:
        #Create network of neurons
        MSNpop = pop.create_population(moose.Neutral(param_net.netname), neurontypes,
                                       param_net.netsizeX, param_net.netsizeY,
                                       param_net.spacing)
        #First, determine how many synaptic inputs (assume not spines for network)
        totaltt=sum(sum(numglu[neurontypes[i]])*len(MSNpop['pop'][i]) for i in range(len(MSNpop['pop'])))
        print("totaltt GLU", ntype, totaltt)
        #Second, read in the spike time tables
        timetab=extern_conn.alltables(param_net.infile,inpath,totaltt,simtime)
        #Third, assign the timetables to synapses for each neuron, but don't re-use uniq
        for ii,ntype in zip(range(len(neurontypes)), neurontypes):
            startt=extern_conn.addinput(timetab,MSNsyn[ntype],['ampa', 'nmda'],MSNpop['pop'][ii],numglu[ntype],startt)
        #Fourth, intrinsic connections, from all spikegens to each population
        #Different conn probs between populations is indicated in SpaceConst
        ######### Add FS['spikegen'] to MSNpop['spikegen'] once FS added to network
        for ii,ntype in zip(range(len(neurontypes)), neurontypes):
            connect=pop.connect_neurons(MSNpop['spikegen'],MSNpop['pop'][ii],MSNsyn[ntype]['gaba'],param_net.SpaceConst[ntype],numgaba[ntype],ntype)
        
        #Last, save/write out the list of connections and location of each neuron
        locationlist=[]
        for neurlist in MSNpop['pop']:
            for jj in range(len(neurlist)):
                neur=moose.element(neurlist[jj]+'/soma')
                neurname = neurlist[jj].split('/')[neurnameNum]
                locationlist.append([neurname,neur.x,neur.y])
        savez(param_net.confile,conn=connect,loc=locationlist)

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
