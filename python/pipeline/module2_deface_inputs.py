import os
import glob
import pydeface
import argparse
import nibabel as nib
import shutil

# Argument Parser
parser = argparse.ArgumentParser()

parser.add_argument("-s", "--subject", required=True, help="Subject ID")
parser.add_argument("-d", "--source_directory", required=True, help="Source Directory")

args = parser.parse_args()

subject = args.subject
source_dir = args.source_directory

source_folder = os.path.join(source_dir, subject, 'ses-*')

def deface_image(in_img, out_img):
    # run defacing
    pydeface_command = 'pydeface {} --outfile {}'.format(in_img, out_img)
    os.system(pydeface_command)

# thresholding the CT scan effectively defaces it
def threshold_ct(in_ct, out_ct):
    ct = nib.load(in_ct)
    ct_affine = ct.affine
    ct_data = ct.get_fdata()

    ct_thresh = ct_data.copy()
    ct_thresh[ct_thresh < 0] = 0

    ct_thresh_nifti = nib.Nifti1Image(ct_thresh, ct_affine)
    nib.save(ct_thresh_nifti, out_ct)

def append_fname(in_fname):
    parts = in_fname.split('_')
    for i, part in enumerate(parts):
        if 'ses-' in part:
            parts[i] = part + '-defaced'
            break
    return '_'.join(parts)

sessions = glob.glob(source_folder)

for ses in sessions:
    ses_name = os.path.basename(ses)
    ses_defaced_path = os.path.join(os.path.dirname(ses), ses_name+'-defaced')
    os.makedirs(ses_defaced_path, exist_ok=True)

    anat_folder = os.path.join(ses, 'anat')
    if os.path.exists(anat_folder):
        anat_defaced_folder = os.path.join(ses_defaced_path, 'anat')
        os.makedirs(anat_defaced_folder, exist_ok=True)
        
        # apply defacing to files in anat
        for anat_file in glob.glob(os.path.join(anat_folder, '*')):
            if 'T1w' in anat_file:
                out_file = os.path.join(anat_defaced_folder, append_fname(os.path.basename(anat_file)))
                deface_image(anat_file, out_file)

    ct_folder = os.path.join(ses, 'ct')
    print(ct_folder)
    if os.path.exists(ct_folder):
        ct_defaced_folder = os.path.join(ses_defaced_path, 'ct')
        os.makedirs(ct_defaced_folder, exist_ok=True)
        
        # threshold the CTs in the 'ct' folder
        for ct_file in glob.glob(os.path.join(ct_folder, '*')):
            out_file = os.path.join(ct_defaced_folder, append_fname(os.path.basename(ct_file)))
            threshold_ct(ct_file, out_file)


    # copy other subfolders to the new defaced sessions
    for subfolder in os.listdir(ses):
        subfolder_path = os.path.join(ses, subfolder)
        if os.path.isdir(subfolder_path) and subfolder not in ['anat', 'ct']:
            subfolder_defaced_path = os.path.join(ses_defaced_path, subfolder)
            os.makedirs(subfolder_defaced_path, exist_ok=True)
            
            # Copy files with modified filenames
            for file_name in os.listdir(subfolder_path):
                file_path = os.path.join(subfolder_path, file_name)
                if os.path.isfile(file_path):
                    if 'ses-' in file_name:
                        defaced_file_name = append_fname(file_name)
                        defaced_file_path = os.path.join(subfolder_defaced_path, defaced_file_name)
                    else:
                        defaced_file_path = os.path.join(subfolder_defaced_path, file_name)
                    shutil.copy2(file_path, defaced_file_path)
                elif os.path.isdir(file_path):
                    shutil.copytree(file_path, os.path.join(subfolder_defaced_path, file_name))
