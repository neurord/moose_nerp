import matplotlib
from matplotlib import pyplot as plt
import seaborn as sns
import numpy as np
import neo
import quantities
import elephant

plt.style.use(['seaborn-paper',
                {'axes.spines.right':False,
                 'axes.spines.top': False,
                 'figure.constrained_layout.use': True,
                 'pdf.fonttype': 3,#42
                 'ps.fonttype': 3,
                 'savefig.dpi': 300,
                 'savefig.pad_inches': 0,
                 'figure.figsize':[8,8/1.333],#[11.32,11.32/1.3333],
                 }])

def fractional_size(f,fractional_size,height=None):
    default_size = f.get_size_inches()
    if height is None:
        newsize=default_size*fractional_size
    else:
        w = default_size[0]*fractional_size
        h = default_size[1]*fractional_size*height
        newsize=(w,h)
    f.set_size_inches(newsize)

def new_fontsize(f,fs):
    axis=f.axes
    for ax in axis:
        ax.tick_params(axis='x', labelsize=fs )
        ax.tick_params(axis='y', labelsize=fs )
        ylbl=ax.get_ylabel()
        ax.set_ylabel(ylbl,fontsize=fs)
        xlbl=ax.get_xlabel()
        ax.set_xlabel(xlbl,fontsize=fs)
    axis[0].set_xlabel('Time (s)',fontsize=fs)


def input_plot(tt_Ctx_SPN,data,low,high):
    trains = [neo.SpikeTrain(train*quantities.s, t_start=-1,t_stop=22) for train in tt_Ctx_SPN[low]['spikeTime']]
    trains_high = [neo.SpikeTrain(train*quantities.s, t_start=-1,t_stop=22) for train in tt_Ctx_SPN[high]['spikeTime']]

    psth = elephant.statistics.time_histogram(trains,quantities.s*.01)
    psth_high = elephant.statistics.time_histogram(trains_high,quantities.s*.01)
    #1st trial is identical regardless of variability.  Use data['low'] to show SPN output

    ###### Plot of low and high variability 
    plt.figure()#figsize=(12,8))
    plt.eventplot(tt_Ctx_SPN[low]['spikeTime'])
    plt.xlim(0,4)
    plt.title('Low Variability')

    plt.figure()#figsize=(12,8))
    plt.eventplot(tt_Ctx_SPN[high]['spikeTime'])
    plt.xlim(0,4)
    plt.title('High Variability')

    ##### plot of 1st and 2nd trial for high variability, to visualize movement of spikes
    plt.figure()
    trial_1 = [tt[tt<1.5] for tt in tt_Ctx_SPN[high]['spikeTime']]
    trial_2 = [tt[(tt>1.5)&(tt<3.5)]-2 for tt in tt_Ctx_SPN[high]['spikeTime']]
    plt.eventplot(trial_1,label='Trial 1')
    plt.eventplot(trial_2,colors=plt.cm.tab10(1),alpha=.7,label='Trial 2');
    plt.title('Initial Trial vs. Second Trial for High Variability')
    #plt.legend()
    plt.xlim(.5,.6)
    plt.ylim(125,150)

    # f,ax = plt.subplots()
    # ax.plot(psth.times,psth)
    # ax.set_xlim(0,2)

    # ## Figure for single trial input
    f1,ax = plt.subplots(2,1,sharex=True)
    a = ax[0]
    a.eventplot(tt_Ctx_SPN[low]['spikeTime'],linewidths=1.5,linelengths=1.5)
    a.set_xlim(0,1.2)
    a.set_ylabel('Neuron #')
    a=ax[1]
    a.plot(psth.times,psth)
    a.set_xlabel('Time (s)')
    a.set_ylabel('PSTH')
    sns.despine()
    fractional_size(f1,.75)

    ####### Figure for input (spike train & PSTH) and output (SPN response) of initial trial
    f2,ax = plt.subplots(3,1,sharex=True,constrained_layout=True)
    a = ax[0]
    a.eventplot(tt_Ctx_SPN[low]['spikeTime'],linewidths=1.5,linelengths=1.5)
    a.set_xlim(0,1.2)
    a.set_ylabel('Input Neuron #')
    a=ax[1]
    a.plot(psth.times,psth)
    a.set_ylabel('PSTH')
    #sns.despine()
    fractional_size(f2,.75,2)
    a=ax[2]
    plt.plot(data['time'],data['/data/VmD1_0']*1e3)
    a.set_xlabel('Time (s)')
    a.set_ylabel('SPN Soma Vm (mV)')
    f2.align_ylabels()
    a.set_xticks([0,.2,.4,.6,.8,1.0,1.2])
    a.set_yticks([-90,-60,-30,0,30])
    sns.despine(trim=True,offset=1)
    for a,l in zip(ax,['A','B','C']):
        a.text(-.175,1,l,transform=a.transAxes,fontweight='bold')
    return f1,f2

def plot_spine_calcium_and_weight(data,spineP,spineD='',stoptime=2,xmax=1.5,camax=3,wtmax=1.5):
    dt=np.diff(data['time'][0:2])[0]
    muM = u'(μM)'
    if len(spineD):
        f,ax = plt.subplots(1,2,sharex=True,sharey=True)
    else:
        f,ax = plt.subplots(1,squeeze=True)
        ax=[ax]
    #x = data['low']['time'][0:int(stoptime/dt)]
    x = data['time'][0:int(stoptime/dt)]
    
    pot_ex_ca = '/data/D1_sp{}{}Shell_0'.format(spineP[spineP.find('headplas')-1], spineP.split('/data/D1-extern1_to_')[-1].split('-sp')[0]) 
    ax[0].plot(x, data[pot_ex_ca][0:int(stoptime/dt)]*1e3)
    ax[0].set_ylabel(r'Spine Calcium '+muM,color=plt.cm.tab10(0),fontweight='bold')
    [a.set_xlabel('Time (s)') for a in ax]
    ax[0].set_title('Potentiation')
    ax[0].set_ylim(0,camax)
    ax[0].set_xlim(0,xmax)
    if len(spineD):
        dep_ex_ca = '/data/D1_sp{}{}Shell_0'.format(spineD[spineD.find('headplas')-1], spineD.split('/data/D1-extern1_to_')[-1].split('-sp')[0]) 
        ax[1].plot(x, data[dep_ex_ca][0:int(stoptime/dt)]*1e3)
        ax[1].set_title('Depression')
    #second value is the change in threshold. Ideally specify as parameters
    pot_amp_thresh = .46*1.158
    dep_amp_thresh = 0.2*1.656
    pot_dur_thresh = .002*1.653
    dep_dur_thresh = .032*.867

    for a in ax:
        a.axhline(y=pot_amp_thresh,linestyle='--',c=plt.cm.Blues(.4),zorder=-1)
        a.axhline(y=dep_amp_thresh,linestyle='-.',c=plt.cm.Blues(.4),zorder=-1)
    ax[0].annotate('Potentiation\nThreshold',(xmax,pot_amp_thresh),(-25,25),textcoords='offset points',arrowprops={'arrowstyle':'simple'})

    ax0twin = ax[0].twinx()

    ax0twin.plot(x,data[spineP][0:int(stoptime/dt)],c=plt.cm.tab10(2))
    ax0twin.spines['right'].set_visible(True)
    ax0twin.spines['right'].set_color(plt.cm.tab10(2))
    ax0twin.spines['left'].set_visible(False) 
    ax0twin.tick_params(left=False,labelleft=False)
    ax[0].tick_params('y',color=plt.cm.tab10(0),labelcolor=plt.cm.tab10(0))
    ax0twin.spines['left'].set_color(plt.cm.tab10(0))
    ax0twin.tick_params(right=False,labelright=False) 
    fractional_size(f,[1,.75])
    if len(spineD):
        ax1twin = ax[1].twinx()
        ax1twin.plot(x,data[spineD][0:int(stoptime/dt)],c=plt.cm.tab10(2))
        ax1twin.spines['right'].set_visible(True) 
        ax1twin.spines['right'].set_color(plt.cm.tab10(2)) 
        ax[1].spines['left'].set_visible(False)
        ax1twin.set_ylabel('Synaptic Weight',color=plt.cm.tab10(2),fontweight='bold')
        ax[1].tick_params(left=False)
        ax1twin.spines['left'].set_visible(False)  
        ax0twin.spines['right'].set_visible(False)  
        ax1twin.tick_params('y',color=plt.cm.tab10(2),labelcolor=plt.cm.tab10(2))
        ax[1].annotate('Depression\nThreshold',(0,dep_amp_thresh),(-25,25),textcoords='offset points',arrowprops={'arrowstyle':'simple'})
        twinaxes=[ax0twin,ax1twin]
        ax[0].text(-.25,1.1,'A',transform=ax[0].transAxes,fontweight='bold') #do these after fractional_size, else the coordinates specified are off the graph
        ax[1].text(-.2,1.1,'B',transform=ax[1].transAxes,fontweight='bold')
    else:
        twinaxes=[ax0twin]
        ax0twin.set_ylabel('Synaptic Weight',color=plt.cm.tab10(2),fontweight='bold')
    for tw in twinaxes:
        tw.set_ylim(0.5,wtmax)
    plt.show()
    return f

################### Scatter plot and histogram of weight change at end of trials - unused figure
def weight_change_plots(weight_change_event_df,binmin=-0.2,binmax=0.2,binsize=0.01):
    #scatter plot of weight change at each trial - one panel for each different variabilitity types
    sns.catplot(x='time',y='weightchange',data=weight_change_event_df,col='trial')

    #histogram of weight change events.
    bins=[binmin+i*binsize for i in range(int((-binmin-binsize)/binsize)+1)]+[-binsize/10,binsize/10]+[binsize+i*binsize for i in range(int((binmax-binsize)/binsize)+1)]
    weight_change_event_df.hist('weightchange',bins=bins)

def weight_histogram(data):
    f,ax = plt.subplots(1,1)
    #endweight={}
    index_for_weight = (np.abs(data['time'] - 2)).argmin()
    endweight = [data[n][index_for_weight] for n in data.dtype.names if 'plas' in n]
    ax.hist(endweight,bins=20)
    ax.set_yscale('log')
    ax.set_xlabel('Synaptic weight')
    ax.set_ylabel('Number of synapses (log scale)')
    fractional_size(f,.75)
    ax.set_xlim(.59,1.3)
    sns.despine(trim=True)
    return f

def nearby_synapse_image(all_mean,binned_means,tmax=1.0,mean_sub=True,title=''):
    from scipy import ndimage
    allf=[]
    #f,axs=plt.subplots(1,1,constrained_layout=True,figsize=(8,32))
    #for ax,ar in zip(axs,[pot_mean[1:,:]-all_mean[1:,:],dep_mean[1:,:]-all_mean[1:,:]]):#,nochange_mean[1:,:]]):
    for i,(k,v) in enumerate(binned_means.items()):
        if mean_sub:
            ar = v[0:,:]-all_mean[0:,:]
            pre_title='Mean-subtracted a'
            vmin=-25
            vmax=25
        else:
            ar = v[0:,:]
            pre_title='A'
            vmin=0
            vmax=50
        f,axs=plt.subplots(1,1,constrained_layout=True,figsize=(4,3))

        ax = axs#[i]
        #print('min: ',np.min(ar),'max: ',np.max(ar))
        pc=ax.pcolormesh(ndimage.gaussian_filter(ar,[0,0]),vmin=vmin,vmax=vmax,cmap='seismic')
        ax.set_yticks([0.5,9.5,18.5])
        ax.set_yticklabels([0,9,18])
        ax.set_ylim(0,20)
        ax.set_xticklabels(np.linspace(0,tmax,5))
        if tmax==1.0:
            ax.set_xticks([0,25,50,75,100])
        else:
            xticks=np.arange(0,np.shape(ar)[1],5)
            ax.set_xticks(xticks)
        ax.set_xlabel('Time (s)',fontsize=12)
        ax.set_title('weight bin='+str(round(k[0],3))+' to '+str(round(k[1],3)),fontsize=12)
        print('nearby synapse, min: ',np.min(ndimage.gaussian_filter(ar,[0,0])), ', max: ',np.max(ndimage.gaussian_filter(ar,[0,0])))

        ax.set_ylabel('Nearest neighboring synapses',fontsize=12)
        cbar=f.colorbar(pc)
        cbar.ax.set_ylabel('Firing rate (Hz)')# instantaneous firing rate (Hz)')
        if title:
           
            f.suptitle(pre_title+'vg firing of neighbors',fontsize=19)#,y=1.075)
        allf.append(f)
    return f

def nearby_synapse_1image(all_mean,binned_means,mean_sub=True,title=False):
    from scipy import ndimage
    f,axes=plt.subplots(3,2,constrained_layout=True,figsize=(12,12))
    j=0
    for k,v in binned_means.items():
        if mean_sub:
            ar = v[0:,:]-all_mean[0:,:]
            pre_title='Mean-subtracted a'
            vmin=-25
            vmax=25
        else:
            ar = v[0:,:]
            pre_title='A'
            vmin=0
            vmax=50
        if k[0]>0 or k[1] < [0]: #skip middle bin
            if k[0]<0:
                i=0
            else:
                i=1
            jj=j%3
            ax=axes[jj,i]
            pc=ax.pcolormesh(ndimage.gaussian_filter(ar,[0,0]),vmin=vmin,vmax=vmax,cmap='seismic')
            ax.set_yticks([0.5,6.5,12.5,18.5])
            ax.set_yticklabels([0,6,12,18])
            ax.tick_params(labelsize=12)
            ax.set_ylim(0,20)
            ax.set_xticks([0,25,50,75,100])
            ax.set_xticklabels(np.linspace(0,1,5))
            ax.set_xlabel('Time (s)',fontsize=12)
            ax.set_title('weight bin='+str(round(k[0],3))+' to '+str(round(k[1],3)),fontsize=12)
            ax.set_ylabel('Neighboring synapses',fontsize=12)
            if title:            
                f.suptitle(pre_title+'verage firing rate of neighboring synapses',fontsize=14)#,y=1.075)
            j+=1
        else:
            print('skipping',k)
    cbar=f.colorbar(pc)
    cbar.ax.set_ylabel('Firing rate (Hz)')# instantaneous firing rate (Hz)')
    return f

def weight_vs_variability(data,df,titles,keys,sigma={}):
    f1,a = plt.subplots(1,5,gridspec_kw={'width_ratios':[3,3,3,3,2]}, sharey=True)
    axes=[a[0],a[1],a[2],a[3]]
    colors = plt.cm.tab10([0,1,2,3])
    colors=sns.color_palette('colorblind')[0:4]

    for i,k in enumerate(keys):
        plas_names=[nm for nm in data[k].dtype.names if 'plas' in nm]
        for n in plas_names:
            axes[i].plot(data[k]['time'][::100],data[k][n][::100],c=colors[i],linewidth=1,alpha=.7)
        axes[i].set_title(titles[i])
        axes[i].set_ylim(0,2)
        axes[i].set_xlabel('Time (s)')
    axes[0].set_ylabel('Synaptic Weight')
        #f.suptitle('Synaptic weight')

    ax=a[4]
    cs=plt.cm.tab10([0,1,2,3])
    cs=sns.color_palette('colorblind')[0:4]
    for spine in df['spine'].drop_duplicates():
        #do not plot if all trials have weight change < 0.025
        line = [ df.loc[ (df.spine == spine) & (df.trial == sv) ]['endweight'].iat[0] for sv in keys]
        #if line.count(1.0)==len(line):
        if np.any(abs(np.array(line)-1)>=0.25): #if ([l for l in line if abs(l-1)<.025]): continue
            x = np.arange(len(line))+np.random.uniform(-.1,.1)
            ax.plot(x,line,color=plt.cm.gray(.8),linewidth=.5)
            ax.scatter(x,line,marker='o',c=cs,zorder=10,s=30,edgecolor='white',alpha=.75)
    ax.axhline(1.0,color='grey',linestyle='--',linewidth=1.5)
    ax.set_xticks([0,3])
    ax.set_xticklabels(['Low','High'])
    ax.set_xlim(-1,4)
    #ax.set_ylabel('Synaptic Weight')
    ax.set_title('Final\nWeight')
    #ax.tick_params(labelrotation=90)

    ########## Figure 4 bottom panels in manuscript

    f2,ax = plt.subplots(1,2,constrained_layout=True,sharey=False)
    sns.boxplot(x='trial',y='endweight',data=df[df['endweight']<.99],ax=ax[0],palette='colorblind')

    #plt.figure()
    sns.boxplot(x='trial',y='endweight',data=df[df['endweight']>1.01],ax=ax[1],palette='colorblind')
    
    from scipy.stats import pearsonr
    if 'sigma' in titles[0]:
        df['sigma']=df.trial.map(sigma)
        group_var='sigma'
    else:
        group_var='trial'
    means=df[df['endweight']<.99].groupby(group_var).mean().endweight
    print('LTD, correlation of endweight with variability=',pearsonr(means.index,means.values))
    print('LTD, N=',len(df[df['endweight']<0.99]),'R,p=', pearsonr(df[df['endweight']<.99].endweight,df[df['endweight']<.99][group_var]))
    means=df[df['endweight']>1.01].groupby(group_var).mean().endweight
    print('LTP, N=4, correlation of endweight with variability=',pearsonr(means.index,means.values))
    print('LTP, N=',len(df[df['endweight']>1.01]),'R,p=', pearsonr(df[df['endweight']>1.01].endweight,df[df['endweight']>1.01][group_var]))
    
    # Could fit depression to ending weight vs. sigma; might be signficant
    # Specify a consistent plasticity criteria: i.e. 1% change in synaptic weight
    for a in ax:
        #a.set_xticklabels([1,10,100,200])
        if 'sigma' in titles[0]:
            a.set_xlabel('$\sigma $ (ms)')
        elif 'move' in titles[0]:
            a.set_xlabel('P(move), %')
        a.set_ylabel('Final Weight')
    ax[0].set_title('Depression')
    ax[1].set_title('Potentiation')
    return f1,f2

######################## Weight Change Triggered Average Pre-Syn firing #####################
def colorbar7(cs,binned_weight_change_index,ax,fontsize=10):
    cmap = matplotlib.colors.LinearSegmentedColormap.from_list('Custom cmap', cs,N=len(cs))
    norm = matplotlib.colors.BoundaryNorm(binned_weight_change_index, len(cs))
    ## Color bar
    #plt.colorbar.ColorbarBase(ax,cmap=cmap,norm=norm,
    #             label='Weight Change',spacing='proportional',ticks=binned_weight_change_index)
    #plt.colorbar(plt.cm.ScalarMappable(norm=plt.Normalize(vmin=binned_weight_change_index[0],vmax=binned_weight_change_index[-1]),cmap=plt.cm.coolwarm),
    #              ax=ax,label='Weight Change',spacing='proportional',ticks=binned_weight_change_index)
    cbar = plt.colorbar(plt.cm.ScalarMappable(norm=norm,cmap=cmap),
                  ax=ax,label='Weight Change',spacing='proportional',ticks=binned_weight_change_index,format='%.2f',aspect=40)

    # cbar.ax.get_yticklabels()[3].set_va('top')
    # cbar.ax.get_yticklabels()[2].set_va('top')
    # cbar.ax.get_yticklabels()[1].set_va('top')
    # cbar.ax.get_yticklabels()[0].set_va('top')
    updateticks = cbar.ax.get_yticks()
    updateticks = updateticks[[0,1,2,3,5,6,7]]
    updateticks[3]=0
    cbar.set_ticks(updateticks)
    labels = cbar.ax.get_yticklabels()
    labels[3]='$\pm0.01$'
    cbar.set_ticklabels(labels)
    cbar.ax.tick_params(labelsize=fontsize)
    
#### Combined Figure
def combined_figure(binned_pre,binned_calcium,binned_weight_change_index,duration,std=None):
    fig=plt.figure(constrained_layout=True,figsize=(6,8))
    grid=fig.add_gridspec(4,40)
    ax_pre=fig.add_subplot(grid[0:2,0:-1])
    ax_cbar=fig.add_subplot(grid[:,-1])
    ax_cal=fig.add_subplot(grid[2:4,0:-1])
    ax_cbar.spines['left'].set_visible(False)
    ax_cbar.spines['bottom'].set_visible(False)
    ax_cbar.tick_params(left=False,labelleft=False)
    ax_cbar.tick_params(bottom=False,labelbottom=False)
    cs = plt.cm.coolwarm(np.linspace(0,1,len(binned_pre)-1))
    cs =list(cs)
    cs.insert(len(binned_pre)//2,plt.cm.gray(0.5))
    ylabels=['Presynaptic Firing Rate (Hz)','Calcium Concentration (mM)']
    for ax, binned_means, ylbl in zip([ax_pre,ax_cal],[binned_pre,binned_calcium],ylabels):
        for i,(k,v) in enumerate(binned_means.items()):
            x = np.linspace(0,duration,np.shape(v)[-1])
            if len(np.shape(v))==2:
                ax.plot(x,v[0,:],c=cs[i])
            elif len(np.shape(v))==1:
                ax.plot(x,v,c=cs[i])
            else:
                print('binned means has too many dimensions')
    if std is not None:
        for ax,binned_means, stdy in zip([ax_pre,ax_cal],[binned_pre,binned_calcium], std):
            for i,(k,v) in enumerate(binned_means.items()):
                x = np.linspace(0,duration,np.shape(v)[-1])
                if len(np.shape(v))==2:
                    ax.fill_between(x, v[0,:]-stdy[k][0,:], v[0,:]+stdy[k][0,:],alpha=0.2,facecolor=cs[i])
                elif len(np.shape(v))==1:
                    ax.fill_between(x, v-stdy[k], v+stdy[k],alpha=0.2,facecolor=cs[i])
        ax.set_ylabel(ylbl,fontsize=12)
    ax_cal.set_xlabel('Time (s)',fontsize=12)
    colorbar7(cs,binned_weight_change_index,ax_cbar,fontsize=12)
    return fig,cs

def combined_spatial(combined_neighbors_array,binned_weight_change_dict,binned_weight_change_index,all_cor,cs):
    fig=plt.figure(constrained_layout=True,figsize=(6,8))
    grid=fig.add_gridspec(4,40)
    ax_neighbor=fig.add_subplot(grid[0:2,0:-1])
    ax_cbar=fig.add_subplot(grid[:,-1])
    ax_hist=fig.add_subplot(grid[2:4,0:-1])
    ax_cbar.spines['left'].set_visible(False)
    ax_cbar.spines['bottom'].set_visible(False)
    ax_cbar.tick_params(left=False,labelleft=False)
    ax_cbar.tick_params(bottom=False,labelbottom=False)
    x = np.linspace(0,1,len(combined_neighbors_array))
    for i,(k,v) in enumerate(binned_weight_change_dict.items()):
        ax_neighbor.plot(x,np.mean(combined_neighbors_array[:,v],axis=1),c = cs[i])
        ax_hist.hist(all_cor[v],histtype='step',bins=21,range=(-1,1),density=True,label=k,linewidth=2,color=cs[i],alpha=.8)
    ax_neighbor.set_ylabel('Combined Firing\n Rate of Neighbors (Hz)')
    ax_neighbor.set_xlabel('Time (s)')
    
    ax_hist.set_xlim(-1,1)
    ax_hist.set_xlabel('Correlation between Direct and Neighbors Input')
    ax_hist.set_ylabel('Normalized Histogram')
    colorbar7(cs,binned_weight_change_index,ax_cbar)
    return fig
    
#### Use 7 bins
def weight_change_trig_avg(binned_means,binned_weight_change_index,duration,std=None,cs=None,colorbar=False,title='',ylabel='Instantaneous Presynaptic Firing Rate (Hz)'):
    fig,ax = plt.subplots(1,1,constrained_layout=False)#,figsize=(12,8))
    fig.suptitle(title)
    if len(title):
        fontsize=10
    else:
        fontsize=14
    if not cs:
        cs = plt.cm.coolwarm(np.linspace(0,1,len(binned_means)-1))
        cs =list(cs)
        cs.insert(len(binned_means)//2,plt.cm.gray(0.5))
    for i,(k,v) in enumerate(binned_means.items()):
        x = np.linspace(0,duration,np.shape(v)[-1])
        if isinstance(k,tuple):
            lbl=' '.join([str(round(float(k[0]),3)),'to',str(round(float(k[1]),3))])
        else:
            lbl=k
        if len(np.shape(v))==2:
            ax.plot(x,v[0,:],c=cs[i],label=lbl)
            #if std is not None:
            #    ax.fill_between(x, v[0,:], v[0,:]+std[k][0,:],alpha=0.2,facecolor=cs[i])
        elif len(np.shape(v))==1:
            ax.plot(x,v,c=cs[i],label=lbl)
            #if std is not None:
            #    ax.fill_between(x, v, v+std[k],alpha=0.2,facecolor=cs[i])
        else:
            print('binned means has too many dimensions')
    ax.set_ylabel(ylabel)
    ax.set_xlabel('Time (s)')
    #ax.tick_params(axis='y', labelsize=12 )
    #ax.set_title('Binned Weight-change triggered\n average presynaptic firing rate')
    if not colorbar:
        ax.legend()
    else:
        colorbar7(cs,binned_weight_change_index,ax,fontsize=fontsize)
        # #cbar.ax.set_yticklabels(cbar.ax.get_yticklabels(),va='top')
        # cbar.ax.get_yticklabels()[4].set_va('bottom')
        # cbar.ax.get_yticklabels()[5].set_va('bottom')
        # cbar.ax.get_yticklabels()[6].set_va('bottom')
        # cbar.ax.get_yticklabels()[7].set_va('bottom')
    return fig,cs

def endwt_plot(df,xcolumn,xlabel,titles):
    if len(np.unique(df.trial))>10:
        leg=False
    else:
        leg='full'
    f_bcm,ax = plt.subplots()#figsize=(12,8))
    sns.scatterplot(x=xcolumn,y='endweight',data=df,hue='trial',ax=ax,palette='magma',legend=leg)
    ax.set_ylabel('Ending Synaptic Weight')
    ax.set_xlabel(xlabel)
    if 'sigma' in titles[0]:
        for i,t in enumerate(titles):
            if len(ax.get_legend().get_texts())  > len(titles):
                j=i+1
                ax.get_legend().get_texts()[0].set_text('Variability')            
            else:
                j=i
            ax.get_legend().get_texts()[j].set_text(t)
    #ax.set_title('Ending weight vs. total presynaptic spike count for every synapse')
    sns.despine(trim=True)
    return f_bcm

def fft_plot(fft_dict,freqs,binned_weight_change_index,cs=None,colorbar=False,title='',ylabel='FFT magnitude',min_pt=1,maxfreq=0.1):
    fig,ax = plt.subplots(1,1,constrained_layout=False)#,figsize=(12,8))
    fig.suptitle(title)
    if len(title):
        fontsize=10
    else:
        fontsize=14
    if not cs:
        cs = plt.cm.coolwarm(np.linspace(0,1,len(binned_means)-1))
        cs =list(cs)
        cs.insert(len(binned_means)//2,plt.cm.gray(0.5))
    for k,v in binned_means.items():
        if isinstance(k,tuple):
            lbl=' '.join([str(round(float(k[0]),3)),'to',str(round(float(k[1]),3))])
        else:
            lbl=k
        ax.plot(freqs[1:],v[min_pt:],c=cs[i],label=lbl)
    ax.set_ylabel(ylabel)
    ax.set_xlabel('Frequency (Hz)')
    ax.set_xlim([0,maxfreq])
    if not colorbar:
        ax.legend()
    else:
        colorbar7(cs,binned_weight_change_index,ax,fontsize=fontsize)
    return fig,cs
   
def rand_forest_plot(ytrain,ytest,fit,pred,title=''):
    f,axes = plt.subplots(1,2,sharey=True,sharex=True)
    axes[0].scatter(ytrain,fit)
    axes[0].set_title('train')
    #reg.score(y_train,fit)
    axes[1].set_title('test')
    axes[1].scatter(ytest,pred)
    axes[0].set_ylabel('predicted weight change')
    xmin=round(min(ytrain.min(),ytest.min()),1)
    xmax=round(max(ytrain.max(),ytest.max()),1)
    ymin=round(min(fit.min(),pred.min()),1)
    ymax=round(max(fit.max(),pred.max()),1)
    diagmin=min(xmin,ymin)
    diagmax=max(ymin,ymax)
    for ax in axes:
        ax.set_xlabel('weight change')
        ax.hlines(0,xmin,xmax,'gray','dashed')
        ax.vlines(0,ymin,ymax,'gray','dashed')
        ax.plot([diagmin,diagmax],[diagmin,diagmax],'g')
    f.suptitle(title)

def plot_features(list_features,epochs,ylabel):
    objects=[name for name,weight in list_features]
    y_pos = np.arange(len(list_features))
    performance = [weight for name, weight in list_features]
    f = plt.figure(figsize=(6,4))

    plt.bar(y_pos, performance, align='center', alpha=0.5)
    plt.xticks(y_pos, objects)
    plt.xticks(rotation=90)
    plt.ylabel(ylabel)
    plt.xlabel('Feature')
    plt.title(ylabel+' over '+epochs+' epochs')
    plt.tight_layout()

def plotPredictions(max_feat, train_test, predict_dict, class_labels, feature_order,title,colors):
    from matplotlib.colors import ListedColormap
    ########## Graph the output using contour graph
    #inputdf contains the value of a subset of features used for classifier, i.e., two different columns from df
    feature_cols = [feat[0] for feat in feature_order]
    #['r', 'b','m','gray','g','orange','cyan']
    plt.ion()
    edgecolors=['k','none']
    feature_axes=[(i,i+1) for i in range(0,max_feat,2)]
    print(feature_axes)
    for cols in feature_axes:
        plt.figure()
        plt.title(title)
        for key,col in zip(train_test.keys(),edgecolors):
            predict=predict_dict[key]
            df=train_test[key][0]
            plot_predict=[list(class_labels).index(p) for p in predict]
            plt.scatter(df[feature_cols[cols[0]]], df[feature_cols[cols[1]]], c=plot_predict,cmap=ListedColormap(colors), edgecolor=col, s=20,label=key)
            plt.xlabel(feature_cols[cols[0]])
            plt.ylabel(feature_cols[cols[1]])
            plt.legend()


def inst_wt_change_plot(weight_change_event_df,save_name=''):
    figs={}
    for xcolumn in ['isi','pre_rate']:#,'presyn_spike','postsyn_spike',]:
        f,ax = plt.subplots()
        sns.scatterplot(x=xcolumn,y='dW',data=weight_change_event_df,hue='trial',ax=ax,palette='magma',legend='full')    
        ax.set_ylabel('Weight Change',fontsize=12)
        ax.set_xlabel(xcolumn+' (sec)',fontsize=12)
        if xcolumn=='isi':
            xlim=ax.get_xlim()
            newXmin=max(-0.5,xlim[0])
            ax.set_xlim([newXmin,0.4])
        ax.tick_params(labelsize=12)
        ax.legend()
        figs[xcolumn]=f
    return figs

def dW_2Dcolor_plot(inst_weight_change):
    figs={}
    for ycolumn in ['isi2','pre_interval']:#'pre_spike2_dt'
        f,ax = plt.subplots()
        sns.scatterplot(x='isi',y=ycolumn,data=inst_weight_change,hue='dW',hue_norm=(-.0003,.0003),ax=ax,palette='seismic',legend='brief')    
        ax.set_ylabel(ycolumn,fontsize=12)
        ax.set_xlabel('ISI (sec)',fontsize=12)
        newYmin=min(max(-0.15,inst_weight_change[ycolumn].min()),0)
        newYmax=min(0.2,inst_weight_change[ycolumn].max())
        ax.set_ylim([newYmin,newYmax])
        ax.set_xlim([-0.15,0.1])
        ax.tick_params(labelsize=12)
        figs[ycolumn]=f
    return figs

 
def spiketime_plot(binned_spiketime,binned_spiketime_std,save_name='',wt_change_title=''):
    figs={}
    for kk in ['isi','pre_rate','isi2','pre_interval','pre_spike_dt']:# binned_spiketime.keys():
        f,ax = plt.subplots()
        f.suptitle(wt_change_title)
        labels=[str(round((b[0]+b[1])/2,5)) for b in binned_spiketime[kk].keys()]
        if kk.startswith('isi') or kk.startswith('pre'):
            values=binned_spiketime[kk].values()
            std=binned_spiketime_std[kk].values()
            ax.set_ylabel(kk+' (sec)',fontsize=12)
        else:   
             values=[np.log(val) for val in binned_spiketime[kk].values()]
             std=[np.log(val) for val in binned_spiketime_std[kk].values()]
             ax.set_ylabel('log('+kk+')(sec)',fontsize=12)
        ax.bar(labels,values,yerr=std)
        ax.set_xlabel('Weight Change Bin',fontsize=12)
        ax.tick_params(labelsize=12)
        figs[kk]=f
    return figs

def plot_3D_scatter(df,xname,yname,zname,binned_dict,cs):
    x={}; y={}; z={}
    for k,v in binned_dict.items():
        x[k]=df[xname].iloc[v]
        y[k]=df[yname].iloc[v]
        z[k]=df[zname].iloc[v]
    fig=plt.figure()
    ax=fig.add_subplot(projection='3d')
    for i,k in enumerate(x.keys()):
        label=' to '.join([str(round(wt,5)) for wt in k])
        ax.scatter(x[k].values,y[k].values,z[k].values,color=cs[i],label=label)
    ax.legend()
    ax.set_xlabel(xname)
    xlim=ax.get_xlim()
    ax.set_xlim([xlim[0],0.4])
    ylim=ax.get_ylim()
    ax.set_ylim([0,ylim[1]])
    ax.set_ylabel(yname)
    ax.set_zlabel(zname)
    ax.tick_params(labelsize=12)
    return fig

#3D scatter/color plot of dW (in color) vs isi1(x) vs isi2(y), or vs y=pre_dt or y = pre_interval
'''
#nothing shows up???
from mpl_toolkits.mplot3d import Axes3D
fig = plt.figure(figsize=(8, 6))
ax = fig.add_subplot(111, projection='3d')
ax.scatter(df.spikecount,df.spinedist,df.endweight)
'''
'''
# ## Synaptic Weight all trials and synapses
# f,axes = plt.subplots(10,1,sharex=True,sharey=True,figsize=(12,20))
# for i,(k,d) in enumerate(data.items()):
#     for n in d.dtype.names:
#         if 'plas' in n:
#             axes[i].plot(d['time'][::100],d[n][::100])
#     axes[i].set_title(k)
#     axes[i].set_ylim(0,2.1)
#     axes[i].set_xlabel('Time (s)')
# axes[0].set_ylabel('Synaptic Weight')
#     #f.suptitle('Synaptic weight')
# #f.savefig(path+'all_syn_weight_over_time_figure.svg')

# cs=plt.cm.tab10(range(10))
# f,ax = plt.subplots()
# for spine in df['spine'].drop_duplicates():
#     #ignore no all no change:
#     line = [ df.loc[ (df.spine == spine) & (df.trial == sv) ]['endweight'].iat[0] for sv in range(10,101,10) ]
#     #if line.count(1.0)==len(line):
#     if ([l for l in line if abs(l-1)<.01]):
#         continue
#     x = np.arange(len(line))+np.random.uniform(-.1,.1)
#     ax.plot(x,line,color=plt.cm.gray(.8),linewidth=.5)
#     ax.scatter(x,line,marker='o',c=cs,zorder=10)
# #ax.set_xticks([0,1,2])
# #ax.set_xticklabels(['Low','Intermediate','High'])
# ax.set_ylabel('Synaptic Weight')
# ax.set_title('Ending Synaptic Weight')
# #f.savefig(path+'ending_synaptic_weight_figure.svg')


###### What is this figure ???
# for n in d.dtype.names:
#     if n.endswith('tertdend5_11-sp1head'):
#         print(n)
#         plt.figure()
#         peaks,_=find_peaks(d[n])
#         raster = d['time'][peaks]
#         plt.eventplot(np.sort(raster))
#         vmpeaks,_ = find_peaks(d[[vm for vm in d.dtype.names if 'Vm' in vm][0]],height=20e-3)
#         vmraster = d['time'][vmpeaks]
#         plt.eventplot(np.sort(vmraster),lineoffsets=-1,colors='r')
#         sorted_other_stim_spines = [s.replace('_sp','-sp').replace('ecdend','secdend') for s in stimspinetospinedist['tertdend5_11_sp1head'].sort_values().index]
#         for i,other in enumerate(sorted_other_stim_spines):
#             othername = '/data/D1-extern1_to_'+other
#             otherpeaks,_ = find_peaks(d[othername])
#             raster = d['time'][otherpeaks]
#             plt.eventplot(np.sort(raster),lineoffsets=i)
# plt.figure();plt.eventplot(np.sort(raster))


for i in spine_weights.index:
    plot_spine_calcium_and_weight(i)

f,axes = plt.subplots(1,1)
axes=[axes]
for i,(k,d) in enumerate(data.items()):
     for n in d.dtype.names:
         if 'sp' in n and 'Shell' in n:
             axes[i].plot(d['time'][::50],d[n][::50])
     axes[i].set_title(k)
     break
     #axes[i].set_ylim(0,2)
# f.suptitle('Spine Calcium')
'''
