from . import param_cond

from moose_nerp.prototypes import util as _util

#UNITS: len, dia, spineStart,spineEnd: meters
#       density: spines per meter
#       RA: ohm-meters, RM: ohm-m2, CM: Farads/m2
SpineParams = _util.NamedDict(
    'SpineParams',
    spineDensity = 0, #Actual, experimentally reported/estimated spine density, in spines/meter, used to compensate for spines when spines not explicitly modeled; should make this distance dependent
    necklen = 0.3e-6,          #define all these parameters elsewhere
    neckdia = 0.1e-6,
    headdia = 0.5e-6,
    headlen = 0.5e-6,
    headRA = 4*4,    #additional factor of 4 due to exptl higher than expected Ra Spine
    neckRA = 11.3,
    spineRM = 2.8,
    spineCM = 0.01,
    spineELEAK = -50e-3,
    spineEREST = -80e-3,
    spineStart = 26.1e-6,
    spineEnd = 300e-6,
    
    explicitSpineDensity = 0, #Density of spines (per meter dendritic length) to explicitly model, < or = to spineDensity
    spineChanList = [], #['CaL13']
    spineParent = 'soma',
)
