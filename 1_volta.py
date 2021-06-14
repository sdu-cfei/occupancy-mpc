"""
This script downloads data from Volta (zone ...)
and saves it in "measurements/zone_name/measurements.csv".
"""

from datetime import datetime
import logging
import asyncio
import os
import numpy as np
import pandas as pd

import pytz

# This library is available at http://cfeidocker.tek.sdu.dk:7080/cfei/cfei-smap/
# A Wheel file which can be installed with `pip install /path/to/wheel.whl` is
# available at http://cfeidocker.tek.sdu.dk:7080/cfei/cfei-smap/tags
# A Debian package (usable on Ubuntu as well) is also available.
from cfei.smap import SmapAiohttpInterface


zones = ['22-511-2', '20-601b-2']

uuids = {
    '22-511-2': {
        'CO2':    'f1d3f196-6ad4-5bd5-bb13-d620dce773ed',
        'T':      '4834d20f-d2d8-5a16-9fc6-738dc5cfdbe1',
        'solrad': 'b2bfefa6-32f1-583e-91e7-332e74503d42',   # Pyrometer [W/m2]
        'Tout':   '76958e41-8361-531e-9ae4-f25500f4fd55',   # 5 degC too high on average !!!
        'occ':    '40fadf34-8d39-1f0e-ec2a-2f76e5fe7b5f',   # OccuRE Estimation
        'dpos':   '93ad2f1b-e821-51a3-99ae-2051fcdf44a5',   # damper, OPC, range 0-255 !!!
        'vpos':   'cdd972bc-4724-51e7-879f-af4d4044bb5a'    # Valve, OPC, range 0-100
    },
    '20-601b-2': {
        'CO2':    '6af5e0aa-4d39-5bbb-994b-0548ebff04de',
        'T':      '3ca7b95f-3232-50bc-9ec4-739b010a1d70',
        'solrad': 'b2bfefa6-32f1-583e-91e7-332e74503d42',   # Pyrometer [W/m2]
        'Tout':   '76958e41-8361-531e-9ae4-f25500f4fd55',   # 5 degC too high on average !!!
        'occ':    'acf29328-9428-43d7-0b38-c8c6733fbcd4',   # OccuRE Estimation
        'dpos':   'f2d38f04-1466-54ce-8e58-1bdf8e71280b',   # damper, OPC, range 0-100
        'vpos':   'bdbcabd6-432a-54b1-b06b-e80e8afde710'    # Valve, OPC, range 0-100
    }
}


def fetch(dest, fname, dt_start, dt_stop, **kwargs):
    """
    Fetches multiple streams from volta. The results are saved
    in ./download/dest/. The streams have to be uniquely described
    with **kwargs (metadata keys and values).

    :param dest: destination directory, results are saved in ./download/dest/
    :param fname: destination file name
    :param dt_start: datetime instance, beginning of the period
    :param dt_stop: datetime instance, end of the period
    :param kwargs: k1 = meta_key, v1 = meta_value, k2 = ...
    :return: None
    """

    outdir = os.path.join(dest)

    # smap = SmapAiohttpInterface("http://volta.sdu.dk:8079")
    smap = SmapAiohttpInterface("http://10.137.0.167:8079")

    timezone = pytz.timezone("Europe/Copenhagen")

    # Construct metadata keys and values from kwargs
    metadata = dict()
    for key in kwargs:
        if 'k' in key:
            # Add new key and value to metadata
            key_num = int(key[1:])
            metadata[kwargs[key]] = kwargs["v{}".format(key_num)]
        elif 'v' in key:
            # values are found based on key_num
            pass
        else:
            raise KeyError("Invalid key ({}) in kwargs. ".format(key) + \
                           "Keys in kwargs should be names k1, v1, k2, v2, ...")

    # Specify the current timezone, but all queries must be done on UTC
    start = timezone.localize(dt_start).astimezone(pytz.UTC)
    end = timezone.localize(dt_stop).astimezone(pytz.UTC)

    # Construct query
    # e.g.
    # where = "Metadata/Description = '...' and Metadata/OPCUADescription = '...'"
    where = ""
    key_count = len(metadata.keys())
    n = 0
    for key in metadata:
        where += "{} = '{}'".format(key, metadata[key])
        n += 1
        if n < key_count:
            where += " and "

    print("QUERY:")
    print(where)

    streamlimit = 10  # How many streams to return (default 10)

    loop = asyncio.get_event_loop()

    results = loop.run_until_complete(
        # This method returns a map (UUID -> Pandas time-series)
        smap.fetch_readings(start, end, where, streamlimit=streamlimit, limit=1e9)
    )

    print("RESULTS:")
    print(results)

    # Make output directory
    if not os.path.exists(outdir):
        os.makedirs(outdir)

    # Create dataframe
    df = pd.DataFrame()

    for uuid, readings in results.items():
        # Convert the index back to the desired timezone
        # Not necessary if UTC is acceptable
        readings.index = readings.index.tz_convert(None)  # Convert to UTC

        # Remove timezone information (***HIGHLY*** discouraged)
        # This must be done after converting the timezone in the step before
        # readings.index = readings.index.tz_convert(None)

        readings.name = fname.split('.')[0]  # Column name in CSV

        # Add to dataframe
        df[readings.name] = readings

    df.to_csv(os.path.join(outdir, fname), index_label="datetime", header=True)

    return df


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)

    # Download all into separate files

    dest = "measurements"
    dt_start = datetime(2018, 4, 4)
    dt_stop = datetime(2018, 4, 14)


    for z in zones:
        dfs = list()
        dest_z = os.path.join(dest, z)

        for k, v in uuids[z].items():
            fname = "{}.csv".format(k)
            df = fetch(
                dest=dest_z,
                fname=fname,
                dt_start=dt_start,
                dt_stop=dt_stop,
                k1="uuid", v1=v
            )
            dfs.append(df)

        # Merge all files into measurements.csv
        meas = pd.concat(dfs, axis=1)
        meas.index.rename('datetime', inplace=True)

        # Indoor temperature setpoint
        # meas['Tstp'] = 21.  # Not needed for the current model (ZoneCO2R2C2)

        # Resample to 30 minutes
        meas = meas.resample('30min').mean()

        # Shift occupancy by 1h
        meas['occ'] = meas['occ'].shift(2)

        # Correct outdoor temperature (degC -> K)
        meas['Tout'] = meas['Tout'] - 5. + 273.15

        # Correct indoor temperature (degC -> K)
        meas['T'] = meas['T'] + 273.15

        # Rescale dpos in 22-511-2
        if z == '22-511-2':
            meas['dpos'] = meas['dpos'] / 2.55

        # Drop empty rows
        meas = meas.ffill().dropna()

        # Save
        meas.to_csv(os.path.join(dest_z, 'measurements.csv'))




