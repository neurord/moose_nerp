# -*- coding:utf-8 -*-
from __future__ import print_function, division
import numpy as np
import matplotlib.pyplot as plt
from pprint import pprint
import moose
import logging
import inspect


from moose_nerp.prototypes import (cell_proto,
                                   calcium,
                                   clocks,
                                   inject_func,
                                   tables,
                                   plasticity_test,
                                   logutil,
                                   util,
                                   standard_options,
                                   constants,
                                   print_params)
from moose_nerp.graph import plot_channel, neuron_graph, spine_graph

def setupLogging(model, level = logging.INFO):
    ### logging.basicConfig(level=level) ### basicConfig only works in __main__
    logging.getLogger().setLevel(level) # Setting this works outside of __main__
    model.log = logutil.Logger()
    return model.log

def setupOptions(model, **kwargs):
    '''Can be called with no arguments except model. This will use the defaults
    in standard_options.standard_options() and apply no param_sim overrides.
    Can pass any keyword arguments that specify fname, plotcomps, logging_level,
    defaults for standard_options.standard_options(), and param_sim overrides.

    Automatically detects possible kwargs in standard_options, so any default
    added to standard_options or any argument added to standard_options can be
    used without modifying this function.

    Current possible kwargs:
    ### Insert list

    Function logic: This function handles kwargs successively; when a kwarg
    meets a criteria, it is popped from kwargs. At the end of the function,
    kwargs should be empy; if anything is left in kwargs, then a meaningless
    kwarg was passed and a warning is raised.

    After the function definition, an attribute setupOptions.hasBeenCalled is
    initialized to False. When the function is called, this gets set to True.
    '''
    # Warn if overwriting prior setupOptions
    if setupOptions.hasBeenCalled is True:
        model.log.warning('''setupOptions has already been called. Overwriting
                          prior call with new options''')

    # Setup logging level if passed in kwargs, else set to a default level
    if 'logging_level' in kwargs.keys():
        log = setupLogging(model,level = kwargs.pop('logging_level'))
    else: log = setupLogging(model)

    # Assign plotcomps if in kwargs, else set to a default.
    if "plotcomps" in kwargs.keys():
        plotcomps = kwargs.pop("plotcomps")
    else: plotcomps = [model.NAME_SOMA]

    ######### Parse default arguments in standard_options.standard_options();
    ######### check if any kwargs match, and assign new default values if so.
    # Get the possible default arguments in standard_options:
    standard_options_argnames = (standard_options.standard_options.__code__.
                                 co_varnames)
    # Find set of all kwargs that are also standard_options_argnames:
    standard_options_default_overrides = set(set(kwargs.keys())
                                             & set(standard_options_argnames))
    #create dictionary for standard options overrides and pop item from kwargs
    standard_options_dict = dict([ (k, kwargs.pop(k)) for k in
                                          standard_options_default_overrides])
    # Now call standard_options, passing any default overrides
    option_parser = standard_options.standard_options(**standard_options_dict)

    ######### Now we must first call option_parser.parse_args(), and then can
    ######### apply any kwargs that are param_sim overrides.
    param_sim = option_parser.parse_args()
    # Find set of all kwargs that match param_sim variables
    param_sim_overrides = set(set(kwargs.keys()) & set(vars(param_sim).keys()))
    # Override each param_sim parameter in kwargs and pop item from kwargs
    for k in param_sim_overrides:
        setattr(param_sim, k, kwargs.pop(k))
    # Pass param_sim to overrides and return model, plotcomps, and param_sim
    model, plotcomps, param_sim = standard_options.overrides(param_sim, model,
                                                             plotcomps)

    ######### Any additional kwarg handling for kwargs not in param_sim or
    ######### standard_options can be added here:
    # Optionally pass 'fname' in kwargs, else set default:
    if 'fname' in kwargs.keys():
        fname = kwargs.pop('fname')
    else:
        fname = (model.param_stim.Stimulation.Paradigm.name + '_' +
                 model.param_stim.location.stim_dendrites[0])

    ######### Add any new code here to parse additional possible kwargs.
    ######### Be sure to pop any parsed kwarg from kwargs dictionary.

    ######### Now kwargs should be empty, if not we passed an invalid kwarg
    if len(kwargs) > 0:
        log.warning("Passed invalid keyword arguments {} to setupOptions",
                    kwargs)
    ######### Append these variables as fields to model namespace to simplify
    ######### passing and returning. No need to return anything because this
    ######### function takes model as pass by reference; and everything modified
    ######### and needed outside this function is done to model namespace.
    model.plotcomps = plotcomps
    model.param_sim = param_sim
    model.fname = fname
    # Set hasBeenCalled flag to True
    setupOptions.hasBeenCalled = True
    return #model, plotcomps, param_sim, fname
# Must be initialized here after function definition, intializes to False;
#   toggled to True within function call:
setupOptions.hasBeenCalled = False


def setupNeurons(model, forceSetupOptions=True, **kwargs):
    '''Creates neuron(s) defined by model. forceSetupOptions=True by default
    will ensure that setupOptions is called before setupNeurons, but if a user
    passes forceSetupOptions = False, neurons can be created whether options
    setup or not--Could be useful for inspecting default model. kwargs are
    simply passed to setupOptions.
    '''
    if forceSetupOptions is True and setupOptions.hasBeenCalled is False:
        setupOptions(model, **kwargs)

    # build neurons and specify returns to model namespace
    model.syn, model.neurons = cell_proto.neuronclasses(model)
    if forceSetupOptions is False: # Only build neuron and return.
        return
    param_sim = model.param_sim
    # If calcium and synapses created, could test plasticity at a single synapse
    # in syncomp. Need to debug this since eliminated param_sim.stimtimes. See
    # what else needs to be changed in plasticity_test.
    model.plas = {}
    if model.plasYN:
        model.plas, model.stimtab = plasticity_test.plasticity_test(model,
                                                    param_sim.syncomp,
                                                    model.syn,
                                                    param_sim.stimtimes)

    ########## clocks are critical. assign_clocks also sets up the hsolver
    simpaths=['/'+neurotype for neurotype in util.neurontypes(model.param_cond)]
    clocks.assign_clocks(simpaths, param_sim.simdt, param_sim.plotdt,
                         param_sim.hsolve, model.param_cond.NAME_SOMA)
    # Fix calculation of B parameter in CaConc if using hsolve
    if model.param_sim.hsolve and model.calYN:
        calcium.fix_calcium(util.neurontypes(model.param_cond), model)

    setupNeurons.hasBeenCalled = True
    return model
setupNeurons.hasBeenCalled = False

def setupStim(model,**kwargs):
    '''Setup the stimulation pulse generator. This function requires that the
    neurons have already been setup, and so if they haven't it first calls
    setupNeurons(), passing any kwargs '''
    if setupNeurons.hasBeenCalled is False:
        setupNeurons(model, forceSetupOptions=True, **kwargs)
    neuron_paths = {ntype:[neur.path] for ntype, neur in model.neurons.items()}
    pg, param_sim = inject_func.setup_stim(model, model.param_sim, neuron_paths)
    model.pg, model.param_sim = pg, param_sim
    return model

def setupOutput(model, **kwargs):
    if setupNeurons.hasBeenCalled is False:
        setupNeurons(model, forceSetupOptions=True, **kwargs)
    ###############--------------output elements
    (vmtab,
     catab,
     plastab,
     currtab) = tables.graphtables(model, model.neurons,
                                   model.param_sim.plot_current,
                                   model.param_sim.plot_current_message,
                                   model.plas,
                                   model.plotcomps)

    if model.param_sim.save:
        writer=tables.setup_hdf5_output(model, model.neurons,
                                        filename=model.fname,
                                        compartments=model.plotcomps)
    else:
        writer=None
    model.writer = writer
    # Add tables to model namespace to simplify passing/returning
    model.vmtab = vmtab
    model.catab = catab
    model.plastab = plastab
    model.currtab = currtab

    if model.log.logger.getEffectiveLevel() == logging.DEBUG:
        for neur in model.neurons.keys():
            print_params.print_elem_params(model, neur, model.param_sim)

    if model.param_sim.plot_channels:
        for chan in model.Channels.keys():
            libchan = moose.element('/library/'+chan)
            plot_channel.plot_gate_params(libchan,
                                          model.param_sim.plot_activation,
                                          model.VMIN, model.VMAX,
                                          model.CAMIN, model.CAMAX)

    if model.spineYN:
        model.spinecatab, model.spinevmtab = tables.spinetabs(model,
                                                              model.neurons,
                                                              model.plotcomps)
    else:
        model.spinevmtab = []
    return


def runOneSim(model, simtime=None, injection_current=None):
    if model.param_stim.Stimulation.Paradigm.name == 'inject':
        print(u'◢◤◢◤◢◤◢◤ injection_current = {} ◢◤◢◤◢◤◢◤'.format(injection_current))
        model.pg.firstLevel = injection_current
    if simtime is None: simtime = model.param_sim.simtime
    moose.reinit()
    moose.start(simtime)


def runAll(model):
    plt.ion()
    traces, names, catraces = [], [], []
    for inj in model.param_sim.injection_current:
        runOneSim(model, simtime=model.param_sim.simtime, injection_current=inj)
        if model.param_sim.plot_vm:
            neuron_graph.graphs(model, model.vmtab, model.param_sim.plot_current,
                                model.param_sim.simtime, model.currtab,
                                model.param_sim.plot_current_label,
                                model.catab, model.plastab)

        #set up tables that accumulate soma traces for multiple simulations
        for neurnum,neurtype in enumerate(util.neurontypes(model.param_cond)):
            traces.append(model.vmtab[neurnum][0].vector)
            if model.calYN and model.param_sim.plot_calcium:
                catraces.append(model.catab[neurnum][0].vector)
            names.append('{} @ {}'.format(neurtype, inj))
            # In Python3.6, the following syntax works:
            #names.append(f'{neurtype} @ {inj}')
        #plot spines
        if len(model.spinevmtab) and model.param_sim.plot_vm:
            spine_graph.spineFig(model, model.spinecatab, model.spinevmtab,
                                 model.param_sim.simtime)
        #save output - expand this to optionally save current data
        if model.param_sim.save:
            inj_nA=inj*1e9
            tables.write_textfile(model.vmtab, 'Vm', model.fname, inj_nA,
                                  model.param_sim.simtime)
            if model.calYN:
                tables.write_textfile(model.catab, 'Ca', model.fname, inj_nA,
                                      model.param_sim.simtime)
            if model.spineYN and len(model.spinevmtab):
                tables.write_textfile(list(model.spinevmtab.values()), 'SpVm',
                                      model.fname, inj_nA, model.param_sim.simtime)
            if model.spineYN and len(model.spinecatab):
                tables.write_textfile(list(model.spinecatab.values()), 'SpCa',
                                      model.fname, inj_nA, model.param_sim.simtime)
    if model.param_sim.plot_vm:
        neuron_graph.SingleGraphSet(traces, names, model.param_sim.simtime)
        if model.calYN and model.param_sim.plot_calcium:
            neuron_graph.SingleGraphSet(catraces, names, model.param_sim.simtime)
    model.traces = traces
    util.block_if_noninteractive()

def main(model,**kwargs):
    setupOptions(model, **kwargs)
    setupNeurons(model)
    setupOutput(model)
    setupStim(model)
    runAll(model)
    return model
