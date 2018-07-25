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

def selectRandom(elementList, n=1, replace=False, weight=None):
    '''Returns array of n elements selected from elementList.
    
    weight can be an array-like of same length of element list, should sum to 1.
    
    Add weight parsing to this function, or create a separate function?
    '''
    selections = np.random.choice(elementList, size=n, replace=replace, p=weight)
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
                        numBranches='all', branchOrder=None):
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
    print(allList)
    possibleBranches = getBranchesOfOrder(neuron, branchOrder, n=numBranches,
                                          commonParentOrder=commonParentOrder)    
    bd = getBranchDict(neuron)
    possibleCompartments = [comp for branch in possibleBranches for comp in bd[branch]['CompList']]
    elementList = []
    for el in allList:
        # Get Distance of element, or parent compartment if element not compartment
        if isinstance(el, (moose.Compartment, moose.ZombieCompartment)):
            dist,name = util.get_dist_name(el)
        elif isinstance(moose.element(el.parent),(moose.Compartment,moose.ZombieCompartment)):
            dist,name = util.get_dist_name(moose.element(el.parent))
        else:
            print('Invalid Element')
        if (minDistance<dist<maxDistance) and moose.element(name).path in possibleCompartments:
            elementList.append(el)
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
            lastbranchpoint = comp.path
        if len(parentCompChildren)>1: # This is the first compartment of a branch
            if not comp.path==lastbranchpoint: # Do this for all except soma
                branchDict[comp.path] = {'BranchPath':lastbranchpoint+[comp.path]}
            else: # Do this for Soma
                branchDict[comp.path] = {'BranchPath':[comp.path]}
            branchDict[comp.path]['BranchOrder']=len(branchDict[comp.path]['BranchPath'])-1
            branchDict[comp.path]['CompList'] = [comp.path]
            lastbranchpoint = branchDict[comp.path]['BranchPath']
        elif len(parentCompChildren)==1: # This is an additional compartment of lastbranchpoint, just append to comp list
            branchDict[lastbranchpoint[-1]]['CompList'].append(comp.path)

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
    for comp in neuron.compartments:
        for k,v in bd.items():
                if comp.path in bd[k]['CompList']:
                    compToBranchDict[comp.path]={'Branch':k}
                    compToBranchDict[comp.path]['BranchOrder']=bd[k]['BranchOrder']
                    compToBranchDict[comp.path]['Terminal']=bd[k]['Terminal']
                    compToBranchDict[comp.path]['BranchPath']=bd[k]['BranchPath']
    return compToBranchDict    
    
#%%
def getBranchesOfOrder(neuron,order,n=1,commonParentOrder=0):
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
    if n in ['all','All','ALL']:
        return branchesOfOrder
    else:
        nBranches = np.random.choice(branchesOfOrder, size=n, replace=False)
        return nBranches
