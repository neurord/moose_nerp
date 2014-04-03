from __future__ import division
import numpy as np

def inclusive_range(start, stop=None, step=None):
    if stop is None:
        stop = start
    if stop == start:
        return np.array([start])
    if step is None:
        step = stop - start
    return np.arange(start, stop + step/2, step)

def dist_num(table, dist):
    for num, val in enumerate(table):
        if dist < val:
            return num
    else:
        return num

try:
    from __builtin__ import execfile
except ImportError:
    def execfile(fn):
        exec(compile(open(fn).read(), fn, 'exec'))
