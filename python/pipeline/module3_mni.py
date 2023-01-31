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

## Add the Command Line Interface
from nipype.interfaces.base import CommandLineInputSpec, File, TraitedSpec,  CommandLine
from nipype.interfaces.c3 import C3dAffineTool

## Argument Parser
import argparse
parser = argparse.ArgumentParser()

#-db DATABSE -u USERNAME -p PASSWORD -size 20
parser.add_argument("-s", "--subject", help="Subject ID")
parser.add_argument("-d", "--source_directory", help="Source Directory")
parser.add_argument("-rs","--reference_session")


args = parser.parse_args()


print(args.subject)


#subjects = ['sub-RID0031','sub-RID0051','sub-RID0089','sub-RID0102','sub-RID0117','sub-RID0139','sub-RID0143','sub-RID0194','sub-RID0278','sub-RID0309','sub-RID0320','sub-RID0365','sub-RID0420','sub-RID0440','sub-RID0454','sub-RID0476','sub-RID0490','sub-RID0508','sub-RID0520','sub-RID0522','sub-RID0536','sub-RID0566','sub-RID0572','sub-RID0595','sub-RID0646','sub-RID0648','sub-RID0679']

subject = args.subject


#subjects = ['sub-RID0139']

source_dir = args.source_directory

mod2_folder = os.path.join(source_dir,subject,'derivatives','ieeg_recon', 'module2')
mod3_folder = os.path.join(source_dir,subject,'derivatives','ieeg_recon', 'module3','MNI')

# Define the SelectFiles
print(os.path.exists(os.path.join(mod2_folder,'MRI_RAS', subject+'_'+args.reference_session+'_acq-3D_space-T00mri_T1w.nii.gz')))
if os.path.exists(os.path.join(mod2_folder,'MRI_RAS', subject+'_'+args.reference_session+'_acq-3D_space-T00mri_T1w.nii.gz')):
    templates= {
    'mri_coords': '{subject}_{session}_space-T00mri_desc-vox_electrodes.txt',
    'preimplant_mri_ras': 'MRI_RAS/{subject}_{session_reference}_acq-3D_space-T00mri_T1w.nii.gz'}
else:
    templates= {
    'mri_coords': '{subject}_{session}_space-T00mri_desc-vox_electrodes.txt',
    'preimplant_mri_ras': '{subject}_{session_reference}_acq-3D_space-T00mri_T1w_ras.nii.gz'}

sf = Node(SelectFiles(templates),
            name='selectfiles')
sf.inputs.base_directory = mod2_folder
sf.inputs.subject = subject
sf.inputs.session = args.reference_session
sf.inputs.session_reference = args.reference_session


# Define SelectFiles for MNI template
templates= {'mni_template':'tpl-MNI152NLin2009cAsym_res-01_T1w.nii.gz'}

sf2 = Node(SelectFiles(templates),
            name='selectfiles2')
sf2.inputs.base_directory = str(pathlib.Path(__file__).parent.resolve())+'/../source_data/'
starting_dir = str(pathlib.Path(__file__).parent.resolve())
session = args.reference_session # session of the reference MRI
#session = sf.inputs.session

# Define data sink
datasink = Node(nio.DataSink(), name='sinker')
datasink.inputs.base_directory = mod3_folder


# Transform Coordinates in Input Array by Applying Transformation Matrix (or its inverse)
def transform_coordinates(in_mat ,coords_path, out_fname, inverse=True):

    import nibabel as nib
    import numpy as np
    import os

    message = "Transforming Coordinates"
    print(message)
    
    # Return an array with the vox coordinates
    def get_original_vox_coords(coords_path):
        coords = np.loadtxt(coords_path, dtype=object)
        coords = coords[:,1:4].astype(float).astype(int)
        return coords
    
    def get_first_and_last_cols_coords(coords_path):
        coords = np.loadtxt(coords_path, dtype=object)
        return coords[:,0], coords[:,4], coords[:,5], coords[:,6]

    # Affine manipulation
    # define the functions to apply the affine transform
    def split_affine(affine):
        return affine[:3,:3], affine[:3,3]

    def apply_affine(xyz, affine):
        M, abc = split_affine(affine)
        return (np.matmul(M,xyz) + abc).astype(int)


    coords = get_original_vox_coords(coords_path)

    transform_matrix = np.loadtxt(in_mat)
    print('Matrix loaded')
    # Invert the transform matrix if inverse bool is true
    if inverse==True:

        transform_matrix = np.linalg.pinv(transform_matrix)
    

    # Create empty array to store the coordinates
    coords_transformed = np.zeros([coords.shape[0],coords.shape[1]+4], dtype=object)

    for i in range(len(coords)):
        coords_transformed[i,1:4] = apply_affine(coords[i,:], transform_matrix).astype(int)

    coords_transformed = coords_transformed

    a,b,c,d = get_first_and_last_cols_coords(coords_path)
    coords_transformed[:,0] = a
    coords_transformed[:,4] = b
    coords_transformed[:,5] = c
    coords_transformed[:,6] = d

    np.savetxt(out_fname,coords_transformed, fmt='%s')

    return os.path.abspath(out_fname)

# Plot the Spheres of the Coordinates
def get_seg_vox_coords_mri(in_mri ,coords_path):

    import nibabel as nib
    import numpy as np
    import os

    message = "Generating MRI Coordinate Spheres"
    print(message)

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

    # Return an array with the vox coordinates
    def get_original_vox_coords(coords_path):
        coords = np.loadtxt(coords_path, dtype=object)
        coords = coords.astype(float).astype(int)
        return coords

    coords = get_original_vox_coords(coords_path)

    ct = nib.load(in_mri)
    ct_affine = ct.affine
    ct_shape = ct.shape

    # Create empty array to store the coordinates
    spheres = np.zeros(ct_shape)
    print(ct_shape)
    for i in range(len(coords)):
        print(i)
        try:
            spheres = generate_sphere(spheres, coords[i,0], coords[i,1], coords[i,2], 2, i+1)
        except IndexError:
            print('Index Error at coordinate: ',i+1)
    
    spheres_nifti = nib.Nifti1Image(spheres, ct_affine)

    def append_fname(fname, suffix='thresholded',delim='.nii.gz'):
        fname = fname.split('/')[-1]
        return fname.split(delim)[0] + '_' + suffix + delim 

    fname = append_fname(in_mri, suffix='electrode_spheres')

    nib.save(spheres_nifti,fname)

    return os.path.abspath(fname)


# Zero out the scaling row in the transform matrix
def zero_scaling(xfm_file):
    import numpy as np
    mat = np.loadtxt(xfm_file)
    mat[:,-1] = [0,0,0,1] 
    np.savetxt('zeroed_xfm.mat', mat)

    return os.path.abspath('zeroed_xfm.mat')

# This function is needed because NiPype skips the first line when saving certain files
def append_zeros(in_coords):
    import os
    import numpy as np
    mat = np.loadtxt(in_coords)
    zeros = np.array([0,0,0])
    appended = np.concatenate([zeros.reshape(1,-1), mat],axis=0)
    np.savetxt('prepended_coords.txt', appended)

    return os.path.abspath('prepended_coords.txt')


transform_coords_to_mri = MapNode(fsl.utils.WarpPoints(), name='transform_coords_to_mri', iterfield=['in_coords','xfm_file', 'src_file','dest_file'])

transform_coords_to_mri_mm = MapNode(fsl.utils.WarpPointsToStd(), name='transform_coords_to_mri_mm', iterfield=['in_coords','xfm_file', 'img_file', 'std_file'])

transform_ct_to_mri = MapNode(fsl.ApplyXFM(), name='transform_ct_to_mri', iterfield=['in_file','in_matrix_file','reference'])

# this is only used if Greedy is used
transform_mri_to_mni = MapNode(fsl.ApplyXFM(), name='transform_mri_to_mni', iterfield=['in_file','in_matrix_file','reference'])

transform_ct_to_ras = MapNode(fsl.utils.WarpPoints(), name='transform_ct_to_ras', iterfield=['in_coords','xfm_file', 'src_file','dest_file'])
#transform_mri_to_ras = MapNode(fsl.ApplyXFM(), name='transform_ct_to_ras', iterfield=['in_file','in_matrix_file','reference'])

plot_mri_coords = MapNode(name='plot_mri_coords',
                interface=Function(input_names=['in_mri','coords_path'],
                                    output_names=['out_file'],
                                    function=get_seg_vox_coords_mri), iterfield=['in_mri','coords_path'])


get_ct_to_mri_xfm = MapNode(fsl.ConvertXFM(),name='get_ct_to_mri_xfm', iterfield='in_file')
get_ct_to_mri_xfm.inputs.invert_xfm = True


prepend_zeros = MapNode(name='prepend_zeros', interface=Function(input_names=['in_coords'],
                                    output_names=['out_file'],
                                    function=append_zeros), iterfield='in_coords')

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
mni = Workflow(name="module1", base_dir=mod3_folder)
mni.connect([

        # Get Greedy transform between MRI in native and MNI space
        (sf,run_greedy_w_centering,[('preimplant_mri_ras','mov_img')]),
        (sf2,run_greedy_w_centering,[('mni_template','ref_img')]),
        (run_greedy_w_centering, datasink, [('out_file','greedy_affine')]),

        # Convert Greedy Transform to FSL
        (run_greedy_w_centering,convert_greedy,[('out_file','xfm_file')]),
        (sf,convert_greedy,[('preimplant_mri_ras','mov_img')]),
        (sf2,convert_greedy,[('mni_template','ref_img')]),

        # Transform the native MRI to the MNI space (since greedy does not do that for us)
        (convert_greedy, transform_mri_to_mni, [('out_file','in_matrix_file')]),
        (sf2, transform_mri_to_mni, [('mni_template','reference')]),
        (sf, transform_mri_to_mni, [('preimplant_mri_ras','in_file')]),
        (transform_mri_to_mni, datasink, [('out_file','mri_in_mni_space')]),

        ### Coordinate Transformation 

        # Transform MRI RAS coords to MNI coords in Voxel Space
        (convert_greedy, transform_coords_to_mri, [('out_file','xfm_file')]),
        (sf, transform_coords_to_mri, [('mri_coords','in_coords')]),
        (transform_mri_to_mni, transform_coords_to_mri, [('out_file','dest_file')]),
        (sf, transform_coords_to_mri, [('preimplant_mri_ras','src_file')]),
        (transform_coords_to_mri, datasink, [('out_file', 'coordinates_in_mri')]),

        # Plot final coordinates in MRI space as spheres
        (transform_coords_to_mri, plot_mri_coords, [('out_file', 'coords_path')]),
        (sf, plot_mri_coords, [('preimplant_mri_ras', 'in_mri')]),
        (plot_mri_coords, datasink, [('out_file', 'electrode_spheres_mri')]),
        
])

mni.run()

# Clean the output folder 

# # Remove the module cached folder
os.chdir(mod3_folder)

# Rename some files
os.rename('coordinates_in_mri/_transform_coords_to_mri0/'+subject+'_'+session+'_space-T00mri_desc-vox_electrodes_warped.txt','coordinates_in_mri/_transform_coords_to_mri0/' + subject+'_'+session+'_space-MNI152NLin2009cAsym_desc-vox_electrodes.txt')

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

# Rename some of the final files
try:
    os.rename(subject+'_'+session+'_acq-3D_space-T00mri_T1w_electrode_spheres.nii.gz', subject+'_'+session+'_acq-3D_space-MNI152NLin2009cAsym_T1w_electrode_spheres.nii.gz')
    os.rename(subject+'_'+session+'_acq-3D_space-T00mri_T1w_flirt.nii.gz', subject+'_'+session+'_acq-3D_space-MNI152NLin2009cAsym_T1w.nii.gz')
except:
    os.rename(subject+'_'+session+'_acq-3D_space-T00mri_T1w_ras_electrode_spheres.nii.gz', subject+'_'+session+'_acq-3D_space-MNI152NLin2009cAsym_T1w_electrode_spheres.nii.gz')
    os.rename(subject+'_'+session+'_acq-3D_space-T00mri_T1w_ras_flirt.nii.gz', subject+'_'+session+'_acq-3D_space-MNI152NLin2009cAsym_T1w.nii.gz')


# Generate an svg to visualize
# #%% Visualization
from niworkflows.viz.notebook import display
display(subject+'_'+session+'_acq-3D_space-MNI152NLin2009cAsym_T1w.nii.gz',starting_dir+'/../source_data/tpl-MNI152NLin2009cAsym_res-01_T1w.nii.gz')

command = 'mv report.svg '+subject+'_'+session+'_T00mri_MNI_registration.svg'
os.system(command)
