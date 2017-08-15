# moose_nerp — declarative specification of neuron model in MOOSE
Complete example given for a Striatal Spiny Projection Neuron

[![Build Status](https://semaphoreci.com/api/v1/neurord/spspine/branches/master/badge.svg)](https://semaphoreci.com/neurord/spspine)

Set of prototype files and parameter files to simplify creation of neuron and network models in a declarative format.
Each neuron or set of neurons has its own package in moose_nerp, d1d2 for two types of spiny projection neurons, gp for two types of globus pallidus neurons, and ca1 for hippocampal CA1 neurons.
Each package, e.g. moose_nerp/d1d2, contains a set of parameter files for creating ion channels, synaptic channels, neuron morphology, plasticity, spines and calcium dynamics, as well as the main program, which both creates and simulates the neurons.

run the simulation from a terminal window (in spspine directory) using the command:

  `python -m moose_nerp.d1d2`

from a python window, run using the command:

  `import moose_nerp.d1d2.__main__`, or `execfile('moose_nerp/d1d2/__main__.py')`

to evaluate variables created in __main__ after the import, use the following syntax:
   `moose_nerp.d1d2.__main__.variable_name`

**Files in each package**

1. `param_chan.py`: parameters governing channel gating
2. `param_cond.py`: channel conductances, which can be distance dependent, morphology file, external Ca concentration and Temperature
3. `param_syn.py`: synaptic channel parameters, including the distance dependent synaptic density
4. `param_spine.py`: morphology and electrical parameters describing spines, also spine density.
5. `param_ca_plas.py`: calcium and plasticity parameters.  Calcium can be either single time constant of decay, or can have multiple pumps and buffers.  Plasticity parameters implement calcium dependent synaptic plasticity, with both amplitude and duration thresholds
6. `*.p`: morphology file
7. `__init__.py`: specifies all the parameter files, and also some binary variables indicating whether to add spines, synapses, calcium, plasticity

**To create a new neuron type**

1. clone one of the packages, e.g. d1d2 
2. edit param_chan to specify ion channels and their gating
3. edit param_cond to list morphology file and conductance of channels.  Note that you need only specify a subset of channels listed in param_chan
4. edit param_spine for your neuron type.  Note that if you don't want spines, no need to edit this, just make spineYN=0 in `__init__.py`
5. edit param_ca_plas for your neuron type.  Note that if you don't want calcium, no need to edit this, just make calYN=0 in `__init__.py`.  If you want calcium but not plasticity, make calYN=1 and plasYN=0
6. edit param_syn for your neuron type.  Note that if you don't want synapses, no need to edit this, just make synYN=0 in `__init__.py`
7. Note that if calYN=0 or synYN=0, no plasticity will be created, even if plasYN=1
8. make sure the .p file for your neuron is in thie package
9. edit `__main__.py`: global search and replace d1d2 with the name of your package. A "standard" set of graphs are created, showing membrane potential in every compartment, and calcium (if created).  You might want to customize this aspect.

**Networks**
