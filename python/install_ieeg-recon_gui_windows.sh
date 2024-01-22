#!/bin/bash

# Directory where this script is located
INSTALL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
echo "Install directory: ${INSTALL_DIR}"


# source conda
CONDA_PATH=$(dirname $(dirname $(which conda)))
source "$CONDA_PATH/etc/profile.d/conda.sh"


# Create a conda environment with the specified Python version
echo "Creating iEEG-recon Environment"

conda create -n ieeg_recon python=3.9 -y

# Activate the conda environment
# source activate ieeg_recon_m1
conda activate ieeg_recon

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
pip install pillow
echo "Python Environment installed..."
echo "Activate the environment with: conda activate ieeg_recon"
echo "After activation, run the iEEG-recon docker GUI with: python ${INSTALL_DIR}/ieeg_recon_gui_docker.py"
