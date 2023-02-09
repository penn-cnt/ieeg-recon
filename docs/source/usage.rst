.. role:: red
.. role:: blue
.. role:: green
.. role:: pink
.. role:: cyan


Usage
=====


Requirements
-------------

* `FSL <https://fsl.fmrib.ox.ac.uk/fsl/fslwiki/FslInstallation>`_ >= 3.8.0 

   *  Ensure that FSLDIR environment variable is set on your terminal path. 
* Greedy and C3D: 

   *  Install `ITK Snap <http://www.itksnap.org/pmwiki/pmwiki.php?n=Main.HomePage>`_ >= V3.2. Open ITK Snap and click on `Help` > `Install Command Line Tools`.
   *  Or: see `compile from source <http://www.itksnap.org/pmwiki/pmwiki.php?n=Documentation.CommandLine>`_ instructions to install without ITK-Snap. 
 
*  `Anaconda <https://www.anaconda.com/products/distribution>`_ 
*  `MATLAB <https://matlab.mathworks.com>`_ >=2020a (only if using MATLAB tools)


.. _install:

Installation
------------

To use IEEG-recon, first clone the repository:

.. code-block:: console

   $ git clone git@github.com:penn-cnt/ieeg-recon.git


.. tabs::

   .. tab:: Python

      Create conda environment from dependancies: 

      .. code-block:: console

         $ cd python
         $ conda env create -f ieeg_recon_config.yml 

   .. tab:: MATLAB

      Set the FSLDIR and ITKSNAPDIR environment variables in ``~/../MATLAB/startup.m``

      .. note :: 

         You you may need to change the library paths
      
      .. code-block:: MATLAB

         %% in MATLAB/startup.m
         
         % Set FSLDIR to FSL install location
        setenv( 'FSLDIR', '/usr/local/fsl' );
        setenv('FSLOUTPUTTYPE', 'NIFTI_GZ');
        fsldir = getenv('FSLDIR');
        fsldirmpath = sprintf('%s/etc/matlab',fsldir);
        path(path, fsldirmpath);
        clear fsldir fsldirmpath;

         % Set ITKSNAPDIR to ITK-Snap install location
        setenv('ITKSNAPDIR', '/Applications/ITK-SNAP.app/Contents/bin');
        itksnapdir = getenv('ITKSNAPDIR');
        itksnapmpath = sprintf('%s',itksnapdir);
        path(path,itksnapmpath)
        clear itksnapdir itksnapmpath;



Data Setup
------------------

| CT scans, MRI scans, and coordinate files should be arranged in BIDS format with the following naming conventions. 
| Example for subject `sub-RID0031` is shown: 

.. code-block:: console

   BIDS/
   ├── sub-RID0031/
   │   ├── ses-clinical01/
   │   │   ├── anat/
   │   │   │   └── sub-RID0031_ses-clinical01_acq-3D_space-T00mri_T1w.nii.gz
   │   │   ├── ct/
   │   │   │   └── sub-RID0031_ses-clinical01_acq-3D_space-T01ct_ct.nii.gz
   │   │   └── ieeg/
   │   │       └── sub-RID0031_ses-clinical01_space-T01ct_desc-vox_electrodes.txt
   │   └── ses-research3T/
   │       └── anat/
   │           └── sub-RID0031_ses-research3T_acq-3D_space-T00mri_T1w.nii.gz
   ├── sub-RID0032
   └── sub-RID0050


Data used for our examples can be `downloaded here <https://www.dropbox.com/sh/ylxc586grm0p7au/AAAs8QQwUo0VQOSweDyj1v_ta?dl=0>`_.


.. autosummary::
   :toctree: generated

   ieeg-recon


