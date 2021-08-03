import numpy as np
import neo
import elephant
from quantities import Hz,s
import pandas as pd

############## Create weight_change_event array, then binned spike train array, for calculating weight change triggered average ########
def weight_change_events_spikes_calcium(files,simtime,params,extern_names):
    #### This loops over every data file ######
    from scipy.signal import find_peaks
    from elephant import kernels
    neighbors=params['neighbors']
    bins_per_sec=params['bins_per_sec']
    samp_rate=params['samp_rate']
    length_of_firing_rate_vector=params['length_of_firing_rate_vector']
    ca_downsamp=params['ca_downsamp']
    ITI=params['ITI']
    down_samp=int(samp_rate/bins_per_sec)
    
    kernel = kernels.GaussianKernel(sigma=100e-3*s)
    binned_trains_index=[]
    trains = []
    numtrains=len(extern_names)*len(files) #use extern_names
    inst_rate_array = np.zeros((numtrains,int(simtime*bins_per_sec)))
    all_ca_array=[];ca_index=[]

    # dt = 0.1e-3 (.1 ms) so a stepsize of 100 data points is equivalent to 10 ms, step size of 1000 datapoints = 100 ms
    dframelist = []
    t1weight_dist={'mean':[],'std':[],'no change':[],'files':[]}
    # ## Detect weight change events
    #stepsize = 1000
    weight_at_times = np.arange(0.,simtime,ITI)
    weight_at_index = (weight_at_times*samp_rate).astype(np.int64)
    weightchangelist=[]
    for i,(tr,f) in enumerate(files.items()):  
        missing=0
        d= np.load(f,mmap_mode='r')  
        print(i, 'analyzing',tr)
        index_for_weight = (np.abs(d['time'] - 2)).argmin() #1st trial ending weight.  2 = ITI?  get weight just prior to next trial
        t1weight = [d[n][index_for_weight] for n in d.dtype.names if 'plas' in n]
        t1weight_dist['mean'].append(np.mean(t1weight))
        t1weight_dist['std'].append(np.std(t1weight))
        t1weight_dist['no change'].append(t1weight.count(1.0))
        t1weight_dist['files'].append(tr)
        plas_names=[nm for nm in d.dtype.names if 'plas' in nm] #plas names may differ for each file if using different seeds
        extern_names=[nm for nm in plas_names if 'extern1' in nm]
        for n in plas_names:
            #print(n,d[n][-1])
            endweight = d[n][-1]
            stimvariability = tr
            if '_to_' in n:
                spine = n.split('_to_')[-1].replace('-','_').strip('plas')
                stim=True
                spikecount = len(find_peaks(d[n.rstrip('plas')])[0])
            elif 'ampa' in n:
                spine = '_'.join(n.split('/')[-1].split('_')[1:-1])
                stim=False
                spikecount = 0
            weight_change_variance = np.var(np.diff(d[n]))
            spinedist = np.nan#[v for k2,v in spinedistdict.items() if spine in '_'.join(k2.split('/')[-2:]).replace('[0]','')][0]
            #print(n,spine,endweight,stimvariability,spinedist)
            dframelist.append((spine,endweight,stimvariability,spinedist,stim,spikecount,weight_change_variance))
        for j,syn in enumerate(extern_names):        
            weightchange=np.diff(d[syn][weight_at_index])
            startingweight = d[syn][weight_at_index]
            for k,w in enumerate(weightchange):
                weightchangelist.append((tr,syn,weight_at_times[k+1],startingweight[k],w))                
            peaks,_ = find_peaks(d[syn.rpartition('plas')[0]]) 
            peaktimes = d['time'][peaks]
            ### create SpikeTrain DataFrame for every trial/synapse
            train = neo.SpikeTrain(peaktimes,t_stop=simtime*s,units=s)
            trains.append(train)
            binned_trains_index.append((tr,syn))
            train.sampling_rate=samp_rate*Hz
            jj=i*len(extern_names)+j
            inst_rate_array[jj,:] = elephant.statistics.instantaneous_rate(train,train.sampling_period,kernel=kernel)[::down_samp,0].flatten()
            #extract calcium traces
            shellnum=syn.split('_3-')[0].split('_to_')[-1]
            spnum=syn.split('-sp')[-1][0]          
            shell='/data/D1_sp'+spnum+shellnum+'_3Shell_0'
            if shell in d.dtype.names:
                ca_index.append((tr,shell))
                #jj=i*len(ca_names)+j
                all_ca_array.append(d[shell][::ca_downsamp])
            else:
                missing+=1
                print(missing,shell,' NOT IN FILE',tr)
    binned_trains = elephant.conversion.BinnedSpikeTrain(trains,binsize=1e-3*s) #never used
    binned_trains_array = binned_trains.to_array() #never used
    
    df = pd.DataFrame(dframelist,columns = ['spine','endweight','Variability','spinedist','stim','spikecount','weight_change_variance'])
    weight_change_event_df = pd.DataFrame(weightchangelist,columns = ['trial','synapse','time','startingweight','weightchange'])
    return df,weight_change_event_df,inst_rate_array,trains,binned_trains_index,np.array(all_ca_array),ca_index,t1weight_dist

def add_spine_soma_dist(wce_df,df, spine_soma_dist_file):
    spine_soma_dist=pd.read_csv(spine_soma_dist_file,index_col=0)    
    wce_df['spine_soma_dist']=np.nan
    for wce in wce_df.index:
        syn = wce_df.synapse[wce]
        spine = syn.split('_to_')[-1].replace('plas','').replace('-sp','_sp')
        wce_df.loc[wce,'spine_soma_dist']=spine_soma_dist.loc[spine].distance
    for syn in df.spine:
        df.loc[df.spine==syn,'spinedist']=1e6*spine_soma_dist.loc[syn].distance #distance in um
    return wce_df,df
'''
spine_soma_dist=pd.read_csv(spine_soma_dist_file,index_col=0)    
for syn in df.spine:
    df.loc[syn,'spinedist']=spine_soma_dist.loc[syn].distance'''
#from sklearn.preprocessing import PolynomialFeatures
#from scipy.stats import binned_statistic

def do_random_forest(X_train,y_train,X_test,y_test,n_est=100):
    from sklearn.ensemble import RandomForestRegressor
    regr = RandomForestRegressor(random_state=0,n_estimators=n_est)#,max_features='sqrt')
    reg = regr.fit(X_train, y_train)
    fit = reg.predict(X_train)
    pred = reg.predict(X_test)
    print('Training set score: ',reg.score(X_train, y_train))
    print('Testing Set score: ', reg.score(X_test,y_test))
    score= {'train':reg.score(X_train,y_train),'test':reg.score(X_test,y_test)}
    return reg,fit,pred,score,reg.feature_importances_[:]

def downsample_X(Xinput,numbins,weight_change_event_df, num_events,add_start_wt=True): 
    downsamp=np.shape(Xinput)[1]//numbins
    #Xbins=Xinput[:,::downsamp] #simplest is to downsample by 10
    Xbins=np.zeros((np.shape(Xinput)[0],numbins))  #Better is to average across bins
    for b in range(numbins):
        Xbins[:,b]=np.mean(Xinput[:,b*downsamp:(b+1)*downsamp],axis=1)
    feature_labels=[str(b) for b in range(numbins)]
    if np.std(weight_change_event_df['startingweight'].to_numpy())>0 and add_start_wt:
        Xbins=np.concatenate((Xbins,weight_change_event_df['startingweight'].to_numpy().reshape(num_events,1)),axis=1)
        feature_labels.append('start_wt')
    return Xbins,feature_labels

def create_set_of_Xarrays(newX,adjX,numbins,weight_change_event_df,all_cor,num_events,lin=False):
    Xbins,feat_lbl=downsample_X(newX,numbins,weight_change_event_df,num_events)
    if lin:
        Xbins_adj,_=downsample_X(adjX,1,weight_change_event_df,num_events,add_start_wt=False)
        Xbins_combined=np.concatenate((Xbins,Xbins_adj),axis=1)
        set_of_Xbins={'':Xbins,'_adj':Xbins_combined}
    else:
        Xbins_adj,_=downsample_X(adjX,numbins,weight_change_event_df,num_events,add_start_wt=False)
        Xbins_combined=np.concatenate((Xbins,Xbins_adj),axis=1)
        Xbins_dist=np.concatenate((Xbins,weight_change_event_df['spine_soma_dist'].to_numpy().reshape(num_events,1)),axis=1)
        Xbins_corr = np.concatenate((Xbins,all_cor.reshape(num_events,1)),axis=1)
        Xbins_corr_dist=np.concatenate((Xbins_dist,all_cor.reshape(num_events,1)),axis=1)
        set_of_Xbins={'':Xbins,'_corr':Xbins_corr,'_adj':Xbins_combined,'_dist':Xbins_dist,'_corr_dist':Xbins_corr_dist}
    return set_of_Xbins,feat_lbl

def random_forest_LeaveNout(newX, adjacentX, y, weight_change_event_df,all_cor,bin_set,num_events,trials=3,linear=False):
    from sklearn.model_selection import train_test_split
    from sklearn import linear_model
    feature_types=['','_corr','_adj','_dist','_corr_dist']
    reg_score={str(bn)+k :[] for bn in bin_set for k in feature_types}
    feature_import={str(bn)+k :[] for bn in bin_set for k in feature_types}
    linreg_score={str(bn)+k :[] for bn in bin_set for k in feature_types}
    for numbins in bin_set:
        set_of_Xbins,feat_lbl=create_set_of_Xarrays(newX,adjacentX,numbins,weight_change_event_df,all_cor,num_events,lin=linear)
        for i in range(trials):
            for feat,Xarray in set_of_Xbins.items():
                X_train, X_test, y_train, y_test = train_test_split(Xarray, y, test_size=1/trials)
                if linear:
                    linreg = linear_model.LinearRegression(fit_intercept=True).fit(X_train, y_train)
                    linreg_score[str(numbins)+feat].append({'train':linreg.score(X_train, y_train),'test':linreg.score(X_test, y_test),'coef':linreg.coef_})
                reg,fit,pred,regscore,feature=do_random_forest(X_train,y_train,X_test,y_test)
                reg_score[str(numbins)+feat].append(regscore)
                if feat == '_dist': 
                    feat_list=list(feature)
                    feat_list.insert(numbins,0)
                    feature_import[str(numbins)+feat].append(np.array(feat_list))
                else:
                    feature_import[str(numbins)+feat].append(feature)
        xticks=feat_lbl+['corr','dist']
        feature_import[str(numbins)+'_features']=xticks
    return reg_score,feature_import,linreg_score

def random_forest_variations(newX, adjacentX, y, weight_change_event_df,all_cor,bin_set,num_events,wt_change_title,RF_plots,linear=False):
    from sklearn.model_selection import train_test_split
    from sklearn import linear_model
    from plas_sim_plots import rand_forest_plot
    if RF_plots:
        from matplotlib import pyplot as plt
    reg_score={}
    feature_import={}
    linreg_score={}
    for numbins in bin_set:        
        set_of_Xbins,feat_lbl=create_set_of_Xarrays(newX,adjacentX, numbins,weight_change_event_df,all_cor,num_events,lin=linear)
        print('###########',numbins,' bins,',' ##############')
        for feat,Xarray in set_of_Xbins.items():
            print('      ##',feat[1:],', features:', np.shape(Xarray)[1], ' ##')
            X_train, X_test, y_train, y_test = train_test_split(Xarray, y, test_size=0.1, random_state=42)
            if linear:
                linreg = linear_model.LinearRegression(fit_intercept=True).fit(X_train, y_train)
                print('linear score:',linreg.score(X_train, y_train),', coef:',linreg.coef_,linreg.intercept_) 
                #rfe = RFE(estimator=linear_model.LinearRegression(), n_features_to_select=1, step=1)
                #rfe.fit(X_train, y_train)
                #ranking = rfe.ranking_
                #print('selecting subset of columns',[newX.columns[ranking==i] for i in range(1,11)])
                linreg_score[str(numbins)+feat]={'score':linreg.score(X_test, y_test),'coef':linreg.coef_}
            reg,fit,pred,regscore,feature=do_random_forest(X_train,y_train,X_test,y_test)
            reg_score[str(numbins)+feat]=regscore
            if feat == '_dist':
                feat_list=list(feature)
                feat_list.insert(numbins,0)
                feature_import[str(numbins)+feat]=np.array(feat_list)
            else:
                feature_import[str(numbins)+feat]=feature
            if RF_plots:
                rand_forest_plot(y_train,y_test,fit,pred,str(numbins)+' bins '+feat+wt_change_title)
        xticks=feat_lbl+['corr','dist']
        feature_import[str(numbins)+'_features']=xticks
        
    if RF_plots:
        for numbins in bin_set:
            fimport,ax=plt.subplots()
            for regname,features in feature_import.items():
                if regname.startswith(str(numbins)) and not regname.endswith('features'):
                    ax.plot(features,label=regname+',score='+str(round(reg_score[regname]['test'],3)))
            ax.set_ylabel('feature important')
            ax.set_xticks(range(len(feature_import[str(numbins)+'_features'])))
            ax.set_xticklabels(feature_import[str(numbins)+'_features'])
            ax.set_xlabel('feature name')
            ax.legend()
    return reg_score,feature_import,linreg_score

def RF_oob(weight_change_alligned_array,all_cor,weight_change_event_df,y, RF_plots=False):
    from sklearn.model_selection import train_test_split
    from sklearn.ensemble import RandomForestRegressor
    from matplotlib import pyplot as plt
    ################### Try Random Forest with oob_score=True and max_features='sqrt' ##########
    wce_len=np.shape(weight_change_alligned_array.max(1).T[:,0])[0]
    X= weight_change_alligned_array.max(1).T[:,0].reshape(wce_len,1)
    #Xt = combined_neighbors_array.max(0).reshape(wce_len,1)
    Xt = all_cor.reshape(wce_len,1)
    X=np.concatenate((X,weight_change_event_df.startingweight.to_numpy().reshape(wce_len,1),
                      Xt,
                     ),axis=1)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.01, random_state=42)
    regr = RandomForestRegressor(100,random_state=0,oob_score=True,max_features='sqrt')
    reg = regr.fit(X_train, y_train)
    fit = reg.predict(X_train)
    pred = reg.predict(X_test)
    if RF_plots:
        f,axes = plt.subplots(1,2,sharey=True,sharex=True)
        axes[0].scatter(y_train,fit)
        xmin=round(min(y_train.min(),y_test.min()),1)
        xmax=round(max(y_train.max(),y_test.max()),1)
        ymin=round(min(fit.min(),pred.min()),1)
        ymax=round(max(fit.max(),pred.max()),1)
        diagmin=min(xmin,ymin)
        diagmax=max(ymin,ymax)
        axes[0].plot([diagmin,diagmax],[diagmin,diagmax])
        #reg.score(y_train,fit)
        axes[1].scatter(y_test,pred)
        axes[0].plot([diagmin,diagmax],[diagmin,diagmax])
        #v = [X.columns[ranking==i] for i in range(1,11)][-5][0]
        #v = 'spikecount'
        #axes[0].set_title(v)
        # axes[0].scatter(X_train[v],fit)
        # axes[0].scatter(X_train[v],y_train)
        # axes[1].scatter(X_test[v],pred)
        # axes[1].scatter(X_test[v],y_test)
    
    print('oob regression scores, train:',reg.score(X_train,y_train), 'test:',reg.score(X_test,y_test))
    print('oob score',reg.oob_score_)
    
def runClusterAnalysis(param_values, labels, num_features, class_labels,epoch):

    from sklearn import model_selection
    from sklearn.ensemble import RandomForestClassifier
    import operator

    ############ data is ready for the cluster analysis ##################
    #select a random subset of data for training, and use the other part for testing
    #sklearn.model_selection.train_test_split(*arrays, **options)
    #returns the top max_feat number of features and their weights

    df_values_train, df_values_test, df_labels_train, df_labels_test = model_selection.train_test_split(param_values, labels, test_size=0.25)
    train_test = {'train':(df_values_train,df_labels_train), 'test':(df_values_test, df_labels_test)}

    #number of estimators (n_estim) is number of trees in the forest
    #This is NOT the number of clusters to be found
    #max_feat is the number of features to use for classification
    #Empirical good default value is max_features=sqrt(num_features) for classification tasks
    max_feat=int(np.ceil(np.sqrt(num_features)))
    n_estim=20
    rtc = RandomForestClassifier(n_estimators=n_estim, max_features=max_feat)

    #This line actually builds the random forest (does the training)
    rtc.fit(df_values_train,df_labels_train)

    ###### EVALUATE THE RESULT
    #calculate a score, show the confusion matrix
    predict_dict = {}
    for nm,(df,labl) in train_test.items():
        predict = rtc.predict(df)
        predict_dict[nm] = predict
    
    #evauate the importance of each feature in the classifier
    #The relative rank (i.e. depth) of a feature used as a decision node in a tree can be used to assess the relative importance of that feature with respect to the predictability of the target variable. 
    feature_order = sorted({feature : importance for feature, importance in zip(list(df_values_train.columns), list(rtc.feature_importances_))}.items(), key=operator.itemgetter(1), reverse=True)
    return feature_order[0:max_feat],predict_dict,train_test
    
def cluster_analysis(y,X,adjX,numbins,weight_change_event_df,all_cor,epochs,num_events,cs,max_feat=2 ):
    import operator
    from sklearn.metrics import confusion_matrix
    from plas_sim_plots import plotPredictions
    classes=np.unique(y.values).astype('int')
    set_of_Xbins,feat_lbl=create_set_of_Xarrays(X,adjX, numbins,weight_change_event_df,all_cor,num_events)
    collectionBestFeatures={Xinputs:{} for Xinputs in set_of_Xbins.keys()}
    collectionTopFeatures={Xinputs:{} for Xinputs in set_of_Xbins.keys()}
    confuse_mat={Xinputs:[] for Xinputs in set_of_Xbins.keys()}
    for Xinputs,Xarray in set_of_Xbins.items():
        if Xinputs=='_corr' or Xinputs=='_dist':            
            feature_labels=feat_lbl+[Xinputs.strip('_')]
        elif Xinputs=='_corr_dist':
            feature_labels=feat_lbl+['corr','dist']
        elif Xinputs=='_adj':
            feature_labels=feat_lbl+[str(lbl)+'adj' for lbl in feat_lbl if lbl != 'start_wt']
        else:
            feature_labels=feat_lbl
        print (Xinputs,feature_labels,np.shape(Xarray))
        X_df=pd.DataFrame(Xarray,columns = feature_labels)
        num_feat=np.shape(Xarray)[1]
        for epoch in range(0, epochs):
            features, predict_dict,train_test = runClusterAnalysis(X_df,y.astype('int'),num_feat,classes,epoch)
            #print(Xinputs,epoch,'test classes', np.unique(train_test['test'][1]), 'predict classes', np.unique(predict_dict['test']),
            #      '\n',confusion_matrix(train_test['test'][1],predict_dict['test']))
            confuse_mat[Xinputs].append({'true':np.unique(train_test['test'][1]),'pred':np.unique(predict_dict['test']),'mat': confusion_matrix(train_test['test'][1],predict_dict['test'])})

            if epoch<2 and max_feat>0: #plot not working when max_feat=4
                plotPredictions(max_feat, train_test, predict_dict, classes, features,'E'+str(epoch)+'_bins'+str(numbins)+Xinputs,cs)
            for i,(feat, weight) in enumerate(features):
                #print(str(numbins),Xinputs,'feat=',feat,collectionBestFeatures[str(numbins)][Xinputs])
                #print(i,feat,weight) #monitor progress 
                if feat not in collectionBestFeatures[Xinputs]:          # How is the weight scaled? caution
                    collectionBestFeatures[Xinputs][feat] = weight
                else:
                    collectionBestFeatures[Xinputs][feat] += weight
                #print(collectionBestFeatures[str(numbins)][Xinputs])        
            f, w = features[0]
            if f not in collectionTopFeatures[Xinputs]:
                collectionTopFeatures[Xinputs][f] = 1
            else:
                collectionTopFeatures[Xinputs][f] += 1

        listBestFeatures=sorted(collectionBestFeatures[Xinputs].items(),key=operator.itemgetter(1),reverse=True)
        collectionBestFeatures[Xinputs]=listBestFeatures
        listTopFeatures=sorted(collectionTopFeatures[Xinputs].items(),key=operator.itemgetter(1),reverse=True)
        collectionTopFeatures[Xinputs]=listTopFeatures
    return collectionBestFeatures,collectionTopFeatures,confuse_mat

'''
del dframelist,weightchangelist
def calcium(files,downsamp):
    all_ca_array=[];ca_index=[]
    for i,(tr,f) in enumerate(files.items()): 
        missing=0
        d= np.load(f,mmap_mode='r')
        plas_names=[nm for nm in d.dtype.names if 'plas' in nm] #plas names may differ for each file if using different seeds
        extern_names=[nm for nm in plas_names if 'extern1' in nm]
        print(i, 'analyzing calcium for',tr)
        for j, syn in enumerate(extern_names):
            shellnum=syn.split('_3-')[0].split('_to_')[-1]
            spnum=syn.split('-sp')[-1][0]          
            shell='/data/D1_sp'+spnum+shellnum+'_3Shell_0'
            if shell in d.dtype.names:
                ca_index.append((tr,shell))
                #jj=i*len(ca_names)+j
                all_ca_array.append(d[shell][::downsamp])
            else:
                missing+=1
                print(missing,shell,' NOT IN FILE',tr)
    return ca_index, np.array(all_ca_array)


'''
