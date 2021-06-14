import os

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import re

from sklearn.metrics import mean_squared_error
from math import sqrt

# MPC results directory
res = os.path.join('results', 'mpc_predicted_occ')
out_dir = os.path.join('results', 'figs_occ_error')

horizons = os.listdir(res)

for horizon in horizons:
    current_dir = os.path.join(res, horizon)
    out = os.path.join(out_dir, horizon)
    rooms = os.listdir(current_dir)
    for room in rooms:
        prediction_sr = pd.Series()
        room_in = os.path.join(current_dir, room)
        room_out = os.path.join(out, room)
        if not os.path.exists(room_out):
            os.makedirs(room_out)
        
        files = os.listdir(room_in)
        valid = [re.match("(inp_ctr\w+)", elements) for elements in files]
        matches = [e is not None for e in valid]
        ideal = pd.DataFrame().from_csv(os.path.join(room_in, "meas.csv"))

        for i in range(len(matches)):
            if matches[i]:
                file = files[i]
                df = pd.DataFrame().from_csv(os.path.join(room_in, file))
                prediction_sr = prediction_sr.set_value(int(df.index[0]), int(df.iloc[0]["occ"]))

        prediction_sr.index = prediction_sr.index - 3600
        ideal_occ = ideal["occ"]
        ideal_occ.index = ideal_occ.index
        common_index = list(set(ideal_occ.index).intersection(prediction_sr.index))
        rms = sqrt(mean_squared_error(ideal_occ.loc[common_index], prediction_sr.loc[common_index]))
        RMSE=pd.DataFrame({'RMSE':[rms]})
        RMSE.to_csv(os.path.join(room_out,'RMSE.csv'))

        df_plot = pd.DataFrame(columns=["Ideal", "Predicted"], index = common_index)
        df_plot["Ideal"] = ideal_occ.loc[common_index]
        df_plot["Predicted"] = prediction_sr.loc[common_index]
        df_plot = df_plot.sort_index()

        
        df_plot.plot()
        plt.title(room + " at horizon " + horizon)
        plt.savefig(os.path.join(room_out, "out_occ_%s.png"%(room)))
        # plt.show()

        
