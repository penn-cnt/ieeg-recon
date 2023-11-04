
.. role:: red
.. role:: blue
.. role:: green
.. role:: pink
.. role:: cyan


.. _Module 2:

Module 2
==========


Purpose: Register Post-implant CT to pre-Implant MRI scan

Description
----------------

In this module, each subject's CT and MRI images will be linearly aligned (co-registered). Electrode coordinates will be transformed from their native CT into MRI space.

* Input Files: 
   - Pre-implant MRI: anat/:blue:`sub-xxxx_`:red:`ses-yy`\_acq-3D\_\ :green:`space-T00mri`\_\ :pink:`T1w`.nii.gz
   - Post-implant CT: ct/:blue:`sub-xxxx_`:red:`ses-yy`\_acq-3D\_\ :green:`space-T01ct`\_\ :pink:`ct`.nii.gz
   - Electrode coordinates in CT space: ieeg/:blue:`sub-xxxx_`:red:`ses-yy`\_\ :green:`space-T01ct`\_ :cyan:`desc-vox`\_\ :pink:`electrodes`.txt
  
* Output Files (in `sub-xxx/derivatives/ieeg_recon/module2/`): 
   - Quality Report:
       - :blue:`sub-xxxx_`:red:`ses-yy`\_report.html
       - :blue:`sub-xxxx_`:red:`ses-yy`\_itksnap_workspace.itksnap
       - :blue:`sub-xxxx_`:red:`ses-yy`\_\ :green:`space-T00mri`\_desc-mm_electrodes_plot.html
       - :blue:`sub-xxxx_`:red:`ses-yy`\_T00mri_T01ct_registration.svg
       - :blue:`sub-xxxx_`:red:`ses-yy`\_\ :green:`space-T01ct`\_desc-vox_electrodes_itk_snap_labels.txt
   - Image Files:
       - :blue:`sub-xxxx_`:red:`ses-yy`\_acq-3D\_\ :green:`space-T00mri`\_ct_thresholded.nii.gz
       - :blue:`sub-xxxx_`:red:`ses-yy`\_acq-3D\_\ :green:`space-T00mri`\_T1w_electrode_spheres.nii.gz
       - :blue:`sub-xxxx_`:red:`ses-yy`\_acq-3D\_\ :green:`space-T01ct`\_T1w.nii.gz
       - :blue:`sub-xxxx_`:red:`ses-yy`\_acq-3D\_\ :green:`space-T01ct`\_ct_ras_electrode_spheres.nii.gz
       - :blue:`sub-xxxx_`:red:`ses-yy`\_acq-3D\_\ :green:`space-T01ct`\_ct_ras_thresholded.nii.gz
       - :blue:`sub-xxxx_`:red:`ses-yy`\_acq-3D\_\ :green:`space-T01ct`\_ct_ras.nii.gz
   - Coordinate files:
       - :blue:`sub-xxxx_`:red:`ses-yy`\_\ :green:`space-T00mri`\_desc-mm_electrodes.txt
       - :blue:`sub-xxxx_`:red:`ses-yy`\_\ :green:`space-T00mri`\_desc-vox_electrodes.txt
       - :blue:`sub-xxxx_`:red:`ses-yy`\_electrode_names.txt
       - :blue:`sub-xxxx_`:red:`ses-yy`\_orig_coords_in_mm.txt
   - Transformation Matrices:
       - :blue:`sub-xxxx_`:red:`ses-yy`\_T00mri_to_T01ct_fsl.mat
       - :blue:`sub-xxxx_`:red:`ses-yy`\_T01ct_to_T00mri_fsl.mat
       - :blue:`sub-xxxx_`:red:`ses-yy`\_T00mri_to_T01ct_greedy.mat (if using Greedy)

   


Running Module 2
------------------
If running from the iEEG-recon Application, follow the :ref:`Running the App` instructions. 

If running from the command line, first make sure your input patient data is organized according to the pseudo-BIDS structure outlined in :ref:`Data Setup`.
You can also run this tutorial with our `example data <https://www.dropbox.com/sh/ylxc586grm0p7au/AAAs8QQwUo0VQOSweDyj1v_ta?dl=0>`_.

The code below demonstrates how to run Module 2 from the command line. 

.. tabs::

   .. tab:: Docker

      .. code-block:: console
         
         $ docker run -v absolute/path/to/exampleData:/source_data lucasalf11/ieeg_recon -s sub-RID0922 -m 2 -cs ses-clinical01 -rs ses-clinical01 -d /source_data

         | Arguments:
         | -s: subject ID
         | -m: Module number
         | -cs: name of session with CT scan
         | -rs: name of session with reference MRI scan
         | -d: path to BIDS directory
         | -gc: (optional, recommended) run with Greedy 

   .. tab:: Python

      .. code-block:: console

         $ conda activate ieeg_recon
         $ cd python
         $ python ieeg_recon.py -s sub-RID0922 -m 2 -cs ses-clinical101 -rs ses-clinical01 -d absolute/path/to/exampleData -gc

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


Optional Arguments (recommended)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

* ``-gc`` runs Module 2 with Greedy registration, and is faster than using the default registration method (FLIRT). We recommend using Greedy, but in case of failure, remove the ``-gc`` flag to use FLIRT as a fallback option.



Module 2 Outputs
-----------------

Quality Report
^^^^^^^^^^^^^^^^^
Module 2 will generate a number of outputs including an html report that can be used to determine whether the coregistration worked properly.

Example: ``sub-RID0922_ses-clinical01_report.html``:


.. raw:: html 

   <iframe src="_static/mod2_full_report.html" style="border:2px solid #adace6;" scrolling="no" height="1600px" width="120%"></iframe>


Image Files
^^^^^^^^^^^^^^

Module 2 generates a number of transformed image files

- `...acq-3D_space-T00mri_ct_thresholded.nii.gz`: Original CT scan (left) transformed to MRI (T00) space with an intensity threshold applied (right):
  
  .. image:: images/mod2_out_threshct.png
    :width: 300
    :alt: Single contact selected
    :align: center

- `...acq-3D_space-T00mri_T1w_electrode_spheres.nii.gz`: Spheres marking electrodes in MRI (T00) space. 
- `...acq-3D_space-T01ct_T1w.nii.gz`: Original MRI transformed to CT (T01) space. 

The next three outputs are the original CT scan, thresholded CT scan, and electrode spheres in native T01 CT space, transformed to the RAS (Right, Anterior, Superior) coordinate system. The units of RAS are voxels, and the voxels are indexed from left to right, posterior to anterior, and inferior to superior, respectively: 

.. - :blue:`sub-xxxx_`:red:`ses_yy`\_acq-3D_\ :green:`space-T01ct`\_ct_ras_electrode_spheres.nii.gz
.. - :blue:`sub-xxxx_`:red:`ses_yy`\_acq-3D_\ :green:`space-T01ct`\_ct_ras_thresholded.nii.gz
.. - :blue:`sub-xxxx_`:red:`ses_yy`\_acq-3D_\ :green:`space-T01ct`\_ct_ras.nii.gz

Coordinate files
^^^^^^^^^^^^^^^^^
- :blue:`sub-xxxx_`:red:`ses_yy`\_\ :green:`space-T00mri`\_desc-mm_electrodes.txt
- :blue:`sub-xxxx_`:red:`ses_yy`\_\ :green:`space-T00mri`\_desc-vox_electrodes.txt
- :blue:`sub-xxxx_`:red:`ses_yy`\_electrode_names.txt
- :blue:`sub-xxxx_`:red:`ses_yy`\_orig_coords_in_mm.txt
  
Transformation Matrices
^^^^^^^^^^^^^^^^^^^^^^^^^
- :blue:`sub-xxxx_`:red:`ses_yy`\_T00mri_to_T01ct_fsl.mat
- :blue:`sub-xxxx_`:red:`ses_yy`\_T01ct_to_T00mri_fsl.mat
- :blue:`sub-xxxx_`:red:`ses_yy`\_T00mri_to_T01ct_greedy.mat (if using Greedy)


.. autosummary::
   :toctree: generated

   ieeg-recon
