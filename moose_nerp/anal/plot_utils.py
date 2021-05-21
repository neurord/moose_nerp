import numpy as np
from matplotlib import pyplot as plt
plt.ion()
from net_anal_class import flatten

def colornum(list_index,whole_list,colormap):
    return int(list_index*(colormap.N/len(whole_list)))

def plot_dict(measures,xaxis_vals,ylabel='',xlabel='Time (sec)',std_dict={},ftitle='',trials=1):
    colors=[plt.get_cmap('Greys'),plt.get_cmap('Blues'),plt.get_cmap('Reds'),plt.get_cmap('Purples'),plt.get_cmap('Oranges')]
    fig=plt.figure()
    fig.suptitle(ftitle)
    for i,(key, yvalues) in enumerate(measures.items()):
        colormap=i%len(colors)
        if isinstance(xaxis_vals,dict):
            if isinstance(xaxis_vals[key][0],tuple):
                xvals=[(x[0]+x[1])/2. for x in xaxis_vals[key]]
            else:
                xvals=xaxis_vals[key]
        else:
            xvals=xaxis_vals
        plt.plot(xvals,yvalues,label=key,color=colors[colormap].__call__(200))
        if len(std_dict):
            ste=np.array(std_dict[key])/np.sqrt(trials) #with  default=1, if not num trials not specified, just divide by 1
            plt.fill_between(xvals,np.array(yvalues)+ste,np.array(yvalues)-ste,facecolor=colors[colormap].__call__(100))
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.legend()

def choose_xvals(xarray,yvals,param1,param2,epoch=-1):
    if xarray is not None:
        if isinstance(xarray,dict):
            if isinstance(xarray[param1],dict): #could be dict of dict
                xvals=xarray[param1][param2]
                #print('xarray is dict of dict, with keys:',xarray[param1].keys(),ylabel,ftitle)
            else:
                xvals=xarray[param1] #could be single dict
                #print('xarray is dict, with keys:',xarray.keys(),ylabel,ftitle)
        else:
            xvals=xarray
    else:
        if epoch>-1:
            xvals=range(i*len(yvals),len(yvals)*(i+1))
        else:
            xvals=range(len(yvals))
    return xvals

def plot_dict_of_dicts(mean_dict,xarray=None,ylabel='',xlabel='Time (sec)',std_dict={},ftitle='',trials=1):
    colormap=plt.get_cmap('viridis') #'plasma','inferno'
    fig,axes =plt.subplots(len(mean_dict),1,sharex=True)
    fig.suptitle(ftitle)
    axis=fig.axes
    for i,param1 in enumerate(mean_dict.keys()): #param1 is neurtype
        for k,param2 in enumerate(mean_dict[param1].keys()): #param2 is condition
            sdvals={}
            ####################################################### 
            # Determine if there is a 3d level of dictionary
            # if so, and the 3d level has only 1 key - fine
            # else, cannot plot all the data with this function
            if isinstance(mean_dict[param1][param2],dict):
                print('3 level dictionary',param1,param2,'mean',mean_dict[param1].keys(), 'std',std_dict[param1].keys())
                if len(mean_dict[param1][param2].keys())>1:
                    print('plot_dict_of_dicts:PROBLEM - multiple epochs per condition per neuron, NO PLOTS',mean_dict[param1][param2].keys(),' for ',ftitle)
                    return
                else:
                    epoch=list(mean_dict[param1][param2].keys())[0] #if 3 level dictionary, take just the one epoch
                    yvals=np.array(mean_dict[param1][param2][epoch])
                    if len(std_dict):
                        sdvals=np.array(std_dict[param1][param2][epoch])
            else:
                yvals=np.array(mean_dict[param1][param2])
                if np.shape(np.shape(yvals))[0]==2:
                    print(' ****** Only printing first item in array of size',np.shape(yvals))
                    yvals=yvals[0]
                if len(std_dict):
                    sdvals=np.array(std_dict[param1][param2])
            xvals=choose_xvals(xarray,yvals,param1,param2)
            ####################################################### 
            main_color=colormap.__call__(colornum(k,mean_dict[param1],colormap))
            std_color=tuple([mc/4 for mc in main_color])
            axis[i].plot(xvals,yvals,color=main_color,label=str(param2))
            if len(sdvals):
                axis[i].fill_between(xvals,yvals+sdvals/np.sqrt(trials),yvals-sdvals/np.sqrt(trials),facecolor=std_color)
        axis[i].legend()
        axis[i].set_xlabel(xlabel)
        axis[i].set_ylabel(str(param1)+ ' '+ylabel)

#A. dict has N neuron keys, M condition keys - ABOVE WORKS: not dict, plots the list
#B. dict has N neuron keys, M condition keys, (and 1 epoch key) - ABOVE WORKS: plots list of 1st key
#C. dict has 1 neuron key, M condition keys - ABOVE WORKS
#C. dict has 1 neuron key, M condition keys, and P epoch keys - send in only the 1 neuron's dictionary

######### Key difference with dict_of_dict is that top key specifies trace (e.g. epoch) and second key specifies axis (e.g. param)
### could avoid this if accumulated lat_mean, etc differently 
def plot_dict_of_epochs(mean_dict,xarray=None,ylabel='',xlabel='Time (sec)',std_dict={},ftitle=''):
    colormap=plt.get_cmap('viridis') #'plasma','inferno'
    fig,axes =plt.subplots(1,1,sharex=True)
    fig.suptitle(ftitle)
    axis=fig.axes
    for i,param1 in enumerate(mean_dict.keys()): #param1 is epoch
        for k,param2 in enumerate(mean_dict[param1].keys()): #param2 is condition
            yvals=np.array(mean_dict[param1][param2])
            if len(std_dict):
                sdvals=np.array(std_dict[param1][param2])
            xvals=choose_xvals(xarray,yvals,param1,param2,epoch=i)
            main_color=colormap.__call__(colornum(k,mean_dict[param1],colormap))
            std_color=tuple([mc/4 for mc in main_color])
            if i == 0:
                axis[0].plot(xvals,yvals,color=main_color,label=str(param2))
            else:
                axis[0].plot(xvals,yvals,color=main_color)
            if len(sdvals):
                axis[0].fill_between(xvals,yvals+sdvals,yvals-sdvals,facecolor=std_color)
    axis[0].legend()
    axis[0].set_xlabel(xlabel)
    axis[0].set_ylabel(ylabel)

def plot_raster(spikes,max_time,max_trains=np.inf,ftitle='',syntt={}):
    #will plot input spikes from single trials, or output spikes
    colors=plt.get_cmap('viridis')
    fig,axes =plt.subplots(len(spikes), 1,sharex=True)
    fig.suptitle('raster \n'+ftitle)
    axis=fig.axes
    for ax,(key,spikeset) in enumerate(spikes.items()):
        #print(key,np.shape(spikeset)) 
        if len(np.shape(spikeset))==2: #multiple neurons per trial, need to reshape!
            spikeset=flatten(spikeset)
        numtrains=min(max_trains,len(spikeset))
        color_num=[colornum(cellnum,spikeset,colors) for cellnum in range(numtrains)]
        color_set=np.array([colors.__call__(color) for color in color_num])
        axis[ax].eventplot(spikeset[0:numtrains],color=color_set)
        axis[ax].set_ylabel(key)
        if key in syntt:
            xstart=syntt[key]['xstart']
            xend=syntt[key]['xend']
            axis[ax].annotate('stim onset',xy=(xstart,0),xytext=(xstart/max_time, -0.2),
                              textcoords='axes fraction', arrowprops=dict(facecolor='black', shrink=0.05))
            axis[ax].annotate('offset',xy=(xend,0),xytext=(xend/max_time, -0.2),
                              textcoords='axes fraction', arrowprops=dict(facecolor='red', shrink=0.05))
    axis[-1].set_xlim([0,max_time])
    axis[-1].set_xlabel('time (s)')

def fft_plot(alldata,maxfreq=500,phase=True,title='',mean_fft=False):
    colors=[plt.get_cmap('Greys'),plt.get_cmap('Blues'),plt.get_cmap('Reds'),plt.get_cmap('Purples'),plt.get_cmap('Oranges')]
    if phase:
        fig,axes=plt.subplots(2,1)
    else:
        fig,axes=plt.subplots(1,1)
    fig.suptitle(title+' fft')

    maxfreq_pt=np.min(np.where(alldata.freqs>maxfreq))
    minpt=1
    maxval=np.max([np.max(np.abs(f[minpt:])) for fft_set in alldata.fft_wave.values() for f in fft_set])
    for i,(epoch,fft) in enumerate(alldata.fft_wave.items()):
        mapnum=i%len(colors)
        for jj,ft in enumerate(fft):
            color=colornum(jj,fft,colors[mapnum])
            axes[0].plot(alldata.freqs[minpt:maxfreq_pt], np.abs(ft*ft)[minpt:maxfreq_pt],label=epoch,color=colors[mapnum].__call__(color))
            if phase:
                axes[1].plot(alldata.freqs[minpt:maxfreq_pt], np.angle(ft)[minpt:maxfreq_pt],'.',label=epoch,color=colors[mapnum].__call__(color))
                axes[1].set_ylabel('FFT Phase')
        if mean_fft:
            axes[0].plot(alldata.freqs[minpt:maxfreq_pt],np.abs(alldata.fft_of_mean[epoch]**2)[minpt:maxfreq_pt],color=colors[mapnum].__call__(80))
            if phase:
                axes[1].plot(alldata.freqs[minpt:maxfreq_pt],np.angle(alldata.fft_of_mean[epoch])[minpt:maxfreq_pt],'.',color=colors[mapnum].__call__(80))
    axes[0].set_ylabel('FFT Power')
    axes[0].set_ylim(0,np.round(maxval)**2 )
    axes[-1].set_xlim(0 , alldata.freqs[maxfreq_pt] )
    axes[-1].set_xlabel('Frequency in Hertz [Hz]')
    axes[0].legend()

#Triple dict of dicts of dicts
def plot_prespike_sta_cond(mean_prespike_sta,bins):
    fig,axis=plt.subplots(len(mean_prespike_sta[cond][synfreq].keys()),len(mean_prespike_sta[cond].
keys()),sharex=True)
    fig.suptitle('mean spike triggered average pre-synaptic firing')
    #need titles for each of the three columns
    for cond in mean_prespike_sta.keys():
        for axy,synfreq in enumerate(mean_prespike_sta[cond].keys()):
            for axx,(key,sta) in enumerate(mean_prespike_sta[cond][synfreq].items()):
                axis[axx,axy].plot(bins,sta,label=cond)
                axis[axx,0].set_ylabel(key)
            axis[-1,axy].set_xlabel('time (s)')
            axis[0,axy].title.set_text(synfreq)
        axis[0,0].legend()

#Triple dict of dicts of dicts, with scale and offset, either scatter or line plot
def plot_freq_dep(data,xvals,ylabel,title,num_neurs,xlabel='Time (sec)',scale=1,offset=0):
    colormap=plt.get_cmap('plasma')#'inferno'
    fig,axes =plt.subplots(len(data),num_neurs,sharex=True, sharey=True)
    fig.suptitle(title)
    axis=fig.axes
    x=xvals
    for i,presyn in enumerate(data.keys()):
        for k,freq in enumerate(sorted(data[presyn].keys())):
            #if freq.startswith('_'):
            #    freq_lbl=freq[1:]
            #else:
            freq_lbl=freq
            main_color=colormap.__call__(colornum(k,data[presyn],colormap))
            for j,ntype in enumerate(data[presyn][freq].keys()):
                if isinstance(xvals,dict):
                    x=xvals[presyn][freq][ntype]
                axisnum=i*len(data[presyn][freq].keys())+j
                if np.shape(np.shape(data[presyn][freq][ntype]))[0]==2:
                    y=np.array(data[presyn][freq][ntype][0])
                else:
                    y=np.array(data[presyn][freq][ntype])
                if xlabel=='Time (sec)':
                    axis[axisnum].plot(x[0:len(y)],scale*y+k*offset,color=main_color,label=freq_lbl)
                else:
                    axis[axisnum].scatter(x[0:len(y)],scale*y-k*offset,marker='.',color=main_color,label=freq_lbl)
                #axis[axisnum].legend(title=str(ntype))
                axis[axisnum].set_ylabel(str(presyn)+' '+ylabel)
    for j in range(num_neurs):
        axis[(len(data.keys())-1)*num_neurs+j].set_xlabel(xlabel)
    axis[0].legend(title=str(ntype))
 
def plot_cross_corr(mean_cc,mean_cc_shuffle,cc_shuffle_corrected,xbins):
    fig,axes =plt.subplots(3,1,sharex=True)
    fig.suptitle('cross correlograms ')
    for key in mean_cc.keys():
        axes[0].plot(xbins,mean_cc[key],label=key)
        axes[1].plot(xbins,mean_cc_shuffle[key],label=key)
        axes[2].plot(xbins,cc_shuffle_corrected[key],label=key)
    axes[0].set_ylabel('mean cc')
    axes[1].set_ylabel('mean cc shuffled')
    axes[2].set_ylabel('mean cc shuffled-corrected')
    axes[2].legend()
