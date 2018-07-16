'''
If spineRM, spineCM, headRA, neckRA, spineELEAK, or spineEREST == None,
then those values will be set using the global values (calculated from the 
soma values in spines.py, so will work with .p files or a future implementation
of .swc morphology files). Otherwise, values given here will be used. 
'''
from . import param_cond
from moose_nerp.prototypes import util as _util

SpineParams = _util.NamedDict(
    'SpineParams',
    # TODO: Make distance dependent
    spineDensity = 1.01e6,      #Actual, experimentally reported/estimated spine density, used to compensate for spines when spines not explicitly modeled; should make this distance dependent
    necklen = 0.5e-6,          #define all these parameters elsewhere
    neckdia = 0.12e-6,
    headdia = 0.5e-6,
    headlen = 0.5e-6,
    headRA = None,
    neckRA = 11.3, # gives neckRa = 500 megaOhms, experimentally estimated value at least in pyramidal neurons.
    spineRM = None,
    spineCM = None,
    spineELEAK = None,
    spineEREST = None,
    spineStart = 26.1e-6,
    spineEnd = 300e-6,
    explicitSpineDensity = .3e6, #Density of spines to explicitly model, < or = to spineDensity
    spineChanList = [['CaL13'],['CaL12','CaR','CaT']], #TODO: Specify for each channel the gbar ratio as a dictionary or named dict rather than list; also specify which difshell;
    #spines added to branches that are children of this branch:
    spineParent = 'secdend11', 
    #spineCond = [0.65 *cond for  param_cond.ghKluge],

)
