import argparse
import numpy as np
from . import util

def inclusive_range_from_string(arg):
    parts = arg.split(':')
    if len(parts) == 1:
        return np.array([float(parts[0])])
    start, stop = float(parts[0]), float(parts[1])
    if len(parts) == 2:
        return utils.inclusive_range(start, stop, (stop - start) / 5)
    elif len(parts) == 3:
        return utils.inclusive_range(start, stop, float(parts[1]))
    raise ValueError('too many colons')

def comma_seperated_list(float):
    def parser(arg):
        return [float(x) for x in arg.split(',')]

def standard_options(parser=None,
                     default_injection_current=[0.25e-9, 0.35e-9],
                     default_injection_delay=0.1,
                     default_injection_width=0.4,
                     default_simulation_time=0.35,
                     default_stimtimes=[0.04,0.19,0.46],
                     default_syncomp=4):

    if parser is None:
        parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('--simtime', '-t', type=float,
                        help='Simulation time',
                        default=default_simulation_time)
    parser.add_argument('--simdt', type=float,
                        help='Simulation step',
                        default=10e-6)
    parser.add_argument('--plotdt', type=float,
                        help='Plot point distance',
                        default=0.2e-3)
    parser.add_argument('--hsolve', type=bool, nargs='?',
                        help='Use the HSOLVE solver',
                        const=True, default=True)

    parser.add_argument('--injection-current', '-i', type=inclusive_range_from_string,
                        metavar='CURRENT',
                        help='One or more injection currents (V)',
                        default=default_injection_current)
    parser.add_argument('--injection-delay', type=float,
                        metavar='TIME',
                        help='Start current injection at this time',
                        default=default_injection_delay)
    parser.add_argument('--injection-width', type=float,
                        metavar='TIME',
                        help='Inject current for this much time',
                        default=default_injection_width)

    parser.add_argument('--stimtimes', type=comma_seperated_list(float),
                        metavar='TIMEPOINTS',
                        help='',
                        default=default_stimtimes)
    parser.add_argument('--syncomp', type=int,
                        help='Synapse compartment number',
                        default=default_syncomp)

    parser.add_argument('--plot-current', type=bool, nargs='?',
                        help='Whether to plot the current',
                        const=True, default=False)
    parser.add_argument('--plot-current-message', metavar='NAME',
                        help='The moose message to use',
                        default='getGk')
    parser.add_argument('--plot-current-label', metavar='LABEL',
                        help='Current plot label',
                        default='Cond, S')

    parser.add_argument('--plot-synapse', type=bool, nargs='?', metavar='BOOL',
                        const=True, default=False)
    parser.add_argument('--plot-synapse-message', metavar='NAME',
                        default='getGk')
    parser.add_argument('--plot-synapse-label', metavar='LABEL',
                        default='Cond, nS')

    parser.add_argument('--plot-channels', type=bool, nargs='?', metavar='BOOL',
                        const=True, default=False)
    parser.add_argument('--plot-activation', type=bool, nargs='?', metavar='BOOL',
                        const=True, default=False)
    parser.add_argument('--plot-network', type=bool, nargs='?', metavar='BOOL',
                        const=True, default=False)
    parser.add_argument('--plot-netvm', type=bool, nargs='?', metavar='BOOL',
                        const=True, default=False)
    return parser
