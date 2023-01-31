## Argument Parser
import argparse
import os
import subprocess

# Parse all the required arguments

import sys

def get_script_path():
    return os.path.dirname(os.path.realpath(sys.argv[0]))

parser = argparse.ArgumentParser()

# Global arguments
parser.add_argument("-s", "--subject", help="Subject ID" )
parser.add_argument("-d", "--source_directory", help="Source Directory")
parser.add_argument("-rs","--reference_session")
parser.add_argument("-cs","--clinical_session")

# Parse the arguments
args = parser.parse_args()


# Identify the folders
subject = args.subject
source_dir = args.source_directory

reference_session = args.reference_session
clinical_session = args.clinical_session


# We need quotes around all file paths for the workspace file
module2_path = os.path.join(source_dir,subject,'derivatives','ieeg_recon', 'module2')

if os.path.exists(os.path.join(module2_path,'MRI_RAS')):
    mri_path = os.path.join(module2_path,'MRI_RAS',subject+'_'+reference_session+'_acq-3D_space-T00mri_T1w.nii.gz')
else:
    mri_path = os.path.join(module2_path,subject+'_'+reference_session+'_acq-3D_space-T00mri_T1w_ras.nii.gz')

spheres_labels = os.path.join(module2_path,subject+'_'+clinical_session+'_space-T01ct_desc-vox_electrodes_itk_snap_labels.txt')

spheres_path = os.path.join(module2_path,subject+'_'+reference_session+'_acq-3D_space-T00mri_T1w_electrode_spheres.nii.gz')

ct_path = os.path.join(module2_path,subject+'_'+clinical_session+'_acq-3D_space-T00mri_ct_thresholded.nii.gz')


reference_mri_name = subject+'_'+ reference_session + '_acq-3D_space-T00mri_T1w.nii.gz'

source_ct_name = subject+'_'+ clinical_session + '_acq-3D_space-T01ct_ct.nii.gz'


# Load the HTML scatterplot
html_scatterplot_name = os.path.join(module2_path,subject+'_'+reference_session+'_space-T00mri_desc-mm_electrodes_plot.html')

with open(html_scatterplot_name) as f:
    main_plot = f.readlines()[3:-2]

main_plot = ''.join(main_plot)

# Load the html report template
with open(os.path.join(get_script_path(),'sample_html.html')) as f:
    main_html = f.readlines()

main_html = ''.join(main_html)

main_html_replaced = main_html.replace("{html_plot}", main_plot)
main_html_replaced = main_html_replaced.replace("{subject}", subject)
main_html_replaced = main_html_replaced.replace("{source_dir}", os.path.join(source_dir,subject))
main_html_replaced = main_html_replaced.replace("{cs}", clinical_session)
main_html_replaced = main_html_replaced.replace("{rs}", reference_session)

main_html_replaced = main_html_replaced.replace("{reference_mri}", reference_mri_name)
main_html_replaced = main_html_replaced.replace("{post_ct}", source_ct_name)

main_html_replaced = main_html_replaced.replace("{source_dir}", os.path.join(source_dir,subject))

main_html_replaced = main_html_replaced.replace("{derivatives_dir}", os.path.join(source_dir,subject,'derivatives'))

svg_name_t00_mri_to_t01_ct = subject+'_'+reference_session+'_T00mri_T01ct_registration.svg'

main_html_replaced = main_html_replaced.replace("{svg_t00_to_t01_ct_mri}", svg_name_t00_mri_to_t01_ct)


# Write the workspace file
with open(os.path.join(os.path.join(source_dir,subject,'derivatives','ieeg_recon', 'module2'), subject+'_'+reference_session+'_report.html'), 'w') as f:
    f.write(main_html_replaced)

