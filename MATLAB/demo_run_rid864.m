clc
clear
close all

%% Make ieeg_recon object

subID = 'sub-RID0864';
ct_session = 'ses-clinical01';
mri_session = 'ses-clinical01';
BIDS_dir = '../exampleData';

subject_rid864 = ieeg_recon(subID, ct_session, mri_session, BIDS_dir);
subject_rid864.freeSurfer = '/Applications/freesurfer/7.3.2/bin';

%% Run Module 1

subject_rid864.module1

%% Run Module 2

fileLocations = subject_rid864.module2;

%% Run Module 2 QualityAssurance
snapshot = 1;
subject_rid864.module2_QualityAssuranceFreeSurfer(fileLocations,snapshot);

