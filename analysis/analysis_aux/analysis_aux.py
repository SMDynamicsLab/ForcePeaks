# -*- coding: utf-8 -*-
"""
Created on Thu Sep 8 13:40:59 2022

@author: RLaje, ASilva
"""

import numpy as np
import matplotlib.pyplot as plt
import glob
import pandas as pd
import json
import sys
# Setting path.
sys.path.append('../experiment')
# Importing.
import tappinduino as tp
import seaborn as sns
import scipy.stats as stats
import statsmodels.stats.multitest as sm
from statsmodels.stats.multitest import multipletests


#%% Load_SubjectExpMetadata.
# Function to load experiment subject metadata. Return a dataframe.
# subject_number --> int (ej: 0). path --> string (ej: '../data_aux/Experiment_PS_SC/'). total_blocks --> int (ej: 1).
def Load_SubjectMetadata(subject_number, path, total_blocks):
    s_number = '{0:0>3}'.format(subject_number)
    conc_block_conditions_df = pd.DataFrame()
    for i in range(total_blocks):
        file_to_load = glob.glob(path + 'S'+s_number+"*-block"+str(i)+"-trials.csv")
        if (len(file_to_load) != 0):
            file_to_load = glob.glob(path + 'S'+s_number+"*-block"+str(i)+"-trials.csv")[0]
            file_to_load_df = pd.read_csv(file_to_load)
            conc_block_conditions_df = pd.concat([conc_block_conditions_df, file_to_load_df]).reset_index(drop = True)
    return conc_block_conditions_df


#%% Load_ExpMetadata.
# Function to load experiment metadata. Return a dataframe.
# path --> string (ej: '../data_aux/Experiment_PS_SC/'). n_blocks --> int (ej: 1).
def Load_ExpMetadata(path, n_blocks):
    filename_names = path + 'Dic_names.dat'
    with open(filename_names) as f_names:
       total_subjects = sum(1 for line in f_names) - 1
    f_names.close()
    conc_blocks_conditions_df = pd.DataFrame()
    for i in range(total_subjects):
        blocks_conditions_df = Load_SubjectMetadata(i, path, n_blocks)    
        conc_blocks_conditions_df = pd.concat([conc_blocks_conditions_df, blocks_conditions_df]).reset_index(drop = True)
    conc_blocks_conditions_df.to_csv(path + 'ExpMetaData.csv',na_rep = np.NaN)
    return conc_blocks_conditions_df


#%% Load_SingleTrial.
# Function to load trial data from trial data file. Return a dataframe.
# subject_number --> int (ej: 0). path --> string (ej: '../data_aux/Experiment_PS_SC/'). block --> int (ej: 1). trial --> int (ej: 2).
def Load_SingleTrial(subject_number, path, block, trial):
    s_number = '{0:0>3}'.format(subject_number)
    file_to_load = glob.glob(path + 'S'+s_number+"*-block"+str(block)+"-trial"+str(trial)+".dat")[0]
    f_to_load = open(file_to_load,"r")
    content = f_to_load.read()
    f_to_load.close()
    content = json.loads(content)

    trialData_df = pd.DataFrame(columns=['Subject', 'Block', 'Trial', 'Event', 'Event_Order', 'Assigned_Stim', 'Time'], index=range(len(content['Stim_time'])))
    trialData_df['Subject'] = subject_number
    trialData_df['Block'] = block
    trialData_df['Trial'] = trial
    trialData_df['Event'] = 'S'
    trialData_df['Event_Order'] = range(0,len(content['Stim_time']))
    trialData_df['Time'] = content['Stim_time']
    
    trialDataAux_df = pd.DataFrame(columns=['Subject', 'Block', 'Trial', 'Event', 'Event_Order', 'Assigned_Stim', 'Time'], index=range(len(content['Resp_time'])))
    trialDataAux_df['Subject'] = subject_number
    trialDataAux_df['Block'] = block
    trialDataAux_df['Trial'] = trial
    trialDataAux_df['Event'] = 'R'
    trialDataAux_df['Event_Order'] = range(0,len(content['Resp_time']))
    trialDataAux_df['Time'] = content['Resp_time']

    trialData_df = pd.concat([trialData_df, trialDataAux_df]).reset_index(drop = True)

    trialDataAux_df = pd.DataFrame(columns=['Subject', 'Block', 'Trial', 'Event', 'Event_Order', 'Assigned_Stim', 'Time'], index=range(len(content['Asynchrony'])))
    trialDataAux_df['Subject'] = subject_number
    trialDataAux_df['Block'] = block
    trialDataAux_df['Trial'] = trial
    trialDataAux_df['Event'] = 'A'
    trialDataAux_df['Assigned_Stim'] = content['Stim_assigned_to_asyn']
    trialDataAux_df['Time'] = content['Asynchrony']
    
    trialData_df = pd.concat([trialData_df, trialDataAux_df]).reset_index(drop = True)
    return trialData_df


#%% Load_TrialsData.
# Function to load trials data. Return a dataframe.
# path --> string (ej: '../data_aux/Experiment_PS_SC/'). n_blocks --> int (ej: 1).
def Load_TrialsData(path, n_blocks):
    expMetadata_df = Load_ExpMetadata(path, n_blocks)
    conc_trialData_df = pd.DataFrame()
    for i in range(len(expMetadata_df.index)): 
        subject_number = expMetadata_df['Subject'][i]
        block = expMetadata_df['Block'][i]
        trial = expMetadata_df['Trial'][i]
        trialData_df = Load_SingleTrial(subject_number, path, block, trial)
        conc_trialData_df = pd.concat([conc_trialData_df, trialData_df]).reset_index(drop = True)
    return conc_trialData_df


#%% Load_AllAsynchronies_AllValidTrials.
# Function to load asynchronies from valid trials. Return a dataframe.
# path --> string (ej: '../data_aux/Experiment_PS_SC/'). n_blocks --> int (ej: 1).
def Load_AllAsynchronies_AllValidTrials(path, n_blocks):
    expMetaData_df = Load_ExpMetadata(path, n_blocks)
    trialsData_df = Load_TrialsData(path, n_blocks)
    result_df = pd.merge(expMetaData_df, trialsData_df, on=["Subject", "Block", "Trial"])
    result_df = result_df[(result_df['Valid_trial'] == 1) & (result_df['Event'] == 'A')].reset_index().drop(columns = ['index'])
    result_df['Relative_beep'] = result_df['Assigned_Stim'] - result_df['Perturb_bip']
    result_df.drop(columns = ['Original_trial', 'Perturb_type','Perturb_size', 'Valid_trial', 'Message', 'Error', 'Event', 'Event_Order'], inplace = True)
    result_df = result_df.reindex(columns=['Subject', 'Block', 'Trial', 'Condition', 'Assigned_Stim', 'Relative_beep', 'Perturb_bip', 'Time'])
    return result_df


#%% Experiments_Parameters
# Function to load all experiments parameters. Return a nested dictionary.
# path --> string (ej: '../data_aux/'). 
def Experiments_Parameters(path):
    
    # Define path.
    path_list = glob.glob(path + 'Experiment' + '*')

    # Experiment Parameters.
    file_to_load = []
    content_dict = {}
    for i in range(len(path_list)):
        try:
            file_to_load = path_list[i] + '/Experiment_parameters.dat'
            f_to_load = open(file_to_load,"r")
            content = f_to_load.read()
            f_to_load.close()
            content_dict[str(i)] = json.loads(content)
        except:
            print('Warning: Para ' + file_to_load + ' no existe el archivo Experiment_parameters.dat')
    return content_dict


#%%










#%% Preprocessing data version 1: Preperturbation zeroed. At the end, outlier cuantification. 

#%% Asyn_Zeroed
# Complementary function of the function Preprocessing_Data to bring asynchrony to zero. Return a dataframe.
# data_df --> dataframe. n_subjects --> int (ej: 2). n_blocks --> int (ej: 3). 
def Asyn_Zeroed(data_df):
    
    data_mean_aux_df = pd.DataFrame()
    n_experiments = sorted((pd.unique(data_df['Experiment'])).tolist())
    for experiment in n_experiments:
        data_aux_df = data_df[(data_df['Experiment'] == experiment)]
        n_subjects = sorted((pd.unique(data_df['Subject'])).tolist())
        for subject in n_subjects:
            data_aux2_df = data_aux_df[(data_aux_df['Subject'] == subject)]
            n_blocks = sorted((pd.unique(data_aux2_df['Block'])).tolist())
            for block in n_blocks:
                data_aux3_df = data_aux2_df[(data_aux2_df['Block'] == block)]
                n_trials = sorted((pd.unique(data_aux3_df['Trial'])).tolist())
                for trial in n_trials:
                    data_aux4_df = data_aux3_df[(data_aux3_df['Trial'] == trial)].reset_index(drop = True)
                    perturb_bip = int(data_aux4_df['Perturb_bip'][0])
                    data_aux5_df = data_aux4_df[(data_aux4_df['Assigned_Stim'] < perturb_bip)]
                    data_mean_aux_df = pd.concat([data_mean_aux_df, data_aux5_df]).reset_index(drop = True)
    
    data_mean_df = data_mean_aux_df.groupby(["Experiment", "Subject", "Block", "Trial", "Condition"], as_index = False)["Time"].mean()
    data_mean_df.rename(columns={"Time": "Asyn_mean"}, inplace = True)
    
    result_df = pd.merge(data_df, data_mean_df, on=["Experiment", "Subject", "Block", "Trial", "Condition"])
    result_df["Asyn_zeroed"] = result_df["Time"] - result_df["Asyn_mean"]
    result_df = result_df.drop(columns = ['Perturb_bip', 'Asyn_mean'])
        
    return result_df


#%% Preprocessing_Data
# Function to process data for all experiments and general conditions dictionary, 
# considering the transient and the beeps out of range. Return tuple with two dataframes.
# path --> string (ej: '../data_aux/'). transient_dur --> int (ej: 1).
def Preprocessing_Data(path, transient_dur): 

    # Experiments Parameters.
    experiments_parameters_dict = Experiments_Parameters(path)
    exp_index_list = list(experiments_parameters_dict.keys())

    general_cond_dict_df = pd.DataFrame()
    general_proc_data_df = pd.DataFrame()
    for i in exp_index_list:
        # Experiment Parameters.
        n_blocks = experiments_parameters_dict[i]['n_blocks']                                                       # Number of blocks.
        perturb_type_dictionary = experiments_parameters_dict[i]['perturb_type_dictionary']				            # Perturbation type dictionary. 1--> Step change. 2--> Phase shift.                                     
        perturb_size_dictionary = experiments_parameters_dict[i]['perturb_size_dictionary']				            # Perturbation size dictionary.
        data_path = experiments_parameters_dict[i]['path']                                                          # Data path.
        
        # General conditions dictionary.
        exp_name_index = data_path.find('Experiment')
        experiment_name = data_path[exp_name_index:-1]
        condition_dictionary_df = tp.Condition_Dictionary(perturb_type_dictionary, perturb_size_dictionary)         # Possible conditions dictionary per experiment.
        condition_dictionary_df = condition_dictionary_df.assign(Experiment = int(i), Exp_name = experiment_name)
        general_cond_dict_df = pd.concat([general_cond_dict_df, condition_dictionary_df]).reset_index(drop = True)
        
        # General process data.
        processing_data_df = Load_AllAsynchronies_AllValidTrials(data_path, n_blocks)                                    # Process data per experiment.
        processing_data_df = processing_data_df.assign(Experiment = int(i))
        general_proc_data_df = pd.concat([general_proc_data_df, processing_data_df]).reset_index(drop = True)

    general_cond_dict_df.index.name = "General_condition"
    general_cond_dict_df.reset_index(inplace = True)

    result_df = pd.DataFrame()
    result_df = pd.merge(general_cond_dict_df, general_proc_data_df, on=["Experiment", "Condition"])
    result_df = result_df.reindex(columns=['Exp_name', 'Experiment', 'Subject', 'Block', 'Trial', 'General_condition', 'Condition', 'Assigned_Stim', 'Relative_beep', 'Time', 'Perturb_bip'])
    result_df.sort_values(['Experiment', 'Subject', 'Block', 'Trial'], inplace = True)
    result_df.reset_index(drop = True, inplace = True)

    # Find first and last stim of every trial.
    result_df["First_beep"] = result_df.groupby(["Experiment", "Subject", "Condition", "Trial"])["Relative_beep"].transform(min)
    result_df["Last_beep"] = result_df.groupby(["Experiment", "Subject", "Condition", "Trial"])["Relative_beep"].transform(max)
    
    # Keep beeps after transient only.
    result_df.query("Relative_beep >= First_beep + @transient_dur", inplace=True)
    
    # Find first and last COMMON stim for all trials. The first beeps of the trial are discarded.
    result_df.drop(columns=["First_beep"], inplace=True)
    result_df["First_beep"] = result_df.groupby(["Experiment", "Subject", "Condition", "Trial"])["Relative_beep"].transform(min)
    result_df["First_common_beep"] = result_df["First_beep"].agg(max)
    result_df["Last_common_beep"] = result_df["Last_beep"].agg(min)

    # Keep common beeps only. If the relative beep falls outside the range of common beeps, the asynchrony is discarded.
    result_df.query("Relative_beep >= First_common_beep & Relative_beep <= Last_common_beep", inplace=True)
    
    # Remove unused columns.
    result_df.drop(columns=["First_beep","Last_beep","First_common_beep","Last_common_beep"], inplace=True)
    result_df = result_df.reset_index(drop=True)
    
    # Asynchronies zeroed.
    data_df = Asyn_Zeroed(result_df)

    return general_cond_dict_df, data_df


#%% Preprocessing_Data_AllExperiments_MarkingOutliers
# Function to process data for all experiments and general conditions dictionary, marking outlier trials. Return a tuple with three dataframes.
# path --> string (ej: '../data_aux/'). data_df --> dataframe. postPerturb_bip --> int (ej: 5).
def Preprocessing_Data_AllExperiments_MarkingTrialOutliers(path, data_df, postPerturb_bip):

    # Experiments dictionary and data
    general_cond_dict_df = data_df[0]
    general_proc_data_df = data_df[1]

    # Keep beeps after postPerturb_bip only
    postPerturb_bip_df = general_proc_data_df.query("Relative_beep >= @postPerturb_bip")

    # Data mean per each trial across beeps
    data_mean_df = (postPerturb_bip_df
                          # First average across trials.
                          .groupby(["Experiment", "Subject", "Condition", "Block", "Trial"], as_index=False)
                          .agg(mean_asyn=("Asyn_zeroed","mean"),std_asyn=("Asyn_zeroed","std")))

    # Applying quantile criteria
    data_mean_df["Outlier_trial_meanAsyn"] = 0
    data_mean_df["Outlier_trial_std"] = 0   
    data_mean_outlier_df = pd.DataFrame()
    n_experiments = sorted((pd.unique(general_proc_data_df['Experiment'])).tolist())
    for experiment in n_experiments:
        quantile_data_aux_df = general_proc_data_df[general_proc_data_df['Experiment'] == experiment]
        n_subjects = sorted((pd.unique(quantile_data_aux_df['Subject'])).tolist())
        for subject in n_subjects:
            n_conditions = sorted((pd.unique(quantile_data_aux_df['Condition'])).tolist())
            for condition in n_conditions:
                quantile_data_df = data_mean_df[(data_mean_df['Experiment'] == experiment) & (data_mean_df['Subject'] == subject)
                                                   & (data_mean_df['Condition'] == condition)].reset_index(drop = True)
                
                quantile_data_df["Outlier_trial_meanAsyn"] = 0
                quantile_data_df["Outlier_trial_std"] = 0
                                
                quantile = quantile_data_df.mean_asyn.quantile([0.25,0.5,0.75])
                Q1 = quantile[0.25]
                Q3 = quantile[0.75]
                IQR = Q3 - Q1             
                quantile_data_df.loc[quantile_data_df.mean_asyn < (Q1 - 1.5 * IQR),'Outlier_trial_meanAsyn'] = 1
                quantile_data_df.loc[quantile_data_df.mean_asyn > (Q3 + 1.5 * IQR),'Outlier_trial_meanAsyn'] = 1
                
                quantile = quantile_data_df.std_asyn.quantile([0.25,0.5,0.75])
                Q1 = quantile[0.25]
                Q3 = quantile[0.75]
                IQR = Q3 - Q1             
                quantile_data_df.loc[quantile_data_df.std_asyn < (Q1 - 1.5 * IQR),'Outlier_trial_std'] = 1
                quantile_data_df.loc[quantile_data_df.std_asyn > (Q3 + 1.5 * IQR),'Outlier_trial_std'] = 1
                
                # Trial mean
                data_mean_outlier_df = pd.concat([data_mean_outlier_df, quantile_data_df]).reset_index(drop = True)
    data_mean_outlier_df.drop(columns = ["mean_asyn", "std_asyn"], inplace = True)
    
    # Experiments data with meanAsyn and STD outlier trials marked
    result_df = pd.merge(general_proc_data_df, data_mean_outlier_df, on=["Experiment", "Subject", "Block", "Trial", "Condition"])
 
    # Data Search trials outliers
    data_aux_df = data_mean_outlier_df[(data_mean_outlier_df['Outlier_trial_meanAsyn'] == 1) | (data_mean_outlier_df['Outlier_trial_std'] == 1)].reset_index(drop = True)
    data_aux_df['Outlier'] = 1
    data_aux_df = (data_aux_df.groupby(["Experiment", "Subject", "Condition"], as_index=False).agg(Total_outlier_trial_mean = ("Outlier_trial_meanAsyn", "sum"), Total_outlier_trial_std = ("Outlier_trial_std", "sum"), Total_outlier = ("Outlier", "sum")))
    
    # Total trials per experiment, per subject and per condition
    data_aux2_df = data_mean_outlier_df.reset_index(drop = True)
    data_aux2_df['Trials'] = 1 
    data_aux2_df = (data_aux2_df.groupby(["Experiment", "Subject", "Condition"], as_index=False).agg(Total_trials = ("Trials", "sum")))

    # Porcentual outlier trials per experiment, per subject and per condition
    data_porcOutTrials_df = pd.merge(data_aux_df, data_aux2_df, on=["Experiment", "Subject", "Condition"])
    data_porcOutTrials_df['Total_outlier_trial_porc'] = (data_porcOutTrials_df['Total_outlier'] * 100) / data_porcOutTrials_df['Total_trials']
    
    return general_cond_dict_df, result_df, data_porcOutTrials_df


#%% Outliers_Trials_Cuantification
# Function to know outlier trials information.
# path --> string (ej: '../data_aux/'). data_OutTrials_df --> dataframe.
def Outliers_Trials_Cuantification(path, data_OutTrials_df):
    
    # Experiments dictionary and data
    general_proc_data_df = data_OutTrials_df[1]
    data_porcOutTrials_df = data_OutTrials_df[2]
        
    # Total trials per experiment and per subject
    data_aux_df = general_proc_data_df.reset_index(drop = True)
    data_aux_df['Trials'] = 1
    data_aux_df = (data_aux_df.groupby(["Experiment", "Subject", "Condition", "Block", "Trial"], as_index=False).agg(Trials = ("Trials", "max")))
    data_aux_df = (data_aux_df.groupby(["Experiment", "Subject"], as_index=False).agg(Total_trials = ("Trials", "sum")))
            
    # Outlier trials per experiment and per subject
    data_aux2_df = data_porcOutTrials_df.reset_index(drop = True)
    data_aux2_df = (data_aux2_df.groupby(["Experiment", "Subject"], as_index=False).agg(Total_outliers = ("Total_outlier", "sum")))

    # Porcentual outlier trials per experiment and per subject
    data_aux3_df = pd.merge(data_aux_df, data_aux2_df, on=["Experiment", "Subject"])
    data_aux3_df['Total_outlier_trials_porc'] = (data_aux3_df['Total_outliers'] * 100) / data_aux3_df['Total_trials']
    
    # Total trials per experiment
    data_aux4_df = (data_aux_df.groupby(["Experiment"], as_index=False).agg(Total_trials = ("Total_trials", "sum")))

    # Outlier trials per experiment
    data_aux5_df = (data_aux2_df.groupby(["Experiment"], as_index=False).agg(Total_outliers = ("Total_outliers", "sum")))
        
    # Porcentual outlier trials per experiment
    data_aux6_df = pd.merge(data_aux4_df, data_aux5_df, on=["Experiment"])
    data_aux6_df['Total_outlier_trial_porc'] = (data_aux6_df['Total_outliers'] * 100) / data_aux6_df['Total_trials']
    
    # Total subjects with outlier trials    
    data_aux7_df = pd.DataFrame({'Total_subects': [len(data_aux2_df['Subject'])]})
        
    # Subjects with more outlier trials
    data_aux8_df = data_aux3_df[(data_aux3_df['Total_outliers'] == data_aux3_df.Total_outliers.max())].reset_index(drop = True)
    
    # Porcentual subjects with more outlier trials %
    data_aux9_df = data_aux3_df[(data_aux3_df['Total_outlier_trials_porc'] == data_aux3_df.Total_outlier_trials_porc.max())].reset_index(drop = True)

    # Save files
    data_porcOutTrials_df.to_csv(path + "porc_outlier_trials_perExp_perSubj_perCond.csv", na_rep = np.NaN)
    data_aux3_df.to_csv(path + "porc_outlier_trials_perExp_perSubj.csv", na_rep = np.NaN)
    data_aux6_df.to_csv(path + "porc_outlier_trials_perExp.csv", na_rep = np.NaN)
    data_aux7_df.to_csv(path + "total_subj_with_outlier_trials.csv", na_rep = np.NaN)
    data_aux8_df.to_csv(path + "subj_with_more_outlier_trials.csv", na_rep = np.NaN)
    data_aux9_df.to_csv(path + "subj_with_more_outlier_trials_porc.csv", na_rep = np.NaN)
    
    return


#%% Preprocessing_Data_AllExperiments_MarkingSubjCondOutliers
# Function to process data for all experiments and general conditions dictionary, marking outlier subject conditions. Return a tuple with four dataframes.
# path --> string (ej: '../data_aux/'). data_OutTrials_df--> dataframe. porcTrialPrevCond --> int (ej: 10). postPerturb_bip --> int (ej: 5).
def Preprocessing_Data_AllExperiments_MarkingSubjCondOutliers(path, data_OutTrials_df, porcTrialPrevCond, postPerturb_bip):

    # Experiments dictionary and data
    general_cond_dict_df = data_OutTrials_df[0]
    general_proc_data_df = data_OutTrials_df[1]
    data_porcOutTrials_df = data_OutTrials_df[2]
  
    # Applying porcentual previous outlier trials conditions criteria
    general_proc_data2_aux_df = data_porcOutTrials_df.reset_index(drop = True) 
    general_proc_data2_aux_df["Outlier_trial_porcPrevCond"] = 0
    general_proc_data2_aux_df.loc[general_proc_data2_aux_df.Total_outlier_trial_porc > porcTrialPrevCond,'Outlier_trial_porcPrevCond'] = 1
    general_proc_data2_aux_df = general_proc_data2_aux_df.reset_index(drop = True).drop(columns = ['Total_outlier_trial_mean', 'Total_outlier_trial_std', 'Total_outlier', 'Total_trials', 'Total_outlier_trial_porc'])
    
    # Experiments data with meanAsyn, STD, procentual outlier trials marked
    general_proc_data2_aux2_df = general_proc_data_df.groupby(["Experiment", "Subject", "Condition"], as_index=False).agg(Outlier_trial_meanAsyn = ("Outlier_trial_meanAsyn", "max"), Outlier_trial_std = ("Outlier_trial_std", "max"))
    general_proc_data2_aux2_df = general_proc_data2_aux2_df[(general_proc_data2_aux2_df['Outlier_trial_meanAsyn'] == 0) & (general_proc_data2_aux2_df['Outlier_trial_std'] == 0)]
    general_proc_data2_aux2_df["Outlier_trial_porcPrevCond"] = 0
    general_proc_data2_aux2_df = general_proc_data2_aux2_df.reset_index().drop(columns = ['Outlier_trial_meanAsyn', 'Outlier_trial_std'])
    general_proc_data2_aux3_df = pd.concat([general_proc_data2_aux_df, general_proc_data2_aux2_df]).reset_index(drop = True)
    general_proc_data2_aux3_df = general_proc_data2_aux3_df.reset_index().drop(columns = ['index', 'level_0'])
    general_proc_data2_df = pd.merge(general_proc_data_df, general_proc_data2_aux3_df, on=["Experiment", "Subject", "Condition"])

    # Searching data without outlier trials
    particular_exp_data_df = general_proc_data2_df[(general_proc_data2_df['Outlier_trial_meanAsyn'] == 0) & (general_proc_data2_df['Outlier_trial_std'] == 0) & 
                                               (general_proc_data2_df['Outlier_trial_porcPrevCond'] == 0)].reset_index(drop = True)
    perSubjAve_df = (particular_exp_data_df
                          # Average across trials without outlier trials and outlier subj cond.
                          .groupby(["Experiment", "Subject", "General_condition", "Condition", "Relative_beep"], as_index=False)
                          .agg(mean_asyn=("Asyn_zeroed","mean")))

    # Keep beeps after postPerturb_bip only
    postPerturb_bip_df = perSubjAve_df.query("Relative_beep >= @postPerturb_bip")
        
    # Mean valid trials asyn all subjects per conditions and mean of the last ones
    data_mean_df = (postPerturb_bip_df
                          # First average across trials.
                          .groupby(["Experiment", "Subject", "General_condition", "Condition"], as_index=False)
                          .agg(mean_asyn=("mean_asyn","mean"),std_asyn=("mean_asyn","std")))

    # Applying quantile criteria
    data_mean_df["Outlier_subj_meanAsyn"] = 0
    data_mean_df["Outlier_subj_std"] = 0   
    data_mean_outlier_df = pd.DataFrame()
    n_experiments = sorted((pd.unique(data_mean_df['Experiment'])).tolist())
    for experiment in n_experiments:
        quantile_data_aux_df = data_mean_df[data_mean_df['Experiment'] == experiment]
        n_conditions = sorted((pd.unique(quantile_data_aux_df['Condition'])).tolist())
        for condition in n_conditions:
            quantile_data_df = data_mean_df[(data_mean_df['Experiment'] == experiment) & (data_mean_df['Condition'] == condition)].reset_index(drop = True)
                        
            quantile = quantile_data_df.mean_asyn.quantile([0.25,0.5,0.75])
            Q1 = quantile[0.25]
            Q3 = quantile[0.75]
            IQR = Q3 - Q1             
            quantile_data_df.loc[quantile_data_df.mean_asyn < (Q1 - 1.5 * IQR),'Outlier_subj_meanAsyn'] = 1
            quantile_data_df.loc[quantile_data_df.mean_asyn > (Q3 + 1.5 * IQR),'Outlier_subj_meanAsyn'] = 1
                
            quantile = quantile_data_df.std_asyn.quantile([0.25,0.5,0.75])
            Q1 = quantile[0.25]
            Q3 = quantile[0.75]
            IQR = Q3 - Q1             
            quantile_data_df.loc[quantile_data_df.std_asyn < (Q1 - 1.5 * IQR),'Outlier_subj_std'] = 1
            quantile_data_df.loc[quantile_data_df.std_asyn > (Q3 + 1.5 * IQR),'Outlier_subj_std'] = 1
            
            # Exp Subj Cond mean
            data_mean_outlier_df = pd.concat([data_mean_outlier_df, quantile_data_df]).reset_index(drop = True)
    
    # General processing data with meanAsyn and STD outlier subj cond marked
    data_mean_outlier2_df = data_mean_outlier_df.drop(columns = ['General_condition', 'mean_asyn', 'std_asyn'])
    data_mean_outlier3_df = general_proc_data2_aux_df[(general_proc_data2_aux_df['Outlier_trial_porcPrevCond'] == 1)].reset_index(drop = True)
    data_mean_outlier3B_df = data_mean_outlier3_df.drop(columns = ["Outlier_trial_porcPrevCond"])
    data_mean_outlier3B_df["Outlier_subj_meanAsyn"] = 0
    data_mean_outlier3B_df["Outlier_subj_std"] = 0
    data_mean_outlier4_df = pd.concat([data_mean_outlier2_df, data_mean_outlier3B_df]).reset_index(drop = True)
    general_proc_data3_df = pd.merge(general_proc_data2_df, data_mean_outlier4_df, on=["Experiment", "Subject", "Condition"]).reset_index(drop = True)

    # General processing data without outlier trials.  
    general_proc_WithoutOutlierTrials_df = general_proc_data3_df[(general_proc_data3_df['Outlier_trial_meanAsyn'] == 0) & (general_proc_data3_df['Outlier_trial_std'] == 0)].reset_index(drop = True)

    # Total conditions per experiment.
    gen_cond_df = general_cond_dict_df.reset_index(drop = True)
    gen_cond_df["Total_conditions"] = 1
    gen_cond_df = (gen_cond_df.groupby(["Experiment"], as_index=False).agg(Total_conditions = ("Total_conditions", "sum")))

    # Total outlier conditions per trials analysis.
    result_df = data_mean_outlier3_df.groupby(["Experiment", "Subject"], as_index = False).agg(Total_outlier_trial_conditions = ("Outlier_trial_porcPrevCond", "sum"))
    result_df = pd.merge(gen_cond_df, result_df, on=["Experiment"]).reset_index(drop = True)

    # Total outlier conditions per subj cond per meanAsyn and STD analysis.
    result2_df = data_mean_outlier_df[(data_mean_outlier_df['Outlier_subj_meanAsyn'] == 1) | (data_mean_outlier_df['Outlier_subj_std'] == 1)].reset_index(drop = True)    
    result2_df['Total_outlier_subj_conditions'] = 1
    result2_df = result2_df.groupby(["Experiment", "Subject", "Condition"], as_index = False).agg(Total_outlier_subj_conditions = ("Total_outlier_subj_conditions", "max"))
    result2_df = result2_df.groupby(["Experiment", "Subject"], as_index = False).agg(Total_outlier_subj_conditions = ("Total_outlier_subj_conditions", "sum"))
    result2_df = pd.merge(result2_df, gen_cond_df, on=["Experiment"]).reset_index(drop = True)
    result_df["Total_outlier_subj_conditions"] = 0
    result2_df["Total_outlier_trial_conditions"] = 0
    result3_df = pd.concat([result_df, result2_df]).reset_index(drop = True)
    result3_df["Total_outlier_conditions"] = result3_df["Total_outlier_trial_conditions"] + result3_df["Total_outlier_subj_conditions"]
    result4_df = result3_df.groupby(["Experiment", "Subject", "Total_conditions"], as_index = False).agg(Total_outlier_conditions = ("Total_outlier_conditions", "sum"))

    # Total outlier conditions porcentual
    data_porcOutSubjCond_df = result4_df.reset_index(drop = True)
    data_porcOutSubjCond_df["Total_outlier_conditions_porc"] = data_porcOutSubjCond_df["Total_outlier_conditions"] * 100 / data_porcOutSubjCond_df["Total_conditions"]
    
    return general_cond_dict_df, general_proc_data3_df, general_proc_WithoutOutlierTrials_df, data_porcOutSubjCond_df


#%% Outliers_SubjCond_Cuantification
# Function to know outlier subject conditions cuantification.
# path --> string (ej: '../data_aux/'). data_OutSubjCond_df --> dataframe.
def Outliers_SubjCond_Cuantification(path, data_OutSubjCond_df):

    # Experiments dictionary and data
    general_proc_data_df = data_OutSubjCond_df[1]
    data_porcOutSubjCond_df = data_OutSubjCond_df[3] 

    # Total subjects per experiment
    n_subjects_df = general_proc_data_df.drop(columns = ['Exp_name', 'General_condition', "Condition", "Assigned_Stim", 
                                                         "Relative_beep", "Time", "Asyn_zeroed", "Outlier_trial_meanAsyn", 
                                                         "Outlier_trial_std", 'Outlier_trial_porcPrevCond', 'Outlier_subj_meanAsyn', 'Outlier_subj_std'])
    n_subjects_df["Total_subjects"] = 1
    n_subjects_df = n_subjects_df.groupby(["Experiment", "Subject"], as_index = False).agg(Total_subjects = ("Total_subjects", "max"))
    n_subjects_df = n_subjects_df.groupby(["Experiment"], as_index = False).agg(Total_subjects = ("Total_subjects", "sum"))

    # Total outlier conditions and total subject conditions per experiment. 
    n_subjCond_df = data_porcOutSubjCond_df.drop(columns = ['Subject', 'Total_outlier_conditions_porc'])
    n_subjCond_df = n_subjCond_df.groupby(["Experiment"], as_index = False).agg(Total_conditions = ("Total_conditions", "max"), Total_outlier_conditions = ("Total_outlier_conditions", "sum"))
    n_subjCond_df = pd.merge(n_subjCond_df, n_subjects_df, on=["Experiment"]).reset_index(drop = True)
    n_subjCond_df["Total_subjCond"] = n_subjCond_df["Total_conditions"] * n_subjCond_df["Total_subjects"] 
    n_subjCond_df.drop(columns = ['Total_conditions', 'Total_subjects'], inplace = True)
    
    # Porcentual total outlier conditions per total subject conditions per experiment.
    data_porcTotalOutCondPerTotalSubjCond_df = n_subjCond_df.reset_index(drop = True)
    data_porcTotalOutCondPerTotalSubjCond_df["Total_out_cond_perSubjCond_porc"] = data_porcTotalOutCondPerTotalSubjCond_df["Total_outlier_conditions"] * 100 / data_porcTotalOutCondPerTotalSubjCond_df["Total_subjCond"]

    # Save Files.
    data_porcOutSubjCond_df.to_csv(path + "porc_outlier_conditions_perExp_perSub.csv", na_rep = np.NaN)
    data_porcTotalOutCondPerTotalSubjCond_df.to_csv(path + "porc_outlier_conditions_perExp_perSubjCond.csv", na_rep = np.NaN)

    return


#%% Preprocessing_Data_AllExperiments_MarkingSubjOutliers
# Function to process data for all experiments and general conditions dictionary, marking outlier subjects. Return a tuple with four dataframes.
# path --> string (ej: '../data_aux/'). data_OutSubjCond_df --> dataframe. porcSubjCondPrevCond --> int (ej: 10).
def Preprocessing_Data_AllExperiments_MarkingSubjOutliers(path, data_OutSubjCond_df, porcSubjCondPrevCond):

    # Experiments dictionary and data
    general_cond_dict_df = data_OutSubjCond_df[0]
    general_proc_data_df = data_OutSubjCond_df[1]
    general_proc_WithoutOutlierTrials_df = data_OutSubjCond_df[2]
    data_porcOutSubjCond_df = data_OutSubjCond_df[3]

    # Applying porcentual previous outlier subject conditions criteria
    general_proc_data2_aux_df = data_porcOutSubjCond_df.reset_index(drop = True) 
    general_proc_data2_aux_df["Outlier_subj_porcPrevCond"] = 0
    general_proc_data2_aux_df.loc[general_proc_data2_aux_df.Total_outlier_conditions_porc > porcSubjCondPrevCond,'Outlier_subj_porcPrevCond'] = 1
    general_proc_data2_aux_df = general_proc_data2_aux_df.reset_index(drop = True).drop(columns = ['Total_outlier_conditions', 'Total_conditions', 'Total_outlier_conditions_porc'])

    # General processing data with meanAsyn, STD, procentual outlier trials, subj cond and subj marked
    general_proc_data2_aux2_df = general_proc_WithoutOutlierTrials_df.groupby(["Experiment", "Subject"], as_index=False).agg(Outlier_trial_porcPrevCond = ("Outlier_trial_porcPrevCond", "max"), 
                                                                                                                             Outlier_subj_meanAsyn = ("Outlier_subj_meanAsyn", "max"), Outlier_subj_std = ("Outlier_subj_std", "max"))                       
    general_proc_data2_aux2_df = general_proc_data2_aux2_df[(general_proc_data2_aux2_df['Outlier_trial_porcPrevCond'] == 0) & (general_proc_data2_aux2_df['Outlier_subj_meanAsyn'] == 0) & (general_proc_data2_aux2_df['Outlier_subj_std'] == 0)]
    general_proc_data2_aux2_df["Outlier_subj_porcPrevCond"] = 0
    general_proc_data2_aux2_df = general_proc_data2_aux2_df.reset_index(drop = True).drop(columns = ['Outlier_trial_porcPrevCond', 'Outlier_subj_meanAsyn', 'Outlier_subj_std'])
    general_proc_data2_aux3_df = pd.concat([general_proc_data2_aux_df, general_proc_data2_aux2_df]).reset_index(drop = True)
    general_proc_data2_df = pd.merge(general_proc_data_df, general_proc_data2_aux3_df, on=["Experiment", "Subject"])

    # General processing data without outlier trials and subj cond.  
    general_proc_WithoutOutlierTrialsAndSubjCond_df = general_proc_data2_df[(general_proc_data2_df['Outlier_trial_meanAsyn'] == 0) & (general_proc_data2_df['Outlier_trial_std'] == 0) 
                                                                            & (general_proc_data2_df['Outlier_trial_porcPrevCond'] == 0) & (general_proc_data2_df['Outlier_subj_meanAsyn'] == 0) 
                                                                            & (general_proc_data2_df['Outlier_subj_std'] == 0)].reset_index(drop = True)
    
    # General processing data without outlier trials and subj cond and subject.  
    general_proc_WithoutOutlierTrialsAndSubjCondAndSubj_df = general_proc_WithoutOutlierTrialsAndSubjCond_df[(general_proc_WithoutOutlierTrialsAndSubjCond_df['Outlier_subj_porcPrevCond'] == 0)].reset_index(drop = True)

    # Save files
    general_cond_dict_df.to_csv(path + "general_cond_dict.csv", na_rep = np.NaN)
    general_proc_data2_df.to_csv(path + "general_proc_data.csv", na_rep = np.NaN)

    return general_cond_dict_df, general_proc_data2_df, general_proc_WithoutOutlierTrialsAndSubjCond_df, general_proc_WithoutOutlierTrialsAndSubjCondAndSubj_df


#%% Outliers_Subj_Cuantification
# Function to know outlier subjects cuantification.
# path --> string (ej: '../data_aux/'). data_OutSubj_df --> dataframe.
def Outliers_Subj_Cuantification(path, data_OutSubj_df):

    # Experiments dictionary and data
    general_proc_data_df = data_OutSubj_df[1]
    
    # Preprocessing data
    data2_df = general_proc_data_df.drop(columns = ['Exp_name', 'Block', 'Trial', 'Assigned_Stim', 
                                                    'Relative_beep', 'Time', 'Asyn_zeroed', 'Outlier_trial_meanAsyn', 
                                                    'Outlier_trial_std'])

    # Total subjects per experiment
    n_subjects_df = data2_df.drop(columns = ['General_condition', "Condition", 'Outlier_trial_porcPrevCond', 'Outlier_subj_meanAsyn', 'Outlier_subj_std', 'Outlier_subj_porcPrevCond'])
    n_subjects_df["Total_subjects"] = 1
    n_subjects_df = n_subjects_df.groupby(["Experiment", "Subject"], as_index = False).agg(Total_subjects = ("Total_subjects", "max"))
    n_subjects_df = n_subjects_df.groupby(["Experiment"], as_index = False).agg(Total_subjects = ("Total_subjects", "sum"))

    # Per group condition, percentage of complete subjects discarded
    data3_df = data2_df[(data2_df['Outlier_subj_porcPrevCond'] == 1)]
    data3_df = data3_df.drop(columns = ['Outlier_trial_porcPrevCond', 'Outlier_subj_meanAsyn', 'Outlier_subj_std']).reset_index(drop = True)    
    result_df = data3_df.groupby(["Experiment", "Condition", "Subject"], as_index = False).agg(N_subjects = ("Outlier_subj_porcPrevCond", "max"))
    result_df = result_df.groupby(["Experiment", "Condition"], as_index = False).agg(Total_outlier_subjects = ("N_subjects", "sum"))
    result_df = pd.merge(n_subjects_df, result_df, on=["Experiment"]).reset_index(drop = True)
    result_df["Total_outlier_subjects_porc"] = result_df["Total_outlier_subjects"] * 100 / result_df["Total_subjects"]
    result_df = result_df.reindex(columns=['Experiment', 'Condition', 'Total_subjects', 'Total_outlier_subjects', 'Total_outlier_subjects_porc'])

    # Per group subject, conditions removed.
    data4_df = data2_df[(data2_df['Outlier_trial_porcPrevCond'] == 1) | (data2_df['Outlier_subj_meanAsyn'] == 1) | (data2_df['Outlier_subj_std'] == 1) | 
                        (data2_df['Outlier_subj_porcPrevCond'] == 1)].reset_index(drop = True)
    result2_df = data4_df.groupby(["Experiment", "Subject", "Condition"], as_index = False).agg(Outlier_trial_porcPrevCond = ("Outlier_trial_porcPrevCond", "max"),
                                                                                                Outlier_subj_meanAsyn = ("Outlier_subj_meanAsyn", "max"),
                                                                                                Outlier_subj_std = ("Outlier_subj_std", "max"),
                                                                                                Outlier_subj_porcPrevCond = ("Outlier_subj_porcPrevCond", "max"))

    # Save Files.
    result_df.to_csv(path + "porc_outlier_subjects_perExp_perCond.csv", na_rep = np.NaN)
    result2_df.to_csv(path + "perExp_perSubj_perCond_What_is_the_outlier_condition_criteria.csv", na_rep = np.NaN)


#%% Group_Subject_Condition_Outlier_SubjCond
# Function to obtain meanasyn and stdasyn for each group subject condition.
def Group_Subject_Condition_Outlier_SubjCond(data_OutSubjCond_df):

    # Experiments dictionary and data
    general_cond_dict_df = data_OutSubjCond_df[0]
    general_proc_WithoutOutlierTrials_df = data_OutSubjCond_df[2]

    # Searching data for experiment_type
    particular_exp_data2_df = general_proc_WithoutOutlierTrials_df[(general_proc_WithoutOutlierTrials_df['Outlier_subj_meanAsyn'] == 0) 
                                                                   & (general_proc_WithoutOutlierTrials_df['Outlier_subj_std'] == 0)].reset_index(drop = True)
    particular_exp_data3_df = general_proc_WithoutOutlierTrials_df[(general_proc_WithoutOutlierTrials_df['Outlier_subj_meanAsyn'] == 1) 
                                                                   | (general_proc_WithoutOutlierTrials_df['Outlier_subj_std'] == 1)].reset_index(drop = True)
    
    # Mean valid trials asyn all subjects per conditions and mean of the last ones
    perSubjAve2_df = (particular_exp_data2_df
                          # Average across trials without outlier trials and outlier subj cond.
                          .groupby(["Exp_name", "Experiment", "Subject", "General_condition", "Condition", "Relative_beep"], as_index=False)
                          .agg(mean_asyn=("Asyn_zeroed","mean"),sem_asyn=("Asyn_zeroed","sem")))
    
    perSubjAve3_df = (particular_exp_data3_df
                          # Average across trials, only outlier subj cond.
                          .groupby(["Exp_name", "Experiment", "Subject", "General_condition", "Condition", "Relative_beep"], as_index=False)
                          .agg(mean_asyn=("Asyn_zeroed","mean"),sem_asyn=("Asyn_zeroed","sem")))
    
    return general_cond_dict_df, perSubjAve2_df, perSubjAve3_df


#%% Group_Subject_Condition_Outlier_Subject
# Function to obtain meanasyn and stdasyn for each group subject condition.
def Group_Subject_Condition_Outlier_Subject(data_OutSubj_df):

    # Experiments dictionary and data
    general_cond_dict_df = data_OutSubj_df[0]
    general_proc_WithoutOutlierTrialsAndSubjCond_df = data_OutSubj_df[2]

    # Searching data for experiment_type
    particular_exp_data2_df = general_proc_WithoutOutlierTrialsAndSubjCond_df[(general_proc_WithoutOutlierTrialsAndSubjCond_df['Outlier_subj_porcPrevCond'] == 0)].reset_index(drop = True)
    particular_exp_data3_df = general_proc_WithoutOutlierTrialsAndSubjCond_df[(general_proc_WithoutOutlierTrialsAndSubjCond_df['Outlier_subj_porcPrevCond'] == 1)].reset_index(drop = True)     

    # Mean valid trials asyn all subjects per conditions and mean of the last ones
    perSubjAve2_df = (particular_exp_data2_df
                          # Average across trials without outlier trials and outlier subj cond.
                          .groupby(["Exp_name", "Experiment", "Subject", "General_condition", "Condition", "Relative_beep"], as_index=False)
                          .agg(mean_asyn=("Asyn_zeroed","mean"),sem_asyn=("Asyn_zeroed","sem")))
    
    perSubjAve3_df = (particular_exp_data3_df
                          # Average across trials, only outlier subj cond.
                          .groupby(["Exp_name", "Experiment", "Subject", "General_condition", "Condition", "Relative_beep"], as_index=False)
                          .agg(mean_asyn=("Asyn_zeroed","mean"),sem_asyn=("Asyn_zeroed","sem")))
    
    return general_cond_dict_df, perSubjAve2_df, perSubjAve3_df
    

#%%










#%% Plot_Valid_Trials_Asyn_PerSubject_PerCondition_And_Mean
# Function to plot trial asynchronies per valid trial, and trials mean without outlier trials.
# path --> string (ej: '../data_aux/'). data_OutTrials_df --> dataframe. experiment_name --> string (ej: 'Experiment_PS_SC'). 
# experiment_condition --> string (ej: 'SCneg'). perturb_size --> int (ej: 50). subject --> int (ej: 0). figure_number --> int (ej: 1).
def Plot_Valid_Trials_Asyn_PerSubject_PerCondition_And_Mean(path, data_OutTrials_df, experiment_name, experiment_condition, perturb_size, subject, figure_number):
    
    # Experiments dictionary and data
    general_cond_dict_df = data_OutTrials_df[0]
    general_proc_data_df = data_OutTrials_df[1]
    
    # Searching dictionay for experiment_type    
    particular_exp_dic_df = general_cond_dict_df[general_cond_dict_df['Exp_name'] == experiment_name]
    particular_exp_dic_df = particular_exp_dic_df[particular_exp_dic_df.Name.str.contains(experiment_condition)]
    particular_exp_dic_df = particular_exp_dic_df[(particular_exp_dic_df['Perturb_size'] == perturb_size) | 
                                                  (particular_exp_dic_df['Perturb_size'] == -perturb_size)]
    particular_exp_dic_df.reset_index(drop = True, inplace = True)
    
    # Subject Data Search
    gen_cond = particular_exp_dic_df['General_condition'].tolist()[0]
    particular_exp_data_df = general_proc_data_df[(general_proc_data_df['General_condition'] == gen_cond) & (general_proc_data_df['Subject'] == subject)].reset_index(drop = True)
    
    # Subject Data Search Filtered
    particular_exp_data2_df = particular_exp_data_df[(particular_exp_data_df['Outlier_trial_meanAsyn'] == 0) & (particular_exp_data_df['Outlier_trial_std'] == 0)].reset_index(drop = True)
    particular_exp_data3_df = particular_exp_data_df[(particular_exp_data_df['Outlier_trial_meanAsyn'] == 1) | (particular_exp_data_df['Outlier_trial_std'] == 1)].reset_index(drop = True)
    
    # Mean valid trials asyn per experiment, per subject and per condition
    TrialsAve_df = (particular_exp_data2_df
                       # First average across trials.
                       .groupby(["Exp_name", "Experiment", "Subject", "General_condition", "Condition", "Relative_beep"], as_index=False).agg(Asyn_zeroed=("Asyn_zeroed","mean"),sem_asyn=("Asyn_zeroed","sem")))

    # Plot Trials
    title = 'Asynchronies per experiment, per subject, per condition and per trial, and mean across trials.'
    n_blocks = (pd.unique(particular_exp_data2_df['Block'])).tolist()
    for block in n_blocks:
        asyn_aux_df = particular_exp_data2_df[particular_exp_data2_df['Block'] == block].reset_index(drop = True)
        n_trials = (pd.unique(asyn_aux_df['Trial'])).tolist()
        for trial in n_trials:
            asyn_df = asyn_aux_df[asyn_aux_df['Trial'] == trial].reset_index(drop = True)
            legend = ('Subject: ' + str(subject) + ', ' + str(particular_exp_dic_df['Exp_name'][0]) + ', ' 
                      + str(particular_exp_dic_df['Name'][0]) + ', ' + 'DeltaT: ' + str(particular_exp_dic_df['Perturb_size'][0]) + ', ' 
                      + 'Block: ' + str(block) + ', ' + 'Trial: ' + str(trial) + '.')
            Plot_Relative_Beep_Asynch(path, asyn_df, title, legend, '.-', 1, figure_number) 
    n_blocks = (pd.unique(particular_exp_data3_df['Block'])).tolist()
    for block in n_blocks:
        asyn_aux_df = particular_exp_data3_df[particular_exp_data3_df['Block'] == block].reset_index(drop = True)
        n_trials = (pd.unique(asyn_aux_df['Trial'])).tolist()
        for trial in n_trials:
            asyn_df = asyn_aux_df[asyn_aux_df['Trial'] == trial].reset_index(drop = True)
            legend = ('Subject: ' + str(subject) + ', ' + str(particular_exp_dic_df['Exp_name'][0]) + ', ' 
                      + str(particular_exp_dic_df['Name'][0]) + ', ' + 'DeltaT: ' + str(particular_exp_dic_df['Perturb_size'][0]) + ', ' 
                      + 'Block: ' + str(block) + ', ' + 'Trial: ' + str(trial) + '.')
            Plot_Relative_Beep_Asynch(path, asyn_df, title, legend, '.--', 1, figure_number)

    # Plot mean trials
    legend = ('Subject: ' + str(subject) + ', ' + str(particular_exp_dic_df['Exp_name'][0]) + ', ' 
              + str(particular_exp_dic_df['Name'][0]) + ', ' + 'DeltaT: ' + str(particular_exp_dic_df['Perturb_size'][0]) + ', Mean Trials without outliers.')
    Plot_Relative_Beep_Asynch_WithErrorbar(path, TrialsAve_df, title, legend, '.-', 3, figure_number, False)


#%% Plot_Relative_Beep_Asynch
# Function to plot relative beep asynch with standard deviation.
def Plot_Relative_Beep_Asynch(path, asyn_df, title, legend, fmt_type, line_with, figure_number):
    
    # Number of figure
    plt.figure(num = figure_number)
    
    # Plot with error bars
    plt.errorbar(asyn_df['Relative_beep'], asyn_df['Asyn_zeroed'], fmt = fmt_type, linewidth = line_with, label = legend)
    
    # x label and y label
    plt.xlabel('# beep',fontsize=12)
    plt.ylabel('Asynchrony[ms]',fontsize=12)
    
    # Set ticks
    minimum = asyn_df['Relative_beep'].min()
    maximum = asyn_df['Relative_beep'].max()
    plt.xticks(range(minimum, maximum + 1))
    
    # Grid
    plt.grid(True) 
    
    # Title
    plt.title(title)
    
    # legend location
    plt.legend(loc ='upper left')
        
    # Save Figure
    plt.savefig(path + str(figure_number) + '.pdf')


#%% Plot_Relative_Beep_Asynch_WithErrorbar
# Function to plot relative beep asynch with standard deviation.
def Plot_Relative_Beep_Asynch_WithErrorbar(path, asyn_df, title, legend, fmt_type, line_with, figure_number, significance):
    
    # Number of figure
    plt.figure(num = figure_number)
    
    # Standar error
    yerror = asyn_df['sem_asyn']
    
    # Plot with error bars
    plt.errorbar(asyn_df['Relative_beep'], asyn_df['Asyn_zeroed'], yerr = yerror, fmt = fmt_type, linewidth = line_with, label = legend)
    
    # x label and y label
    plt.xlabel('# beep',fontsize=12)
    plt.ylabel('Asynchrony[ms]',fontsize=12)
    
    # Set ticks
    minimum = asyn_df['Relative_beep'].min()
    maximum = asyn_df['Relative_beep'].max()
    plt.xticks(range(minimum, maximum + 1))
    
    # Grid
    plt.grid(True) 
    
    # Title
    plt.title(title)
    
    # legend location
    plt.legend(loc ='upper left')
    
    if significance:
        for relative_beep in range(minimum, maximum + 1):
            rejected_df = asyn_df[asyn_df['Relative_beep'] == relative_beep] 
            rejected = rejected_df['rejected'].tolist()[0]
            if rejected:
                b = rejected_df['Asyn_zeroed'].tolist()[0]
                if (b < 0):
                    b = b - 10
                else:
                    b = b +10
                plt.text(relative_beep, b, "*")
        
    # Save Figure
    plt.savefig(path + str(figure_number) + '.pdf')


#%% Plot_Mean_Valid_Trials_Asyn_AllSubjectcs_PerCondition_And_MeanOfTheLastOnes_WithoutOutliers_perTrialAndSubjCondAnalysis
# Function to plot mean trials asynchronies across all subjects, per condition and mean of the last ones. Without oulier per Trial and Subj Cond Analysis.
# Outlier subjects in dotted line. Mean only of the non outliers subjects. 
# path --> string (ej: '../data_aux/'). data_GroupSubjCond_df --> dataframe tuple. experiment_name --> string (ej: 'Experiment_SC'). experiment_condition --> string (ej: 'SCneg'). perturb_size --> int (ej: 50). figure_number --> int (ej: 1). 
def Plot_Mean_Valid_Trials_Asyn_AllSubjectcs_PerCondition_And_MeanOfTheLastOnes_WithoutOutliers_perTrialAndSubjCondAnalysis(path, data_GroupSubjCond_df, experiment_name, experiment_condition, perturb_size, figure_number):

    # Experiments dictionary and data
    experiment_dictionary_df = data_GroupSubjCond_df[0]
    exp_data_without_out_trial_SubjCond_df = data_GroupSubjCond_df[1]
    exp_data_only_out_SubjCond_df = data_GroupSubjCond_df[2]

    # Searching dictionay for experiment_type    
    particular_exp_dic_df = experiment_dictionary_df[experiment_dictionary_df['Exp_name'] == experiment_name]
    particular_exp_dic_df = particular_exp_dic_df[particular_exp_dic_df.Name.str.contains(experiment_condition)]
    particular_exp_dic_df = particular_exp_dic_df[(particular_exp_dic_df['Perturb_size'] == perturb_size) | 
                                                  (particular_exp_dic_df['Perturb_size'] == -perturb_size)]
    particular_exp_dic_df.reset_index(drop = True, inplace = True)

    # Searching data for experiment_type
    gen_cond = particular_exp_dic_df['General_condition'].tolist()[0]
    perSubjAve2_df = exp_data_without_out_trial_SubjCond_df[exp_data_without_out_trial_SubjCond_df['General_condition'] == gen_cond].reset_index(drop = True)
    perSubjAve3_df = exp_data_only_out_SubjCond_df[exp_data_only_out_SubjCond_df['General_condition'] == gen_cond].reset_index(drop = True)
    
    # Then average across subjects
    subjAve_df = (perSubjAve2_df.groupby(["General_condition", "Condition","Relative_beep"], as_index=False)
                          .agg(mean_asyn=("mean_asyn","mean"),sem_asyn=("mean_asyn","sem")))
    
    # Plot
    title = 'Mean asyn per valid trial, across all subj and per cond, and mean of the last ones. Without outliers per mean asyn, per SEM asyn and porc previous cond'
    subjects = (pd.unique(perSubjAve2_df['Subject'])).tolist()
    for n_subject in subjects:
        asyn_df = perSubjAve2_df[perSubjAve2_df['Subject'] == n_subject]
        asyn_df = asyn_df.drop(columns = ['Subject', 'General_condition', 'Condition'])
        asyn_df.rename(columns={'mean_asyn':'Asyn_zeroed'}, inplace = True)
        legend = ('Subject: ' + str(n_subject) + ', ' + str(particular_exp_dic_df['Exp_name'][0]) + ', ' 
                  + str(particular_exp_dic_df['Name'][0]) + ', ' + str(particular_exp_dic_df['Perturb_size'][0]) + '.')
        Plot_Relative_Beep_Asynch_WithErrorbar(path, asyn_df, title, legend, '.-', 1, figure_number, False)
    subjects = (pd.unique(perSubjAve3_df['Subject'])).tolist()
    for n_subject in subjects:
        asyn_df = perSubjAve3_df[perSubjAve3_df['Subject'] == n_subject]
        asyn_df = asyn_df.drop(columns = ['Subject', 'General_condition', 'Condition'])
        asyn_df.rename(columns={'mean_asyn':'Asyn_zeroed'}, inplace = True)
        legend = ('Subject: ' + str(n_subject) + ', ' + str(particular_exp_dic_df['Exp_name'][0]) + ', ' 
                  + str(particular_exp_dic_df['Name'][0]) + ', ' + str(particular_exp_dic_df['Perturb_size'][0]) + '.')
        Plot_Relative_Beep_Asynch_WithErrorbar(path, asyn_df, title, legend, '.--', 1, figure_number, False)  
    asyn_df = subjAve_df.drop(columns = ['General_condition', 'Condition'])
    asyn_df.rename(columns={'mean_asyn':'Asyn_zeroed'}, inplace = True)
    legend = ('Mean all subjects, ' + str(particular_exp_dic_df['Exp_name'][0]) + ', ' 
              + str(particular_exp_dic_df['Name'][0]) + ', ' + str(particular_exp_dic_df['Perturb_size'][0]) + '.')
    Plot_Relative_Beep_Asynch_WithErrorbar(path, asyn_df, title, legend, '.-', 3, figure_number, False)
    
    
#%% Boxplot_And_Dots
# Function to plot boxplot and stripplot to see quantile criteria.
# path --> string (ej: '../data_aux/'). data_OutSubjCond_df --> dataframe. experiment_name --> string (ej: 'Experiment_SC'). experiment_condition --> string (ej: 'SCneg'). perturb_size --> int (ej: 50). postPerturb_bip --> int (ej: 5). figure_number_1 --> int (ej: 1). figure_number_2 --> int (ej: 2). 
def Boxplot_And_Dots(path, data_GroupSubjCond_df, experiment_name, experiment_condition, perturb_size, postPerturb_bip, figure_number_1, figure_number_2):

    # Experiments dictionary and data
    experiment_dictionary_df = data_GroupSubjCond_df[0]
    exp_data_without_out_trial_SubjCond_df = data_GroupSubjCond_df[1]
    exp_data_only_out_SubjCond_df = data_GroupSubjCond_df[2]

    # Searching dictionay for experiment_type    
    particular_exp_dic_df = experiment_dictionary_df[experiment_dictionary_df['Exp_name'] == experiment_name]
    particular_exp_dic_df = particular_exp_dic_df[particular_exp_dic_df.Name.str.contains(experiment_condition)]
    particular_exp_dic_df = particular_exp_dic_df[(particular_exp_dic_df['Perturb_size'] == perturb_size) | 
                                                  (particular_exp_dic_df['Perturb_size'] == -perturb_size)]
    particular_exp_dic_df.reset_index(drop = True, inplace = True)

    # Searching data for experiment_type
    gen_cond = particular_exp_dic_df['General_condition'].tolist()[0]
    particular_exp_data_df = pd.concat([exp_data_without_out_trial_SubjCond_df, exp_data_only_out_SubjCond_df])
    particular_exp_data_df = particular_exp_data_df[particular_exp_data_df['General_condition'] == gen_cond].reset_index(drop = True)
 
    # Keep beeps after postPerturb_bip only (twice)
    postPerturb_bip_df = particular_exp_data_df.query("Relative_beep >= @postPerturb_bip")
    
    # Mean valid trials asyn all subjects per conditions and mean of the last ones
    data_mean_df = (postPerturb_bip_df
                          # First average across trials.
                          .groupby(["Experiment", "Subject", "General_condition", "Condition"], as_index=False)
                          .agg(mean_asyn=("mean_asyn","mean"),std_asyn=("mean_asyn","std")))
    
    # Plot
    f1 = plt.figure(num = figure_number_1, figsize=[18,12])
    ax1 = f1.add_subplot(111)
    sns.boxplot(y = "mean_asyn", data = data_mean_df, ax = ax1)
    sns.stripplot(y = "mean_asyn", color = 'black', data = data_mean_df, ax = ax1)
    
    f2 = plt.figure(num = figure_number_2, figsize=[18,12])
    ax2 = f2.add_subplot(111)
    sns.boxplot(y = "std_asyn", data = data_mean_df, ax = ax2)
    sns.stripplot(y = "std_asyn", color = 'black', data = data_mean_df, ax = ax2)


#%% Plot_Difference_Between_Same_Condition_Different_Experiments
# Function to plot difference between same condition (condition per experiment, across all subjects) different experiments.
# path --> string (ej: '../data_aux/'). data_GroupSubjCond_OS_df --> dataframe. experiment_name_1 --> string (ej: 'Experiment_SC'). 
# experiment_name_2 --> string (ej: 'Experiment_PS_SC'). experiment_condition --> string (ej: 'SCneg'). perturb_size --> int (ej: 50). 
# relative_beep_ini --> int (ej: 1). relative_beep_final --> int (ej: 6). figure_number --> int (ej: 1).
def Plot_Difference_Between_Same_Condition_Different_Experiments(path, data_GroupSubjCond_OS_df, experiment_name_1, experiment_name_2, experiment_condition, perturb_size, relative_beep_ini, relative_beep_final, figure_number):

    # Experiments dictionary and data
    experiment_dictionary_df = data_GroupSubjCond_OS_df[0]
    experiment_data_df = data_GroupSubjCond_OS_df[1]

    # Search dictionay for experiment_type    
    particular_exp_dic_df = experiment_dictionary_df[(experiment_dictionary_df['Exp_name'] == experiment_name_1) | 
                                                     (experiment_dictionary_df['Exp_name'] == experiment_name_2)]
    particular_exp_dic_df = particular_exp_dic_df[particular_exp_dic_df.Name.str.contains(experiment_condition)]
    particular_exp_dic_df = particular_exp_dic_df[(particular_exp_dic_df['Perturb_size'] == perturb_size) | 
                                                  (particular_exp_dic_df['Perturb_size'] == -perturb_size)]
    particular_exp_dic_df.reset_index(drop = True, inplace = True)

    # Searching data for experiment_type
    n_gen_cond = particular_exp_dic_df['General_condition'].tolist()
    particular_exp_data_df = pd.DataFrame()
    for gen_cond in n_gen_cond:
        particular_exp_data_aux_df = (experiment_data_df[experiment_data_df['General_condition'] == gen_cond]).reset_index(drop = True)
        particular_exp_data_df = pd.concat([particular_exp_data_df, particular_exp_data_aux_df])
    particular_exp_data_df.reset_index(drop = True, inplace = True)

    # Searching data to calculate p-values
    particular_exp_data2_df = particular_exp_data_df[(particular_exp_data_df['Relative_beep'] >= relative_beep_ini) & 
                                                     (particular_exp_data_df['Relative_beep'] <= relative_beep_final)]
    
    # Calculating the p-value
    pvalue_df = pd.DataFrame()
    n_relativeBeep = sorted((pd.unique(particular_exp_data2_df['Relative_beep'])).tolist())
    for relativeBeep in n_relativeBeep:
        pvalue_aux_df = pd.DataFrame()
        data_pvalue_df = particular_exp_data2_df[(particular_exp_data2_df['Relative_beep'] == relativeBeep)]
        n_experiment = sorted((pd.unique(data_pvalue_df['Experiment'])).tolist())
        data_pvalue_G1_df = data_pvalue_df[(data_pvalue_df['Experiment'] == n_experiment[0])]
        data_pvalue_G1_list = data_pvalue_G1_df['mean_asyn'].tolist()
        data_pvalue_G2_df = data_pvalue_df[(data_pvalue_df['Experiment'] == n_experiment[1])]
        data_pvalue_G2_list = data_pvalue_G2_df['mean_asyn'].tolist()
        s, p = stats.ttest_ind(a = data_pvalue_G1_list, b = data_pvalue_G2_list, equal_var = False)
        pvalue_aux_df['Relative_beep'] = [relativeBeep]
        pvalue_aux_df['pvalue'] = [p]
        pvalue_df = pd.concat([pvalue_df, pvalue_aux_df]).reset_index(drop = True)   

    # Applying FDR correction
    pvalues_list = pvalue_df['pvalue'].tolist()
    rejected_array, pvalue_corrected_array = sm.fdrcorrection(pvalues_list, alpha = 0.05, method = 'indep', is_sorted = False)
    pvalue_df['pvalue_corrected'] = pvalue_corrected_array
    pvalue_df['rejected'] = rejected_array
    pvalue_df.loc[pvalue_df.rejected == False,'rejected'] = 0
    pvalue_df.loc[pvalue_df.rejected == True,'rejected'] = 1
    pvalue_df.to_csv(path + "pvalue.csv", na_rep = np.NaN)

    # Experiments data after FDR correction
    pvalue2_df = pvalue_df.drop(columns = ['pvalue', 'pvalue_corrected'])
    n_relativeBeep2 = sorted((pd.unique(particular_exp_data_df['Relative_beep'])).tolist())
    pvalue3_df = pd.DataFrame({"Relative_beep" : n_relativeBeep2})
    pvalue3_df = pvalue3_df[(pvalue3_df['Relative_beep'] < relative_beep_ini) | (pvalue3_df['Relative_beep'] > relative_beep_final)]
    pvalue3_df['rejected'] = 0
    pvalue4_df = pd.concat([pvalue2_df, pvalue3_df]).reset_index(drop = True)  

    # Experiments data with pvalues and FDR correction
    particular_exp_data3_df = pd.merge(particular_exp_data_df, pvalue4_df, on=["Relative_beep"]).reset_index(drop = True)

    # Mean data across subjects
    groupCond_data_df = (particular_exp_data3_df 
                              # then average across subjects
                              .groupby(["Exp_name", "Experiment", "General_condition", "Condition", "Relative_beep"], as_index=False)
                              .agg(Asyn_zeroed = ("mean_asyn", "mean"), sem_asyn = ("mean_asyn", "sem"), rejected = ("rejected", "max")))

    # Difference
    condition_min_df = particular_exp_dic_df[particular_exp_dic_df['Exp_name'] == experiment_name_1].reset_index(drop = True)
    condition_min = condition_min_df['General_condition'][0]
    minuendo_df = groupCond_data_df[groupCond_data_df['General_condition'] == condition_min].reset_index(drop = True)
    condition_sub_df = particular_exp_dic_df[particular_exp_dic_df['Exp_name'] == experiment_name_2].reset_index(drop = True)
    condition_sub = condition_sub_df['General_condition'][0]
    subtrahend_df = groupCond_data_df[groupCond_data_df['General_condition'] == condition_sub].reset_index(drop = True)
    difference_df = pd.DataFrame()
    difference_df['Relative_beep'] = minuendo_df['Relative_beep']
    difference_df['Asyn_zeroed'] = minuendo_df['Asyn_zeroed'] - subtrahend_df['Asyn_zeroed']
    difference_df['sem_asyn'] = minuendo_df['sem_asyn'] + subtrahend_df['sem_asyn']
    difference_df['rejected'] = minuendo_df['rejected']

    # Plot
    title = 'Difference between same condition from different experiments, without all outliers.'
    legend = str(condition_min_df['Exp_name'][0]) + ', ' + str(condition_min_df['Name'][0]) + ', ' + str(condition_min_df['Perturb_size'][0]) + '.' 
    Plot_Relative_Beep_Asynch_WithErrorbar(path, minuendo_df, title, legend, '.-', 1, figure_number, False)
    legend = str(condition_sub_df['Exp_name'][0]) + ', ' + str(condition_sub_df['Name'][0]) + ', ' + str(condition_sub_df['Perturb_size'][0]) + '.' 
    Plot_Relative_Beep_Asynch_WithErrorbar(path, subtrahend_df, title, legend, '.-', 1, figure_number, False)
    legend = 'Difference.' 
    Plot_Relative_Beep_Asynch_WithErrorbar(path, difference_df, title, legend, '.--', 1, figure_number, True)


#%% Plot_Asymmetry_Between_Opposite_Conditions_Same_Experiments
# Function to plot asymmetry between opposite conditions (condition per experiment, across all subjects) from same experiment.
# path --> string (ej: '../data_aux/'). data_GroupSubjCond_OS_df --> dataframe. experiment_name --> string (ej: 'Experiment_SC'). 
# experiment_type --> string (ej: 'SC'). perturb_size --> int (ej: 50). relative_beep_ini --> int (ej: 1). relative_beep_final --> int (ej: 6). figure_number --> int (ej: 1).
def Plot_Asymmetry_Between_Opposite_Conditions_Same_Experiments(path, data_GroupSubjCond_OS_df, experiment_name, experiment_type, perturb_size, relative_beep_ini, relative_beep_final, figure_number):

    # Experiments dictionary and data
    experiment_dictionary_df = data_GroupSubjCond_OS_df[0]
    experiment_data_df = data_GroupSubjCond_OS_df[1]
    
    # Search dictionay for experiment_type    
    particular_exp_dic_df = experiment_dictionary_df[experiment_dictionary_df['Exp_name'] == experiment_name]
    particular_exp_dic_df = particular_exp_dic_df[particular_exp_dic_df.Name.str.contains(experiment_type)]
    particular_exp_dic_df = particular_exp_dic_df[(particular_exp_dic_df['Perturb_size'] == perturb_size) | 
                                                  (particular_exp_dic_df['Perturb_size'] == -perturb_size)]
    particular_exp_dic_df.reset_index(drop = True, inplace = True)
    
    # Searching data for experiment_type
    n_gen_cond = particular_exp_dic_df['General_condition'].tolist()
    particular_exp_data_df = pd.DataFrame()
    for gen_cond in n_gen_cond:
        particular_exp_data_aux_df = (experiment_data_df[experiment_data_df['General_condition'] == gen_cond]).reset_index(drop = True)
        particular_exp_data_df = pd.concat([particular_exp_data_df, particular_exp_data_aux_df])
    particular_exp_data_df.reset_index(drop = True, inplace = True) 

    # Searching data to calculate p-values
    particular_exp_data2_df = particular_exp_data_df[(particular_exp_data_df['Relative_beep'] >= relative_beep_ini) & 
                                                     (particular_exp_data_df['Relative_beep'] <= relative_beep_final)]

    # Calculating the p-value
    pvalue_df = pd.DataFrame()
    condition_addUp1_df = particular_exp_dic_df[particular_exp_dic_df.Name.str.contains("neg")].reset_index(drop = True)
    condition_addUp1 = condition_addUp1_df['General_condition'][0]
    condition_addUp2_df = particular_exp_dic_df[particular_exp_dic_df.Name.str.contains("pos")].reset_index(drop = True)
    condition_addUp2 = condition_addUp2_df['General_condition'][0]  
    n_relativeBeep = sorted((pd.unique(particular_exp_data2_df['Relative_beep'])).tolist())
    for relativeBeep in n_relativeBeep:
        pvalue_aux_df = pd.DataFrame()
        data_pvalue_df = particular_exp_data2_df[(particular_exp_data2_df['Relative_beep'] == relativeBeep)]
        data_pvalue_G1_df = data_pvalue_df[(data_pvalue_df['General_condition'] == condition_addUp1)]
        data_pvalue_G1_list = data_pvalue_G1_df['mean_asyn'].tolist()
        data_pvalue_G2_df = data_pvalue_df[(data_pvalue_df['General_condition'] == condition_addUp2)]
        data_pvalue_G2_list = data_pvalue_G2_df['mean_asyn'].tolist()
        data_pvalue_G2_list = [numero * -1 for numero in data_pvalue_G2_list] 
        s, p = stats.ttest_ind(a = data_pvalue_G1_list, b = data_pvalue_G2_list, equal_var = True)
        pvalue_aux_df['Relative_beep'] = [relativeBeep]
        pvalue_aux_df['pvalue'] = [p]
        pvalue_df = pd.concat([pvalue_df, pvalue_aux_df]).reset_index(drop = True)   

    # Applying FDR correction
    pvalues_list = pvalue_df['pvalue'].tolist()
    rejected_array, pvalue_corrected_array = sm.fdrcorrection(pvalues_list, alpha = 0.05, method = 'indep', is_sorted = False)
    pvalue_df['pvalue_corrected'] = pvalue_corrected_array
    pvalue_df['rejected'] = rejected_array
    pvalue_df.loc[pvalue_df.rejected == False,'rejected'] = 0
    pvalue_df.loc[pvalue_df.rejected == True,'rejected'] = 1
    pvalue_df.to_csv(path + "pvalue.csv", na_rep = np.NaN)

    # Experiments data after FDR correction
    pvalue2_df = pvalue_df.drop(columns = ['pvalue', 'pvalue_corrected'])
    n_relativeBeep2 = sorted((pd.unique(particular_exp_data_df['Relative_beep'])).tolist())
    pvalue3_df = pd.DataFrame({"Relative_beep" : n_relativeBeep2})
    pvalue3_df = pvalue3_df[(pvalue3_df['Relative_beep'] < relative_beep_ini) | (pvalue3_df['Relative_beep'] > relative_beep_final)]
    pvalue3_df['rejected'] = 0
    pvalue4_df = pd.concat([pvalue2_df, pvalue3_df]).reset_index(drop = True)  

    # Experiments data with pvalues and FDR correction
    particular_exp_data3_df = pd.merge(particular_exp_data_df, pvalue4_df, on=["Relative_beep"]).reset_index(drop = True)

    # Mean data across subjects
    groupCond_data_df = (particular_exp_data3_df 
                              # then average across subjects
                              .groupby(["Exp_name", "Experiment", "General_condition", "Condition", "Relative_beep"], as_index=False)
                              .agg(Asyn_zeroed = ("mean_asyn", "mean"), sem_asyn = ("mean_asyn", "sem"), rejected = ("rejected", "max")))

    # Asymmetry
    addingUp1_df = groupCond_data_df[groupCond_data_df['General_condition'] == condition_addUp1].reset_index(drop = True)
    addingUp2_df = groupCond_data_df[groupCond_data_df['General_condition'] == condition_addUp2].reset_index(drop = True)
    asymmetry_df = pd.DataFrame()
    asymmetry_df['Relative_beep'] = addingUp1_df['Relative_beep'] 
    asymmetry_df['Asyn_zeroed'] = addingUp1_df['Asyn_zeroed'] + addingUp2_df['Asyn_zeroed']
    asymmetry_df['sem_asyn'] = addingUp1_df['sem_asyn'] + addingUp2_df['sem_asyn']
    asymmetry_df['rejected'] = addingUp1_df['rejected']

    # Plot
    title = 'Asymmetry between opposite conditions from same experiments, without all outliers.'
    legend = str(condition_addUp1_df['Exp_name'][0]) + ', ' + str(condition_addUp1_df['Name'][0]) + ', ' + str(condition_addUp1_df['Perturb_size'][0]) + '.' 
    Plot_Relative_Beep_Asynch_WithErrorbar(path, addingUp1_df, title, legend, '.-', 1, figure_number, False)
    legend = str(condition_addUp2_df['Exp_name'][0]) + ', ' + str(condition_addUp2_df['Name'][0]) + ', ' + str(condition_addUp2_df['Perturb_size'][0]) + '.' 
    Plot_Relative_Beep_Asynch_WithErrorbar(path, addingUp2_df, title, legend, '.-', 1, figure_number, False)
    legend = 'Asymmetry .' 
    Plot_Relative_Beep_Asynch_WithErrorbar(path, asymmetry_df, title, legend, '.--', 1, figure_number, True)


#%% Plot_Difference_Between_Same_Condition_Different_Experiments_BootstrappingPerBeep
# Function to plot difference between same condition (condition per experiment, across all subjects) different experiments.
# path --> string (ej: '../data_aux/'). data_GroupSubjCond_OS_df --> dataframe. experiment_name_1 --> string (ej: 'Experiment_SC'). 
# experiment_name_2 --> string (ej: 'Experiment_PS_SC'). experiment_condition --> string (ej: 'SCneg'). perturb_size --> int (ej: 50). 
# relative_beep_ini --> int (ej: 1). relative_beep_final --> int (ej: 6). figure_number --> int (ej: 1). histogram --> boolean (ej: True).
def Plot_Difference_Between_Same_Condition_Different_Experiments_BootstrappingPerBeep(path, data_GroupSubjCond_OS_df, experiment_name_1, experiment_name_2, experiment_condition, perturb_size, relative_beep_ini, relative_beep_final, figure_number, histogram):
    
    # Experiments dictionary and data
    experiment_dictionary_df = data_GroupSubjCond_OS_df[0]
    experiment_data_df = data_GroupSubjCond_OS_df[1]
    
    # Search dictionay for experiment_type    
    particular_exp_dic_df = experiment_dictionary_df[(experiment_dictionary_df['Exp_name'] == experiment_name_1) | 
                                                     (experiment_dictionary_df['Exp_name'] == experiment_name_2)]
    particular_exp_dic_df = particular_exp_dic_df[particular_exp_dic_df.Name.str.contains(experiment_condition)]
    particular_exp_dic_df = particular_exp_dic_df[(particular_exp_dic_df['Perturb_size'] == perturb_size) | 
                                                  (particular_exp_dic_df['Perturb_size'] == -perturb_size)]
    particular_exp_dic_df.reset_index(drop = True, inplace = True)
     
    # Searching data for experiment_type
    n_gen_cond = particular_exp_dic_df['General_condition'].tolist()
    particular_exp_data_df = pd.DataFrame()
    for gen_cond in n_gen_cond:
        particular_exp_data_aux_df = (experiment_data_df[experiment_data_df['General_condition'] == gen_cond]).reset_index(drop = True)
        particular_exp_data_df = pd.concat([particular_exp_data_df, particular_exp_data_aux_df])
    particular_exp_data_df.reset_index(drop = True, inplace = True)

    # Mean data across subjects
    groupCond_data_df = (particular_exp_data_df 
                              # then average across subjects
                              .groupby(["Exp_name", "Experiment", "General_condition", "Condition", "Relative_beep"], as_index=False)
                              .agg(Asyn_zeroed = ("mean_asyn", "mean"), sem_asyn = ("mean_asyn", "sem")))
    
    # Difference real value
    condition_min_df = particular_exp_dic_df[particular_exp_dic_df['Exp_name'] == experiment_name_1].reset_index(drop = True)
    condition_min = condition_min_df['General_condition'][0]
    minuendo_df = groupCond_data_df[groupCond_data_df['General_condition'] == condition_min].reset_index(drop = True)
    condition_sub_df = particular_exp_dic_df[particular_exp_dic_df['Exp_name'] == experiment_name_2].reset_index(drop = True)
    condition_sub = condition_sub_df['General_condition'][0]
    subtrahend_df = groupCond_data_df[groupCond_data_df['General_condition'] == condition_sub].reset_index(drop = True)
    difference_df = pd.DataFrame()
    difference_df['Relative_beep'] = minuendo_df['Relative_beep']
    difference_df['Asyn_zeroed'] = minuendo_df['Asyn_zeroed'] - subtrahend_df['Asyn_zeroed']
    difference_df['sem_asyn'] = minuendo_df['sem_asyn'] + subtrahend_df['sem_asyn']
    
    # Particular data per experiment
    particular_exp1_data_df = particular_exp_data_df[particular_exp_data_df['General_condition'] == condition_min]
    #particular_exp2_data_df = particular_exp_data_df[particular_exp_data_df['General_condition'] == condition_sub]

    # Number of subjects per experiment
    n_subjects_exp1 = len((pd.unique(particular_exp1_data_df['Subject'])).tolist())
    #n_subjects_exp2 = len((pd.unique(particular_exp2_data_df['Subject'])).tolist())
    
    # Bootstrapping
    n_iterations = 10000
    difference_totalFake_df = pd.DataFrame()
    for i in range(n_iterations):
        # Random data
        data_df = particular_exp_data_df.reset_index(drop = True)
        data_df["Fake_condition"] = 0
        data_df = data_df.groupby(["Experiment", "General_condition", "Subject"], as_index=False).agg(Fake_condition = ("Fake_condition", "min"))
        data2_df = data_df.sample(frac = 1).reset_index(drop = True)
        data2_df.loc[data2_df.index > (n_subjects_exp1 - 1), "Fake_condition"] = 1
        data3_df = pd.merge(particular_exp_data_df, data2_df, on=["Experiment", "General_condition", "Subject"]).reset_index(drop = True)
    
        # Mean fake data across subjects
        groupCond_fake_data_df = (data3_df 
                                  # then average across subjects
                                  .groupby(["Fake_condition", "Relative_beep"], as_index=False)
                                  .agg(Asyn_zeroed = ("mean_asyn", "mean"), sem_asyn = ("mean_asyn", "sem")))
       
        # Difference fake value
        minuendo_fake_df = groupCond_fake_data_df[groupCond_fake_data_df['Fake_condition'] == 0].reset_index(drop = True)
        subtrahend_fake_df = groupCond_fake_data_df[groupCond_fake_data_df['Fake_condition'] == 1].reset_index(drop = True)
        difference_fake_df = pd.DataFrame()
        difference_fake_df['Relative_beep'] = minuendo_fake_df['Relative_beep']
        difference_fake_df['Asyn_zeroed'] = minuendo_fake_df['Asyn_zeroed'] - subtrahend_fake_df['Asyn_zeroed']
        difference_fake_df['sem_asyn'] = minuendo_fake_df['sem_asyn'] + subtrahend_fake_df['sem_asyn']
        difference_fake_df['Number'] = i 
        difference_totalFake_df = pd.concat([difference_totalFake_df, difference_fake_df]).reset_index(drop = True)  

    # Merge real values and fake values
    data4_df = difference_df.reset_index(drop = True)
    data4_df.drop(columns = ['sem_asyn'], inplace = True)
    data4_df.rename(columns={"Asyn_zeroed": "Real_asyn_zeroed"}, inplace = True)
    data5_df = pd.merge(data4_df, difference_totalFake_df, on=["Relative_beep"]).reset_index(drop = True)

    # P-value
    data6_df = data5_df.reset_index(drop = True)
    data6_df["False_pos_diff"] = 0
    data6_df.loc[(data6_df.Real_asyn_zeroed > 0) & (data6_df.Asyn_zeroed > data6_df.Real_asyn_zeroed),'False_pos_diff'] = 1 
    data6_df.loc[(data6_df.Real_asyn_zeroed < 0) & (data6_df.Asyn_zeroed < data6_df.Real_asyn_zeroed),'False_pos_diff'] = 1 
    #data6_df.loc[data6_df.Asyn_zeroed > data6_df.Real_asyn_zeroed,'False_pos_diff'] = 1    
    data7_df = data6_df.groupby(["Relative_beep"], as_index=False).agg(False_pos_diff = ("False_pos_diff", "sum"))
    data7_df["n_iterations"] = n_iterations
    data7_df["p_value"] = data7_df["False_pos_diff"] / data7_df["n_iterations"]
    
    # Merge p_values
    data8_df = data7_df.reset_index(drop = True)
    data8_df.drop(columns = ['False_pos_diff', 'n_iterations'], inplace = True)
    data9_df = pd.merge(data8_df, data5_df, on=["Relative_beep"]).reset_index(drop = True) # Data for histograms

    # Applying FDR correction ((Benjamini/Hochberg (non-negative))
    data10_df = data7_df[(data7_df['Relative_beep'] >= relative_beep_ini) & (data7_df['Relative_beep'] <= relative_beep_final)].reset_index(drop = True)
    pvalues_list = data10_df['p_value'].tolist()
    rejected_array, pvalue_corrected_array = sm.fdrcorrection(pvalues_list, alpha = 0.05, method = 'indep', is_sorted = False)
    data10_df['pvalue_corrected'] = pvalue_corrected_array
    data10_df['rejected'] = rejected_array
    data10_df.loc[data10_df.rejected == False, 'rejected'] = 0
    data10_df.loc[data10_df.rejected == True, 'rejected'] = 1
    data10_df.to_csv(path + "pvalue.csv", na_rep = np.NaN)

    # Applying alternative FDR corrections (Benjamini/Hochberg (non-negative))
    data10B_df = data7_df[(data7_df['Relative_beep'] >= relative_beep_ini) & (data7_df['Relative_beep'] <= relative_beep_final)].reset_index(drop = True)
    pvalues_list = data10B_df['p_value'].tolist()
    rejected_arrayB, pvalue_corrected_arrayB, alphacSidakB, alphacBonfB = multipletests(pvalues_list, alpha = 0.05, method = 'fdr_bh')
    data10B_df['pvalue_corrected'] = pvalue_corrected_arrayB
    data10B_df['rejected'] = rejected_arrayB
    data10B_df.loc[data10B_df.rejected == False, 'rejected'] = 0
    data10B_df.loc[data10B_df.rejected == True, 'rejected'] = 1
    data10B_df.to_csv(path + "pvalue_FDR_Benjamini_Hochberg_nonNegative.csv", na_rep = np.NaN)
    
    # Applying alternative FDR corrections (two stage fdr correction (non-negative))
    data10C_df = data7_df[(data7_df['Relative_beep'] >= relative_beep_ini) & (data7_df['Relative_beep'] <= relative_beep_final)].reset_index(drop = True)
    pvalues_list = data10C_df['p_value'].tolist()
    rejected_arrayC, pvalue_corrected_arrayC, alphacSidakC, alphacBonfC = multipletests(pvalues_list, alpha = 0.05, method = 'fdr_tsbky')
    data10C_df['pvalue_corrected'] = pvalue_corrected_arrayC
    data10C_df['rejected'] = rejected_arrayC
    data10C_df.loc[data10C_df.rejected == False, 'rejected'] = 0
    data10C_df.loc[data10C_df.rejected == True, 'rejected'] = 1
    data10C_df.to_csv(path + "pvalue_FDR_two_stage_nonNegative.csv", na_rep = np.NaN) 

    # P_values state
    data11_df = data10_df.drop(columns = ['False_pos_diff', 'n_iterations', 'p_value', 'pvalue_corrected'])
    n_relativeBeep = sorted((pd.unique(data7_df['Relative_beep'])).tolist())
    data12_df = pd.DataFrame({"Relative_beep" : n_relativeBeep})
    data12_df = data12_df[(data12_df['Relative_beep'] < relative_beep_ini) | (data12_df['Relative_beep'] > relative_beep_final)]
    data12_df['rejected'] = 0
    data13_df = pd.concat([data11_df, data12_df]).reset_index(drop = True)  

    # Difference with p_values state
    data14_df = pd.merge(difference_df, data13_df, on=["Relative_beep"]).reset_index(drop = True)

    # Plot
    title = 'Difference between same condition from different experiments, without all outliers.'
    legend = str(condition_min_df['Exp_name'][0]) + ', ' + str(condition_min_df['Name'][0]) + ', ' + str(condition_min_df['Perturb_size'][0]) + '.' 
    Plot_Relative_Beep_Asynch_WithErrorbar(path, minuendo_df, title, legend, '.-', 1, figure_number, False)
    legend = str(condition_sub_df['Exp_name'][0]) + ', ' + str(condition_sub_df['Name'][0]) + ', ' + str(condition_sub_df['Perturb_size'][0]) + '.' 
    Plot_Relative_Beep_Asynch_WithErrorbar(path, subtrahend_df, title, legend, '.-', 1, figure_number, False)
    legend = 'Difference.' 
    Plot_Relative_Beep_Asynch_WithErrorbar(path, data14_df, title, legend, '.--', 1, figure_number, True)

    # Histogram
    if histogram:
        for relativeBeep in n_relativeBeep: 
            figure_number = figure_number + 1
            data_hist_df = (data9_df[data9_df['Relative_beep'] == relativeBeep]).reset_index(drop = True)
            data_hist = pd.Series((data_hist_df["Asyn_zeroed"]))
            intervals = range(int(min(data_hist) - 1), int(max(data_hist) + 2)) 
            p_value = data_hist_df.iloc[0]['p_value']
            real_asyn_zeroed = data_hist_df.iloc[0]['Real_asyn_zeroed']
            plt.figure(num = figure_number)
            plt.hist(data_hist, 100, fc="green")
            plt.vlines(x = real_asyn_zeroed, ymin = 0, ymax = 20)
            plt.xticks(intervals)
            plt.ylabel('Frecuency')
            plt.xlabel('Difference [mS]. real_diff = ' + str(real_asyn_zeroed) + '. p_value = ' + str(p_value))
            plt.title('Difference histogram. Condition: ' + experiment_condition + '. Relative beep: ' + str(relativeBeep))
    
    return


#%% Plot_Asymmetry_Between_Opposite_Conditions_Same_Experiments_BootstrappingPerBeep
# Function to plot asymmetry between opposite conditions (condition per experiment, across all subjects) from same experiment.
# path --> string (ej: '../data_aux/'). data_GroupSubjCond_OS_df --> dataframe. experiment_name --> string (ej: 'Experiment_SC'). 
# experiment_type --> string (ej: 'SC'). perturb_size --> int (ej: 50). relative_beep_ini --> int (ej: 1). relative_beep_final --> int (ej: 6). 
# figure_number --> int (ej: 1). histogram --> boolean (ej: True).
def Plot_Asymmetry_Between_Opposite_Conditions_Same_Experiments_BootstrappingPerBeep(path, data_GroupSubjCond_OS_df, experiment_name, experiment_type, perturb_size, relative_beep_ini, relative_beep_final, figure_number, histogram):

    # Experiments dictionary and data
    experiment_dictionary_df = data_GroupSubjCond_OS_df[0]
    experiment_data_df = data_GroupSubjCond_OS_df[1]
    
    # Search dictionay for experiment_type    
    particular_exp_dic_df = experiment_dictionary_df[experiment_dictionary_df['Exp_name'] == experiment_name]
    particular_exp_dic_df = particular_exp_dic_df[particular_exp_dic_df.Name.str.contains(experiment_type)]
    particular_exp_dic_df = particular_exp_dic_df[(particular_exp_dic_df['Perturb_size'] == perturb_size) | 
                                                  (particular_exp_dic_df['Perturb_size'] == -perturb_size)]
    particular_exp_dic_df.reset_index(drop = True, inplace = True)
       
    # Searching data for experiment_type
    n_gen_cond = particular_exp_dic_df['General_condition'].tolist()
    particular_exp_data_df = pd.DataFrame()
    for gen_cond in n_gen_cond:
        particular_exp_data_aux_df = (experiment_data_df[experiment_data_df['General_condition'] == gen_cond]).reset_index(drop = True)
        particular_exp_data_df = pd.concat([particular_exp_data_df, particular_exp_data_aux_df])
    particular_exp_data_df.reset_index(drop = True, inplace = True) 

    # Mean data across subjects
    groupCond_data_df = (particular_exp_data_df 
                              # then average across subjects
                              .groupby(["Exp_name", "Experiment", "General_condition", "Condition", "Relative_beep"], as_index=False)
                              .agg(Asyn_zeroed = ("mean_asyn", "mean"), sem_asyn = ("mean_asyn", "sem")))

    # Asymmetry
    condition_addUp1_df = particular_exp_dic_df[particular_exp_dic_df.Name.str.contains("neg")].reset_index(drop = True)
    condition_addUp1 = condition_addUp1_df['General_condition'][0]
    condition_addUp2_df = particular_exp_dic_df[particular_exp_dic_df.Name.str.contains("pos")].reset_index(drop = True)
    condition_addUp2 = condition_addUp2_df['General_condition'][0]  
    addingUp1_df = groupCond_data_df[groupCond_data_df['General_condition'] == condition_addUp1].reset_index(drop = True)
    addingUp2_df = groupCond_data_df[groupCond_data_df['General_condition'] == condition_addUp2].reset_index(drop = True)
    asymmetry_df = pd.DataFrame()
    asymmetry_df['Relative_beep'] = addingUp1_df['Relative_beep'] 
    asymmetry_df['Asyn_zeroed'] = addingUp1_df['Asyn_zeroed'] + addingUp2_df['Asyn_zeroed']
    asymmetry_df['sem_asyn'] = addingUp1_df['sem_asyn'] + addingUp2_df['sem_asyn']

    # Particular data per experiment
    particular_exp1_data_df = particular_exp_data_df[particular_exp_data_df['General_condition'] == condition_addUp1]
    particular_exp2_data_df = particular_exp_data_df[particular_exp_data_df['General_condition'] == condition_addUp2]

    # Number of subjects per experiment
    n_subjects_exp1 = len((pd.unique(particular_exp1_data_df['Subject'])).tolist())

    # Bootstrapping
    particular_exp2B_data_df = particular_exp2_data_df.reset_index(drop = True)
    particular_exp2B_data_df['mean_asyn'] = - particular_exp2B_data_df['mean_asyn']         #Invert the sign to the second group
    particular_exp_data2_df = pd.concat([particular_exp1_data_df, particular_exp2B_data_df]).reset_index(drop = True)
    n_iterations = 10000
    asymmetry_totalFake_df = pd.DataFrame()
    for i in range(n_iterations):
        # Random data
        data_df = particular_exp_data2_df.reset_index(drop = True)
        data_df["Fake_condition"] = 0
        data_df = data_df.groupby(["Experiment", "General_condition", "Subject"], as_index=False).agg(Fake_condition = ("Fake_condition", "min"))
        data2_df = data_df.sample(frac = 1).reset_index(drop = True)
        data2_df.loc[data2_df.index > (n_subjects_exp1 - 1), "Fake_condition"] = 1
        data3_df = pd.merge(particular_exp_data2_df, data2_df, on=["Experiment", "General_condition", "Subject"]).reset_index(drop = True)

        # Mean fake data across subjects
        groupCond_fake_data_df = (data3_df 
                                  # then average across subjects
                                  .groupby(["Fake_condition", "Relative_beep"], as_index=False)
                                  .agg(Asyn_zeroed = ("mean_asyn", "mean"), sem_asyn = ("mean_asyn", "sem")))
        
        # Asymmetry fake value
        addingUp1_fake_df = groupCond_fake_data_df[groupCond_fake_data_df['Fake_condition'] == 0].reset_index(drop = True)
        addingUp2_fake_df = groupCond_fake_data_df[groupCond_fake_data_df['Fake_condition'] == 1].reset_index(drop = True)
        asymmetry_fake_df = pd.DataFrame()
        asymmetry_fake_df['Relative_beep'] = addingUp1_fake_df['Relative_beep'] 
        asymmetry_fake_df['Asyn_zeroed'] = addingUp1_fake_df['Asyn_zeroed'] - addingUp2_fake_df['Asyn_zeroed']
        asymmetry_fake_df['sem_asyn'] = addingUp1_fake_df['sem_asyn'] + addingUp2_fake_df['sem_asyn']
        asymmetry_fake_df['Number'] = i
        asymmetry_totalFake_df = pd.concat([asymmetry_totalFake_df, asymmetry_fake_df]).reset_index(drop = True)

    # Merge real values and fake values
    data4_df = asymmetry_df.reset_index(drop = True)
    data4_df.drop(columns = ['sem_asyn'], inplace = True)
    data4_df.rename(columns={"Asyn_zeroed": "Real_asyn_zeroed"}, inplace = True)
    data5_df = pd.merge(data4_df, asymmetry_totalFake_df, on=["Relative_beep"]).reset_index(drop = True)
    data5B_df = asymmetry_totalFake_df.groupby(["Relative_beep"], as_index=False).agg(Mean_asyn_zeroed = ("Asyn_zeroed", "mean"))
    data5_df = pd.merge(data5_df, data5B_df, on=["Relative_beep"]).reset_index(drop = True)

    # P-value
    data6_df = data5_df.reset_index(drop = True)
    data6_df["False_pos_diff"] = 0
    data6_df.loc[(data6_df.Real_asyn_zeroed > data6_df.Mean_asyn_zeroed) & (data6_df.Asyn_zeroed > data6_df.Real_asyn_zeroed),'False_pos_diff'] = 1 
    data6_df.loc[(data6_df.Real_asyn_zeroed < data6_df.Mean_asyn_zeroed) & (data6_df.Asyn_zeroed < data6_df.Real_asyn_zeroed),'False_pos_diff'] = 1 
    data7_df = data6_df.groupby(["Relative_beep"], as_index=False).agg(False_pos_diff = ("False_pos_diff", "sum"))
    data7_df["n_iterations"] = n_iterations
    data7_df["p_value"] = data7_df["False_pos_diff"] / data7_df["n_iterations"]

    # Merge p_values
    data8_df = data7_df.reset_index(drop = True)
    data8_df.drop(columns = ['False_pos_diff', 'n_iterations'], inplace = True)
    data9_df = pd.merge(data8_df, data5_df, on=["Relative_beep"]).reset_index(drop = True) # Data for histograms

    # Applying FDR correction ((Benjamini/Hochberg (non-negative))
    data10_df = data7_df[(data7_df['Relative_beep'] >= relative_beep_ini) & (data7_df['Relative_beep'] <= relative_beep_final)].reset_index(drop = True)
    pvalues_list = data10_df['p_value'].tolist()
    rejected_array, pvalue_corrected_array = sm.fdrcorrection(pvalues_list, alpha = 0.05, method = 'indep', is_sorted = False)
    data10_df['pvalue_corrected'] = pvalue_corrected_array
    data10_df['rejected'] = rejected_array
    data10_df.loc[data10_df.rejected == False, 'rejected'] = 0
    data10_df.loc[data10_df.rejected == True, 'rejected'] = 1
    data10_df.to_csv(path + "pvalue.csv", na_rep = np.NaN)

    # P_values state
    data11_df = data10_df.drop(columns = ['False_pos_diff', 'n_iterations', 'p_value', 'pvalue_corrected'])
    n_relativeBeep = sorted((pd.unique(data7_df['Relative_beep'])).tolist())
    data12_df = pd.DataFrame({"Relative_beep" : n_relativeBeep})
    data12_df = data12_df[(data12_df['Relative_beep'] < relative_beep_ini) | (data12_df['Relative_beep'] > relative_beep_final)]
    data12_df['rejected'] = 0
    data13_df = pd.concat([data11_df, data12_df]).reset_index(drop = True)  

    # Asymmetry with p_values state
    data14_df = pd.merge(asymmetry_df, data13_df, on=["Relative_beep"]).reset_index(drop = True)

    # Plot
    title = 'Asymmetry between opposite conditions from same experiments, without all outliers.'
    legend = str(condition_addUp1_df['Exp_name'][0]) + ', ' + str(condition_addUp1_df['Name'][0]) + ', ' + str(condition_addUp1_df['Perturb_size'][0]) + '.' 
    Plot_Relative_Beep_Asynch_WithErrorbar(path, addingUp1_df, title, legend, '.-', 1, figure_number, False)
    legend = str(condition_addUp2_df['Exp_name'][0]) + ', ' + str(condition_addUp2_df['Name'][0]) + ', ' + str(condition_addUp2_df['Perturb_size'][0]) + '.' 
    Plot_Relative_Beep_Asynch_WithErrorbar(path, addingUp2_df, title, legend, '.-', 1, figure_number, False)
    legend = 'Asymmetry .' 
    Plot_Relative_Beep_Asynch_WithErrorbar(path, data14_df, title, legend, '.--', 1, figure_number, True)

    # Histogram
    if histogram:
        for relativeBeep in n_relativeBeep: 
             figure_number = figure_number + 1
             data_hist_df = (data9_df[data9_df['Relative_beep'] == relativeBeep]).reset_index(drop = True)
             data_hist = pd.Series((data_hist_df["Asyn_zeroed"]))
             intervals = range(int(min(data_hist) - 1), int(max(data_hist) + 2)) 
             p_value = data_hist_df.iloc[0]['p_value']
             real_asyn_zeroed = data_hist_df.iloc[0]['Real_asyn_zeroed']
             plt.figure(num = figure_number)
             plt.hist(data_hist, 100, fc="green")
             plt.vlines(x = real_asyn_zeroed, ymin = 0, ymax = 20)
             plt.xticks(intervals)
             plt.ylabel('Frecuency')
             plt.xlabel('Asymmetry [mS]. real_diff = ' + str(real_asyn_zeroed) + '. p_value = ' + str(p_value))
             plt.title('Asymmetry histogram. Condition: ' + experiment_type + '. Relative beep: ' + str(relativeBeep))
     
    return


#%% Plot_Difference_Between_Same_Condition_Different_Experiments_BootstrappingPerSubject
# Function to plot difference between same condition (condition per experiment, across all subjects) different experiments.
# path --> string (ej: '../data_aux/'). data_GroupSubjCond_OS_df --> dataframe. experiment_name_1 --> string (ej: 'Experiment_SC'). 
# experiment_name_2 --> string (ej: 'Experiment_PS_SC'). experiment_condition --> string (ej: 'SCneg'). perturb_size --> int (ej: 50). 
# relative_beep_ini --> int (ej: 1). relative_beep_final --> int (ej: 6). figure_number --> int (ej: 1). histogram --> boolean (ej: True).
def Plot_Difference_Between_Same_Condition_Different_Experiments_BootstrappingPerSubject(path, data_GroupSubjCond_OS_df, experiment_name_1, experiment_name_2, experiment_condition, perturb_size, relative_beep_ini, relative_beep_final, figure_number, histogram):
    
    # Experiments dictionary and data
    experiment_dictionary_df = data_GroupSubjCond_OS_df[0]
    experiment_data_df = data_GroupSubjCond_OS_df[1]

    # Search dictionay for experiment_type    
    particular_exp_dic_df = experiment_dictionary_df[(experiment_dictionary_df['Exp_name'] == experiment_name_1) | 
                                                     (experiment_dictionary_df['Exp_name'] == experiment_name_2)]
    particular_exp_dic_df = particular_exp_dic_df[particular_exp_dic_df.Name.str.contains(experiment_condition)]
    particular_exp_dic_df = particular_exp_dic_df[(particular_exp_dic_df['Perturb_size'] == perturb_size) | 
                                                  (particular_exp_dic_df['Perturb_size'] == -perturb_size)]
    particular_exp_dic_df.reset_index(drop = True, inplace = True)

    # Searching data for experiment_type
    n_gen_cond = particular_exp_dic_df['General_condition'].tolist()
    particular_exp_data_df = pd.DataFrame()
    for gen_cond in n_gen_cond:
        particular_exp_data_aux_df = (experiment_data_df[experiment_data_df['General_condition'] == gen_cond]).reset_index(drop = True)
        particular_exp_data_df = pd.concat([particular_exp_data_df, particular_exp_data_aux_df])
    particular_exp_data_df.reset_index(drop = True, inplace = True)

    # Mean data across subjects
    groupCond_data_df = (particular_exp_data_df 
                              # then average across subjects
                              .groupby(["Exp_name", "Experiment", "General_condition", "Condition", "Relative_beep"], as_index=False)
                              .agg(Asyn_zeroed = ("mean_asyn", "mean"), sem_asyn = ("mean_asyn", "sem")))
    
    # Difference real value
    condition_min_df = particular_exp_dic_df[particular_exp_dic_df['Exp_name'] == experiment_name_1].reset_index(drop = True)
    condition_min = condition_min_df['General_condition'][0]
    minuendo_df = groupCond_data_df[groupCond_data_df['General_condition'] == condition_min].reset_index(drop = True)
    condition_sub_df = particular_exp_dic_df[particular_exp_dic_df['Exp_name'] == experiment_name_2].reset_index(drop = True)
    condition_sub = condition_sub_df['General_condition'][0]
    subtrahend_df = groupCond_data_df[groupCond_data_df['General_condition'] == condition_sub].reset_index(drop = True)
    difference_df = pd.DataFrame()
    difference_df['Relative_beep'] = minuendo_df['Relative_beep']
    difference_df['Asyn_zeroed'] = minuendo_df['Asyn_zeroed'] - subtrahend_df['Asyn_zeroed']
    difference_df['sem_asyn'] = minuendo_df['sem_asyn'] + subtrahend_df['sem_asyn']
    
    # Particular data per experiment
    particular_exp1_data_df = particular_exp_data_df[particular_exp_data_df['General_condition'] == condition_min]
    particular_exp2_data_df = particular_exp_data_df[particular_exp_data_df['General_condition'] == condition_sub]

    # Number of subjects
    n_subjects_exp1 = len((pd.unique(particular_exp1_data_df['Subject'])).tolist())
    n_subjects_exp2 = len((pd.unique(particular_exp2_data_df['Subject'])).tolist())
    n_subjects = n_subjects_exp1 + n_subjects_exp2
    
    # Subject unique
    particular_exp_data2_df = particular_exp_data_df.reset_index(drop = True)
    particular_exp_data2_df["Subject_unique"] = 0
    particular_exp_data2_df = particular_exp_data2_df.groupby(["Experiment", "General_condition", "Subject"], as_index=False).agg(Subject_unique = ("Subject_unique", "min"))
    particular_exp_data2_df["Subject_unique"] = list(range(n_subjects))
    particular_exp_data2_df.drop(columns = ['General_condition'], inplace = True)
    particular_exp_data3_df = pd.merge(particular_exp_data_df, particular_exp_data2_df, on=["Experiment", "Subject"]).reset_index(drop = True)

    # Bootstrapping
    n_iterations = 10000
    difference_totalFake_df = pd.DataFrame()
    for i in range(n_iterations):
        # Random data
        data_df = particular_exp_data3_df.reset_index(drop = True)
        data_df.set_index(['Subject_unique'], inplace = True) 
        data_df['General_condition'] = data_df.loc[np.random.permutation(data_df.index.unique())][['General_condition']].values

        # Mean fake data across subjects
        groupCond_fake_data_df = (data_df.groupby(["General_condition", "Relative_beep"], as_index=False)
               .agg(Asyn_zeroed = ("mean_asyn", "mean"), sem_asyn = ("mean_asyn", "sem")))
    
        # Difference fake value
        minuendo_fake_df = groupCond_fake_data_df[groupCond_fake_data_df['General_condition'] == condition_min].reset_index(drop = True)
        subtrahend_fake_df = groupCond_fake_data_df[groupCond_fake_data_df['General_condition'] == condition_sub].reset_index(drop = True)
        difference_fake_df = pd.DataFrame()
        difference_fake_df['Relative_beep'] = minuendo_fake_df['Relative_beep']
        difference_fake_df['Asyn_zeroed'] = minuendo_fake_df['Asyn_zeroed'] - subtrahend_fake_df['Asyn_zeroed']
        difference_fake_df['sem_asyn'] = minuendo_fake_df['sem_asyn'] + subtrahend_fake_df['sem_asyn']
        difference_fake_df['Number'] = i 
        difference_totalFake_df = pd.concat([difference_totalFake_df, difference_fake_df]).reset_index(drop = True)  

    # Merge real values and fake values
    data4_df = difference_df.reset_index(drop = True)
    data4_df.drop(columns = ['sem_asyn'], inplace = True)
    data4_df.rename(columns={"Asyn_zeroed": "Real_asyn_zeroed"}, inplace = True)
    data5_df = pd.merge(data4_df, difference_totalFake_df, on=["Relative_beep"]).reset_index(drop = True)
    data5B_df = difference_totalFake_df.groupby(["Relative_beep"], as_index=False).agg(Mean_asyn_zeroed = ("Asyn_zeroed", "mean"))
    data5_df = pd.merge(data5_df, data5B_df, on=["Relative_beep"]).reset_index(drop = True)

    # P-value
    data6_df = data5_df.reset_index(drop = True)
    data6_df["False_pos_diff"] = 0
    data6_df.loc[(data6_df.Real_asyn_zeroed > data6_df.Mean_asyn_zeroed) & (data6_df.Asyn_zeroed > data6_df.Real_asyn_zeroed),'False_pos_diff'] = 1 
    data6_df.loc[(data6_df.Real_asyn_zeroed < data6_df.Mean_asyn_zeroed) & (data6_df.Asyn_zeroed < data6_df.Real_asyn_zeroed),'False_pos_diff'] = 1 
    #data6_df.loc[data6_df.Asyn_zeroed > data6_df.Real_asyn_zeroed,'False_pos_diff'] = 1    
    data7_df = data6_df.groupby(["Relative_beep"], as_index=False).agg(False_pos_diff = ("False_pos_diff", "sum"))
    data7_df["n_iterations"] = n_iterations
    data7_df["p_value"] = data7_df["False_pos_diff"] / data7_df["n_iterations"]
    
    # Merge p_values
    data8_df = data7_df.reset_index(drop = True)
    data8_df.drop(columns = ['False_pos_diff', 'n_iterations'], inplace = True)
    data9_df = pd.merge(data8_df, data5_df, on=["Relative_beep"]).reset_index(drop = True) # Data for histograms

    # Applying FDR correction ((Benjamini/Hochberg (non-negative))
    data10_df = data7_df[(data7_df['Relative_beep'] >= relative_beep_ini) & (data7_df['Relative_beep'] <= relative_beep_final)].reset_index(drop = True)
    pvalues_list = data10_df['p_value'].tolist()
    rejected_array, pvalue_corrected_array = sm.fdrcorrection(pvalues_list, alpha = 0.05, method = 'indep', is_sorted = False)
    data10_df['pvalue_corrected'] = pvalue_corrected_array
    data10_df['rejected'] = rejected_array
    data10_df.loc[data10_df.rejected == False, 'rejected'] = 0
    data10_df.loc[data10_df.rejected == True, 'rejected'] = 1
    data10_df.to_csv(path + "pvalue.csv", na_rep = np.NaN)

    # P_values state
    data11_df = data10_df.drop(columns = ['False_pos_diff', 'n_iterations', 'p_value', 'pvalue_corrected'])
    n_relativeBeep = sorted((pd.unique(data7_df['Relative_beep'])).tolist())
    data12_df = pd.DataFrame({"Relative_beep" : n_relativeBeep})
    data12_df = data12_df[(data12_df['Relative_beep'] < relative_beep_ini) | (data12_df['Relative_beep'] > relative_beep_final)]
    data12_df['rejected'] = 0
    data13_df = pd.concat([data11_df, data12_df]).reset_index(drop = True)  

    # Difference with p_values state
    data14_df = pd.merge(difference_df, data13_df, on=["Relative_beep"]).reset_index(drop = True)

    # Plot
    title = 'Difference between same condition from different experiments, without all outliers.'
    legend = str(condition_min_df['Exp_name'][0]) + ', ' + str(condition_min_df['Name'][0]) + ', ' + str(condition_min_df['Perturb_size'][0]) + '.' 
    Plot_Relative_Beep_Asynch_WithErrorbar(path, minuendo_df, title, legend, '.-', 1, figure_number, False)
    legend = str(condition_sub_df['Exp_name'][0]) + ', ' + str(condition_sub_df['Name'][0]) + ', ' + str(condition_sub_df['Perturb_size'][0]) + '.' 
    Plot_Relative_Beep_Asynch_WithErrorbar(path, subtrahend_df, title, legend, '.-', 1, figure_number, False)
    legend = 'Difference.' 
    Plot_Relative_Beep_Asynch_WithErrorbar(path, data14_df, title, legend, '.--', 1, figure_number, True)

    # Histogram
    if histogram:
        for relativeBeep in n_relativeBeep: 
            figure_number = figure_number + 1
            data_hist_df = (data9_df[data9_df['Relative_beep'] == relativeBeep]).reset_index(drop = True)
            data_hist = pd.Series((data_hist_df["Asyn_zeroed"]))
            intervals = range(int(min(data_hist) - 1), int(max(data_hist) + 2)) 
            p_value = data_hist_df.iloc[0]['p_value']
            real_asyn_zeroed = data_hist_df.iloc[0]['Real_asyn_zeroed']
            plt.figure(num = figure_number)
            plt.hist(data_hist, 100, fc="green")
            plt.vlines(x = real_asyn_zeroed, ymin = 0, ymax = 20)
            plt.xticks(intervals)
            plt.ylabel('Frecuency')
            plt.xlabel('Difference [mS]. real_diff = ' + str(real_asyn_zeroed) + '. p_value = ' + str(p_value))
            plt.title('Difference histogram. Condition: ' + experiment_condition + '. Relative beep: ' + str(relativeBeep))
    
    return


#%% Plot_Asymmetry_Between_Opposite_Conditions_Same_Experiments_BootstrappingPerSubject
# Function to plot asymmetry between opposite conditions (condition per experiment, across all subjects) from same experiment.
# path --> string (ej: '../data_aux/'). data_GroupSubjCond_OS_df --> dataframe. experiment_name --> string (ej: 'Experiment_SC'). 
# experiment_type --> string (ej: 'SC'). perturb_size --> int (ej: 50). relative_beep_ini --> int (ej: 1). relative_beep_final --> int (ej: 6). 
# figure_number --> int (ej: 1). histogram --> boolean (ej: True).
def Plot_Asymmetry_Between_Opposite_Conditions_Same_Experiments_BootstrappingPerSubject(path, data_GroupSubjCond_OS_df, experiment_name, experiment_type, perturb_size, relative_beep_ini, relative_beep_final, figure_number, histogram):

    # Experiments dictionary and data
    experiment_dictionary_df = data_GroupSubjCond_OS_df[0]
    experiment_data_df = data_GroupSubjCond_OS_df[1]
    
    # Search dictionay for experiment_type    
    particular_exp_dic_df = experiment_dictionary_df[experiment_dictionary_df['Exp_name'] == experiment_name]
    particular_exp_dic_df = particular_exp_dic_df[particular_exp_dic_df.Name.str.contains(experiment_type)]
    particular_exp_dic_df = particular_exp_dic_df[(particular_exp_dic_df['Perturb_size'] == perturb_size) | 
                                                  (particular_exp_dic_df['Perturb_size'] == -perturb_size)]
    particular_exp_dic_df.reset_index(drop = True, inplace = True)
    
    # Searching data for experiment_type
    n_gen_cond = particular_exp_dic_df['General_condition'].tolist()
    particular_exp_data_df = pd.DataFrame()
    for gen_cond in n_gen_cond:
        particular_exp_data_aux_df = (experiment_data_df[experiment_data_df['General_condition'] == gen_cond]).reset_index(drop = True)
        particular_exp_data_df = pd.concat([particular_exp_data_df, particular_exp_data_aux_df])
    particular_exp_data_df.reset_index(drop = True, inplace = True) 

    # Mean data across subjects
    groupCond_data_df = (particular_exp_data_df 
                              # then average across subjects
                              .groupby(["Exp_name", "Experiment", "General_condition", "Condition", "Relative_beep"], as_index=False)
                              .agg(Asyn_zeroed = ("mean_asyn", "mean"), sem_asyn = ("mean_asyn", "sem")))

    # Asymmetry
    condition_addUp1_df = particular_exp_dic_df[particular_exp_dic_df.Name.str.contains("neg")].reset_index(drop = True)
    condition_addUp1 = condition_addUp1_df['General_condition'][0]
    condition_addUp2_df = particular_exp_dic_df[particular_exp_dic_df.Name.str.contains("pos")].reset_index(drop = True)
    condition_addUp2 = condition_addUp2_df['General_condition'][0]  
    addingUp1_df = groupCond_data_df[groupCond_data_df['General_condition'] == condition_addUp1].reset_index(drop = True)
    addingUp2_df = groupCond_data_df[groupCond_data_df['General_condition'] == condition_addUp2].reset_index(drop = True)
    asymmetry_df = pd.DataFrame()
    asymmetry_df['Relative_beep'] = addingUp1_df['Relative_beep'] 
    asymmetry_df['Asyn_zeroed'] = addingUp1_df['Asyn_zeroed'] + addingUp2_df['Asyn_zeroed']
    asymmetry_df['sem_asyn'] = addingUp1_df['sem_asyn'] + addingUp2_df['sem_asyn']

    # Particular data per experiment
    particular_exp1_data_df = particular_exp_data_df[particular_exp_data_df['General_condition'] == condition_addUp1]
    particular_exp2_data_df = particular_exp_data_df[particular_exp_data_df['General_condition'] == condition_addUp2]

    # Number of subjects per experiment
    n_subjects_exp1 = len((pd.unique(particular_exp1_data_df['Subject'])).tolist())
    n_subjects_exp2 = len((pd.unique(particular_exp2_data_df['Subject'])).tolist())
    n_subjects = n_subjects_exp1 + n_subjects_exp2

    # Invert the sign to the second group
    particular_exp2B_data_df = particular_exp2_data_df.reset_index(drop = True)
    particular_exp2B_data_df['mean_asyn'] = - particular_exp2B_data_df['mean_asyn']         
    particular_exp_data2_df = pd.concat([particular_exp1_data_df, particular_exp2B_data_df]).reset_index(drop = True)
    
    # Subject unique
    particular_exp_data3_df = particular_exp_data2_df.reset_index(drop = True)
    particular_exp_data3_df["Subject_unique"] = 0
    particular_exp_data3_df = particular_exp_data3_df.groupby(["Experiment", "General_condition", "Subject"], as_index=False).agg(Subject_unique = ("Subject_unique", "min"))
    particular_exp_data3_df["Subject_unique"] = list(range(n_subjects))
    particular_exp_data3_df.drop(columns = ['Experiment'], inplace = True)
    particular_exp_data4_df = pd.merge(particular_exp_data2_df, particular_exp_data3_df, on=["General_condition", "Subject"]).reset_index(drop = True)
    
    # Bootstrapping
    n_iterations = 10000
    asymmetry_totalFake_df = pd.DataFrame()
    for i in range(n_iterations):
        # Random data
        data_df = particular_exp_data4_df.reset_index(drop = True)
        data_df.set_index(['Subject_unique'], inplace = True) 
        data_df['General_condition'] = data_df.loc[np.random.permutation(data_df.index.unique())][['General_condition']].values
        
        # Mean fake data across subjects
        groupCond_fake_data_df = (data_df.groupby(["General_condition", "Relative_beep"], as_index=False)
               .agg(Asyn_zeroed = ("mean_asyn", "mean"), sem_asyn = ("mean_asyn", "sem")))
        
        # Asymmetry fake value
        addingUp1_fake_df = groupCond_fake_data_df[groupCond_fake_data_df['General_condition'] == condition_addUp1].reset_index(drop = True)
        addingUp2_fake_df = groupCond_fake_data_df[groupCond_fake_data_df['General_condition'] == condition_addUp2].reset_index(drop = True)
        asymmetry_fake_df = pd.DataFrame()
        asymmetry_fake_df['Relative_beep'] = addingUp1_fake_df['Relative_beep'] 
        asymmetry_fake_df['Asyn_zeroed'] = addingUp1_fake_df['Asyn_zeroed'] - addingUp2_fake_df['Asyn_zeroed']
        asymmetry_fake_df['sem_asyn'] = addingUp1_fake_df['sem_asyn'] + addingUp2_fake_df['sem_asyn']
        asymmetry_fake_df['Number'] = i
        asymmetry_totalFake_df = pd.concat([asymmetry_totalFake_df, asymmetry_fake_df]).reset_index(drop = True)
        
    # Merge real values and fake values
    data4_df = asymmetry_df.reset_index(drop = True)
    data4_df.drop(columns = ['sem_asyn'], inplace = True)
    data4_df.rename(columns={"Asyn_zeroed": "Real_asyn_zeroed"}, inplace = True)
    data5_df = pd.merge(data4_df, asymmetry_totalFake_df, on=["Relative_beep"]).reset_index(drop = True)
    data5B_df = asymmetry_totalFake_df.groupby(["Relative_beep"], as_index=False).agg(Mean_asyn_zeroed = ("Asyn_zeroed", "mean"))
    data5_df = pd.merge(data5_df, data5B_df, on=["Relative_beep"]).reset_index(drop = True)

    # P-value
    data6_df = data5_df.reset_index(drop = True)
    data6_df["False_pos_diff"] = 0
    data6_df.loc[(data6_df.Real_asyn_zeroed > data6_df.Mean_asyn_zeroed) & (data6_df.Asyn_zeroed > data6_df.Real_asyn_zeroed),'False_pos_diff'] = 1 
    data6_df.loc[(data6_df.Real_asyn_zeroed < data6_df.Mean_asyn_zeroed) & (data6_df.Asyn_zeroed < data6_df.Real_asyn_zeroed),'False_pos_diff'] = 1 
    data7_df = data6_df.groupby(["Relative_beep"], as_index=False).agg(False_pos_diff = ("False_pos_diff", "sum"))
    data7_df["n_iterations"] = n_iterations
    data7_df["p_value"] = data7_df["False_pos_diff"] / data7_df["n_iterations"]

    # Merge p_values
    data8_df = data7_df.reset_index(drop = True)
    data8_df.drop(columns = ['False_pos_diff', 'n_iterations'], inplace = True)
    data9_df = pd.merge(data8_df, data5_df, on=["Relative_beep"]).reset_index(drop = True) # Data for histograms

    # Applying FDR correction ((Benjamini/Hochberg (non-negative))
    data10_df = data7_df[(data7_df['Relative_beep'] >= relative_beep_ini) & (data7_df['Relative_beep'] <= relative_beep_final)].reset_index(drop = True)
    pvalues_list = data10_df['p_value'].tolist()
    rejected_array, pvalue_corrected_array = sm.fdrcorrection(pvalues_list, alpha = 0.05, method = 'indep', is_sorted = False)
    data10_df['pvalue_corrected'] = pvalue_corrected_array
    data10_df['rejected'] = rejected_array
    data10_df.loc[data10_df.rejected == False, 'rejected'] = 0
    data10_df.loc[data10_df.rejected == True, 'rejected'] = 1
    data10_df.to_csv(path + "pvalue.csv", na_rep = np.NaN)

    # P_values state
    data11_df = data10_df.drop(columns = ['False_pos_diff', 'n_iterations', 'p_value', 'pvalue_corrected'])
    n_relativeBeep = sorted((pd.unique(data7_df['Relative_beep'])).tolist())
    data12_df = pd.DataFrame({"Relative_beep" : n_relativeBeep})
    data12_df = data12_df[(data12_df['Relative_beep'] < relative_beep_ini) | (data12_df['Relative_beep'] > relative_beep_final)]
    data12_df['rejected'] = 0
    data13_df = pd.concat([data11_df, data12_df]).reset_index(drop = True)  

    # Asymmetry with p_values state
    data14_df = pd.merge(asymmetry_df, data13_df, on=["Relative_beep"]).reset_index(drop = True)

    # Plot
    title = 'Asymmetry between opposite conditions from same experiments, without all outliers.'
    legend = str(condition_addUp1_df['Exp_name'][0]) + ', ' + str(condition_addUp1_df['Name'][0]) + ', ' + str(condition_addUp1_df['Perturb_size'][0]) + '.' 
    Plot_Relative_Beep_Asynch_WithErrorbar(path, addingUp1_df, title, legend, '.-', 1, figure_number, False)
    legend = str(condition_addUp2_df['Exp_name'][0]) + ', ' + str(condition_addUp2_df['Name'][0]) + ', ' + str(condition_addUp2_df['Perturb_size'][0]) + '.' 
    Plot_Relative_Beep_Asynch_WithErrorbar(path, addingUp2_df, title, legend, '.-', 1, figure_number, False)
    legend = 'Asymmetry .' 
    Plot_Relative_Beep_Asynch_WithErrorbar(path, data14_df, title, legend, '.--', 1, figure_number, True)

    # Histogram
    if histogram:
        for relativeBeep in n_relativeBeep: 
             figure_number = figure_number + 1
             data_hist_df = (data9_df[data9_df['Relative_beep'] == relativeBeep]).reset_index(drop = True)
             data_hist = pd.Series((data_hist_df["Asyn_zeroed"]))
             intervals = range(int(min(data_hist) - 1), int(max(data_hist) + 2)) 
             p_value = data_hist_df.iloc[0]['p_value']
             real_asyn_zeroed = data_hist_df.iloc[0]['Real_asyn_zeroed']
             plt.figure(num = figure_number)
             plt.hist(data_hist, 100, fc="green")
             plt.vlines(x = real_asyn_zeroed, ymin = 0, ymax = 20)
             plt.xticks(intervals)
             plt.ylabel('Frecuency')
             plt.xlabel('Asymmetry [mS]. real_diff = ' + str(real_asyn_zeroed) + '. p_value = ' + str(p_value))
             plt.title('Asymmetry histogram. Condition: ' + experiment_type + '. Relative beep: ' + str(relativeBeep))
     
    return

