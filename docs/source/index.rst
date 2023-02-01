IEEG-recon
===================================

**IEEG-recon** is a modular pipeline used to reconstruct intracranial electrode coordinates from a post-implant CT scan, into a pre-implant MRI.  The pipeline is available in both MATLAB and python computing environments.

iEEG-Recon is divided into 3 modules:

* :doc:`module 1` consists of an electrode labeling GUI called VoxTool, available here: https://github.com/penn-cnt/voxTool. VoxTool allows the user to label the electrode locations in the post-implant CT scan.
* :doc:`module 2` registers the CT scan to the pre-implant MRI and transforms the VoxTool generated coordinates from CT space to MRI space
* :doc:`module 3` maps each electrode to a specific ROI defined by a brain atlas registered to the pre-implant MRI

.. note::

   This project is under active development.


.. image:: images/OHBM.png
  :width: 800
  :alt: IEEG-recon pipeline


Check out the :doc:`usage` section for further information, including
how to :ref:`install` the project.


Table of Contents
-------------------

.. toctree::

   usage
   module 1
   module 2
   module 3
