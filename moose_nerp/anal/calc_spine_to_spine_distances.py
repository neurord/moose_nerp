# -*- coding: utf-8 -*-
"""
Created on Fri Jun 25 13:11:10 2021

@author: kblackw1
"""
import numpy as np
import moose
from moose_nerp import D1PatchSample5 as model
model.spineYN = True
from moose_nerp.prototypes import (
        create_model_sim,
        cell_proto,
        clocks,
        inject_func,
        create_network,
        tables,
        net_output,
        logutil,
        util,
        standard_options,
        ttables,
        spines,
    )
from moose_nerp.prototypes import spatiotemporalInputMapping as stim
from moose_nerp import str_net as net
net.single = True
total_spines = 200 # Minimum -- note that we round up n spines per cluster
model.SpineParams.ClusteringParams = {}
model.SpineParams.ClusteringParams['n_clusters'] = 20
model.SpineParams.ClusteringParams['cluster_length'] = 200e-6/model.SpineParams.ClusteringParams['n_clusters']# 200 microns divided by number of clusters, fewer clusters --> greater cluster length to distribute within.
model.SpineParams.ClusteringParams['n_spines_per_cluster'] = int(np.ceil(total_spines/model.SpineParams.ClusteringParams['n_clusters']))
create_model_sim.setupOptions(model)
model = create_model_sim.setupNeurons(model, network=not net.single)
ntypes = util.neurontypes(model.param_cond)

import pandas as pd

d1 = ntypes[0]

#calculate distance from soma - but not working
d1.pathDistanceFromSoma

'''Notes on calculating spine to spine distance
loop through every spine in model
for each spine, loop again over every other spine in model
for each pair of spines (from outer and inner loops), find their common parent compartment and compute the distance of each one from the common parent
sum the two distances and append to spine_to_spine_distances table
'''

                
bd = stim.getBranchDict(d1) #dictionary of 39 items - only those branches which receive synaptic input
#dictionary of dictionaries
# for each branch with stimulation input, provide:
# 'BranchPath'(compartments from branch to soma)
# 'MinBranchDistance', 'MaxBranchDistance','BranchOrder', 'CompList','BranchLength', 'CompDistances'
#To determine distance to soma of all spines, need comp_to_branch_dict for all spines

comp_to_branch_dict = stim.mapCompartmentToBranch(d1, bd)
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
            spine_to_spine_dist_array[i,j] = spines.compute_spine_to_spine_dist(spine, other_spine)
        #else:
        #    print(spine.path,other_spine.path,'not found')

spine_dist_df = pd.DataFrame(spine_to_spine_dist_array,columns=[sp.path for sp in allspines],index=[sp.path for sp in allspines])
#spine_dist_df.to_csv('spine_to_spine_dist_D1PatchSample5.csv')
spine_dist_df.to_csv('test.csv')

######## ####### ####### ####### ####### ####### ####### ####### ###### 
####### Use branch_dist to calculate spine distance from soma
########## Add this part to spines, in possible_spine_to_spine_distances?
#### but replace allspines with possible_spines
branch_dist={k:(v['MinBranchDistance']+v['MaxBranchDistance'])/2 for k,v in bd.items()}
spine_to_soma_distance={}
#all_spine_to_soma_distance={}
#### calculate spine to soma distance
#for spine_path,spine_parent_path in allspines_paths:
for spine in allspines: #possible_spines
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

