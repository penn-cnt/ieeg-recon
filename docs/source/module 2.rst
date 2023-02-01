Module 2
==========


Electrode Mapping ot Pre-Implant MRI

* Inputs: 
   - Post-implant CT
   - Pre-implant MRI
   - Electrode coordinates in CT space
* Output: 
   - Electrode coordinates in MRI space


Running Module 2
------------------


| subject: sub-RID0031
| clinical session: ses-clinical101
| research session: ses-research3T  
| BIDS folder: /BIDS  

.. tabs:: lang

   .. code-tab:: py

      ieeg_recon -s sub-RID0031 -m 2 -cs ses-clinical101 -rs ses-research3T -d /BIDS

   .. code-tab:: matlab

      subject_rid0031 = ieeg_recon;


      % set up
      subject_rid0031.preImplantMRI = 'exampleData/sub-RID0031/ses-clinical01/anat/sub-RID0031_ses-clinical01_acq-3D_space-T00mri_T1w.nii.gz';
      subject_rid0031.postImplantCT = 'exampleData/sub-RID0031/ses-clinical01/ct/sub-RID0031_ses-clinical01_acq-3D_space-T01ct_ct.nii.gz';
      subject_rid0031.postImplantCT_electrodes = 'exampleData/sub-RID0031/ses-clinical01/ieeg/sub-RID0031_ses-clinical01_space-T01ct_desc-vox_electrodes.txt';
      subject_rid0031.output = 'exampleData/sub-RID0031/derivatives';
      subject_rid0031.fslLoc = '/usr/local/fsl/bin';
      subject_rid0031.itksnap = '/Applications/ITK-SNAP.app/Contents/bin';
      subject_rid0031.freeSurfer = '/Applications/freesurfer/7.3.2/bin';

      fileLocations = subject_rid0031.module2;

      



.. autosummary::
   :toctree: generated

   ieeg-recon
