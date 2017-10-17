from . import param_cond

from moose_nerp.prototypes import util as _util

SpineParams = _util.NamedDict(
    'SpineParams',
    spineDensity = 1.01e6,      #should make this distance dependent
    necklen = 0.5e-6,          #define all these parameters elsewhere
    neckdia = 0.12e-6,
    headdia = 0.5e-6,
    headlen = 0.5e-6,
    headRA = 1.25,    #additional factor of 4 due to exptl higher than expected Ra Spine
    neckRA = 11.3,
    spineRM = 1.875,
    spineCM = 0.01,
    spineELEAK = -70e-3,
    spineEREST = -80e-3,
    spineStart = 26.1e-6,
    spineEnd = 300e-6,
    
    compensationSpineDensity = 0,
    spineChanList = [['CaL13'],['CaL12','CaR','CaT']],
    #spines added to branches that are childrne of this branch:
    spineParent = 'secdend11',
    #spineCond = [0.65 *cond for  param_cond.ghKluge],

)
