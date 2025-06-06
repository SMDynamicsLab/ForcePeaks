# -*- coding: utf-8 -*-
#%% Importo Librerias
"""
@author: Tucu y Pachu

Copyright © 2023 Tucu-Pachu. All rights reserved.

===============================
elTucu-labs
===============================

This product includes software developed by elTucu-labs. Project for use in the lab project.

Redistribution and use in source and binary forms, with or without modification, are permitted provided 
that the following conditions are met:

*Redistributions of source code must remain the above copyright notice, this list of conditions and the
following disclaimer. 

*Redistributions in binary form must reproduce the above copyright notice, this list of conditions and 
the following disclaimer in the documentation and/or other materials provided with the distribution.


*Neither the name of the Lab nor the names of its contributors may be used to endorse or promote products
derived from this software without specific prior written permission.

"""

import numpy as np
import matplotlib.pyplot as plt
from tqdm import tqdm
import os
import pandas as pd 
from scipy.signal import find_peaks
import math
import glob
import json
from IPython import get_ipython
#get_ipython().run_line_magic("matplotlib","qt5")


#%% datos(sujeto,block,trial) = data de ese trial

# Funcion para abrir los datos de un trial especifico de algun sujeto
def datos(numero_de_sujeto, block, trial):
    # Primero que recopile los datos
    register_subjs_path = '../data/registered_subjects.dat'
    with open(register_subjs_path,"r") as fp:
        subj_number_fullstring = fp.readlines()[numero_de_sujeto].replace("\n", "") # devuelve el S01 si #sujeto = 1
   
    print(subj_number_fullstring)
    for filename in os.listdir('../data'): # en el () va el path
        if filename.startswith('S' + subj_number_fullstring) and filename.endswith("block" + str(block) + "-" + "trial" + str(trial) + ".dat"):
            data_fname = filename
    
    print(data_fname)
    file_to_load = glob.glob(f"../data/{data_fname}")[0]
    f_to_load = open(file_to_load,"r")
    content = f_to_load.read()
    f_to_load.close()
    content = json.loads(content)
    return content

#%% tap_separator(voltajes) = taps, peaks

def tap_separator(voltajes,tap_length):
    taps = []
    start_i = 10000
    for v in range(len(voltajes)-10):
       
        if voltajes[v] == 0 and voltajes[v+1] > 0:
            start_i = v
            # print(start_i)
        # if v > start_i and voltajes[v] > 0 and voltajes[v+1] == 0 and voltajes[v+10] == 0 and start_i<(len(voltajes)-45):
        if v > start_i and voltajes[v] > 0 and voltajes[v+1] == 0 and start_i<(len(voltajes)-tap_length):
            end_i = v
            bip = np.asarray(voltajes[start_i+1:end_i+3])
            # print("start_i =" +str(start_i))
            # print("end_i =" +str(end_i))
            if len(bip)>8:    
                bip_posta =  np.asarray(voltajes[start_i+1:start_i+tap_length+1])
                taps.append(bip_posta)
                
    peaks = []
    p_min = 0
    taps_posta = []
    for b in taps:
        pk, _ = find_peaks(b, distance=5,height=10, width = 3)
        if len(pk)>1:
            if b[pk[0]]> b[pk[-1]]:
                taps_posta.append(b)
                peaks.append(pk[:2])
        if len(pk)==1:           
            pk = np.concatenate((pk,[np.nan]))
            taps_posta.append(b)
            peaks.append(pk[:2])
        if len(pk)==0:
            pk = [np.nan,np.nan]
            taps_posta.append(b)
            peaks.append(pk[:2])      
        
        min_peaks,_ = find_peaks(-b, distance=5, width = 3)
        if len(min_peaks) != 0: 
            p_min = min_peaks[0]
            
              
    return taps_posta, peaks, p_min

#%% Para seleccionar trials y taps fallidos
 
tap_length = 50
trials_per_block = 9 
blocks_per_subj = 4
ppf = 6 # el primer pico de fuerza que medimos (tiramos los primeros 5)
heigth_interval = 10 # diferencia minima de altura entre el primer pico y el primer minimo
register_subjs_path = '../data/registered_subjects.dat'
subjects = []

tap_length = 50
trials_per_block = 9 
blocks_per_subj = 4

#%% cond_of_trial()

def cond_of_trial(subject,block,trial,trials_per_block):
    path_po = '../data/presentation_orders.csv'
    with open(path_po, 'r') as file:
        f = file.readlines()
    cond =  list(f[1+ trial+block*trials_per_block].split(","))[subject + 2]
    return cond

#%% Data Frame de Tiempos y Voltajes
blocks_per_subj = 4
register_subjs_path = '../data/registered_subjects.dat'
subjects = [0]
with open(register_subjs_path,"r") as fp:
    for i in fp.readlines():
        subjects.append(int(i.replace("\n", "").replace("S", "")))
        
ppf = 6 # el primer pico de fuerza que medimos (tiramos los primeros 5)
trials_per_block = 9

df = pd.DataFrame({'Subjs':[], 'Block':[], 'Trial':[], 'Cond':[], 'Tap':[], 'P1':[], 'P2':[], 'Asyns_c':[],'Asyns_p1':[],'Asyns_p2':[],'Peak_interval':[]}) # 'Asign_Resp':[]
df_voltage = pd.DataFrame({'Subjs':[], 'Block':[], 'Trial':[], 'Cond':[], 'Tap':[], 'Time':[], 'Voltages':[]})

#subjs = [1,2,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21]#sujetos 0 y 3 descartados por falta de contenido
subjs = [1,2,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,
        29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52] 
# sujetos 0 y 3 descartados por falta de contenido

# La idea es que cada fila es un bip
for s in subjs:
    for block in tqdm(range(blocks_per_subj)): # number_of_blocks
        for t in range(trials_per_block): # number of trials_per_block
            datos_trial = datos(s,block,t)
            resp_time   = datos_trial['Resp_time']
            stim_time   = datos_trial['Stim_time']
            asyns       = datos_trial["Asynchrony"]
            voltajes    = datos_trial["voltage_value"]
            assign_stim = datos_trial['Stim_assigned_to_asyn']
            
            taps, peaks, p_min = tap_separator(np.asarray(voltajes),tap_length)
            taps=np.asarray(taps)
            peaks=np.asarray(peaks)
            # print(np.shape(peaks))
            # print(np.shape(taps))
            cond = cond_of_trial(s, block, t, trials_per_block)
            
            if len(np.asarray(assign_stim))>1:
                cosito=np.argwhere(np.array(assign_stim)>=ppf-1)
                if len(cosito)>0:
                    indice =  int(cosito[0][0]) #NUESTRO PROBLEMA ES CAUNDO NO EXISTE UNO MAYOR A 6
                    # indice del primer elemento mayo o igual a 5
                    asyns_over6 = asyns[indice:]
                    
                
                    resp_time_taps = resp_time[len(resp_time)-len(taps):]
                    asyns_taps = asyns[len(asyns)-len(taps):]
                    for tap in range(len(asyns_taps)):  
                        # asign_stim_tap = assign_stim[tap+indice]
                        if not math.isnan(asyns_taps[tap]):              
                            if not math.isnan(peaks[tap][1]):
                                if peaks[tap][0] < p_min and peaks[tap][1] > p_min and (taps[tap][int(peaks[tap][0])] - taps[tap][int(p_min)]) > heigth_interval:
                                    c_asyn = asyns_taps[tap] 
                                    p1_tap = peaks[tap][0] # 
                                    p2_tap = peaks[tap][1] # esta es la asincronia de p2 con la respuesta
                                    # asyns_p2 = resp_time[tap+indice] + p2_tap[tap] - stim_time[asing_stim_tap]
                                    asyns_p1 = c_asyn + p1_tap
                                    asyns_p2 = c_asyn + p2_tap
                                    peak_interval = p2_tap-p1_tap
                                    df.loc[len(df.index)] = [s, block, t, cond, tap, p1_tap, p2_tap, c_asyn, asyns_p1, asyns_p2, peak_interval] 
                                    for ms in range(len(taps[tap])):                 
                                        voltage = taps[tap][ms]
                                        
                                        df_voltage.loc[len(df_voltage.index)] = [s, block, t, cond, tap, ms, voltage]
        
    # Print data.  
    # print(df)

#%% Guardar df
df_posta= df.copy(deep=True)
df_posta[['Effector', 'Period']] = df_posta['Cond'].str.extract('(\w+)(\w+)', expand=True)
df_posta['Period']= df_posta['Period'].replace('1','444')
df_posta['Period']= df_posta['Period'].replace('2','666')

df_posta.to_csv('../data/Df_2025.csv')
df_voltage.to_csv('../data/Df_Voltage_2025.csv')
# %%
