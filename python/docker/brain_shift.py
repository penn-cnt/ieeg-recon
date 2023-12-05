import os


import numpy as np
import nibabel as nib
import ants


## Argument Parser
import argparse
parser = argparse.ArgumentParser()

# import module 3 atlas finder

#-db DATABSE -u USERNAME -p PASSWORD -size 20
parser.add_argument("-s", "--subject", help="Subject ID")
parser.add_argument("-d", "--source_directory", help="Source Directory")
parser.add_argument("-rs","--reference_session")
parser.add_argument("-cs","--clinical_session")
parser.add_argument("-fs","--freesurfer_dir")
args = parser.parse_args()


print(args.subject)

subject = args.subject

source_dir = args.source_directory
reference_session = args.reference_session
mod2_folder = os.path.join(source_dir,subject,'derivatives','ieeg_recon', 'module2')
brainshift_folder = os.path.join(mod2_folder,'brainshift')
os.makedirs(brainshift_folder)

clinical_module_dir = mod2_folder
mod3_folder = os.path.join(source_dir,subject,'derivatives','ieeg_recon', 'module3','brain_shift')
freesurfer_dir = args.freesurfer_dir

# Load the MRI
if os.path.exists(os.path.join(clinical_module_dir,'MRI_RAS', subject+'_'+reference_session+'_acq-3D_space-T00mri_T1w.nii.gz')):
    img_path = os.path.join(clinical_module_dir,'MRI_RAS', subject+'_'+reference_session+'_acq-3D_space-T00mri_T1w.nii.gz')
else:
    img_path = os.path.join(clinical_module_dir, subject+'_'+reference_session+'_acq-3D_space-T00mri_T1w_ras.nii.gz')

# Load the freesurfer data
lh_pial = nib.freesurfer.read_geometry(os.path.join(freesurfer_dir,'surf/lh.pial'))
rh_pial = nib.freesurfer.read_geometry(os.path.join(freesurfer_dir,'surf/rh.pial'))

# Load the freesurfer mesh
vertices_lh, triangles_lh = lh_pial
vertices_rh, triangles_rh = rh_pial

vertices = np.vstack([vertices_lh, vertices_rh])
triangles = np.vstack([triangles_lh, triangles_rh+len(vertices_lh)])

# Load the freesurfer and iEEG-recon MRIs, we need them for their affines
volume_fs = nib.load(os.path.join(freesurfer_dir,'mri/T1.mgz'))
volume_recon = nib.load(img_path)

# get transform from FreeSurfer MRI Surface RAS to iEEG-recon MRI Voxel Space
Torig = volume_fs.header.get_vox2ras_tkr()
affine_fs = volume_fs.affine
affine_target = volume_recon.affine
T = np.dot(np.linalg.inv(affine_target),np.dot(affine_fs,np.linalg.inv(Torig)))

# transform the vertices to the iEEG-recon MRI voxel space
def apply_affine(affine, coords):
    """Apply an affine transformation to 3D coordinates."""
    homogeneous_coords = np.hstack((coords, np.ones((coords.shape[0], 1))))
    transformed_coords = np.dot(homogeneous_coords, affine.T)
    return transformed_coords[:, :3]

transformed_vertices = apply_affine(T, vertices)

# load the electrode coordinates in MRI space
electrode_coordinates = np.loadtxt(os.path.join(mod2_folder, subject+'_'+reference_session+'_space-T00mri_desc-vox_electrodes.txt'))

# load the voxtool output to identify the electrode type
voxtool_out = np.loadtxt(os.path.join(source_dir,subject,args.clinical_session,'ieeg', args.subject+'_'+args.clinical_session+'_space-T01ct_desc-vox_electrodes.txt'), dtype=object)
electrode_type = voxtool_out[:,4]

grid_idx = np.where(electrode_type!='D')[0]
depth_idx = np.where(electrode_type=='D')[0]

##### Apply electrode snapping to the pial surface using constraints and optimization ######

from scipy.optimize import minimize

def compute_alpha(e0):
    N = len(e0)
    alpha = np.zeros((N, N))
    distances = np.array([[np.linalg.norm(e0[i] - e0[j]) for j in range(N)] for i in range(N)])
    
    # Find the 5 nearest neighbors for each electrode
    nearest_neighbors = np.argsort(distances, axis=1)[:, 1:6]  # Exclude the diagonal (distance to self)
    
    # Quantize the distances and determine the bin with the largest count
    quantized_bins = (distances // 0.2).astype(int)
    bins_counts = np.bincount(quantized_bins.flatten())
    fundamental_distance_bin = np.argmax(bins_counts)
    fundamental_distance = fundamental_distance_bin * 0.2
    
    threshold = 1.25 * fundamental_distance
    
    for i in range(N):
        for j in nearest_neighbors[i]:
            if distances[i][j] < threshold:
                alpha[i][j] = 1
    
    # Ensure each electrode has at least one connection
    for i in range(N):
        if np.sum(alpha[i]) == 0:
            nearest_electrode = np.argmin(distances[i])
            alpha[i][nearest_electrode] = 1
            
            for j in range(N):
                if distances[i][j] < 1.25 * distances[i][nearest_electrode]:
                    alpha[i][j] = 1
    
    return alpha

e0 = electrode_coordinates[grid_idx]
N = len(e0)
Nv = len(transformed_vertices)
e_s_distance_array = np.array([[np.linalg.norm(e0[i] - transformed_vertices[j]) for j in range(Nv)] for i in range(N)])

# Original distances between electrodes in a symmetric matrix form
d0 = np.array([[np.linalg.norm(e0[i] - e0[j]) for j in range(N)] for i in range(N)])

alpha = compute_alpha(e0)  # Random 0s and 1s for the alpha matrix

s = transformed_vertices[np.argmin(e_s_distance_array,axis=1)]

# define the objective function and run optimization

def objective(e_flat):
    e = e_flat.reshape(N, 3)
    
    # Computing the distances between the current electrode positions
    d = np.array([[np.linalg.norm(e[i] - e[j]) for j in range(N)] for i in range(N)])
    
    term1 = np.sum(np.square(e - e0))
    term2 = np.sum(alpha * ((d - d0)**2))
    
    return term1 + term2

def constraint(e_flat):
    e = e_flat.reshape(N, 3)
    return np.sum(np.square(e - s))

# Constraints in the form required by `minimize`
cons = {'type':'eq', 'fun': constraint}

# Initial guesses for e values
x0 = e0.flatten()

# Solve the optimization problem
result = minimize(objective, x0, constraints=cons)

optimized_e = result.x.reshape(N, 3)



#### Rename the module 2 outputs to before brainshift

os.rename(os.path.join(mod2_folder, subject+'_'+reference_session+'_space-T00mri_desc-vox_electrodes.txt'),
          os.path.join(mod2_folder, subject+'_'+reference_session+'_space-T00mri_desc-vox_electrodes_before_brainshift.txt'))

try:
    os.rename(os.path.join(mod2_folder, subject+'_'+reference_session+'_acq-3D_space-T00mri_T1w_electrode_spheres.nii.gz'),
              os.path.join(mod2_folder, subject+'_'+reference_session+'_acq-3D_space-T00mri_T1w_electrode_spheres_before_brainshift.nii.gz'))
except:
    os.rename(os.path.join(mod2_folder, subject+'_'+reference_session+'_acq-3D_space-T00mri_T1w_ras_electrode_spheres.nii.gz'),
              os.path.join(mod2_folder, subject+'_'+reference_session+'_acq-3D_space-T00mri_T1w_electrode_spheres_before_brainshift.nii.gz'))

#### Save the new module 2 outputs after brainshift

# save the new voxel coordinates

new_coords = np.zeros((len(grid_idx)+len(depth_idx),3))

# reassign the depths
new_coords[depth_idx] = electrode_coordinates[depth_idx]
new_coords[grid_idx] = optimized_e

np.savetxt(os.path.join(mod2_folder, subject+'_'+reference_session+'_space-T00mri_desc-vox_electrodes.txt'), new_coords)

# save the new electrode spheres
v = volume_recon.get_fdata()
new_spheres = np.zeros(v.shape, dtype=np.float64)

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

val = 0
for coord in new_coords:
    val += 1
    new_spheres = generate_sphere(new_spheres, int(coord[0]), int(coord[1]), int(coord[2]), 2, val)

nib.save(nib.Nifti1Image(new_spheres, volume_recon.affine),os.path.join(mod2_folder, subject+'_'+reference_session+'_acq-3D_space-T00mri_T1w_electrode_spheres.nii.gz'))