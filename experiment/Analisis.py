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
from IPython import get_ipython
get_ipython().run_line_magic("matplotlib","qt5")

#%%

path = '../data/'
#dat_file =  path + 'SS00-2023_09_12-15.50.50-block0-trial0.dat'

# Funcion para abrir los datos de un trial especifico de algun sujeto
def datos(numero_de_sujeto, block, trial):
    # Primero que recopile los datos
    register_subjs_path = path + 'registered_subjects.dat'
    with open(register_subjs_path,"r") as fp:
        subj_number_fullstring = fp.readlines()[numero_de_sujeto].replace("\n", "") # devuelve el S01 si #sujeto = 1

    for filename in os.listdir(path):
        if filename.startswith('S' + subj_number_fullstring) and filename.endswith("block" + str(block) + "-" + "trial" + str(trial) + "-raw.dat"):
            rawdata_fname = filename
    
    with open(path + rawdata_fname,"r") as fp:
        data = fp.readlines()

    # Ahora que separe los datos
    e_total = len(data)
    e_type = []
    e_number = []
    e_time = []
    for event in data:
        e_type.append(event.split()[0])
        e_number.append(int(event.split()[1]))
        e_time.append(int(event.split()[2]))

    # separates number and time according to if it comes from stimulus or response
    stim_number = []
    resp_number = []
    stim_time = []
    resp_time = []
    voltage_value = []
    for events in range(e_total):
        if e_type[events]=='S':
            stim_number.append(e_number[events])
            stim_time.append(e_time[events])

        if e_type[events]=='R':
            resp_number.append(e_number[events])
            resp_time.append(e_time[events])
                    
        if e_type[events]=='V':
            # resp_number.append(e_number[events])
            voltage_value.append(e_time[events])
    
    return({'stim_number':stim_number, 'resp_number':resp_number,
            'stim_time':stim_time, 'resp_time':resp_time,
            'voltage_value':voltage_value })

# Para poder vincular las respuestas con sus estimulos 
def find_nearest(array, value):
    array = np.asarray(array)
    idx = (np.abs(array - value)).argmin()
    return array[idx]

def asincronia(data):
    asincronias = []
    respuestas = data["resp_time"]
    estimulos = data["stim_time"]
    for resp in respuestas:
        nearest_stim = find_nearest(estimulos, resp)
        asincronias.append(resp - nearest_stim)
    return asincronias

#%%          
data = datos(1,1,5)
voltajes = data["voltage_value"]
x = np.linspace(0,len(voltajes)-1,len(voltajes))

plt.figure(figsize = (10,6))
plt.plot(x,voltajes)
plt.show()

#%%
data = datos(1,1,5)
print(asincronia(data))

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

subject = 1
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



























