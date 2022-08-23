import numpy as np
import pandas as pd

def do_random_forest(X_train,y_train,X_test,y_test,n_est=100,feat=''):
    from sklearn.ensemble import RandomForestRegressor
    regr = RandomForestRegressor(random_state=0,n_estimators=n_est)#,max_features='sqrt')
    reg = regr.fit(X_train, y_train)
    fit = reg.predict(X_train)
    pred = reg.predict(X_test)
    print('FEATURES',feat,np.shape(X_train)[1])
    print('Training set score: ',reg.score(X_train, y_train), '    Testing Set score: ', reg.score(X_test,y_test))
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
    Xbins_adj,_=downsample_X(adjX,numbins,weight_change_event_df,num_events,add_start_wt=False)
    Xbins_combined=np.concatenate((Xbins,Xbins_adj),axis=1)
    Xbins_dist=np.concatenate((Xbins,weight_change_event_df['spine_soma_dist'].to_numpy().reshape(num_events,1)),axis=1)
    set_of_Xbins={'':Xbins,'_adj':Xbins_combined,'_dist':Xbins_dist}
    if 'cluster_length' in weight_change_event_df.columns:
        #Xbins_clust=np.concatenate((Xbins,weight_change_event_df['cluster_length'].to_numpy().reshape(num_events,1), weight_change_event_df['spines_per_cluster'].to_numpy().reshape(num_events,1)),axis=1)
        Xbins_clust=np.concatenate((Xbins,weight_change_event_df['cluster_length'].to_numpy().reshape(num_events,1)),axis=1)
        Xbins_distclust=np.concatenate((Xbins,weight_change_event_df['cluster_length'].to_numpy().reshape(num_events,1),weight_change_event_df['spine_soma_dist'].to_numpy().reshape(num_events,1)),axis=1)
        Xbins_spclust=np.concatenate((Xbins,weight_change_event_df['spines_per_cluster'].to_numpy().reshape(num_events,1)),axis=1)
        Xbins_allclust=np.concatenate((Xbins_clust,weight_change_event_df['spines_per_cluster'].to_numpy().reshape(num_events,1)),axis=1)
        set_of_Xbins={'':Xbins,'_adj':Xbins_combined,'_dist':Xbins_dist,'_clust':Xbins_clust,'_dist_clust':Xbins_distclust,'_spines':Xbins_spclust,'_spines_clustLen':Xbins_allclust}
    return set_of_Xbins,feat_lbl

def random_forest_LeaveNout(newX, adjacentX, y, weight_change_event_df,all_cor,bin_set,num_events,trials=3,linear=False):
    from sklearn.model_selection import train_test_split
    from sklearn import linear_model
    feature_types=['','_adj','_dist']
    if 'cluster_length'  in weight_change_event_df.columns:
       feature_types=feature+types+['_clust', '_dist_clust','_spines','_spines_clustLen']
    reg_score={str(bn)+k :[] for bn in bin_set for k in feature_types}
    feature_import={str(bn)+k :[] for bn in bin_set for k in feature_types}
    linreg_score={str(bn)+k :[] for bn in bin_set for k in feature_types}
    for numbins in bin_set:
        set_of_Xbins,feat_lbl=create_set_of_Xarrays(newX,adjacentX,numbins,weight_change_event_df,all_cor,num_events,lin=linear)
        for i in range(trials):
            for feat in list(set(set_of_Xbins.keys()) & set(feature_types)):
                X_train, X_test, y_train, y_test = train_test_split(set_of_Xbins[feat], y, test_size=1/trials)
                if linear:
                    linreg = linear_model.LinearRegression(fit_intercept=True).fit(X_train, y_train)
                    linreg_score[str(numbins)+feat].append({'train':linreg.score(X_train, y_train),'test':linreg.score(X_test, y_test),'coef':linreg.coef_})
                reg,fit,pred,regscore,feat_vals=do_random_forest(X_train,y_train,X_test,y_test,feat=feat)
                reg_score[str(numbins)+feat].append(regscore)
                feature_import[str(numbins)+feat].append(feat_vals)
        for feat in list(set(set_of_Xbins.keys()) & set(feature_types)):
            feature_import[str(numbins)+feat]=np.mean(feature_import[str(numbins)+feat],axis=0)
        adj_labels=['adj'+str(i)+' or other' for i in range(numbins)]
        feature_import[str(numbins)+'_features']=feat_lbl+adj_labels
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
            reg,fit,pred,regscore,feat_vals=do_random_forest(X_train,y_train,X_test,y_test,feat=feat)
            reg_score[str(numbins)+feat]=regscore
            feature_import[str(numbins)+feat]=feat_vals
            if RF_plots:
                rand_forest_plot(y_train,y_test,fit,pred,str(numbins)+' bins '+feat+wt_change_title)
        adj_labels=['adj'+str(i)+' or other' for i in range(numbins)]
        feature_import[str(numbins)+'_features']=feat_lbl+adj_labels
        
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

def RF_calcium(weight_change_alligned_ca,y,bin_set,trials):
    from sklearn.model_selection import train_test_split
    
    feat='_cal'
    ca_reg_score={str(numbins)+feat:[] for numbins in bin_set}

    for numbins in bin_set:
        Xinput=weight_change_alligned_ca.T #transpose to become trials X length of trace
        downsamp=np.shape(Xinput)[1]//numbins
        #Xbins=Xinput[:,::downsamp] #simplest is to downsample by 10
        Xbins=np.zeros((np.shape(Xinput)[0],numbins))  #Better is to average across bins
        for b in range(numbins):
            Xbins[:,b]=np.mean(Xinput[:,b*downsamp:(b+1)*downsamp],axis=1)
        for i in range(trials):
            X_train, X_test, y_train, y_test = train_test_split(Xbins, y, test_size=1/trials)
            reg,fit,pred,regscore,feat_vals=do_random_forest(X_train,y_train,X_test,y_test,feat=feat)
            ca_reg_score[str(numbins)+feat].append(regscore)
            ca_reg_score[str(numbins)+'import']=feat_vals
    return ca_reg_score

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

