# moose_nerp — declarative specification of neuron model in MOOSE
Complete example given for a Striatal Spiny Projection Neuron

[![Build Status](https://semaphoreci.com/api/v1/neurord/spspine/branches/master/badge.svg)](https://semaphoreci.com/neurord/spspine)

Set of prototype files and parameter files to simplify creation of neuron and network models in a declarative format for the MOOSE simulator (https://moose.ncbs.res.in/).
Each neuron or set of neurons has its own package in moose_nerp, d1d2 for two types of spiny projection neurons, gp for two types of globus pallidus neurons, and ca1 for hippocampal CA1 neurons.
Each package, e.g. moose_nerp/d1d2, contains a set of parameter files for creating ion channels, synaptic channels, neuron morphology, plasticity, spines and calcium dynamics, as well as the main program, which both creates and simulates the neurons.

run the simulation from a terminal window (in spspine directory) using the command:

  `python -m moose_nerp.d1d2`

from a python window (python 2 only), run using the command:

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
2. edit param_chan to specify ion channels and their gating.
  - Gate equations for TypicalOneD channels have the form:
    + AlphaBetaChannelParams (specify forward and backward transition rates):
      - alpha(v) or beta(v) = (rate + B * v) / (C + exp((v + vhalf) / vslope))
    + StandardMooseTauInfChannelParams (specify steady state and time constants):
      - tau(v) or inf(v) = (rate + B * v) / (C + exp((v + vhalf) / vslope))
    + TauInfMinChannelParams (specify steady state and time constants with non-zero minimum - useful for tau):
      - tau(v) or inf(v) = min + max / (1 + exp((v - vhalf) / vslope))
    + SSTauQuadratichannelParams (specify steady state and inverted U shaped time constant):
      - tau(v) = tau_min + tau_vdep / (1 + exp((v - tau_vhalf) / vslope))* 1/ (1 + exp((v - vhalf) / -vslope))
      - ss(v) = A/(C+ exp((v - vhalf) / vslope))
   - To specify calcium dependent potassium channels (SK) or calcium dependent inactivaion, use ZChannelParams for gating variables (and  TypicalOneD in the Channel dictionary):
      - inf(Ca) = (Ca/Kd)^power/(1+(Ca/Kd)^power
      - tau(Ca) = tau+ (taumax-tau)/(1+ (Ca/Cahalf)^tau_power)
   - To specify the voltage and calcium dependent potassium channel (BK), use BKChannelParams for gating variables and TwoD in the Channel dictionary
3. edit param_cond to list morphology file and conductance of channels.  Note that you need only specify a subset of channels listed in param_chan.
4. edit param_spine for your neuron type.  Note that if you don't want spines, no need to edit this, just make spineYN=0 in `__init__.py`.  If you do have spines, make sure that spineParent is a compartment name from your pfile.
5. edit param_ca_plas for your neuron type.  Note that if you don't want calcium, no need to edit this, just make calYN=0 in `__init__.py`.  If you want calcium but not plasticity, make calYN=1 and plasYN=0
6. edit param_syn for your neuron type.  Note that if you don't want synapses, no need to edit this, just make synYN=0 in `__init__.py`
7. Note that if calYN=0 or synYN=0, no plasticity will be created, even if plasYN=1
8. make sure the .p file for your neuron is in the package
9. edit `__main__.py`: global search and replace d1d2 with the name of your package. A "standard" set of graphs are created, showing membrane potential in every compartment, and calcium (if created).  You might want to customize this aspect.

**Networks**
1. clone othe package, str_net, and edit param_net.py.  Note there are three neuron types specified in this network: D1, D2 and FSI.  Delete all lines with FSI in you only want two neuron types, and delete all the lines with FSI or D2 if you want only one neuron type in your network.
2. replace "striatum" with name of your tissue (global search and replace)
3. replace "D1", and optionally "D2" and "FSI" with the names of your neuron types (from the single neuron package your created)
4. Edit grid, which specifies the size of the network (in meters, from xyzmin to xyzmax in each of three dimensions) and the distance between neuron types in each dimension (in meters, inc=).
5. For each population, specify the percent of total neurons.  The percents summed over neuron types should equal 1
6. Specify connections. 
 - Each intrinsic connection uses the NamedList 'connect', and specifies synapse type (e.g. GABA), neuron class of pre-synaptic neuron, neuron class of post-synaptic neuron, and a connection rule: either a probability (not distance dependent), or a distance dependence give by the space_const.
 - Each extrinsic connection uses the NamedList 'ext_connect', and specifies synapse type (e.g. AMPA), name of the TableSet that specifies the list of spike times, neuron class of post-synaptic neuron, and what fraction of the synapses should be filled with those time tables (e.g. 1.0 if only a single TableSet specified, 0.5 if two TableSets specified).
  - After specifying each connection, collect all connections for each post-synaptic neuron type into a dictionary, e.g. D1['gaba']={'D1': D1pre_D1post, 'D2': D2pre_D1post}; D1['ampa']={'extern1': ctx_D1post, 'extern2': thal_D1post}
  - then collect all those connections into one big dictonary with neuron type as key, e.g. connect_dict['D1']=D1
7. edit `__main__.py`: global search and replace d1d2 and strnet with the names of your packages. A "standard" set of graphs are created, showing membrane potential and calcium (if created) in each neuron.  You might want to customize this aspect.
