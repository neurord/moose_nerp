from __future__ import print_function, division
import numpy as np
import moose

from spspine import param_cond, param_sim, param_spine

def synconn(synpath,dist,presyn,cal,mindel=1e-3,cond_vel=0.8):
    synchan=moose.element(synpath)
    shname=synchan.path+'/SH'
    sh=moose.SimpleSynHandler(shname)
    if sh.synapse.num==1:
        moose.connect(sh, 'activationOut', synchan, 'activation')
    jj=sh.synapse.num
    sh.synapse.num = sh.synapse.num+1
    if mindel:
        sh.synapse[jj].delay = max(mindel,np.random.normal(mindel+dist/cond_vel,mindel))
    else:
        sh.synapse[jj].delay=mindel
    if param_sim.printMoreInfo:
        print("SYNAPSE:", synpath,jj,sh.synapse.num,sh.synapse[jj].delay)
    #It is possible to set the synaptic weight here.  
    m = moose.connect(presyn, 'eventOut', sh.synapse[jj], 'addSpike')
    if 'nmda' in synchan.path and cal:
        synchanCa=moose.SynChan(synchan.path+'/CaCurr')
        shnameCa=synchanCa.path+'/SH'
        shca=moose.SimpleSynHandler(shnameCa)
        if shca.synapse.num==1:
            moose.connect(shca, 'activationOut', synchan, 'activation')
        shca.synapse.num=sh.synapse.num
        shca.synapse[jj].delay=sh.synapse[jj].delay
        if param_sim.printMoreInfo:
            print("NMDA Syn", synchanCa.path, moose.element(shca))
        m = moose.connect(presyn, 'eventOut', shca.synapse[jj], 'addSpike')

def filltimtable(spikeTime,simtime,name,path):
    stimtab=[]
    for ii in range(len(spikeTime)):
        #convert spiketimes into form that can be used
        stimtimes=spikeTime[ii][spikeTime[ii]<simtime]
        #create stimtab and fille it with the 0-1 vector
        stimtab.append(moose.TimeTable('{}/{}TimTab{}'.format(path, name, ii)))
        stimtab[ii].vector=stimtimes
    return stimtab

def alltables(fname,inpath,maxtt,simtime):
    #Read in file with spike times.  both duplicates and unique
    ######################Add some code to allow entering fname if not found by system
    temp=np.load(fname+'.npz')
    DupSpikes=temp['Dup']
    UniqueSpikes=temp['Unique']
    if param_sim.printinfo:
        print("AVAILBLE Dup trains:", len(DupSpikes), DupSpikes,", Unique trains:", len(UniqueSpikes))
    #create Time tables
    Duptt=filltimtable(DupSpikes,simtime,'Dup',inpath)
    uniqnum=min(maxtt,len(UniqueSpikes))
    if param_sim.printinfo:
        print("TIME TABLES TO USE", maxtt, "Unique:", uniqnum)
    Uniqtt=filltimtable(UniqueSpikes[0:maxtt],simtime,'Uniq',inpath)
    return {'Dup':Duptt,'Uniq':Uniqtt}

def addinput(ttab,synchans,synlist,cells,SynPerComp,startt):
    #all synpases in synlist must in same compartment (e.g. both on spines or both on dendrites)
    if param_sim.printinfo:
        print("CELLS", len(cells),cells, "syn/Comp", SynPerComp)
    #create table of synapse compartments for each neuron
    comps=[]
    Duptt=ttab['Dup']
    Uniqtt=ttab['Uniq']
    delay=0   #no need for delay for time table inputs

    for kk in range(len(synchans[synlist[0]])):
        p = synchans[synlist[0]][kk].path.split('/')
        compname = '/' + p[param_cond.compNameNum]
        if param_sim.printMoreInfo:
            print(kk, SynPerComp[kk])
        if param_sim.spineYesNo:
            comps.append(compname + '/' + p[param_spine.SpineParams.spineNameNum])
        else:
            for qq in range(SynPerComp[kk]):
                comps.append(compname)
        if param_sim.printMoreInfo:
            print(comps)
    allcomps=np.tile(comps,(len(cells),1))
    remainingcomps=[len(comps) for ii in range(len(cells))]
    if param_sim.printinfo:
        print("Remaing COMPS TO CONNECT",remainingcomps, np.shape(allcomps))
    #
    #loop through duplicates and connect them to a compartment in each neuron
    for train in range(len(Duptt)):
        tt=moose.TimeTable(Duptt[train])
        for cell in range(len(cells)):
            postneur=cells[cell]
            branch=np.random.random_integers(0,remainingcomps[cell]-1)
            synpath=postneur+allcomps[cell][branch]
            remainingcomps[cell]=remainingcomps[cell]-1
            allcomps[cell][branch]=allcomps[cell][remainingcomps[cell]]
            allcomps[cell][remainingcomps[cell]]=''
            if param_sim.printMoreInfo:
                print("CONNECT:", branch,tt.path,cells[cell].path,remainingcomps,synpath)
                print(allcomps)
            for chan in synlist:
                synconn(synpath+'/'+chan,dist,tt,param_sim.calcium,delay)
    #loop through unique trains and connect them to one comp in one neuron
    TotalTrains=0
    for train in range(startt,len(Uniqtt)):
        if sum(remainingcomps)>0:
            TotalTrains+=1
            tt=moose.TimeTable(Uniqtt[train])
            br=np.random.random_integers(0,sum(remainingcomps)-1)
            cumcomps=np.array([int(sum(remainingcomps[0:x])) for x in np.arange(1,len(remainingcomps)+1)])
            cell=int(np.min(np.where(cumcomps>br)))
            postneur=cells[cell]
            if cell > 0:
                branch=br-cumcomps[cell-1]
            else:
                branch=br
            if param_sim.printMoreInfo:
                print(br, sum(remainingcomps), cumcomps, np.where(cumcomps>br), cell, branch,allcomps[cell][branch])
            synpath=postneur+allcomps[cell][branch]
            remainingcomps[cell]=remainingcomps[cell]-1
            allcomps[cell][branch]=allcomps[cell][remainingcomps[cell]]
            allcomps[cell][remainingcomps[cell]]=''
            if param_sim.printMoreInfo:
                print("CONNECT:", br, branch, cumcomps, remainingcomps, tt.path, synpath)
            for chan in synlist:
                synconn(synpath+'/'+chan,0,tt,param_sim.calcium,delay)
        else:
            #print "out of synpases"
            break
            #don't do anything. I don't think this break is exiting the loop
    return len(Uniqtt)
