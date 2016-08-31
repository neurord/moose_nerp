"""\
Simulation and plotting parameters

plas=plasticity elements and synaptic input, curr=ionic currents
"""

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
plotpow=0
# plotnet=0 plots all comps from single neuron, plotnet=1 plots soma from all neurons
# These two param used in SPnetSpineSim only
plotnet=1
showgraphs=1

#showclocks=1 will show which elements are assigned to clocks between a and b
showclocks=1
clocka=3
clockb=6

#####################Third, specify values for somatic current injection and/or synaptic input
current1=20e-3
current2=400e-3
currinc=-50e-12
delay=0.1
width=0.1

#For single neuron, provide synaptic input at specified times, to compartment specified
#Can adjust these to provide synaptic input appropriately timed to Action Potential
inpath='/input'
stimtimes=[0.04,0.19,0.46]
syncomp=4

###################Fourth, specify simulation time, time step:dt and solver
simtime = 0.05
simdt = 25e-6
plotdt = 0.25e-3
hsolve=1
