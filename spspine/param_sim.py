"""\
Simulation and plotting parameters, as well as parameter overrides

plas=plasticity elements and synaptic input, curr=ionic currents
"""

############## First, optionally override parameters specifying model detail
#calcium: include or exclude calcium concentration dynamics, single tau
calcium=1

#include or exclude plasticity based on calcium
plasYesNo=1

#note that if ghkYesNo=0, make sure that ghKluge = 1
ghkYesNo=0

spineYesNo=1

#No point adding synapses unless they receive inputs
synYesNo=1

# The parameter single only used in SPnetSpineSim.py
# set single=1 to create a single neuron of each type with synaptic input 
# set single=0 to create a network (in which case spines are a bad idea)
single=1
# For now, don't create spines if creating a network of neurons
if not single:
    spineYesNo=0
    title1 = 'network'
    neurnameNum=2
else:
    title1 = 'single'

#Second, specify which graphs of the simulation should be shown?
plotplas=1

#to prevent you from plotting plasticity if not created:
if not plasYesNo or not calcium:
    plotplas=0

######################plotcurr indicates whether to plot time dependent currents (or conductances)
plotcurr=0
currmsg='getGk' # make this get_Ik to plot current
currlabel='Cond, S'
# graphsyn indicate whether to plot the synaptic inputs
graphsyn=0
Synmsg='getGk'  # make this get_Ik to plot current
SynLabel='Cond, nS' #make this 'Curr, nA' for current
#whether to plot the various ion channel activation and inactivation curves
plotchan=0
plotpow=1
# plotnet=0 plots all comps from single neuron, plotnet=1 plots soma from all neurons
# These two param used in SPnetSpineSim only
plotnet=1
showgraphs=1
#whether to plot additional information during simulation set-up
printinfo=1
#printMoreInfo is compartment based - generates a lot
printMoreInfo=0

#showclocks=1 will show which elements are assigned to clocks between a and b
showclocks=1
clocka=3
clockb=6

#####################Third, specify values for somatic current injection and/or synaptic input
current1=0.25e-9
current2=0.35e-9
currinc=0.1e-9
delay=0.1
width=0.4

#For single neuron, provide synaptic input at specified times, to compartment specified
#Can adjust these to provide synaptic input appropriately timed to Action Potential
inpath='/input'
stimtimes=[0.04,0.19,0.46]
syncomp=4

###################Fourth, specify simulation time, time step:dt and solver
simtime = 0.4999 #0.4999
plotdt = 0.2e-3
simdt = 2.5e-5
hsolve=1
