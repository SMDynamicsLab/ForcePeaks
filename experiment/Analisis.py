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
# from IPython import get_ipython
# get_ipython().run_line_magic("matplotlib","qt5")


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

sujeto, bloque, trial = 12, 3, 5 
data1 = datos(sujeto, bloque, trial)['Asynchrony']
data2 = datos(sujeto, bloque, trial)['Stim_assigned_to_asyn']
data3 = datos(sujeto, bloque, trial)['Resp_time']
data4 = datos(sujeto, bloque, trial)['voltage_value']
data5 = datos(sujeto, bloque, trial)['Data']

data = datos(sujeto, bloque, trial)
voltajes = data["voltage_value"]
x = np.linspace(0,len(voltajes)-1,len(voltajes))
x_1 = np.linspace(0,len(data1)-1,len(data1))
x_1 = [8,106,204,302,400,]
x_1 = np.linspace(8,1880,20)


plt.close("all")
fig, axs = plt.subplots(2,figsize = (20,6),sharex=True)
# fig.suptitle('Vertically stacked subplots')
colors=plt.cm.viridis(np.linspace(0,1,5))
axs[1].plot(x,voltajes,color=colors[0])
axs[0].plot(x_1,data1[4:],color=colors[0])
axs[0].plot(x_1,data1[4:],'o',color=colors[2],markersize=10)
axs[0].set_ylabel("Asincronías [ms]",size="20")
axs[1].set_ylabel("Voltajes [u.a]",size="20")
axs[1].set_xlabel("Tiempo [ms]",size="20")
axs[0].grid()
axs[1].grid()
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

#%% CARGAR DATAFRAME

df = pd.read_csv("Df.csv")
df_voltage = pd.read_csv("Df_Voltage.csv")

df_voltage_2 = df_voltage.copy(deep=True)
df_voltage_2['Subjs'] = df_voltage_2.Subjs.astype('string')
df_voltage_2['Block'] = df_voltage_2.Block.astype('string')
df_voltage_2['Trial'] = df_voltage_2.Trial.astype('string')
df_voltage_2['Tap'] = df_voltage_2.Tap.astype('string')
df_voltage_2 = (df_voltage_2
				   # create label for plot grouping
				   .assign(label = lambda df: df.Subjs + df.Block + df.Trial + df.Tap)
				   )

df['Subjs'] = df.Subjs.astype('string')
df['Cond'] = df.Cond.astype('string')
df['Trial'] = df.Trial.astype('string')
df['Tap'] = df.Tap.astype('string')


#%%%


df_voltage_3 = (df_voltage_2
                .groupby(['Subjs','Cond','Trial','Time'], as_index=False)
                .agg(mean_voltage = ('Voltages','mean'))
                .assign(label = lambda df: df.Subjs + df.Cond + df.Trial))

df_voltage_4 = (df_voltage_3
                .groupby(['Subjs','Cond','Time'], as_index=False)
                .agg(mean_voltage = ('mean_voltage','mean'),
                     voltage_std = ('mean_voltage','std'))
                .assign(label = lambda df: df.Subjs + df.Cond))

df_voltage_5 = (df_voltage_4
                .groupby(['Cond','Time'], as_index=False)
                .agg(mean_voltage = ('mean_voltage','mean'))
                .assign(label = lambda df: df.Cond))

df_voltage_6 = (df_voltage_2                                   #ESTE ES LA "BOLSA" PARA C/SUJETO
                .groupby(['Subjs','Cond','Time'], as_index=False)
                .agg(mean_voltage = ('Voltages','mean'))
                .assign(label = lambda df: df.Subjs + df.Cond))


df_voltage_7 = (df_voltage_6                                   #ESTE ES LA "BOLSA" 
                .groupby(['Cond','Time'], as_index=False)
                .agg(mean_voltage = ('mean_voltage','mean'))
                .assign(label = lambda df: df.Cond))

df_voltage_8 = (df_voltage_6                                   #ESTE ES LA "BOLSA" 
                .groupby(['Cond','Time'], as_index=False)
                .apply(lambda df: pd.Series({
		'mean_voltage': df.mean_voltage.mean(),
		'sd_voltage': df.mean_voltage.std(),
		'n_voltage': df.mean_voltage.count(),
		'ci_voltage': 1.96*df.mean_voltage.sem()
		}))
                .assign(label = lambda df: df.Cond))




#%% Para graficar los taps de un trial
sujeto, bloque, trial = 1, 1, 0
tap_length = 74
data = datos(sujeto, bloque, trial)
taps, peaks, p_min = tap_separator(data["voltage_value"],tap_length)


plt.close("all")
plt.figure(figsize = (10,6))
colors = plt.cm.tab20(np.linspace(0,1,len(taps)))
plt.plot(df_voltage_3['Time'][:tap_length],df_voltage_3['mean_voltage'][:tap_length])

for tap in range(len(taps)):   
    etiqueta = "S" + str(sujeto) + "B" + str(bloque) + "T" + str(trial) + "t" + str(tap)
    if not math.isnan(peaks[tap][0]) and not math.isnan(peaks[tap][1]):
        plt.plot(taps[tap], ".-", color=colors[tap], alpha = 0.7, label = etiqueta)
        plt.plot(peaks[tap],taps[tap][peaks[tap]],"o",markersize = 10, color=colors[tap])
        plt.plot(p_min,taps[tap][int(p_min)],"o",markersize = 10, color=colors[tap])
    else:
        plt.plot(taps[tap], "--", color="black", alpha = 0.2,)
        
    # plt.plot(p_min,taps[tap][int(p_min)],"o",markersize = 10, color=colors[tap])

plt.tight_layout()
plt.legend()
plt.show()
#%% Para graficar los taps de un trial (Informe)
sujeto, bloque, trial = 1, 1, 0
tap_length = 74
data = datos(sujeto, bloque, trial)
taps, peaks, p_min = tap_separator(data["voltage_value"],tap_length)


plt.close("all")
plt.figure(figsize = (10,6))
colors = plt.cm.viridis(np.linspace(0,1,5))
plt.plot(df_voltage_3['Time'][:tap_length],df_voltage_3['mean_voltage'][:tap_length],color=colors[0],lw=2,
         label = "Tap promedio")

plt.plot(taps[0], "--", color=colors[1], alpha = 0.3,lw=2,label="Taps")
for tap in range(len(taps)):   
    etiqueta = "S" + str(sujeto) + "B" + str(bloque) + "T" + str(trial) + "t" + str(tap)
    
    if not math.isnan(peaks[tap][0]) and not math.isnan(peaks[tap][1]):
        plt.plot(taps[tap], "--", color=colors[1], alpha = 0.3,lw=2)
        # plt.plot(peaks[tap],taps[tap][peaks[tap]],"o",markersize = 10, color=colors[tap])
        # plt.plot(p_min,taps[tap][int(p_min)],"o",markersize = 10, color=colors[tap])
    # else:
        # plt.plot(taps[tap], "--", color="black", alpha = 0.2,)
        
    # plt.plot(p_min,taps[tap][int(p_min)],"o",markersize = 10, color=colors[tap])
plt.xlabel("Tiempo [ms]", size = 20)
plt.ylabel("Voltajes [u.a.]",size = 20)
plt.grid()
plt.tight_layout()
plt.legend(fontsize = 18)
plt.show()
#%% Para seleccionar trials y taps fallidos
 
tap_length = 50
trials_per_block = 9 
blocks_per_subj = 4
ppf = 6 # el primer pico de fuerza que medimos (tiramos los primeros 5)
heigth_interval = 10 # diferencia minima de altura entre el primer pico y el primer minimo
register_subjs_path = 'registered_subjects.dat'
subjects = []
with open(register_subjs_path,"r") as fp:
    for i in fp.readlines():
        subjects.append(int(i.replace("\n", "").replace("S", "")))


subjs = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21]
for s in subjs:
    for block in range(blocks_per_subj): # number_of_blocks
        for t in range(trials_per_block): # number of trials_per_block
            datos_trial = datos(s,block,t)
            resp_time   = datos_trial['Resp_time']
            stim_time   = datos_trial['Stim_time']
            asyns       = datos_trial["Asynchrony"]
            voltajes    = datos_trial["voltage_value"]
            assign_stim = datos_trial['Stim_assigned_to_asyn']
            
            input("Enter para ver el trial: S" + str(s) + "B" + str(block) + "T" + str(t) + ": ")
            
            taps, peaks, p_min = tap_separator(np.asarray(voltajes),tap_length)
            taps=np.asarray(taps)
            peaks=np.asarray(peaks)
            # print(np.shape(peaks))
            # print(np.shape(taps))
            # cond = cond_of_trial(s, block, t, trials_per_block)
            if len(taps) != 0:
                indice =  int(np.argwhere(np.array(assign_stim)>=ppf-1)[0][0]) # indice del primer elemento mayo o igual a 5
                asyns_over6 = asyns[indice:]
                resp_time_taps = resp_time[len(resp_time)-len(taps):]
                asyns_taps = asyns[len(asyns)-len(taps):]
                
                
        
                plt.close("all")
                plt.figure(figsize = (10,6))
                plt.title("Sujeto " + str(s) + ", Bloque " + str(block) + ", Trial " + str(t) )
                colors = plt.cm.tab20(np.linspace(0,1,len(taps)))
            
                for tap in range(len(asyns_taps)): 
               
                    if not math.isnan(asyns_taps[tap]):              
                        if not math.isnan(peaks[tap][1]):
                            # if taps[tap][int(peaks[tap][1])] > taps[tap][int(peaks[tap][p_min])] and (taps[tap][int(peaks[tap][0])] - taps[tap][int(peaks[tap][p_min])]) > heigth_interval:
                            if peaks[tap][0] < p_min and peaks[tap][1] > p_min and (taps[tap][int(peaks[tap][0])] - taps[tap][int(p_min)]) > heigth_interval:       
                                plt.plot(taps[tap], ".-", color=colors[tap], alpha = 0.7, label = str(tap),lw = 2)
                                plt.plot(peaks[tap][0],taps[tap][int(peaks[tap][0])],"o",markersize = 10, color=colors[tap])
                                plt.plot(peaks[tap][1],taps[tap][int(peaks[tap][1])],"o",markersize = 10, color=colors[tap])
                                plt.plot(p_min,taps[tap][int(p_min)],"o",markersize = 10, color=colors[tap])
                    else:
                        plt.plot(taps[tap], "--", color="black", alpha = 0.2)
                
                plt.plot((0,0), alpha = 0, label = " ") # 
                plt.tight_layout()
                plt.legend()
                plt.show()
            else:
                print("No data in trial")
                        


#%% Para seleccionar trials y taps fallidos - beta
 
tap_length = 50
trials_per_block = 9 
blocks_per_subj = 4

register_subjs_path = 'registered_subjects.dat'
subjects = []
with open(register_subjs_path,"r") as fp:
    for i in fp.readlines():
        subjects.append(int(i.replace("\n", "").replace("S", "")))


for s in range(len(subjects)):
    for block in range(blocks_per_subj): # number_of_blocks
        for t in range(trials_per_block): # number of trials_per_block
            datos_trial = datos(s,block,t)
            voltajes    = datos_trial["voltage_value"]
            taps, peaks = tap_separator(voltajes,tap_length)
            
            input("Enter para ver el trial: S" + str(s) + "B" + str(block) + "T" + str(t) + ": ")
            
            plt.close("all")
            plt.figure(figsize = (10,6))
            colors = plt.cm.tab20(np.linspace(0,1,len(taps)))
            all_peaks = []
            for tap in range(len(taps)):   
                peaks,_ = find_peaks(taps[tap], distance = 10,height=10, width = 3)
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
    path_po = 'presentation_orders.csv'
    with open(path_po, 'r') as file:
        f = file.readlines()
    cond =  list(f[1+ trial+block*trials_per_block].split(","))[subject + 2]
    return cond

    
#%% Data Frame de Tiempos y Voltajes
blocks_per_subj = 4
register_subjs_path = 'registered_subjects.dat'
subjects = [0]
with open(register_subjs_path,"r") as fp:
    for i in fp.readlines():
        subjects.append(int(i.replace("\n", "").replace("S", "")))
        
ppf = 6 # el primer pico de fuerza que medimos (tiramos los primeros 5)
trials_per_block = 9

df = pd.DataFrame({'Subjs':[], 'Block':[], 'Trial':[], 'Cond':[], 'Tap':[], 'P1':[], 'P2':[], 'Asyns_c':[],'Asyns_p1':[],'Asyns_p2':[],'Peak_interval':[]}) # 'Asign_Resp':[]
df_voltage = pd.DataFrame({'Subjs':[], 'Block':[], 'Trial':[], 'Cond':[], 'Tap':[], 'Time':[], 'Voltages':[]})
subjs = [1,2,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21]#sujetos 0 y 3 descartados por falta de contenido

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
#%%% #ESTE NO USAR PORQUE NO TIENE LOS 444 Y 666

df.to_csv('Df_casi.csv')
df_voltage.to_csv('Df_Voltage.csv')


#%% Guardar df
df_posta= df.copy(deep=True)
df_posta[['Effector', 'Period']] = df_posta['Cond'].str.extract('(\w+)(\w+)', expand=True)
df_posta['Period']= df_posta['Period'].replace('1','444')
df_posta['Period']= df_posta['Period'].replace('2','666')

df_posta.to_csv('Df.csv')
df_voltage.to_csv('Df_Voltage.csv')

#%% NO CORRER ES POR SI NECESITAMOS AGREGAR SUJETOS AL DF



# blocks_per_subj = 4
# register_subjs_path = 'registered_subjects.dat'
# with open(register_subjs_path,"r") as fp:
#     for i in fp.readlines():
#         subjects.append(int(i.replace("\n", "").replace("S", "")))
        
ppf = 6 # el primer pico de fuerza que medimos (tiramos los primeros 5)
trials_per_block = 9
subjs_2=[22,23,24,25,26]
df_2 = pd.read_csv("Df.csv")
df_voltage_2 = pd.read_csv("Df_Voltage.csv")
tap_length = 50
df_2 = df_2.drop('Unnamed: 0',axis=1)

df_voltage_2 = df_voltage_2.drop('Unnamed: 0',axis=1)





# La idea es que cada fila es un bip
for s in subjs_2:
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
                                    df_2.loc[len(df_2.index)] = [s, block, t, cond, tap, p1_tap, p2_tap, c_asyn, asyns_p1, asyns_p2, peak_interval,cond[0],cond[1]] 
                                    for ms in range(len(taps[tap])):                 
                                        voltage = taps[tap][ms]
                                        
                                        df_voltage_2.loc[len(df_voltage_2.index)] = [s, block, t, cond, tap, ms, voltage]
        
# Print data. 
# print(df)

#%%%

df_posta= df_2.copy(deep=True)
# df_posta[['Effector', 'Period']] = df_posta['Cond'].str.extract('(\w+)(\w+)', expand=True)
df_posta['Period']= df_posta['Period'].replace('1','444')
df_posta['Period']= df_posta['Period'].replace('2','666')

df_posta.to_csv('Df.csv')
df_voltage_2.to_csv('Df_Voltage.csv')







