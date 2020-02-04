from .param_net import (confile,
                        outfile,
                        connect_dict,
                        connect_delete,
                        change_syn,
                        change_weight,
                        change_prob,
                        mindelay,
                        cond_vel,
                        merge_connect)

###########plotting control
#probably put these into param_sim?  similar to that in single neuron sims?
plot_netvm=1
plots_per_neur=1
#number of neurons per neuron type for current injection
#set to np.inf to inject entire population, set to 0 for no injection
num_inject=1
single=False

