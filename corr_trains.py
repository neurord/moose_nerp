#CorrTrains.py
#Creates Poisson distributed trains.  Either uncorrelated, 
# or with one of two different types of correlation
# Inputs: 1: output filename
#         2: number of trains
#            check_netparams will calculate how many trains you need for your network
#         3: Spike Frequency
#         4: maxTime
#         5: type of correlation
#              0: no correlations
#              1: all trains are randomly shifted versions of the first train
#                  shift param is maximum amount shift - additional parameter
#              2: some trains are linear combinations of others
#                  specify correlation value, and program calculates
#                       how many independent trains and
#                       how many dependent trains.
#                    correlation is actually R^2 - so if sqrt(corr_val)=0.5, then half of trains are independent
#         6: for corr type 1 - shift parameter, for type 2, amount of corrlation
# Future changes:
# incorporate stuff from InputwithCorrelation2.py: within neuron correlation
# Ampa2.py: motor and sensory upstates
from __future__ import print_function, division
import sys
sys.path.append('./')
import os
os.environ['NUMPTHREADS'] = '1'
from pylab import *
import numpy as np

###############################################################################
#parameters for creating fake spike trains. Replace with argparser
###############################################################################
try:
    args = ARGS.split(",")
    print("ARGS =", ARGS, "commandline=", args)
    do_exit = False
except NameError: #NameError refers to an undefined variable (in this case ARGS)
    args = sys.argv[1:]
    print("commandline =", args)
    do_exit = True

fname=args[0]

num_trains=np.int(args[1])

#Mean frequency of the trains, previously was set to 10
Freq=np.float(args[2])

maxTime = float(args[3])

#this parameter controls whether to introduce correlations between trains:
corr=int(args[4])
if (corr==1): 
    shift=float(args[5])
    print (shift, type(shift))
if (corr==2):
    corr_val=float(args[5])
    print (corr_val, type(corr_val))

################End of parameter parsing #############
#More notes for future improvements:
#check_connect will calculate number of synapses and trains needed 
#BUT, need to create the neuron prototype first
#from spspine import check_connect, param_net, d1d2

#standard_options provides simulation time
# from spspine import standard_options
# option_parser = standard_options.standard_options()
# param_sim = option_parser.parse_args()
# maxTime=param_sim.simtime

isi=1/Freq
samples=np.int(2*Freq*maxTime)

############################

def make_trains(num_trains,isi,samples,maxTime):
    spikeIsi=np.zeros((num_trains,samples))
    spikeTime=list()
    for i in range(num_trains):
        spikeIsi[i]=np.random.exponential(isi,samples)
        spikeTimeTemp=np.cumsum(spikeIsi[i])
        spikeTime.append(np.extract(spikeTimeTemp<maxTime,spikeTimeTemp))
        #print ("shape of spikeISI, spikeTime:", np.shape(spikeIsi),np.shape(spikeTime[i]))
    return spikeTime

############################

#### Uncorrelated trains (if corr==0)
#### Or, correlation will be imparted from fraction_duplicate and check_connect
if (corr==0):
    spikeTime=make_trains(num_trains,isi,samples,maxTime)

########
#correlated trains
########
#method 1 - each train is randomly shifted version
########## DOESN"T WORK - DEBUG ####################
if (corr==1):
    spikeTime[0]=make_trains(1,isi,samples,maxTime)
    for i in range(num_trains-1):
        spikeShift=shift*np.random.uniform()
        #print ("i, shift:", i, spikeShift)
        spikeTime.append(spikeTime[0][:]+spikeShift)

#Second correlation method - linear combination of trains
if (corr==2):
    #for now, set num_syn = num_trains
    num_syn=num_trains
    indep_trains=int(num_syn-np.sqrt(corr_val)*(num_syn-1))
    depend_trains=num_syn-indep_trains
    print ("Dep, Indep, Total:", depend_trains,indep_trains,num_syn)
    #
    #First create the set of independent Trains
    spikeTime=make_trains(indep_trains,isi,samples,maxTime)
    total_spikes=[len(item) for item in spikeTime]
    spikes_per_train=sum(total_spikes)/indep_trains
    print ("spikes_per_train", spikes_per_train,"Indep SpikeTime", shape(spikeTime), shape(spikeTime[0]))
    #
    #Second, randomly select spikeTimes from independent trains to create dependent Trains
    if (indep_trains<num_syn):
        for i in range(indep_trains,num_syn):
            #1. determine how many spikeTimes to obtain from each indep Train
            samplesPerTrain=np.random.poisson(float(spikes_per_train)/indep_trains,indep_trains)
            spikeTimeTemp=[]
            for j in range(indep_trains):
                #2. from each indep train, select some spikes, eliminating duplicates
              if len(spikeTime[j]):
                high=len(spikeTime[j])-1
                indices=list(set(np.sort(np.random.random_integers(0,high,samplesPerTrain[j]))))
                spikeTimeTemp=np.append(spikeTimeTemp,spikeTime[j][indices])
            print ('spike train %d:' % (i), spikeTimeTemp,'train length', len(spikeTimeTemp))
            #3. after sampling each indepTrain, sort spikes before appending to spikeTime list
            spikeTime.append(np.sort(spikeTimeTemp))
        print ("num trains:", shape(spikeTime))

################Save the spike times array#############
##### Probably could just save to plain text file  ####
savez(fname, spikeTime=spikeTime)

################ Created jittered version of spike times
#This assumes that above creates trains for one neuron, and then the network receives jittered version
meanjitter=0.1
spikeTimeJit=[]
#for i in range(netsize):
#    jitter=np.random.normal(meanjitter,meanjitter,len(spikeTime[i]))
#    spikeTimeJit.append(spikeTime[i]+jitter)

#fnamejit=fname+'jitter'
#print (fnamejit)
#savez(fnamejit, spikeTime=spikeTime)
    
