from __future__ import print_function, division
import numpy as np
import moose
import random
random.seed(1)

from . import logutil
from .util import distance_mapping
from .add_channel import addOneChan
log = logutil.Logger()

#NAME_NECK and NAME_HEAD are used in calcium.py to add calcium objects to spines
#If you get rid of them, you have to change calcium.py
NAME_NECK = "neck"
NAME_HEAD = "head"

def setSpineCompParams(model, comp,compdia,complen,RA,RM,CM):
    
    comp.diameter = compdia
    comp.length = complen
    
    XArea = np.pi*comp.diameter*comp.diameter/4
    
    circumf = np.pi*compdia
    log.debug('Xarea,circumf of {}, {}, {} CM {} {}',
              comp.path, XArea, circumf,
              CM*complen*circumf)
    comp.Ra = 4*RA*complen/XArea
    comp.Rm = RM/(complen*circumf)
    cm = CM*compdia*circumf
    if cm < 1e-15:
        cm = 1e-15
    comp.Cm = cm
    comp.Em = model.SpineParams.spineELEAK
    comp.initVm = model.SpineParams.spineEREST

def makeSpine(model, parentComp, compName,index,frac,SpineParams):
    #frac is where along the compartment the spine is attached
    #unfortunately, these values specified in the .p file are not accessible
    neck_path = '{}/{}{}{}'.format(parentComp.path, compName, index, NAME_NECK)
    neck = moose.Compartment(neck_path)
    log.debug('{} at {} x,y,z={2.x},{2.y},{2.z}', neck.path, frac, parentComp)
    moose.connect(parentComp,'raxial',neck,'axial','Single')
    x=parentComp.x0+ frac * (parentComp.x - parentComp.x0)
    y=parentComp.y0+ frac * (parentComp.y - parentComp.y0)
    z=parentComp.z0+ frac * (parentComp.z - parentComp.z0)
    neck.x0, neck.y0, neck.z0 = x, y, z
    #could pass in an angle and use cos and sin to set y and z
    neck.x, neck.y, neck.z = x, y + SpineParams.necklen, z
    setSpineCompParams(model, neck,SpineParams.neckdia,SpineParams.necklen,SpineParams.neckRA,SpineParams.spineRM,SpineParams.spineCM)

    head_path = '{}/{}{}{}'.format(parentComp.path, compName, index, NAME_HEAD)
    head = moose.Compartment(head_path)
    moose.connect(neck, 'raxial', head, 'axial', 'Single')
    head.x0, head.y0, head.z0 = neck.x, neck.y, neck.z
    head.x, head.y, head.z = head.x0, head.y0 + SpineParams.headlen, head.z0

    setSpineCompParams(model, head,SpineParams.headdia,SpineParams.headlen,SpineParams.headRA,SpineParams.spineRM,SpineParams.spineCM)

    return head, neck


def compensate_for_spines(comp,total_spine_surface,surface_area):
    old_Cm = comp.Cm
    old_Rm = comp.Rm
    scaling_factor = (surface_area+total_spine_surface)/surface_area
   
    comp.Cm = old_Cm/scaling_factor
    comp.Rm = old_Rm/scaling_factor
    
def spine_surface(SpineParams):
    headdia = SpineParams.headdia
    headlen = SpineParams.headlen
    neckdia = SpineParams.neckdia
    necklen = SpineParams.necklen
    surface = headdia*(headlen+headdia/4) + neckdia*necklen

    return surface*np.pi
    
def addSpines(model, container,ghkYN,name_soma):
    headarray=[]
    SpineParams = model.SpineParams
    suma = 0

    modelcond = model.Condset[container]
    
    single_spine_surface = spine_surface(SpineParams)
    print('Single spine surface ', single_spine_surface)
    for comp in moose.wildcardFind(container + '/#[TYPE=Compartment]'):
        if name_soma not in comp.path:
            numSpines = int(np.round(SpineParams.spineDensity*comp.length))
            if not numSpines:
                 rand = random.random()
                 if rand > SpineParams.spineDensity*comp.length:
                     numSpines = 1
                     suma += 1
            total_spine_surface = numSpines*single_spine_surface
            surface_area = comp.diameter*comp.length*np.pi
            compensate_for_spines(comp,total_spine_surface,surface_area)
            
            spineSpace = comp.length/(numSpines+1)
            for index in range(numSpines):
                frac = (index+0.5)/numSpines
                #print comp.path,"Spine:", index, "located:", frac
                head,neck = makeSpine(model, comp, 'sp',index, frac, SpineParams)
                compensate_for_spines(head,total_spine_surface,surface_area)
                compensate_for_spines(neck,total_spine_surface,surface_area)
                headarray.append(head)
                if SpineParams.spineChanList:
                    if ghkYN:
                        ghkproto=moose.element('/library/ghk')
                        ghk=moose.copy(ghkproto,comp,'ghk')[0]
                        moose.connect(ghk,'channel',comp,'channel')
                    chan_list = []
                    for c in SpineParams.spineChanList:
                        chan_list.extend(c)
                    for chanpath in chan_list:
                        cond = distance_mapping(modelcond[chanpath],head)
                        addOneChan(chanpath,cond,head,ghkYN)
            #end for index
    #end for comp
    
    log.info('{} spines created in {}', len(headarray), container)
    return headarray
