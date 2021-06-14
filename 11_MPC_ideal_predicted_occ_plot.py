import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
 

zone='20-601b-2'

yemu_ideal_occ=pd.read_csv(os.path.join('new_results','mpc_ideal_occ','240_qr',zone,'yemu.csv'))
yemu_predicted_occ=pd.read_csv(os.path.join('new_results','mpc_predicted_occ','240_qr',zone,'yemu.csv'))
yemu_low_occ=pd.read_csv(os.path.join('new_results','mpc_predefined_occ','240_qr',zone,'yemu.csv'))
yemu_high_occ=pd.read_csv(os.path.join('new_results','mpc_predefined_high_occ','240_qr',zone,'yemu.csv'))
yemu_no_occ=pd.read_csv(os.path.join('new_results','mpc_predefined_no_occ','240_qr',zone,'yemu.csv'))


constr=pd.read_csv(os.path.join('new_results','mpc_ideal_occ','240_qr',zone,'constr.csv'))
tindex = pd.read_csv(os.path.join('new_results','no_control',zone,'tindex.csv'))
tindex['datetime'] = pd.to_datetime(tindex['datetime'])
tindex['time'] /= 3600.
t = tindex['time'].values

out= os.path.join('new_results','figs_MPC_ideal_vs_predicted',zone)
if not os.path.exists(out):
    os.makedirs(out)

#plotting indoor temperature vs. constraints
plt.figure(figsize=(10,4),dpi=150)
plt.plot(constr['Tair_lo'], color='black', ls='--', lw=1.0)
plt.plot(constr['Tair_hi'], color='black', ls='--', lw=1.0)
plt.plot(yemu_ideal_occ['T'],color=[1,0.5,0.5], label='ideal occ')
plt.plot(yemu_predicted_occ['T'],color='r',label='predicted occ')
plt.plot(yemu_no_occ['T'],color='g',label='no occ')
plt.plot(yemu_low_occ['T'],color=[0,0.8,0.8],label='low occ')
plt.plot(yemu_high_occ['T'],color='y',label='high occ')
plt.legend()
plt.title('MPC indoor temperature vs. constraints')
plt.xticks(np.arange(0,t[-1],24))
plt.ylabel('T[K]')
plt.xlabel('t[h]')
plt.savefig(os.path.join(out,'T.png'))

#plotting energy consumption 
plt.figure(figsize=(10,4),dpi=150)
plt.plot(yemu_ideal_occ['qr'],color=[1,0.5,0.5], label='ideal occ')
plt.plot(yemu_predicted_occ['qr'],color='r',label='predicted occ')
plt.plot(yemu_no_occ['qr'],color='g',label='no occ')
plt.plot(yemu_low_occ['qr'],color=[0,0.8,0.8],label='low occ')
plt.plot(yemu_high_occ['qr'],color='y',label='high occ')
plt.legend()
plt.title('MPC energy consumption')
plt.xticks(np.arange(0,t[-1],24))
plt.ylabel('q[W]')
plt.xlabel('t[h]')
plt.savefig(os.path.join(out,'Q.png'))


    
            