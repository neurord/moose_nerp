from __future__ import division as _, print_function as _
import sys as _sys
import os as _os
import numbers as _numbers
from collections import OrderedDict as _OrderedDict
from operator import itemgetter as _itemgetter, eq as _eq
import numpy as _np
import functools
import moose

def syn_name(synpath,headname):
    if headname in synpath:
        #try to strip out name of cell from branch name
        headpath=moose.element(synpath).parent.path
        parentname=moose.element(headpath).parent.name
        postbranch=parentname+moose.element(headpath).name
    else:
        postbranch=moose.element(synpath).parent.name
    return postbranch
    
def inclusive_range(start, stop=None, step=None):
    if stop is None:
        stop = start
    if stop == start:
        return _np.array([start])
    if step is None:
        step = stop - start
    return _np.arange(start, stop + step/2, step)

def get_dist_name(comp):
    name = comp.name
    xloc = comp.x
    yloc = comp.y
    dist = _np.sqrt(xloc*xloc+yloc*yloc)
    return dist,name

def distance_mapping(mapping, where):
    # We assume that the dictionary is very small, so a linear search is OK.
   
    if isinstance(where, (moose.Compartment, moose.ZombieCompartment)):
        dist,name = get_dist_name(where)
        
    elif isinstance(where,moose.vec):
        comp = moose.element(where)
        if isinstance(comp, (moose.Compartment, moose.ZombieCompartment)):
            dist,name = get_dist_name(comp)
        else:
            print('Wrong element class ',dist)
            return 0

    elif isinstance(where,str):
        try:
            comp =  moose.element(where)
        except ValueError:
            print('No element ',where)
            return 0
        
        if isinstance(comp, (moose.Compartment, moose.ZombieCompartment)):
            dist,name = get_dist_name(comp)
        else:
            print('Wrong element class ',where)
            return 0
    elif isinstance(where, _numbers.Number):
        name = ''
        dist = where
    else:
        print('Wrong distance/element passed in distance mapping ',where)
        return 0

    res = {}
    for k, v in mapping.items():
        if len(k)  == 3:
            left, right, description = k
        elif len(k) == 2:
            left, right = k
            description = ''
        else:
            continue
        if left <= dist < right:
            if description:
                if name.startswith(description) or name.endswith(description):
                    res['description'] = v
            else:
                res['no_description'] = v
            
    if not res: 
        return 0

    if 'description' in res:
        v = res['description']
    else:
        v = res['no_description']
    if isinstance(v, _numbers.Number):
        return v
    elif isinstance(v, list):
        return v
    elif isinstance(v, dict):
        return v
    
    return v(dist)

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
    def __init__(self, name, **kwargs):
        super(NamedDict, self).__init__(**kwargs)
        self.__name__ = name

    def __repr__(self):
        items = ('{}={}'.format(k,v) for (k,v) in self.items())
        l = len(self.__name__) + 1
        sep = ',\n' + ' '*l
        return '{}({})'.format(self.__name__, sep.join(items))

    def __setitem__(self, k, v):
        raise ValueError('Assignment is not allowed')

    def __getattribute__(self, k):
        # attributes have higher priority
        try:
            return super(NamedDict, self).__getattribute__(k)
        except AttributeError:
            return super(NamedDict, self).__getitem__(k)

    def __setattribute__(self, k, v):
        raise ValueError('Assignment is not allowed')

def block_if_noninteractive():
    if not hasattr(_sys, 'ps1'):
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
