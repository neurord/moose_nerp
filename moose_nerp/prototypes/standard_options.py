import argparse
import numbers
import numpy as np
from . import util

def inclusive_range_from_string(arg):
    parts = arg.split(':')
    if len(parts) == 1:
        return np.array([float(parts[0])])
    start, stop = float(parts[0]), float(parts[1])
    if len(parts) == 2:
        return util.inclusive_range(start, stop)
    elif len(parts) == 3:
        return util.inclusive_range(start, stop, float(parts[2]))
    raise ValueError('too many colons')


def comma_seperated_list(float):
    def parser(arg):
        return [float(x) for x in arg.split(',')]

def parse_boolean(s):
    if s in {"1", "true", "True", "yes"}:
        return True

    if s in {"0", "false", "False", "no"}:
        return False

    raise ValueError("Invalid literal for bool(): {!r}".format(s))

def standard_options(parser=None,
                     default_simulation_time=0.35,
                     default_plotdt=0.2e-3,
                     default_calcium=None,
                     default_spines=None,
                     default_synapse=None,
                     default_injection_current=None,
                     default_injection_delay=0.1,
                     default_injection_width=0.4,
                     default_plot_vm=True,
                     default_stim=None,
                     default_stim_loc=None):

    if parser is None:
        param_sim_parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    #simulation parameters
    param_sim_parser.add_argument('--simtime', '-t', type=float,
                        help='Simulation time',
                        default=default_simulation_time)
    param_sim_parser.add_argument('--simdt', type=float,
                        help='Simulation step',
                        default=10e-6)
    param_sim_parser.add_argument('--plotdt', type=float,
                        help='Plot point distance',
                        default=default_plotdt)
    param_sim_parser.add_argument('--hsolve', type=parse_boolean, nargs='?',
                        help='Use the HSOLVE solver',
                        const=True, default=True)
    param_sim_parser.add_argument('--save', nargs='?', metavar='FILE',
                        help='Write voltage and calcium (if enabled) to (HDF5) file. use single character for auto naming',
                        const='d1d2.h5')

    #arguments/parameters to control what model details to include
    model_parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter, add_help=True)
    model_parser.add_argument('--calcium', type=parse_boolean, nargs='?',
                        help='Implement Ca dynamics',
                        const=True, default=default_calcium, dest = 'calYN')
    model_parser.add_argument('--spines', type=parse_boolean, nargs='?',
                        help='Implement spines',
                        const=True, default=default_spines, dest = 'spineYN')
    model_parser.add_argument('--synapse', type=parse_boolean, nargs='?',
                        help='Implement synapses',
                        const=True, default=default_calcium, dest = 'synYN')

    #Argument/parameters to control model parameter overrides.
    #ONLY applies to subattritubes of model, anything accessible as model[dot]XX
    model_parser.add_argument('--modelParamOverrides', default=None, nargs='*',
                        metavar='PARAMS.PARAMNAME:PARAMVALUE',
                        help='One or more (space separated) param:value pairs (colon-designated) to override model params, e.g.: ParamSpine.SpineDensity:1e6 SYNAPSE_TYPES.ampa.Gbar:1e-9')

    #arguments / parameters to control stimulation during simulation
    param_sim_parser.add_argument('--injection-current', '-i', type=inclusive_range_from_string,
                        metavar='CURRENT',
                        help='One or range of currents (either start:stop or start:stop:increment)',
                        default=default_injection_current)
    param_sim_parser.add_argument('--injection-delay', type=float,
                        metavar='TIME',
                        help='Start current injection at this time',
                        default=default_injection_delay)
    param_sim_parser.add_argument('--injection-width', type=float,
                        metavar='TIME',
                        help='Inject current for this much time',
                        default=default_injection_width)
    #Test that specifying 'TBS' will work, maybe not str but Paradigm
    param_sim_parser.add_argument('--stim-paradigm', type=str,
                        help='Stimuation Paradigm from param_stim.py, or inject',
                        default=default_stim)
    # type= for stimLoc - allow multiple spines
    param_sim_parser.add_argument('--stim-loc', type=str,
                        help='compartment for synapses',
                        default=default_stim_loc)

    #arguments that control what to plot
    param_sim_parser.add_argument('--plot-vm', type=parse_boolean, nargs='?',
                        help='Whether to plot membrane potential Vm',
                        const=True, default=default_plot_vm)
    param_sim_parser.add_argument('--plot-current', type=parse_boolean, nargs='?',
                        help='Whether to plot the current',
                        const=True)
    param_sim_parser.add_argument('--plot-calcium', type=parse_boolean, nargs='?',
                        help='Whether to plot calcium',
                        const=True)
    param_sim_parser.add_argument('--plot-current-message', metavar='NAME',
                        help='The moose message to use',
                        default='getGk')
    param_sim_parser.add_argument('--plot-current-label', metavar='LABEL',
                        help='Current plot label',
                        default='Cond, S')

    param_sim_parser.add_argument('--plot-synapse', type=parse_boolean, nargs='?', metavar='BOOL',
                        const=True)
    param_sim_parser.add_argument('--plot-synapse-message', metavar='NAME',
                        default='getGk')
    param_sim_parser.add_argument('--plot-synapse-label', metavar='LABEL',
                        default='Cond, nS')

    param_sim_parser.add_argument('--plot-channels', type=parse_boolean, nargs='?', metavar='BOOL',
                        const=True)
    param_sim_parser.add_argument('--plot-activation', type=parse_boolean, nargs='?', metavar='BOOL',
                        const=True)
    param_sim_parser.add_argument('--plot-network', type=parse_boolean, nargs='?', metavar='BOOL',
                        const=True)
    param_sim_parser.add_argument('--plot-netvm', type=parse_boolean, nargs='?', metavar='BOOL',
                        const=True)
    return param_sim_parser, model_parser


def parseModelParamOverrides(model, modelParamOverrides):
    ''' modelParamOverrides is a list of strings, each string indicating a
    param to override. Each list item is a colon separated key:value pair,
    e.g. 'SpineParams.SpineDensity:1e6'. Params can consist of multiple
    periods, e.g. MyParams.Aparams.Bparams.C '''
    # TODO: In addition to attribute access, could add index access with [];
    #    This would allow param like: model.SpineParams.SpineChanList[0]:'CaT'
    for i in modelParamOverrides:  # for string in override list
        paramString, valueString = i.split(':')  # split on colon
        # Split on period to determine nested attributes
        paramList = paramString.split('.')
        # Makes sure first entry is an attribute of model, e.g.
        # model.SpineParams. Raises attribute error if attribute does not exist
        j = 0
        a = getattr(model, paramList[j])
        # successively check that attribute exists
        for j in range(1, len(paramList)):  # Won't enter loop if length is 1
            a = getattr(a, paramList[j])
        # Limit to string or number
        if isinstance(a, (str, numbers.Number)):
            # Convert the value string to value of same class type as a. if a
            # is float, will convert value string to float.
            value = a.__class__(valueString)
            originalvalue = a
        else:
            raise Exception('modelParamOverrides limited to strings & numbers')
        # Now get 2nd to last attribute and set attribute of last item
        a = getattr(model, paramList[0])
        # Won't enter loop if length is 1; will loop to the second to last item
        for j in range(1, len(paramList)-1):
            a = getattr(a, paramList[j])
        setattr(a, paramList[-1], value)  # Set a.paramValue to new value
        print('Setting attribute ' + paramList[-1] + ' of object '+str(a) +
              ' from ' + str(originalvalue) + ' to ' + str(value))


def overrides(param_sim, model):
    #These assignment statements are required because they are not part of param_sim namespace.
    if param_sim.stim_paradigm is not None:
        model.param_stim.Stimulation.Paradigm=model.param_stim.paradigm_dict[param_sim.stim_paradigm]
    if param_sim.stim_loc is not None:
        model.param_stim.Stimulation.StimLoc.stim_dendrites=[param_sim.stim_loc]
    if model.modelParamOverrides is not None:
        parseModelParamOverrides(model,param_sim.modelParamOverrides)
    #These assignments make assumptions about which parameters should be changed together
    if model.calYN and param_sim.plot_calcium is None:
        param_sim.plot_calcium = True
    if model.param_stim.Stimulation.Paradigm.name is not 'inject':
        #override defaults if synaptic stimulation is planned
        model.synYN=1

    #update in future: currently cannot deal with more than one stim_dendrite in option parser (OK in param_stim.location)
    if model.param_stim.Stimulation.Paradigm.name is not 'inject' or param_sim.stim_loc is not None:
        #param_sim.plotcomps=list(np.unique(param_sim.plotcomps+model.param_stim.location.stim_dendrites))
        #np.unique sorts the list.  Move soma to be first if it exists
        plotcomps=list(np.unique(param_sim.plotcomps+model.param_stim.Stimulation.StimLoc.stim_dendrites))
        if model.NAME_SOMA in plotcomps:
            plotcomps.insert(0,plotcomps.pop(plotcomps.index(model.NAME_SOMA)))
        param_sim.plotcomps=plotcomps
    return model,param_sim

class AppendFlat(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        getattr(namespace, self.dest).extend(values)
