
.. role:: red
.. role:: blue
.. role:: green
.. role:: pink
.. role:: cyan




Module 2
==========


Purpose: Register Post-implant CT to Pre-Implant MRI scan

Description
----------------

In this module, each subject's CT and MRI images will be linearly aligned (co-registered). Electrode coordinates will be transformed from their native CT into MRI space.

* Input Files: 
   - Post-implant CT  (`ct/…acq-3D_space-T01ct_ct.nii.gz`)
   - Pre-implant MRI  (`anat/…acq-3D_space-T00mri_T1w.nii.gz`)
   - Electrode coordinates in CT space (`ieeg/...space-T01ct_desc-vox_electrodes.txt`)
* Output Files (in `sub-xxx/derivatives/ieeg_recon/module2/`): 
   - Images:
       - sub-xxxx_ses-xxxx_acq-3D_space-T00mri_ct_thresholded.nii.gz
       - sub-xxxx_ses-xxxx_acq-3D_space-T00mri_T1w_electrode_spheres.nii.gz
       - sub-xxxx_ses-xxxx_acq-3D_space-T01ct_T1w.nii.gz
       - sub-xxxx_ses-xxxx_acq-3D_space-T01ct_ct_ras_electrode_spheres.nii.gz
       - sub-xxxx_ses-xxxx_acq-3D_space-T01ct_ct_ras_thresholded.nii.gz
       - sub-xxxx_ses-xxxx_acq-3D_space-T01ct_ct_ras.nii.gz
   - QA Report:
       - sub-xxxx_ses-xxxx_report.html
       - sub-xxxx_ses-xxxx_itksnap_workspace.itksnap
       - sub-xxxx_ses-xxxx_space-T00mri_desc-mm_electrodes_plot.html
       - sub-xxxx_ses-xxxx_T00mri_T01ct_registration.svg
   - Coordinate files:
       - sub-xxxx_ses-xxxx_space-T00mri_desc-mm_electrodes.txt
       - sub-xxxx_ses-xxxx_space-T00mri_desc-vox_electrodes.txt
       - sub-xxxx_ses-xxxx_electrode_names.txt
   - Transformation Matrices:
       - sub-xxxx_ses-xxxx_T00mri_to_T01ct.mat
       - sub-xxxx_ses-xxxx_T01ct_to_T00mri.mat

   


Running Module 2
------------------
First, make sure your input patient data is organized according to the pseudo-BIDS structure outlined in :ref:`Data Setup`. You can also run this tutorial with our `example data <https://www.dropbox.com/sh/ylxc586grm0p7au/AAAs8QQwUo0VQOSweDyj1v_ta?dl=0>`_.


.. tabs::

   .. tab:: Python

      .. code-block:: console

         $ conda activate ieeg_recon
         $ cd python
         $ python ieeg_recon.py -s sub-RID0922 -m 2 -cs ses-clinical101 -rs ses-clinical01 -d ../exampleData -gc

         | Arguments:
         | -s: subject ID
         | -m: Module number
         | -cs: name of session with CT scan
         | -rs: name of session with reference MRI scan
         | -d: path to BIDS directory
         | -gc: (optional, recommended) run with Greedy 

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
         | -gc: (optional, recommended) run with Greedy 


Optional Arguments (recommended)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

* ``-gc`` runs Module 2 with Greedy registration, and is faster than using the default registration method (FLIRT). We recommend using Greedy, but in case of failure, remove the ``-gc`` flag to use FLIRT as a fallback option.



Quality Assessment
--------------------

Module 2 will generate a number of outputs including an html report that can be used to determine whether the coregistration worked properly.

Example: ``sub-RID0922_ses-clinical01_report.html``:


.. raw:: html 

   <iframe src="_static/mod2_full_report.html" style="border:2px solid #adace6;" scrolling="no" height="1600px" width="120%"></iframe>

.. autosummary::
   :toctree: generated

   ieeg-recon
