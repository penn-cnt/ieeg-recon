#!/usr/bin/env python

import argparse
import os
import subprocess
import sys

def parse_args():
    parser = argparse.ArgumentParser()

    # Global arguments
    parser.add_argument("-s", "--subject", help="Subject ID")
    parser.add_argument("-rs", "--reference_session")
    parser.add_argument("-m", "--module", help="Module to Run, -1 to run modules 2 and 3")

    # Module 2 arguments
    parser.add_argument("-d", "--source_directory", help="Source Directory")
    parser.add_argument("-cs", "--clinical_session")
    parser.add_argument("-g", "--greedy", action="store_true")
    parser.add_argument("-gc", "--greedy_centering", action="store_true")
    parser.add_argument("-bs", "--brain_shift", action="store_true")
    parser.add_argument("-fs", "--freesurfer_dir")
    parser.add_argument("-dfo", "--deface_outputs", action="store_true")

    # Module 3 arguments
    parser.add_argument("-a", "--atlas_path")
    parser.add_argument("-an", "--atlas_name")
    parser.add_argument("-ri", "--roi_indices", help="ROI Indices")
    parser.add_argument("-rl", "--roi_labels", help="ROI Labels")
    parser.add_argument("-r", "--radius", help="Radius for Electrode atlas Assignment")
    parser.add_argument("-ird", "--ieeg_recon_dir", help="Source iEEG Recon Directory")
    parser.add_argument("-lut", "--atlas_lookup_table", help="Atlas Lookup Table")
    parser.add_argument("-apn", "--ants_pynet", help="Run AntsPyNet DKT Segmentation", action="store_true")

    # Module 3 MNI
    parser.add_argument("-mni", "--run_mni", help="Run MNI registration", action="store_true")

    return parser.parse_args()

def file_check(args):

    run_pipeline = True

    # check for the minimum required files to run iEEG-recon
    subject_dir = os.path.join(args.source_directory, args.subject)

    ref_dir = os.path.join(subject_dir, args.reference_session,'anat')

    # check for reference anat directory
    if os.path.exists(ref_dir)==False:
        print('ERROR: Reference directory: ', ref_dir, ' does not exist!')
        run_pipeline = False
    
    # check for reference T1w image
    t1w_ref = args.subject+'_'+args.reference_session+'_acq-3D_space-T00mri_T1w.nii.gz'

    if os.path.exists(os.path.join(ref_dir,t1w_ref))==False:
        print('ERROR: Reference T1w image ', t1w_ref, ' does not exist in ', ref_dir,'. Check filename...')
        run_pipeline = False
    

    # check for clinical anat, ct and ieeg directories
    clin_dir_t1w = os.path.join(subject_dir, args.clinical_session, 'anat')
    clin_t1w = args.subject+'_'+args.clinical_session+'_acq-3D_space-T00mri_T1w.nii.gz'

    clin_dir_ct = os.path.join(subject_dir, args.clinical_session, 'ct')
    clin_ct = args.subject+'_'+args.clinical_session+'_acq-3D_space-T01ct_ct.nii.gz'

    clin_dir_ieeg = os.path.join(subject_dir, args.clinical_session, 'ieeg')
    clin_ieeg = args.subject+'_'+args.clinical_session+'_space-T01ct_desc-vox_electrodes.txt'

    
    if os.path.exists(os.path.join(clin_dir_ct, clin_ct))==False:
        print('ERROR: Clinical CT Scan image ', clin_ct, ' does not exist in ', clin_dir_ct,'. Check filenames...')
        run_pipeline = False

    if os.path.exists(os.path.join(clin_dir_ieeg, clin_ieeg))==False:
        print('ERROR: VoxTool coordinates ', clin_ieeg, ' does not exist in ', clin_dir_ieeg,'. Check filenames...')
        run_pipeline = False
    
    return run_pipeline
    


def get_atlas_lookup_params(args):
    if args.ants_pynet:
        args.atlas_name = 'DKTantspynet'
        args.atlas_path = 'notneeded'
        return " -apn"
    
    if args.atlas_lookup_table:
        return " -lut " + args.atlas_lookup_table
    
    elif (args.roi_indices != None) and (args.roi_labels != None):
        return " -ri " + args.roi_indices + " -rl " + args.roi_labels
    else:
        return None

def run_module2(args):
    cmd = ["python", "pipeline/module2.py", "-s", args.subject, "-rs", args.reference_session, "-d", args.source_directory, "-cs", args.clinical_session]
    
    if args.greedy:
        print('Module 2 is using Greedy correction ...')
        cmd.append("-g")
    elif args.greedy_centering:
        print('Module 2 is using Greedy centering alone ...')
        cmd.append("-gc")
    
    subprocess.call(cmd)
    
    if args.deface_outputs:
        print("Defacing outputs...")
        subprocess.call(["python","pipeline/deface_outputs.py","-s", args.subject, "-d", args.source_directory])

    if args.brain_shift:
        print("Applying brain shift correction to module 2 outputs...")
        subprocess.call(["python", "pipeline/brain_shift.py", "-s", args.subject, "-rs", args.reference_session, "-d", args.source_directory, "-fs", args.freesurfer_dir, "-cs", args.clinical_session])

def run_module3(args, atlas_lookup_params):
    if atlas_lookup_params!=None:
        if not args.ieeg_recon_dir:
            clinical_module_dir = os.path.join(args.source_directory, args.subject, 'derivatives', 'ieeg_recon')
        else:
            clinical_module_dir = args.ieeg_recon_dir

        cmd = [
            "python", "pipeline/module3.py", 
            "-s", args.subject, 
            "-rs", args.reference_session, 
            "-ird", clinical_module_dir, 
            "-a", args.atlas_path, 
            "-an", args.atlas_name, 
            "-r", args.radius
        ] + atlas_lookup_params.split()

        subprocess.call(cmd)
    else:
        print('Incorrect Module 3 parameters... \nModule 3 will not run')
        

def run_reports(args):
    subprocess.call(["python", "reports/create_workspace.py", "-s", args.subject, "-rs", args.reference_session, "-d", args.source_directory, "-cs", args.clinical_session])
    subprocess.call(["python", "reports/create_html.py", "-s", args.subject, "-rs", args.reference_session, "-d", args.source_directory, "-cs", args.clinical_session])

def run_mni(args):
    print('Running MNI registration, make sure Module 2 has ran already (i.e. run with -m 2 or -m -1 flags if not)')
    subprocess.call(["python", "pipeline/module3_mni_V2.py", "-s", args.subject, "-rs", args.reference_session, "-cs", args.clinical_session,"-d", args.source_directory])


def main():

    args = parse_args()

    # Printing initial arguments
    print("Command:", " ".join(sys.argv))
    print('Subject: ', args.subject)
    print('Clinical Session: ', args.clinical_session)
    print('Reference Session: ', args.reference_session)

    # Determine atlas lookup parameters
    atlas_lookup_params = get_atlas_lookup_params(args)
    
    # Check that the minimum required files are present
    run_pipeline= file_check(args)

    if run_pipeline:
        if args.module == '-1':
            print('Running Modules 2 and 3 ... \n \n \n \n ')
            run_module2(args)
            run_module3(args, atlas_lookup_params)
            if args.run_mni:
                run_mni(args)
            run_reports(args)

        elif args.module == '2':
            print('Running Module 2 ...')
            run_module2(args)
            run_reports(args)

        elif args.module == '3':
            print('Running Module 3 ...')
            run_module3(args, atlas_lookup_params)
            if args.run_mni:
                run_mni(args)


if __name__ == "__main__":
    main()