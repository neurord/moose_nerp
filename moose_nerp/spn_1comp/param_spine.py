'''
If spineRM, spineCM, headRA, neckRA, spineELEAK, or spineEREST == None,
then those values will be set using the global values (calculated from the
soma values in spines.py, so will work with .p files or a future implementation
of .swc morphology files). Otherwise, values given here will be used.

The spineDensity parameter can be a value or a callable function. If callable,
it should be a function of a single argument, f(x), where x is distance from
soma (in meters). The function or the single value will only be applied between
the spineStart and spineEnd parameters.

The model implements spine Compensation by default for the spineDensity
parameter. This can be bypassed by setting spineDensity = 0.

Spines can also be explicitly modeled at the density specified by
explicitSpineDensity (which at this point should be a value, not a callable).
Spines are only explicitly modeled on branches that are children of spineParent.
This will only be done if the spinesYN option is set to True (e.g. by --spines 1
from command line argument).
'''
from . import param_cond
from moose_nerp.prototypes import util as _util
import numpy as np

def _callableSpineDensity(x):
    '''Returns spine density at distance x (in meters) from soma by computing a
    distance-dependent function.

    This function fits a dual exponential to spine density estimates from:
        Wilson, C. J. (1992). Dendritic morphology, inward rectification, and
        the functional properties of neostriatal neurons. In Single neuron
        computation (pp. 141-171).

    The function is a function of spineStart location, so to make it a function
    of distance from the soma we must subtract spineStart from x.
    '''
    spineStart = SpineParams.spineStart
    x = x - spineStart
    a = 5.78e6  # Amplitude of dual exponential function fit, spines/meter
    tau1 = 106.2e-6  # meters
    tau2 = 24.9e-6  # meters
    f = a * (np.exp(-x/tau1) - np.exp(-x/tau2))
    return f

_condfrac = 1.0
SpineParams = _util.NamedDict(
    'SpineParams',
    # Actual, experimentally reported/estimated spine density, used to
    # compensate for spines when spines not explicitly modeled; can be a value
    # or a distance dependent function
    #spineDensity = 1.01e6,  # spineDensity as a value
    spineDensity = _callableSpineDensity,  # spineDensity as a callable
    necklen = 0.5e-6,
    neckdia = 0.12e-6,
    headdia = 0.5e-6,
    headlen = 0.5e-6,
    headRA = None,
    neckRA = 11.3,  # gives neckRa = 500 megaOhms, experimentally estimated value at least in pyramidal neurons.
    spineRM = None,
    spineCM = None,
    spineELEAK = None,
    spineEREST = None,
    spineStart = 26.1e-6,
    spineEnd = 300e-6,
    explicitSpineDensity = .1e6, #Density of spines to explicitly model, Should be < or = to spineDensity. TODO: Consider changing to Fraction of SpineDensity
    spineChanList = [[('CaL13',_condfrac)],[('CaL12',_condfrac),('CaR',_condfrac),('CaT',_condfrac)]], #TODO: Specify for each channel the gbar ratio as a dictionary or named dict rather than list; also specify which difshell;
    #spines added to branches that are children of this branch:
    spineParent = 'soma',
    #spineCond = [0.65 *cond for  param_cond.ghKluge],

)
