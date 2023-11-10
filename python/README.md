# iEEG-Recon
iEEG electrode reconstruction pipeline

# Overview

iEEG-Recon is a pipeline used to reconstruct intracranial electrode coordinates from a post-implant CT scan, into a pre-implant MRI. iEEG-Recon is divided into 3 modules:

- Module 1 consists of an electrode labeling GUI called VoxTool, available here: https://github.com/penn-cnt/voxTool. VoxTool allows the user to label the electrode locations in the post-implant CT scan.
- Module 2 registers the CT scan to the pre-implant MRI and transforms the VoxTool generated coordinates from CT space to MRI space
- Module 3 maps each electrode to a specific ROI defined by a brain atlas registered to the pre-implant MRI

# Installation

## Installing the GUI

We provide a GUI for convenience. All of the commands present in the GUI can be executed in the command line and viceversa. For instructions on installing the GUI, see here: https://github.com/penn-cnt/ieeg-recon/blob/main/python/docs/Installing_the_GUI.md

Two versions of the GUI are available: one runs commands through a Docker container, the other runs commands natively in Python.

## Docker

We recommend using the Docker container available here: https://hub.docker.com/repository/docker/lucasalf11/ieeg_recon

## Native Python Version

The Native Python version is the most flexible, but requires installing all of the dependencies manually. The instructions are below. If you already have these dependencies, and they are available in your system's path, there is no need to re-install them.

## 1. Install Anaconda and Python
- **Anaconda**: Visit [Anaconda's Website](https://www.anaconda.com/products/distribution) and download Anaconda with at least Python 3.7.

## 2. Set Up Your Python Environment
- Open a terminal window.
- Navigate to the directory where you cloned the repository. If you haven't cloned the repository yet, use this command: `git clone [repository-url]`.

- Type the following command:
  ```
  bash ieeg-recon/python/install_ieeg-recon.sh
  ```
- This will create a new `conda` environment called `ieeg_recon_m1`. You can activate your new virtual environment with:
  ```
  conda activate ieeg_recon_m1
  ```

### If You Have M1/M2 Apple Devices

- Inside the repository directory, run the following command:
  ```
  bash ieeg-recon/python/install_ieeg-recon_m1m2.sh
  ```
- Your can activate your new virtual environment with:
  ```
  conda activate ieeg_recon_m1
  ```

## 3. Install FSL


### Installing FSL
- Go to [FSL's Installation Page](https://fsl.fmrib.ox.ac.uk/fsl/fslwiki/FslInstallation) and follow the instructions.
- Alternatively, you can use the following commands to install FSL:
  ```
  curl -o fslinstaller.py https://fsl.fmrib.ox.ac.uk/fsldownloads/fslconda/releases/fslinstaller.py
  python fslinstaller.py

  ```
- Once installed, add FSL to your PATH with these commands (replace [FSLDIR] with your installation directory, if you just opened the terminal and ran the command,`~/fsl` will be default):
  ```
  export FSLDIR=~/fsl
  export PATH=${FSLDIR}/bin:${PATH}
  echo "export FSLDIR=~/fsl" >> ~/.zshrc
  echo "export PATH=$FSLDIR/bin:$PATH" >> ~/.zshrc
  ```
- If you use `bash`, replace `.zshrc` with `.bashrc`.

## 4. Install ANTs
- Install `homebrew` with the following command:
  ```
  /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
  ```
- Follow the prompt to add `homebrew` to your PATH.
- Install `cmake` with `homebrew`:
  ```
  brew install cmake
  ```
- Install ANTs:
  ```
  mkdir ANTs
  cd ANTs
  curl -o installANTs.sh https://raw.githubusercontent.com/cookpa/antsInstallExample/master/installANTs.sh
  bash installANTs.sh
  ```
- Add ANTs to your PATH (if you installed ANTs outside of your home directory, you might have to modify the script below):
  ```
  export PATH=~/ANTs/install/bin:$PATH
  echo "export PATH=~/ANTs/install/bin:$PATH" >> ~/.zshrc
  ```
- If you use `bash`, replace `.zshrc` with `.bashrc`.

## 5. Install Greedy and C3D
- Install ITK-Snap from [ITK-Snap's Website](http://www.itksnap.org/pmwiki/pmwiki.php?n=Downloads.SNAP4).
- After installing ITK-Snap, go to `Help` > `Install Command Line Tools`.
- Alternatively, you can install Greedy and C3D without ITK-Snap by downloading the binaries from [ITK-Snap's Documentation](http://www.itksnap.org/pmwiki/pmwiki.php?n=Documentation.CommandLine).
- If you already have ITK-SNAP installed, use this command:
  ```
  sudo /Applications/ITK-SNAP.app/Contents/bin/install_cmdl.sh

# Usage

For an overview of the pipeline as well as its usage see here: https://github.com/allucas/ieeg_recon/blob/main/figures/ieeg_recon.pdf

For examples on how to run the electrode reconstruction through the GUI, see here: https://github.com/penn-cnt/ieeg-recon/blob/main/python/docs/Running_iEEG-recon.md

An example dataset can be downloaded from [here](https://drive.google.com/uc?export=download&id=13mbHbU9xpn5XZZenveywD6nxQbgZaJQU)

## Example

Given a subject named `sub-RID0031`, with its data located in a BIDS directory on my desktop that looks as such: 

```
Desktop/BIDS/
├── sub-RID0031/
│   ├── ses-clinical01/
│   │   ├── anat/
│   │   │   └── sub-RID0031_ses-clinical01_acq-3D_space-T00mri_T1w.nii.gz
│   │   ├── ct/
│   │   │   └── sub-RID0031_ses-clinical01_acq-3D_space-T01ct_ct.nii.gz
│   │   └── ieeg/
│   │       └── sub-RID0031_ses-clinical01_space-T01ct_desc-vox_electrodes.txt
│   └── ses-research3T/
│       └── anat/
│           └── sub-RID0031_ses-research3T_acq-3D_space-T00mri_T1w.nii.gz
├── sub-RID0032
└── sub-RID0050
```

Then running module 2 and 3, with built-in AntsPyNet Desikan-Killiany-Tourville Atlas deep learning segmentation, using Greedy for CT-MRI co-registration, and generating an additional MNI registration for visualization purposes, we do:

```
python ieeg_recon.py -d Desktop/BIDS/ -s sub-RID0031 -rs ses-research3T -cs ses-clinical01 -m -1 -gc -apn -mni -r 2 
```

- `d`: specifies the BIDS directory where all the subjects are located
- `s`: specifies the name of the subject
- `rs`: specifies the session name where the reference MRI is located
- `cs`: specifies the session name where the post-implant CT and the electrode coordinates from VoxTool are located
- `m`: specifies the module to run (-1 runs both modules 2 and 3)
- `gc`: specifies to run using only Greedy for module 2
- `apn`: specifies to run AntsPyNet DKT and Atropos segmentation for module 3
- `mni`: specifies to run an additional MNI registration in module 3 for visualization purposes
- `r`: specifies the radius (in mm) of the electrode spheres used to assign regions to each electrode coordinate

NOTE: For now, the only flexibility in the naming convention for the BIDS directory specified above is the subject ID and the session names, please keep rest of the naming stems as specified above. Future updates will make things more flexible!

### Docker Example

Make sure you have Docker installed on your device (https://docs.docker.com/get-docker/) , and make sure that is is currently running. 

Pull the Docker image for `ieeg_recon`:

```
docker pull lucasalf11/ieeg_recon
```

To execute the same procedure as above but in Docker, the following command would be used:

```
docker run -v Desktop/BIDS/:/source_data lucasalf11/ieeg_recon -s sub-RID0031 -d /source_data -cs ses-clinical01 -rs ses-research3T -gc -m -1 -apn -r 2
```

The `-d` flag now points to a directory inside the container called `source_data`, this directory was created for the purpose of mounting the BIDS directory from the local machine with the `-v` flag, as shown above.

### Singularity Example

Make sure Singularity is installed in the machine that will be used to run the analysis.

Pull the singularity image for `ieeg_recon` into the current directory:

```
singularity pull docker://lucasalf11/ieeg_recon:1.0
```

To execute the same procedure as above but in Singularity, the following command would be used:

```
singularity run -B Desktop/BIDS/:/source_data ieeg_recon_1.0.sif -s sub-RID0031 -d /source_data -cs ses-clinical01 -rs ses-research3T -gc -m -1 -apn -r 2
```

This is identical to the Docker command, but the mount flag `-v` is replaced by `-B`


