from . import param_cond

from moose_nerp.prototypes import util as _util

SpineParams = _util.NamedDict(
    'SpineParams',
    spineDensity = 0.1e6,      #should make this distance dependent
    necklen = 0.3e-6,          #define all these parameters elsewhere
    neckdia = 0.1e-6,
    headdia = 0.5e-6,
    headlen = 0.5e-6,
    headRA = 1.25, 
    neckRA = 4*4,    #additional factor of 4 due to exptl higher than expected Ra Spine
    spineRM = 2.8,
    spineCM = 0.01,
    spineELEAK = -50e-3,
    spineEREST = -80e-3,
    spineStart = 26.1e-6,
    spineEnd = 300e-6,
    compensationSpineDensity = 0,
    #add spines to dendrites connected to /downstream of this branch. 
    spineParent = '31_4',
    spineChanList = [], #['CaL13']
   

)
