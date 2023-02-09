clc
clear
close all

%% Make ieeg_recon object


subID = 'sub-RID0922';
ct_session = 'ses-clinical01';
mri_session = 'ses-clinical01';
BIDS_dir = '../exampleData';

subject_rid922 = ieeg_recon(subID, ct_session, mri_session, BIDS_dir);
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
