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
path = '../data/'

import glob
import json
# Funcion para abrir los datos de un trial especifico de algun sujeto
def datos(numero_de_sujeto, block, trial):
    # Primero que recopile los datos
    register_subjs_path = path + 'registered_subjects.dat'
    with open(register_subjs_path,"r") as fp:
        subj_number_fullstring = fp.readlines()[numero_de_sujeto].replace("\n", "") # devuelve el S01 si #sujeto = 1

    for filename in os.listdir(path):
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

data1 = datos(2,0,5)['Asynchrony']
data2 = datos(2,0,5)['Stim_assigned_to_asyn']
data3 = datos(2,0,5)['Resp_time']
data4 = datos(2,0,5)['voltage_value']
data5 = datos(2,0,5)['Data']

data = datos(2,0,5)
voltajes = data["voltage_value"]
x = np.linspace(0,len(voltajes)-1,len(voltajes))

plt.figure(figsize = (10,6))
plt.plot(x,voltajes)
plt.show()

#%%


register_subjs_path = path + 'registered_subjects.dat'
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


#%%

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

#%% 



data1 = datos(2,0,5)['Asynchrony']
data2 = datos(2,0,5)['Stim_assigned_to_asyn']
data3 = datos(2,0,5)['Resp_time']
data4 = datos(2,0,5)['voltage_value']
data5 = datos(2,0,5)['Data']

#%%%


data = datos(2,0,5)
voltajes = data["voltage_value"]
x = np.linspace(0,len(voltajes)-1,len(voltajes))

peaks,_ = find_peaks(voltajes, distance=15)
def filtro_peaks(voltajes,peaks):
    filter_peaks = []
    for p in peaks:
        if voltajes[p] > 10 and voltajes[p] < 600:
            filter_peaks.append(p)
    return filter_peaks
    
plt.close("all")
plt.figure(figsize = (10,6))
plt.plot(voltajes)
f_peaks = filtro_peaks(voltajes,peaks)
for p in f_peaks:
    plt.plot(p,voltajes[int(p)],"o",markersize = 5, c = "darkred", alpha = 0.5)
plt.show()






#%% Cond_trial

path = 'presentation_orders_prueba.csv'

def cond_of_trial(subject,block,trial,trials_per_block):
    with open(path, 'r') as file:
        f = file.readlines()
    cond =  list(f[1+ trial+block*trials_per_block].split(","))[subject + 2]
    return cond

    
#%% Data Frame
register_subjs_path = path + 'registered_subjects.dat'
subjects = []
with open(register_subjs_path,"r") as fp:
    for i in fp.readlines():
        subjects.append(int(i.replace("\n", "").replace("S", "")))
        

df = {'Subjs':[], 'Block':[], 'Trial':[], 'Cond':[],'Asign_Stim':[],'Asign_Resp':[],'Asyns_p1':[],,'Asyns_p2':[]}
trials_per_block = 13
# La idea es que cada fila es un bip
for s in range(len(subjects)):
    for b in range(4): # number_of_blocks
        for t in range(13): # number of trials_per_block
            
            for a in 
                cond = cond_of_trial(s, b, t, trials_per_block)
                df.loc[len(df.index)] = [s, b, t, cond,] 
# Print data.  
print(dframe)





















