# -*- coding: utf-8 -*-
"""
Created on Tue May 14 15:23:42 2019

@author: taoy
"""

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

## CO2 discomfort
zone='20-601b-2'  
result_dir='figs_horizon_predicted_occ'     
#result_dir='figs_horizon_ideal_occ'    ## use this to plot CO2 discomfort for ideal occupancy

def filter_CO2(row):
    for index_CO2 in ['CO2_240','CO2_360','CO2_480','CO2_600']:
        if (row[index_CO2]<=row['CO2_hi'])&(row[index_CO2]>row['CO2_lo']):
            row[index_CO2]=0.
        else:
            row[index_CO2]=min(abs(row[index_CO2]-row['CO2_hi']),abs(row[index_CO2]-row['CO2_lo']))
    return row


out_dir=os.path.join('results','figs_CO2_discomfort',zone,'predicted_occ') # change to 'ideal_occ' to plot CO2 discomfort for ideal occupancy
if not os.path.exists(out_dir):
    os.makedirs(out_dir)

CO2_horizon=pd.read_csv(os.path.join('results',result_dir,zone,'CO2_horizon.csv'), index_col=0)
CO2_horizon['CO2_hi']=800.
CO2_horizon['CO2_lo']=400.
CO2_discomfort=CO2_horizon.copy()
CO2_discomfort=CO2_discomfort.apply(filter_CO2,axis=1)
CO2_discomfort=pd.DataFrame(CO2_discomfort.iloc[:,0:4].sum()).set_index(np.arange(4,12,2))
    
plt.figure(figsize=(10,4),dpi=150)    
plt.plot(CO2_discomfort,color='r',label='CO2 discomfort')
plt.legend()
plt.title('CO2 discomfort vs. horizon')
plt.xticks(np.arange(4,12,2))
plt.ylabel('CO2[ppm]')
plt.xlabel('horizon[h]')
plt.savefig(os.path.join(out_dir,'CO2_discomfort vs. horizon_zone_20-601b-2.png'))
plt.show()


## Temperature discomfort

zone='20-601b-2'
result_dir='figs_horizon_predicted_occ'     
#result_dir='figs_horizon_ideal_occ'    ## usr this to plot CO2 discomfort for ideal occupancy
def filter_T(row):
    for index_T in ['T_240','T_360','T_480','T_600']:
        if (row[index_T]<=row['T_hi'])&(row[index_T]>=row['T_lo']):
            row[index_T]=0.
        else:
            row[index_T]=min(abs(row[index_T]-row['T_hi']),abs(row[index_T]-row['T_lo']))
    return row

out_dir=os.path.join('results','figs_T_discomfort',zone,'predicted_occ') # change to 'ideal_occ' to plot CO2 discomfort for ideal occupancy
if not os.path.exists(out_dir):
    os.makedirs(out_dir)

T_horizon=pd.read_csv(os.path.join('results',result_dir,zone,'T_horizon.csv'), index_col=0)
constr=pd.read_csv(os.path.join('results','mpc_ideal_occ','240_qr_qv_ve',zone,'constr.csv'))
T_horizon['T_hi']=constr['Tair_hi']
T_horizon['T_lo']=constr['Tair_lo']
T_discomfort=T_horizon.copy()
T_discomfort=T_discomfort.apply(filter_T,axis=1)
T_discomfort=pd.DataFrame(T_discomfort.iloc[:,0:4].sum()).set_index(np.arange(4,12,2))

plt.figure(figsize=(10,4),dpi=150)    
plt.plot(T_discomfort,color='r',label='temperature discomfort')
plt.legend()
plt.title('T discomfort vs. horizon')
plt.xticks(np.arange(4,12,2))
plt.ylabel('T[℃]')
plt.xlabel('horizon[h]')
plt.savefig(os.path.join(out_dir,'T_discomfort vs. horizon_zone_20-601b-2.png'))
plt.show()













            
