from . import param_cond

from moose_nerp.prototypes import util as _util

#TODO: Automatically pull spine RM, CM, values from p File values?
# Set default RM,CM, etc.. to None and if None use the global values
# in spine compensation functions.
SpineParams = _util.NamedDict(
    'SpineParams',
    spineDensity = 1.01e6,      #Actual, experimentally reported/estimated spine density, used to compensate for spines when spines not explicitly modeled; should make this distance dependent
    necklen = 0.5e-6,          #define all these parameters elsewhere
    neckdia = 0.12e-6,
    headdia = 0.5e-6,
    headlen = 0.5e-6,
    headRA = 1.921,
    neckRA = 1.921*4,    #additional factor of 4 due to exptl higher than expected Ra Spine
    spineRM = 4.8448,
    spineCM = 0.03,
    spineELEAK = -79.2e-3,
    spineEREST = -86e-3,
    spineStart = 26.1e-6,
    spineEnd = 300e-6,
    
    explicitSpineDensity = .3e6, #Density of spines to explicitly model, < or = to spineDensity
    spineChanList = [['CaL13'],['CaL12','CaR','CaT']], #TODO: Specify for each channel the gbar ratio as a dictionary;
    #spines added to branches that are children of this branch:
    spineParent = 'secdend11', 
    #spineCond = [0.65 *cond for  param_cond.ghKluge],

)
