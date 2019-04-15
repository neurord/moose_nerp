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
    in param_sim.py param_model_defaults.py and apply no overrides.

    Optionally, can pass any keyword arguments that are parameter names in
    param_sim (e.g. fname, plotcomps, logging_level, etc.) to override them.

    This function also handles any command line arguments. When run from command
    line, any command line options will take precedence over param_sim and
    param_model_defaults.

    Function is wrapped with a function that counts calls to enable checking if
    options have already been set up.
    '''
    # Warn if overwriting prior setupOptions
    if setupOptions.calls > 1:
        model.log.warning('''setupOptions has already been called. Overwriting
                          prior call with new options''')

    # Get the option_parsers
    param_sim_parser, model_parser = standard_options.standard_options()

    param_sim = model.param_sim
    ###### apply any kwargs that are param_sim overrides. #####
    # Find set of all kwargs that match param_sim variables
    param_sim_overrides = set(set(kwargs.keys()) & set(vars(param_sim).keys()))
    # Override each param_sim parameter in kwargs and pop item from kwargs
    for k in param_sim_overrides:
        setattr(param_sim, k, kwargs.pop(k))

    # Command line args should have precedence--call here to update param_sim
    # with any command line options after applying param_sim_overrides above
    # Passing existing namespace into parse_known_args will only set attributes
    # for command line arguments that are explicitly passed; no defaults are set
    param_sim, unknown_args = param_sim_parser.parse_known_args(namespace = param_sim)
    # parsing model params separately for setting spineYN, calYN, etc. from command line
    model, _ = model_parser.parse_known_args(unknown_args, namespace = model)

    # Pass param_sim to overrides and return model, plotcomps, and param_sim
    model, param_sim = standard_options.overrides(param_sim, model)

    # Any additional kwarg handling for kwargs not in param_sim can be added here:
    # Setup logging level
    log = setupLogging(model, level = param_sim.logging_level)

    # Set fname to default if is None in param_sim:
    if param_sim.fname is None:
        param_sim.fname = (model.param_stim.Stimulation.Paradigm.name + '_' +
                           #model.param_stim.location.stim_dendrites[0])
                           #change to (after checking with Dan)
                           model.param_stim.Stimulation.StimLoc.stim_dendrites[0])

    ######### Add any new code here to parse additional possible kwargs.
    ######### Be sure to pop any parsed kwarg from kwargs dictionary.

    ######### Now kwargs should be empty, if not we passed an invalid kwarg
    if len(kwargs) > 0:
        log.warning("Passed invalid keyword arguments {} to setupOptions",
                    kwargs)
    return model # Not necessary to return


#@util.call_counter
def setupNeurons(model, **kwargs):
    '''Creates neuron(s) defined by model.

    By default, uses param_sim imported with model (model.param_sim), but
    passing 'param_sim=param_sim' in as a kwarg allows overriding; when called
    in ajustador, the param_sim defined by ajustador is explicitly passed in.'''

    if hasattr(model,'neurons'):
        model.log.warning('Neurons already setup. Returning.')
        return

    # If network (expects Boolean) passed to setupNeurons, get the value. otherwise set to None
    if 'network' in kwargs:
        network = kwargs.pop('network')
    else:
        network = None

    if 'param_sim' in kwargs:
        param_sim = kwargs['param_sim']
    else:
        param_sim = model.param_sim
    if getattr(param_sim, 'neuron_type', None) is not None:
        model.param_cond.neurontypes = util.neurontypes(model.param_cond,
                                                    [param_sim.neuron_type])
    # build neurons and specify returns to model namespace
    model.syn, model.neurons = cell_proto.neuronclasses(model)
    # If calcium and synapses created, could test plasticity at a single synapse
    # in syncomp. Need to debug this since eliminated param_sim.stimtimes. See
    # what else needs to be changed in plasticity_test.
    model.plas = {}
    #if model.plasYN:
    #    model.plas, model.stimtab = plasticity_test.plasticity_test(model)
                                                    #param_sim.syncomp,
                                                    #model.syn,
                                                    #param_sim.stimtimes)

    ########## clocks are critical. assign_clocks also sets up the hsolver

    if not network:
        print("Not simulating network; setting up simpaths and clocks in create_model_sim")
        simpaths=['/'+neurotype for neurotype in util.neurontypes(model.param_cond)]
        clocks.assign_clocks(simpaths, param_sim.simdt, param_sim.plotdt,
                             param_sim.hsolve, model.param_cond.NAME_SOMA)
        # Fix calculation of B parameter in CaConc if using hsolve
        if model.param_sim.hsolve and model.calYN:
            calcium.fix_calcium(util.neurontypes(model.param_cond), model)
    else:
        print("Simulating network; not setting up simpaths and clocks in create_model_sim")

    print('****Model.plasYN = {}*****'.format(model.plasYN))

    return model


def setupStim(model,**kwargs):
    '''Setup the stimulation pulse generator. This function requires that the
    neurons and options have already been setup'''
    if getattr(model,'inject_pop',False):
        neuron_paths = model.inject_pop
    else:
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
        if type(model.param_sim.plot_channels) is str:
            useChans = [model.param_sim.plot_channels] #Convert to list of len 1
        elif type(model.param_sim.plot_channels) is list:
            useChans = model.param_sim.plot_channels # Use the list of channel name strings
        else:
            useChans = model.Channels.keys() # Use all channels
        for chan in useChans:
            libchan = moose.element('/library/'+chan)
            plot_channel.plot_gate_params(libchan,
                                          model.param_sim.plot_activation,
                                          model.VMIN, model.VMAX,
                                          model.CAMIN, model.CAMAX)

    if model.spineYN:
        model.spinecatab, model.spinevmtab = tables.spinetabs(model,
                                                              model.neurons,
                                                              #model.param_sim.plotcomps,
                                                              )
    else:
        model.spinevmtab = []

    model.spiketab=tables.spiketables(model.neurons, model.param_cond)

    if getattr(model.param_sim,'plotgate',None):
        plotgate = model.param_sim.plotgate
        gatepath = list(model.neurons.values())[0].path+'/'+model.NAME_SOMA+'/'+plotgate
        gate = moose.element(gatepath)
        model.gatetables = {}
        gatextab=moose.Table('/data/gatex')
        moose.connect(gatextab, 'requestOut', gate, 'getX')
        model.gatetables['gatextab']=gatextab
        gateytab=moose.Table('/data/gatey')
        moose.connect(gateytab, 'requestOut', gate, 'getY')
        model.gatetables['gateytab']=gateytab
        if model.Channels[plotgate][0][2]==1:
            gateztab=moose.Table('/data/gatez')
            moose.connect(gateztab, 'requestOut', gate, 'getZ')
            model.gatetables['gateztab']=gateztab
    return


def runOneSim(model, simtime=None, injection_current=None):
    if model.param_stim.Stimulation.Paradigm.name == 'inject':
        print(u'◢◤◢◤◢◤◢◤ injection_current = {} ◢◤◢◤◢◤◢◤'.format(injection_current))
        model.pg.firstLevel = injection_current
    if simtime is None: simtime = model.param_sim.simtime
    moose.reinit()
    moose.start(simtime)

def stepRunPlot(model, **kwargs):
    if 'neuron' in kwargs:
        mod = kwargs['neuron']
    else:
        mod = list(model.neurons.values())[0][0]
    mod.buildSegmentTree()
    import moogul
    mv = moogul.MooView()
    #mv.ax.set_proj_type('ortho')

    # [baseclass, fieldGetFunc, scale, axisText, min, max]
    fieldinfo = ['Compartment', 'getVm', 1, 'Vm', 0, 1]
    m = moogul.MooNeuron(mod,fieldinfo, maxLineWidth = 10, diaScale = 10e6, colormap = 'viridis')
    mv.addDrawable(m)
    mv.firstDraw()
    #mv.ax.set_proj_type('ortho')

    plt.pause(1)
    mv.updateValues()
    plt.pause(60)

    #steps = int(np.round(model.param_sim.simtime/(model.param_sim.plotdt)))
    #for i in range(steps):
    #    moose.start(model.param_sim.plotdt)
    #    mv.updateValues()
    #    plt.pause(.01)

def runAll(model, plotIndividualInjections=False, writeWavesCSV=False, printParams = False):
    plt.ion()
    if model.plasYN:
        plotIndividualInjections=True
    traces, names, catraces, current_traces, curr_names = [], [], [], [], []
    for inj in model.param_sim.injection_current:
        runOneSim(model, simtime=model.param_sim.simtime, injection_current=inj)
        if model.param_sim.plot_vm and plotIndividualInjections:
            neuron_graph.graphs(model, model.vmtab, model.param_sim.plot_current,
                                model.param_sim.simtime, model.currtab,
                                model.param_sim.plot_current_label,
                                model.catab, model.plastab)
        #set up tables that accumulate soma traces for multiple simulations
        for neurnum,neurtype in enumerate(model.neurons.keys()):
            for plotcompnum, plotcomp in enumerate(model.param_sim.plotcomps):
                traces.append(model.vmtab[neurtype][plotcompnum].vector)
                if model.calYN and model.param_sim.plot_calcium:
                    catraces.append(model.catab[neurtype][plotcompnum].vector)
                names.append('{} {} @ {}'.format(plotcomp, neurtype, inj))
                # In Python3.6, the following syntax works:
                #names.append(f'{neurtype} @ {inj}')
        if model.param_sim.plot_current:
            for channame in model.Channels.keys():
                current_traces.append(model.currtab[neurtype][channame][0].vector)
                curr_names.append('{}: {} @ {}'.format(neurtype, channame,inj))

        #plot spines
        if len(model.spinevmtab) and model.param_sim.plot_vm:
            spine_graph.spineFig(model, model.spinecatab, model.spinevmtab,
                                 model.param_sim.simtime)
        #save plain text output - expand this to optionally save current data
        if model.param_sim.save_txt:
            tables.write_textfiles(model, inj)

        # Switch hdf5writer mode from 2 (overwrite) to 1 (append)
        # Note that hdf5writer is initialized in mode 2, overwriting prior simulations,
        # But within one simulation at multiple current injections setting mode to 1
        # allows appending the file with each current injection iteration,
        # and calling "wrap_hdf5" modifies the hdf5 file for each injection
        if model.param_sim.save:
            model.writer.mode=1
            model.writer.close()
            tables.wrap_hdf5(model,'injection_{}'.format(inj))

    if model.param_sim.plot_vm:
        neuron_graph.SingleGraphSet(traces, names, model.param_sim.simtime)
        if model.calYN and model.param_sim.plot_calcium:
            neuron_graph.SingleGraphSet(catraces, names, model.param_sim.simtime,title='Calcium')

    if model.param_sim.plot_current:
        num_currents=np.shape(current_traces)[0]//len(model.param_sim.injection_current)
        neuron_graph.SingleGraphSet(current_traces[-num_currents:], curr_names,model.param_sim.simtime)
        if getattr(model.param_sim,'plotgate',None):
            plt.figure()
            ts = np.linspace(0, model.param_sim.simtime, len(model.gatetables['gatextab'].vector))
            plt.suptitle('X,Y,Z gates; hsolve='+str(model.param_sim.hsolve)+' calYN='+str(model.calYN)+' Zgate='+str(model.Channels[model.param_sim.plotgate][0][2]))
            plt.plot(ts,model.gatetables['gatextab'].vector,label='X')
            plt.plot(ts,model.gatetables['gateytab'].vector,label='Y')
            if model.Channels[model.param_sim.plotgate][0][2]==1:
                plt.plot(ts,model.gatetables['gateztab'].vector,label='Z')
            plt.legend()

    util.block_if_noninteractive()
    for st in model.spiketab:
          print("number of spikes", st.path, ' = ',len(st.vector))

    model.traces, model.catraces = traces, catraces
    if model.param_sim.save:
        tables.save_hdf5_attributes(model)
        model.writer.close()
    if writeWavesCSV:
        timeCol = np.linspace(0, model.param_sim.simtime, len(model.traces[0]))*1e3 #ms
        vCol = model.traces[0] *1e3 #mV
        inj = model.param_sim.injection_current[0]
        header = 'Time (ms),{} pA'.format(inj*1e12)
        np.savetxt(model.param_sim.fname+'difshellwaves.csv', np.column_stack((timeCol,vCol)), delimiter=',', header = header, comments='' )


def setupAll(model,**kwargs):
    setupOptions(model, **kwargs)
    setupNeurons(model)
    setupOutput(model)
    setupStim(model)
    return model
