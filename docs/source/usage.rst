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
   * 
* Greedy and C3D 
   * Either: Install `ITK Snap <http://www.itksnap.org/pmwiki/pmwiki.php?n=Main.HomePage>`_ >= . Open ITK Snap and click on `Help` > `Install Command Line Tools`.
   * Or: see `compile from source <http://www.itksnap.org/pmwiki/pmwiki.php?n=Documentation.CommandLine>`_ instructions to install without ITK-Snap. 


.. tabs::

   .. tab:: Python

      * `Anaconda <https://www.anaconda.com/products/distribution>`_

 .. tab:: Matlab

      * Check that $FSLDIR is set and that the following lines are added to ~/Documents/MATLAB/startup.m file:
      
      .. code-block:: matlab

       % FSL Setup
        setenv( 'FSLDIR', '/path/to/fsl/bin' );
        setenv('FSLOUTPUTTYPE', 'NIFTI_GZ');
        fsldir = getenv('FSLDIR');
        fsldirmpath = sprintf('%s/etc/matlab',fsldir);
        path(path, fsldirmpath);
        clear fsldir fsldirmpath;

        % ITK snap Setup
        setenv('ITKSNAPDIR', '/Applications/ITK-SNAP.app/Contents/bin');
        itksnapdir = getenv('ITKSNAPDIR');
        itksnapmpath = sprintf('%s',itksnapdir);
        path(path,itksnapmpath)
        clear itksnapdir itksnapmpath;


.. _install:

Installation
------------

To use IEEG-recon, first clone the repository:

.. code-block:: console

   $ git clone git@github.com:penn-cnt/ieeg-recon.git


.. tabs::

   .. tab:: Python

      * Create conda environment from dependancies 

      .. code-block:: py

         $ conda env create -f python/ieeg_recon_config.yml 

   .. tab:: Matlab

      Check that $FSLDIR is set and that the following lines are added to ~/Documents/MATLAB/startup.m file:
      
      .. code-block:: matlab

         % FSL Setup
        setenv( 'FSLDIR', '/path/to/your/fsl/installation' );
        setenv('FSLOUTPUTTYPE', 'NIFTI_GZ');
        fsldir = getenv('FSLDIR');
        fsldirmpath = sprintf('%s/etc/matlab',fsldir);
        path(path, fsldirmpath);
        clear fsldir fsldirmpath;


Folder Setup
--------------

CT scans, MRI scans, and coordinate files should be arranged in BIDS format with the following naming conventions. Example for subject `sub-RID0031` is shown: 

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


.. autosummary::
   :toctree: generated

   ieeg-recon


