from __future__ import print_function, division

from moose_nerp.prototypes import (cell_proto,
                                   calcium,
                                   clocks,
                                   inject_func,
                                   tables,
                                   plasticity_test,
                                   util)

def create_model_sim(model,fname,param_sim,plotcomps):

    #create model
    syn,neurons = cell_proto.neuronclasses(model)

    #If calcium and synapses created, could test plasticity at a single synapse in syncomp
    #Need to debug this since eliminated param_sim.stimtimes
    #See what else needs to be changed in plasticity_test.
    plas = {}
    if model.plasYN:
        plas,stimtab=plasticity_test.plasticity_test(model, param_sim.syncomp, syn, param_sim.stimtimes)

    ###############--------------output elements
    vmtab, catab, plastab, currtab = tables.graphtables(model, neurons,
                                                        param_sim.plot_current,
                                                        param_sim.plot_current_message,
                                                        plas,plotcomps)

    if param_sim.save:
        writer=tables.setup_hdf5_output(model, neurons, filename=fname)
    else:
        writer=None

    ########## clocks are critical. assign_clocks also sets up the hsolver
    simpaths=['/'+neurotype for neurotype in util.neurontypes(model.param_cond)]

    clocks.assign_clocks(simpaths, param_sim.simdt, param_sim.plotdt, param_sim.hsolve,model.param_cond.NAME_SOMA)
    #fix calculation of B parameter in CaConc if using hsolve
    if param_sim.hsolve and model.calYN:
        calcium.fix_calcium(util.neurontypes(model.param_cond), model)

    return syn,neurons,writer,[vmtab, catab, plastab, currtab]
