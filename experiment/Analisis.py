# -*- coding: utf-8 -*-
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
import statistics as stat
import more_itertools as mt
import seaborn as sns
import os
import pandas as pd 
from scipy.signal import find_peaks

from IPython import get_ipython
get_ipython().run_line_magic("matplotlib","qt5")




#%%
#path = '../data/'

import glob
import json
# Funcion para abrir los datos de un trial especifico de algun sujeto
def datos(numero_de_sujeto, block, trial):
    # Primero que recopile los datos
    register_subjs_path = 'registered_subjects.dat'
    with open(register_subjs_path,"r") as fp:
        subj_number_fullstring = fp.readlines()[numero_de_sujeto].replace("\n", "") # devuelve el S01 si #sujeto = 1

    for filename in os.listdir(): # en el () va el path
        if filename.startswith('S' + subj_number_fullstring) and filename.endswith("block" + str(block) + "-" + "trial" + str(trial) + ".dat"):
            data_fname = filename
    print(data_fname)
    file_to_load = glob.glob(data_fname)[0]
    f_to_load = open(file_to_load,"r")
    content = f_to_load.read()
    f_to_load.close()
    content = json.loads(content)
    return content

#%%

# data1 = datos(2,0,5)['Asynchrony']
# data2 = datos(2,0,5)['Stim_assigned_to_asyn']
# data3 = datos(2,0,5)['Resp_time']
# data4 = datos(2,0,5)['voltage_value']
# data5 = datos(2,0,5)['Data']

data = datos(0,0,5)
voltajes = data["voltage_value"]
x = np.linspace(0,len(voltajes)-1,len(voltajes))

plt.figure(figsize = (10,6))
plt.plot(x,voltajes)
plt.show()

#%%


register_subjs_path = 'registered_subjects.dat'
with open(register_subjs_path,"r") as fp:
    total_subjects = 1 + int( fp.readlines()[-1].replace("\n", "").replace("S", ""))

datos_totales = []
for s in range(total_subjects): # N° sujetos
    datos_subject_s = []
    for b in range(4): # N° bloques  
        datos_block_b = []
        for t in range(9): # N° trials
                datos_sbt = datos(s,b,t) # numero_de_sujeto, block, trial
                #datos_trial_t = {'subject':s,'block':b,'trial':t,'datos':datos_sbt}
                datos_block_b.append(datos_sbt)
        datos_subject_s.append(datos_block_b)        
    datos_totales.append(datos_subject_s)


#%% tipos de datos en datos()

subject = 0
block = 3
trial = 5
data_type = 'voltage_value'

voltajes = datos_totales[subject][block][trial][data_type]

data = datos(1,1,5)
voltajes = data["voltage_value"]
x = np.linspace(0,len(voltajes)-1,len(voltajes))

plt.figure(figsize = (10,6))
plt.plot(x,voltajes)
plt.show()

data1 = datos(2,0,5)['Asynchrony']
data2 = datos(2,0,5)['Stim_assigned_to_asyn']
data3 = datos(2,0,5)['Resp_time']
data4 = datos(2,0,5)['voltage_value']
data5 = datos(2,0,5)['Data']

#%% bip_separator

def bip_separator(voltajes):
    bips = []
    start_i = 10000
    for v in range(len(voltajes)-1):
       
        if voltajes[v] == 0 and voltajes[v+1] > 0:
            start_i = v
            print(start_i)
        if v > start_i and voltajes[v] > 0 and voltajes[v+1] == 0:
            end_i = v
            bip = np.asarray(voltajes[start_i+1:end_i+3])
            print("start_i =" +str(start_i))
            print("end_i =" +str(end_i))
            if len(bip)>10:    
                bips.append(bip)
    peaks = []
    for b in bips:
        pk, _ = find_peaks(b, distance=5,height=10)
        peaks.append(pk)
    return bips, np.asarray(peaks)

#%%% Para graficar los bips
data = datos(0,2,7)
bips, peaks = bip_separator(data["voltage_value"])
bip = 7
# peaks,_ = find_peaks(bips[bip], distance=5,height=10)

plt.close("all")
plt.figure(figsize = (10,6))
plt.plot(bips[bip], ".-")
for p in peaks[bip]:
    plt.plot(p,bips[bip][int(p)],"o",markersize = 10, c = "darkred", alpha = 0.5)
plt.show()


#%% Cond_trial

# path = 'presentation_orders_prueba.csv'

def cond_of_trial(subject,block,trial,trials_per_block):
    path_po = 'presentation_orders_prueba.csv'
    with open(path, 'r') as file:
        f = file.readlines()
    cond =  list(f[1+ trial+block*trials_per_block].split(","))[subject + 2]
    return cond

    
#%% Data Frame

register_subjs_path = 'registered_subjects.dat'
subjects = []
with open(register_subjs_path,"r") as fp:
    for i in fp.readlines():
        subjects.append(int(i.replace("\n", "").replace("S", "")))
        

df = {'Subjs':[], 'Block':[], 'Trial':[], 'Cond':[],'Asign_Stim':[],'Asign_Resp':[],'Asyns_p1':[],'Asyns_p2':[]}
trials_per_block = 13
# La idea es que cada fila es un bip
for s in range(len(subjects)):
    for block in range(4): # number_of_blocks
        for t in range(13): # number of trials_per_block
            datos_trial = datos(s,block,t)
            resp_time   = datos_trial['Resp_time']
            stim_time   = datos_trial['Stim_time']
            asyns       = datos_trial["Asynchronys"]
            voltajes    = datos_trial["voltage_value"]
            asign_stim  = datos_trial['Stim_assigned_to_asyn']
            
            taps, peaks = bip_separator(voltajes)
            cond = cond_of_trial(s, block, t, trials_per_block)
            for tap in range(len(taps)):                
                if len(peaks)>1:              
                    indice = # indice del primer elemento mayo o igual a 5
                    asign_stim_tap = asign_stim[tap+indice]
                    p1_tap = peaks[tap][0] # 
                    p2_tap = peaks[tap][1] # esta es la asincronia de p2 con la respuesta
                    asyns_p2 = resp_time[tap+indice] + p2_tap[tap] - stim_time[asing_stim_tap]
                
                
                df.loc[len(df.index)] = [s, block, t, cond,b, ] 
# Print data.  
print(dframe)





















