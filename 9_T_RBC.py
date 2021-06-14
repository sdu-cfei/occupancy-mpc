import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
 

zone='20-601b-2'

ydf_no_control=pd.read_csv(os.path.join('new_results','no_control',zone,'ydf.csv'))
ydf_heating_cooling=pd.read_csv(os.path.join('new_results','rbc_heating_cooling',zone,'ydf.csv'))
ydf_only_cooling=pd.read_csv(os.path.join('new_results','rbc_only_cooling',zone,'ydf.csv'))
ydf_only_heating=pd.read_csv(os.path.join('new_results','rbc_only_heating',zone,'ydf.csv'))
constr=pd.read_csv(os.path.join('new_results','mpc_ideal_occ','240_qr',zone,'constr.csv'))

tindex = pd.read_csv(os.path.join('new_results','no_control',zone,'tindex.csv'))
tindex['datetime'] = pd.to_datetime(tindex['datetime'])
tindex['time'] /= 3600.
t = tindex['time'].values

out= os.path.join('new_results','figs_rbc',zone)
if not os.path.exists(out):
    os.makedirs(out)

#plotting indoor temperature vs. constraints
plt.figure(figsize=(10,4),dpi=150)
plt.plot(constr['Tair_lo'], color='black', ls='--', lw=1.0)
plt.plot(constr['Tair_hi'], color='black', ls='--', lw=1.0)
plt.plot(ydf_no_control['T'],color=[1,0.5,0.5], label='no control')
plt.plot(ydf_heating_cooling['T'],color='y',label='heating/cooling')
plt.plot(ydf_only_cooling['T'],color='g',label='only cooling')
plt.plot(ydf_only_heating['T'],color=[0,0.8,0.8],label='only heating')
plt.legend()
plt.title('RBC indoor temperature vs. constraints')
plt.xticks(np.arange(0,t[-1],24))
plt.ylabel('T[K]')
plt.xlabel('t[h]')
plt.savefig(os.path.join(out,'T.png'))


    
            