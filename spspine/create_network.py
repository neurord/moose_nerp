"""\
Sets up time tables, then connects them after creating population
"""
from __future__ import print_function, division
import moose

from spspine import (#extern_conn,
                     pop_funcs,
                     plasticity,
                     logutil)
log = logutil.Logger()

from spspine import param_net

#Note that the code actually allows different timetabs to D1 and D2, and different D1 and D2 morphology

def CreateNetwork(model, inputelement, spineheads, synarray, MSNsyn, simtime):
    #First, extract number of synapses per compartment for glu and gaba
    _types = model.neurontypes()
    if synarray:
        numglu = {ntype:synarray[ntype][:,param_syn.GLU] for ntype in _types}
        numgaba = {ntype:synarray[ntype][:,param_syn.GABA] for ntype in _types}
    else:
        numglu = {ntype:[] for ntype in _types}
        numgaba = {ntype:[] for ntype in _types}
    log.info('synarray {}', synarray)

    inpath=inputelement.path
    startt=0
    if model.single:
        #Create one of each neuron type, add synaptic inputs
        population=[]
        totaltt=0
        for ntype in _types:
            #First, determine how many synaptic inputs, and whether connection to spine
            if spineheads:
                totaltt += len(spineheads[ntype])
            elif synarray:
                totaltt += synarray[ntype].sum(axis=0)[param_syn.GLU]
        print("totaltt GLU", ntype, totaltt)
        #Second, read in the spike time tables
        timetab=extern_conn.alltables(param_net.infile,inpath,totaltt,simtime)
        #Third, assign the timetables to synapses for each neuron
        for ntype in _types:
            synapses = MSNsyn[ntype] if synarray else {'ampa':[], 'nmda':[]}
            neuronpaths = [neuron[ntype]['cell'].path]
            startt=extern_conn.addinput(model, timetab,synapses,['ampa','nmda'], neuronpaths, numglu[ntype], startt)
    else:
        #Create network of neurons
        population = pop_funcs.create_population(moose.Neutral(param_net.netname), 
                                                 param_net.pop_dict)
        #First, determine how many synaptic inputs (assume not spines for network)
        totaltt=sum(sum(numglu[_types[i]])*len(population['pop'][i]) for i in range(len(population['pop'])))
        print("totaltt GLU", ntype, totaltt)
        #Second, read in the spike time tables
        timetab=extern_conn.alltables(param_net.infile,inpath,totaltt,simtime)
        #Third, assign the timetables to synapses for each neuron, but don't re-use uniq
        for ii,ntype in enumerate(_types):
            startt=extern_conn.addinput(model, timetab,MSNsyn[ntype],['ampa', 'nmda'],population['pop'][ii],numglu[ntype],startt)
        #Fourth, intrinsic connections, from all spikegens to each population
        #Different conn probs between populations is indicated in SpaceConst
        ######### Add FS['spikegen'] to population['spikegen'] once FS added to network
        for ii,ntype in _enumerate(_types):
            connect=pop_funcs.connect_neurons(population['spikegen'],
                                              population['pop'][ii],
                                              MSNsyn[ntype]['gaba'],
                                              param_net.SpaceConst[ntype],
                                              numgaba[ntype],
                                              ntype)

        #Last, save/write out the list of connections and location of each neuron
        locationlist=[]
        for neurlist in population['pop']:
            for jj in range(len(neurlist)):
                neur=moose.element(neurlist[jj]+'/soma')
                neurname = neurlist[jj].split('/')[-1]
                locationlist.append([neurname,neur.x,neur.y])
        savez(param_net.confile,conn=connect,loc=locationlist)

    ##### Synaptic Plasticity, requires calcium
    #### Array of SynPlas has ALL neurons of a single type in one big array.  Might want to change this
    if (model.caltype == 1) and model.plasYN:
        #rolled back code because didn't know how to add loop over nnum (synchronized to ntype) in single line
        SynPlas={}
        if model.single:
            for ntype in _types:
                SynPlas[ntype]=plasticity.addPlasticity(MSNsyn[ntype]['ampa'],
                                                        model.CaPlasticityParams.highThresh,
                                                        model.CaPlasticityParams.lowThresh,
                                                        model.CaPlasticityParams.highfactor,
                                                        model.CaPlasticityParams.lowfactor,
                                                        [])
        else:
            for nnum,ntype in _enumerate(_types):
                SynPlas[ntype]=plasticity.addPlasticity(MSNsyn[ntype]['ampa'],
                                                        model.CaPlasticityParams.highThresh,
                                                        model.CaPlasticityParams.lowThresh,
                                                        model.CaPlasticityParams.highfactor,
                                                        model.CaPlasticityParams.lowfactor,
                                                        population['pop'][nnum])
    else:
        SynPlas=[]
    return population, SynPlas
