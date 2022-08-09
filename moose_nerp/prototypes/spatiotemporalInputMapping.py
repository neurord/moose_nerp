#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jul 18 21:24:35 2018

Ideas for spatiotemporal input mapping.

1. Define number of total inputs and number of inputs per cluster,
   e.g. nInputs = 100 and clusterSize = 5; if clusterSize == 1, then there is
   no clustering and we can randomly apply nInputs. if clusterSize > 1, then
   define number of clusters, numClusters = nInputs/clusterSize, randomly
   determine the center spine/synapse for each cluster, Additionally we need
   a clusterLength parameter, then randomly select clusterSize spines/synapses
   within the clusterLength window around the cluster center.

   Note: Check for overlap of individual spines: don't select a spine if it has
   already been selected. Also, check for overlap of cluster window; if a
   cluster location would cause overlap then re-select.

2. Optionally apply different distributions for randomly selecting things;
   Uniform by default, but also gaussian, or distance-dependent skewed
   distributions to favor proximal vs. distal inputs

3. Optionally define the minimum distance from soma and maximum distance from
   soma for performing any random selection of spines.

4. Define Pools of inputs--one pool can be created with one set of parameters,
   and/or multiple pools can be created.

5. Optionally define number/subset of branches to apply inputs to, and order
   relative to the soma (primary, secondary, tertiary) or terminal. Also,
   optionally define the relationship between multiple branches -- e.g., apply
   to 2 sibling branches, 2 first cousin branches, 2 second cousin branches,

6. Temporal mapping: Per Pool, per spatial cluster, Random, spatial-order
   dependent, e.g. distal to proximal or proximal to distal; mean ISI, or
   give min/max time window and select within window by evenly dividing into
   enough intervals OR randomly selecting from time window, with optional
   distributions.

7. Distributions: Using distance-dependent functions, e.g. linear, sigmoid,
   etc., to weight probability of applying input distally? Order List of
   possible synapses by distance, then randomly select?

8. np.random.choice for selecting from discrete list of spines/synapses

9. Pros/cons of randomly selecting synapses from a list of possible moose
   elements, vs. randomly determining numerical position and then making a
   synapse there? Might be more efficient to determine where synapses should be
   first and then make only those, rather than simulating unnecessary synapses?

@author: dandorman
"""

import numpy as np
import moose_nerp.prototypes.util as util
import moose


def selectRandom(elementList, n=1, replace=False, weight=None, seed = None):
    '''Returns array of n elements selected from elementList.

    weight can be an array-like of same length of element list, should sum to 1.

    Add weight parsing to this function, or create a separate function?
    '''
    selections = np.random.RandomState(seed).choice(elementList, size=n, replace=replace, p=weight)
    return selections


def distanceWeighting(elementList, distanceMapping):
    '''Creates non-uniform, distance-dependent weighted probability.
    distanceMapping should be a callable or a dictionary of {(distanceMin,distanceMax):RelativeWeight}

    The distance mapping can be relative weights as a function of distance,
    and this function will normalize the sum to 1.

    Returns array of weights that can be passed to selectRandom for non-uniform
    distance-dependent selection of inputs
    '''
    weights = []
    for el in elementList:
        w = util.distance_mapping(distanceMapping, el)
        weights.append(w)
    # Normalize weights to sum to 1:
    weights = weights/np.sum(weights)
    return weights


def generateElementList(neuron, wildcardStrings=['ampa,nmda'], elementType='SynChan',
                        minDistance=0, maxDistance=1, commonParentOrder=0,
                        numBranches='all', branchOrder=None,min_length = None, min_path_length = None, max_path_length = None,branch_list = None, exclude_branch_list = None, branch_seed = None, select_seed = None):
    '''Generate list of Moose elements between minDistance and maxDistance from
    soma. if commonParent is None, then all branches considered. If numBranches
    is None, then all branches included. If numBranches is not None, then n branches
    that are of order branchOrder and have a commonParent order returned.
    commonParent can be specified as an int where 1 = primary branch off soma,
    2 = secondary branch, etc. branchOrder can be specified likewise, or with
    negative integers to indicate order from terminal, e.g. -1 means a terminal
    branch, -2 means a parent branch of a terminal branch, etc.

    elementType controls whether to return Moose spines, synapses, or compartments.

    Optional idea: specify numbranches and branchorder as a dict to have
    multiple branches of different orders inclduded, e.g. {branchOrder:numBranches}
    like {-1:2,1:1} would give 2 terminal branches and 1 primary branch

    Examples: Add use cases
    '''
    # 1. Moose wildcard find from neuron using elementType.
    neuron.buildSegmentTree()

    allList = []
    for s in wildcardStrings:
        l = moose.wildcardFind(neuron.path+'/##/#'+s+'#[ISA='+elementType+']')
        allList.extend(l)
    #print(allList)
    if branch_list is None:
        possibleBranches = getBranchesOfOrder(neuron, branchOrder, n=numBranches,
                                          commonParentOrder=commonParentOrder, min_length = min_length, min_path_length = minDistance, max_path_length = maxDistance,seed=branch_seed)
    else:
        possibleBranches = branch_list
    if exclude_branch_list is not None:
        possibleBranches = [b for b in possibleBranches if b not in exclude_branch_list]
    bd = getBranchDict(neuron)
    possibleCompartments = [comp for branch in possibleBranches for comp in bd[branch]['CompList']]
    possible_comp_dists = [d for branch in possibleBranches for d in bd[branch]['CompDistances']]
    elementList = []
    for el in allList:
        # Get Distance of element, or parent compartment if element not compartment
        el = moose.element(el)
        if isinstance(el, (moose.Compartment, moose.ZombieCompartment)):
            dist,name = util.get_dist_name(el)
            path = el
        elif isinstance(moose.element(el.parent),(moose.Compartment,moose.ZombieCompartment)):
            dist,name = util.get_dist_name(moose.element(el.parent))
            path = el.parent
        else:
            print('Invalid Element')
        if any(s in name.lower() for s in ['head'.lower(),'neck'.lower()]):
            dist,name = util.get_dist_name(moose.element(el.parent))
            path = moose.element(path).parent
        #print('#####possible compartments')
        #print(possibleCompartments)
        #print(name, dist, path)
        if path.path in possibleCompartments:
            ind = possibleCompartments.index(path.path)
            dist = possible_comp_dists[ind]
            # print(path, minDistance,dist+path.length/2., maxDistance, dist-path.length/2.)
            if (minDistance <= dist+path.length/2.) and (dist-path.length/2. <= maxDistance):
                elementList.append(el)
    # print(elementList)
    return elementList


def getBranchOrder(compartment):
    '''Return OrderFromSoma of a dendritic compartment.
    Order specified by integer, relative to soma. For a neuron with Primary,
    Secondary, and Tertiary dendrites, a compartment on a primary branch would
    return 1, a secondary branch compartment will return 2, and a tertiary
    branch compartment will return 3.
    '''

    return

def getBranchDict(neuron):
    '''Return a {BranchNameString: {CompList: [CompartmentsInBranchList],
                                    BranchPath: [Soma,Primary,...CurrentBranch],
                                    BranchOrder: IntegerValue,
                                    BranchLength: Float in meters,
                                    Terminal: Bool}
    dictionary for all dendritic compartments of a neuron. BranchNameString
    should be the compartment path string of the first compartment after a
    branch point. Every Moose soma/dend compartment including the first after a
    branchpoint should be in the CompList. BranchPath should be [Soma,...
    currentBranch], e.g. [Soma,Primdend1,Secdend21,]. BranchOrder should be
    an integer value with 0 for soma, 1 for primary branches, 2 for secondary
    branches, etc. Terminal should be a boolean, True if a branch is a terminal
    branch, and False if a branch is not.

    Neuron must be an instance of class Moose.Neuron
    '''
    branchDict={}
    neuron.buildSegmentTree()
    #lastbranchpoint=''
    def recursiveBranch(comp,lastbranchpoint):
        nonlocal branchDict
        children = comp.neighbors['axialOut']
        if not comp.path==lastbranchpoint: # Do this if we are not at the root, soma, compartment
            parentComp = comp.neighbors['handleAxial'][0]
            parentCompChildren = moose.element(parentComp).neighbors['axialOut']
        else: # Do this only the first time for the root soma compartment
            parentCompChildren = children
            lastbranchpoint = [comp.path]
        if len(parentCompChildren)>1: # This is the first compartment of a branch
            if not comp.path==lastbranchpoint[-1]: # Do this for all except soma
                branchDict[comp.path] = {'BranchPath':lastbranchpoint+[comp.path]}
            else: # Do this for Soma
                branchDict[comp.path] = {'BranchPath':[comp.path]}
                branchDict[comp.path]['MinBranchDistance']=0
                branchDict[comp.path]['MaxBranchDistance']=0
            branchDict[comp.path]['BranchOrder']=len(branchDict[comp.path]['BranchPath'])-1
            branchDict[comp.path]['CompList'] = [comp.path]
            branchDict[comp.path]['BranchLength'] = comp.length
            
            #dist,name = util.get_dist_name(comp)
            #branchDict[comp.path]['MinBranchDistance'] = dist-comp.length/2
            # print('last branch point: ', lastbranchpoint)
            #import pdb; pdb.set_trace()
            branchDict[comp.path]['MinBranchDistance'] = branchDict[lastbranchpoint[-1]]['MaxBranchDistance']
            branchDict[comp.path]['MaxBranchDistance'] = branchDict[comp.path]['MinBranchDistance'] + comp.length
            branchDict[comp.path]['CompDistances']=[branchDict[comp.path]['MinBranchDistance'] + comp.length/2.]
                        
            lastbranchpoint = branchDict[comp.path]['BranchPath']
        elif len(parentCompChildren)==1: # This is an additional compartment of lastbranchpoint, just append to comp list
            branchDict[lastbranchpoint[-1]]['CompList'].append(comp.path)
            branchDict[lastbranchpoint[-1]]['BranchLength'] += comp.length
            branchDict[lastbranchpoint[-1]]['CompDistances'].append(branchDict[lastbranchpoint[-1]]['MaxBranchDistance']+comp.length/2.)
            branchDict[lastbranchpoint[-1]]['MaxBranchDistance'] += comp.length
        else:
            print(comp.path,'length of parentCompChildren == 0')

        if len(children)==0: #This is a terminal compartment
            branchDict[lastbranchpoint[-1]]['Terminal'] = True
        else:
            branchDict[lastbranchpoint[-1]]['Terminal'] = False

        for child in children: # Loop recursively through all children compartments
            n = moose.element(child)
            #print(branchDict)
            recursiveBranch(n,lastbranchpoint)
    recursiveBranch(moose.element(neuron.compartments[0]),moose.element(neuron.compartments[0]).path)
    return branchDict


def mapCompartmentToBranch(neuron):
    bd = getBranchDict(neuron)
    compToBranchDict={}
    missing=[]
    for comp in neuron.compartments:
        for k,v in bd.items():
            if comp.path in bd[k]['CompList']:
                compToBranchDict[comp.path]={'Branch':k}
                compToBranchDict[comp.path]['BranchOrder']=bd[k]['BranchOrder']
                compToBranchDict[comp.path]['Terminal']=bd[k]['Terminal']
                compToBranchDict[comp.path]['BranchPath']=bd[k]['BranchPath']
        if comp.path not in bd.keys() and comp.path not in missing:
            #print(comp.path,'not in branchDict keys')
            missing.append(comp.path)
            #compToBranchDict[comp.path]['Distance']
    if len(missing):
        print('these comps not in comp_to_branch_dict',missing)
    return compToBranchDict


def getBranchesOfOrder(neuron,order,n=1,commonParentOrder=0, min_length = None, min_path_length = None, max_path_length = None, seed = None):
    '''Returns n Branches selected without replacement of specified order from
    soma (0=soma, 1=primary branch, etc.). n can be an int, less than the
    total number of branches of specified order, or an error will be raised.
    n can b also be a string='all' to return all branches of specified order.
    if order = -1, then terminal branches are selected, regardless of order from soma.
    If order is None, then branches selected from any order (but with commonParent if
    commonParentOrder not 0).
    '''
    bd = getBranchDict(neuron)
    if commonParentOrder != 0:
        commonParentBranch = getBranchesOfOrder(neuron,commonParentOrder)[0]
    else:
        commonParentBranch = neuron.compartments[0].path
    if order == -1:
        branchesOfOrder = [branch for branch in bd.keys() if bd[branch]['Terminal'] == True and commonParentBranch in bd[branch]['BranchPath']]
    elif order is None:
        branchesOfOrder = [branch for branch in bd.keys() if commonParentBranch in bd[branch]['BranchPath']]
    else:
        branchesOfOrder = [branch for branch in bd.keys() if order == bd[branch]['BranchOrder'] and commonParentBranch in bd[branch]['BranchPath']]
    
    if min_length is not None:
        branchesOfOrder = [branch for branch in branchesOfOrder if bd[branch]['BranchLength'] > min_length]
    
    if min_path_length is not None:
        branchesOfOrder = [branch for branch in branchesOfOrder if bd[branch]['MaxBranchDistance'] >= min_path_length]
    
    if max_path_length is not None:
        branchesOfOrder = [branch for branch in branchesOfOrder if bd[branch]['MinBranchDistance'] <= max_path_length]
    
    if n in ['all','All','ALL']:
        return branchesOfOrder
    else:
        nBranches = np.random.RandomState(seed).choice(branchesOfOrder, size=n, replace=False)
        return nBranches

def temporalMapping(inputList, minTime = 0, maxTime = 0, random = True):
    n = len(inputList)
    for input in inputList:
        input.delay = np.random.uniform(minTime, maxTime)

def createTimeTables(inputList,model,n_per_syn=1,start_time=0.05,freq=500.0, duration_limit = None):
    from moose_nerp.prototypes import connect
    num = len(inputList)
    input_times = []
    for i,input in enumerate(inputList):
        sh = moose.element(input.path+'/SH')
        tt = moose.TimeTable(input.path+'/tt')
        
        times = [start_time+i*1./freq + j*num*1./freq for j in range(n_per_syn)]
        times = np.array(times)
        if duration_limit is not None:
            times = times[times<(start_time+duration_limit)]
        tt.vector = times
        input_times.extend(tt.vector)
        #print(tt.vector)
        connect.synconn(sh.path,False,tt,model.param_syn,mindel=0)
    input_times.sort()
    return input_times

def exampleClusteredDistal(model, nInputs = 5,branch_list = None, seed = None):
    for neuron in model.neurons.values():
        elementlist = generateElementList(neuron[0], wildcardStrings=['ampa,nmda'], elementType='SynChan',
                                minDistance=150e-6, maxDistance=190e-6, commonParentOrder=0,
                                numBranches=1, branchOrder=-1,min_length=20e-6, #max_path_length = 180e-6, min_path_length = 200e-6,
                                branch_list=branch_list,
                                #branch_list = ['/D1[0]/570_3[0]'],
                                #branch_list = ['/D1[0]/138_3[0]'],
                                )
        inputs = selectRandom(elementlist,n=nInputs,seed=seed)
        #print(inputs)
        return inputs

def dispersed(model, nInputs = 100,exclude_branch_list=None, seed = None):
    for neuron in model.neurons.values():
        elementlist = generateElementList(neuron[0], wildcardStrings=['ampa,nmda'], elementType='SynChan',exclude_branch_list=exclude_branch_list)
        inputs = selectRandom(elementlist,n=nInputs,seed=seed)
        return inputs

def test():
    from moose_nerp import D1MatrixSample2 as model
    from moose_nerp.prototypes import create_model_sim as cms 
    model.spineYN = True
    model.calYN = True
    model.synYN = True

    cms.setupAll(model)
    neuron = model.neurons['D1'][0]
    bd = getBranchDict(neuron)
    possibleBranches = getBranchesOfOrder(neuron, -1, n='all',
                                          commonParentOrder=0, min_length = 20e-6, min_path_length = 150e-6, max_path_length = 180e-6)
    
    elist = generateElementList(neuron, wildcardStrings=['ampa,nmda'], elementType='SynChan',
                                minDistance=180e-6, maxDistance=200e-6, commonParentOrder=0,
                                numBranches=1, branchOrder=-1,min_length=20e-6,
                                )
    # elist = generateElementList(neuron, wildcardStrings=['ampa,nmda'], elementType='SynChan',
    #                             minDistance=120e-6, maxDistance=200e-6, commonParentOrder=0,
    #                             numBranches=1, branchOrder=-1,min_length=20e-6,
    #                             )
    
    return elist, possibleBranches

    
def generate_clusters(model,num_clusters = 1, cluster_distance = 20e-6, total_num_spines = 20):
    # Want to distribute total_num_spines into num_clusters of size cluster_distance
    # Generate num_clusters non-overlapping cluster centers on dendritic tree where the dendritic distance from center of 
    # each cluster is cluster_distance
    # Determine dendritic location of each connection 
    # Add explicit spines to each location
    for neuron in model.neurons.values():
        branch_dict = getBranchDict(neuron)
        # randomly choose compartment for potential cluster center
        # We don't want clusters near each other, so choose the parent level that maximally disperses each cluster
        # e.g. if we have 1 cluster, soma is the parent level; if we have 4 primary branches and 4 clusters, each cluster should be within 
        # a different primary branch. if we have 4 primary branches and more than 4 clusters, choose clusters based on secondary branches, etc.
        comp_to_branch_dict = mapCompartmentToBranch(neuron)
        num_branches_per_order = [len(getBranchesOfOrder(neuron,order,'all')) for order in [0,1,2,3]]
        for i,nb in enumerate(num_branches_per_order):
            if num_clusters <= nb:
                cluster_parent_order = i
                break
        for clus in range(num_clusters):
            pass

if __name__ == '__main__':
    from moose_nerp import d1patchsample2 as model
    from moose_nerp.prototypes import create_model_sim
    #model.param_sim.hsolve=False
    model.spineYN = True
    model.calYN = True
    model.synYN = True
    model.SpineParams.explicitSpineDensity=1e6
    model.SpineParams.spineParent = '570_3'
    model.param_syn._SynNMDA.Gbar = 10e-09*1.2
    model.param_syn._SynAMPA.Gbar = 1e-09
    #model.morph_file = 'D1_patch_sample_3.p'
    #for k,v in model.Condset.D1.NaF.items():
    #    model.Condset.D1.NaF[k]=0.0
    model.Condset.D1.NaF[model.param_cond.dist]=0
    #model.Condset.D1.SKCa[model.param_cond.dist]*=.25
    #model.Condset.D1.BKCa[model.param_cond.dist]*=.25
    model.Condset.D1.KaF[model.param_cond.dist]*=.5
    model.Condset.D1.KaS[model.param_cond.dist]*=.25
    model.Condset.D1.Kir[model.param_cond.dist]*=.5
    

    for chan in ['CaL12','CaL13']:
        for k,v in model.Condset.D1[chan].items():
            #model.Condset.D1[chan][k]*=.2
            model.Condset.D1[chan][model.param_cond.dist]*=1
    for chan in ['CaT33']:
        for k,v in model.Condset.D1[chan].items():
            #model.Condset.D1[chan][k]*=10#0.000001#.#1.0e-12
            model.Condset.D1[chan][model.param_cond.dist]*=2

    for chan in ['CaR']:
        for k,v in model.Condset.D1[chan].items():
            model.Condset.D1[chan][k]*=.5#0.01#1.2#1.0e-12
            #model.Condset.D1[chan][model.param_cond.dist]*=1
            
    model.param_syn.SYNAPSE_TYPES.nmda.MgBlock.C=1
    create_model_sim.setupOptions(model)

    create_model_sim.setupNeurons(model)

    create_model_sim.setupOutput(model)

    
    inputs = exampleClusteredDistal(model,nInputs = 15)
    spine_cur_tab = []
    which_spine = inputs[0].parent
    for ch in ['SKCa','CaL13','CaL12','CaR','CaT33','CaT32']:
        chan = moose.element(which_spine.path+'/'+ch)
        tab = moose.Table('data/'+chan.path.replace('/','__').replace('[0]',''))
        moose.connect(tab,'requestOut',chan,'getGk')
        spine_cur_tab.append(tab)
    

    plotgates =['CaR','CaT32','CaT33','CaL12','CaL13']
    model.gatetables = {}
    
    for plotgate in plotgates:
        model.gatetables[plotgate] = {}
        gatepath = which_spine.path+'/'+plotgate
        gate = moose.element(gatepath)
        gatextab=moose.Table('/data/'+plotgate+'_gatex')
        moose.connect(gatextab, 'requestOut', gate, 'getX')
        model.gatetables[plotgate]['gatextab']=gatextab
        gateytab=moose.Table('/data/'+plotgate+'_gatey')
        moose.connect(gateytab, 'requestOut', gate, 'getY')
        model.gatetables[plotgate]['gateytab']=gateytab
        if model.Channels[plotgate][0][2]>0:
            gateztab=moose.Table('/data/'+plotgate+'_gatez')
            moose.connect(gateztab, 'requestOut', gate, 'getZ')
            model.gatetables[plotgate]['gateztab']=gateztab


    #dispersed_inputs = dispersed(model, nInputs = 100)
    createTimeTables(inputs,model,n_per_syn=3)
    #createTimeTables(dispersed_inputs,model,n_per_syn=2,start_time=0.01,freq=100.0)
    #c = moose.element('D1/634_3')
    #c.Rm = c.Rm*100

    moose.reinit()
    moose.start(.4)
    create_model_sim.neuron_graph.graphs(model, model.vmtab, False,.4)
    from matplotlib import pyplot as plt
    plt.ion()
    plt.show()
    plt.figure()
    for i in model.spinevmtab[0]:
        t = np.linspace(0,.4,len(i.vector))
        plt.plot(t,i.vector)

    n = model.neurons['D1'][0]
    d_vs_len = [(p,c.diameter) for c,p in zip(n.compartments,n.geometricalDistanceFromSoma)]
    d_vs_len = np.array(d_vs_len)
    plt.figure()
    plt.scatter(d_vs_len[:,0],d_vs_len[:,1])

    plt.figure()
    
    for cur in spine_cur_tab:
        plt.plot(cur.vector,label=cur.name.strip('_'))
    
    plt.legend()
    create_model_sim.plot_channel.plot_gate_params(moose.element('/library/CaT32'),3)

    
    for c,d in model.gatetables.items():
        plt.figure()
        plt.title(c)
        for g,t in d.items():    
            plt.plot(t.vector,label=g)
        plt.legend()
