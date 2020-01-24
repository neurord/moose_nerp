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

'''The default behavior for spines is to assume no explicit spines and
compensate for the spineDensity parameter in initial model construction. This
file includes the compensation function, called in cellproto. Then, if any
explicit spines are to be included, reverse compensation is performed.
'''

def setSpineCompParams(model, comp,compdia,complen,RA,RM,CM):

    comp.diameter = compdia
    comp.length = complen

    XArea = np.pi*comp.diameter*comp.diameter/4

    circumf = np.pi*compdia
    log.debug('Xarea,circumf of {}, {}, {} CM {} {}',
              comp.path, XArea, circumf,
              CM,np.pi*comp.diameter*comp.length)
    comp.Ra = RA*comp.length/XArea
    comp.Rm = RM/(np.pi*comp.diameter*comp.length)
    cm = CM*np.pi*comp.diameter*comp.length
    if cm < 1e-15:
        cm = 1e-15
    comp.Cm = cm
    comp.Em = model.SpineParams.spineELEAK
    comp.initVm = model.SpineParams.spineEREST


def setPassiveSpineParams(model,container,name_soma):
    '''Sets the Spine Params for RM, CM, RA, from global values if NONE '''
    soma = moose.element(container+'/'+name_soma)
    if soma.length == 0:
         SA = np.pi*soma.diameter**2
         len_by_XA=1/(np.pi * soma.diameter/8) #eqn from Hendrickson & Jaeger 2010
    else:
        SA =np.pi * soma.diameter * soma.length
        len_by_XA=soma.length / (np.pi * soma.diameter * soma.diameter/4) #4 converts dia to radius
    globalRM = soma.Rm * SA
    globalCM = soma.Cm / SA
    globalRA = soma.Ra / len_by_XA
    globalELEAK = soma.Em
    globalEREST = soma.initVm
    if model.SpineParams.spineRM is None:
        model.SpineParams.spineRM = globalRM
        log.debug('Setting spineRM to globalRM = {}', globalRM)
    if model.SpineParams.spineCM is None:
        model.SpineParams.spineCM = globalCM
        log.debug('Setting spineCM to globalCM = {}', globalCM)
    if model.SpineParams.neckRA is None:
        model.SpineParams.neckRA = globalRA
        log.debug('Setting neckRA to globalRA = {}', globalRA)
    if model.SpineParams.headRA is None:
        model.SpineParams.headRA = globalRA
        log.debug('Setting headRA to globalRA = {}', globalRA)
    if model.SpineParams.spineELEAK is None:
        model.SpineParams.spineELEAK = globalELEAK
        log.debug('Setting spineELEAK to globalELEAK = {}', globalELEAK)
    if model.SpineParams.spineEREST is None:
        model.SpineParams.spineEREST = globalEREST
        log.debug('Setting spineEREST to globalEREST = {}', globalEREST)

def makeSpine(model, parentComp, compName,index,frac,SpineParams,randomAngles=True):
    #frac is where along the compartment the spine is attached
    #unfortunately, these values specified in the .p file are not accessible
    neck_path = '{}/{}{}{}'.format(parentComp.path, compName, index, NAME_NECK)
    neck = moose.Compartment(neck_path)
    log.debug('{} at {} x,y,z={},{},{}', neck.path, frac, parentComp.x, parentComp.y, parentComp.z)
    moose.connect(parentComp,'raxial',neck,'axial','Single')
    #evenly distribute the spines along the parent compartment
    x=parentComp.x0+ frac * (parentComp.x - parentComp.x0)
    y=parentComp.y0+ frac * (parentComp.y - parentComp.y0)
    z=parentComp.z0+ frac * (parentComp.z - parentComp.z0)
    neck.x0, neck.y0, neck.z0 = x, y, z
    from scipy.linalg import norm

    if randomAngles:
        # random angles for visualization
        dendvect = np.array([parentComp.x, parentComp.y, parentComp.z]) - np.array([parentComp.x0, parentComp.y0, parentComp.z0])
        dendvmag = norm(dendvect)
        dendunitvec = dendvect/dendvmag
        not_v = np.random.random(3)
        not_v /= norm(not_v)
        while (dendunitvec == not_v).all():
            not_v = np.random.random(3)
            not_v /= norm(not_v)
        #make vector perpendicular to v
        n1 = np.cross(dendunitvec, not_v)
        #normalize n1
        n1 /= norm(n1)
        neck.x, neck.y, neck.z = SpineParams.necklen*n1
        #print(neck.x, neck.y, neck.z)
    else:
        #could pass in an angle and use cos and sin to set y and z
        neck.x, neck.y, neck.z = x, y + SpineParams.necklen, z
    setSpineCompParams(model, neck,SpineParams.neckdia,SpineParams.necklen,SpineParams.neckRA,SpineParams.spineRM,SpineParams.spineCM)

    head_path = '{}/{}{}{}'.format(parentComp.path, compName, index, NAME_HEAD)
    head = moose.Compartment(head_path)
    moose.connect(neck, 'raxial', head, 'axial', 'Single')
    head.x0, head.y0, head.z0 = neck.x, neck.y, neck.z
    head.x, head.y, head.z = SpineParams.headlen*np.array([head.x0, head.y0, head.z0])/norm(np.array([head.x0, head.y0, head.z0]))
    #head.x0, head.y0 + SpineParams.headlen, head.z0

    setSpineCompParams(model, head,SpineParams.headdia,SpineParams.headlen,SpineParams.headRA,SpineParams.spineRM,SpineParams.spineCM)
    return head, neck


def compensate_for_spines(model,comp,name_soma):#,total_spine_surface,surface_area):
    setPassiveSpineParams(model,comp.parent.name,name_soma)
    SpineParams = model.SpineParams
    distance_mapped_spineDensity = {(SpineParams.spineStart,SpineParams.spineEnd):SpineParams.spineDensity}
    if SpineParams.spineDensity == 0:
        return
    if not compensate_for_spines.has_been_called:
        print('Compensating for spines using SpineParams.spineDensity = ' +
              str(SpineParams.spineDensity) +
              ' ; Set to zero skip spine compensation.' )
        compensate_for_spines.has_been_called = True
    dist = (comp.x**2+comp.y**2+comp.z**2)**0.5
    if name_soma not in comp.path and (SpineParams.spineEnd > dist > SpineParams.spineStart):
        #determine the number of spines
        spineDensity = distance_mapping(distance_mapped_spineDensity,comp)
        if spineDensity < 0 or spineDensity > 20e6:
            print('SpineDensity {} may be unrealistic; check function'.format(spineDensity))
        numSpines = int(np.round(spineDensity*comp.length))
        #print('Spine Density = ' + str(spineDensity), 'NumSpines={}'.format(numSpines))

        #if spine density is low (less than 1 per comp) use random number to determine whether to add a spine
        if not numSpines:
             rand = random.random()
             if rand > spineDensity*comp.length:
                 numSpines = 1
        #calculate total surface area of the added spines
        single_spine_surface = spine_surface(SpineParams)
        total_spine_surface = numSpines*single_spine_surface
        surface_area = comp.diameter*comp.length*np.pi

        ## Compensate RM and CM
        old_Cm = comp.Cm
        old_Rm = comp.Rm
        scaling_factor = (surface_area+total_spine_surface)/surface_area

        comp.Cm = old_Cm * scaling_factor
        comp.Rm = old_Rm / scaling_factor

        ## Additionally, compensate for ion channels in spines
        # Flatten the nested chan list:
        chan_list = []
        for c in SpineParams.spineChanList:
            chan_list.extend(c)
        # Get the conductance for each channel:
        for chanpath,mult in chan_list:
            if moose.exists(comp.path+'/'+chanpath):
                chan = moose.element(comp.path+'/'+chanpath)
                old_gbar = chan.Gbar/surface_area
                spine_dend_gbar_ratio = 1.0 #TODO: Change if spine has different gbar than dendrite
                gbar_factor = (surface_area + spine_dend_gbar_ratio*total_spine_surface)/surface_area
                new_gbar = old_gbar*gbar_factor
                chan.Gbar = new_gbar*surface_area
                #if 'CaR' in chan.path and 'tertdend1_2' in chan.path:
                #    print('Compensating ' + chan.path + ' from old gbar: ' + str(old_gbar) + ' to new: ' + str(new_gbar))
#Initialize function attribute:
compensate_for_spines.has_been_called = False

def reverse_compensate_for_explicit_spines(model,comp,explicit_spine_surface,surface_area):
    old_Cm = comp.Cm
    old_Rm = comp.Rm
    scaling_factor = (surface_area+explicit_spine_surface)/surface_area

    comp.Cm = old_Cm / scaling_factor # Note, opposite signs from spine compensation
    comp.Rm = old_Rm * scaling_factor
    ## Additionally, reverse compensate for ion channels in spines
    # Flatten the nested chan list:
    SpineParams = model.SpineParams
    chan_list = []
    for c in SpineParams.spineChanList:
        chan_list.extend(c)
    # Get the conductance for each channel:
    for chanpath,mult in chan_list:
        if moose.exists(comp.path+'/'+chanpath):
            chan = moose.element(comp.path+'/'+chanpath)
            old_gbar = chan.Gbar/surface_area
            spine_dend_gbar_ratio = 1.0 #TODO: Change if spine has different gbar than dendrite
            gbar_factor = (surface_area + spine_dend_gbar_ratio*explicit_spine_surface)/surface_area
            new_gbar = old_gbar/gbar_factor
            chan.Gbar = new_gbar*surface_area
            #if 'CaR' in chan.path and 'tertdend1_2' in chan.path:
            #    print('Reverse Compensating ' + chan.path + ' from old gbar: ' + str(old_gbar) + ' to new: ' + str(new_gbar))


def spine_surface(SpineParams):
    headdia = SpineParams.headdia
    headlen = SpineParams.headlen
    neckdia = SpineParams.neckdia
    necklen = SpineParams.necklen
    surface = headdia*headlen + neckdia*necklen

    return surface*np.pi

def getChildren(parentname,childrenlist):

    children = moose.element(parentname).neighbors['axialOut']
    if len(children):
        for child in children:
            childrenlist.append(child.name)
            getChildren(child,childrenlist)

def addSpines(model, container,ghkYN,name_soma,module=None):
    distance_mapped_spineDensity = {(model.SpineParams.spineStart,model.SpineParams.spineEnd):model.SpineParams.spineDensity}
    headarray=[]
    # Sets Spine Params to global values for RM, CM, etc. if value is None:
    setPassiveSpineParams(model,container,name_soma)
    SpineParams = model.SpineParams
    suma = 0

    modelcond = model.Condset[container]
    single_spine_surface = spine_surface(SpineParams)

    parentComp = container+'/'+SpineParams.spineParent
    print('Adding spines to parent: ' + parentComp)
    if not moose.exists(parentComp):
        raise Exception(parentComp + ' Does not exist in Moose model!')
    compList = [SpineParams.spineParent]
    getChildren(parentComp,compList)

    for comp in moose.wildcardFind(container + '/#[TYPE=Compartment]'):
        dist = (comp.x**2+comp.y**2+comp.z**2)**0.5
        if name_soma not in comp.path and comp.name in compList and (SpineParams.spineEnd > dist > SpineParams.spineStart):
            #determine the number of spines
            try:
                #If SpineParams has this, use this density
                density=SpineParams.explicitSpineDensity
            except KeyError:
                #Else, just use the actual density value
                density=distance_mapping(distance_mapped_spineDensity,comp)
            numSpines = int(np.round(density*comp.length))

            #if spine density is low (less than 1 per comp) use random number to determine whether to add a spine
            if not numSpines:
                 rand = random.random()
                 if rand > density*comp.length:
                     numSpines = 1
                     suma += 1
            #calculate total surface area of the added spines
            total_spine_surface = numSpines*single_spine_surface
            surface_area = comp.diameter*comp.length*np.pi

            # if SpineParams.compensationSpineDensity:
            #     compensation_spine_surface = int(np.round(SpineParams.compensationSpineDensity*comp.length))*single_spine_surface
            #     decompensate_compensate_for_spines(comp,total_spine_surface,surface_area,compensation_spine_surface)
            # else:
            #increase resistance according to the spines that should be there but aren't
            reverse_compensate_for_explicit_spines(model,comp,total_spine_surface,surface_area)

            #spineSpace = comp.length/(numSpines+1)
            #for each spine, make a spine and possibly compensate for its surface area
            for index in range(numSpines):
                frac = (index+0.5)/numSpines
                #print comp.path,"Spine:", index, "located:", frac
                head,neck = makeSpine(model, comp, 'sp',index, frac, SpineParams)
                headarray.append(head)
                if SpineParams.spineChanList:
                    if ghkYN:
                        ghkproto=moose.element('/library/ghk')
                        ghk=moose.copy(ghkproto,comp,'ghk')[0]
                        moose.connect(ghk,'channel',comp,'channel')
                    chan_list = []
                    for c in SpineParams.spineChanList:
                        chan_list.extend(c)
                    for chanpath,mult in chan_list:
                        cond = mult*distance_mapping(modelcond[chanpath],head)
                        if cond > 0:
                            log.debug('Testing Cond If {} {}', chanpath, cond)
                            calciumPermeable = model.Channels[chanpath].calciumPermeable
                            addOneChan(chanpath,cond,head,ghkYN,calciumPermeable=calciumPermeable,module=module)
            #end for index
    #end for comp

    log.info('{} spines created in {}', len(headarray), container)
    return headarray
