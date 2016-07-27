# -*- coding:utf-8 -*-
from collections import namedtuple
import numpy as np

IsoScaling = namedtuple('IsoScaling', 'unit divisor')
ISO = {-1:u'm',
       -2:u'µ',
       -3:u'n',
       -4:u'p',
       -5:u'f',
       -6:u'a',
       -7:u'z',
       -8:u'y',
       1:u'k',
       2:u'M',
       3:u'G',
       4:u'T',
       5:u'P',
       6:u'E',
       7:u'Z',
       8:u'Y'}

def iso_scaling(*arrays):
    extent = max(np.abs(array).max() for array in arrays)
    magn = np.log10(extent) // 3 if extent > 0 else 0
    try:
        return IsoScaling(ISO[magn], 10**(magn*3))
    except KeyError:
        return IsoScaling(u'', 1)
