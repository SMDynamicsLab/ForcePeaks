# -*- coding: utf-8 -*-
"""
Created on Jun 2022

@author: 3.rodlaje, 2.galilei83, 1.paulacaral
"""


import serial, time
import numpy as np
import random
import os
import pandas as pd
import json
import string
import tappinduino as tp


#%% parameters and files


n_stims = 6 # number of bips in a sequence

effector_list_dict = {'D':'dedo', 'M':'mano'}
period_list_dict = {'1':444, '2':666} # interstimulus intervals (ms)

n_trials_perblock = 9 # (multiple of number of pairs of periods) + 1
n_blocks = 4 # either DMMD or MDDM

noise_amp = 120

path = '../data/'
recorded_subject_pseudos_fname = path + 'pseudonyms.dat'
recorded_subject_numbers_fname = path + 'registered_subjects.dat'
presentation_orders_fname = path + 'presentation_orders.csv'

# get effector and period from condition string, e.g. 'D1'
def get_effectors(condition):
	effectors = [x[0] for x in condition]
	return effectors
def get_periods(condition):
	periods = [x[1] for x in condition]
	return periods
# make dictionary out of list of variable names
def vars2dict(varnames): # e.g. varnames=['var1','var2']
	varvalues = globals()
	vardict = {var: varvalues[var] for var in varnames}
	return vardict



#%% experiment



# get condition presentation orderstom
presentation_orders_df = pd.read_csv(presentation_orders_fname,index_col='Trial')

if os.path.exists(recorded_subject_numbers_fname):
	# get last recorded subject
	with open(recorded_subject_numbers_fname,"r") as fp:
		# read last nonempty line
		last_subj_number_full = fp.readlines()[-1]
		last_subj_number = int(last_subj_number_full[-3:-1])
		subj_number = last_subj_number + 1
else:
	# first subject ever
	subj_number = 1

subj_number_fullstring = 'S' + '{0:0>2}'.format(subj_number)
# get conditions presentation order
conditions_order = presentation_orders_df[['Block',subj_number_fullstring]]

# get subject name, save name and number pseudonym
subj_name = input("Ingrese su nombre y apellido:")
# append to files, create if nonexistent
with open(recorded_subject_pseudos_fname, "a+") as fp:
	fp.write(subj_name + '\t' + subj_number_fullstring + '\n') # keep the \n at the end here
with open(recorded_subject_numbers_fname, "a+") as fp:
	fp.write(subj_number_fullstring + '\n') # keep the \n at the end here

# save experiment parameters
# experiment_parameters_dict = dict_of(period_list_dict,n_stims,n_trials_perblock,n_blocks,conditions_order,path)
experiment_parameters_dict = vars2dict(['period_list_dict','n_stims','n_trials_perblock','n_blocks','conditions_order','path'])
# with open(path + subj_number_fullstring + '_experiment_parameters.dat', 'w') as fp:
# 	json.dump(experiment_parameters_dict, fp)


# open arduino serial port
arduino = serial.Serial('COM3', 9600) # windows
# arduino = serial.Serial('/dev/ttyACM0', 9600) # linux

# block loop
for block in range(0,n_blocks):

	# get timestamp for block file names
    timestr = time.strftime("%Y_%m_%d-%H.%M.%S")
    block_fname = path + 'S' + subj_number_fullstring + "-" + timestr + "-" + "block" + str(block) + "-alltrials.csv"

    block_conditions = conditions_order.query('Block==@block')[subj_number_fullstring]
    block_effectors = get_effectors(block_conditions)
    block_periods = get_periods(block_conditions)
# 	block_effectors = get_effectors(block_conditions['cond'])
# 	block_periods = get_periods(block_conditions['cond'])
    messages = [] # history of messages to arduino
    effector = block_effectors[0] # assumes same effector for the whole block
    print("Preparar efector: " + effector_list_dict[effector].upper())
    input("Cuando el efector esté listo, presione Enter para comenzar el bloque (%d/%d): " % (block+1,n_blocks))
    # trial loop
    for trial in range(0,n_trials_perblock):
        
        input("Presione Enter para comenzar el trial (%d/%d): " %(trial+1,n_trials_perblock))
        period=block_periods[trial]
 		#ISI =block_periods[trial]
        ISI =period_list_dict[period]
		# raw data filename for arduino data
        rawdata_fname = path + 'S' + subj_number_fullstring + "-" + timestr + "-" + "block" + str(block) + "-" + "trial" + str(trial) + "-raw.dat"
		# parsed data filename (stimulus times, response times, asynchrony, force)
        parseddata_fname = path + 'S' + subj_number_fullstring + "-" + timestr + "-" + "block" + str(block) + "-" + "trial" + str(trial) + ".dat"

		# wait random time before actually starting the trial
        wait = random.random() + 1
        time.sleep(wait)

		# start trial
        message = str.encode(";S%c;F%c;N%c;A%d;I%d;n%d;X" % ('B', 'B', 'B', noise_amp, ISI, n_stims))
        arduino.write(message)
        messages.append(message.decode())
		# (trial under arduino control)

		# read information from arduino
        data = []
        aux = arduino.readline().decode()
        while (aux[0] != 'E'):
            data.append(aux)
            aux = arduino.readline().decode()

		# save raw data
        with open(rawdata_fname, "a+") as fp:
            fp.writelines(data)

		# separates data in type, number, and time
        e_total = len(data)
        e_type = []
        e_number = []
        e_time = []
        for event in data:
            e_type.append(event.split()[0])
            e_number.append(int(event.split()[1]))
            e_time.append(int(event.split()[2]))

		# eparates number and time according to if it comes from stimulus or response
        stim_number = []
        resp_number = []
        stim_time = []
        resp_time = []
        for events in range(e_total):
            if e_type[events]=='S':
                stim_number.append(e_number[events])
                stim_time.append(e_time[events])

            if e_type[events]=='R':
                resp_number.append(e_number[events])
                resp_time.append(e_time[events])


		# asynchrony calculation
        asyn_df = tp.Compute_Asyn(stim_time,resp_time)

		# save parsed trial data
# 		trial_data_dict = dict_of(data,stim_time,resp_time,asyn_df)
        trial_data_dict = vars2dict(['data','stim_time','resp_time','asyn_df'])
        
        # Tuve que agregar la siguiente linea para que funcione (C-GPT)
        converted_data = {key: value.to_dict(orient='records') if isinstance(value, pd.DataFrame) else value for key, value in trial_data_dict.items()}
        with open(parseddata_fname, "w") as fp:
#            json.dumps(trial_data_dict, fp)  # Tira error pq dumps requiere 1 unico argumento
            json.dump(converted_data, fp) 
            

		# next trial
        trial = trial + 1

	# next block
    print("Fin del bloque!\n")
    block = block + 1

# 	block_data_dict = dict_of(block_conditions, messages)
    block_data_dict = vars2dict(['block_conditions','messages'])
    with open(block_fname, "w") as fp:
        #json.dumps(block_data_dict, fp) # Tira error pq dumps requiere 1 unico argumento
        json.dump(converted_data, fp)
        
print("Fin del experimento!")
arduino.close()


#%%
