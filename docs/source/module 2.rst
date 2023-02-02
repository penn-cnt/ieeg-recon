
.. role:: red
.. role:: blue
.. role:: green
.. role:: pink
.. role:: cyan




Module 2
==========


Electrode Mapping of Pre-Implant MRI

Description
------------------

In this module, each subject's CT and MRI images will be linearly aligned (co-registered). Electrode coordinates will be transformed into MRI space. 

* Inputs: 
   - Post-implant CT
   - Pre-implant MRI
   - Electrode coordinates in CT space
* Output: 
   - Electrode coordinates in MRI space


Running Module 2
------------------

Example:

| BIDS folder: /BIDS  
| subject: :blue:`sub-RID0031`
| clinical session: :red:`ses-clinical101`
| research session: :red:`ses-research3T`  


.. tabs::

   .. tab:: Python

      .. code-block:: py

         ieeg_recon -s sub-RID0031 -m 2 -cs ses-clinical101 -rs ses-research3T -d /BIDS

      | Arguments:
      | -s: subject ID
      | -m: Module number
      | -cs: name of clinical session
      | -rs: name of session with reference MRI
      | -d: path to BIDS directory


   .. code-tab:: matlab

      subject_rid0031 = ieeg_recon;


      % set up
      subject_rid0031.preImplantMRI = 'BIDS/sub-RID0031/ses-clinical01/anat/sub-RID0031_ses-clinical01_acq-3D_space-T00mri_T1w.nii.gz';
      subject_rid0031.postImplantCT = 'BIDS/sub-RID0031/ses-clinical01/ct/sub-RID0031_ses-clinical01_acq-3D_space-T01ct_ct.nii.gz';
      subject_rid0031.postImplantCT_electrodes = 'BIDS/sub-RID0031/ses-clinical01/ieeg/sub-RID0031_ses-clinical01_space-T01ct_desc-vox_electrodes.txt';
      subject_rid0031.output = 'BIDS/sub-RID0031/derivatives';
      subject_rid0031.fslLoc = '/usr/local/fsl/bin';
      subject_rid0031.itksnap = '/Applications/ITK-SNAP.app/Contents/bin';
      subject_rid0031.freeSurfer = '/Applications/freesurfer/7.3.2/bin';

      % Run Module 2
      fileLocations = subject_rid0031.module2;


      
Quality Control
-----------------



.. autosummary::
   :toctree: generated

   ieeg-recon
