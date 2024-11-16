# iEEG Implant Reconstruction Pipeline

A MATLAB-based pipeline for reconstructing intracranial EEG (iEEG) electrode locations from post-implant CT and pre-implant MRI scans.

## Overview

This pipeline provides tools for:
- Extracting electrode coordinates from post-implant CT scans
- Co-registering CT and MRI images
- Mapping electrodes to anatomical regions
- Quality assurance visualization

## Prerequisites

### Required Software
- MATLAB (version 2019b or later recommended)
- FSL (FMRIB Software Library)
- ITK-SNAP
- FreeSurfer

### System Requirements
- Operating System: Linux/Unix (recommended), macOS, or Windows with Unix subsystem
- RAM: 8GB minimum, 16GB recommended
- Storage: At least 10GB free space for processing

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/username/iEEG_implant_reconstruction.git
   ```

2. Add FSL to your shell profile:
   ```bash
   export FSLDIR=/path/to/fsl
   source ${FSLDIR}/etc/fslconf/fsl.sh
   export PATH=${FSLDIR}/bin:${PATH}
   ```

3. Configure paths in `config_iEEGrecon.m`

## Configuration Example

After cloning the repository and setting up the required software, you need to configure the paths in `config_iEEGrecon.m`. Below is an example configuration:

```matlab
%% Set external library in path

addpath(genpath('/path/to/your/dependencies'))

%% FSL Setup

setenv('FSLDIR', '/path/to/fsl');
setenv('FSLOUTPUTTYPE', 'NIFTI_GZ');
fsldir = getenv('FSLDIR');
fsldirmpath = sprintf('%s/etc/matlab', fsldir);
path(path, fsldirmpath);
clear fsldir fsldirmpath;

%% ITK Snap Setup

setenv('ITKSNAPDIR', '/path/to/ITK-SNAP');
itksnapdir = getenv('ITKSNAPDIR');
itksnapmpath = sprintf('%s', itksnapdir);
path(path, itksnapmpath);
clear itksnapdir itksnapmpath;

%% Freesurfer setup

setenv('FREESURFER_HOME', '/path/to/freesurfer');
setenv('SUBJECTS_DIR', '/path/to/your/subjects_dir');
FREESURFER_HOME = getenv('FREESURFER_HOME');
freesurferdirmpath = sprintf('%s/SetUpFreeSurfer.sh', FREESURFER_HOME);
system(['sh ' freesurferdirmpath], '-echo');
clear freesurferdirmpath FREESURFER_HOME;
```

Make sure to replace `/path/to/your/dependencies`, `/path/to/fsl`, `/path/to/ITK-SNAP`, `/path/to/freesurfer`, and `/path/to/your/subjects_dir` with the actual paths on your system.


## Usage

### Module 1: Electrode Coordinate Export
This module extracts electrode coordinates from post-implant CT scans in both voxel and native space.

```matlab
% Initialize the pipeline object
obj = iEEGReconPipeline();

% Run Module 1
obj.module1();
```

### Module 2: Image Registration
This module performs CT-MRI co-registration. You can choose between:
- Greedy registration with image centering (`'gc'`)
- FLIRT registration fine-tuned with greedy (`'g'`)

```matlab
% Run Module 2 with greedy registration and no visualization
fileLocations = obj.module2('gc', false);
```

### Module 3: ROI Mapping
This module maps electrodes to anatomical regions using an atlas.

```matlab
% Run Module 3
obj.module3();
```

### Notes
- Ensure that all input files are correctly placed in the expected directories before running the modules.
- Adjust the parameters as needed for your specific dataset and analysis requirements.


## Data Structure

### Input Files
- **Pre-implant MRI scan (T1-weighted):** Required for anatomical reference.
- **Post-implant CT scan:** Used to locate electrode positions.
- **Electrode coordinates file:** Contains initial electrode positions.
- **Atlas file (optional):** Used for mapping electrodes to anatomical regions.
- **Lookup table (optional):** Provides additional mapping information.

### Output Structure
The pipeline generates the following output files organized by module:

```
ieeg_recon/
├── module1/
│   ├── electrode_names.txt       # List of electrode names
│   ├── electrodes_inCTvox.txt    # Electrode coordinates in CT voxel space
│   └── electrodes_inCTmm.txt     # Electrode coordinates in CT millimeter space
├── module2/
│   ├── ct_to_mri.nii.gz          # Registered CT to MRI image
│   ├── electrodes_inMRI.nii.gz   # Electrode positions in MRI space
│   └── QA_registration_.png      # Quality assurance image for registration
└── module3/
    └── electrodes2ROI.csv        # Mapping of electrodes to regions of interest
```

### Notes
- Ensure that input files are correctly formatted and placed in the expected directories before running the pipeline.
- The output files are organized by module to facilitate easy access and analysis.

## Example Data

Example data is available for testing: [download](https://www.dropbox.com/sh/ylxc586grm0p7au/AAAs8QQwUo0VQOSweDyj1v_ta?dl=0)

## Quality Assurance

The pipeline includes built-in quality assurance tools:
- Registration quality checks
- Electrode placement verification
- Visual inspection tools

## Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Citation

If you use this software in your research, please cite:

> **Lucas A, Scheid BH, Pattnaik AR, Gallagher R, Mojena M, Tranquille A, Prager B, Gleichgerrcht E, Gong R, Litt B, Davis KA, Das S, Stein JM, Sinha N. iEEG-recon: A fast and scalable pipeline for accurate reconstruction of intracranial electrodes and implantable devices. Epilepsia. 2024 Mar;65(3):817-829. doi: 10.1111/epi.17863. Epub 2024 Jan 10. PMID: 38148517; PMCID: PMC10948311.**

## Support

For bug reports and feature requests, please use the [GitHub Issue Tracker](https://github.com/username/iEEG_implant_reconstruction/issues).
