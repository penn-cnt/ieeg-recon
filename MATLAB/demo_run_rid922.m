clc
clear
close all

%% Make ieeg_recon object

subject_rid922 = ieeg_recon;

subject_rid922.preImplantMRI = 'exampleData/sub-RID0922/ses-clinical01/anat/sub-RID0922_ses-clinical01_acq-3D_space-T00mri_T1w.nii.gz';
subject_rid922.postImplantCT = 'exampleData/sub-RID0922/ses-clinical01/ct/sub-RID0922_ses-clinical01_acq-3D_space-T01ct_ct.nii.gz';
subject_rid922.postImplantCT_electrodes = 'exampleData/sub-RID0922/ses-clinical01/ieeg/sub-RID0922_ses-clinical01_space-T01ct_desc-vox_electrodes.txt';
subject_rid922.output = 'exampleData/sub-RID0922/derivatives';
subject_rid922.fslLoc = '/usr/local/fsl/bin';
subject_rid922.itksnap = '/Applications/ITK-SNAP.app/Contents/bin';
subject_rid922.freeSurfer = '/Applications/freesurfer/7.3.2/bin';

%% Run Module 1

subject_rid922.module1

%% Run Module 2

fileLocations = subject_rid922.module2;

%% Run Module 2 QualityAssurance
snapshot = 1;
subject_rid922.module2_QualityAssuranceFreeSurfer(fileLocations,snapshot);

%% Run Module 3

atlas = 'exampleData/sub-RID0922/derivatives/freesurfer/mri/aparc+aseg.nii.gz';
lookupTable = 'atlas_lookuptable/desikanKilliany.csv';
 
electrodes = subject_rid922.module3(atlas, lookupTable);
