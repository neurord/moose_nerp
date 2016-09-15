import argparse
from . import util

def inclusive_range_from_string(arg):
    parts = args.split(':')
    if len(parts) == 1:
        return numpy.array([float(parts[0])])
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

    parser.add_argument('--simtime', '-t',
                        help='Simulation time',
                        default=default_simulation_time)
    parser.add_argument('--simdt', type=float,
                        default=10e-6)
    parser.add_argument('--plotdt', type=float,
                        default=0.2e-3)
    parser.add_argument('--hsolve', type=bool, nargs='?',
                        const=True, default=True)

    parser.add_argument('--injection-current', '-i', type=inclusive_range_from_string,
                        default=default_injection_current)
    parser.add_argument('--injection-delay', type=float,
                        default=default_injection_delay)
    parser.add_argument('--injection-width', type=float,
                        default=default_injection_width)

    parser.add_argument('--stimtimes', type=comma_seperated_list(float),
                        default=default_stimtimes)
    parser.add_argument('--syncomp', type=int,
                        default=default_syncomp)

    parser.add_argument('--plot-current', type=bool, nargs='?',
                        const=True, default=False)
    parser.add_argument('--plot-current-message',
                        default='getGk')
    parser.add_argument('--plot-current-label',
                        default='Cond, S')

    parser.add_argument('--plot-synapse', type=bool, nargs='?',
                        const=True, default=False)
    parser.add_argument('--plot-synapse-message',
                        default='getGk')
    parser.add_argument('--plot-synapse-label',
                        default='Cond, nS')

    parser.add_argument('--plot-channels', type=bool, nargs='?',
                        const=True, default=False)
    parser.add_argument('--plot-activation', type=bool, nargs='?',
                        const=True, default=False)
    parser.add_argument('--plot-network', type=bool, nargs='?',
                        const=True, default=False)
    parser.add_argument('--plot-xxx', type=bool, nargs='?',
                        const=True, default=False)
    return parser
