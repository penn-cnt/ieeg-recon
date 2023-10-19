#!/bin/bash

# Create a conda environment with the specified Python version
conda create -n ieeg_recon_m1 python=3.9 -y

# Activate the conda environment
source activate ieeg_recon_m1

# Upgrade pip
pip install -U pip

# Install the required Python packages
pip install antspyx
pip install antspynet

# Uninstall tensorflow
pip uninstall tensorflow -y

# Install tensorflow for macOS with metal support
SYSTEM_VERSION_COMPAT=0 pip install tensorflow-macos tensorflow-metal

# Install a specific version of tensorflow_probability
pip install tensorflow_probability==0.20.0

# Install the rest of the python packages
pip install nipype
pip install niworkflows
pip install ipython
pip install mayavi
pip install pyqt5
pip install voxtool

echo "Python Environment installed..."
echo "Activate the environment with: conda activate ieeg_recon_m1"
echo "After activation, run iEEG-recon"

# Installing gui
chmod +x install_gui_v2.sh
bash install_gui_v2.sh