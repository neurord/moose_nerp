CreateNetwork.py
#Sets up time tables, then connects them after creating population

def CreateNetwork(inputpath,networkname,infile,calYN,plasYN,single,confile):
#First, extract number of synapses per compartment for glu and gaba
    numglu = {}
    numgaba = {}
    for ntype in neurontypes:
        numglu[ntype] = synarray[ntype][:,GLU]
        numgaba[ntype] = synarray[ntype][:,GABA]
   
    indata=moose.Neutral(inputpath)
    inpath=indata.path
    totaltt=0
    startt=0
    if single:
        for ntype in neurontypes:
            totaltt += synarray[ntype].sum(axis=0)[GLU]
    #Second, read in the spike time tables
        timetab=alltables(infile,inpath,totaltt)
    #Third, assign the timetables to synapses for each neuron
        for ntype in neurontypes:
            startt=addinput(timetab,MSNsyn[ntype],['ampa','nmda'],simtime,[neuron[ntype]['cell'].path],numglu[ntype],startt)
    else:
    #Second, create population
        MSNpop = create_population(moose.Neutral(networkname), neurontypes, netsizeX,netsizeY,spacing)
        totaltt=sum(sum(numglu[neurontypes[i]])*len(MSNpop['pop'][i]) for i in range(len(MSNpop['pop'])))
        #Third, read in the spike time tables
        timetab=alltables(infile,inpath,totaltt)
        #Fourth, assign the timetables to synapses for each neuron, but don't re-use uniq
        #this structure actually allows different timetabs to D1 and D2, and different D1 and D2 morphology
        for ii,ntype in zip(range(len(neurontypes)), neurontypes):
            startt=addinput(timetab,MSNsyn[ntype],['ampa', 'nmda'],simtime,MSNpop['pop'][ii],numglu[ntype],startt)
        #Fifth, intrinsic connections, from all spikegens to each population
        #Different conn probs between populations is indicated in SpaceConst
        ######### Add FS['spikegen'] to MSNpop['spikegen'] once FS added to network
        for ii,ntype in zip(range(len(neurontypes)), neurontypes):
            conn=connect_neurons(MSNpop['spikegen'],MSNpop['pop'][ii],MSNsyn[ntype]['gaba'],SpaceConst[ntype],numgaba[ntype],ntype)
        
        #Last, save/write out the list of connections and location of each neuron
        locationlist=[]
        for neurlist in MSNpop['pop']:
            for jj in range(len(neurlist)):
                neur=moose.element(neurlist[jj]+'/soma')
                neurname=neurlist[jj][rfind(neurlist[jj],'/')+1:]
                locationlist.append([neurname,neur.x,neur.y])
        savez(confile,conn=conn,loc=locationlist)

    ##### Synaptic Plasticity, requires calcium
    #### Array of SynPlas has ALL neurons of a single type in one big array.  Might want to change this
    if (calYN==1 and plasYN==1):
        SynPlas[ntype] = addPlasticity(MSNsyn[ntype]['ampa'],
                                   highThresh, lowThresh, highfactor, lowfactor,
                                   [] if single else MSNpop['pop'][nnum])
    return SynPlas
