from email import header
from nipype.interfaces import (
    utility as niu,
    freesurfer as fs,
    fsl,
    image,
)

import pathlib

from nipype import Node, Workflow, SelectFiles, MapNode
from nipype.interfaces.utility import Function

import nipype.interfaces.io as nio
import os
from nipype.interfaces.ants.base import Info as ANTsInfo
from nipype.interfaces.ants import N4BiasFieldCorrection
from nipype.interfaces.image import Reorient

import numpy as np
import nibabel as nib
import ants


## Add the Command Line Interface
from nipype.interfaces.base import CommandLineInputSpec, File, TraitedSpec,  CommandLine
from nipype.interfaces.c3 import C3dAffineTool

## Argument Parser
import argparse
parser = argparse.ArgumentParser()

# import module 3 atlas finder

#-db DATABSE -u USERNAME -p PASSWORD -size 20
parser.add_argument("-s", "--subject", help="Subject ID")
parser.add_argument("-d", "--source_directory", help="Source Directory")
parser.add_argument("-rs","--reference_session")
parser.add_argument("-ps","--postop_session")
parser.add_argument("-r_postsurg","--postsurgical_radius")



args = parser.parse_args()


print(args.subject)


#subjects = ['sub-RID0031','sub-RID0051','sub-RID0089','sub-RID0102','sub-RID0117','sub-RID0139','sub-RID0143','sub-RID0194','sub-RID0278','sub-RID0309','sub-RID0320','sub-RID0365','sub-RID0420','sub-RID0440','sub-RID0454','sub-RID0476','sub-RID0490','sub-RID0508','sub-RID0520','sub-RID0522','sub-RID0536','sub-RID0566','sub-RID0572','sub-RID0595','sub-RID0646','sub-RID0648','sub-RID0679']

subject = args.subject


#subjects = ['sub-RID0139']

source_dir = args.source_directory

mod2_folder = os.path.join(source_dir,subject,'derivatives','ieeg_recon', 'module2')
mod3_folder = os.path.join(source_dir,subject,'derivatives','ieeg_recon', 'module3','postop')

# Define the SelectFiles
print(os.path.exists(os.path.join(mod2_folder,'MRI_RAS', subject+'_'+args.reference_session+'_acq-3D_space-T00mri_T1w.nii.gz')))
if os.path.exists(os.path.join(mod2_folder,'MRI_RAS', subject+'_'+args.reference_session+'_acq-3D_space-T00mri_T1w.nii.gz')):
    templates= {
    'mri_coords': '{subject}_{session}_space-T00mri_desc-vox_electrodes.txt',
    'preimplant_mri_ras': 'MRI_RAS/{subject}_{session_reference}_acq-3D_space-T00mri_T1w.nii.gz',
    'postop_mri': '../../../{postop_session}/anat/{subject}_{postop_session}_acq-3D_space-T02mri_T1w.nii.gz',
    'postop_mask': '../../resection_masks/{subject}_{postop_session}_space-T02mri_resection_mask.nii.gz'}
else:
    templates= {
    'mri_coords': '{subject}_{session}_space-T00mri_desc-vox_electrodes.txt',
    'preimplant_mri_ras': '{subject}_{session_reference}_acq-3D_space-T00mri_T1w_ras.nii.gz',
    'postop_mri': '../../../{postop_session}/anat/{subject}_{postop_session}_acq-3D_space-T02mri_T1w.nii.gz',
    'postop_mask': '../../resection_masks/{subject}_{postop_session}_space-T02mri_resection_mask.nii.gz'}

sf = Node(SelectFiles(templates),
            name='selectfiles')
sf.inputs.base_directory = mod2_folder
sf.inputs.subject = subject
sf.inputs.session = args.reference_session
sf.inputs.session_reference = args.reference_session
sf.inputs.postop_session = args.postop_session
session = args.postop_session

# Define data sink
datasink = Node(nio.DataSink(), name='sinker')
datasink.inputs.base_directory = mod3_folder


# this is only used if Greedy is used
transform_postopmri_to_preopmri = MapNode(fsl.ApplyXFM(), name='transform_postopmri_to_preopmri', iterfield=['in_file','in_matrix_file','reference'])

transform_postopmask_to_preopmri = MapNode(fsl.ApplyXFM(), name='transform_postopmask_to_preopmri', iterfield=['in_file','in_matrix_file','reference'])
transform_postopmask_to_preopmri.inputs.interp = 'nearestneighbour'

transform_ct_to_ras = MapNode(fsl.utils.WarpPoints(), name='transform_ct_to_ras', iterfield=['in_coords','xfm_file', 'src_file','dest_file'])
#transform_mri_to_ras = MapNode(fsl.ApplyXFM(), name='transform_ct_to_ras', iterfield=['in_file','in_matrix_file','reference'])


## Define command line interface for greedy

class CustomGreedyInputSpec(CommandLineInputSpec):
    ref_img = File(exists=True, mandatory=True, argstr='-d 3 -a -i %s', position=0, desc='the reference image')
    mov_img = File(exists=True, mandatory=True, argstr='%s -ia-identity -dof 6 -n 100x100x0x0 -m NMI', position=1, desc='the moving image')

    # Do not set exists=True for output files!
    out_file = File(mandatory=True, argstr='-o %s', position=2, desc='the output affine matrix')


class CustomGreedyInputSpec_w_image_centering(CommandLineInputSpec):
    ref_img = File(exists=True, mandatory=True, argstr='-d 3 -a -i %s', position=0, desc='the reference image')
    mov_img = File(exists=True, mandatory=True, argstr='%s -ia-image-centers -n 100x100x0x0 -m NMI', position=1, desc='the moving image')

    # Do not set exists=True for output files!
    out_file = File(mandatory=True, argstr='-o %s', position=2, desc='the output affine matrix')



class CustomGreedyOutputSpec(TraitedSpec):
    out_file = File(desc='the output affine matrix')

class CustomGreedy(CommandLine):
    _cmd = 'greedy'
    input_spec = CustomGreedyInputSpec
    output_spec = CustomGreedyOutputSpec

    def _list_outputs(self):

        # Get the attribute saved during _run_interface
        return {'out_file': self.inputs.out_file}

class CustomGreedy_w_image_centering(CommandLine):
    _cmd = 'greedy'
    input_spec = CustomGreedyInputSpec_w_image_centering
    output_spec = CustomGreedyOutputSpec

    def _list_outputs(self):

        # Get the attribute saved during _run_interface
        return {'out_file': self.inputs.out_file}


run_greedy = MapNode(CustomGreedy(), name='run_greedy', iterfield=['ref_img','mov_img'])
run_greedy.inputs.out_file = os.path.join(mod3_folder,'greedy_affine.mat')

run_greedy_w_centering = MapNode(CustomGreedy_w_image_centering(), name='run_greedy_w_centering', iterfield=['ref_img','mov_img'])
run_greedy_w_centering.inputs.out_file = os.path.join(mod3_folder,'greedy_affine.mat')

## Define command line interface for C3dAffineTool to get ITK file to RAS

class CustomC3DInputSpec(CommandLineInputSpec):
    ref_img = File(exists=True, mandatory=True, argstr='-ref %s', position=0, desc='the reference image')
    mov_img = File(exists=True, mandatory=True, argstr='-src %s', position=1, desc='the moving image')
    xfm_file = File(exists=True, mandatory=True, argstr='%s -ras2fsl', position=2, desc='the affine matrix in itk space')
    # Do not set exists=True for output files!
    out_file = File(mandatory=True, argstr='-o %s', position=3, desc='the output affine matrix in fsl space')

class CustomC3DOutputSpec(TraitedSpec):
    out_file = File(desc='the output affine matrix')

class CustomC3D(CommandLine):
    _cmd = 'c3d_affine_tool'
    input_spec = CustomC3DInputSpec
    output_spec = CustomC3DOutputSpec

    def _list_outputs(self):

        # Get the attribute saved during _run_interface
        return {'out_file': self.inputs.out_file}



## Add conversion of XFM from ITK to FSL
convert_greedy = MapNode(CustomC3D(), name='convert_greedy', iterfield=['ref_img','mov_img','xfm_file'])
convert_greedy.inputs.out_file = os.path.join(mod3_folder,'greedy_affine_fsl.mat')

## Add multiplication of affines to combine greedy with fsl
def matmul(xfm_1, xfm_2):
    import numpy as np
    import os
    affine_a = np.loadtxt(xfm_1)
    affine_b = np.loadtxt(xfm_2)
    affine_c = np.matmul(affine_b, affine_a)
    np.savetxt('affine_combined.mat',affine_c)
    
    return os.path.abspath('affine_combined.mat')

combine_affines = MapNode(name='combine_affines', interface=Function(input_names=['xfm_1','xfm_2'],
                                    output_names=['out_file'],
                                    function=matmul), iterfield=['xfm_1','xfm_2'])




#%%
postop = Workflow(name="module1", base_dir=mod3_folder)
postop.connect([

        # Get Greedy transform between MRI in native and MNI space
        (sf,run_greedy_w_centering,[('preimplant_mri_ras','ref_img')]),
        (sf,run_greedy_w_centering,[('postop_mri','mov_img')]),
        (run_greedy_w_centering, datasink, [('out_file','greedy_affine')]),

        # Convert Greedy Transform to FSL
        (run_greedy_w_centering,convert_greedy,[('out_file','xfm_file')]),
        (sf,convert_greedy,[('preimplant_mri_ras','ref_img')]),
        (sf,convert_greedy,[('postop_mri','mov_img')]),

        # Transform the postop MRI to preop MRI (since greedy does not do that for us)
        (convert_greedy, transform_postopmri_to_preopmri, [('out_file','in_matrix_file')]),
        (sf, transform_postopmri_to_preopmri, [('postop_mri','in_file')]),
        (sf, transform_postopmri_to_preopmri, [('preimplant_mri_ras','reference')]),
        (transform_postopmri_to_preopmri, datasink, [('out_file','postopmri_in_preopmri_space')]),


        # Transform the postop MASK to preop MRI space (since greedy does not do that for us)
        (convert_greedy, transform_postopmask_to_preopmri, [('out_file','in_matrix_file')]),
        (sf, transform_postopmask_to_preopmri, [('postop_mask','in_file')]),
        (sf, transform_postopmask_to_preopmri, [('preimplant_mri_ras','reference')]),
        (transform_postopmask_to_preopmri, datasink, [('out_file','postopmask_in_preopmri_space')]),

        
])

postop.run()

# Clean the output folder 

# # Remove the module cached folder
os.chdir(mod3_folder)

# Rename some files
os.rename('postopmask_in_preopmri_space/_transform_postopmask_to_preopmri0/'+subject+'_'+session+'_space-T02mri_resection_mask_flirt.nii.gz','postopmask_in_preopmri_space/_transform_postopmask_to_preopmri0/'+subject+'_'+session+'_space-T00mri_resection_mask.nii.gz')
os.rename('postopmri_in_preopmri_space/_transform_postopmri_to_preopmri0/'+subject+'_'+session+'_acq-3D_space-T02mri_T1w_flirt.nii.gz','postopmask_in_preopmri_space/_transform_postopmask_to_preopmri0/'+subject+'_'+session+'_acq-3D_space-T00mri_T1w.nii.gz')

#input('Check the outputs...')


# Remove the cached folder
command = 'rm -r module1'
os.system(command)

# # Move everything to derivatives folder
command = 'mv */*/* .'
os.system(command)

command = 'find . -type f -name "*.DS_Store" -delete'
os.system(command)

command = 'find . -empty -type d -delete'
os.system(command)

# # Rename some of the final files
# try:
#     os.rename(subject+'_'+session+'_acq-3D_space-T00mri_T1w_electrode_spheres.nii.gz', subject+'_'+session+'_acq-3D_space-MNI152NLin2009cAsym_T1w_electrode_spheres.nii.gz')
#     os.rename(subject+'_'+session+'_acq-3D_space-T00mri_T1w_flirt.nii.gz', subject+'_'+session+'_acq-3D_space-MNI152NLin2009cAsym_T1w.nii.gz')
# except:
#     os.rename(subject+'_'+session+'_acq-3D_space-T00mri_T1w_ras_electrode_spheres.nii.gz', subject+'_'+session+'_acq-3D_space-MNI152NLin2009cAsym_T1w_electrode_spheres.nii.gz')
#     os.rename(subject+'_'+session+'_acq-3D_space-T00mri_T1w_ras_flirt.nii.gz', subject+'_'+session+'_acq-3D_space-MNI152NLin2009cAsym_T1w.nii.gz')


# Generate an svg to visualize
# #%% Visualization
from niworkflows.viz.notebook import display
try:
    display(subject+'_'+session+'_acq-3D_space-T00mri_T1w.nii.gz',mod2_folder+'/MRI_RAS/'+subject+'_'+sf.inputs.session_reference+'_acq-3D_space-T00mri_T1w.nii.gz')
except:
    display(subject+'_'+session+'_acq-3D_space-T00mri_T1w.nii.gz',mod2_folder+'/'+subject+'_'+sf.inputs.session_reference+'_acq-3D_space-T00mri_T1w_ras.nii.gz')

command = 'mv report.svg '+subject+'_'+session+'_T00mri_T02mri_registration.svg'
os.system(command)

# %% Localize the electrodes within the mask as resected or not resected

# function to localize the electrodes within the resection mask


atlas = nib.load(subject+'_'+session+'_space-T00mri_resection_mask.nii.gz')

atlas_name = 'resected_electrodes'
clinical_module_dir = mod2_folder
atlas_module_dir = os.path.join(clinical_module_dir,'..','module3','postop')
reference_session = args.reference_session
radius = float(args.postsurgical_radius)

# define the labels for the resection mask atlas
roi_indices_resected = np.array([0,1])
roi_labels_resected = np.array(['Not Resected','Resected'])

 # Load the MRI
try:
    img = nib.load(os.path.join(clinical_module_dir,'MRI_RAS', subject+'_'+reference_session+'_acq-3D_space-T00mri_T1w.nii.gz'))
except FileNotFoundError:
    img = nib.load(os.path.join(clinical_module_dir, subject+'_'+reference_session+'_acq-3D_space-T00mri_T1w_ras.nii.gz'))

## Relevant function definitions
def split_affine(affine):
    return affine[:3,:3], affine[:3,3]

def apply_affine(xyz, affine):
    M, abc = split_affine(affine)
    return (np.matmul(M,xyz) + abc).astype(int)

def generate_sphere(A, x0,y0,z0, radius, value):
    ''' 
        A: array where the sphere will be drawn
        radius : radius of circle inside A which will be filled with ones.
        x0,y0,z0: coordinates for the center of the sphere within A
        value: value to fill the sphere with
    '''

    ''' AA : copy of A (you don't want the original copy of A to be overwritten.) '''
    AA = A



    for x in range(x0-radius, x0+radius+1):
        for y in range(y0-radius, y0+radius+1):
            for z in range(z0-radius, z0+radius+1):
                ''' deb: measures how far a coordinate in A is far from the center. 
                        deb>=0: inside the sphere.
                        deb<0: outside the sphere.'''   
                deb = radius - ((x0-x)**2 + (y0-y)**2 + (z0-z)**2)**0.5 
                if (deb)>=0: AA[x,y,z] = value
    return AA
def most_common(lst):
    return max(set(lst), key=lst.count)

def match_label(index,index_list, label_list):
    return label_list[np.where(index_list==index)[0][0]]

def unique(list1):
  
    # initialize a null list
    unique_list = []
  
    # traverse for all elements
    for x in list1:
        # check if exists in unique_list or not
        if x not in unique_list:
            unique_list.append(x)
    return unique_list


def most_common_list(lst):
    unique_list = unique(sorted(lst, key = lst.count,
                                reverse = True))
    
    unique_percent = list(map(lambda x: lst.count(x)/len(lst), unique_list))

    return unique_list, unique_percent

def match_label_list(index_list_list, index_list_orig, label_list):
    label_list_list = []
    for i in range(len(index_list_list)):
        label_list_list.append(match_label(index_list_list[i], index_list_orig, label_list))
    return label_list_list

def get_regions_resected_from_coords(atlas, atlas_name, img, roi_indices, roi_labels):


    pixdims = atlas.header['pixdim'][1:4]

    max_dim = np.max(pixdims)
    min_radius = np.round(1/max_dim) # the minimum possible radius given the voxel size

    # load the electrodes from the module 2 folder
    coords = np.loadtxt(os.path.join(clinical_module_dir, subject+'_'+reference_session+'_space-T00mri_desc-vox_electrodes.txt'))
    electrode_names = np.loadtxt(os.path.join(clinical_module_dir, subject+'_electrode_names.txt'), dtype=object)

    # load the atlas
    atlas_data = atlas.get_fdata()

    electrode_assignment_index = []
    electrode_assignment_label = []

    electrode_assignment_index_list = []
    electrode_assignment_label_list = []


    for i in range(len(coords)):
        coords_atlas = apply_affine(coords[i,:],np.matmul(np.linalg.pinv(atlas.affine),img.affine))
        
        mask = np.zeros(atlas.shape)

        mask = generate_sphere(mask, coords_atlas[0], coords_atlas[1], coords_atlas[2], int(max([radius/max_dim, min_radius])), 1)

        index = most_common(list(atlas_data[mask==1]))
        label = match_label(index, roi_indices, roi_labels)

        electrode_assignment_index.append(index)
        electrode_assignment_label.append(label)

        # Store a sorted list of possible labels
        unique_list, percent_list = most_common_list(list(atlas_data[mask==1]))
        electrode_assignment_index_list.append(percent_list)
        electrode_assignment_label_list.append(match_label_list(unique_list,roi_indices, roi_labels))
                    

    atlas_coords = np.zeros((len(coords), 8), dtype=object)

    atlas_coords[:,0] = electrode_names
    atlas_coords[:,1:4] = coords
    atlas_coords[:,4] = electrode_assignment_index
    atlas_coords[:,5] = electrode_assignment_label

    np.savetxt(os.path.join(atlas_module_dir, subject+'_'+reference_session+'_space-T00mri_atlas-'+atlas_name+'_radius-'+str(radius)+'_desc-vox_coordinates.txt') ,atlas_coords, fmt='%s')

    import pandas as pd
    df_coords = pd.DataFrame()
    df_coords['name'] = electrode_names
    df_coords['x'] = coords[:,0]
    df_coords['y'] = coords[:,1]
    df_coords['z'] = coords[:,2]
    df_coords['index'] = electrode_assignment_index
    df_coords['label'] = electrode_assignment_label

    df_coords.to_csv(os.path.join(atlas_module_dir, subject+'_'+reference_session+'_space-T00mri_atlas-'+atlas_name+'_radius-'+str(radius)+'_desc-vox_coordinates.csv'))

    df_coords['labels_sorted'] = electrode_assignment_label_list
    df_coords['percent_assigned'] = electrode_assignment_index_list

    df_coords.to_json(os.path.join(atlas_module_dir, subject+'_'+reference_session+'_space-T00mri_atlas-'+atlas_name+'_radius-'+str(radius)+'_desc-vox_coordinates.json'), lines=True, orient='records')

    # Generate a segmentation mask of the sampled regions

    seg_mask = np.zeros(atlas.shape)

    atlas_vals = atlas.get_fdata()

    for i in range(len(electrode_assignment_index)):
        seg_mask[electrode_assignment_index[i]==atlas_vals] = 1

    seg_mask_nifti = nib.Nifti1Image(seg_mask, atlas.affine)
    nib.save(seg_mask_nifti, os.path.join(atlas_module_dir, subject+'_'+reference_session+'_space-T00mri_atlas-'+atlas_name+'_radius-'+str(radius)+'_sampling_mask.nii.gz'))



get_regions_resected_from_coords(atlas, atlas_name, img, roi_indices_resected, roi_labels_resected)


#######  make final segmentation for visualizing overlap of electrodes with resection mask
electrode_spheres_path = os.path.join(mod2_folder,subject+'_'+reference_session+'_acq-3D_space-T00mri_T1w_electrode_spheres.nii.gz')
electrode_spheres_in_postsurg_space = os.path.join(mod2_folder,subject+'_'+reference_session+'_acq-3D_space-T00mri_T1w_electrode_spheres_resliced_to_presurg.nii.gz')
reference_image_path = subject+'_'+session+'_space-T00mri_resection_mask.nii.gz'

# Define the command to be executed
command = "c3d " + reference_image_path + " " + electrode_spheres_path + " -interpolation NearestNeighbor -reslice-identity -o " + electrode_spheres_in_postsurg_space

# Execute the command using the os.system() function
os.system(command)



affine = nib.load(reference_image_path).affine

mask = nib.load(reference_image_path).get_fdata()

electrodes = nib.load(electrode_spheres_in_postsurg_space).get_fdata()

# make electrode labels = 1
electrodes[electrodes>0] = 1

# make mask label = 2
mask[mask>0] = 2

final_seg = electrodes + mask

nib.save(nib.Nifti1Image(final_seg, affine),subject+'_'+session+'_space-T00mri_resection_mask+electrodes.nii.gz')
