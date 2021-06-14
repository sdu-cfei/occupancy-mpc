import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

zone='20-601b-2'
wdir=os.path.join('results','calibration',zone)
ideal=pd.read_csv(os.path.join(wdir,'ideal.csv'),index_col='time')
vld_res=pd.read_csv(os.path.join(wdir,'vld_res.csv'),index_col='time')
vld_res['hour']=np.arange(0,96.5,0.5)
vld_res=vld_res.set_index('hour')
vld_res['T']=vld_res['T']-273.15

vld_ideal=ideal[(ideal.index>=432000)&(ideal.index<=777600)]
vld_ideal['hour']=np.arange(0,96.5,0.5)
vld_ideal=vld_ideal.set_index('hour')
vld_ideal['T']=vld_ideal['T']-273.15
#plotting valve position of heating/cooling supply

fig, axes = plt.subplots(2,1, figsize=(20, 8),dpi=150)
plt.subplot(2,1,1)
plt.plot(vld_res['T'], color='orange', ls='--', label='T_val')
plt.plot(vld_ideal['T'],color=[0,0.4,0.8], label='T_meas')
plt.ylabel('Temperature[\u2103]',fontsize=26)
#plt.yticks(np.arange(294,301,1))
plt.xticks(np.arange(0,97,24))
plt.legend(loc='upper right', fontsize=26,
          fancybox=True, shadow=False, ncol=3)

plt.subplot(2,1,2)
plt.plot(vld_res['CO2'],color='orange',ls='--', label='CO2_val')
plt.plot(vld_ideal['CO2'],color=[0,0.4,0.8], label='CO2_meas')
plt.legend(loc='upper right', fontsize=26,
          fancybox=True, shadow=False, ncol=3)

plt.ylabel('CO2 [ppm]',fontsize=26)
plt.xlabel('Time [hour]',fontsize=26)
plt.yticks(np.arange(400,900,100),fontsize=26)
plt.xticks(np.arange(0,97,24),fontsize=26)


plt.rc('xtick', labelsize=26)    # fontsize of the tick labels
plt.rc('ytick', labelsize=26) 

plt.savefig(os.path.join(wdir,'validation_new_2.pdf'))
