from __future__ import division as _, print_function as _
import sys as _sys
import os as _os
import numbers as _numbers
from collections import OrderedDict as _OrderedDict
from operator import itemgetter as _itemgetter, eq as _eq
import numpy as _np
import functools
import moose
from subprocess import check_output

def syn_name(synpath,headname):
    if headname in synpath:
        #try to strip out name of cell from branch name
        headpath=moose.element(synpath).parent.path
        parentname=moose.element(headpath).parent.name
        postbranch=parentname+'/'+moose.element(headpath).name
    else:
        postbranch=moose.element(synpath).parent.name

    return postbranch

def select_neuron(neuron):
    if isinstance(neuron,list) or isinstance(neuron,_np.ndarray) or isinstance(neuron,moose.vec):
        neur=neuron[0]
    else:
        neur=neuron
    return neur 

def select_branch(parent):
    if int(moose.__version__[0])>3:
        branch_list = ["/D1[0]/{}".format(parent)]
    else:
        branch_list = ["/D1[0]/{}[0]".format(parent)]
    return branch_list 

def neurontypes(param_cond,override=None):
    "Query or set names of neurontypes of each neurons to be created"
    if override is None:
        return param_cond.neurontypes if param_cond.neurontypes is not None else sorted(param_cond.Condset.keys())
    else:
        if any(key not in param_cond.Condset.keys() for key in override):
            raise ValueError('unknown neuron types requested')
        return override

def inclusive_range(start, stop=None, step=None):
    if stop is None:
        stop = start
    if stop == start:
        return _np.array([start])
    if step is None:
        step = stop - start
    return _np.arange(start, stop + step/2, step)

def get_dist_name(comp,soma_loc=[0,0,0]):
    name = comp.name
    xloc = comp.x-soma_loc[0]
    yloc = comp.y-soma_loc[1]
    zloc = comp.z-soma_loc[2]
    dist = _np.sqrt(xloc*xloc+yloc*yloc+zloc*zloc)
    return dist,name

def move_neuron(dx,dy,dz,neurpath):
    for comp in moose.wildcardFind(neurpath+'/##[ISA=Compartment]'):
        comp.x=comp.x+dx
        comp.x0=comp.x0+dx
        comp.y=comp.y+dy
        comp.y0=comp.y0+dy
        comp.z=comp.z0+dz
        comp.z0=comp.z0+dz
    return

class dist_dependent_cond_equation:
    def __init__(self,cmin,cmax,dhalf,slope):
        self.cmin = cmin
        self.cmax = cmax
        self.dhalf = dhalf
        self.slope = slope
        self.__repr__()
    def __call__(self,distance):
            return self.cmin+(self.cmax-self.cmin)/(1+_np.exp((distance-self.dhalf)/self.slope))

    def __repr__(self):
        return '{}+({}-{})/(1+np.exp((distance-{})/{})))'.format(self.cmin,self.cmax,self.cmin,self.dhalf,self.slope)

"""
def dist_dependent_cond_equation(cmin, cmax, dhalf, slope):
    '''Returns a function only of distance that specifies a distance
    dependent sigmoid equation for channel conductance.

    cmin: minimal distance-dependent conductance
    cmax: maximal distant-dependent conductance
    dhalf: distance from soma where amplitude of sigmoid is one half max-min
    slope: slope of sigmoid equation. If positive, somatic conductance is higher; If negative, somatic conductance is smaller
    '''

    def equation(distance):
        return cmin+(cmax-cmin)/(1+_np.exp((distance-dhalf)/slope))

    print('{}+({}-{})/(1+np.exp((distance-{})/{})))'.format(cmin,cmax,cmin,dhalf,slope))
    return equation

"""
def distance_mapping(mapping, where):
    #where is a location, either a compartment or string or moose.vec
    if where.className=='Compartment' or where.className=='ZombieCompartment':
        comp=where
    elif isinstance(where,moose.vec):
        #Needs to be tested.  May need to loop over comps in moose.vec
        comp = moose.element(where)
    elif isinstance(where,str):
        try:
            comp =  moose.element(where)
        except ValueError:
            print('No element ',where)
            return 0
    elif isinstance(where, _numbers.Number):
        name = ''
        dist = where
    else:
        print('Wrong distance/element passed in distance mapping ',where)
        return 0
    #calculate distance of compartment from soma
    if where.className=='Compartment' or where.className=='ZombieCompartment':
        dist,name = get_dist_name(where)

    from collections import OrderedDict as od
    ordered_map=od(sorted(mapping.items(),key=lambda x:len(x[0]),reverse=True))
    result=None
    for k, value in ordered_map.items():
        #print('k,v',k,value)
        if len(k) == 3:
            min_dist, max_dist, description = k
        elif len(k) == 2:
            min_dist, max_dist = k
            description=''
        else:
            continue
        if min_dist <= dist < max_dist:
            if description:
                #name.startswith allows using swc files with _1 as soma, _2 as apical dend, _3 as basal dend and _4 as axon
                if name.startswith(description) or name.endswith(description):
                    result = value
                    break
            else:
                result = value
                break
    #print('##########', comp.name,'at',dist,'=',result)
    if not result:
        return 0

    if isinstance(result, _numbers.Number):
        return result
    elif isinstance(result, list):
        return result
    elif isinstance(result, dict): #Used for calcium buffer and pump dictionaries
        return result
    #otherwise, calculate distance dependent function.
    return result(dist)

try:
    from __builtin__ import execfile
except ImportError:
    def execfile(fn):
        exec(compile(open(fn).read(), fn, 'exec'))

def _itemsetter(index):
    def helper(where, value):
        where[index] = value
    return helper

_class_template = '''\
class {typename}(list):
    '{typename}({arg_list})'

    __slots__ = ()

    def __init__(self, {init_args}):
        'Create new instance of {typename}({arg_list})'
        return _list.__init__(self, ({arg_list}))

    def __repr__(self):
        'Return a nicely formatted representation string'
        return '{typename}({repr_fmt})' % tuple(self)

{field_defs}
'''

_repr_template = '{name}=%r'

_field_template = '''\
    {name} = _property(_itemgetter({index:d}), _itemsetter({index:d}),
                       doc='Alias for field number {index:d}')
'''

def NamedList(typename, field_names, verbose=False):
    "Returns a new subclass of list with named fields."

    # Validate the field names.
    init_args = field_names.replace(',', ' ').split()
    field_names = [name.partition('=')[0] for name in init_args]
    if sorted(set(field_names)) != sorted(field_names):
        raise ValueError('Duplicate field names')

    # Fill-in the class template
    class_definition = _class_template.format(
        typename = typename,
        num_fields = len(field_names),
        init_args = ', '.join(init_args),
        arg_list = ', '.join(field_names),
        repr_fmt = ', '.join(_repr_template.format(name=name)
                             for name in field_names),
        field_defs = '\n'.join(_field_template.format(index=index, name=name)
                               for index, name in enumerate(field_names))
    )
    if verbose:
        print(class_definition)

    # Execute the template string in a temporary namespace and support
    # tracing utilities by setting a value for frame.f_globals['__name__']
    namespace = dict(_itemgetter=_itemgetter, _itemsetter=_itemsetter,
                     __name__='NamedList_%s' % typename,
                     OrderedDict=_OrderedDict, _property=property, _list=list)
    exec(class_definition, namespace)
    result = namespace[typename]

    # For pickling to work, the __module__ variable needs to be set to the frame
    # where the named tuple is created.  Bypass this step in enviroments where
    # sys._getframe is not defined (Jython for example) or sys._getframe is not
    # defined for arguments greater than 0 (IronPython).
    try:
        result.__module__ = _sys._getframe(1).f_globals.get('__name__', '__main__')
    except (AttributeError, ValueError):
        pass

    return result

class NamedDict(dict):
    """Creates a python dict with a name and attribute access of keys.

    Usage: mydict = NamedDict(name,**kwargs)
    where **kwargs are used to create dictionary key/value pairs.
    e.g.: params = NamedDict('modelParams',x=15,y=0)

    dict keys can be accessed and written as keys or attributes:
        myNamedDict['k'] is equivalent to myNamedDict.k, and
        myNamedDict['k'] = newvalue is equivalent to myNamedDict.k=newvalue.

    New entries/attributes can be created:
        myNamedDict.newkey = newvalue OR myNamedDict['newkey']= newvalue.

    Note: Dict ignores attributes beginning with underscore, so
    myNamedDict.__name__ returns the NamedDict name, but there is no dict key
    == "__name__"

    Note: all dict keys must be valid attribute names: that is, strings with
    first character in a-z/A-Z. This could be changed to allow all valid python
    dict keys as keys, but these keys would not have attribute access.

    """

    def __init__(self, name, **kwargs):
        super(NamedDict, self).__init__(**kwargs)
        self.__dict__ = dict(**kwargs)
        self.__name__ = name

    def __repr__(self):
        items = ('{}={}'.format(k,v) for (k,v) in self.items())
        l = len(self.__name__) + 1
        sep = ',\n' + ' '*l
        return '{}({})'.format(self.__name__, sep.join(items))

    def __setitem__(self, k, v):
        super(NamedDict, self).__setitem__(k,v)
        setattr(self,k,v)

    def __getattribute__(self, k):
        # attributes have higher priority
        try:
            return super(NamedDict, self).__getattribute__(k)
        except AttributeError:
            return super(NamedDict, self).__getitem__(k)

    def __setattr__(self, k, v):
        super(NamedDict, self).__setattr__(k,v)
        if not k.startswith('_'):
            super(NamedDict, self).__setitem__(k,v)

    def __dir__(self):
        dirlist = super(NamedDict, self).__dir__()
        return dirlist


def block_if_noninteractive():
    if not any([hasattr(_sys, 'ps1'), _sys.flags.interactive]):
        print('Simulation finished. Close all windows or press ^C to exit.')
        import matplotlib.pyplot as plt
        try:
            plt.show(block=True)
        except KeyboardInterrupt:
            pass

def find_file(name, *paths):
    if not _os.path.isabs(name):
        for path in paths:
            p = _os.path.join(path, name)
            if _os.path.exists(p):
                return p
    return name

def find_model_file(model, name):
    return find_file(name, _os.path.dirname(model.__file__))

def listize(func):
    def wrapper(*args, **kwargs):
        return list(func(*args, **kwargs))
    return functools.update_wrapper(wrapper, func)


def call_counter(func):
    '''Decorator to count number of times a function has been called'''
    def wrapper(*args,**kwargs):
        try:
            wrapper.calls += 1
            return func(*args,**kwargs)
        except Exception as E: # Fixes count if there's an exception
            wrapper.calls += -1
            raise E
            return func(*args,**kwargs)
    wrapper.calls = 0
    return functools.update_wrapper(wrapper, func)


def gitlog(model):
    '''Log current git commit hash and any uncommitted differences of model

    For computational reproducibility, logging the git commit hash plus any
    uncomitted changes of currently checked out branch almost allows reproducing
    any result.

    Need to also know any command line arguments or optional kwargs passed to
    model at setup.
    '''
    enc = _sys.stdout.encoding
    modelpath = model.__path__[0]
    gitRepoPath = check_output(['git', '-C', modelpath, 'rev-parse',
                                '--show-toplevel']).decode(enc).rstrip()
    gitCurrentCommitHash = check_output(['git', '-C', gitRepoPath, 'rev-parse',
                                         'HEAD']).decode(enc).rstrip()
    gitUnstagedDiff = check_output(['git', '-C', gitRepoPath, 'diff-index',
                                    '-p', 'HEAD', '--']).decode(enc)
    gitStagedDiff = check_output(['git', '-C', gitRepoPath, 'diff-index', '-p',
                                  '--cached', 'HEAD', '--']).decode(enc)

    #print(gitRepoPath, gitCurrentCommitHash, gitUnstagedDiff, gitStagedDiff)
    return '\n'.join(['Git Repo Path of model: '+gitRepoPath + '\n',
                      'Current Git Commit Hash: '+gitCurrentCommitHash + '\n',
                      'Unstaged Git Differences: \n' + gitUnstagedDiff +'\n',
                      'Staged Git Differences: \n' + gitStagedDiff])
