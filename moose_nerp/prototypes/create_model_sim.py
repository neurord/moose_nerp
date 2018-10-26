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

@util.call_counter
def setupOptions(model, **kwargs):
    '''Can be called with no arguments except model. This will use the defaults
    in standard_options.standard_options() and apply no param_sim overrides.
    Can pass any keyword arguments that specify fname, plotcomps, logging_level,
    defaults for standard_options.standard_options(), and param_sim overrides.

    Automatically detects possible kwargs in standard_options, so any default
    added to standard_options or any argument added to standard_options can be
    used without modifying this function.

    Function logic: This function handles kwargs successively; when a kwarg
    meets a criteria, it is popped from kwargs. At the end of the function,
    kwargs should be empy; if anything is left in kwargs, then a meaningless
    kwarg was passed and a warning is raised.

    Function is wrapped with a function that counts calls to enable checking if
    options have already been set up.
    '''
    # Warn if overwriting prior setupOptions
    if setupOptions.calls > 1:
        model.log.warning('''setupOptions has already been called. Overwriting
                          prior call with new options''')

    # Get the option_parser
    option_parser, model_parser = standard_options.standard_options()

    # First parse args with empty list to return param_sim defaults
    # to override below
    # Edit: don't have to do this with param_sim.py method.
    # param_sim, _ = option_parser.parse_known_args([])
    param_sim = model.param_sim

    ###### apply any kwargs that are param_sim overrides. #####
    # Find set of all kwargs that match param_sim variables
    param_sim_overrides = set(set(kwargs.keys()) & set(vars(param_sim).keys()))
    # Override each param_sim parameter in kwargs and pop item from kwargs
    for k in param_sim_overrides:
        setattr(param_sim, k, kwargs.pop(k))

    # Precedence order: Command Line > python module passed kwargs >
    #   model specific defaults > prototype defaults

    # Command line args should have precedence--call here to update param_sim
    # with any command line options after applying param_sim_overrides above
    # TODO: This seems to work but it is not obvious that param_sim attributes
    # are not overridden except only by explicitly passed command line args.
    # Another option: use option_parser.set_defaults(**param_sim_kwargs) to set
    # the param_sim overrides and then call option_parser.parse_known_args.
    # OR yet another option: create sim_params within model directory; import
    # in __init__.py, then calling below command will use the existing namespace
    # and only change any specifically passed command line args
    param_sim, extraArgs = option_parser.parse_known_args(namespace = param_sim)
    # Pass param_sim to overrides and return model, plotcomps, and param_sim
    model_overrides, _ = model_parser.parse_known_args(extraArgs)

    model, plotcomps, param_sim = standard_options.overrides(param_sim, model_overrides, model,
                                                             param_sim.plotcomps)

    ######### Any additional kwarg handling for kwargs not in param_sim or
    ######### standard_options can be added here:
    # Setup logging level
    log = setupLogging(model, level = param_sim.logging_level)

    # Optionally pass 'fname' in kwargs, else set default:
    if param_sim.fname is None:
        param_sim.fname = (model.param_stim.Stimulation.Paradigm.name + '_' +
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
    # model.plotcomps = plotcomps # Now in param_sim
    model.param_sim = param_sim
    # model.fname = fname # now in param_sim
    import pdb
    pdb.set_trace()
    return #model, plotcomps, param_sim, fname


@util.call_counter
def setupNeurons(model, **kwargs):
    '''Creates neuron(s) defined by model. kwargs not yet implemented.'''

    if hasattr(model,'neurons'):
        model.log.warning('Neurons already setup. Returning.')
        return

    if 'param_sim' in kwargs:
        param_sim = kwargs['param_sim']
    else:
        param_sim = model.param_sim
    if param_sim.neuron_type is not None:
        model.param_cond.neurontypes = util.neurontypes(model.param_cond,
                                                    [param_sim.neuron_type])
    # build neurons and specify returns to model namespace
    model.syn, model.neurons = cell_proto.neuronclasses(model)
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

    return model


def setupStim(model,**kwargs):
    '''Setup the stimulation pulse generator. This function requires that the
    neurons and options have already been setup'''
    neuron_paths = {ntype:[neur.path] for ntype, neur in model.neurons.items()}
    pg, param_sim = inject_func.setup_stim(model, model.param_sim, neuron_paths)
    model.pg, model.param_sim = pg, param_sim
    return model

def setupOutput(model, **kwargs):
    ###############--------------output elements
    (vmtab,
     catab,
     plastab,
     currtab) = tables.graphtables(model, model.neurons,
                                   model.param_sim.plot_current,
                                   model.param_sim.plot_current_message,
                                   model.plas,
                                   model.param_sim.plotcomps)

    if model.param_sim.save:
        writer=tables.setup_hdf5_output(model, model.neurons,
                                        filename=model.param_sim.fname,
                                        compartments=model.param_sim.plotcomps)
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
        plt.ion()
        for chan in model.Channels.keys():
            libchan = moose.element('/library/'+chan)
            plot_channel.plot_gate_params(libchan,
                                          model.param_sim.plot_activation,
                                          model.VMIN, model.VMAX,
                                          model.CAMIN, model.CAMAX)

    if model.spineYN:
        model.spinecatab, model.spinevmtab = tables.spinetabs(model,
                                                              model.neurons,
                                                              model.param_sim.plotcomps)
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


def runAll(model, plotIndividualInjections = False):
    plt.ion()
    traces, names, catraces = [], [], []
    for inj in model.param_sim.injection_current:
        runOneSim(model, simtime=model.param_sim.simtime, injection_current=inj)
        if model.param_sim.plot_vm and plotIndividualInjections:
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
        if model.param_sim.save: #TODO: separate hdf5 from save text and make savetext separate function
            inj_nA=inj*1e9
            tables.write_textfile(model.vmtab, 'Vm', model.param_sim.fname, inj_nA,
                                  model.param_sim.simtime)
            if model.calYN:
                tables.write_textfile(model.catab, 'Ca', model.param_sim.fname, inj_nA,
                                      model.param_sim.simtime)
            if model.spineYN and len(model.spinevmtab):
                tables.write_textfile(list(model.spinevmtab.values()), 'SpVm',
                                      model.param_sim.fname, inj_nA, model.param_sim.simtime)
            if model.spineYN and len(model.spinecatab):
                tables.write_textfile(list(model.spinecatab.values()), 'SpCa',
                                      model.param_sim.fname, inj_nA, model.param_sim.simtime)
    if model.param_sim.plot_vm:
        neuron_graph.SingleGraphSet(traces, names, model.param_sim.simtime)
        if model.calYN and model.param_sim.plot_calcium:
            neuron_graph.SingleGraphSet(catraces, names, model.param_sim.simtime)
    model.traces = traces
    util.block_if_noninteractive()

def setupAll(model,**kwargs):
    setupOptions(model, **kwargs)
    setupNeurons(model)
    setupOutput(model)
    setupStim(model)
    return model
