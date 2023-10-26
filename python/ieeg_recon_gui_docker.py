import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter import filedialog
import subprocess
import os
from PIL import Image, ImageTk

# Get the current script directory
current_script_directory = os.path.dirname(os.path.abspath(__file__))

# Replace the period with the current script directory
standard_atlas_directory = os.path.join(current_script_directory, 'source_data', 'standard_atlases')


def run_pipeline():
    # Construct the command based on GUI selections
    # this is basically a wrapper for the Docker command
    cmd_first_part = ["docker","run"]
    
    cmd_second_part = ["lucasalf11/ieeg_recon:1.0"]

    if subject_var.get():
        cmd_second_part.extend(["-s", subject_var.get()])
    if reference_session_var.get():
        cmd_second_part.extend(["-rs", reference_session_var.get()])
    if module_var.get():
        cmd_second_part.extend(["-m", module_options[module_var.get()]])
        
    # Module 2 arguments
    if source_directory_var.get():
        cmd_first_part.extend(["-v", source_directory_var.get()+':/source_data'])
        cmd_second_part.extend(["-d", "/source_data"])
    if clinical_session_var.get():
        cmd_second_part.extend(["-cs", clinical_session_var.get()])
    if greedy_var.get():
        cmd_second_part.append(greedy_var.get())
    if bs_var.get() and fs_var.get():
        cmd_second_part.append("-bs")
        cmd_first_part.extend(["-v", fs_var.get()+':/freesurfer'])
        cmd_second_part.extend(["-fs", '/freesurfer'])
    if deface_var.get():
        cmd_second_part.append("-dfo")
    
    
    # Module 3 arguments
    if atlas_path_var.get():
        cmd_first_part.extend(["-v", atlas_path_var.get()+':/atlas_files/atlas.nii.gz'])
        cmd_second_part.extend(["-a", '/atlas_files/atlas.nii.gz'])
    if atlas_name_var.get():
        cmd_second_part.extend(["-an", atlas_name_var.get()])
    if roi_indices_var.get():
        cmd_first_part.extend(["-v", roi_indices_var.get()+':/atlas_files/indices.txt'])
        cmd_second_part.extend(["-ri", '/atlas_files/indices.txt'])
    if roi_labels_var.get():
        cmd_first_part.extend(["-v", roi_labels_var.get()+':/atlas_files/labels.txt'])
        cmd_second_part.extend(["-rl","/atlas_files/labels.txt"])
    if radius_var.get():
        cmd_second_part.extend(["-r", radius_var.get()])
    # if ieeg_recon_dir_var.get():
    #     cmd.extend(["-ird", ieeg_recon_dir_var.get()])
    if atlas_lookup_table_var.get():
        cmd_first_part.extend(["-v", atlas_lookup_table_var.get()+':/atlas_files/lut.txt'])
        cmd_second_part.extend(["-lut", '/atlas_files/lut.txt'])
    if ants_pynet_var.get():
        cmd_second_part.append("-apn")

    # Additional arguments
    if mni_var.get():
        cmd_second_part.append("-mni")

    if convert_atlas_var.get():
        cmd_second_part.append("-ca")

    # Now run the command

    cmd = cmd_first_part + cmd_second_part
    cmd = ' '.join(cmd)
    print(cmd)
    try:
        #subprocess.call(cmd_first_part)

        # pull the docker image
        cmd_pull = 'docker pull lucasalf11/ieeg_recon:1.0'
        os.system(cmd_pull)

        # run the docker command
        os.system(cmd)
    except Exception as e:
        messagebox.showerror("Error", f"Failed to run pipeline: {e}")
    else:
        messagebox.showinfo("Success", "Pipeline completed successfully!")

def open_file_creator():
    cmd = ["python","ieeg_recon_filecreator.py"]
    subprocess.call(cmd)

def open_voxtool():
    cmd = ["bash","run_voxtool.sh"]
    subprocess.call(cmd)

def browse_directory(var):
    directory = filedialog.askdirectory()
    if directory:
        var.set(directory)

def browse_for_file(var):
    filepath = filedialog.askopenfilename()
    if filepath:
        var.set(filepath)

def browse_source_directory(var, subject_combobox):
    directory = filedialog.askdirectory()
    if directory:
        var.set(directory)
        subjects = [d for d in os.listdir(directory) if os.path.isdir(os.path.join(directory, d)) and d.startswith("sub-")]
        subject_combobox['values'] = subjects

def browse_source_directory(var, subject_combobox, reference_session_combobox, clinical_session_combobox):
    directory = filedialog.askdirectory()
    if directory:
        var.set(directory)
        subjects = [d for d in os.listdir(directory) if os.path.isdir(os.path.join(directory, d)) and d.startswith("sub-")]
        subject_combobox['values'] = subjects
        if subjects:
            subject_combobox.set(subjects[0])
            update_sessions(directory, subjects[0], reference_session_combobox, clinical_session_combobox)

def update_sessions(source_directory, subject, reference_session_combobox, clinical_session_combobox):
    subject_directory = os.path.join(source_directory, subject)
    sessions = [d for d in os.listdir(subject_directory) if os.path.isdir(os.path.join(subject_directory, d)) and d.startswith("ses-")]
    reference_session_combobox['values'] = sessions
    clinical_session_combobox['values'] = sessions
    if sessions:
        reference_session_combobox.set(sessions[0])
        clinical_session_combobox.set(sessions[0])
       
def on_subject_change(event):
    source_directory = source_directory_var.get()
    subject = subject_var.get()
    update_sessions(source_directory, subject, reference_session_combobox, clinical_session_combobox)

app = tk.Tk()
app.title("iEEG-recon GUI")

frame = ttk.Frame(app)
frame.pack(padx=10, pady=10)

app.grid_rowconfigure(0, weight=1)
app.grid_columnconfigure(0, weight=1)
frame.grid(sticky='nsew')
frame.grid_rowconfigure(7, weight=1)
frame.grid_columnconfigure(1, weight=1)

image_path = "./figures/ieeg_recon_logo.png"
image = Image.open(image_path)
photo = ImageTk.PhotoImage(image)

img_label = ttk.Label(frame, image=photo)
img_label.grid(row=0, column=1, padx=5, pady=5)

ttk.Label(frame, text="Source Directory:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
source_directory_var = tk.StringVar()
source_directory_entry = ttk.Entry(frame, textvariable=source_directory_var)
source_directory_entry.grid(row=1, column=1, padx=0, pady=5)

ttk.Label(frame, text="Subject ID:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
subject_var = tk.StringVar()
subject_combobox = ttk.Combobox(frame, textvariable=subject_var)
subject_combobox.grid(row=2, column=1, padx=5, pady=5)
subject_var.set("sub-")
subject_combobox.bind('<<ComboboxSelected>>', on_subject_change)

ttk.Button(frame, text="Browse", command=lambda: browse_source_directory(source_directory_var, subject_combobox, reference_session_combobox, clinical_session_combobox)).grid(row=1, column=2, padx=5, pady=5)

ttk.Label(frame, text="Reference Session:").grid(row=3, column=0, sticky=tk.W, padx=5, pady=5)
reference_session_var = tk.StringVar()
reference_session_combobox = ttk.Combobox(frame, textvariable=reference_session_var)
reference_session_combobox.grid(row=3, column=1, padx=5, pady=5)
reference_session_var.set("ses-clinical01")

ttk.Label(frame, text="Clinical Session:").grid(row=4, column=0, sticky=tk.W, padx=5, pady=5)
clinical_session_var = tk.StringVar()
clinical_session_combobox = ttk.Combobox(frame, textvariable=clinical_session_var)
clinical_session_combobox.grid(row=4, column=1, padx=5, pady=5)
clinical_session_var.set("ses-clinical01")

ttk.Label(frame, text="Module to Run:").grid(row=5, column=0, sticky=tk.W, padx=5, pady=5)
module_var = tk.StringVar()
module_options = {"2": "2", "3": "3", "2 and 3": "-1"}
module_dropdown = ttk.Combobox(frame, textvariable=module_var, values=list(module_options.keys()), state="readonly")
module_dropdown.grid(row=5, column=1, padx=5, pady=5)
module_dropdown.set("2 and 3")  # Default value

# Module 2 arguments section
module2_frame = ttk.LabelFrame(frame, text="Module 2 Arguments")
module2_frame.grid(row=6, column=0, columnspan=2, pady=10, sticky=tk.W+tk.E)

# Choosing the greedy option for module 2
greedy_var = tk.StringVar()

# Create Radiobuttons for the two exclusive options
ttk.Label(module2_frame, text="Greedy Options: ").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
ttk.Radiobutton(module2_frame, text="None", variable=greedy_var, value="").grid(row=2, column=1, sticky=tk.W, padx=5, pady=5)
ttk.Radiobutton(module2_frame, text="Greedy correction", variable=greedy_var, value="-g").grid(row=3, column=1, sticky=tk.W, padx=5, pady=5)
ttk.Radiobutton(module2_frame, text="Greedy centering alone", variable=greedy_var, value="-gc").grid(row=4, column=1, sticky=tk.W, padx=5, pady=5)

# Set "None" as the default selection
greedy_var.set("-gc")

# Add the option to deface outputs

deface_var = tk.BooleanVar()
deface_chk = ttk.Checkbutton(module2_frame, text="Deface Outputs", variable=deface_var)
deface_chk.grid(row=5, column=2, columnspan=2, sticky=tk.W, padx=5, pady=5)


# Add the option for brain shift

bs_var = tk.BooleanVar()
bs_chk = ttk.Checkbutton(module2_frame, text="Correct for Brain Shift (ECoG; requires FreeSurfer)", variable=bs_var)
bs_chk.grid(row=5, column=0, columnspan=2, sticky=tk.W, padx=5, pady=5)


ttk.Label(module2_frame, text="FreeSurfer Directory:").grid(row=6, column=0, sticky=tk.W, padx=5, pady=5)
fs_var = tk.StringVar()
fs_entry = ttk.Entry(module2_frame, textvariable=fs_var)
fs_entry.grid(row=6, column=1, padx=5, pady=5)
ttk.Button(module2_frame, text="Browse", command=lambda: browse_directory(fs_var)).grid(row=6, column=2, padx=5, pady=5)

# Module 3 arguments section

def toggle_module3_inputs():
    if ants_pynet_var.get():
        state, bg_color, fg_color = "disabled", "light gray", "gray"
    else:
        state, bg_color, fg_color = "normal", "white", "black"
    
    for widget in module3_inputs:
        widget.configure(state=state, background=bg_color, foreground=fg_color)


module3_frame = ttk.LabelFrame(frame, text="Module 3 Arguments")
module3_frame.grid(row=7, column=0, columnspan=2, pady=10, sticky=tk.W+tk.E)

module3_frame.grid_rowconfigure(7, weight=1)  # Adjusts the last row inside module3_frame
module3_frame.grid_columnconfigure(1, weight=1)  # Adjusts the main column inside module3_frame

# Checkbox for -apn option, if this option is selected, no need to add the other options
ants_pynet_var = tk.BooleanVar()
ants_pynet_var.set(True)  # Set the checkbox to be checked by default
ants_pynet_var.trace_add("write", lambda *args: toggle_module3_inputs())
ants_pynet_chk = ttk.Checkbutton(module3_frame, text="Run AntsPyNet DKT Segmentation", variable=ants_pynet_var)
ants_pynet_chk.grid(row=0, column=0, columnspan=2, sticky=tk.W, padx=5, pady=5)


mni_var = tk.BooleanVar()
mni_chk = ttk.Checkbutton(module3_frame, text="Include MNI Outputs", variable=mni_var)
mni_chk.grid(row=0, column=2, columnspan=2, sticky=tk.W, padx=5, pady=5)



# Radius
ttk.Label(module3_frame, text="Radius:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
radius_var = tk.StringVar()
radius_entry = ttk.Entry(module3_frame, textvariable=radius_var)
radius_entry.grid(row=1, column=1, padx=5, pady=5)
radius_var.set("2")

# Combobox that selects the standard atlases
available_atlases = ["none"] + [a for a in os.listdir(standard_atlas_directory) if os.path.isdir(os.path.join(standard_atlas_directory, a))]
ttk.Label(module3_frame, text="Standard Atlas:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
atlas_var = tk.StringVar()
atlas_dropdown = ttk.Combobox(module3_frame, textvariable=atlas_var, values=available_atlases, state="readonly")
atlas_dropdown.grid(row=2, column=1, padx=5, pady=5)
atlas_dropdown.set("none")  # Default value

# Callback function to be called when a new atlas is selected from the combobox
def on_atlas_selected(event):
    selected_atlas = atlas_var.get()
    if selected_atlas != "none":
        convert_atlas_var.set(True)  # Automatically check the "Convert atlas from MNI" checkbox
        atlas_path = os.path.join(standard_atlas_directory, selected_atlas, selected_atlas + 'MNI.nii.gz')
        atlas_path_var.set(atlas_path)  # Populate the atlas path
        atlas_name_var.set(selected_atlas)  # Populate the atlas name
        atlas_lookup_table = os.path.join(standard_atlas_directory, selected_atlas, selected_atlas + '_lut.csv')
        atlas_lookup_table_var.set(atlas_lookup_table)  # Populate the atlas lookup table
    else:
        convert_atlas_var.set(False)
        atlas_path_var.set('')
        atlas_name_var.set('')
        atlas_lookup_table_var.set('')

# Bind the callback function to the combobox
atlas_dropdown.bind('<<ComboboxSelected>>', on_atlas_selected)


# Atlas Path
ttk.Label(module3_frame, text="Atlas Path:").grid(row=3, column=0, sticky=tk.W, padx=5, pady=5)
atlas_path_var = tk.StringVar()
atlas_path_entry = ttk.Entry(module3_frame, textvariable=atlas_path_var)
atlas_path_entry.grid(row=3, column=1, padx=5, pady=5)
bb1 = ttk.Button(module3_frame, text="Browse", command=lambda: browse_for_file(atlas_path_var)).grid(row=3, column=2, padx=5, pady=5)

convert_atlas_var = tk.BooleanVar()
convert_atlas_chk = ttk.Checkbutton(module3_frame, text="Convert atlas from MNI", variable=convert_atlas_var)
convert_atlas_chk.grid(row=3, column=3, columnspan=2, sticky=tk.W, padx=5, pady=5)


# Atlas Name
ttk.Label(module3_frame, text="Atlas Name:").grid(row=4, column=0, sticky=tk.W, padx=5, pady=5)
atlas_name_var = tk.StringVar()
atlas_name_entry = ttk.Entry(module3_frame, textvariable=atlas_name_var)
atlas_name_entry.grid(row=4, column=1, padx=5, pady=5)

# Atlas Lookup Table
ttk.Label(module3_frame, text="Atlas Lookup Table:").grid(row=5, column=0, sticky=tk.W, padx=5, pady=5)
atlas_lookup_table_var = tk.StringVar()
atlas_lookup_table_entry = ttk.Entry(module3_frame, textvariable=atlas_lookup_table_var)
atlas_lookup_table_entry.grid(row=5, column=1, padx=5, pady=5)
bb5 = ttk.Button(module3_frame, text="Browse", command=lambda: browse_for_file(atlas_lookup_table_var)).grid(row=5, column=2, padx=5, pady=5)


# ROI Indices
ttk.Label(module3_frame, text="ROI Indices:").grid(row=6, column=0, sticky=tk.W, padx=5, pady=5)
roi_indices_var = tk.StringVar()
roi_indices_entry = ttk.Entry(module3_frame, textvariable=roi_indices_var)
roi_indices_entry.grid(row=6, column=1, padx=5, pady=5)
bb2 = ttk.Button(module3_frame, text="Browse", command=lambda: browse_for_file(roi_indices_var)).grid(row=6, column=2, padx=5, pady=5)

# ROI Labels
ttk.Label(module3_frame, text="ROI Labels:").grid(row=7, column=0, sticky=tk.W, padx=5, pady=5)
roi_labels_var = tk.StringVar()
roi_labels_entry = ttk.Entry(module3_frame, textvariable=roi_labels_var)
roi_labels_entry.grid(row=7, column=1, padx=5, pady=5)
bb3 = ttk.Button(module3_frame, text="Browse", command=lambda: browse_for_file(roi_labels_var)).grid(row=7, column=2, padx=5, pady=5)


module3_inputs = [
    atlas_path_entry,
    atlas_name_entry,
    roi_indices_entry,
    roi_labels_entry,
    atlas_lookup_table_entry,
]

# At the end of all options
voxtool_button = ttk.Button(frame, text="VoxTool", command=open_voxtool)
voxtool_button.grid(row=10, column=0, padx=10, pady=20)

filecreator_button = ttk.Button(frame, text="File Creator", command=open_file_creator)
filecreator_button.grid(row=10, column=1, padx=10, pady=20)

run_button = ttk.Button(frame, text="Run Pipeline", command=run_pipeline)
run_button.grid(row=10, column=2, padx=10, pady=20)



app.mainloop()
