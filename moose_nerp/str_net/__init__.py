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
plot_netvm=1
plots_per_neur=2
#number of neurons per neuron type for current injection
#set to np.inf to inject entire population, set to 0 for no injection
num_inject=0
single=True

