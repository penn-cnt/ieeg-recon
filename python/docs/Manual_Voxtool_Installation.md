# Installing Miniconda

Before setting up the `voxtool` environment, you need to have Miniconda installed on your system. Follow the instructions below based on your operating system.

## For Windows:

1. Download the Miniconda installer for Windows from the [official Miniconda page](https://docs.conda.io/en/latest/miniconda.html).
2. Run the installer and follow the on-screen instructions.
3. After installation, use the Anaconda Prompt for the following commands.

## For macOS and Linux:

1. Download the Miniconda installer for macOS or Linux from the [official Miniconda page](https://docs.conda.io/en/latest/miniconda.html).
2. Open a terminal.
3. Run the installation script. For example, if the downloaded file is `Miniconda3-latest-MacOSX-x86_64.sh`, run:
   ```
   bash Miniconda3-latest-MacOSX-x86_64.sh
   ```
   Follow the on-screen instructions during the installation.

After installing Miniconda, you can proceed with setting up the `voxtool` environment as described below.

---

# Setting Up Environment for voxtool

Follow these steps to set up the environment and install the necessary dependencies for `voxtool`.

## Step 1: Create a New Conda Environment

First, create a new conda environment named `vt` with Python 2.7.

```
conda create --name vt python=2.7
```

## Step 2: Add Conda Channels

Add the `conda-forge` and `free` channels to Conda configuration.

```
conda config --add channels conda-forge
conda config --add channels free
```

## Step 3: Activate the Environment

Activate the newly created environment.

```
conda activate vt
```

*Note: If you encounter any issues activating the environment, ensure that your Conda setup is correctly initialized in your shell.*

## Step 4: Install Dependencies

Install the necessary packages in the `vt` environment. In this section, please install one package after the other (sorry, it is tedious, but it ensures that everything is set up correctly)

```
conda install vtk
conda install pyqt=4
conda install mayavi
conda install nibabel
conda install pydicom=1.2
conda install matplotlib
conda install yaml
conda install pyyaml
```

## Final Step: Verify Installation

After installing all the packages, verify that everything is installed correctly. You can do this by trying to import the packages in a Python session.

---

Following these steps should set up the `vt` environment with all the required dependencies for `voxtool`.
