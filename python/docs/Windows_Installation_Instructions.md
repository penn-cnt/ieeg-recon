# Installing Docker

Please install docker following the instructions found [here](https://github.com/penn-cnt/ieeg-recon/blob/main/python/docs/Docker_Installation.md)

# Installing Miniconda

You need to have Miniconda installed on your system. Follow the instructions below based on your operating system.

1. Download the Miniconda installer for Windows from the [official Miniconda page](https://docs.conda.io/en/latest/miniconda.html).
2. Run the installer and follow the on-screen instructions.
3. After installation, use the Anaconda Prompt for the following commands.

**Note about WSL:** I have tried WSL, and the Anaconda Prompt approach descibed above is a better option. If you get WSL working with this approach, let me know!

# Installing Git:

Install git by typing:

```
conda install git
```

# Clone the repository

Clone this repository by doing:

```
git clone https://github.com/penn-cnt/ieeg-recon.git
```

# Install the GUI:

After cloning, install the GUI by running:

```
bash ieeg-recon/python/install_ieeg-recon_gui_windows.sh
```

# Install VoxTool

Due to differences in package dependencies, the Windows version of iEEG-recon requires a step-by-step installation of VoxTool. It can easily be done by following the instructions [here](https://github.com/penn-cnt/ieeg-recon/blob/main/python/docs/Manual_Voxtool_Installation.md)

# Running iEEG-recon

After all the steps above are completed, activate the `ieeg_recon` environment:

```
conda activate ieeg_recon
```

Then run the GUI by typing:


```
python  ieeg-recon/python/ieeg_recon_gui_docker_windows.py
```
