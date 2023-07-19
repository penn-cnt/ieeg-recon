import nibabel as nib
import numpy as np
from traits.api import HasTraits , CArray, Instance,on_trait_change
from collections import OrderedDict
import logging
import json
from . import interpolator
import re

log = logging.getLogger()


class PylocModelException(Exception):
    pass


class Scan(object):
    def __init__(self):
        self.filename = None
        self.data = None
        self.brainmask = None


class PointCloud(HasTraits):
    coordinates = CArray

    def __init__(self, coordinates):
        super(PointCloud, self).__init__()
        self.coordinates = np.array(coordinates)

    def __len__(self):
        return len(self.coordinates)

    def center(self):
        return self.coordinates.mean(0)

    def clear(self):
        self.coordinates = np.array([[], [], []]).T

    def set_coordinates(self, coordinates):
        self.coordinates = np.array([tuple(coord) for coord in coordinates])

    def get_coordinates(self, mask=None):
        if mask is None:
            return self.coordinates
        else:
            return self.coordinates[mask]


class PointMask(HasTraits):

    point_cloud = Instance(PointCloud)

    def __init__(self, label, point_cloud, mask=None):
        super(PointMask, self).__init__()
        self.label = label
        self._bounds = None
        self.point_cloud = point_cloud
        if mask is None:
            mask = np.zeros(len(point_cloud), bool)
        self.mask = mask
        self._bounds = self._calculate_bounds()

    def copy(self):
        return PointMask(self.label, self.point_cloud, self.mask.copy())

    def clear(self):
        self.mask = np.zeros(len(self.point_cloud), bool)

    def add_points(self, coordinates):
        all_coordinates = self.point_cloud.get_coordinates()
        for coordinate in coordinates:
            self.mask[all_coordinates == coordinate] = True

    def add_mask(self, point_mask):
        self.mask = np.logical_or(self.mask, point_mask.mask)
        self._bounds = self._calculate_bounds()

    def remove_mask(self, point_mask):
        to_keep = np.logical_not(point_mask.mask)

        before = np.count_nonzero(self.mask)
        self.mask = np.logical_and(self.mask, to_keep)
        after = np.count_nonzero(self.mask)

        log.debug("Removing {} points".format(after - before))
        self._bounds = self._calculate_bounds()

    def coordinates(self):
        return self.point_cloud.get_coordinates(self.mask)

    @on_trait_change('point_cloud.coordinates')
    def update_mask(self):
        """
        Mask the same area on a new set of coordinates
        :return:
        """
        if self._bounds is not None:
            new_mask = self.__contains__(self.point_cloud.coordinates)
            self.mask = new_mask

    @staticmethod
    def combined(point_masks):
        indices = np.array([])
        coords = np.array([[], [], []]).T
        labels = []
        for mask in point_masks:
            mask_indices = np.where(mask.mask)[0]
            new_indices = mask_indices[np.logical_not(np.in1d(mask_indices, indices, True))]
            if len(new_indices) > 0:
                new_coords = np.array([mask.point_cloud.get_coordinates()[i, :] for i in new_indices])
                coords = np.concatenate([coords, new_coords], 0)
                labels.extend([mask.label for _ in new_indices])
                indices = np.union1d(indices, new_indices)
        return coords, labels

    def _calculate_bounds(self):
        if len(self.point_cloud) == 0 or not self.mask.any():
            return np.array([[0, 0, 0], [0, 0, 0]])
        coords = self.coordinates()
        x, y, z = coords[:, 0], coords[:, 1], coords[:, 2]
        return np.array([[min(x), min(y), min(z)], [max(x), max(y), max(z)]])

    @property
    def bounds(self):
        return self._bounds

    def __contains__(self, coordinate):
        lower =  ((coordinate - self.bounds[0, :]) > -1.5)
        upper  = ((coordinate - self.bounds[1, :]) < 1.5)
        if lower.squeeze().shape==(3,) and upper.squeeze().shape==(3,):
            return (lower.all() and upper.all())
        else:
           return (lower & upper).all(1)

    @staticmethod
    def proximity_mask(point_cloud, point, distance):
        vector_dist = point_cloud.get_coordinates() - point
        dists = np.sqrt(np.sum(np.square(vector_dist), 1))
        return PointMask('_proximity', point_cloud, dists < distance)

    @staticmethod
    def centered_proximity_mask(point_cloud, point, distance):
        coordinates = point_cloud.get_coordinates()

        attempts = 0
        for _ in range(4):
            log.debug("Center attempt {}".format(attempts))
            vector_dist = coordinates - point
            dists = np.sqrt(np.sum(np.square(vector_dist), 1))
            point = np.mean(coordinates[dists < distance, :], 0)
            attempts += 1
        return PointMask('_proximity', point_cloud, dists < distance)

    def get_center(self):
        return np.mean(self.coordinates(), 0)


class Contact(object):
    def __init__(self, point_mask, contact_label,
                 lead_location, lead_group):
        self.point_mask = point_mask.copy()
        self.label = contact_label
        self.lead_location = lead_location
        self.lead_group = lead_group

    def __contains__(self, coordinate):
        return coordinate in self.point_mask

    def coordinates(self):
        return self.point_mask.coordinates()

    @property
    def center(self):
        return np.round(self.point_mask.get_center(), 1)

    @property
    def center_str(self):
        return '({:.1f}, {:.1f}, {:.1f})'.format(*self.point_mask.get_center())

    @property
    def lead_location_str(self):
        return '({}, {})'.format(*self.lead_location)

class MicroContact(Contact):
    """ Microcontacts are not necessarily visible in the CT scan, and so
    we need to define a contact class that lacks a point mask"""
    def __init__(self,center,point_cloud,contact_label,lead_location,lead_group):
        mask = PointMask(contact_label,point_cloud,mask=np.zeros(len(point_cloud)))
        super(MicroContact, self).__init__(mask,contact_label,lead_location,lead_group)
        self._center = center

    def __contains__(self, coordinate):
        return False
    @property
    def center(self):
        return np.round(self._center,1)

    @property
    def center_str(self):
        return '({:.1f}, {:.1f}, {:.1f})'.format(*self._center)


class Lead(object):
    def __init__(self, point_cloud, lead_label, lead_type='S',
                 dimensions=(1, 5), radius=4, spacing=10,micros=None):
        self.point_cloud = point_cloud
        self.label = lead_label
        self.type_ = lead_type
        self.dimensions = dimensions
        self.radius = radius
        self.spacing = spacing
        self.contacts = OrderedDict()
        self.micros = {"name" : " None"} if micros is None else micros

    def seed_next_contact(self, centered_coordinate):

        if self.has_coordinate(centered_coordinate):
            log.debug("Coordinate {} is already assigned".format(centered_coordinate))
            return

        if len(self.contacts) == 0:
            new_mask = PointMask.centered_proximity_mask(self.point_cloud, centered_coordinate, self.radius)
            if not new_mask.mask.any():
                log.debug("Could not find an electrode at {}".format(centered_coordinate))
                return
            log.debug("Added first contact to {}".format(self.label))
            self.add_contact(new_mask, *self._next_contact_info())
            return

        last_contact = list(self.contacts.values())[-1]

        new_mask = PointMask.centered_proximity_mask(self.point_cloud, centered_coordinate, self.radius)
        if not new_mask.mask.any():
            log.debug("Could not find an electrode at {}".format(centered_coordinate))
            return
        next_info = self._next_contact_info()
        if next_info[0] != last_contact.label:
            self.add_contact(new_mask, *next_info)
            dist = np.linalg.norm(centered_coordinate - last_contact.center)
            _, next_loc, _ = self._next_contact_info()
            if next_loc[1] == last_contact.lead_location[1]:
                if dist < 3 or dist > 50:
                    return
                next_coordinate = centered_coordinate + (centered_coordinate - last_contact.center)
                self.seed_next_contact(next_coordinate)

    def has_coordinate(self, coordinate):
        centers = [contact.center for contact in list(self.contacts.values())]
        for existing_center in centers:
            if all(abs(existing_center - coordinate) < .5):
                return True
        return False

    def next_contact_label(self):
        return self._next_contact_info()[0]

    def next_contact_loc(self):
        return self._next_contact_info()[1]

    def _next_contact_info(self):
        if len(self.contacts) == 0:
            return '1', (1, 1), 1

        last_contact = list(self.contacts.values())[-1]

        last_label = last_contact.label
        last_num = int(re.findall(r"\d+", last_label)[-1])

        if last_num == self.dimensions[0] * self.dimensions[1]:
            log.debug("Last contact in place. Not incrementing")
            return last_label, last_contact.lead_location, last_contact.lead_group

        last_locs = last_contact.lead_location

        if last_locs[0] >= self.dimensions[0] and last_locs[1] >= self.dimensions[1]:
            log.debug("Last location in place. Not incrementing")
            return last_label, last_contact.lead_location, last_contact.lead_group


        next_label = last_label.replace(str(last_num), str(last_num+1))

        if last_locs[1] >= self.dimensions[1]:
            next_locs = last_locs[0]+1, 1
        else:
            next_locs = last_locs[0], last_locs[1]+1

        return next_label, next_locs, last_contact.lead_group



    def interpolate(self):
        groups = set(contact.lead_group for contact in list(self.contacts.values()))
        if self.dimensions[1] > 1:
            for group in groups:
                self._interpolate_grid(group)
        else:
            for group in groups:
                self._interpolate_strip(group)

    def _interpolate_grid(self, group):
        dims = self.dimensions
        contacts = [contact for contact in list(self.contacts.values()) if contact.lead_group == group]
        locations = [tuple(contact.lead_location) for contact in contacts]
        possible_locations = [(i, j) for i in range(1, dims[0] + 1) for j in range(1, dims[1] + 1)]

        present = np.zeros(len(possible_locations), bool).reshape(dims)

        for i, location in enumerate(possible_locations):
            present[location[0] - 1, location[1] - 1] = location in locations

        if present.all():
            log.info("All leads present. Nothing to interpolate")
            return

        diffs = np.diff(present.astype(int), axis=1)

        log.debug("Lead diffs 1 = {}".format(diffs))

        holes = []

        for i in range(diffs.shape[0]):
            downs = np.where(diffs[i, :] == -1)[0]
            downs_xy = [(i + 1, down + 1) for down in downs]
            ups = np.where(diffs[i, :] == 1)[0]
            ups_xy = [(i + 1, up + 2) for up in ups]
            holes.extend(list(zip(downs_xy, ups_xy)))

        for down, up in holes:
            c1 = [contact for contact, location in zip(contacts, locations) if location == down][0]
            c2 = [contact for contact, location in zip(contacts, locations) if location == up][0]
            self._interpolate_between_1d(c1, c2, dims[0])

        diffs = np.diff(present.astype(int), axis=0)

        log.debug("Lead diffs 0 = {}".format(diffs))

        holes = []

        for i in range(diffs.shape[1]):
            downs = np.where(diffs[:, i] == -1)[0]
            downs_xy = [(down + 1, i + 1) for down in downs]
            ups = np.where(diffs[:, i] == 1)[0]
            ups_xy = [(up + 2, i + 1) for up in ups]
            holes.extend(list(zip(downs_xy, ups_xy)))

        for down, up in holes:
            c1 = [contact for contact, location in zip(contacts, locations) if location == down][0]
            c2 = [contact for contact, location in zip(contacts, locations) if location == up][0]
            self._interpolate_between_1d(c1, c2, 1)

    def _interpolate_strip(self, group):
        dims = self.dimensions
        contacts = [contact for contact in list(self.contacts.values()) if contact.lead_group == group]
        locations = [tuple(contact.lead_location) for contact in contacts if not 'Micro' in contact.label]
        possible_locations = [(i, 1) for i in range(1, dims[0] + 1)]

        present = np.array(list(x in locations for x in possible_locations))

        if all(present):
            log.info("All leads present. Nothing to interpolate")
            return

        diffs = np.diff(present.astype(int))

        log.debug("Lead diffs = {}".format(diffs))

        if not any(diffs == -1) or not any(diffs == 1):
            log.info("No holes present. Nothing to interpolate")
            return

        downs = np.where(diffs == -1)[0]
        ups = np.where(diffs == 1)[0]

        for down, up in zip(downs, ups):
            c1 = [contact for contact, location in zip(contacts, locations) if location == possible_locations[down]][0]
            c2 = [contact for contact, location in zip(contacts, locations) if location == possible_locations[up + 1]][
                0]
            self._interpolate_between_1d(c1, c2, 1)

    def _interpolate_between_1d(self, contact_1, contact_2, increment):

        log.debug("Interpolating between {} and {}".format(contact_1.label, contact_2.label))

        start_label = contact_1.label
        start_num = ''.join(re.findall(r'\d+', start_label))
        start_int = int(start_num)

        start_coords = contact_1.center
        end_coords = contact_2.center

        if contact_2.lead_location[1] == contact_1.lead_location[1]:
            dim = 0
            loc = contact_2.lead_location[1]
        elif contact_2.lead_location[0] == contact_1.lead_location[0]:
            dim = 1
            loc = contact_2.lead_location[0]
        else:
            log.error("Contacts are not alignable!")
            return

        n_points = contact_2.lead_location[dim] - contact_1.lead_location[dim] + 1

        points = interpolator.interpol(start_coords, end_coords, [], n_points, 1)

        centers = [start_coords, end_coords]

        for i, point in enumerate(points):
            if dim == 0:
                grid_coordinate = [contact_1.lead_location[dim] + i, loc]
            else:
                grid_coordinate = [loc, contact_1.lead_location[dim] + i]
            mask = PointMask.centered_proximity_mask(self.point_cloud, point, self.radius)
            if not mask.mask.any():
                log.info("Could not find any points near {}".format(point))
                continue
            center = mask.get_center()

            new_label = start_label.replace(start_num, str(start_int + (i * increment)))

            do_skip = False
            for existing_center in centers:
                if all(abs(existing_center - center) < .5):
                    log.warning("Contact {} determined to have same center as previously defined contact."
                                " Skipping".format(new_label))
                    do_skip = True
                    break
            if do_skip:
                continue
            centers.append(center)

            self.add_contact(mask, new_label, grid_coordinate, contact_1.lead_group)
            log.info("Added contact {} at {}".format(new_label, point))

    def make_micro_contacts(self):
        # All this only works for depth electrodes
        sorted_contacts = [self.contacts[c] for c in sorted(self.contacts.keys())]
        contact_1 = sorted_contacts[0]
        contact_n = sorted_contacts[1]
        lead_unit_vector = (contact_n.center - contact_1.center)
        # Micro-contact positions are in relative units from the center of the last contact
        micro_nums = iter(range(1,1+sum(self.micros['numbering'])))
        contacts=[]
        for i,(n_contacts,spacing) in enumerate(zip(self.micros['numbering'],self.micros['spacing'])):
            micro_center = spacing*lead_unit_vector+contact_1.center
            for j in range(n_contacts):
                lead_location = (float('%s.%s'%(i+1,j+1)),1)
                contact_num = str(next(micro_nums))
                contacts.append(dict(
                    center=micro_center,
                    point_cloud=self.point_cloud,
                    contact_label=contact_num,
                    lead_location=lead_location,
                    lead_group=0))
        return contacts

    def has_lead_location(self, lead_location, lead_group):
        for contact in list(self.contacts.values()):
            if np.all(contact.lead_location == lead_location):
                if contact.lead_group == lead_group:
                    return True
        return False

    def add_contact(self,*args,**kwargs):
        if self.type_.startswith('u'):
            self.add_micro(*args,**kwargs)
        else:
            self.add_macro(*args,**kwargs)

    def add_micro(self,center,point_cloud,contact_label,lead_location,lead_group):
        contact = MicroContact(center,point_cloud,contact_label,lead_location,lead_group)
        if contact_label in self.contacts:
            self.remove_contact(contact_label)
        self.contacts[contact_label]=contact
        self.last_contact = contact

    def add_macro(self, point_mask, contact_label, lead_location, lead_group):
        assert not np.isnan(point_mask.get_center()).any()
        contact = Contact(point_mask, contact_label, lead_location, lead_group)
        if contact_label in self.contacts:
            self.remove_contact(contact_label)
        if self.has_coordinate(point_mask.get_center()):
            log.warning("Coordinates {} of {}{} already exist.".format(point_mask.get_center(), self.label, contact_label))
        self.contacts[contact_label] = contact
        self.last_contact = contact

    def remove_contact(self, contact_label):
        del self.contacts[contact_label]

    def coordinates(self):
        masks = [contact.point_mask for contact in list(self.contacts.values())]
        coords, _ = PointMask.combined(masks)
        return coords

    def get_mask(self):
        masks = [contact.point_mask for contact in list(self.contacts.values())]
        full_mask = np.zeros(len(self.point_cloud.get_coordinates()), bool)
        for mask in masks:
            full_mask = np.logical_or(full_mask, mask.mask)
        return PointMask(self.label, self.point_cloud, full_mask)

    def update(self,point_cloud):
        """
        Creates new Contact objects for each contact in the lead based on a new point cloud
        point cloud.
        :param point_cloud:
        :return:
        """
        new_contacts = OrderedDict()
        for label_ in self.contacts:
            contact  = self.contacts[label_]

            if 'u' in self.type_:
                new_contact = MicroContact(contact.center,point_cloud,label_,contact.lead_location,contact.lead_group)
            else:
                mask = PointMask.centered_proximity_mask(point_cloud, contact.center, self.radius)
                new_contact = Contact(mask,label_,contact.lead_location,contact.lead_group)
            new_contacts[label_] = new_contact
        self.contacts = new_contacts


class CT(object):
    DEFAULT_THRESHOLD = 99.96


    def __init__(self, config):
        super(CT, self).__init__()
        self.config = config
        self.threshold = self.DEFAULT_THRESHOLD
        self._points = PointCloud([])
        self._leads = OrderedDict()
        self._selection = PointMask("_selected", self._points)
        self.selected_lead_label = ""
        self.filename = None
        self.data = None
        self.brainmask = None
        self.affine = None

        self.SAVE_METHODS = {
            '.json': self.to_json,
            '.vox_mom': self.to_vox_mom,
            '.txt': self.to_vox_mom
        }

    def _load_scan(self, img_file):
        self.filename = img_file
        log.debug("Loading {}".format(img_file))
        img = nib.load(self.filename)
        self.data = img.get_fdata().squeeze()
        self.brainmask = np.zeros(img.get_fdata().shape, bool)
        self.affine = img.affine[:3,:]

    def add_mask(self, filename):
        mask = nib.load(filename).get_data()
        self.brainmask = mask

    def interpolate(self, lead_label):
        lead = self._leads[lead_label]
        lead.interpolate()

    def add_micro_contacts(self):
        for lead in list(self._leads.values()):
            if lead.micros and lead.micros['name'] != ' None':
                micro_contacts = lead.make_micro_contacts()
                micro_lead = Lead(lead.point_cloud,lead.label+'Micro',lead_type=lead.micros['type'],dimensions=lead.dimensions,
                                  micros=None)
                for contact_dict in micro_contacts:
                    micro_lead.add_contact(**contact_dict)
                self._leads[micro_lead.label]=micro_lead

    def to_dict(self,include_bipolar=False):
        leads = {}
        for lead in list(self._leads.values()):
            contacts = []
            groups = set()
            for contact in list(lead.contacts.values()):
                groups.add(contact.lead_group)
                contacts.append(dict(
                    name=lead.label + contact.label,
                    lead_group=contact.lead_group,
                    lead_loc=contact.lead_location,
                    coordinate_spaces=dict(
                        ct_voxel=dict(
                            raw=contact.center.astype(int).tolist()
                        )
                    )
                ))
            if include_bipolar:
                pairs = [{'atlases':{},
                          'info':{},
                          'coordinate_spaces':{'ct_voxel':{'raw':(0.5*(c1.center+c2.center)).astype(int).tolist()}},
                          'names':(lead.label+c1.label,lead.label+c2.label) }
                         for (c1, c2) in self.calculate_pairs(lead)]
            else:
                pairs = []
            leads[lead.label] = dict(
                contacts=contacts,
                pairs=pairs,
                n_groups=len(groups),
                dimensions=lead.dimensions,
                type=lead.type_
            )
        return dict(
            leads=leads,
            origin_ct=self.filename
        )

    def saveas(self,fname,format_,include_bipolar=False):
        try:
            self.SAVE_METHODS[format_.lower()](fname,include_bipolar)
        except KeyError:
            raise KeyError('Unknown file format %s'%format_)

    def to_vox_mom(self,fname,include_bipolar=False):
        csv_out = []
        for lead in sorted(list(self.get_leads().values()),key=lambda x: x.label.upper()):
            ltype = lead.type_
            dims = lead.dimensions
            for contact in sorted(list(lead.contacts.keys()),key=int):
                voxel = np.rint(lead.contacts[contact].center)
                contact_name = lead.label+contact
                csv_out += "%s\t%s\t%s\t%s\t%s\t%s %s\n"%(
                    contact_name,int(voxel[0]),int(voxel[1]),int(voxel[2]),ltype,dims[0],dims[1]
                )
            if include_bipolar:
                pairs = self.calculate_pairs(lead)
                for pair in pairs:
                    voxel = np.rint((pair[0].center+pair[1].center)/2)
                    pair_name = '{lead.label}{pair[0].label}-{lead.label}{pair[1].label}'.format(lead=lead,pair=pair)
                    csv_out += "%s\t%s\t%s\t%s\t%s\t%s %s\n"%(
                        pair_name,int(voxel[0]),int(voxel[1]),int(voxel[2]),ltype,dims[0],dims[1])
        with open(fname,'w') as vox_mom:
            vox_mom.writelines(csv_out)



    def calculate_pairs(self,lead):
        pairs = []
        groups = np.unique([contact.lead_group for contact in list(lead.contacts.values())])
        for group in groups:
            group_contacts = [contact for contact in list(lead.contacts.values()) if contact.lead_group == group]
            for contact1 in group_contacts:
                gl1 = contact1.lead_location
                contact_pairs = [(contact1, contact2) for contact2 in group_contacts if
                                 gl1[0] == contact2.lead_location[0] and gl1[1] + 1 == contact2.lead_location[1] or
                                 gl1[1] == contact2.lead_location[1] and gl1[0] + 1 == contact2.lead_location[0]]
                pairs.extend(contact_pairs)
        return pairs

    def to_json(self, filename,include_bipolar=False):
        json.dump(self.to_dict(include_bipolar), open(filename, 'w'),indent=2)


    def from_dict(self, input_dict):
        leads = input_dict['leads']
        labels = list(leads.keys())
        types = [leads[label]['type'] for label in labels]
        try:
            dimensions = [leads[label]['dimensions'] for label in labels]
        except KeyError:
            def get_dimensions(lead):
                x = max([c['lead_loc'][1] for c in lead['contacts']])
                y =  max([c['lead_loc'][0] for c in lead['contacts']])
                return (x+1,y+1)
            dimensions = [get_dimensions(leads[label]) for label in labels]
        radii = [self.config['lead_types'][type_]['radius'] for type_ in types ]
        spacings = [self.config['lead_types'][type_]['spacing'] for type_ in types ]
        self.set_leads(labels, types, dimensions, radii, spacings)
        for i, lead_label in enumerate(labels):
            for contact in leads[lead_label]['contacts']:
                coordinates = contact['coordinate_spaces']['ct_voxel']['raw']
                point_mask = PointMask.proximity_mask(self._points, coordinates, radii[i])
                group = contact['lead_group']
                loc = contact['lead_loc']
                contact_label = contact['name'].replace(lead_label, '')
                if 'u' in types[i]:
                    self._leads[lead_label].add_contact(coordinates,self._points,contact_label,loc,group)
                else:
                    self._leads[lead_label].add_contact(point_mask, contact_label, loc, group)


    def from_json(self, filename):
        self.from_dict(json.load(open(filename)))

    def set_leads(self, labels, lead_types, dimensions, radii, spacings,micros=None):
        for label in list(self._leads.keys()):
            if label not in labels:
                del self._leads[label]
        if micros is None:
            micros = [self.config['micros'][' None'] for l in labels]
        for label, lead_type, dimension, radius, spacing,micro in zip(
                labels, lead_types, dimensions, radii, spacings,micros):
            if label not in self._leads:
                log.debug("Adding lead {}, ({} {} {})".format(label, lead_type, dimension, spacing))
                self._leads[label] = Lead(self._points, label, lead_type, dimension, radius, spacing,micro)

    def get_lead(self, lead_name):
        return self._leads[lead_name]

    def get_leads(self):
        return self._leads

    def load(self, img_file, threshold=None):
        self._load_scan(img_file)
        self.set_threshold(self.threshold if threshold is None else threshold)

    @property
    def shape(self):
        return self.data.shape

    def set_threshold(self, threshold):
        logging.debug("Threshold is set to {} percentile".format(threshold))
        self.threshold = threshold
        if self.data is None:
            raise PylocModelException("Data is not loaded")
        threshold_value = np.percentile(self.data, self.threshold)
        logging.debug("Thresholding at an intensity of {}".format(threshold_value))
        mask = self.data >= threshold_value
        logging.debug("Getting super-threshold indices")
        indices = np.array(mask.nonzero()).T
        self._points.set_coordinates(indices)
        self._selection = PointMask("_selection", self._points)

    def select_points(self, point_mask):
        self._selection.clear()
        self._selection.add_mask(point_mask)

    def select_points_near(self, point, nearby_range=10):
        self.select_points(PointMask.proximity_mask(self._points, point, nearby_range))

    def selection_center(self):
        return self._selection.get_center()

    def select_weighted_center(self, point, radius=10, iterations=1):
        self.select_points_near(point, radius)
        for _ in range(iterations):
            center = self._selection.get_center()
            self.select_points_near(center, radius)
        return self._selection.get_center()

    def contact_exists(self, lead_label, contact_label):
        return lead_label in self._leads and contact_label in self._leads[lead_label].contacts

    def lead_location_exists(self, lead_label, lead_location, lead_group):
        return self._leads[lead_label].has_lead_location(lead_location, lead_group)

    def add_selection_to_lead(self, lead_label, contact_label, lead_location,
                              lead_group):
        self._leads[lead_label].add_contact(self._selection, contact_label,
                                            lead_location, lead_group)

    def set_selected_lead(self, lead_label):
        self.selected_lead_label = lead_label

    def all_xyz(self):
        c = self._points.get_coordinates()
        label = ['_ct'] * len(c[:, 0])
        return label, c[:, 0], c[:, 1], c[:, 2],

    def lead_xyz(self):
        coords, labels = PointMask.combined([lead.get_mask() for lead in list(self._leads.values())])
        if len(coords) == 0:
            return [], [], [], []
        return labels, coords[:, 0], coords[:, 1], coords[:, 2]

    def selection_xyz(self):
        c = self._selection.coordinates()
        label = ['_selected'] * len(c[:, 0])
        return label, c[:, 0], c[:, 1], c[:, 2]

    def xyz(self, label):
        if label == '_ct':
            return self.all_xyz()
        if label == '_leads':
            return self.lead_xyz()
        if label == '_selected':
            return self.selection_xyz()

    def clear_selection(self):
        self._selection.clear()
