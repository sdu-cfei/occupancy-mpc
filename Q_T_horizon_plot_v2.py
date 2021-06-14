import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

zone='20-601b-2'
 
## Ideal occ
#horizons=os.listdir(os.path.join('new_results','mpc_ideal_occ_v2'))
horizons=['240','360','480','600']

Q_ideal_horizon=pd.DataFrame()
T_discomfort_ideal_horizon=pd.DataFrame()
for horizon in horizons:
    Q_ideal_horizon['{}'.format(horizon)]=pd.read_csv(os.path.join('new_results','figs_ideal_occ_v2','{}_qr_200'.format(horizon), zone,'Q.csv'))['Q']
    T_discomfort_ideal_horizon['{}'.format(horizon)]=pd.read_csv(os.path.join('new_results','figs_ideal_occ_v2','{}_qr_200'.format(horizon),zone,'T_discomfort.csv'))['T_vio']
    
## Predicted occ    
Q_predicted_horizon=pd.DataFrame()
T_discomfort_predicted_horizon=pd.DataFrame()
for horizon in horizons:
    Q_predicted_horizon['{}'.format(horizon)]=pd.read_csv(os.path.join('new_results','figs_predicted_occ_v2','{}_qr_200'.format(horizon),zone,'Q.csv'))['Q']
    T_discomfort_predicted_horizon['{}'.format(horizon)]=pd.read_csv(os.path.join('new_results','figs_predicted_occ_v2','{}_qr_200'.format(horizon),zone,'T_discomfort.csv'))['T_vio']


Q_ideal=pd.DataFrame(Q_ideal_horizon.iloc[0]).set_index(np.arange(4,12,2)).rename(columns={0:'ideal_occ'})
Q_predicted=pd.DataFrame(Q_predicted_horizon.iloc[0]).set_index(np.arange(4,12,2)).rename(columns={0:'predicted_occ'})
Q=pd.concat([Q_ideal,Q_predicted],axis=1)

T_discomfort_ideal=pd.DataFrame(T_discomfort_ideal_horizon.iloc[0]).set_index(np.arange(4,12,2)).rename(columns={0:'ideal_occ'})
T_discomfort_predicted=pd.DataFrame(T_discomfort_predicted_horizon.iloc[0]).set_index(np.arange(4,12,2)).rename(columns={0:'predicted_occ'})
T_discomfort=pd.concat([T_discomfort_ideal,T_discomfort_predicted],axis=1)

Q_RBC=pd.read_csv(os.path.join('new_results','figs_rbc_Tc_Th_v2',zone,'Q.csv'))
T_RBC=pd.read_csv(os.path.join('new_results','figs_rbc_Tc_Th_v2',zone,'T_discomfort.csv'))

#plot energy consumption 
plt.figure(figsize=(30,2),dpi=150)
ax=Q.plot.bar(rot=0)
for x in Q.index.values:
    plt.text((-0.25+(x-4)/2.), Q.at[x,'ideal_occ']+0.5, round(Q.at[x,'ideal_occ'],1))
    plt.text((0.02+(x-4)/2.), Q.at[x,'predicted_occ']+0.7, round(Q.at[x,'predicted_occ'],1))

plt.axhline(y=Q_RBC['Q'].values, color='r', linestyle='--',label='RBC')
ax.legend(loc='upper center',
          fancybox=True, shadow=True, ncol=3,fontsize=10)
#plt.xticks(np.arange(4,12,2))
plt.yticks(np.arange(0,80,10),fontsize=16)
plt.ylabel('Energy consumption [kWh]',fontsize=16)
plt.xlabel('Horizon [hour]',fontsize=16)
plt.rc('font', size=12)          # controls default text sizes
plt.rc('axes', labelsize=20)    # fontsize of the x and y labels
plt.rc('xtick', labelsize=20)    # fontsize of the tick labels
plt.rc('ytick', labelsize=20) 
plt.savefig(os.path.join('new_results','figs_MPC_ideal_vs_predicted_v2','20-601b-2','Q_total_bar_new.pdf'))

#plot temperature discomfort
plt.figure(figsize=(30,4),dpi=150)
ax=T_discomfort.plot.bar(rot=0)
for x in T_discomfort.index.values:
    plt.text((-0.25+(x-4)/2.), T_discomfort.at[x,'ideal_occ']+0.2, round(T_discomfort.at[x,'ideal_occ'],1))
    plt.text((0.02+(x-4)/2.), T_discomfort.at[x,'predicted_occ']+0.2, round(T_discomfort.at[x,'predicted_occ'],1))

plt.axhline(y=T_RBC['T_vio'].values, color='r', linestyle='--',label='RBC')
ax.legend(loc='upper center',
          fancybox=True, shadow=True, ncol=3,fontsize=10)
#plt.title('Temperature discomfort')
#plt.xticks(np.arange(4,12,2))
plt.yticks(np.arange(0,8,1))
plt.ylabel('Temperature discomfort [Kh]')
plt.xlabel('Horizon [hour]')
plt.rc('font', size=12)          # controls default text sizes
plt.rc('axes', labelsize=12)    # fontsize of the x and y labels
plt.rc('xtick', labelsize=14)    # fontsize of the tick labels
plt.rc('ytick', labelsize=14) 
plt.savefig(os.path.join('new_results','figs_MPC_ideal_vs_predicted_v2','20-601b-2','T_discomfort_bar_new.pdf'))
