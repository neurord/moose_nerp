def synconn(synpath,dist,presyn,mindel=1e-3,cond_vel=0.8):
    s=moose.SynChan(synpath)
    s.synapse.num = s.synapse.num+1
    jj=s.synapse.num-1
    s.synapse[jj].delay = max(mindel,np.random.normal(mindel+dist/cond_vel,mindel))
    if printMoreInfo:
        print "SYNAPSE:", synpath,jj,s.synapse.num,s.synapse[jj].delay
    #It is possible to set the synaptic weight here.  
    m = moose.connect(presyn, 'event', moose.element(s.path + '/synapse'), 'addSpike')
    if 'nmda' in synpath and calcium:
        synchanCa=moose.SynChan(s.path+'/CaCurr')
        synchanCa.synapse.num=s.synapse.num
        synchanCa.synapse[jj].delay=s.synapse[jj].delay
        if printMoreInfo:
            print "NMDA Syn", synchanCa.path, moose.element(synchanCa.path + '/synapse')
        m = moose.connect(presyn, 'event', moose.element(synchanCa.path + '/synapse'), 'addSpike')

def filltimtable(spikeTime,simtime,name,path):
    stimtab=[]
    for ii in range(len(spikeTime)):
    #convert spiketimes into form that can be used
        stimtimes=spikeTime[ii][spikeTime[ii]<simtime]
    #create stimtab and fille it with the 0-1 vector
        stimtab.append(moose.TimeTable(path+'/%sTimTab%s' % (name,ii)))
        stimtab[ii].vec=stimtimes
    #
    return stimtab

def alltables(fname,inpath,maxtt):
    #Read in file with spike times.  both duplicates and unique
    temp=np.load(fname)
    DupSpikes=temp['Dup']
    UniqueSpikes=temp['Unique']
    if printinfo:
        print "AVAILBLE Dup trains:", len(DupSpikes), DupSpikes,", Unique trains:", len(UniqueSpikes)
    #create Time tables
    Duptt=filltimtable(DupSpikes,simtime,'Dup',inpath)
    uniqnum=min(maxtt,len(UniqueSpikes))
    if printinfo:
        print "TIME TABLES TO USE", maxtt, "Unique:", uniqnum
    Uniqtt=filltimtable(UniqueSpikes[0:maxtt],simtime,'Uniq',inpath)
    return {'Dup':Duptt,'Uniq':Uniqtt}

def addinput(ttab,synchans,synlist,simtime,cells,SynPerComp,startt):
    #all synpases in synlist must in same compartment (e.g. both on spines or both on dendrites)
    if printinfo:
        print "CELLS", len(cells),cells, "syn/Comp", SynPerComp
    #create table of synapse compartments for each neuron
    comps=[]
    Duptt=ttab['Dup']
    Uniqtt=ttab['Uniq']

    for kk in range(len(synchans[synlist[0]])):
        compname='/'+split(synchans[synlist[0]][kk].path,'/')[compNameNum]
        if printMoreInfo:
            print kk, SynPerComp[kk]
        if spineYesNo:
            comps.append(compname+'/'+split(synchans[synlist[0]][kk].path,'/')[spineNameNum])
        else:
            for qq in range(SynPerComp[kk]):
                comps.append(compname)
        if printMoreInfo:
            print comps
    allcomps=tile(comps,(len(cells),1))
    remainingcomps=[len(comps) for ii in range(len(cells))]
    if printinfo:
        print "Remaing COMPS TO CONNECT",remainingcomps, shape(allcomps)
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
            if printMoreInfo:
                print "CONNECT:", branch,tt.path,cells[cell].path,remainingcomps,synpath
                print allcomps
            for chan in synlist:
                synconn(synpath+'/'+chan,dist,tt)
    #loop through unique trains and connect them to one comp in one neuron
    TotalTrains=0
    for train in range(startt,len(Uniqtt)):
        if sum(remainingcomps)>0:
            TotalTrains+=1
            tt=moose.TimeTable(Uniqtt[train])
            br=np.random.random_integers(0,sum(remainingcomps)-1)
            cumcomps=np.array([int(sum(remainingcomps[0:x])) for x in arange(1,len(remainingcomps)+1)])
            cell=int(np.min(where(cumcomps>br)))
            postneur=cells[cell]
            if cell > 0:
                branch=br-cumcomps[cell-1]
            else:
                branch=br
            if printMoreInfo:
                print br, sum(remainingcomps), cumcomps, where(cumcomps>br), cell, branch,allcomps[cell][branch]
            synpath=postneur+allcomps[cell][branch]
            remainingcomps[cell]=remainingcomps[cell]-1
            allcomps[cell][branch]=allcomps[cell][remainingcomps[cell]]
            allcomps[cell][remainingcomps[cell]]=''
            if printMoreInfo:
                print "CONNECT:", br, branch, cumcomps, remainingcomps, tt.path, synpath
            for chan in synlist:
                synconn(synpath+'/'+chan,0,tt)
        else:
            #print "out of synpases"
            break
            #don't do anything. I don't think this break is exiting the loop
    if printinfo:
        print "LastTrainNum:",train
    return train

