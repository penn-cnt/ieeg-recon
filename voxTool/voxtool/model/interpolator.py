#!/usr/bin/python

""" This utility module interpolates all electrode grids in a strip or grid configuration.
"""

__version__ = '0.1'
__author__ = 'Xavier Islam'
__email__ = 'islamx@seas.upenn.edu'
__copyright__ = "Copyright 2016, University of Pennsylvania"
__credits__ = ["iped", "islamx", "lkini", "srdas",
               "jmstein", "kadavis"]
__status__ = "Development"

import math

import nibabel as nib
import numpy as np
import numpy.linalg
import numpy.matlib

import scipy.ndimage.measurements
import scipy.ndimage.morphology
import scipy.spatial


def normalize(v):
    """ returns the unit vector in the direction of v

    @param v : Vector (numpy)
    @rtype numpy array
    """

    norm = np.linalg.norm(v)
    if norm == 0:
        return v
    return v / norm


def totuple(a):
    """ returns numpy arrays as tuples
    """

    try:
        return tuple(totuple(i) for i in a)
    except TypeError:
        return a


def interpol(coor1, coor2, coor3, m, n):
    """ returns the coordinates of all interpolated electrodes in a
        grid/strip of configuration m x n along with numeric labels in
        order.

    It takes as inputs up to three sample voxel coordinates representing
        the oriented corners of the grid as well as the grid
        configuration (e.g. 8x8). The order of the corners determines
        the label order; i.e., coor1 corresponds to 1, coor2 corresponds
         to n*(m-1) + 1, coor3 corresponds to m*n.

    @param coor1 : Coordinate corresponding to label 1
    @param coor2 : Coordinate corresponding to the first electrode in
        the last row
    @param coor3 : Coordinate corresponding to the last electrode
        (optional in case of strip)
    @param m : Number of rows
    @param n : Number of columns
    @type coor1: list
    @type coor2: list
    @type coor3: list
    @type m: int
    @type n: int
    @rtype dict

    Example:
        >> interpol([77, 170, 81],[65, 106, 112],[104, 121, 158],8,8)
    """

    # Check if no third coordinate is present
    if not list(coor3):
        if m != 1 and n != 1:
            raise ValueError('Third corner coordinate not given despite\
                configuration being a grid.')
        return interpol_strip(coor1, coor2, m, n)
    else:
        if m == 1 or n == 1:
            raise ValueError('Third corner coordinate given despite\
                configuration being a strip.')
        return interpol_grid(coor1, coor2, coor3, m, n)


def rotation_matrix(axis, theta):
    """
    Return the rotation matrix associated with counterclockwise rotation about
    the given axis by theta radians.
    """
    axis = np.asarray(axis)
    axis = axis / math.sqrt(np.dot(axis, axis))
    a = math.cos(theta / 2.0)
    b, c, d = -axis * math.sin(theta / 2.0)
    aa, bb, cc, dd = a * a, b * b, c * c, d * d
    bc, ad, ac, ab, bd, cd = b * c, a * d, a * c, a * b, b * d, c * d
    return np.array([[aa + bb - cc - dd, 2 * (bc + ad), 2 * (bd - ac)],
                     [2 * (bc - ad), aa + cc - bb - dd, 2 * (cd + ab)],
                     [2 * (bd + ac), 2 * (cd - ab), aa + dd - bb - cc]])


def interpol_grid_helper(coor1, coor1_coord, coor2, coor2_coord, coor3, coor3_coord):
    """
    ??? FIX when time possible

    :param coor1:
    :param coor1_coord:
    :param coor2:
    :param coor2_coord:
    :param coor3:
    :param coor3_coord:
    :param m:
    :param n:
    :return:
    """

    coor1_p = np.array([coor1_coord[1], -coor1_coord[0]])
    coor2_p = np.array([coor2_coord[1], -coor2_coord[0]])
    coor3_p = np.array([coor3_coord[1], -coor3_coord[0]])
    delta = np.array([-coor1_coord[1], coor1_coord[0]])

    coor1_p = coor1_p + delta
    coor2_p = coor2_p + delta
    coor3_p = coor3_p + delta

    coor21 = coor2 - coor1
    coor31 = coor3 - coor1

    x21 = coor2_p - coor1_p
    x31 = coor3_p - coor1_p
    theta_x = np.arctan(x21[1] * 1.0 / x21[0])
    theta_y = np.arctan(x31[0] * 1.0 / x31[1])
    print(x21, x31, theta_x, theta_y)

    cross_product = np.cross(coor21, coor31)
    axis = cross_product / np.sqrt(np.sum(np.square(cross_product), axis=0))

    if (x21[0] < 0):
        if (x21[1] < 0):
            res_x = np.dot(rotation_matrix(axis, np.pi - theta_x), coor2)
        else:
            res_x = np.dot(rotation_matrix(axis, np.pi + theta_x), coor2)
    else:
        res_x = np.dot(rotation_matrix(axis, theta_x), coor2)
    print(res_x)
    if (x21[0]):
        res_x = res_x / np.abs(x21[0])
    else:
        res_x = res_x / np.abs(x21[1])

    if (x31[0] < 0):
        res_y = np.dot(rotation_matrix(axis, np.pi - theta_y), coor3)
    else:
        res_y = np.dot(rotation_matrix(axis, theta_y), coor3)
    print(res_y)
    if (x31[1]):
        res_y = res_y / x31[1]
    else:
        res_y = res_y / x31[0]
    print(res_x, res_y)


def interpol_grid(coor1, coor2, coor3, m, n):
    """ returns the coordinates of all interpolated electrodes in a
        grid of configuration m x n along with numeric labels in
        order.

    This is the worker function of interpol(...).

    @param coor1 : Coordinate corresponding to label 1
    @param coor2 : Coordinate corresponding to the first electrode in
        the last row
    @param coor3 : Coordinate corresponding to the last electrode
        (optional in case of strip)
    @param m : Number of rows
    @param n : Number of columns
    @type coor1: list
    @type coor2: list
    @type coor3: list
    @type m: int
    @type n: int
    @rtype dict

    Example:
        >> interpol([77, 170, 81],[65, 106, 112],[104, 121, 158],8,8)
    """
    # Turn input coordinates (which are presumably lists)
    # into numpy arrays.
    coor1 = np.asarray(coor1)
    coor2 = np.asarray(coor2)
    coor3 = np.asarray(coor3)

    # Figure out points A, B, and C of grid and respective vectors
    # (A2B and B2C) that define grid.
    vec1 = np.subtract(coor1, coor2)
    vec2 = np.subtract(coor2, coor3)
    vec3 = np.subtract(coor1, coor3)
    mag_1 = np.linalg.norm(vec1)
    mag_2 = np.linalg.norm(vec2)
    mag_3 = np.linalg.norm(vec3)

    # Reorient the vectors appropriately
    if (mag_1 >= mag_2) and (mag_1 >= mag_3):
        A = coor1
        B = coor3
        C = coor2
        A2B = -1 * vec3
        B2C = vec2
    if (mag_2 >= mag_1) and (mag_2 >= mag_3):
        A = coor2
        B = coor1
        C = coor3
        A2B = vec1
        B2C = -1 * vec3
    if (mag_3 >= mag_1) and (mag_3 >= mag_2):
        A = coor1
        B = coor2
        C = coor3
        A2B = -1 * vec1
        B2C = -1 * vec2

    # Compute unit vectors
    unit_A2B = normalize(A2B)
    unit_B2C = normalize(B2C)
    mag_A2B = np.linalg.norm(A2B)
    mag_B2C = np.linalg.norm(B2C)

    # Initialize outputs
    names = []
    elec_coor = []
    new_corr = A
    elec_coor.append(totuple(new_corr))
    count = 1
    names.append("GRID %d" % count)

    # Use for loops to deduce locations of electrodes.
    for j in range(n):
        for i in range(m - 1):
            new_corr = np.add(new_corr, (mag_A2B / (m - 1)) * (unit_A2B))
            elec_coor.append(totuple(new_corr))
            count += 1
            names.append("GRID %d" % count)
        new_corr = np.add(A, (mag_B2C / (n - 1)) * (j + 1) * (unit_B2C))
        elec_coor.append(totuple(new_corr))
        count += 1
        names.append("GRID %d" % count)
    names = names[0:-1]
    elec_coor = elec_coor[0:-1]
    # pairs = dict(zip(names, elec_coor))
    return elec_coor


def interpol_grid_to_mask(coor1, coor2, coor3, m, n, mask):
    """ returns the coordinates of all interpolated electrodes in a
        grid of configuration m x n along with numeric labels in
        order.

    This is the worker function of interpol(...).

    @param coor1 : Coordinate corresponding to label 1
    @param coor2 : Coordinate corresponding to the first electrode in
        the last row
    @param coor3 : Coordinate corresponding to the last electrode
        (optional in case of strip)
    @param m : Number of rows
    @param n : Number of columns
    @type coor1: list
    @type coor2: list
    @type coor3: list
    @type m: int
    @type n: int
    @rtype dict

    Example:
        >> interpol([77, 170, 81],[65, 106, 112],[104, 121, 158],8,8)
    """
    # Turn input coordinates (which are presumably lists)
    # into numpy arrays.
    coor1 = np.asarray(coor1)
    coor2 = np.asarray(coor2)
    coor3 = np.asarray(coor3)

    # Figure out points A, B, and C of grid and respective vectors
    # (A2B and B2C) that define grid.
    vec1 = np.subtract(coor1, coor2)
    vec2 = np.subtract(coor2, coor3)
    vec3 = np.subtract(coor1, coor3)
    mag_1 = np.linalg.norm(vec1)
    mag_2 = np.linalg.norm(vec2)
    mag_3 = np.linalg.norm(vec3)

    # Reorient the vectors appropriately
    if (mag_1 >= mag_2) and (mag_1 >= mag_3):
        A = coor1
        B = coor3
        C = coor2
        A2B = -1 * vec3
        B2C = vec2
    if (mag_2 >= mag_1) and (mag_2 >= mag_3):
        A = coor2
        B = coor1
        C = coor3
        A2B = vec1
        B2C = -1 * vec3
    if (mag_3 >= mag_1) and (mag_3 >= mag_2):
        A = coor1
        B = coor2
        C = coor3
        A2B = -1 * vec1
        B2C = -1 * vec2

    # Compute unit vectors
    unit_A2B = normalize(A2B)
    unit_B2C = normalize(B2C)
    mag_A2B = np.linalg.norm(A2B)
    mag_B2C = np.linalg.norm(B2C)

    # Initialize outputs
    elec_coor = []
    new_corr = A
    elec_coor.append(totuple(new_corr))
    count = 1

    # Use for loops to deduce locations of electrodes.
    for j in range(n):
        for i in range(m - 1):
            new_corr = np.add(new_corr, (mag_A2B / (m - 1)) * (unit_A2B))
            elec_coor.append(totuple(new_corr))
            count += 1
        new_corr = np.add(A, (mag_B2C / (n - 1)) * (j + 1) * (unit_B2C))
        elec_coor.append(totuple(new_corr))
        count += 1
    elec_coor = elec_coor[0:-1]
    warped_elec_coor = np.array(elec_coor)

    # initialize minimization parameters
    new_warped_elec_coor = np.copy(warped_elec_coor)
    mask_ind = np.array(np.where(mask))
    step = 1
    delta = 10000
    iter_i = 1
    end_delta = 2

    while delta > end_delta:
        for ii, coor in enumerate(warped_elec_coor):
            dist = np.sqrt(np.square(coor[0] - mask_ind[0, :]) + np.square(coor[1] - mask_ind[1, :]) + np.square(
                coor[2] - mask_ind[2, :]))
            near_mask = mask_ind[:, dist < 20]

            if not (dist < 1).any():
                edist = np.sqrt(np.sum(np.square(coor - warped_elec_coor), axis=1))
                neighbors = warped_elec_coor[edist < 10, :].T
                cost = np.zeros(near_mask.shape[1], )
                for neighbor in neighbors.T:
                    cost += np.sum(np.square(np.array([neighbor]).T - near_mask), axis=0)

                ind = np.argmax(cost)
                v = near_mask[:, ind] - coor
                v = v / numpy.linalg.norm(v, 2) * step
                new_warped_elec_coor[ii] = coor + v
            else:
                new_warped_elec_coor[ii] = coor

        delta = np.sum(np.sum(np.square(warped_elec_coor - new_warped_elec_coor)))
        warped_elec_coor = np.copy(new_warped_elec_coor)

        print(delta)
        tmp = np.copy(mask)
        for k in warped_elec_coor:
            tmp[int(k[0]), int(k[1]), int(k[2])] = 2
        if np.mod(iter_i, 5) == 0:
            nib.save(nib.Nifti1Image(tmp, np.eye(4)), '/Users/lkini/Documents/LittLab/Data/tmp/tmp_%i.nii.gz' % iter_i)
        iter_i += 1





def interpol_strip(coor1, coor2, m, n):
    """ returns the coordinates of all interpolated electrodes in a
        grid of configuration m x n along with numeric labels in
        order.

    This is the worker function of interpol(...).

    @param coor1 : Coordinate corresponding to label 1
    @param coor2 : Coordinate corresponding to the last electrode in
        strip
    @param m : Number of rows (could be 1)
    @param n : Number of columns (could be 1)
    @type coor1: list
    @type coor2: list
    @type m: int
    @type n: int
    @rtype dict

    Example:
        >> interpol([77, 170, 81],[65, 106, 112],6,1)
    """

    # Turn input coordinates (which are presumably lists) into numpy arrays.
    A = np.asarray(coor1)
    B = np.asarray(coor2)
    A2B = np.subtract(coor2, coor1)

    # Compute unit vectors
    unit_A2B = normalize(A2B)
    mag_A2B = np.linalg.norm(A2B)

    # Use for loops to deduce locations of electrodes.
    names = []
    elec_coor = []
    new_corr = A
    elec_coor.append(totuple(new_corr))
    count = 1
    names.append("GRID %d" % count)
    for i in range(m):
        new_corr = np.add(A, (mag_A2B / (m - 1)) * (i + 1) * (unit_A2B))
        elec_coor.append(totuple(new_corr))
        count += 1
        names.append("GRID %d" % count)
    names = names[0:-1]
    elec_coor = elec_coor[0:-1]
    # pairs = dict(zip(names, elec_coor))
    return elec_coor


def get_mask_surface(mask):
    '''

    :param mask:
    :return:
    '''

    # isinstance(mask,(np.ndarray))
    mask_dilated = scipy.ndimage.morphology.binary_dilation(mask)
    surface = mask_dilated-mask
    surface = np.array(np.where(surface)).T
    surface_cKDTree = scipy.spatial.cKDTree(surface)
    return surface, surface_cKDTree

def unique_rows(a):
    '''
    Finds unique rows in a ndarray.
    Credit: http://stackoverflow.com/questions/8560440/removing-duplicate-columns-and-rows-from-a-numpy-2d-array/8567929#8567929

    :param a:
    :return:
    '''
    a = np.ascontiguousarray(a)
    unique_a = np.unique(a.view([('', a.dtype)]*a.shape[1]))
    return unique_a.view(a.dtype).reshape((unique_a.shape[0], a.shape[1]))