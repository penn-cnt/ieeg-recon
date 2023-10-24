# this code converts any input atlas from MNI space to subject space
import pathlib

from nipype import Node, Workflow, SelectFiles, MapNode
from nipype.interfaces.utility import Function

import nipype.interfaces.io as nio
import os
import shutil
import glob
from nipype.interfaces.ants import ApplyTransforms, ApplyTransformsToPoints


## Argument Parser
import argparse
parser = argparse.ArgumentParser()

#-db DATABSE -u USERNAME -p PASSWORD -size 20
parser.add_argument("-s", "--subject", help="Subject ID")
parser.add_argument("-d", "--source_directory", help="Source Directory")
parser.add_argument("-rs","--reference_session")
parser.add_argument("-a", "--atlas_path")
parser.add_argument("-an", "--atlas_name")

args = parser.parse_args()


print(args.subject)


subject = args.subject


source_dir = args.source_directory

mod2_folder = os.path.join(source_dir,subject,'derivatives','ieeg_recon', 'module2')
mod3_folder = os.path.join(source_dir,subject,'derivatives','ieeg_recon', 'module3','MNI')

# Define the SelectFiles
if os.path.exists(os.path.join(mod2_folder,'MRI_RAS', subject+'_'+args.reference_session+'_acq-3D_space-T00mri_T1w.nii.gz')):
    templates= {
    'preimplant_mri_ras': 'MRI_RAS/{subject}_{session_reference}_acq-3D_space-T00mri_T1w.nii.gz',
    'mni_to_t00_xfm':'../module3/MNI/{subject}_{session_reference}_MNI152NLin2009cAsym_to_T00mri.h5',
    'atlas':args.atlas_path}
else:
    templates= {
    'preimplant_mri_ras': '{subject}_{session_reference}_acq-3D_space-T00mri_T1w_ras.nii.gz',
    'mni_to_t00_xfm':'../module3/MNI/{subject}_{session_reference}_MNI152NLin2009cAsym_to_T00mri.h5',
    'atlas':args.atlas_path}

sf = Node(SelectFiles(templates),
            name='selectfiles')
sf.inputs.base_directory = mod2_folder
sf.inputs.subject = subject
sf.inputs.session = args.reference_session
sf.inputs.session_reference = args.reference_session

# Define DataSink
# Define data sink
datasink = Node(nio.DataSink(), name='sinker')
datasink.inputs.base_directory = mod3_folder

# Define the ApplyTransforms from ANTs
apply_ants_transform_to_atlas = MapNode(ApplyTransforms(), name='apply_ants_transform_to_atlas', iterfield=['transforms'])
apply_ants_transform_to_atlas.inputs.interpolation = 'NearestNeighbor'

# perform the transform
mni = Workflow(name="module1", base_dir=mod3_folder)
mni.connect([


        # Apply the transform to the CT file
        (sf, apply_ants_transform_to_atlas, [('atlas','input_image')]),
        (sf, apply_ants_transform_to_atlas, [('preimplant_mri_ras','reference_image')]),
        (sf, apply_ants_transform_to_atlas, [('mni_to_t00_xfm','transforms')]),
        (apply_ants_transform_to_atlas, datasink, [('output_image','atlas_in_mri')]),
        
        
])

mni.run()

# rename the output
os.chdir(mod3_folder)
transformed_atlas_file = glob.glob('atlas_in_mri/_apply_ants_transform_to_atlas0/*')[0]
os.rename(transformed_atlas_file,'../'+args.subject+'_'+args.reference_session+'_space-T00mri_atlas-'+args.atlas_name+'.nii.gz')


# remove unnecessary workfiles
command = 'find . -type f -name "*.DS_Store" -delete'
os.system(command)

command = 'find . -type d -delete'
os.system(command)

command = 'rm -r module1'
os.system(command)

