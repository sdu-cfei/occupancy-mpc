# this script is used to plot temperature and CO2 evolution under rule based control
# figures are saved in fig_rbc

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


#read constraints and optimization period
constr=pd.read_csv(os.path.join('new_results','mpc_ideal_occ_v2','240_qr_200','20-601b-2','constr.csv'))
tindex = pd.read_csv(os.path.join('new_results','mpc_ideal_occ_v2','240_qr_200','20-601b-2','tindex.csv'))
tindex['datetime'] = pd.to_datetime(tindex['datetime'])
tindex['time'] /= 3600.
t = tindex['time'].values

zones=['20-601b-2']

for zone in zones:
    res=os.path.join('new_results','rbc_Tc_Th_v2',zone)
    out_dir=os.path.join('new_results','figs_rbc_Tc_Th_v2',zone)
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)
    ydf=pd.read_csv(os.path.join(res,'ydf.csv'))

    q_total=(ydf['qr'].abs()/1000.).sum()
    Q=pd.DataFrame({'Q':[q_total]})
    Q.to_csv(os.path.join(out_dir,'Q.csv'))
    
    #plotting indoor temperature vs. constraints
    plt.figure(figsize=(10,4),dpi=150)
    plt.plot(constr['Tair_lo'], color='black', ls='--', lw=1.0)
    plt.plot(constr['Tair_hi'], color='black', ls='--', lw=1.0)
    plt.plot(ydf['T'],color='r' )
    plt.title('Indoor temperature vs. constraints')
    plt.xticks(np.arange(0,t[-1],24))
    plt.ylabel('T[K]')
    plt.xlabel('t[h]')
    plt.savefig(os.path.join(out_dir,'T.png'))
    
    # Plot indoor CO2 vs. constraints
    plt.figure(figsize=(10,4),dpi=150)
    plt.plot(constr['CO2_lo'], color='black', ls='--', lw=1.0)
    plt.plot(constr['CO2_hi'], color='black', ls='--', lw=1.0)
    plt.plot(ydf['CO2'],color='b')
    plt.title('CO2 concentration vs. constraints')
    plt.xticks(np.arange(0,t[-1],24))
    plt.ylabel('C[ppm]')
    plt.xlabel('t[h]')
    plt.savefig(os.path.join(out_dir,'CO2.png'))


