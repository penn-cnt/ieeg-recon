Module 3
==========

Purpose: Assign electrodes to brain regions of interest (ROIs)

Description
--------------


Module 3 assigns electrodes in the pre-implant MRI space to a specific brain region of interest (ROI). The brain can be subdivided into contiguous regions of interest (ROIs) based on the structural or functional similarity within each region. Users can input any brain atlas (e.g. AAL atlas, Lausanne Atlas, DKT Atlas) to Module 3, and recieve the ROI assignment for each electroe as an output. 

* Inputs:
   - Post-implant CT  (`ct/…acq-3D_space-T01ct_ct.nii.gz`)
   - Pre-implant MRI  (`anat/…acq-3D_space-T00mri_T1w.nii.gz`)
   - Electrode coordinates in CT space (`ieeg/...space-T01ct_desc-vox_electrodes.txt`)
* Outputs:

Running Module 3 with AntSpyNet
--------------------------------

Make sure your input patient data is organized according to the pseudo-BIDS structure outlined in :ref:`Data Setup`. You can also run the tutorial with our `example data <https://www.dropbox.com/sh/ylxc586grm0p7au/AAAs8QQwUo0VQOSweDyj1v_ta?dl=0>`_. The code below demonstrates how to run Module 3 

.. tabs::

   .. tab:: Python

      .. code-block:: console

         $ conda activate ieeg_recon
         $ cd python
         $ python ieeg_recon.py -s sub-RID0922 -m 3 -cs ses-clinical01 -rs ses-clinical01 -d ../exampleData -r 2 -apn

         | Arguments:
         | -s: subject ID
         | -m: Module number
         | -cs: name of session with CT scan
         | -rs: name of session with reference MRI scan
         | -d: path to BIDS directory
         | -r: radius (in mm) of the electrode spheres used to assign regions to each electrode
         | -apn: run AntsPyNet DKT and Atropos segmentation

   .. tab:: Matlab

      .. code-block:: Matlab

        % Set up
        subID = 'sub-RID0922';          % subject ID
        ct_session = 'ses-clinical01';  % name of session with CT scan
        mri_session = 'ses-clinical01'; % name of session with reference MRI scan
        BIDS_dir = '../exampleData';    % path to BIDS directory

        subject_rid922 = ieeg_recon(subID, ct_session, mri_session, BIDS_dir);

        % Run Module 3
        fileLocations = subject_rid0922.module3;

   .. tab:: Docker

      .. code-block:: console
         
         $ ieeg_recon -s sub-RID0922 -m 3 -cs ses-clinical101 -rs ses-clinical01 -d ../exampleData -r 2 -apn

         | Arguments:
         | -s: subject ID
         | -m: Module number
         | -cs: name of session with CT scan
         | -rs: name of session with reference MRI scan
         | -d: path to BIDS directory
         | -r: radius
         | -apn: run AntsPyNet DKT and Atropos segmentation


Running Module 3 with Freesurfer Atlas
--------------------------------------


* Replace ``-apn`` with the following to specify a particular freesurfer atlas and parcellation labels:
    * ``-a /path/to/NIFTI``
    * ``-an /path/to/atlas/segmentation``
    * ``-lut /path/to/roi_csv``



Optional Arguments
-------------------------

* ``-mni`` run an additional MNI registration for visualization purposes

Example for running Module 3 using Greedy, running AntsPyNet DKT segmentation, generating MNI ROI assignments, and using a radius of 2 mm. 

.. tabs::

   .. tab:: Python

      .. code-block:: console

         $ conda activate ieeg_recon
         $ cd python
         $ python ieeg_recon.py -s sub-RID0922 -m 3 -cs ses-clinical101 -rs ses-clinical01 -d ../exampleData -gc -apn -mni -r 2


   .. tab:: Matlab

      .. code-block:: Matlab

        % Set up
        subID = 'sub-RID0922';          % subject ID
        ct_session = 'ses-clinical01';  % name of session with CT scan
        mri_session = 'ses-clinical01'; % name of session with reference MRI scan
        BIDS_dir = '../exampleData';    % path to BIDS directory

        subject_rid922 = ieeg_recon(subID, ct_session, mri_session, BIDS_dir);

        % Run Module 3
        fileLocations = subject_rid0922.module3;

   .. tab:: Docker

      .. code-block:: console
         
         $ ieeg_recon -s sub-RID0922 -m 3 -cs ses-clinical101 -rs ses-clinical01 -d ../exampleData

         | Arguments:
         | -s: subject ID
         | -m: Module number
         | -cs: name of session with CT scan
         | -rs: name of session with reference MRI scan
         | -d: path to BIDS directory

Quality Assessment
--------------


Example
--------------

.. autosummary::
   :toctree: generated

   ieeg-recon
