#param_net.py

from moose_nerp.prototypes.ttables import TableSet
from moose_nerp.prototypes.syn_proto import ShortTermPlasParams,SpikePlasParams
from moose_nerp.prototypes.util import NamedList
from moose_nerp.prototypes.connect import dend_location,connect,ext_connect 

stop_signal=False  #controls which external inputs are used ramp/pulse vs oscillatory (and lognorm)
merge_connect=True
'''
Two methods for merging different networks
A. use connect_dict from other populations(moose_nerp network packages), but with modifications
    set merge_connect = True
    update change_weight to update the synaptic strength of connections
    update change_prob to update the connection probability
B. do not use connect_dict from other populations (moose_nerp network packages)
   set merge_connect = False
   all connections must be specified in connect_dict
'''

rampdur='0.5'
rampfreq='25'
pulsedur='0.05'
pulsefreq_ep='73' #88
pulsefreq='73'
oscfreq='10.0'
stnfreq='28.0'
fb_npas=3 #3
fb_lhx=5 #5
FSI_inputs=0
size_factor=1 #(change from 500x500 str network)

#filename from parameters governing time table inputs, used here and in multisim.py
def fname(stop_signal,freqCtx,freqStn,pulsedur,rampdur,fb_npas,fb_lhx,size_factor=1):
    if stop_signal==True:
        if pulsefreq_ep == pulsefreq:
            fname='Ctx_rampdur'+str(rampdur)+'_freq'+freqCtx+'-STN_pulsedur'+str(pulsedur)+'_freq'+freqStn
        else:
            fname='Ctx_rampdur'+str(rampdur)+'_freq'+freqCtx+'-STN_pulsedur'+str(pulsedur)+'_freq'+freqStn+'ep'+pulsefreq_ep
    else:
        fname='Ctx_osc'+freqCtx+'_STN_lognorm'+freqStn

    #filename from feedback parameters
    fname+='-fb_npas'+str(fb_npas)+'_lhx'+str(fb_lhx)+'-'+str(size_factor*500)+'um'
    confile='bg_connect'+fname  #saves complete list of connections
    outfile='bg_'+fname #saves spikes
    return confile,outfile

if stop_signal==True:
    confile,outfile=fname(stop_signal,rampfreq,pulsefreq,pulsedur,rampdur,fb_npas,fb_lhx)
else:
    confile,outfile=fname(stop_signal,oscfreq,stnfreq,pulsedur,rampdur,fb_npas,fb_lhx)
if FSI_inputs==0:
    outfile=outfile+'noFSI'
    confile=confile+'noFSI'

########### size dependent parameters ####################
#  str network    500umx500um     1mmx1m    700um x 700 um
#syn_per_tt           4            16         8
#connect prob D1->ep  0.2         0.05        0.1
#connect prob D2->gp
#size_factor          1            4          2
#factor in change_syn ?
#################################################

#changes to number of synapses; multiply by NumSyn, 
# - increases number of external inputs
# - increases available synapses (fixes synchan_shortage) for intrinsic connections
change_syn={'proto':{'gaba':4,'ampa':1.2},'Lhx6':{'gaba':4},'Npas':{'gaba':4},'ep':{'ampa':2,'gaba':6},
            'D1':{'gaba':6,'gaba2':3,'ampa':1.5},'D2':{'gaba':6,'gaba2':3,'ampa':1.5},'FSI':{'gaba':2,'ampa':1.6}}

####################################################################
#New external time tables - (filename, syn_per_tt)
#only get created if they are specified in connect_dict
if stop_signal:
    tt_Ctx=TableSet('CtxSPN', 'bg_net/Ctx10000_ramp_freq5.0_'+rampfreq+'dur'+rampdur,syn_per_tt=4*size_factor)
else: 
    tt_Ctx=TableSet('CtxSPN', 'bg_net/Ctx10000_osc_freq'+oscfreq+'_osc0.7',syn_per_tt=4*size_factor)

tt_STN=TableSet('tt_STN','bg_net/STN2000_lognorm_freq'+stnfreq,syn_per_tt=4)
tt_STNp=TableSet('tt_STNp','bg_net/STN500_pulse_freq1.0_'+pulsefreq+'dur'+pulsedur,syn_per_tt=4)

if pulsefreq_ep != pulsefreq:
    tt_STNep=TableSet('tt_STNep','bg_net/STN500_pulse_freq1.0_'+pulsefreq_ep+'dur'+pulsedur,syn_per_tt=4)


ttable_replace={}
ttable_replace={'ep': {'ampa':{'extern1':tt_STN}}}

ttable_replace['proto']={'ampa':{'extern':tt_STN}}
ttable_replace['Npas']={'ampa':{'extern':tt_STN}}
ttable_replace['Lhx6']={'ampa':{'extern':tt_STN}}

ttable_replace['D1']={'ampa':{'extern1':tt_Ctx}}
ttable_replace['D2']={'ampa':{'extern1':tt_Ctx}}
ttable_replace['FSI']={'ampa':{'extern':tt_Ctx}}

############################################################
#three examples of distributions for Connections
even_distr=dend_location(postsyn_fraction=0.5)
proximal_distr= dend_location(mindist=0e-6,maxdist=80e-6,postsyn_fraction=1)
distal_distr=dend_location(mindist=50e-6,maxdist=400e-6,postsyn_fraction=.1)#,half_dist=50e-6,steep=1)

####################### connections between regions #####################
#Inputs to ep/SNr from Striatum/D1 and GPe/proto.
D1_to_ep=0.2/size_factor
D2_to_GPe=0.08/size_factor

#function to add additional AMPA inputs to GPe and Ep/SNr, used here and in multisim.py
def add_connect(connect_dict,change_prob):
    if pulsefreq_ep == pulsefreq:
        connect_dict['ep']['ampa']={'extern2':ext_connect(synapse='ampa',pre=tt_STNp,post='ep', dend_loc=dend_location(postsyn_fraction=0.25),weight=1.5)}
    else:
        connect_dict['ep']['ampa']={'extern2':ext_connect(synapse='ampa',pre=tt_STNep,post='ep', dend_loc=dend_location(postsyn_fraction=0.25),weight=1.5)} 
    connect_dict['Npas']['ampa']={'extern2':ext_connect(synapse='ampa',pre=tt_STNp,post='Npas', dend_loc=dend_location(postsyn_fraction=0.25),weight=1.2)}
    connect_dict['Lhx6']['ampa']={'extern2':ext_connect(synapse='ampa',pre=tt_STNp,post='Lhx6', dend_loc=dend_location(postsyn_fraction=0.25),weight=1.2)}
    connect_dict['proto']['ampa']={'extern2':ext_connect(synapse='ampa',pre=tt_STNp,post='proto', dend_loc=dend_location(postsyn_fraction=0.15),weight=1.2)}
    connect_dict['ep']['ampa']={'extern2':ext_connect(synapse='ampa',pre=tt_STNp,post='ep', dend_loc=dend_location(postsyn_fraction=0.25),weight=1.5)}
    change_prob['proto']['ampa']= {'extern':('dend_loc',dend_location(postsyn_fraction=0.85))}
    change_prob['Lhx6']['ampa']= {'extern':('dend_loc',dend_location(postsyn_fraction=0.75))}
    change_prob['Npas']['ampa']= {'extern':('dend_loc',dend_location(postsyn_fraction=0.75))}
    change_prob['ep']={'ampa':{'extern1':('dend_loc',dend_location(postsyn_fraction=0.75))}}
    return connect_dict,change_prob
    
#function to add feedback from GPe to striatum, used in main and in multisim.py
#PSP ranges from 0.5-1.3 mV to SPNs; Gsyn=0.2 nS (weight=1).  If vclamp in Corbit was at rest, e.g. ~-80 mV with ~20 mV driving potential, that yields 4 pA current
#Corbit values: 0 +/0 40 pA (possibly with optogenetic activation of multiple synapses?)
#For FSIs: 565 pA +/- 560 pA; weight=3 with 0.4 nS Gsyn yields 1.2,2.2,3 mV depolarizations; should be 6x the current
#input resistance: D1: 140 MOhm, D2: 160 MOhm, FSI: 90 (-50 pA), or 170 MOhm (-100 pA) - these are a bit low
def feedback(connect_dict,fb_npas,fb_lhx):
    if fb_npas>0:
        connect_dict['D2']={'gaba2':{}}
        connect_dict['D2']['gaba2']['Npas']=connect(synapse='gaba2', pre='Npas', post='D2', probability=1,weight=fb_npas)
        connect_dict['D1']={'gaba2':{}}
        connect_dict['D1']['gaba2']['Npas']=connect(synapse='gaba2', pre='Npas', post='D1', probability=1,weight=fb_npas)
    if fb_lhx>0:
        connect_dict['FSI']={'gaba':{}}
        connect_dict['FSI']['gaba']['Lhx6']=connect(synapse='gaba', pre='Lhx6', post='FSI', probability=1,weight=fb_lhx)
    return connect_dict

connect_dict={}
##### Note that number of inputs = probability * number of presyn neurons. Thus,
## if increase presyn neurons, will increase inputs
connect_dict={'ep':{'gaba':{}}}
connect_dict['ep']['gaba']['proto']=connect(synapse='gaba', pre='proto', post='ep', probability=0.3,weight=1.0)
connect_dict['ep']['gaba']['Lhx6']=connect(synapse='gaba', pre='Lhx6', post='ep', probability=0.3,weight=1.0)
connect_dict['ep']['gaba']['D1']=connect(synapse='gaba', pre='D1', post='ep', probability=D1_to_ep,weight=1.2)

#Inputs from striatum to GPe
#Input resistance.  Npas: 360 MOhm, proto: 280 Mohm, Lhx6: 300 Mohm
connect_dict['Npas']={'gaba':{}}
connect_dict['Npas']['gaba']['D2']=connect(synapse='gaba', pre='D2', post='Npas', probability=D2_to_GPe,weight=1)
connect_dict['Lhx6']={'gaba':{}}
connect_dict['Lhx6']['gaba']['D2']=connect(synapse='gaba', pre='D2', post='Lhx6', probability=D2_to_GPe,weight=1)
connect_dict['proto']={'gaba':{}}
connect_dict['proto']['gaba']['D2']=connect(synapse='gaba', pre='D2', post='proto', probability=D2_to_GPe,weight=1)

############ change connection probability #####################
#example of tuples needed to change connection probability between neurons
#use multiplicative factor for space constant, since those are such small numbers
#>1 would decrease connections, <1 would increase connections
#use actual value for probability of connection
#The following compensate for very high firing frequency when increasing network size
#could also decrease weight of ampa synapses
#dend_loc is to change probability for external connections

change_prob={'proto':{'gaba':{'proto':('space_const',0.5),'Lhx6':('space_const',0.6),'Npas':('space_const',0.6)}},
             'Lhx6':{'gaba':{'proto':('space_const',0.5),'Lhx6':('space_const',0.6),'Npas':('space_const',0.6)}},
             'Npas':{'gaba':{'proto':('space_const',0.5),'Lhx6':('space_const',0.6),'Npas':('space_const',0.6)}}}   

if stop_signal:
    connect_dict,change_prob=add_connect(connect_dict,change_prob)

##################### These are only used if connect_merge==True ##################
########## Delete these connections that are defined in the other net_modules
# e.g., extrinsic connections that are now replaced by other network connections
connect_delete={}

connect_delete={'ep':{'gaba':['extern2','extern3']}}
if FSI_inputs==0:
    #test effect of FSI input
    connect_delete['D1']= {'gaba2':['FSI']}
    connect_delete['D2']= {'gaba2':['FSI']}

#once STN neurons provided:
#connect_delete['ep']['ampa']='extern'
#connect_delete['proto']={'ampa':'extern'}
#connect_delete['Lhx6']={'ampa':'extern'}
#connect_delete['Npas']={'ampa':'extern'}

#delete intra striatal connections to measure strength of individual GPe inputs
'''
connect_delete['D1']={'gaba':['D1','D2','FSI']}
connect_delete['D2']={'gaba':['D1','D2','FSI']}
connect_delete['FSI']={'gaba':['FSI']}
connect_delete['proto']={'gaba':['proto','Npas','Lhx6']}
connect_delete['Npas']={'gaba':['proto','Npas','Lhx6']}
connect_delete['Lhx6']={'gaba':['proto','Npas','Lhx6']}
'''

######### change weight of synapses, e.g. to add asymmetry as measured in striatum #####################
#multiples synaptic conductance - these are multiplicative factors
######### from param_syn.py #########
''' weight multiplies these values
neuron  gabaG  ampaG 
FSI     0.25,   0.15,  
SPN     0.25,   0.15  
GP      0.25    0.15  
ep      0.25    0.15  
'''
change_weight={'D1':{'gaba':{'D2':('weight',0.85),'D1':('weight',0.65)},'ampa':{'extern1':('weight',1.4)}},
               'D2':{'gaba':{'D2':('weight',0.75),'D1':('weight',0.75)},'ampa':{'extern1':('weight',1.4)}},
               'FSI':{'ampa':{'extern':('weight',1.3)}},
               'proto':{'gaba':{'proto':('weight',0.7),'Npas':('weight',0.7),'Lhx6':('weight',0.7)}},
               'Npas':{'gaba':{'proto':('weight',1.2),'Npas':('weight',1.2),'Lhx6':('weight',1.2)}},
               'Lhx6':{'gaba':{'proto':('weight',1.2),'Npas':('weight',1.2),'Lhx6':('weight',1.2)}},
               'ep':{'ampa':{'extern1':('weight',1.5)}}}

mindelay={}
cond_vel={}

'''
For external connections, the total number of synapses from each set of time tables to post-synaptic cell =
number of synapses*probability (or postsyn_fraction for dend_location)
If multiple sets of time tables, need to ensure sum of probabilities <= 1
To change effect on post-synaptic cell, increase or decrease NumSyn, synaptic conductance, probability, or  firing rate of input tt

for internal connections, , the total number of synapses from each pre-synaptic neuron type to post-synaptic cell =
number of synapses*probability (or postsyn_fraction for dend_location)
If multiple types of pre-synaptic neurons, need to ensure sum of probabilities <= 1
To change effect on post-synaptic cell, increase or decrease NumSyn,, synaptic conductance or probability

connectivity goals
1. 80% of GPe inputs from striatum, 20% from GPe
'''
