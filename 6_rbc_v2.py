"""
This script runs our model with a rule-based controller. The controller is implemented inside
Modelica by adding PID blocks controlling damper and valve positions.

See model MShootBS2019.ZoneCO2R2C2PID.

Krzysztof generated a temporary FMU from this model, but his license doesn't allow to generate
licence-free FMUs. Tao should replace this FMU with a one compiled on his computer.

Results are saved in "results/rbc/".
"""
import os

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

import mshoot


# Zones
#zones=['22-511-2']
zones = ['22-511-2', '20-601b-2']

# Emulation period and settings
emu_start = pd.to_datetime('2018-04-05 00:00:00')  # SHOULD BE CONSISTENT WITH MPC EMULATION TIME FROM 3_mpc.py
emu_stop = pd.to_datetime('2018-04-08 00:00:00')   # SHOULD BE CONSISTENT WITH MPC EMULATION TIME FROM 3_mpc.py
emu_step = 60                                      # SHOULD BE CONSISTENT WITH MPC EMULATION TIME FROM 3_mpc.py

for zone in zones:

    print('Running zone {}...'.format(zone))

    # Output directory
    out = os.path.join('new_results', 'rbc_Tc_Th_v2', zone)

    # Create directory if doesn't exist
    if not os.path.exists(out):
        os.makedirs(out)

    # Read parameters
    parcsv = os.path.join('results', 'calibration', zone, 'parameters.csv')
    parameters = pd.read_csv(parcsv).iloc[0].to_dict()
    parameters['maxHeat']=5378

    # Control and emulation models
    fmupath = os.path.join('models', 'MShootBS2019_ZoneCO2R2C2PID.fmu')

    outputs = ['T', 'CO2', 'qv', 've', 'qr', 'Tout']
    states = ['cair.T', 'cint.T', 'co2.balance.CO2ppmv_i']

    model = mshoot.SimFMU(fmupath, outputs, states, parameters)

    # Measurements
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
    constr['CO2_lo'] = 400.
    constr['CO2_hi'] = 800.

    # Inputs to the model
    inp = meas[['solrad', 'Tout', 'occ']]
    inp['CO2stp'] = 800.             # maximum CO2 setpoint
    inp['Tstp_heating'] = constr['Tair_lo']  # heating setpoint (cooling not available)
    inp['Tstp_cooling'] = constr['Tair_hi']

    # Initial state
    # We assume that internal thermal mass has the same initial temperature as indoor air
    #x0 = [meas.iloc[0]['T'], meas.iloc[0]['T'], meas.iloc[0]['CO2']]
    x0 = [294.15, 294.15, 420]

    # Simulate the model
    ydf, xdf = model.simulate(inp, x0)

    # Save outputs
    ydf.to_csv(os.path.join(out, 'ydf.csv'))

    # Save states
    xdf.to_csv(os.path.join(out, 'xdf.csv'))

