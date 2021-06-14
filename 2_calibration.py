"""
This script calibrates the zone model (R2C2.fmu)
to the measured data.

The calibration results are saved in "results/calibration".
"""

import os

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

import modestpy


zones = ['22-511-2', '20-601b-2']

for zone in zones:

    # Paths
    ms_file = os.path.join('measurements', zone, 'measurements.csv')
    fmu_file = os.path.join('models', 'MShootBS2019_ZoneCO2R2C2.fmu')
    res_dir = os.path.join('results', 'calibration', zone)

    if not os.path.exists(res_dir):
        os.makedirs(res_dir)

    # Training and validation periods
    trn_t0 = 5 * 86400
    trn_t1 = trn_t0 + 3 * 86400
    vld_t0 = trn_t0
    vld_t1 = vld_t0 + 4 * 86400

    # Read measurements
    ms = pd.read_csv(ms_file)
    ms['datetime'] = pd.to_datetime(ms['datetime'])
    ms = ms.set_index('datetime')

    # Resample
    # ms = ms.resample('1h').mean().ffill().bfill()

    # Assign model inputs
    inp = ms[['solrad', 'Tout', 'occ', 'dpos', 'vpos']]
    inp['time'] = (inp.index - inp.index[0]).total_seconds()  # ModestPy needs index in seconds
    inp = inp.set_index('time')                               # ModestPy needs index named 'time'
    inp.to_csv(os.path.join(res_dir, 'inp.csv'))

    ax = inp.loc[trn_t0:trn_t1].plot(subplots=True)
    fig = ax[0].get_figure()
    fig.savefig(os.path.join(res_dir, 'inp_training.png'), dpi=200)

    ax = inp.loc[vld_t0:vld_t1].plot(subplots=True)
    fig = ax[0].get_figure()
    fig.savefig(os.path.join(res_dir, 'inp_validation.png'), dpi=200)

    # Assign model desired outputs
    ideal = ms[['T', 'CO2']]
    ideal['time'] = (ideal.index - ideal.index[0]).total_seconds()  # ModestPy needs index in seconds
    ideal = ideal.set_index('time')                                 # ModestPy needs index named 'time'
    ideal.to_csv(os.path.join(res_dir, 'ideal.csv'))

    ax = ideal.loc[trn_t0:trn_t1].plot(subplots=True)
    fig = ax[0].get_figure()
    fig.savefig(os.path.join(res_dir, 'ideal_training.png'), dpi=200)

    ax = ideal.loc[vld_t0:vld_t1].plot(subplots=True)
    fig = ax[0].get_figure()
    fig.savefig(os.path.join(res_dir, 'ideal_validation.png'), dpi=200)

    # Parameters
    known = dict()

    areas = {
        '20-601b-2': 139.,
        '22-511-2': 139.
    }

    radiators = {
        '20-601b-2': 2689,
        '22-511-2': 2689.
    }

    ventilation = {
        '20-601b-2': 4800.,
        '22-511-2': 4800.
    }

    floor_area = areas[zone]
    height = 3.5
    max_heat = radiators[zone]
    max_vent = ventilation[zone]

    known['Vi'] = floor_area * height
    known['CO2n'] = ms['CO2'].min()
    known['maxHeat'] = max_heat
    known['maxVent'] = max_vent
    known['Tve'] = 21. + 273.15

    est = dict()
    est['Vinf'] = (known['Vi']*0.5, known['Vi']*0.25, known['Vi']*5.0)
    est['shgc'] = (0.5, 0.01, 15.0)
    est['tmass'] = (20., 1., 25.)
    est['imass'] = (20., 1., 200.)
    est['RExt'] = (3., 0.5, 3.)
    est['RInt'] = (0.1, 0.05, 1.)
    est['occheff'] = (1., 0.8, 1.2)
    # est['Tve'] = (21. + 273.15, 19. + 273.15, 23. + 273.15)
    # est['maxVent'] = (max_vent, 0.25 * max_vent, max_vent * 2.)
    est['CO2pp'] = (0.02, 0.005, 0.05)

    ic_param = dict()
    ic_param['cair.T'] = 'T'
    # ic_param['cint.T'] = 'T'
    ic_param['co2.balance.CO2ppmv_i'] = 'CO2'

    # Estimation
    ga_opts = {'maxiter': 40, 'tol': 1e-7, 'lhs': True, 'pop_size': 30}
    scipy_opts = {
        'solver': 'L-BFGS-B',
        'options': {'maxiter': 50, 'tol': 1e-12}
        }

    session = modestpy.Estimation(res_dir, fmu_file, inp, known, est, ideal,
        lp_n=3, lp_frame=(trn_t0, trn_t1),
        vp=(vld_t0, vld_t1),
        methods=('GA', 'SCIPY'),
        ga_opts=ga_opts, scipy_opts=scipy_opts,
        ic_param=ic_param, ftype='NRMSE', seed=1)

    estimates = session.estimate()

    vld = session.validate()
    vld_err = vld[0]
    vld_res = vld[1]

    with open(os.path.join(res_dir, 'vld_err.txt'), 'w') as f:
        for k in vld_err:
            f.write("{}: {:.5f}\n".format(k, vld_err[k]))

    vld_res.to_csv(os.path.join(res_dir, 'vld_res.csv'))

    # Save all parameters
    parameters = pd.DataFrame(index=[0])
    for k in estimates:
        parameters[k] = estimates[k]
    for k in known:
        parameters[k] = known[k]

    # Remove ic params (if present, that's probably because `known` has been modified within ModestPy)
    for p in ic_param:
        if p in list(parameters.columns):
            parameters = parameters.drop(p, axis=1)

    parameters.to_csv(os.path.join(res_dir, 'parameters.csv'), index=False)
