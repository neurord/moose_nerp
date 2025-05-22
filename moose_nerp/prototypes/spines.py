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

from scipy.linalg import norm

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
        chan_dict = {}
        for c in SpineParams.spineChanList:
            chan_dict.update(c)
        # Get the conductance for each channel:
        for chanpath,mult in chan_dict.items():
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
    chan_dict = {}
    for c in SpineParams.spineChanList:
        chan_dict.update(c)
    # Get the conductance for each channel:
    for chanpath,mult in chan_dict.items():
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

def spine_channels(model,SpParams,ghkYN,head,module=None):
    if SpParams.spineChanList:
        if ghkYN:
            ghkproto=moose.element('/library/ghk')
            ghk=moose.copy(ghkproto,head,'ghk')[0]
            moose.connect(ghk,'channel',head,'channel')
        chan_dict = {}
        for c in SpParams.spineChanList:
            chan_dict.update(c)
        for chanpath,mult in chan_dict.items():
            cond = mult#*distance_mapping(modelcond[chanpath],head)
            if cond > 0:
                log.debug('Testing Cond If {} {}', chanpath, cond)
                calciumPermeable = model.Channels[chanpath].calciumPermeable
                addOneChan(chanpath,cond,head,ghkYN,calciumPermeable=calciumPermeable,module=module)

def addSpines(model, container,ghkYN,name_soma,neuron_object,module=None):
    distance_mapped_spineDensity = {(model.SpineParams.spineStart,model.SpineParams.spineEnd):model.SpineParams.spineDensity}
    headarray=[]
    # Sets Spine Params to global values for RM, CM, etc. if value is None:
    setPassiveSpineParams(model,container,name_soma)
    SpineParams = model.SpineParams
    suma = 0

    modelcond = model.Condset[container]
    single_spine_surface = spine_surface(SpineParams)

    # if clustering spines, call those functions here and return early
    if "ClusteringParams" in SpineParams:
        possible_spines = getPossibleSpines(model, container,ghkYN,name_soma)
        spine_to_spine_dists = possible_spine_to_spine_distances(model, possible_spines,neuron_object)
        chosen_spine_clusters,chosen_spines_in_each_cluster,clustered_spine_index = choose_spine_clusters(model, possible_spines, spine_to_spine_dists,SpineParams.ClusteringParams['n_clusters'], SpineParams.ClusteringParams['cluster_length'], SpineParams.ClusteringParams['n_spines_per_cluster'])
        all_possible_spine_info={ps['head_path']:(ps['x'],ps['y'],ps['z']) for ps in possible_spines} #maybe this should be ordered list?
        if len(spine_to_spine_dists)==len(possible_spines)+1:
            soma = moose.element(container+'/'+name_soma)
            print('adding index for soma to s2sd',soma.path)
            all_possible_spine_info[soma.path]=(0,0,0) #add soma
        added_spines={sp:[possible_spines[x]['head_path'] for x in chosen_spines_in_each_cluster[i]] for i,sp in enumerate(chosen_spine_clusters)}
        for sp in clustered_spine_index:
            head =add_one_spine_from_spine_info(possible_spines[sp],model,SpineParams,container,ghkYN,name_soma)
            #print('test adding one spine of cluster')
            headarray.append(head)
        print('prep for auto file name',model.morph_file, container,len(headarray),'spines created')
        fname=model.morph_file[container].split('.p')[0] #container is ntype
        np.savez(fname+'_s2sdist', s2sd=spine_to_spine_dists,index=all_possible_spine_info) #needed for analysis later.  Probably need to save in different directory
        return headarray
    else:
        parentComp = container+'/'+SpineParams.spineParent
        print('Adding spines to parent: ' + parentComp)
        if not moose.exists(parentComp):
            raise Exception(parentComp + ' Does not exist in Moose model!')
        compList = [SpineParams.spineParent]
        getChildren(parentComp,compList)
        possible_spine_list = [] # Collect every potential spine with info needed to make that spine in another function.
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
                    spine_channels(model,SpineParams,ghkYN,head,module=module)
                    spineInfo = makeSpineInfo(model, comp, 'sp',index, frac, SpineParams)
                    possible_spine_list.append(spineInfo)
                #end for index
        #end for comp
        spine_to_spine_dists = possible_spine_to_spine_distances(model, possible_spine_list,neuron_object)
        all_possible_spine_info={ps['head_path']:(ps['x'],ps['y'],ps['z']) for ps in possible_spine_list}
        print('prep for auto file name',model.morph_file, container,len(headarray),'spines created')
        fname=model.morph_file[container].split('.p')[0] #container is ntype
        np.savez(fname+'_s2sdist', s2sd=spine_to_spine_dists,index=all_possible_spine_info) #needed for analysis later.  Probably need to save in different directory

        log.info('{} spines created in {}', len(headarray), container)
        return headarray

def getPossibleSpines(model, container,ghkYN,name_soma):
    possible_spine_list = [] # Collect every potential spine with info needed to make that spine in another function.
        
    distance_mapped_spineDensity = {(model.SpineParams.spineStart,model.SpineParams.spineEnd):model.SpineParams.spineDensity}
    SpineParams = model.SpineParams
    suma = 0
    parentComp = container+'/'+SpineParams.spineParent
    print('Adding spines to parent: ' + parentComp)
    if not moose.exists(parentComp):
        raise Exception(parentComp + ' Does not exist in Moose model!')
    compList = [SpineParams.spineParent]
    getChildren(parentComp,compList)

    for comp in moose.wildcardFind(container + '/#[ISA=CompartmentBase]'):
        #print(comp)
        dist = (comp.x**2+comp.y**2+comp.z**2)**0.5
        if name_soma not in comp.path and comp.name in compList and (SpineParams.spineEnd > dist > SpineParams.spineStart):
            #determine the number of possible spines using distance mapped density
            density=distance_mapping(distance_mapped_spineDensity,comp)
            numSpines = int(np.round(density*comp.length))

            #if spine density is low (less than 1 per comp) use random number to determine whether to add a spine
            if not numSpines:
                 rand = random.random()
                 if rand > density*comp.length:
                     numSpines = 1
                     suma += 1
            #calculate total surface area of the added spines
            #total_spine_surface = numSpines*single_spine_surface
            #surface_area = comp.diameter*comp.length*np.pi

            # if SpineParams.compensationSpineDensity:
            #     compensation_spine_surface = int(np.round(SpineParams.compensationSpineDensity*comp.length))*single_spine_surface
            #     decompensate_compensate_for_spines(comp,total_spine_surface,surface_area,compensation_spine_surface)
            # else:
            #increase resistance according to the spines that should be there but aren't
            
            ### Do this when actually adding the spines
            #reverse_compensate_for_explicit_spines(model,comp,total_spine_surface,surface_area)

            #spineSpace = comp.length/(numSpines+1)
            #for each spine, make a spine and possibly compensate for its surface area
            for index in range(numSpines):
                frac = (index+0.5)/numSpines
                #print comp.path,"Spine:", index, "located:", frac
                #head,neck = makeSpine(model, comp, 'sp',index, frac, SpineParams)
                spineInfo = makeSpineInfo(model, comp, 'sp',index, frac, SpineParams)
                #headarray.append(head)
                possible_spine_list.append(spineInfo)
            #end for index
    #end for comp

    #log.info('{} spines created in {}', len(headarray), container)
    #return headarray
    return possible_spine_list

def makeSpineInfo(model, parentComp, compName,index,frac,SpineParams,randomAngles=True):
    #print('making spine info')
    spine_info = {}
    spine_info['parentComp'] = parentComp
    spine_info['compName']= compName

    #frac is where along the compartment the spine is attached
    #unfortunately, these values specified in the .p file are not accessible
    neck_path = '{}/{}{}{}'.format(parentComp.path, compName, index, NAME_NECK)
    spine_info['neck_path'] = neck_path
    #neck = moose.Compartment(neck_path)
    #log.debug('{} at {} x,y,z={},{},{}', neck.path, frac, parentComp.x, parentComp.y, parentComp.z)
    #moose.connect(parentComp,'raxial',neck,'axial','Single')
    #evenly distribute the spines along the parent compartment
    x=parentComp.x0+ frac * (parentComp.x - parentComp.x0)
    y=parentComp.y0+ frac * (parentComp.y - parentComp.y0)
    z=parentComp.z0+ frac * (parentComp.z - parentComp.z0)
    spine_info['x'] = x
    spine_info['y'] = y
    spine_info['z'] = z
    #neck.x0, neck.y0, neck.z0 = x, y, z
    #setSpineCompParams(model, neck,SpineParams.neckdia,SpineParams.necklen,SpineParams.neckRA,SpineParams.spineRM,SpineParams.spineCM)

    head_path = '{}/{}{}{}'.format(parentComp.path, compName, index, NAME_HEAD)
    spine_info['head_path'] = head_path
    #head = moose.Compartment(head_path)
    #moose.connect(neck, 'raxial', head, 'axial', 'Single')
    #head.x0, head.y0, head.z0 = neck.x, neck.y, neck.z
    #head.x, head.y, head.z = SpineParams.headlen*np.array([head.x0, head.y0, head.z0])/norm(np.array([head.x0, head.y0, head.z0]))
    #head.x0, head.y0 + SpineParams.headlen, head.z0

    #setSpineCompParams(model, head,SpineParams.headdia,SpineParams.headlen,SpineParams.headRA,SpineParams.spineRM,SpineParams.spineCM)
    return spine_info #head, neck

def possible_spine_to_spine_distances(model, possible_spines,neuron_object):
    from moose_nerp.prototypes import spatiotemporalInputMapping as stim
    neuron = neuron_object#list(model.neurons.values())[0][0]
    bd = stim.getBranchDict(neuron)
    comp_to_branch_dict = stim.mapCompartmentToBranch(neuron)
    
    def compute_spine_to_spine_dist(spine, other_spine,print_info=False):
        '''Compute the path distance along dendritic tree between any two spines'''
        # get parent compartment of spine
        spine_parents = [spine['parentComp'], other_spine['parentComp']]

        # get the branch of the spine_parent
        spine_branches = [comp_to_branch_dict[sp.path] for sp in spine_parents]
        branch_paths = spine_branches[0]['BranchPath'], spine_branches[1]['BranchPath']
        # if on same branch
        if spine_branches[0]==spine_branches[1]:
            # if on same compartment:
            if spine_parents[0]==spine_parents[1]:
                spine_to_spine_dist = np.sqrt((spine['x'] - other_spine['x'])**2 + (spine['y'] - other_spine['y'])**2 + (spine['z'] - other_spine['z'])**2)
            # else if on same branch but not same compartment:
            else:
                compdistances = [bd[sb['Branch']]['CompDistances'] for sb in spine_branches]
                complists = [bd[sb['Branch']]['CompList'] for sb in spine_branches]
                compindexes = [cl.index(spine_parent.path) for cl,spine_parent in zip(complists, spine_parents)]
                comp_to_comp_distance = np.abs(compdistances[0][compindexes[0]] - compdistances[1][compindexes[1]])
                spine_to_spine_dist = comp_to_comp_distance
        # else if on different branches, find common parent branch first
        else:
            for a,b in zip(branch_paths[0], branch_paths[1]):
                #print(a,b)
                if a == b:
                    common_parent = a
            common_parent_distance = bd[common_parent]['CompDistances'][0]
            if print_info:
                print('common parent is ', common_parent, 'common_parent_distance is ', common_parent_distance)
            allcompdistances = [bd[sb['Branch']]['CompDistances'] for sb in spine_branches]
            complists = [bd[sb['Branch']]['CompList'] for sb in spine_branches]
            compindexes = [cl.index(spine_parent.path) for cl,spine_parent in zip(complists, spine_parents)]
            compdistances = [allcompdistances[0][compindexes[0]], allcompdistances[1][compindexes[1]]]
            comp_to_comp_distance = (compdistances[0]-common_parent_distance) + (compdistances[1]-common_parent_distance)
            if print_info:
                print('compdistances',compdistances,'comp_to_comp_distance', comp_to_comp_distance)
            spine_to_spine_dist = comp_to_comp_distance
        return spine_to_spine_dist
    

    spine_to_spine_dist_array = np.zeros((len(possible_spines)+1, len(possible_spines)+1)) #+1 for adding spine to soma distance
    spine_index=[]
    import itertools
    for spine_pairs in itertools.combinations(range(len(possible_spines)), 2):
        spine_dist = compute_spine_to_spine_dist(possible_spines[spine_pairs[0]],possible_spines[spine_pairs[1]])
        spine_to_spine_dist_array[spine_pairs[0], spine_pairs[1]] = spine_dist
        spine_to_spine_dist_array[spine_pairs[1], spine_pairs[0]] = spine_dist
    missing=[]
    for spnum,spine in enumerate(possible_spines):
        spine_parent=spine['parentComp']
        if spine_parent.path in comp_to_branch_dict.keys():
            spine_branch = comp_to_branch_dict[spine_parent.path]
            allcompdistances = bd[spine_branch['Branch']]['CompDistances']
            complist = bd[spine_branch['Branch']]['CompList']
            compindex = complist.index(spine_parent.path)
            spine_to_spine_dist_array[spnum,-1]=allcompdistances[compindex]
            spine_to_spine_dist_array[-1,spnum]=allcompdistances[compindex]
        else:
            if spine_parent.path not in missing:
                missing.append(spine_parent.path)
            #print('spine',spine.path,'parent comp not in comp_to_branch_dict', comp_to_branch_dict.keys())
    if len(missing):
        print('these comps not in comp_to_branch_dict',missing)

    return spine_to_spine_dist_array

def choose_spine_clusters(model, possible_spines, spine_to_spine_dist_array, n_clusters, cluster_length, n_spines_per_cluster):
    # randomly choose n_clusters spines from possible spines
    # ensure the randomly chosen spines for each different cluster are well distributed 
    chosen_spine_clusters = []
    possible_spine_index = list(range(len(possible_spines)))
    for i in range(n_clusters):
        validated_spine = False
        failures=0
        while not validated_spine:
            chosen_spine = np.random.choice(possible_spine_index,1)
            possible_spine_index.remove(chosen_spine)
            # make sure at least n_spines_per_cluster within cluster_length of chosen spine
            num_spines_within_length = np.argwhere(spine_to_spine_dist_array[chosen_spine, :]<cluster_length).shape[0]
            if num_spines_within_length < n_spines_per_cluster:
                print('too few spines nearby for cluster choose again')
                continue
            # Check if chosen spine is at least 3xcluster_length distance from all other clusters
            if all(spine_to_spine_dist_array[chosen_spine, chosen_spine_clusters] > 3*cluster_length):
                chosen_spine_clusters.append(chosen_spine[0])
                validated_spine = True
                print('chosen spine cluster length ', len(chosen_spine_clusters)) 
            else:
                failures+=1
        print('cluster',i,'too close to other spines in cluster choosing again', failures,'times')
    
    # Now randomly choose n_spines_percluster within cluster_length of each cluster
    chosen_spines_in_each_cluster = []
    for i in range(n_clusters):
        origin_spine = chosen_spine_clusters[i]
        choices = np.random.choice(np.where(
            (spine_to_spine_dist_array[origin_spine,:]<cluster_length) &
            (spine_to_spine_dist_array[origin_spine,:]>0))[0],
            size=n_spines_per_cluster-1, replace=False)
        choices = list(choices)
        choices.append(origin_spine)
        chosen_spines_in_each_cluster.append(choices)
    
    all_chosen_spines = [s for clus in chosen_spines_in_each_cluster for s in clus]
    return chosen_spine_clusters,chosen_spines_in_each_cluster,all_chosen_spines

def add_one_spine_from_spine_info(spine_info, model,SpineParams,container,ghkYN,name_soma):
    compName = spine_info['compName']
    neck_path = spine_info['neck_path']
    parentComp = spine_info['parentComp']
    neck = moose.Compartment(neck_path)
    #log.debug('{} at {} x,y,z={},{},{}', neck.path, frac, parentComp.x, parentComp.y, parentComp.z)
    moose.connect(parentComp,'raxial',neck,'axial','Single')
    neck.x0, neck.y0, neck.z0 = spine_info['x'], spine_info['y'], spine_info['z']
    neck.x, neck.y, neck.z = neck.x0, neck.y0 + SpineParams.necklen, neck.z0
    setSpineCompParams(model, neck,SpineParams.neckdia,SpineParams.necklen,SpineParams.neckRA,SpineParams.spineRM,SpineParams.spineCM)
    head_path = spine_info['head_path']
    head = moose.Compartment(head_path)
    moose.connect(neck, 'raxial', head, 'axial', 'Single')
    head.x0, head.y0, head.z0 = neck.x, neck.y, neck.z
    head.x, head.y, head.z = SpineParams.headlen*np.array([head.x0, head.y0, head.z0])/norm(np.array([head.x0, head.y0, head.z0]))

    setSpineCompParams(model, head,SpineParams.headdia,SpineParams.headlen,SpineParams.headRA,SpineParams.spineRM,SpineParams.spineCM)

    surface_area = parentComp.diameter*parentComp.length*np.pi
    reverse_compensate_for_explicit_spines(model,parentComp,spine_surface(SpineParams),surface_area)
    # add channel code for single spine here
    spine_channels(model,SpineParams,ghkYN,head)
    return head
