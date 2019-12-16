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
from moose_nerp.prototypes import util as _util

SpineParams = _util.NamedDict(
    'SpineParams',
    spineDensity = 0, #Actual, experimentally reported/estimated spine density, in spines/meter, 
    necklen = 0.3e-6,          #define all these parameters elsewhere
    neckdia = 0.1e-6,
    headdia = 0.5e-6,
    headlen = 0.5e-6,
    headRA = 4,    
    neckRA = 11.3,
    spineRM = 2.8,
    spineCM = 0.01,
    spineELEAK = -50e-3,
    spineEREST = -80e-3,
    spineStart = 26.1e-6,
    spineEnd = 300e-6,

    explicitSpineDensity = 0, #Density of spines (per meter dendritic length) to explicitly model, < or = to spineDensity
    spineChanList = [],
    spineParent = 'soma',
)
