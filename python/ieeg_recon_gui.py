import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter import filedialog
import subprocess
import os
from PIL import Image, ImageTk

def run_pipeline():
    # Construct the command based on GUI selections
    cmd = ["python", "ieeg_recon.py"]

    if subject_var.get():
        cmd.extend(["-s", subject_var.get()])
    if reference_session_var.get():
        cmd.extend(["-rs", reference_session_var.get()])
    if module_var.get():
        cmd.extend(["-m", module_options[module_var.get()]])
        
    # Module 2 arguments
    if source_directory_var.get():
        cmd.extend(["-d", source_directory_var.get()])
    if clinical_session_var.get():
        cmd.extend(["-cs", clinical_session_var.get()])
    if greedy_var.get():
        cmd.append(greedy_var.get())
    if bs_var.get() and fs_var.get():
        cmd.append("-bs")
        cmd.extend(["-fs", fs_var.get()])

    
    
    # Module 3 arguments
    if atlas_path_var.get():
        cmd.extend(["-a", atlas_path_var.get()])
    if atlas_name_var.get():
        cmd.extend(["-an", atlas_name_var.get()])
    if roi_indices_var.get():
        cmd.extend(["-ri", roi_indices_var.get()])
    if roi_labels_var.get():
        cmd.extend(["-rl", roi_labels_var.get()])
    if radius_var.get():
        cmd.extend(["-r", radius_var.get()])
    if ieeg_recon_dir_var.get():
        cmd.extend(["-ird", ieeg_recon_dir_var.get()])
    if atlas_lookup_table_var.get():
        cmd.extend(["-lut", atlas_lookup_table_var.get()])
    if ants_pynet_var.get():
        cmd.append("-apn")

    # Additional arguments
    if mni_var.get():
        cmd.append("-mni")

    # Now run the command
    try:
        subprocess.call(cmd)
    except Exception as e:
        messagebox.showerror("Error", f"Failed to run pipeline: {e}")
    else:
        messagebox.showinfo("Success", "Pipeline completed successfully!")

def open_file_creator():
    cmd = ["python","ieeg_recon_filecreator.py"]
    subprocess.call(cmd)

def open_voxtool():
    cmd = ["voxtool"]
    subprocess.call(cmd)

def browse_directory(var):
    directory = filedialog.askdirectory()
    if directory:
        var.set(directory)

def browse_for_file(var):
    filepath = filedialog.askopenfilename()
    if filepath:
        var.set(filepath)

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
source_directory_entry = ttk.Entry(frame, textvariable=source_directory_var).grid(row=1, column=1, padx=0, pady=5)

ttk.Label(frame, text="Subject ID:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
subject_var = tk.StringVar()
subject_combobox = ttk.Combobox(frame, textvariable=subject_var)
subject_combobox.grid(row=2, column=1, padx=5, pady=5)
subject_var.set("sub-")

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

# Atlas Path
ttk.Label(module3_frame, text="Atlas Path:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
atlas_path_var = tk.StringVar()
atlas_path_entry = ttk.Entry(module3_frame, textvariable=atlas_path_var)
atlas_path_entry.grid(row=2, column=1, padx=5, pady=5)
bb1 = ttk.Button(module3_frame, text="Browse", command=lambda: browse_directory(atlas_path_var)).grid(row=2, column=2, padx=5, pady=5)

# Atlas Name
ttk.Label(module3_frame, text="Atlas Name:").grid(row=3, column=0, sticky=tk.W, padx=5, pady=5)
atlas_name_var = tk.StringVar()
atlas_name_entry = ttk.Entry(module3_frame, textvariable=atlas_name_var)
atlas_name_entry.grid(row=3, column=1, padx=5, pady=5)

# ROI Indices
ttk.Label(module3_frame, text="ROI Indices:").grid(row=4, column=0, sticky=tk.W, padx=5, pady=5)
roi_indices_var = tk.StringVar()
roi_indices_entry = ttk.Entry(module3_frame, textvariable=roi_indices_var)
roi_indices_entry.grid(row=4, column=1, padx=5, pady=5)
bb2 = ttk.Button(module3_frame, text="Browse", command=lambda: browse_for_file(roi_indices_var)).grid(row=4, column=2, padx=5, pady=5)

# ROI Labels
ttk.Label(module3_frame, text="ROI Labels:").grid(row=5, column=0, sticky=tk.W, padx=5, pady=5)
roi_labels_var = tk.StringVar()
roi_labels_entry = ttk.Entry(module3_frame, textvariable=roi_labels_var)
roi_labels_entry.grid(row=5, column=1, padx=5, pady=5)
bb3 = ttk.Button(module3_frame, text="Browse", command=lambda: browse_for_file(roi_labels_var)).grid(row=5, column=2, padx=5, pady=5)


# iEEG Recon Directory
ttk.Label(module3_frame, text="iEEG Recon Directory:").grid(row=6, column=0, sticky=tk.W, padx=5, pady=5)
ieeg_recon_dir_var = tk.StringVar()
ieeg_recon_dir_entry = ttk.Entry(module3_frame, textvariable=ieeg_recon_dir_var)
ieeg_recon_dir_entry.grid(row=6, column=1, padx=5, pady=5)
bb4 = ttk.Button(module3_frame, text="Browse", command=lambda: browse_directory(ieeg_recon_dir_var)).grid(row=6, column=2, padx=5, pady=5)

# Atlas Lookup Table
ttk.Label(module3_frame, text="Atlas Lookup Table:").grid(row=7, column=0, sticky=tk.W, padx=5, pady=5)
atlas_lookup_table_var = tk.StringVar()
atlas_lookup_table_entry = ttk.Entry(module3_frame, textvariable=atlas_lookup_table_var)
atlas_lookup_table_entry.grid(row=7, column=1, padx=5, pady=5)
bb5 = ttk.Button(module3_frame, text="Browse", command=lambda: browse_for_file(atlas_lookup_table_var)).grid(row=7, column=2, padx=5, pady=5)


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
