#!/bin/bash

echo "\n\n------------Loading VoxTool...------------\n\n"

# Get the directory where the install script is located
INSTALL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Find the location of Anaconda
CONDA_PATH=$(dirname $(dirname $(which conda)))

# Load the voxtool virtual environment
source "$CONDA_PATH/etc/profile.d/conda.sh"
conda activate vt

python $INSTALL_DIR/../voxTool/launch_pyloc.py