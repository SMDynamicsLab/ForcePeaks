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
import csv
import random

from IPython import get_ipython
get_ipython().run_line_magic("matplotlib","qt5")

#%% el bloque esta Balanceado?
def balance(block,DoM):
    one_transitions = 0
    two_transitions = 0
    one_two_transitions = 0
    two_one_transitions = 0
    for i in range(len(block)-1):
        if block[i+1] == block[i]:
            if block[i+1] == DoM + '1':
                one_transitions += 1
            else:
                two_transitions += 1
        else:
            if block[i+1] == DoM + '1':
                two_one_transitions += 1
            else:
                one_two_transitions += 1
    
    if one_transitions == two_transitions and one_transitions == one_two_transitions and one_transitions == two_one_transitions and len(block) >= 2:
        reply = 'true'
    else:
        reply = 'false'
    return reply

#%% Generador del bloque 
                
def block_generator(trials_per_block,start,DoM): # ej. trials_per_block = 17, start = '1', DoM = 'D', 'M'
    block = [DoM + start]
    array = []
    for i in range(int( (trials_per_block-1)/2 ) ):
        array.append(DoM + '1')
        array.append(DoM + '2')
    # j = 1
    while balance(block, DoM) == 'false':  
        # j += 1
        block = [DoM + start]
        random.shuffle(array)
        block = np.concatenate([block,array])
    # print(j) 
    return block

#%% presentation_orders_generator


block_types =[['D','D','M','M'],['D','M','M','D'],
         ['M','M','D','D'],['M','D','D','M']]

def presentations_order_generator(path,tot_subjects,blocks_types,trials_per_block):
    blocks_type_num = len(blocks_types) 
    blocks = []   # blocks[subject][block][trial]
    for s in range(tot_subjects):
        bloques_de_un_sujeto = []
        for b in range(len(block_types[0])): 
            # trials_de_un_bloque = []
            # for t in range(trials_per_block):
            start = str((s+b)%2 + 1)
            DoM = block_types[s%blocks_type_num][b] # cada sujeto usa uno de los 4 block_types
            # trials_de_un_bloque.append(block_generator(trials_per_block,start,DoM))
            # bloques_de_un_sujeto.append(trials_de_un_bloque)
            bloques_de_un_sujeto.append(block_generator(trials_per_block,start,DoM))
        blocks.append(bloques_de_un_sujeto)


    subjects = ['Trial', 'Block']
    for i in range(tot_subjects):
        subjects.append("S{:02d}".format(i))

    with open(path, 'w', newline='') as file:
        writer = csv.writer(file)
         
        writer.writerow(subjects)
        
        for b in range(len(block_types[0])): 
            for t in range(trials_per_block):
                fila_bt = [t+b*trials_per_block,b] # t+b*trials_per_cond pq no se reinicia en cada bloque
                for s in range(tot_subjects): 
                    fila_bt.append(blocks[s][b][t])
                writer.writerow(fila_bt)
    
    blocks = []
    return("Archivo Creado")

#%% A crearlo

path = 'presentation_orders_prueba.csv'

tot_subject = 48

block_types =[['D','M','M','D'],['M','D','D','M']]

trial_per_block = 13 # 9, 13, 17 = m(n**2)+1  con n = 2 (periodos)


presentations_order_generator(path, tot_subject, block_types, trial_per_block)






























