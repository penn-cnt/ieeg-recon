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

## Python 

For a standalone python installation, we recommend you have Anaconda (https://www.anaconda.com/products/distribution) with at least Python 3.7

With Anaconda and Python installed, clone the repository, and open a terminal window in the directory where the repository was cloned into. Type the following command:

```
conda env create -f ieeg_recon_config.yml
```

This will create a conda virtual environment called `ieeg_recon` that contains all of the dependencies. To activate the environment type:

```
conda activate ieeg_recon
```
#### M1/M2 Apple Devices
If you have an Apple Silicon chip on your machine (M1/M2), after cloning the repository and with Anaconda installed, run the script `install_ieeg-recon_m1m2.sh` while inside the repository directory by doing:

```
bash install_ieeg-recon_m1m2.sh
```
This will automatically create a virtual environment called `ieeg_recon_m1`. After running the above script, activate the environment by typing:

```
conda activate ieeg_recon_m1
```

### Installing FSL

When using the standalone Python version, FSL must also be installed (https://fsl.fmrib.ox.ac.uk/fsl/fslwiki/FslInstallation). Make sure the `$FSLDIR` variable is properly defined and FSL is sourced before running the `ieeg_recon` script.

For MACs, the following set of commands should work for installing FSL:

```
curl -o fslinstaller.py https://fsl.fmrib.ox.ac.uk/fsldownloads/fslconda/releases/fslinstaller.py
echo -e "\n\n\n\n" | python fslinstaller.py
export FSLDIR=/usr/local/fsl
export PATH=${FSLDIR}/bin:${PATH}
echo "export FSLDIR=/usr/local/fsl" >> ~/.zshrc
echo "export PATH=\$FSLDIR/bin:\$PATH" >> ~/.zshrc
```
If your device uses `bash` instead of `zsh`, replace the `.zshrc` in the two commands with `.bashrc`

### Installing ANTs

To install ANTs, the following commands should work for MacOS:

```
# install homebrew
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

Installing `cmake`:

```
# install cmake
brew install cmake
```

Installing ANTs:

```
# install ANTs
curl -o installANTs.sh https://raw.githubusercontent.com/cookpa/antsInstallExample/master/installANTs.sh
bash installANTs.sh
export PATH=/app/install/bin:$PATH
echo "export PATH=/app/install/bin:\$PATH" >> ~/.zshrc
```

If your device uses `bash` instead of `zsh`, replace the `.zshrc` in the last command with `.bashrc`

### Installing Greedy and C3D

Some registrations between the MRI and CT could be improved by an extra registration step using Greedy (https://sites.google.com/view/greedyreg/about), which implements similar procedures as ANTs. 

The `-g` flag, when running module 2 applies an extra, optional, rigid registration after FLIRT. The `-gc` flag, applies Greedy registration without applying FLIRT first. This approach is often faster and more accurate than doing FLIRT, therefore it should be used when possible. 

Both Greedy and C3D need to be installed for this to work. They can both easily be installed through ITK-Snap (http://www.itksnap.org/pmwiki/pmwiki.php?n=Main.HomePage) by going to Help > Install Command Line Tools. If you would like to install these packages without ITK-Snap, the binaries can be found here: http://www.itksnap.org/pmwiki/pmwiki.php?n=Documentation.CommandLine.

If you already have ITK-SNAP installed on your MAC, you can simply use the following command in the terminal to get these tools:

```
sudo /Applications/ITK-SNAP.app/Contents/bin/install_cmdl.sh 
```
# Usage

For an overview of the pipeline as well as its usage see here: https://github.com/allucas/ieeg_recon/blob/main/figures/ieeg_recon.pdf

For examples on how to run the electrode reconstruction through the GUI, see here: https://github.com/penn-cnt/ieeg-recon/blob/main/python/docs/Running_iEEG-recon.md

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
singularity pull docker://lucasalf11/ieeg_recon
```

To execute the same procedure as above but in Singularity, the following command would be used:

```
singularity run -B Desktop/BIDS/:/source_data lucasalf11/ieeg_recon -s sub-RID0031 -d /source_data -cs ses-clinical01 -rs ses-research3T -gc -m -1 -apn -r 2
```

This is identical to the Docker command, but the mount flag `-v` is replaced by `-B`


