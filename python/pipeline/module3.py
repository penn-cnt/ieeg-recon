import nibabel as nib
import numpy as np
import pandas as pd


from email import header
from nipype.interfaces import (
    utility as niu,
    freesurfer as fs,
    fsl
)

from nipype import Node, Workflow, SelectFiles, MapNode
from nipype.interfaces.utility import Function

import os

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


## Argument Parser
import argparse
parser = argparse.ArgumentParser()

#-db DATABSE -u USERNAME -p PASSWORD -size 20
parser.add_argument("-s", "--subject", help="Subject ID")
parser.add_argument("-rs","--reference_session")
parser.add_argument("-ird", "--ieeg_recon_dir", help="Source iEEG Recon Directory")
parser.add_argument("-a", "--atlas_path", help="Atlas Path")
parser.add_argument("-an", "--atlas_name", help="Atlas Name")
parser.add_argument("-lut", "--atlas_lookup_table", help="Atlas Lookup Table")
parser.add_argument("-ri", "--roi_indices", help="ROI Indices")
parser.add_argument("-rl", "--roi_labels", help="ROI Labels")
parser.add_argument("-r","--radius",help="Radius for Electrode atlast Assignment")
parser.add_argument("-apn","--ants_pynet", help="Run AntsPyNet DKT Segmentation",action='store_true')

# Parse the arguments
args = parser.parse_args()
subject = args.subject
radius = int(args.radius)

# Assign names to files and folders
atlas_name = args.atlas_name
clinical_module_dir = os.path.join(args.ieeg_recon_dir,'module2')
atlas_module_dir = os.path.join(clinical_module_dir,'..','module3')
reference_session = args.reference_session
if os.path.exists(atlas_module_dir) == False:
    os.mkdir(atlas_module_dir)


# Check if the AntsPyNet flag is specified for the segmentation, if so, apply it to the MRI
if args.ants_pynet:
    import ants
    import antspynet
    
    # Load the MRI
    try:
        img = ants.image_read(os.path.join(clinical_module_dir,'MRI_RAS', subject+'_'+reference_session+'_acq-3D_space-T00mri_T1w.nii.gz'))
    except:
        img = ants.image_read(os.path.join(clinical_module_dir, subject+'_'+reference_session+'_acq-3D_space-T00mri_T1w_ras.nii.gz'))
    
    print('Performing AntsPyNet Segmentation...')
    antspynet_segmentation = antspynet.desikan_killiany_tourville_labeling(img)
    antspynet_out_path = os.path.join(atlas_module_dir, subject+'_'+reference_session+'_space-T00mri_atlas-DKTantspynet.nii.gz')
    ants.image_write(antspynet_segmentation, antspynet_out_path)

    print('Performing Atropos Segmentation...')
    atropos_segmentation = antspynet.deep_atropos(img)['segmentation_image']
    atropos_out_path = os.path.join(atlas_module_dir, subject+'_'+reference_session+'_space-T00mri_atlas-atropos.nii.gz')
    ants.image_write(atropos_segmentation, atropos_out_path)
    

# Load the MRI, but now in nibabel format 
try:
    img = nib.load(os.path.join(clinical_module_dir,'MRI_RAS', subject+'_'+reference_session+'_acq-3D_space-T00mri_T1w.nii.gz'))
except FileNotFoundError:
    img = nib.load(os.path.join(clinical_module_dir, subject+'_'+reference_session+'_acq-3D_space-T00mri_T1w_ras.nii.gz'))


## If AntsPyNet is not specified, then an atlas with its corresponding Look-up table must be specified
if args.ants_pynet == False:

    # Load the atlas labels from either a lookup table CSV or from a pair of files specifying the 
    # labels and values
    # Load the atlas
    atlas = nib.load(args.atlas_path)
    if args.atlas_lookup_table == None:
        try:
            roi_indices = np.loadtxt(args.roi_indices, dtype=int)
            roi_labels = np.loadtxt(args.roi_labels, dtype=object)
        except:
            print('No atlas lookup table, or indices/labels files were provided')
    else:
        lut = pd.read_csv(args.atlas_lookup_table, header=None, delimiter=',').values

        roi_indices = lut[:,0]
        roi_labels = lut[:,1]
else:
    atlas_dkt = nib.load(antspynet_out_path)
    atlas_name_dkt = 'DKTantspynet'
    lut_dkt = pd.read_csv('source_data/antspynet_labels.csv',header=None, delimiter=',').values
    roi_indices_dkt = lut_dkt[:,0]
    roi_labels_dkt = lut_dkt[:,1]

    atlas_atropos = nib.load(atropos_out_path)
    atlas_name_atropos = 'atropos'
    lut_atropos = pd.read_csv('source_data/atropos_labels.csv',header=None, delimiter=',').values
    roi_indices_atropos = lut_atropos[:,0]
    roi_labels_atropos = lut_atropos[:,1]

def get_regions_from_coords(atlas, atlas_name, img, roi_indices, roi_labels):

    pixdims = atlas.header['pixdim'][1:4]

    max_dim = np.max(pixdims)
    min_radius = np.round(1/max_dim) # the minimum possible radius given the voxel size

    coords = np.loadtxt(os.path.join(clinical_module_dir, subject+'_'+reference_session+'_space-T00mri_desc-vox_electrodes.txt'))
    electrode_names = np.loadtxt(os.path.join(clinical_module_dir, subject+'_electrode_names.txt'), dtype=object)


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

    if 'dkt' in atlas_name.lower():
        electrode_assignment_index = list(set(electrode_assignment_index)-{0,2,41})

    electrode_assignment_index = list(set(electrode_assignment_index)-{0})


    for i in range(len(electrode_assignment_index)):
        seg_mask[electrode_assignment_index[i]==atlas_vals] = 1

    seg_mask_nifti = nib.Nifti1Image(seg_mask, atlas.affine)
    nib.save(seg_mask_nifti, os.path.join(atlas_module_dir, subject+'_'+reference_session+'_space-T00mri_atlas-'+atlas_name+'_radius-'+str(radius)+'_sampling_mask.nii.gz'))


if args.ants_pynet == False:

    get_regions_from_coords(atlas, args.atlas_name, img, roi_indices, roi_labels)
else:

    get_regions_from_coords(atlas_dkt, atlas_name_dkt, img, roi_indices_dkt, roi_labels_dkt)
    get_regions_from_coords(atlas_atropos, atlas_name_atropos, img, roi_indices_atropos, roi_labels_atropos)
