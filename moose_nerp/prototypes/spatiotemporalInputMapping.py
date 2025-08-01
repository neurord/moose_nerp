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
import moose
import moose_nerp.prototypes.util as util
from moose_nerp.prototypes.spines import compute_spine_to_spine_dist


def selectRandom(elementList, n=1, replace=False, weight=None, seed = None, func=None):
    '''Returns array of n elements selected from elementList.

    weight can be an array-like of same length of element list, should sum to 1.

    Add weight parsing to this function, or create a separate function?
    '''
    intlist=range(len(elementList))
    print('In selectRandom, func=', func, ', seed=',seed,', num elements',len(elementList))
    if n<=len(intlist):
        selections = np.random.RandomState(seed).choice(intlist, size=n, replace=replace, p=weight)
    else:
        print('selectRandom called from',func,'; unable to choose',n, 'from', len(intlist), 'items!!!')
        selections=np.random.RandomState(seed).choice(intlist, size=len(intlist), replace=replace, p=weight)
    return [elementList[s] for s in selections]


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
                        min_max_dist=[0,1], commonParentOrder=0, exclude_syn=[],
                        numBranches='all', branchOrder=None,min_length = None, branch_list = None, exclude_branch_list = None, branch_seed = None):
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
    #neuron.buildSegmentTree()

    allList = []
    for s in wildcardStrings:
        l = moose.wildcardFind(neuron.path+'/##/#'+s+'#[ISA='+elementType+']')
        allList.extend(l)
    #print('allList', allList)
    bd = getBranchDict(neuron)
    if branch_list is None:
        possibleBranches,_ = getBranchesOfOrder(neuron, branchOrder, bd, n=numBranches,
                                          commonParentOrder=commonParentOrder, min_length = min_length, min_max_path_length = min_max_dist,seed=branch_seed)
    else:
        possibleBranches = branch_list
    #print('********** possibleBranches\n', possibleBranches,'\n exclude',exclude_branch_list)
    if exclude_branch_list is not None:
        possibleBranches = [b for b in possibleBranches if b not in exclude_branch_list]
    comp_to_branch_dict = mapCompartmentToBranch(neuron, bd) 
    possibleCompartments = [comp for branch in possibleBranches for comp in bd[branch]['CompList']]
    possible_comp_dists = {comp:d for branch in possibleBranches for comp,d in zip(bd[branch]['CompList'],bd[branch]['CompDistances'])}
    elementList = [];distances={}
    exclude_info={s.parent.path:{'parentComp':s.parent.parent,'x':s.parent.x,'y':s.parent.y,'z':s.parent.z,'soma_dist':util.get_dist_name(s.parent)[0]} for s in exclude_syn}
    exclude_comps=set([s.parent.parent.path for s in exclude_syn])
    for ex in exclude_comps:
        if ex in possibleCompartments:
            possibleCompartments.remove(ex)
    #print('#####possible compartments\n', possibleCompartments)
    for el in allList:
        # Get Distance of element, or parent compartment if element not compartment
        el = moose.element(el)
        if el.className=='Compartment' or el.className=='ZombieCompartment':
            dist,compname = util.get_dist_name(el)
            comppath = el
        elif moose.element(el.parent).className=='Compartment' or moose.element(el.parent).className=='ZombieCompartment':
            dist,compname = util.get_dist_name(moose.element(el.parent))
            comppath = el.parent #path is either spinehead/neck or the parent compartment
        else:
            print('Invalid Element')
        if any(s in compname.lower() for s in ['head'.lower(),'neck'.lower()]):
            dist,name = util.get_dist_name(moose.element(el.parent))
            path = moose.element(comppath).parent #path needs to be the branch/compartment name
            sp_info={'parentComp':comppath.parent,'x':comppath.x,'y':comppath.y,'z':comppath.z}
        else:
            path=comppath
        #print(name, dist, path)
        if path.path in possibleCompartments:
            #print(comppath.path, dist, 'allowed=',min_max_dist, 'range=',dist+path.length/2., dist-path.length/2.) #Start and end distance of compartment
            if ((min_max_dist[0] <= dist+path.length/2.) and (dist-path.length/2. <= min_max_dist[1])):              
                #or ((minDistance <= dist-path.length/2.) and (dist-path.length/2. <= maxDistance))  \
                #or ((minDistance <= dist) and (dist <= maxDistance)):
                #if dist>min_max_dist[1] or dist<min_max_dist[0]:
                #    print(comppath.path, dist, 'range=',min_max_dist)
                #else:
                    elementList.append(el)
                    #calculate distance from exclude_syn
                    distances[comppath.path]=[]
                    for other_spine in exclude_info.values(): #distance to existing, excluded synapses
                        distances[comppath.path].append(compute_spine_to_spine_dist(sp_info, other_spine,bd,comp_to_branch_dict))
    if len(exclude_info):
        # print(elementList)
        return elementList, distances
    else:
        return elementList, distances


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


def mapCompartmentToBranch(neuron, bd): 
    #bd = getBranchDict(neuron) 
    compToBranchDict={}
    missing=[]
    for comp in neuron.compartments:
        found=False
        for k,v in bd.items():
            if comp.path in bd[k]['CompList']:
                compToBranchDict[comp.path]={'Branch':k}
                compToBranchDict[comp.path]['BranchOrder']=bd[k]['BranchOrder']
                compToBranchDict[comp.path]['Terminal']=bd[k]['Terminal']
                compToBranchDict[comp.path]['BranchPath']=bd[k]['BranchPath']
                found=True
        if comp.path not in bd.keys() and found==False and comp.path not in missing:
            #print(comp.path,'not in branchDict keys')
            missing.append(comp.path)
            #compToBranchDict[comp.path]['Distance']
    if len(missing):
        print('these comps not in comp_to_branch_dict',missing)
    return compToBranchDict


def getBranchesOfOrder(neuron,order,bd,n=1,commonParentOrder=0, min_length = None, min_max_path_length = None, seed = None,commonParentBranch=None):
    '''Returns n Branches selected without replacement of specified order from
    soma (0=soma, 1=primary branch, etc.). n can be an int, less than the
    total number of branches of specified order, or an error will be raised.
    n can b also be a string='all' to return all branches of specified order.
    if order = -1, then terminal branches are selected, regardless of order from soma.
    If order is None, then branches selected from any order (but with commonParent if
    commonParentOrder not 0).
    '''

    if commonParentOrder != 0:
        if not commonParentBranch:
            commonParentBranch = getBranchesOfOrder(neuron,commonParentOrder,bd)[0]
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
    
    if min_max_path_length is not None:
        branchesOfOrder = [branch for branch in branchesOfOrder if bd[branch]['MaxBranchDistance'] >= min_max_path_length[0]]
    
        branchesOfOrder = [branch for branch in branchesOfOrder if bd[branch]['MinBranchDistance'] <= min_max_path_length[1]]

    branch_length= {br: (bd[br]['MinBranchDistance'],bd[br]['MaxBranchDistance']) for br in branchesOfOrder} #use if desaire branches < min path len and/or > max path len
    if n in ['all','All','ALL']:
        return branchesOfOrder, branch_length
    else:
        print('random branch',seed)
        nBranches = np.random.RandomState(seed).choice(branchesOfOrder, size=n, replace=False)
        return nBranches, branch_length

def temporalMapping(inputList, minTime = 0, maxTime = 0, random = True):
    n = len(inputList)
    for input in inputList:
        input.delay = np.random.uniform(minTime, maxTime)

######## Edit this one to use real input trains??  ttables.TableSet.create_all(), randomize_input_trains(net.param_net.tt_Ctx_SPN,ran=randomize)
####### Then, for each input in inputList, randomly select a tt from timetable.stimtab
def createTimeTables(inputList,model,n_per_syn=1,start_time=0.05,freq=500.0, end_time=None, input_spikes=None):
    from moose_nerp.prototypes import connect
    
    input_times = [];ttlist=[]
    if input_spikes is not None:
        #from moose_nerp.prototypes import ttables #move up
        from moose_nerp.prototypes.connect import select_entry
        #tt_Ctx_SPN = ttables.TableSet('CtxSPN', input_spikes['fname'],syn_per_tt=input_spikes['syn_per_tt']) #move up
        #ttables.TableSet.create_all() #move up
        for i,input in enumerate(inputList):
            sh = moose.element(input.path+'/SH')
            tt=select_entry(input_spikes.stimtab) #tt_Ctx_SPN
            if end_time is not None: #limit spikes to duration_limit - only for used tables
                times=tt.vector
                times = times[np.array(times<end_time) & np.array(times>start_time)]
                tt.vector = times        
            #tt=input_spikes.stimtab[i][0] #eliminate randomness here
            connect.synconn(sh.path,False,tt,model.param_syn,mindel=0)
            input_times.extend(tt.vector)
            ttlist.append(tt.path)
            print(tt.vector,'to',input.path)
    else:
        num = len(inputList)
        print('regular input times:')
        for i,input in enumerate(inputList):
            sh = moose.element(input.path+'/SH')
            tt = moose.TimeTable(input.path+'/tt')
            #if end_time:
            #    freq=(num*n_per_syn)/(end_time-start_time) #formula does not reproduce correct input frequency 
            times = np.array([start_time+i*1./freq + j*num*1./freq for j in range(n_per_syn)]) #n_per_syn is number of spikes to each synapse
            if end_time: 
                times = times[times<end_time]
            tt.vector = times
            input_times.extend(tt.vector)
            print('   ',tt.path,tt.vector)
            connect.synconn(sh.path,False,tt,model.param_syn,mindel=0)
            #moose.showmsg(sh)
            ttlist.append(tt)
    input_times.sort()
    return input_times,ttlist

def create_groups(inputs,bd,branch):
    input_comps={}
    for ip in inputs:
        comp=ip.path.split('/sp')[0] ######### This assumes that input is to a spine 
        if int(moose.__version__[0])>3:
            comp=comp[0:-3] #strip off [0]
        if comp in input_comps.keys():
            input_comps[comp]['inputs'].append(ip)
        else:
            bd_index=bd[branch]['CompList'].index(comp)
            dist=bd[branch]['CompDistances'][bd_index]
            input_comps[comp]={'dist':dist, 'inputs':[ip]}
    return input_comps

def exampleClusteredDistal(model, nInputs = 5,branch_list = None, seed = None):#FIXME: will only generate inputs for one neuron
    for neuron in model.neurons.values():
        neur=util.select_neuron(neuron)
        elementlist,_ = generateElementList(neur, wildcardStrings=['ampa,nmda'], elementType='SynChan',
                                min_max_dist=[150e-6, 190e-6], commonParentOrder=0,
                                numBranches=1, branchOrder=-1,min_length=20e-6, 
                                branch_list=branch_list,
                                #branch_list = ['/D1[0]/570_3[0]'],
                                #branch_list = ['/D1[0]/138_3[0]'],
                                )
        inputs = selectRandom(elementlist,n=nInputs,seed=seed,func='ExampleClusteredDistal')
        #print(inputs)
        return inputs

def remove_comps(elementlist, input_per_comp,comps=[]):
    elementDict={}
    remove_el=[]
    for el in elementlist:
        key=el.path.split('/sp')[0] #el.parent.path
        if key in elementDict.keys():
            elementDict[key].append(el)
        else:
            elementDict[key]=[el]
        if key[0:-3] in comps:
            remove_el.append(el) #list of items to remove
    for values in elementDict.values():
        if len(values)<input_per_comp:
            for el in values:
                if el in elementlist:
                    elementlist.remove(el)
    for val in remove_el:
        if val in elementlist:
            elementlist.remove(val)
    return elementlist

def n_inputs_per_comp(model, nInputs = 16,spine_per_comp=1,min_max_dist=[40e-6, 60e-6],branch_list = None, seed = None, branchOrder=None,spc_subset=1):
    #get 1 comp, then call elementlist again with that branch excluded, repeat. 
    #select one spine on that comp for a synapse, then select spine_per_comp-1 other spines
    #possibly exclude the entire 1st order parent? (primary dendrite) or 2nd order parent?  - more complicated
    #only exclude that compartment and not the entire branch?
    schan='ampa'
    elementType='SynChan'
    if spc_subset==spine_per_comp:
        total_inputs=nInputs
    else:
        total_inputs=int((spine_per_comp/spc_subset)*nInputs)
    for neuron in model.neurons.values():
        neur=util.select_neuron(neuron)
        bd=getBranchDict(neur)
        compList=[y for x in bd.values() for y in x['CompList'] ]
        compDist=[y for x in bd.values() for y in x['CompDistances'] ]
        compDistdict={x:y for x,y in zip(compList,compDist)}
        all_inputs=[]
        exclude_branch_list=[]
        input_comps={}
        proximal=0;distal=0;middle=0
        dist_constraint=[m for m in min_max_dist]
        while len(all_inputs)<total_inputs:
            #numBranches,commonParentOrder and branchOrder are ignored if branch_list is specified
            elementlist,_ = generateElementList(neur, wildcardStrings=['ampa,nmda'], elementType='SynChan',
                                    min_max_dist=dist_constraint, commonParentOrder=0,
                                    numBranches='all', branchOrder=branchOrder,#min_length=10e-6, 
                                    branch_list=branch_list#, exclude_branch_list=exclude_branch_list,
                                    )
            elementlist=remove_comps(elementlist, spine_per_comp, input_comps) #remove compartments that have < spine_per_comp or already selected
            if len(elementlist):
                inputs = selectRandom(elementlist,n=1,seed=seed) #select one spine from one compartment, update seed?
                comp=inputs[0].path.split('/sp')[0] ######### This assumes that input is to a spine 
                if int(moose.__version__[0])>3:
                    comp=comp[0:-3] #strip off [0]
                input_comps[comp]={'dist':compDistdict[comp], 'inputs':inputs}
                #keep track of how many distal and how many proximal sets of inputs
                if compDistdict[comp]<100e-6:
                    proximal+=1
                elif compDistdict[comp]>150e-6:
                    distal+=1
                else:
                    middle+=1  
                #kluge: though inputs randomly selected, make sure not too many clusters are proximal or distal
                #don't do this for patch simulations, because dendrites are shorter
                if 'matrix' in model.morph_file[neuron.name]:
                    if proximal>=(nInputs/spine_per_comp)/2 and dist_constraint[0]<100e-6: #if too many proximal inputs, make minDistance larger
                        dist_constraint[0]=100e-6
                    if (proximal+middle)>=(nInputs/spine_per_comp) and dist_constraint[0]<150e-6:
                        dist_constraint[0]=150e-6
                    if distal>4 and dist_constraint[1]>200e-6: #if too many distal inputs, make maxDistance smaller
                        dist_constraint[1]=200e-6
                #
                if spine_per_comp>1:
                    chans = list(moose.wildcardFind(comp+'/##/#'+schan+'#[ISA='+elementType+']')) #select additional spines from same  compartment
                    chans.remove(inputs[0])
                    more_inputs=selectRandom(chans,n=spine_per_comp-1,func='n_inputs_per_comp')
                    inputs=[inp for inp in inputs]+[minp for minp in more_inputs]
                    input_comps[comp]['inputs']=inputs
                for branch, bvalues in bd.items(): #possibly don't do this
                    if comp in bvalues['CompList']:
                        exclude_branch_list.append(branch) #do not select any other inputs from that branch.  UNUSED
            else:
                inputs=[]
                if branch_list:
                    print('********* n_inputs_per_comp: PROBLEM, only',  len(all_inputs), 'inputs with', spine_per_comp,'inputs/comp on', branch_list, 'at distance', min_max_dist)
                    break
                elif branchOrder:
                    print('********* n_inputs_per_comp: PROBLEM, only',  len(all_inputs), 'inputs for branches of order', branchOrder, 'at distance', min_max_dist)
                    print('************ changing branchOrder to None')
                    branchOrder=None
                else:
                    print('***** Even with branchOrder of None, insufficient branches. Number of inputs is', len(all_inputs))
                    break
            all_inputs=[ai for ai in all_inputs] + [inp for inp in inputs]
            print('In n_inputs_per_comp, aiming for',total_inputs,', num inputs=',len(all_inputs))
        return all_inputs, input_comps

def dispersed(model, nInputs = 100,exclude_branch_list=None, seed = None,branch_list=None, min_max_dist=[20e-6, 300e-6], exclude_syn=[],dist_to_cluster=None): #FIXME: will only generate inputs for one neuron
    for neuron in model.neurons.values():
        neur=util.select_neuron(neuron)
        elementlist,sp2sp_distDict = generateElementList(neur, wildcardStrings=['ampa,nmda'], elementType='SynChan',exclude_branch_list=exclude_branch_list,
                                          branch_list=branch_list, min_max_dist=min_max_dist, exclude_syn=exclude_syn)

        if dist_to_cluster is not None:
            if not len(exclude_syn):
                print('Cannot calculate distance to cluster unless cluster specified as exclude_syn')
            minDist={x:min(y) for x,y in sp2sp_distDict.items()}
            maxDist={x:max(y) for x,y in sp2sp_distDict.items()} #unused
            #minDist={k: v for k, v in sorted(minDist.items(), key=lambda item: item[1])}
            #print('closest',np.unique(list(minDist.values()))*1e6)

            #dist_to_clust=[[0, 50e-6],[50e-6, 80e-6],[80e-6, 120e-6],[120e-6, 150e-6 ],[150e-6, 300e-6]] 
            #for dtc in dist_to_clust:
            #    subset=[e for e in elementlist if minDist[e.parent.path]<dtc[1] and minDist[e.parent.path]>dtc[0]]
            #    print('dtc',dtc,'num elements',len(subset))
            subset=[e for e in elementlist if minDist[e.parent.path]<dist_to_cluster[1] and minDist[e.parent.path]>dist_to_cluster[0]]
            print('dispersed inputs, num available=',len(subset), ', using soma dist=', min_max_dist, ',sp2sp dist=',dist_to_cluster)
            num_inputs=min(nInputs,len(subset))
            inputs = selectRandom(subset,n=num_inputs,seed=seed, func='dispersed')
        else:
            num_inputs=min(nInputs,len(elementlist))
            inputs = selectRandom(elementlist,n=num_inputs,seed=seed, func='dispersed')
        if num_inputs<nInputs:
            print('In dispersed, insufficient input elements from', min_max_dist[0],'to',min_max_dist[1],', desired=',nInputs,', achieved=',num_inputs)
        return inputs

def report_element_distance(inputs, print_num=50):
    dist_list=[]
    dist100=0
    dist150=0
    #furthest=(inputs[0],0)
    el_dist=[]
    for i,el in enumerate(inputs):
        if el.className=='Compartment' or el.className=='ZombieCompartment':
            dist,name = util.get_dist_name(el) #this is euclidean distance
            path = el
        elif moose.element(el.parent).className=='Compartment' or moose.element(el.parent).className=='ZombieCompartment':
            dist,name = util.get_dist_name(moose.element(el.parent)) #this is euclidean distance
            path = el.parent
        el_dist.append((el,dist))
        #if dist>furthest[1]:
        #    furthest=(el,dist)
        dist_list.append(dist)
        if dist>100e-6:
            dist100+=1
        if dist>150e-6:
            dist150+=1
        if i < print_num: #don't print out 200 inputs
            print('     ',el.path,name, dist)
        el_dist_sorted=sorted(el_dist,key=lambda x:x[1])
    print('Input Path Distance, mean +/- stdev=', round(np.mean(dist_list)*1e6,2), round(np.std(dist_list)*1e6,2), 'um, count=',len(dist_list),', num>100um=', dist100, ',>150um=', dist150)
    return el_dist_sorted

def generate_clusters(model,num_clusters = 1, cluster_distance = 20e-6, total_num_spines = 20):
    # Want to distribute total_num_spines into num_clusters of size cluster_distance
    # Generate num_clusters non-overlapping cluster centers on dendritic tree where the dendritic distance from center of 
    # each cluster is cluster_distance
    # Determine dendritic location of each connection 
    # Add explicit spines to each location
    for neuron in model.neurons.values():
        bd = getBranchDict(neuron) #not used FIXME
        # randomly choose compartment for potential cluster center
        # We don't want clusters near each other, so choose the parent level that maximally disperses each cluster
        # e.g. if we have 1 cluster, soma is the parent level; if we have 4 primary branches and 4 clusters, each cluster should be within 
        # a different primary branch. if we have 4 primary branches and more than 4 clusters, choose clusters based on secondary branches, etc.
        comp_to_branch_dict = mapCompartmentToBranch(neuron, bd) 
        num_branches_per_order = [len(getBranchesOfOrder(neuron,order,bd, 'all')) for order in [0,1,2,3]]
        for i,nb in enumerate(num_branches_per_order):
            if num_clusters <= nb:
                cluster_parent_order = i
                break
        for clus in range(num_clusters):
            pass

if __name__ == '__main__':
    from moose_nerp import D1MatrixSample2 as model
    from moose_nerp.prototypes import create_model_sim as cms 
    model.spineYN = True
    model.calYN = True
    model.synYN = True
    model.SpineParams.explicitSpineDensity =0.2e6

    cms.setupAll(model)
    neuron=util.select_neuron(model.neurons['D1'])
    bd = getBranchDict(neuron) #NOT USED - just for debugging
    with open('branchDict.txt','w') as fo:
        for br,vals in bd.items():
            fo.write(br+'\n')
            for k,v in vals.items():
                if isinstance(v,list):
                    line=' '.join([str(itm) for itm in v])
                    fo.write('   '+k+':'+line+'\n')
                else:
                    fo.write('   '+k+':'+str(v)+'\n')
    possibleBranches, branch_len = getBranchesOfOrder(neuron, 3, bd, n=1,
                                          commonParentOrder=1, min_length = 10e-6, commonParentBranch='/D1[0]/785_3')
    
    #numBranches,commonParentOrder and branchOrder are ignored if branch_list is specified, in generateElementList and n_inputs_per_comp
    #if only using 1 branch, need a long branch to find enough inputs
    elist,_ = generateElementList(neuron, wildcardStrings=['ampa,nmda'], elementType='SynChan',
                                min_max_dist=[40e-6, 80e-6], commonParentOrder=0,
                                numBranches=1, min_length=120e-6, branch_list=possibleBranches
                                ) #could try minDistance=120e-6'''
    elist_DMS = selectRandom(elist,n=16,func='elist_DMS')
    elist,_ = generateElementList(neuron, wildcardStrings=['ampa,nmda'], elementType='SynChan',
                                min_max_dist=[80e-6, 140e-6], commonParentOrder=0,
                                numBranches=1, min_length=40e-6, branch_list=possibleBranches
                                ) #could try minDistance=120e-6'''
    elist_DLS = selectRandom(elist,n=16,func='elist_DMS')
    elist_DLS,group_DLS=n_inputs_per_comp(model, nInputs = 16,spine_per_comp=2,min_max_dist=[80e-6, 140e-6],branch_list=possibleBranches, seed = None)
    elist_DMS,group_DMS=n_inputs_per_comp(model, nInputs = 16,spine_per_comp=2,min_max_dist=[40e-6, 60e-6], branch_list=possibleBranches, seed = None)
    elist_DMS,group_DMS=n_inputs_per_comp(model, nInputs = 32,spine_per_comp=4,min_max_dist=[40e-6, 60e-6],branch_list = None, seed = None, branchOrder=3)
    elist={'DMS':elist_DMS,'DLS':elist_DLS}
    for k,v in elist.items():
        print('elements and distance for', k)
        report_element_distance(v, print_num=100)

    
 
