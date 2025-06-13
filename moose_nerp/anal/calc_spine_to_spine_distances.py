# -*- coding: utf-8 -*-
"""
Created on Fri Jun 25 13:11:10 2021

@author: kblackw1
"""
import numpy as np
import moose
from moose_nerp.prototypes import (
        create_model_sim,
        util,
        spines,
    )
from moose_nerp.prototypes import spatiotemporalInputMapping as stim
from moose_nerp import str_net as net
import sim_upstate as su

args='single -sim_type BLA_DLS -SPN cells.D1PatchSample4 -num_clustered 10 -spc 4 -spc_subset 2 -num_dispersed 4 -dist_dispers 50e-6 350e-6 -dist_cluster 50e-6 350e-6 -d2c 0 50e-6 -block_naf True -start_cluster 0.1 -end_cluster 0.3'.split()
 #
#args = sys.argv[1:]
clust=False #make true to test clustering and create spine to spine distance file for that.

mod_dict = su.make_mod_dict()
single_epsp_seed = 314

par=su.parsarg(args)
dispersed_seed=clustered_seed=par.seed

sims=su.specify_sims(par.sim_type,clustered_seed,dispersed_seed,single_epsp_seed, par)
model = su.setup_model(par.SPN, mod_dict, block_naf=par.block_naf, spine_parent=par.spine_par) #send in spine_parent

if clust:
    net.single = True
    total_spines = 200 # Minimum -- note that we round up n spines per cluster
    model.spineYN = True
    model.SpineParams.ClusteringParams = {}
    model.SpineParams.ClusteringParams['n_clusters'] = 20
    model.SpineParams.ClusteringParams['cluster_length'] = 200e-6/model.SpineParams.ClusteringParams['n_clusters']# 200 microns divided by number of clusters, fewer clusters --> greater cluster length to distribute within.
    model.SpineParams.ClusteringParams['n_spines_per_cluster'] = int(np.ceil(total_spines/model.SpineParams.ClusteringParams['n_clusters']))

create_model_sim.setupOptions(model)
#model = create_model_sim.setupNeurons(model, network=not net.single)
ntypes = util.neurontypes(model.param_cond)

create_model_sim.setupOptions(model)

create_model_sim.setupNeurons(model)

import pandas as pd

neuron=util.select_neuron(model.neurons['D1'])

#calculate distance from soma - but not working
#d1.pathDistanceFromSoma

'''Notes on calculating spine to spine distance
loop through every spine in model
for each spine, loop again over every other spine in model
for each pair of spines (from outer and inner loops), find their common parent compartment and compute the distance of each one from the common parent
sum the two distances and append to spine_to_spine_distances table
'''
                
bd = stim.getBranchDict(neuron) #dictionary of 39 items - only those branches which receive synaptic input
#dictionary of dictionaries
# for each branch with stimulation input, provide:
# 'BranchPath'(compartments from branch to soma)
# 'MinBranchDistance', 'MaxBranchDistance','BranchOrder', 'CompList','BranchLength', 'CompDistances'
#To determine distance to soma of all spines, need comp_to_branch_dict for all spines

comp_to_branch_dict = stim.mapCompartmentToBranch(neuron, bd)
#Similar to bd, but doesn't have distances or lengths

allspines = moose.wildcardFind('/D1/##/#head')
allspines_info=[{'parentComp':sp.parent,'x':sp.x,'y':sp.y,'z':sp.z,'head_path': sp.path} for sp in allspines]

#np.savez('comp_to_branch_dict.npz',bd=bd,comp_to_branch_dict=comp_to_branch_dict,allspines=allspines_paths)

############# Use function and branch distances to calculate spine to spine distances
spine_to_spine_dist_array=spines.possible_spine_to_spine_distances(model, allspines_info,neuron)
spine_index={ps['head_path']:(ps['x'],ps['y'],ps['z']) for ps in allspines_info}
spine_index[neuron.path+'/'+model.NAME_SOMA]=(0,0,0)

################# Can probably delete all but spine_to_soma_distance ###################33333
################ possibly just spine_key and get distance from last row/col of spine_to_spine_dist_array
spine_to_soma_distance={}
for i,spine in enumerate(allspines_info): 
    spine_key=allspines[i].path.replace('[0]','').replace('/','_').replace('D1','').lstrip('_') 
    spine_to_soma_distance[spine_key]=spine_to_spine_dist_array[i,-1]
spine_dist_df = pd.DataFrame(spine_to_spine_dist_array,columns=spine_index.keys(),
                             index=spine_index.keys())
#spine_dist_df.to_csv('spine_to_spine_dist_D1PatchSample5.csv')
spine_dist_df.to_csv('test.csv') #might not be needed since saving npz file

print('prep for auto file name',model.morph_file, neuron.name)
fname=model.morph_file[neuron.name].split('.p')[0] #container is ntype
np.savez(fname+'_test_s2sdist', s2sd=spine_to_spine_dist_array,index=spine_index) #needed for analysis later.  Probably need to save in different directory

######## ####### ####### ####### ####### ####### ####### ####### ###### 
### may not needed since included in spine_to_spine_distance
spine_soma_df=pd.DataFrame.from_dict(spine_to_soma_distance,orient='index',columns=['distance'])
spine_soma_df.to_csv('spine_soma_distance.csv')

print('ready to plot')
#Inspect values with plots
from matplotlib import pyplot as plt
plt.imshow(spine_to_spine_dist_array)
plt.colorbar()

plt.figure()
plt.scatter(spine_to_spine_dist_array[-1,0:-1],spine_to_soma_distance.values())
plt.show()
