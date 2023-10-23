import os
import tkinter as tk
from tkinter import filedialog, ttk
import shutil


class Application(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        self.title("Folder Structure GUI")
        self.geometry("500x400")

        self.subjectID_var = tk.StringVar()
        self.reference_session_var = tk.StringVar()
        self.clinical_session_var = tk.StringVar()
        self.output_directory_var = tk.StringVar()
        self.reference_T1w_var = tk.StringVar()
        self.clinical_CT_var = tk.StringVar()
        self.clinical_iEEG_var = tk.StringVar()

        self.create_widgets()

    def browse_directory(self, variable):
        folder = filedialog.askdirectory()
        if folder:
            variable.set(folder)

    def browse_file(self, variable):
        file = filedialog.askopenfilename()
        if file:
            variable.set(file)

    def deface_inputs(self):
        args = {
            "subject": self.subjectID_var.get(),
            "reference_session": self.reference_session_var.get(),
            "clinical_session": self.clinical_session_var.get(),
            "output_directory": self.output_directory_var.get(),
            "reference_T1w": self.reference_T1w_var.get(),
            "clinical_CT": self.clinical_CT_var.get(),
            "clinical_iEEG": self.clinical_iEEG_var.get(),
        }

        cmd = ["python","pipeline/deface_inputs","-s",args.subject,"-d",args.source_directory]

    def create_folder_structure(self):
        args = {
            "subject": self.subjectID_var.get(),
            "reference_session": self.reference_session_var.get(),
            "clinical_session": self.clinical_session_var.get(),
            "output_directory": self.output_directory_var.get(),
            "reference_T1w": self.reference_T1w_var.get(),
            "clinical_CT": self.clinical_CT_var.get(),
            "clinical_iEEG": self.clinical_iEEG_var.get(),
        }

        subject_dir = os.path.join(args["output_directory"], args["subject"])
        ref_dir = os.path.join(subject_dir, args["reference_session"], "anat")
        clin_dir_t1w = os.path.join(subject_dir, args["clinical_session"], "anat")
        clin_dir_ct = os.path.join(subject_dir, args["clinical_session"], "ct")
        clin_dir_ieeg = os.path.join(subject_dir, args["clinical_session"], "ieeg")

        if not os.path.exists(ref_dir):
            os.makedirs(ref_dir)
        if not os.path.exists(clin_dir_t1w):
            os.makedirs(clin_dir_t1w)
        if not os.path.exists(clin_dir_ct):
            os.makedirs(clin_dir_ct)
        if not os.path.exists(clin_dir_ieeg):
            os.makedirs(clin_dir_ieeg)

        t1w_ref = args["subject"] + "_" + args["reference_session"] + "_acq-3D_space-T00mri_T1w.nii.gz"
        shutil.copy(args["reference_T1w"], os.path.join(ref_dir, t1w_ref))

        clin_ct = args["subject"] + "_" + args["clinical_session"] + "_acq-3D_space-T01ct_ct.nii.gz"
        shutil.copy(args["clinical_CT"], os.path.join(clin_dir_ct, clin_ct))

        clin_ieeg = args["subject"] + "_" + args["clinical_session"] + "_space-T01ct_desc-vox_electrodes.txt"
        shutil.copy(args["clinical_iEEG"], os.path.join(clin_dir_ieeg, clin_ieeg))

    def create_widgets(self):
        ttk.Label(self, text="Subject ID:").grid(column=0, row=0, sticky="w")
        ttk.Entry(self, textvariable=self.subjectID_var).grid(column=1, row=0, sticky="ew")

        ttk.Label(self, text="Reference Session:").grid(column=0, row=1, sticky="w")
        ttk.Entry(self, textvariable=self.reference_session_var).grid(column=1, row=1, sticky="ew")

        ttk.Label(self, text="Clinical Session:").grid(column=0, row=2, sticky="w")
        ttk.Entry(self, textvariable=self.clinical_session_var).grid(column=1, row=2, sticky="ew")

        ttk.Label(self, text="Output Directory:").grid(column=0, row=3, sticky="w")
        ttk.Entry(self, textvariable=self.output_directory_var).grid(column=1, row=3, sticky="ew")
        ttk.Button(self, text="Browse", command=lambda: self.browse_directory(self.output_directory_var)).grid(column=2, row=3, sticky="ew")

        ttk.Label(self, text="Reference T1w:").grid(column=0, row=4, sticky="w")
        ttk.Entry(self, textvariable=self.reference_T1w_var).grid(column=1, row=4, sticky="ew")
        ttk.Button(self, text="Browse", command=lambda: self.browse_file(self.reference_T1w_var)).grid(column=2, row=4, sticky="ew")

        ttk.Label(self, text="Clinical CT:").grid(column=0, row=5, sticky="w")
        ttk.Entry(self, textvariable=self.clinical_CT_var).grid(column=1, row=5, sticky="ew")
        ttk.Button(self, text="Browse", command=lambda: self.browse_file(self.clinical_CT_var)).grid(column=2, row=5, sticky="ew")

        ttk.Label(self, text="Clinical iEEG coordinates:").grid(column=0, row=6, sticky="w")
        ttk.Entry(self, textvariable=self.clinical_iEEG_var).grid(column=1, row=6, sticky="ew")
        ttk.Button(self, text="Browse", command=lambda: self.browse_file(self.clinical_iEEG_var)).grid(column=2, row=6, sticky="ew")

        self.deface_var = tk.BooleanVar()
        deface_chk = ttk.Checkbutton(self, text="Deface Inputs", variable=self.deface_var)
        deface_chk.grid(column=1, row=7, sticky="ew")


        ttk.Button(self, text="Create Folder Structure", command=self.create_folder_structure).grid(column=0, row=8, columnspan=3, sticky="ew")


if __name__ == "__main__":
    app = Application()
    app.mainloop()
