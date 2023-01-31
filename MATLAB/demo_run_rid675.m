clc
clear
close all
warning off

%% Make ieeg_recon object

subject_rid675 = ieeg_recon;

subject_rid675.preImplantMRI = 'exampleData/sub-RID0675/ses-clinical01/anat/sub-RID0675_ses-clinical01_acq-3D_space-T00mri_T1w.nii.gz';
subject_rid675.postImplantCT = 'exampleData/sub-RID0675/ses-clinical01/ct/sub-RID0675_ses-clinical01_acq-3D_space-T01ct_ct.nii.gz';
subject_rid675.postImplantCT_electrodes = 'exampleData/sub-RID0675/ses-clinical01/ieeg/sub-RID0675_ses-clinical01_space-T01ct_desc-vox_electrodes.txt';
subject_rid675.output = 'exampleData/sub-RID0675/derivatives';
subject_rid675.fslLoc = '/usr/local/fsl/bin';
subject_rid675.itksnap = '/Applications/ITK-SNAP.app/Contents/bin';
subject_rid675.freeSurfer = '/Applications/freesurfer/7.3.2/bin';

%% Run Module 1

subject_rid675.module1;

%% Run Module 2

fileLocations = subject_rid675.module2;

%% Run Module 2 QualityAssurance
snapshot = 1;
subject_rid675.module2_QualityAssuranceFreeSurfer(fileLocations,snapshot);

