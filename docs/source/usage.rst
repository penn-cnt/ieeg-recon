.. role:: red
.. role:: blue
.. role:: green
.. role:: pink
.. role:: cyan


Usage
=====

.. _install:

Installation
------------

To use IEEG-recon, first clone the repository:

.. code-block:: console

   $ git clone git@github.com:penn-cnt/ieeg-recon.git


Python Installation
---------------------

* Create conda environment from dependancies 

.. code-block:: console

   $ conda env create -f python/ieeg_recon_config.yml 


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


