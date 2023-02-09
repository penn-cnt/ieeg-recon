clc
clear
close all
warning off

% Download Example Data: 
% https://www.dropbox.com/sh/ylxc586grm0p7au/AAAs8QQwUo0VQOSweDyj1v_ta?dl=0

%% Make ieeg_recon object

subID = 'sub-RID0675';
ct_session = 'ses-clinical01';
mri_session = 'ses-clinical01';
BIDS_dir = '../exampleData';

subject_rid675 = ieeg_recon(subID, ct_session, mri_session, BIDS_dir);

% Add path to library executables:
subject_rid675.freeSurfer = '/Applications/freesurfer/7.3.2/bin';


%% Run Module 1

subject_rid675.module1;

%% Run Module 2

fileLocations = subject_rid675.module2;

%% Run Module 2 QualityAssurance
snapshot = 1;
subject_rid675.module2_QualityAssuranceFreeSurfer(fileLocations,snapshot);

