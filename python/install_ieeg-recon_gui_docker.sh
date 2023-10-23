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

# install packages needed for voxtool
pip install ipython
pip install mayavi
pip install pyqt5
pip install voxtool

echo "Python Environment installed..."
echo "Activate the environment with: conda activate ieeg_recon_m1"

# Install the GUI
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
chmod +x "$SCRIPT_DIR/install_gui_docker_v2.sh"
bash "$SCRIPT_DIR/install_gui_docker_v2.sh"
bash "$SCRIPT_DIR/install_gui_docker_v2.sh"