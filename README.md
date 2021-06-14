# Python environment

These are the steps needed to make Krzysztof's scripts working:

1. conda --add channels conda-forge
2. conda --add channels defaults
3. conda create --name occ-mpc-paper python=3.6
4. conda activate occ-mpc-paper
5. conda install numpy scipy scikit-learn matplotlib keras tensorflow pylint pandas tzlocal modestpy
6. git clone https://github.com/sdu-cfei/cfei-smap
7. cd cfei-smap
8.  python -m pip install .

Note, that `keras` and `tensorflow` are already added (Fisayo's scripts depend on them).

# Scripts

1. 1_volta.py - downloads measurements for 22-511-2 and 20-601b-2 from Volta
2. 2_calibrate.py - calibrates the zone model for both rooms
3. 3_mpc.py - runs MPC emulation for both zones - needs to be adapted by Fisayo
4. 4_analyze.py - creates plots and summary
