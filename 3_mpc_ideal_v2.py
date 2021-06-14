"""
This script runs an MPC emulation using the zone model (R2C2.fmu)
and using occupancy predictions from Fisayo. New predictions
are generated for each optimization horizon.

The results are saved in "results/mpc".
"""

import os
import logging
import time

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

import mshoot

from occupancy.main import Prediction_Strategy

logging.basicConfig(filename='mpc.log', filemode='w', level='WARNING')

np.random.seed(140417)


# Zones
#zones = ['22-511-2', '20-601b-2']

zones =['20-601b-2']

# Emulation period and settings
emu_start = pd.to_datetime('2018-04-05 00:00:00')  # FISAYO, this time is 0s
emu_stop = pd.to_datetime('2018-04-08 00:00:00')   # 3 days for testing, can be 7 days (Apr 12) for paper
emu_step = 60          # optimization time discretization, integer, number of minutes, minimum 30
emu_horizon = 1440     # optimization horizon, integer, number of minutes, must be a multiple of emu_step -- WE CHANGE ONLY THIS BETWEEN CASES

# Number of steps within the horizon - do not modify
hrz_steps = int(emu_horizon / emu_step)


for zone in zones:

    print('Running zone {}...'.format(zone))
 
    # Output directory
    out = os.path.join('new_results', 'mpc_ideal_occ_v2', '{}_qr_200'.format(emu_horizon), zone)

    if os.path.exists(out):
        print('Skipping {}...'.format(out))

    else:
        os.makedirs(out)

        # Read parameters
        parcsv = os.path.join('results', 'calibration', zone, 'parameters.csv')
        parameters = pd.read_csv(parcsv).iloc[0].to_dict()

        # Control and emulation models
        fmupath = os.path.join('models', 'MShootBS2019_ZoneCO2R2C2.fmu')

        outputs = ['T', 'CO2', 'qv', 've', 'qr', 'Tout']
        states = ['cair.T', 'cint.T']

        model_emu = mshoot.SimFMU(fmupath, outputs, states, parameters)
        model_ctr = mshoot.SimFMU(fmupath, outputs, states, parameters)

        # Inputs for the emulation model
        meascsv = os.path.join('measurements', zone, 'measurements.csv')
        meas = pd.read_csv(meascsv)
        meas['datetime'] = pd.to_datetime(meas['datetime'])
        meas = meas[(meas['datetime'] >= emu_start) & (meas['datetime'] <= emu_stop)]

        meas = meas.set_index('datetime')
        meas = meas.resample('{}min'.format(emu_step)).mean()
        meas = meas.reset_index()

        meas['time'] = (meas['datetime'] - meas['datetime'].iloc[0]).dt.total_seconds().astype(int)
        meas['hour'] = meas['datetime'].dt.hour
        meas = meas.set_index('time')

        meas.to_csv(os.path.join(out, 'meas.csv'))

        inp_emu = meas[['solrad', 'Tout', 'occ', 'dpos', 'vpos']]
        inp_emu['dpos']=0.

        #inp_ctr=meas[['solrad','Tout','dpos','vpos']].copy()
        #inp_ctr['dpos']=0.
        #occ_predefined=np.where((meas['hour'] >= 8) & (meas['hour'] < 18), 0., 0.)
        #inp_ctr['occ']=occ_predefined

        # Time in seconds vs. time in datetime
        tindex = meas[['datetime']]
        tindex.to_csv(os.path.join(out, 'tindex.csv'))

        # Constraints
        tlo = np.where((meas['hour'] >= 8) & (meas['hour'] < 18), 21. + 273.15, 16. + 273.15)
        thi = np.where((meas['hour'] >= 8) & (meas['hour'] < 18), 23. + 273.15, 27. + 273.15)

        constr = pd.DataFrame(index=meas.index.copy())
        constr['Tair_lo'] = tlo
        constr['Tair_hi'] = thi
        constr['Tint_lo'] = 273.15
        constr['Tint_hi'] = 333.15
        #constr['CO2_lo'] = 400.
        #constr['CO2_hi'] = 800.

        constr.to_csv(os.path.join(out, 'constr.csv'))

        # Cost function
        def cfun(xdf, ydf):
            """
            :param ydf: DataFrame, model states
            :param ydf: DataFrame, model outputs
            :return: float
            """
            # Minimize heating and ventilation energy consumption (ventilation + radiator)
            #Tout = ydf['Tout'] + 273.15
            #Tin = (ydf['T'] - Tout) * 0.8 + Tout

            #qv = 1005 * ydf['ve'] * 0.01 * parameters['maxVent'] / 3600. * 1.2 * (294.15 - Tin) #/1000.
            #qv = np.where(qv > 0, qv, 0)

            return (ydf['qr'].abs()).sum() # @TAO: divide by some number if objective function becomes too big

        # Callback function generating inputs for the control model
        # HERE WE PUT NEW OCCUPANCY FORECASTS FOR EACH OPTIMIZATION HORIZON
        def inp_clb(index):
            """
            This function is passed to the MPC emulation and called whenever
            MPC needs new forecasts. It is called at the beginning of
            each optimization horizon. `index` is a list with time in seconds
            since the beginning of simulation. To avoid floating-point errors,
            seconds should be given as integers, e.g.:

            - [0, 1800, 3600, 5400] - first optimization horizon,
            - [5400, 7200, 9000, 10800] - second optimization horizon.

            The length of index and time steps might change.
            They depend on the settings of the MPC emulation.

            :param index: list of integers
            :return: pd.Dataframe
            """
            # Take all inputs from measurements
            inp = meas[['solrad', 'Tout', 'occ', 'dpos', 'vpos']].loc[index]
            #inp['dpos']=0.
            
            
            # Replace occupancy with a forecast
            # NOTE: Double-check time alignment of occupancy with other (e.g. occupancy on Volta is 1h ahead of time)
            datetime_start = meas['datetime'].loc[index[0]]  # First datetime
            datetime_stop = meas['datetime'].loc[index[-1]]  # Last datetime
            time_step = index[1] - index[0]                  # Time resolution in seconds

            
            # EXAMPLE HOW TO CALL THE FUNCTION
            strategy = Prediction_Strategy()
            timestamp = str(datetime_start) #ANYTIME
            room = zone # ROOM CAN BE 20-604b-1, 22-511-2, OU44, 22-508-1, 20-601b-2
            look_forward = int((datetime_stop - datetime_start).total_seconds()/60) # IN MINUTES
            resample = emu_step # IN MINUTES
            prediction = strategy.predict(timestamp, room, look_forward, resample) # IT RETURNS THE PREDICTION AND RAW COUNT
            prediction.index = index
        
            inp['occ'] = prediction #.. TODO: ---------------------------------------------------------------------> FISAYO

            # Make sure number of rows equals the length of index
            assert inp.index.size == len(index), 'Incorrect number of rows in Dataframe returned by inp_clb'

            inp.to_csv(os.path.join(out, "inp_ctr_{}.csv".format(index[0])))

            return inp


        # Start MPC emulation
        mpc = mshoot.MPCEmulation(model_emu, cfun)

        x0 = [294.15, 294.15]  # Indoor temperature [K], indoor thermal mass [K], indoor CO2 [ppm]

        t0 = time.time()
        u, xctr, xemu, yemu, u_hist = mpc.optimize(
            model=model_ctr,
            inp_ctr=inp_emu,
            inp_clb=None,
            inp_emu=inp_emu,
            free=['vpos'],
            ubounds=[(-200., 200.)],
            xbounds=[(constr['Tair_lo'].values, constr['Tair_hi'].values),
                    (constr['Tint_lo'].values, constr['Tint_hi'].values)],
                    #(constr['CO2_lo'].values,  constr['CO2_hi'].values)],
            x0=x0,
            maxiter=50,
            ynominal=[300., 800., 5000., 4800., 4000., 300.],  # ['T', 'CO2', 'qv', 've', 'qr', 'Tout']
            step=1,
            horizon=hrz_steps
        )
        cputime = int(time.time() - t0)

        with open(os.path.join(out, 'cputime.txt'), 'w') as f:
            f.write("{}\n".format(cputime))

        # Save results
        u.to_csv(os.path.join(out, 'u.csv'))
        xctr.to_csv(os.path.join(out, 'xctr.csv'))
        xemu.to_csv(os.path.join(out, 'xemu.csv'))
        yemu.to_csv(os.path.join(out, 'yemu.csv'))

        i = 1
        for ui in u_hist:
            ui.to_csv(os.path.join(out, 'u{}.csv'.format(i)))
            i += 1