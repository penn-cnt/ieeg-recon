clc
clear
close all

%% Make ieeg_recon object

subject_rid864 = ieeg_recon;

subject_rid864.preImplantMRI = 'exampleData/sub-RID0864/ses-clinical01/anat/sub-RID0864_ses-clinical01_acq-3D_space-T00mri_T1w.nii.gz';
subject_rid864.postImplantCT = 'exampleData/sub-RID0864/ses-clinical01/ct/sub-RID0864_ses-clinical01_acq-3D_space-T01ct_ct.nii.gz';
subject_rid864.postImplantCT_electrodes = 'exampleData/sub-RID0864/ses-clinical01/ieeg/sub-RID0864_ses-clinical01_space-T01ct_desc-vox_electrodes.txt';
subject_rid864.output = 'exampleData/sub-RID0864/derivatives';
subject_rid864.fslLoc = '/usr/local/fsl/bin';
subject_rid864.itksnap = '/Applications/ITK-SNAP.app/Contents/bin';
subject_rid864.freeSurfer = '/Applications/freesurfer/7.3.2/bin';

%% Run Module 1

subject_rid864.module1

%% Run Module 2

fileLocations = subject_rid864.module2;

%% Run Module 2 QualityAssurance
snapshot = 1;
subject_rid864.module2_QualityAssuranceFreeSurfer(fileLocations,snapshot);

