import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


horizons=['240','360','480','600'] # corresponding to optimization step [4,6,8,10]h
zone = '20-601b-2'

T_horizon=pd.DataFrame()
for horizon in horizons:
        # MPC results directory
        res = os.path.join('new_results', 'mpc_predicted_occ_v2', '{}_qr_200'.format(horizon), zone)
        # Output directory
        out = os.path.join('new_results', 'figs_horizon_predicted_occ_v2', zone)
        if not os.path.exists(out):
            os.makedirs(out)   
            
        ## read indoor temperature, CO2 concentration and radiator power
        yemu=pd.read_csv(os.path.join(res,'yemu.csv'))
        T_horizon['T_{}'.format(horizon)]=yemu['T']-273.15
        

## read temperature data from RBC 
T_horizon['RBC']=pd.read_csv(os.path.join('new_results','rbc_Tc_Th_v2',zone,'ydf.csv'))['T']
T_horizon['RBC']=T_horizon['RBC']-273.15

#save results of different optimization horizon to one dataframe    
T_horizon.to_csv(os.path.join(out, 'T_horizon.csv'))

#read constraints and optimization period
constr=pd.read_csv(os.path.join(res,'constr.csv'))
tindex = pd.read_csv(os.path.join(res, 'tindex.csv'))
tindex['datetime'] = pd.to_datetime(tindex['datetime'])
tindex['time'] /= 3600.
t = tindex['time'].values

#plotting indoor temperature vs. constraints
plt.figure(figsize=(20,8),dpi=150)
plt.plot(constr['Tair_lo']-273.15, color='black', ls='--',label='Tair_bounds', lw=5.0)
plt.plot(constr['Tair_hi']-273.15, color='black', ls='--', lw=5.0)
plt.plot(T_horizon['T_240'],color=[1,0.5,0.5], label='h4',lw=5.0)
plt.plot(T_horizon['T_360'],color='y',label='h6',lw=5.0)
plt.plot(T_horizon['T_480'],color='g',label='h8',lw=5.0)
plt.plot(T_horizon['T_600'],color=[0,0.8,0.8],label='h10',lw=5.0)
plt.plot(T_horizon['RBC'],color='b',label='RBC',lw=5.0)
#plt.legend(loc='upper left',fontsize=28)
plt.legend(loc='lower center', bbox_to_anchor=(0.5, 1.05),
          ncol=7, fancybox=True, shadow=True,fontsize=24)
plt.xticks(np.arange(0,t[-1],24),fontsize=32)
plt.yticks(fontsize=34)
#plt.rc('ytick', labelsize=38)    # fontsize of the tick labels
plt.xlabel('Time [hour]', fontsize=32)
#plt.rc('font', size=30)          # controls default text sizes
    # fontsize of the x and y labels
#plt.rc('xtick', labelsize=30)    # fontsize of the tick labels

plt.ylabel('Temperature [\u2103]', fontsize=38)


plt.savefig(os.path.join(out,'Tnew1.pdf'))
