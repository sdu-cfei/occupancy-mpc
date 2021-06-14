import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
 
## Temperature discomfort
zone='20-601b-2'

def filter_T(row):
    if (row['Tin']<=row['T_hi'])&(row['Tin']>=row['T_lo']):
        row['Tin']=0.
    else:
        row['Tin']=min(abs(row['Tin']-row['T_hi']),abs(row['Tin']-row['T_lo']))
    return row

    
result_dir=os.path.join('new_results','mpc_ideal_occ_v2','1440_qr_200',zone)
out_dir=os.path.join('new_results','figs_ideal_occ_v2','1440_qr_200',zone)
constr=pd.read_csv(os.path.join(result_dir,'constr.csv'))
yemu=pd.read_csv(os.path.join(result_dir,'yemu.csv'))
tindex = pd.read_csv(os.path.join(result_dir,'tindex.csv'))
tindex['datetime'] = pd.to_datetime(tindex['datetime'])
tindex['time'] /= 3600.
t = tindex['time'].values
    
    
T_discomfort=pd.DataFrame(index=np.arange(0,t[-1]+1,1))
T_discomfort['Tin']=yemu['T']
T_discomfort['T_hi']=constr['Tair_hi']
T_discomfort['T_lo']=constr['Tair_lo']
T_discomfort=T_discomfort.apply(filter_T,axis=1)
T_violation=T_discomfort['Tin'].sum()
T_vio=pd.DataFrame({'T_vio':[T_violation]})
T_vio.to_csv(os.path.join(out_dir,'T_discomfort.csv'))
