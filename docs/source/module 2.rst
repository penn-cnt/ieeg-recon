
.. role:: red
.. role:: blue
.. role:: green
.. role:: pink
.. role:: cyan




Module 2
==========


Electrode Mapping of Pre-Implant MRI

Description
----------------

In this module, each subject's CT and MRI images will be linearly aligned (co-registered). Electrode coordinates will be transformed into MRI space. 

* Inputs: 
   - Post-implant CT  (`ct/…acq-3D_space-T01ct_ct.nii.gz`)
   - Pre-implant MRI  (`anat/…acq-3D_space-T00mri_T1w.nii.gz`)
   - Electrode coordinates in CT space (`ieeg/...space-T01ct_desc-vox_electrodes.txt`)
* Outputs: 
   - Electrode coordinates in MRI space (`sub/derivatives/ieeg_recon/module2/`)


Running Module 2
------------------

.. tabs::

   .. tab:: Python

      .. code-block:: console

         $ conda activate ieeg_recon
         $ cd python
         $ python ieeg_recon.py -s sub-RID0922 -m 2 -cs ses-clinical101 -rs ses-clinical01 -d ../exampleData

         | Arguments:
         | -s: subject ID
         | -m: Module number
         | -cs: name of session with CT scan
         | -rs: name of session with reference MRI scan
         | -d: path to BIDS directory

   .. tab:: Matlab

      .. code-block:: Matlab

        % Set up
        subID = 'sub-RID0922';          % subject ID
        ct_session = 'ses-clinical01';  % name of session with CT scan
        mri_session = 'ses-clinical01'; % name of session with reference MRI scan
        BIDS_dir = '../exampleData';    % path to BIDS directory

        subject_rid922 = ieeg_recon(subID, ct_session, mri_session, BIDS_dir);

        % Run Module 2
        fileLocations = subject_rid0922.module2;

   .. tab:: Docker

      .. code-block:: console
         
         $ ieeg_recon -s sub-RID0922 -m 2 -cs ses-clinical101 -rs ses-clinical01 -d ../exampleData

         | Arguments:
         | -s: subject ID
         | -m: Module number
         | -cs: name of session with CT scan
         | -rs: name of session with reference MRI scan
         | -d: path to BIDS directory






      
Quality Control
-----------------



.. autosummary::
   :toctree: generated

   ieeg-recon
