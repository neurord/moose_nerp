#      between versus within neuron correlation?
#1. refine select_branch to make use of location dependence and allow multiple connections per neuron
#2. refine NamedLists for connections to specify post-syn location dependence (optional)
#3. refine count_presyn to account for a. non-dist dependence, and multiple connections per neuron with location dependence
#                                      b. 3D arrays of elements
#4. Refine count_total_tt to allow for a. multiple sets of tt providing input
#                                      b. two neur_types sharing a set of tt
#5. Allow neurons to have both intrinsic (pre-cell) and extern (timetable) inputs of same syntype

#alternative to extern_input, used in addinput:
# a. create list of all post-syn neurons
# b. loop over all timetables, select conn_per_tt out of the post-syn neurons without replacement
# c. for each neuron selected, randomly select a compartment
# disadvantage: can't create table of compartments for one neuron at a time, and different than other connection types.  

#What multiple time tables:
#ensure that ctx_tt + thal_tt is sufficient for D1post popoulation
#    Also ensure that ctx_tt is sufficient for both D1post and D2post
#    To deal with this, need to specify what proportion of inputs are ctx vs thal, OR give range of compartments for ctx vs thal and syn per comp
#    Or probability of connect.
    

#expand external connections to include post-syn location and percent  

#for single neuron, need to know how many trains connected to each synapse, which needs to be added to param_net
#also need to know within neuron correlation

