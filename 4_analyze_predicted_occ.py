"""
This script analyzes the MPC results and generates plots in
"results/figs"
"""

import os

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# Zones
#zones = ['22-511-2', '20-601b-2']
zones=['20-601b-2']

for zone in zones:

    # MPC results directory
    res = os.path.join('new_results', 'mpc_predicted_occ_v2','600_qr_200', zone)

    # Output directory
    out = os.path.join('new_results', 'figs_predicted_occ_v2','600_qr_200', zone)

    if not os.path.exists(out):
        os.makedirs(out)

    # Read data
    tindex = pd.read_csv(os.path.join(res, 'tindex.csv'))
    tindex['datetime'] = pd.to_datetime(tindex['datetime'])
    tindex['time'] /= 3600.
    t = tindex['time'].values

    constr = pd.read_csv(os.path.join(res, 'constr.csv'))
    u = pd.read_csv(os.path.join(res, 'u.csv'))
    xctr = pd.read_csv(os.path.join(res, 'xctr.csv'))
    xemu = pd.read_csv(os.path.join(res, 'xemu.csv'))
    yemu = pd.read_csv(os.path.join(res, 'yemu.csv'))
    
    #plotting indoor temperature vs. constraints
    plt.figure(figsize=(10,4),dpi=150)
    plt.plot(constr['Tair_lo'], color='black', ls='--', lw=1.0)
    plt.plot(constr['Tair_hi'], color='black', ls='--', lw=1.0)
    plt.plot(yemu['T'],color='r', label='Indoor temperature')
    plt.legend()
    plt.title('Indoor temperature vs. constraints')
    plt.xticks(np.arange(0,t[-1],24))
    plt.ylabel('T[K]')
    plt.xlabel('t[h]')
    plt.savefig(os.path.join(out,'T.png'))
    
    #plotting valve position of heating/cooling supply
    plt.figure(figsize=(10,4),dpi=150)
    plt.plot(u['vpos'],color='b', label='Valve position')
    plt.legend()
    plt.title('Valve positon')
    plt.xticks(np.arange(0,t[-1],24))
    plt.ylabel('vpos[%]')
    plt.xlabel('t[h]')
    plt.savefig(os.path.join(out,'vpos.png'))
    
    #plot energy consumption 
    plt.figure(figsize=(10,4),dpi=150)
    plt.plot(yemu['qr']/1000.,color=[1,0.5,0.5], label='Energy consumption')
    plt.legend()
    plt.title('Energy consumption')
    plt.xticks(np.arange(0,t[-1],24))
    plt.ylabel('q[KW]')
    plt.xlabel('t[h]')
    plt.savefig(os.path.join(out,'q.png'))
    
    q_total=(yemu['qr'].abs()/1000.).sum()
    Q=pd.DataFrame({'Q':[q_total]})
    Q.to_csv(os.path.join(out,'Q.csv'))


##plot occupancy of two zones
#mea_601b=pd.read_csv(os.path.join('new_results','mpc_ideal_occ','240_qr','20-601b-2','meas.csv'))
#mea_511=pd.read_csv(os.path.join('new_results','mpc_ideal_occ','240_qr','22-511-2','meas.csv'))
#plt.figure(figsize=(10,4),dpi=150)
#plt.plot(mea_601b['occ'],color='r', label='20-601b-2')
#plt.plot(mea_511['occ'],color='b', label='22-511-2')
#plt.legend()
#plt.title('occupancy of two zones')
#plt.xticks(np.arange(0,t[-1],24))
#plt.ylabel('occupancy')
#plt.xlabel('t[h]')
#plt.savefig(os.path.join('new_results','figs_ideal_occ','occ.png'))


