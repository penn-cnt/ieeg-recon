#!/bin/bash

# Create a conda environment with the specified Python version
conda create -n ieeg_recon_m1 python=3.9 -y

# Activate the conda environment
# source activate ieeg_recon_m1
CONDA_PATH=$(dirname $(dirname $(which conda)))
source "$CONDA_PATH/etc/profile.d/conda.sh"
conda activate ieeg_recon_m1

# Upgrade pip
pip install -U pip

# Install the required Python packages
pip install antspyx
pip install antspynet

# Install the rest of the python packages
pip install nipype
pip install niworkflows
pip install ipython
pip install mayavi
pip install pyqt5
pip install voxtool
pip install pydeface

echo "Python Environment installed..."
echo "Activate the environment with: conda activate ieeg_recon_m1"
echo "After activation, run iEEG-recon"

# Install the GUI
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
chmod +x "$SCRIPT_DIR/install_gui_v2.sh"
bash "$SCRIPT_DIR/install_gui_v2.sh"
bash "$SCRIPT_DIR/install_gui_v2.sh"