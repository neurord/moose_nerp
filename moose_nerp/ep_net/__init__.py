from .param_net import (netname,
                        pop_dict,
                        connect_dict,
                        cond_vel,
                        mindelay,
                        confile,
                        outfile,
                        grid,
                        chanvar)

###########plotting control
#probably put these into param_sim?  similar to that in single neuron sims?
plot_netvm=1
plots_per_neur=1
#number of neurons per neuron type for current injection
#set to np.inf to inject entire population, set to 0 for no injection
num_inject=1
single=True

