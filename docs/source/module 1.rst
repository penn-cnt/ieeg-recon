Module 1
==========

Electrode Labeling using VoxTool


*  **Inputs**: 
  
   * Post-implant CT
  
*  **Output**: 
   
   * Electrode coordinates in CT space


VoxTool 2.0
-------------

Setup
^^^^^^

- Create a Conda environment from the definition file

.. code-block:: console

  $ cd voxTool
  $ conda env create -f conda_env.yml

This creates an environment named `vt` in which to run voxTool.

Running
^^^^^^^^

* Activate the conda environment:

.. code-block:: console

   $ conda activate vt

* Launch the program:

.. code-block:: console

   $ python launch_pyloc.py


Usage
^^^^^^

1. Load a CT file, adjusting the threshold as necessary. To adjust the
   threshold, change the number in the bar at the top of the window
   marked ``CT Threshold``, then press the ``Update`` button next to it.
2. If continuing a previous localization: load the existing coordinates
   from a JSON coordinate file using the ``Load Coordinates`` button.
3. Press ``Define leads`` to set the names, shapes, types, and microcontacts
   for each implanted lead. Shapes are rows x columns.
4. Select the lead you wish to localize in the dropdown menu labeled ``Label``
   in the upper left corner
5. Click on the CT to highlight the next contact on that lead, then press ``Submit`` to mark its location.
6. Press ``Add Micro-Contacts`` to add micro-contacts to any macro/micro leads.
7. Press the ``Save as`` button to save the list of localized contacts. If the checkbox labelled ``Include Bipolar Pairs`` is checked, locations will also be saved for the midpoint of each pair of neighboring contacts.
   

Keyboard Shortcuts
^^^^^^^^^^^^^^^^^^^

+---------------------------------+--------------+
| Button                          | Key Sequence |
+=================================+==============+
|Load Scan                        | Ctrl-O       |
+---------------------------------+--------------+
|Define Leads                     |Ctrl-D        |
+---------------------------------+--------------+
|Save As                          |Ctrl-S        |
+---------------------------------+--------------+
|Submit (contact panel)           |S             |
+---------------------------------+--------------+
|Submit (lead definition window)  |S             |
+---------------------------------+--------------+
|Delete (contact panel)           |Delete        |
+---------------------------------+--------------+
|Delete (lead definition window)  |Delete        |
+---------------------------------+--------------+
|Confirm (lead definition window) |Enter         |
+---------------------------------+--------------+


Other Notes
^^^^^^^^^^^^^^^^^^^
* The list of contact names is sorted by lead name, and within each 
lead by contact number. The ``Interpolate`` button does not always assign
contact numbers in the expected order, so be sure to double-check 
that the numbers it has assigned are the ones that you want after using 
it. 







.. autosummary::
   :toctree: generated

   ieeg-recon
