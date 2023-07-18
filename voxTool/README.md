# VoxTool 2.0


## Setup

To install VoxTool, simply do:

```
pip install voxtool
```

We recommend using voxtool within a virtual environment. If you have anaconda installed, you can do:

  ```
  conda create -n vt
  ```

This creates an environment named `vt` in which to run voxTool. You can then install VoxTool within that environment by doing:

```
conda activate vt
pip install voxtool
```

## Running

Inside the environment where VoxTool is installed, type in the terminal:

```
voxtool
``` 

This will bring up the main VoxTool window.

## Usage
0. Load a CT file, adjusting the threshold as necessary. To adjust the
   threshold, change the number in the bar at the top of the window
   marked ```CT Threshold```, then press the ```Update``` button next to it.
1. If continuing a previous localization: load the existing coordinates
   from a JSON coordinate file using the ```Load Coordinates``` button.
2. Press ```Define leads``` to set the names, shapes, types, and microcontacts
   for each implanted lead. Shapes are rows x columns.
3. Select the lead you wish to localize in the dropdown menu labeled ```Label```
   in the upper left corner
4. Click on the CT to highlight the next contact on that lead, then press
   ```Submit``` to mark its location
   - Alternatively, press the ```Seeding``` button to turn on seeding. VoxTool
     will attempt to extrapolate the locations of the remaing contacts
     as you select them, incrementing the contact number. Be sure to double-check that
     the results make sense, as occasionally two contacts
     will be given the same location
   - Alternatively, add the ends of a strip or depth
     or the corners of the grid with the ```Submit``` button, then press
     the ```Interpolate``` button. VoxTool will attempt to fill in the lead.
     It may not be completely successful. Pressing ```Interpolate``` again
     may interpolate additional contacts.
5. Press ```Add Micro-Contacts``` to add micro-contacts to any macro/micro leads.
6. Press the ```Save as``` button to save the list of localized contacts.
   If the checkbox labelled ```Include Bipolar Pairs``` is checked, locations
   will also be saved for the midpoint of each pair of neighboring contacts.



## Keyboard Shortcuts:

Button | Key Sequence
------ |  ------------
Load Scan | Ctrl-O
Define Leads | Ctrl-D
Save As | Ctrl-S
Submit (contact panel) | S
Submit (lead definition window) | S
Delete (contact panel)| Delete
Delete (lead definition window)| Delete
Confirm (lead definition window) | Enter

## Other Notes
* The list of contact names is sorted by lead name, and within each 
lead by contact number. The ```Interpolate``` button does not always assign
contact numbers in the expected order, so be sure to double-check 
that the numbers it has assigned are the ones that you want after using 
it. 

