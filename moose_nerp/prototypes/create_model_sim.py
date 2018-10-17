# -*- coding:utf-8 -*-
from __future__ import print_function, division
import numpy as np
import matplotlib.pyplot as plt
plt.ion()
from pprint import pprint
import moose
import logging

from moose_nerp.prototypes import (cell_proto,
                                   calcium,
                                   clocks,
                                   inject_func,
                                   tables,
                                   plasticity_test,
                                   logutil,
                                   util,
                                   standard_options,
                                   constants)
from moose_nerp.graph import plot_channel, neuron_graph, spine_graph

def setupLogging(level = logging.DEBUG):
    logging.basicConfig(level=level)
    log = logutil.Logger()
    return log

def setupOptions(model, **kwargs):
    '''Can be called with no arguments (except model; but maybe I can figure
    out how to make model by default point to the imported model) and use the
    defaults in standard_options.standard_options(); and apply no param_sim
    overrides; Or can pass keyword arguments that specify fname, plotcomps, defaults
    for standard_options.standard_options, and param_sim overrides '''

    # Handle kwargs successively; when a kwarg meets criteria, pop it from kwargs
    # At the end, if anything is left unpopped from kwargs, raise warning that
    # a meaningless kwarg has been passed.
    if setupOptions.hasBeenCalled == True:
        print('Warning, setupOptions has already been called; overwriting with new options')
    if "plotcomps" in kwargs.keys():
        plotcomps = kwargs.pop("plotcomps")
    else:
        plotcomps = [model.NAME_SOMA]

    # We need to know the possible default arguments in standard_options:
    standard_options_argnames = standard_options.standard_options.__code__.co_varnames
    # Find all kwargs that equal standard_options_argnames:
    standard_options_default_overrides = set(kwargs.keys()) & set(standard_options_argnames)
    #create a new dictionary for standard options overrides and remove item from kwargs
    standard_options_default_dict = dict([ (k, kwargs.pop(k)) for k in standard_options_default_overrides])
    # Now call standard_options, passing any default overrides
    option_parser = standard_options.standard_options(**standard_options_default_dict)

    # We have to parse args to get param_sim before we can handle additional kwargs
    # for param_sim overrides
    param_sim = option_parser.parse_args()
    # Find all remaining kwargs that match param sim variables
    param_sim_overrides = set(kwargs.keys()) & set(vars(param_sim).keys())
    # Override each param_sim parameter in kwargs and remove item from kwargs
    for k in param_sim_overrides:
        setattr(param_sim,k,kwargs.pop(k))
    # Now we can pass param_sim to overrides and return model, plotcomps, and param_sim
    model,plotcomps,param_sim=standard_options.overrides(param_sim,model,plotcomps)

    # Can optionally pass 'fname' in kwargs, else set default
    if 'fname' in kwargs.keys():
        fname = kwargs.pop('fname')
    else:
        fname=model.param_stim.Stimulation.Paradigm.name+'_'+model.param_stim.location.stim_dendrites[0]

    # Setup logging level if in kwargs else set default
    if 'logging_level' in kwargs.keys():
        log = setupLogging(level = kwargs.pop('logging_level'))
    else:
        log = setupLogging()

    ### Add any new code here to parse additional possible kwargs. Pop any handled kwarg from kwargs###

    # Now kwargs should be empty, if not we passed an invalid kwarg
    if len(kwargs) > 0:
        log.warning("Passed invalid keyword arguments {} to setupOptions", kwargs)
        #print("invalid kwarg")
    model.plotcomps = plotcomps
    model.param_sim = param_sim
    model.fname = fname
    setupOptions.hasBeenCalled = True
    return #model, plotcomps, param_sim, fname

setupOptions.hasBeenCalled = False # intializes to False; toggled to True within funciton call

def setupNeurons(model, forceSetupOptions=True):
    '''Creates neuron(s) defined by model. forceSetupOptions=True by default will
    ensure that setupOptions is called before setupNeurons, but if a user passes
    forceSetupOptions = False, neurons can be created whether options setup or not.
    '''
    if forceSetupOptions == True:
        if setupOptions.hasBeenCalled == False:
            setupOptions(model) # sets up with default option_string
    model.syn, model.neurons = cell_proto.neuronclasses(model)

    model.plas = {}
    if model.plasYN:
        model.plas, model.stimtab=plasticity_test.plasticity_test(model, model.param_sim.syncomp, model.syn, model.param_sim.stimtimes)
    return model

def create_model_sim(model):
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
        writer=tables.setup_hdf5_output(model, neurons, filename=fname,compartments=plotcomps)
    else:
        writer=None

    ########## clocks are critical. assign_clocks also sets up the hsolver
    simpaths=['/'+neurotype for neurotype in util.neurontypes(model.param_cond)]

    clocks.assign_clocks(simpaths, param_sim.simdt, param_sim.plotdt, param_sim.hsolve,model.param_cond.NAME_SOMA)
    #fix calculation of B parameter in CaConc if using hsolve
    if param_sim.hsolve and model.calYN:
        calcium.fix_calcium(util.neurontypes(model.param_cond), model)

    return syn,neurons,writer,[vmtab, catab, plastab, currtab]

def setupStim(model,**kwargs):
    neuron_paths = {ntype:[neur.path] for ntype, neur in neuron.items()}
    pg,param_sim=inject_func.setup_stim(model,param_sim,neuron_paths)
    return pg, param_sim

def setupOutput(neuron, param_sim, model,level = logging.DEBUG):
    if level == logging.DEBUG:
        for neur in neuron.keys():
            print_params.print_elem_params(model,neur,param_sim)

    if param_sim.plot_channels:
        for chan in model.Channels.keys():
            libchan=moose.element('/library/'+chan)
            plot_channel.plot_gate_params(libchan,param_sim.plot_activation,
                                          model.VMIN, model.VMAX, model.CAMIN, model.CAMAX)

    if model.spineYN:
        spinecatab,spinevmtab=tables.spinetabs(model,neuron,plotcomps)
    else:
        spinevmtab=[]


def run_simulation(simtime,injection_current=None):
    if model.param_stim.Stimulation.Paradigm.name == 'inject':
        print(u'◢◤◢◤◢◤◢◤ injection_current = {} ◢◤◢◤◢◤◢◤'.format(injection_current))
        pg.firstLevel = injection_current
    moose.reinit()
    moose.start(simtime)

def run_all():
    traces, names, catraces = [], [], []
    for inj in param_sim.injection_current:
        run_simulation(simtime=param_sim.simtime,injection_current=inj)
        if param_sim.plot_vm:
            neuron_graph.graphs(model, vmtab, param_sim.plot_current, param_sim.simtime,
                            currtab, param_sim.plot_current_label,
                            catab, plastab)
        #set up tables that accumulate soma traces for multiple simulations
        for neurnum,neurtype in enumerate(util.neurontypes(model.param_cond)):
            traces.append(vmtab[neurnum][0].vector)
            if model.calYN and param_sim.plot_calcium:
                catraces.append(catab[neurnum][0].vector)
            names.append('{} @ {}'.format(neurtype, inj))
            # In Python3.6, the following syntax works:
            #names.append(f'{neurtype} @ {inj}')
        #plot spines
        if len(spinevmtab) and param_sim.plot_vm:
            spine_graph.spineFig(model,spinecatab,spinevmtab, param_sim.simtime)
        #save output - expand this to optionally save current data
        if param_sim.save:
            inj_nA=inj*1e9
            tables.write_textfile(vmtab,'Vm', fname,inj_nA,param_sim.simtime)
            if model.calYN:
                tables.write_textfile(catab,'Ca', fname,inj_nA,param_sim.simtime)
            if model.spineYN and len(spinevmtab):
                tables.write_textfile(list(spinevmtab.values()),'SpVm', fname,inj_nA,param_sim.simtime)
                if model.spineYN and len(spinecatab):
                    tables.write_textfile(list(spinecatab.values()),'SpCa', fname,inj_nA,param_sim.simtime)

def plotOutputs():
    if param_sim.plot_vm:
        neuron_graph.SingleGraphSet(traces, names, param_sim.simtime)
        if model.calYN and param_sim.plot_calcium:
            neuron_graph.SingleGraphSet(catraces, names, param_sim.simtime)

def main():
    log = model.setupLogging(level = logging.DEBUG)
    model, plotcomps, param_sim, fname = model.setupOptions(defaultOverrides = {
                        'default_injection_current':[-0.2e-9,0.26e-9],
                        'default_stim':'inject',
                        'default_stim_loc':'soma'},
                       param_sim_overrides = {
                           'save':0,
                           'plot_channels':0}
                        )
    syn,neuron,writer,outtables=model.create_model_sim(model,fname,param_sim,plotcomps)
    vmtab, catab, plastab, currtab = outtables
    pg,param_sim=setupStim(neuron,model,param_sim)
    run_all()

def limit_Condset(model,condSubset = 'all'):
    '''To only create and simulate a subset of neurons in model Condset.
       For instance, passing 'D1' to condset argument will remove D2 from
       moose_nerp.d1d2 model. if condset passed as a list/tuple, then all
       listed condsets are kept and any others are removed.
    '''
    if condSubset == 'all':
        return
    if isinstance(condSubset,str):
        condSubset = [condSubset]
    for c in condSubset:
        if c not in model.Condset.keys():
            print('{} Is not a valid condset; not limiting condset'.format(c))
    for k in list(model.Condset.keys()): # must convert keys to list since keys are popped from dictionary within loop
        if k not in condSubset:
            model.Condset.pop(k)
            print("Removing {} from condset".format(k))
