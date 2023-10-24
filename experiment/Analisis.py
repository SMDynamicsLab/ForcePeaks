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
get_ipython().run_line_magic("matplotlib","qt5")


#%% datos(sujeto,block,trial) = data de ese trial
# path = '../data/'

# Funcion para abrir los datos de un trial especifico de algun sujeto
def datos(numero_de_sujeto, block, trial):
    # Primero que recopile los datos
    register_subjs_path = 'registered_subjects.dat'
    with open(register_subjs_path,"r") as fp:
        subj_number_fullstring = fp.readlines()[numero_de_sujeto].replace("\n", "") # devuelve el S01 si #sujeto = 1
    
    for filename in os.listdir(): # en el () va el path
        if filename.startswith('S' + subj_number_fullstring) and filename.endswith("block" + str(block) + "-" + "trial" + str(trial) + ".dat"):
            data_fname = filename
            
    # print(data_fname)
    file_to_load = glob.glob(data_fname)[0]
    f_to_load = open(file_to_load,"r")
    content = f_to_load.read()
    f_to_load.close()
    content = json.loads(content)
    return content

#%%% Ej. grafico de un trial

sujeto, bloque, trial = 8, 0, 7
data1 = datos(sujeto, bloque, trial)['Asynchrony']
data2 = datos(sujeto, bloque, trial)['Stim_assigned_to_asyn']
data3 = datos(sujeto, bloque, trial)['Resp_time']
data4 = datos(sujeto, bloque, trial)['voltage_value']
data5 = datos(sujeto, bloque, trial)['Data']

data = datos(sujeto, bloque, trial)
voltajes = data["voltage_value"]
x = np.linspace(0,len(voltajes)-1,len(voltajes))

plt.close("all")

plt.figure(figsize = (20,6))
plt.title("Trial = " +str(trial))
plt.plot(x,voltajes)
plt.tight_layout()
plt.show()

#%% tap_separator(voltajes) = taps, peaks

def tap_separator(voltajes,tap_length):
    taps = []
    start_i = 10000
    for v in range(len(voltajes)-10):
       
        if voltajes[v] == 0 and voltajes[v+1] > 0:
            start_i = v
            # print(start_i)
        if v > start_i and voltajes[v] > 0 and voltajes[v+1] == 0 and voltajes[v+10] == 0 and start_i<(len(voltajes)-45):
            end_i = v
            bip = np.asarray(voltajes[start_i+1:end_i+3])
            # print("start_i =" +str(start_i))
            # print("end_i =" +str(end_i))
            if len(bip)>20:    
                bip_posta =  np.asarray(voltajes[start_i+1:start_i+tap_length+1])
                taps.append(bip_posta)
                
    peaks = []
    for b in taps:
        pk, _ = find_peaks(b, distance=5,height=10)
        if len(pk)==1:
            pk = np.concatenate((pk,[np.nan]))
        if len(pk)==0:
            pk = [np.nan,np.nan]
        peaks.append(pk[:2])
        
    return taps, peaks

#%%% Para graficar los taps de un trial
sujeto, bloque, trial = 4, 1, 7
tap_length = 50
data = datos(sujeto, bloque, trial)
taps, peaks = tap_separator(data["voltage_value"],tap_length)



plt.close("all")
plt.figure(figsize = (10,6))
colors = plt.cm.tab20(np.linspace(0,1,len(taps)))
all_peaks = []
for tap in range(len(taps)):   
    peaks,_ = find_peaks(taps[tap], distance = 10,height=10)
    all_peaks.append(peaks)
    etiqueta = "S" + str(sujeto) + "B" + str(bloque) + "T" + str(trial) + "t" + str(tap)
    plt.plot(taps[tap], ".-", color=colors[tap], alpha = 0.5, label = etiqueta)
    
    for p in peaks:
        if not math.isnan(p): 
            plt.plot(p,taps[tap][int(p)],"o",markersize = 10, color=colors[tap])
plt.tight_layout()
plt.legend()
plt.show()

#%% Para seleccionar trials y taps fallidos
 
tap_length = 50
trials_per_block = 9 
blocks_per_subj = 4

register_subjs_path = 'registered_subjects.dat'
subjects = []
with open(register_subjs_path,"r") as fp:
    for i in fp.readlines():
        subjects.append(int(i.replace("\n", "").replace("S", "")))


for s in range(1):
    for block in range(1): # number_of_blocks
        for t in range(2): # number of trials_per_block
            datos_trial = datos(s,block,t)
            voltajes    = datos_trial["voltage_value"]
            taps, peaks = tap_separator(voltajes,tap_length)
            
            input("Enter para ver trial")
            
            plt.close("all")
            plt.figure(figsize = (10,6))
            colors = plt.cm.tab20(np.linspace(0,1,len(taps)))
            all_peaks = []
            for tap in range(len(taps)):   
                peaks,_ = find_peaks(taps[tap], distance = 10,height=10)
                all_peaks.append(peaks)
                etiqueta = "S" + str(s) + "B" + str(block) + "T" + str(t) + "t" + str(tap)
                plt.plot(taps[tap], ".-", color=colors[tap], alpha = 0.5, label = etiqueta)
                
                for p in peaks:
                    if not math.isnan(p): 
                        plt.plot(p,taps[tap][int(p)],"o",markersize = 10, color=colors[tap])
            plt.tight_layout()
            plt.legend()
            plt.show()
            # input("Enter para ver: S")
#%% cond_of_trial()

def cond_of_trial(subject,block,trial,trials_per_block):
    path_po = 'presentation_orders2.csv'
    with open(path_po, 'r') as file:
        f = file.readlines()
    cond =  list(f[1+ trial+block*trials_per_block].split(","))[subject + 2]
    return cond

    
#%% Data Frame de Tiempos y Voltajes

register_subjs_path = 'registered_subjects.dat'
subjects = []
with open(register_subjs_path,"r") as fp:
    for i in fp.readlines():
        subjects.append(int(i.replace("\n", "").replace("S", "")))
        
ppf = 6 # el primer pico de fuerza que medimos (tiramos los primeros 5)
trials_per_block = 13

df = pd.DataFrame({'Subjs':[], 'Block':[], 'Trial':[], 'Cond':[], 'Tap':[], 'P1':[], 'P2':[], 'Asyns_c':[],'Asyns_p1':[],'Asyns_p2':[],'Peak_interval':[]}) # 'Asign_Resp':[]
df_voltage = pd.DataFrame({'Subjs':[], 'Block':[], 'Trial':[], 'Cond':[], 'Tap':[], 'Time':[], 'Voltages':[]})

# La idea es que cada fila es un bip
for s in range(len(subjects)):
    for block in tqdm(range(4)): # number_of_blocks
        for t in range(13): # number of trials_per_block
            datos_trial = datos(s,block,t)
            resp_time   = datos_trial['Resp_time']
            stim_time   = datos_trial['Stim_time']
            asyns       = datos_trial["Asynchrony"]
            voltajes    = datos_trial["voltage_value"]
            assign_stim = datos_trial['Stim_assigned_to_asyn']
            
            taps, peaks = tap_separator(np.asarray(voltajes),tap_length)
            taps=np.asarray(taps)
            peaks=np.asarray(peaks)
            # print(np.shape(peaks))
            # print(np.shape(taps))
            cond = cond_of_trial(s, block, t, trials_per_block)
            
            indice =  int(np.argwhere(np.array(assign_stim)>=ppf-1)[0][0]) # indice del primer elemento mayo o igual a 5
            asyns_over6 = asyns[indice:]
            resp_time_taps = resp_time[len(resp_time)-len(taps):]
            asyns_taps = asyns[len(asyns)-len(taps):]
            for tap in range(len(asyns_taps)):  
                # asign_stim_tap = assign_stim[tap+indice]
                if not math.isnan(asyns_taps[tap]):              
                    if not math.isnan(peaks[tap][1]):
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
#%%%

df_voltage.to_csv('Df_Voltage_prueba.csv')
df.to_csv('Df_prueba.csv')


#%%
df_posta_casi= df.copy(deep=True)
df_posta_casi[['Effector', 'Period']] = df_posta_casi['Cond'].str.extract('(\w+)(\w+)', expand=True)
df_posta_casi['Period']= df_posta_casi['Period'].replace('1','444')
df_posta_casi['Period']= df_posta_casi['Period'].replace('2','666')

df_posta_casi.to_csv('Df_prueba.csv')











