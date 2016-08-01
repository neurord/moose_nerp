#SpineParams.py
from spspine import param_cond
from spspine import util as _util

SpineParams = _util.NamedDict(
    'SpineParams',
    spineDensity = 0.1e6,      #should make this distance dependent
    necklen = 0.3e-6,          #define all these parameters elsewhere
    neckdia = 0.1e-6,
    headdia = 0.5e-6,
    spineRA = 4*4,    #additional factor of 4 due to exptl higher than expected Ra Spine
    spineRM = 2.8,
    spineCM = 0.01,
    spineELEAK = -50e-3,
    spineEREST = -80e-3,

    spineChanList = [], #['CaL13']
    spineCond = [0.1 * param_cond.ghKluge],

    ####These numbers are used with split to extract channel and compartment names
    spineNameNum = 3,
    spineChanNum = 4,
    #within SpineName, character 5 has spine number
    spineNumLoc = 5,
)
