# Installing the iEEG-recon GUI

These instructions are for MacOS. For Windows instructions see [here](https://github.com/penn-cnt/ieeg-recon/blob/main/python/docs/Windows_Installation_Instructions.md)

Before installation, both the Docker and local version require Anaconda in order to run VoxTool (Module 1). Please install Anaconda following the instructions specified here: https://docs.anaconda.com/free/anaconda/install/mac-os/

After Anaconda has been successfully installed, proceed with the options below.

## Installing the GUI for the Docker version

To install the Docker iEEG-recon GUI, make sure you have Docker installed (https://www.docker.com/products/docker-desktop/) and running. Then, clone the repository:

```
git clone https://github.com/penn-cnt/ieeg-recon.git
```

After cloning, run the script: `install_ieeg-recon_gui_docker.sh`

```
bash ieeg-recon/python/install_ieeg-recon_gui_docker.sh
```

If the above code ran successfully, you should be able to find iEEG-recon-Docker in your Applications folder.


## Installing the GUI for the native Python version

**Note:** This requires all of the other dependencies to be present (FSL, ANTs, C3D).

To install the iEEG-recon GUI, first clone the repository:

```
git clone https://github.com/penn-cnt/ieeg-recon.git
```

After cloning, run the script: `install_ieeg-recon_gui_m1m2.sh`

```
bash ieeg-recon/python/install_ieeg-recon_gui_m1m2.sh
```

If the above code ran successfully, you should be able to find iEEG-recon in your Applications folder.

### NOTE: For M1/M2 Users

Make sure you change your terminal to run with Rosetta before completing the above steps. To do so, open `Finder -> Applications -> Utilities`, then right click the `Terminal` app, and select `Get Info`. Under `General`, select `Open using Rosetta`

![](../../docs/source/images/screenshots/1.png)



