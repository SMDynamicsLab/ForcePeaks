#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Sep  8 13:46:34 2022

@author: RLaje, Asilva
"""

import analisis_aux as aux
import sys
# Setting path.
sys.path.append('../experiment')
# Importing.


#%% Define Python user-defined exceptions.
class Error(Exception):
	"""Base class for other exceptions"""
	pass


#%% DEFINITIONS FOR ALL EXPERIMENTS (version 1.1).
# Preprocessing data version 1.1 (Add outliers per subj cond analysis): Preperturbation zeroed. At the end, outlier cuantification. 


# Define path.
path = '../data_aux/'


#%%










#%% Preprocessing_Data
# Function to process data for all experiments and general conditions dictionary, 
# considering the transient and the beeps out of range. Return tuple with two dataframes.
# path --> string (ej: '../data_aux/'). transient_dur --> int (ej: 1).
data_df = aux.Preprocessing_Data(path, 7)


#%% Preprocessing_Data_AllExperiments_MarkingOutliers
# Function to process data for all experiments and general conditions dictionary, marking outlier trials. Return a tuple with three dataframes.
# path --> string (ej: '../data_aux/'). data_df --> dataframe. postPerturb_bip --> int (ej: 5).
data_OutTrials_df = aux.Preprocessing_Data_AllExperiments_MarkingTrialOutliers(path, data_df, 7)


#%% Outliers_Trials_Cuantification
# Function to know outlier trials information.
# path --> string (ej: '../data_aux/'). data_OutTrials_df --> dataframe.
aux.Outliers_Trials_Cuantification(path, data_OutTrials_df)


#%% Plot_Valid_Trials_Asyn_PerSubject_PerCondition_And_Mean
# Function to plot trial asynchronies per valid trial, and trials mean without outlier trials.
# path --> string (ej: '../data_aux/'). data_OutTrials_df --> dataframe. experiment_name --> string (ej: 'Experiment_PS_SC'). 
# experiment_condition --> string (ej: 'SCneg'). perturb_size --> int (ej: 50). subject --> int (ej: 0). figure_number --> int (ej: 1).
aux.Plot_Valid_Trials_Asyn_PerSubject_PerCondition_And_Mean(path, data_OutTrials_df, 'Experiment_PS_SC', 'SCpos', 50, 1, 1)


#%%










#%% Preprocessing_Data_AllExperiments_MarkingSubjCondOutliers
# Function to process data for all experiments and general conditions dictionary, marking outlier subject conditions. Return a tuple with four dataframes.
# path --> string (ej: '../data_aux/'). data_OutTrials_df--> dataframe. porcTrialPrevCond --> int (ej: 10). postPerturb_bip --> int (ej: 5).
data_OutSubjCond_df = aux.Preprocessing_Data_AllExperiments_MarkingSubjCondOutliers(path, data_OutTrials_df, 50, 7)


#%% Outliers_SubjCond_Cuantification
# Function to know outlier subject conditions cuantification.
# path --> string (ej: '../data_aux/'). data_OutSubjCond_df --> dataframe.
aux.Outliers_SubjCond_Cuantification(path, data_OutSubjCond_df)


#%%










#%% Preprocessing_Data_AllExperiments_MarkingSubjOutliers
# Function to process data for all experiments and general conditions dictionary, marking outlier subjects. Return a tuple with four dataframes.
# path --> string (ej: '../data_aux/'). data_OutSubjCond_df --> dataframe. porcSubjCondPrevCond --> int (ej: 10).
data_OutSubj_df = aux.Preprocessing_Data_AllExperiments_MarkingSubjOutliers(path, data_OutSubjCond_df, 50)


#%% Outliers_Subj_Cuantification
# Function to know outlier subjects cuantification.
# path --> string (ej: '../data_aux/'). data_OutSubj_df --> dataframe.
aux.Outliers_Subj_Cuantification(path, data_OutSubj_df)


#%%










#%% Group_Subject_Condition_Outlier_SubjCond
# Function to obtain meanasyn and stdasyn for each group subject condition.
data_GroupSubjCond_OSC_df = aux.Group_Subject_Condition_Outlier_SubjCond(data_OutSubjCond_df)


#%% Group_Subject_Condition_Outlier_Subject
# Function to obtain meanasyn and stdasyn for each group subject condition.
data_GroupSubjCond_OS_df = aux.Group_Subject_Condition_Outlier_Subject(data_OutSubj_df)
    
    
#%% Plot_Mean_Valid_Trials_Asyn_AllSubjectcs_PerCondition_And_MeanOfTheLastOnes_WithoutOutliers_perTrialAndSubjCondAnalysis
# Function to plot mean trials asynchronies across all subjects, per condition and mean of the last ones. Without oulier per Trial and Subj Cond Analysis.
# Outlier subjects in dotted line. Mean only of the non outliers subjects. 
# path --> string (ej: '../data_aux/'). data_df --> dataframe. experiment_name --> string (ej: 'Experiment_SC'). experiment_condition --> string (ej: 'SCneg'). perturb_size --> int (ej: 50). figure_number --> int (ej: 1). 
aux.Plot_Mean_Valid_Trials_Asyn_AllSubjectcs_PerCondition_And_MeanOfTheLastOnes_WithoutOutliers_perTrialAndSubjCondAnalysis(path, data_GroupSubjCond_OS_df, 'Experiment_PS', 'PSneg', 50, 1)


#%% Boxplot_And_Dots
# Function to plot boxplot and stripplot to see quantile criteria.
# path --> string (ej: '../data_aux/'). data_OutSubjCond_df --> dataframe. experiment_name --> string (ej: 'Experiment_SC'). experiment_condition --> string (ej: 'SCneg'). perturb_size --> int (ej: 50). postPerturb_bip --> int (ej: 5). figure_number_1 --> int (ej: 1). figure_number_2 --> int (ej: 2). 
aux.Boxplot_And_Dots(path, data_GroupSubjCond_OS_df, 'Experiment_SC', 'SCpos', 50, 7, 2, 3)


#%%










#%% Plot_Difference_Between_Same_Condition_Different_Experiments
# Function to plot difference between same condition (condition per experiment, across all subjects) different experiments.
# path --> string (ej: '../data_aux/'). data_GroupSubjCond_OS_df --> dataframe. experiment_name_1 --> string (ej: 'Experiment_SC'). 
# experiment_name_2 --> string (ej: 'Experiment_PS_SC'). experiment_condition --> string (ej: 'SCneg'). perturb_size --> int (ej: 50). 
# relative_beep_ini --> int (ej: 1). relative_beep_final --> int (ej: 6). figure_number --> int (ej: 1).
aux.Plot_Difference_Between_Same_Condition_Different_Experiments(path, data_GroupSubjCond_OS_df, 'Experiment_PS', 'Experiment_PS_SC', 'PSpos', 50, 1, 6, 1)
  

#%% Plot_Asymmetry_Between_Opposite_Conditions_Same_Experiments
# Function to plot asymmetry between opposite conditions (condition per experiment, across all subjects) from same experiment.
# path --> string (ej: '../data_aux/'). data_GroupSubjCond_OS_df --> dataframe. experiment_name --> string (ej: 'Experiment_SC'). 
# experiment_type --> string (ej: 'SC'). perturb_size --> int (ej: 50). relative_beep_ini --> int (ej: 1). relative_beep_final --> int (ej: 6). figure_number --> int (ej: 1).
aux.Plot_Asymmetry_Between_Opposite_Conditions_Same_Experiments(path, data_GroupSubjCond_OS_df, 'Experiment_PS_SC', 'PS', 50, 1, 6, 2)


#%%










#%% Plot_Difference_Between_Same_Condition_Different_Experiments_BootstrappingPerBeep
# Function to plot difference between same condition (condition per experiment, across all subjects) different experiments.
# path --> string (ej: '../data_aux/'). data_GroupSubjCond_OS_df --> dataframe. experiment_name_1 --> string (ej: 'Experiment_SC'). 
# experiment_name_2 --> string (ej: 'Experiment_PS_SC'). experiment_condition --> string (ej: 'SCneg'). perturb_size --> int (ej: 50). 
# relative_beep_ini --> int (ej: 1). relative_beep_final --> int (ej: 6). figure_number --> int (ej: 1). histogram --> boolean (ej: True).
aux.Plot_Difference_Between_Same_Condition_Different_Experiments_BootstrappingPerBeep(path, data_GroupSubjCond_OS_df, 'Experiment_PS', 'Experiment_PS_SC', 'PSneg', 50, 1, 6, 1, False)


#%% Plot_Asymmetry_Between_Opposite_Conditions_Same_Experiments_BootstrappingPerBeep
# Function to plot asymmetry between opposite conditions (condition per experiment, across all subjects) from same experiment.
# path --> string (ej: '../data_aux/'). data_GroupSubjCond_OS_df --> dataframe. experiment_name --> string (ej: 'Experiment_SC'). 
# experiment_type --> string (ej: 'SC'). perturb_size --> int (ej: 50). relative_beep_ini --> int (ej: 1). relative_beep_final --> int (ej: 6). 
# figure_number --> int (ej: 1). histogram --> boolean (ej: True).
aux.Plot_Asymmetry_Between_Opposite_Conditions_Same_Experiments_BootstrappingPerBeep(path, data_GroupSubjCond_OS_df, 'Experiment_PS_SC', 'SC', 50, 1, 6, 1, True)


#%%










#%% Plot_Difference_Between_Same_Condition_Different_Experiments_BootstrappingPerSubject
# Function to plot difference between same condition (condition per experiment, across all subjects) different experiments.
# path --> string (ej: '../data_aux/'). data_GroupSubjCond_OS_df --> dataframe. experiment_name_1 --> string (ej: 'Experiment_SC'). 
# experiment_name_2 --> string (ej: 'Experiment_PS_SC'). experiment_condition --> string (ej: 'SCneg'). perturb_size --> int (ej: 50). 
# relative_beep_ini --> int (ej: 1). relative_beep_final --> int (ej: 6). figure_number --> int (ej: 1). histogram --> boolean (ej: True).
aux.Plot_Difference_Between_Same_Condition_Different_Experiments_BootstrappingPerSubject(path, data_GroupSubjCond_OS_df, 'Experiment_PS', 'Experiment_PS_SC', 'PSneg', 50, 1, 6, 2, False)


#%% Plot_Asymmetry_Between_Opposite_Conditions_Same_Experiments_BootstrappingPerSubject
# Function to plot asymmetry between opposite conditions (condition per experiment, across all subjects) from same experiment.
# path --> string (ej: '../data_aux/'). data_GroupSubjCond_OS_df --> dataframe. experiment_name --> string (ej: 'Experiment_SC'). 
# experiment_type --> string (ej: 'SC'). perturb_size --> int (ej: 50). relative_beep_ini --> int (ej: 1). relative_beep_final --> int (ej: 6). 
# figure_number --> int (ej: 1). histogram --> boolean (ej: True).
aux.Plot_Asymmetry_Between_Opposite_Conditions_Same_Experiments_BootstrappingPerSubject(path, data_GroupSubjCond_OS_df, 'Experiment_PS_SC', 'SC', 50, 1, 6, 1, True)

