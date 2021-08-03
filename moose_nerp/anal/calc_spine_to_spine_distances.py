# -*- coding: utf-8 -*-
"""
Created on Fri Jun 25 13:11:10 2021

@author: kblackw1
"""
import numpy as np
import pandas as pd
import moose
from moose_nerp import D1PatchSample5 as model
from moose_nerp.prototypes import spatiotemporalInputMapping as stim

model.spineYN = True
from moose_nerp.prototypes import create_model_sim as cms

#Create neuron
cms.setupNeurons(model)
d1 = model.neurons['D1'][0]

#calculate distance from soma - but not working
d1.pathDistanceFromSoma

'''Notes on calculating spine to spine distance
loop through every spine in model
for each spine, loop again over every other spine in model
for each pair of spines (from outer and inner loops), find their common parent compartment and compute the distance of each one from the common parent
sum the two distances and append to spine_to_spine_distances table
'''
def compute_spine_to_spine_dist(spine, other_spine,print_info=False):
    '''Compute the path distance along dendritic tree between any two spines'''
    # get parent compartment of spine
    spine_parents = [spine.parent, other_spine.parent]

    # get the branch of the spine_parent
    spine_branches = [comp_to_branch_dict[sp.path] for sp in spine_parents]
    branch_paths = spine_branches[0]['BranchPath'], spine_branches[1]['BranchPath']
    # if on same branch
    if spine_branches[0]==spine_branches[1]:
        # if on same compartment:
        if spine_parents[0]==spine_parents[1]:
            spine_to_spine_dist = np.sqrt((spine.x - other_spine.x)**2 + (spine.y - other_spine.y)**2 + (spine.z - other_spine.z)**2)
        # else if on same branch but not same compartment:
        else:
            compdistances = [bd[sb['Branch']]['CompDistances'] for sb in spine_branches]
            complists = [bd[sb['Branch']]['CompList'] for sb in spine_branches]
            compindexes = [cl.index(spine_parent.path) for cl,spine_parent in zip(complists, spine_parents)]
            comp_to_comp_distance = np.abs(compdistances[0][compindexes[0]] - compdistances[1][compindexes[1]])
            spine_to_spine_dist = comp_to_comp_distance
    # else if on different branches, find common parent branch first
    else:
        for a,b in zip(branch_paths[0], branch_paths[1]):
            #print(a,b)
            if a == b:
                common_parent = a
        common_parent_distance = bd[common_parent]['CompDistances'][0]
        if print_info:
            print('common parent is ', common_parent, 'common_parent_distance is ', common_parent_distance)
        allcompdistances = [bd[sb['Branch']]['CompDistances'] for sb in spine_branches]
        complists = [bd[sb['Branch']]['CompList'] for sb in spine_branches]
        compindexes = [cl.index(spine_parent.path) for cl,spine_parent in zip(complists, spine_parents)]
        compdistances = [allcompdistances[0][compindexes[0]], allcompdistances[1][compindexes[1]]]
        comp_to_comp_distance = (compdistances[0]-common_parent_distance) + (compdistances[1]-common_parent_distance)
        if print_info:
            print('compdistances',compdistances,'comp_to_comp_distance', comp_to_comp_distance)
        spine_to_spine_dist = comp_to_comp_distance
    return spine_to_spine_dist

                
bd = stim.getBranchDict(d1) #dictionary of 39 items - only those branches which receive synaptic input
#dictionary of dictionaries
# for each branch with stimulation input, provide:
# 'BranchPath'(compartments from branch to soma)
# 'MinBranchDistance', 'MaxBranchDistance','BranchOrder', 'CompList','BranchLength', 'CompDistances'
#To determine distance to soma of all spines, need comp_to_branch_dict for all spines

comp_to_branch_dict = stim.mapCompartmentToBranch(d1)
#Similar to bd, but doesn't have distances or lengths

allspines = moose.wildcardFind('/D1/##/#head')
allspines_paths={sp.path:sp.parent.path for sp in allspines}

np.savez('comp_to_branch_dict.npz',bd=bd,comp_to_branch_dict=comp_to_branch_dict,allspines=allspines_paths)
spine = allspines[0]
other_spine = allspines[33]
############# Use function and branch distances to calculate spine to spine distances
spine_to_spine_dist_array = np.zeros((len(allspines), len(allspines)))
for i,spine in enumerate(allspines):
    for j,other_spine in enumerate(allspines):
        if spine.parent.path in comp_to_branch_dict.keys() and other_spine.parent.path in comp_to_branch_dict.keys():
            spine_to_spine_dist_array[i,j] = compute_spine_to_spine_dist(spine, other_spine)
        #else:
        #    print(spine.path,other_spine.path,'not found')

spine_dist_df = pd.DataFrame(spine_to_spine_dist_array,columns=[sp.path for sp in allspines],index=[sp.path for sp in allspines])
#spine_dist_df.to_csv('spine_to_spine_dist_D1PatchSample5.csv')
spine_dist_df.to_csv('test.csv')

######## ####### ####### ####### ####### ####### ####### ####### ###### 
####### Use branch_dist to calculate spine distance from soma
branch_dist={k:(v['MinBranchDistance']+v['MaxBranchDistance'])/2 for k,v in bd.items()}
spine_to_soma_distance={}
#all_spine_to_soma_distance={}
#### calculate spine to soma distance
#for spine_path,spine_parent_path in allspines_paths:
for spine in allspines:
    spine_key=spine.path.replace('[0]','').replace('/','_').replace('D1','').lstrip('_')
    #all_spine_to_soma_distance[spine_key]=spine.pathDistanceFromSoma
    if spine.parent.path in comp_to_branch_dict.keys():
        spine_branch = comp_to_branch_dict[spine.parent.path]
        allcompdistances = bd[spine_branch['Branch']]['CompDistances']
        complist = bd[spine_branch['Branch']]['CompList']
        compindex = complist.index(spine.parent.path)
        spine_to_soma_distance[spine_key]=allcompdistances[compindex]

spine_soma_df=pd.DataFrame.from_dict(spine_to_soma_distance,orient='index',columns=['distance'])
spine_soma_df.to_csv('spine_soma_distance.csv')

print('ready to plot')
#Inspect values with plots
from matplotlib import pyplot as plt
plt.imshow(spine_to_spine_dist_array)
plt.colorbar()

