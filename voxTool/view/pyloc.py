import os

os.environ['ETS_TOOLKIT'] = 'qt4'

from pyface.qt import QtGui, QtCore
from model.scan import CT
from .slice_viewer import SliceViewWidget
from mayavi.core.ui.api import MayaviScene, MlabSceneModel, \
    SceneEditor
from mayavi import mlab
from traits.api import HasTraits, Instance, on_trait_change
from traitsui.api import View, Item

import random
import numpy as np
import logging
import yaml
import re

from collections import OrderedDict

log = logging.getLogger()
log.setLevel(0)


def add_labeled_widget(layout, label, *widgets):
    sub_layout = QtGui.QHBoxLayout()
    label_widget = QtGui.QLabel(label)
    sub_layout.addWidget(label_widget)
    for widget in widgets:
        sub_layout.addWidget(widget)
    layout.addLayout(sub_layout)



class PylocControl(object):
    """
    Main class for running VoxTool.
    """
    def __init__(self, config=None):
        if config == None:
            config = yaml.load(open("../model/config.yml"))

        self.app = QtGui.QApplication.instance() #: The underlying application. Runs automatically
        self.view = PylocWidget(self, config) #: The base object for the GUI
        self.view.show()

        self.window = QtGui.QMainWindow()
        self.window.setCentralWidget(self.view)
        self.window.show()

        self.lead_window = None #: See ..self.define_leads and ..LeadDefinitionWidget

        self.ct = None #: See self.load_ct; instance of ..scan.CT
        self.config = config # Global configuration file

        self.assign_callbacks()
        self.assign_shortcuts()

        self.clicked_coordinate = np.zeros((3,))
        self.selected_coordinate = np.zeros((3,))

        self.selected_lead = None #: The lead currently being localized
        self.contact_label = ""
        self.lead_location = [0, 0]
        self.lead_group = 0

        self.seeding = False #: Toggled by self.toggle_seeding

    def interpolate_selected_lead(self):
        """
        Callback for "Interpolate" button in lead panel
        :return:
        """
        self.ct.interpolate(self.selected_lead.label)
        self.view.update_cloud('_leads')
        self.view.contact_panel.set_chosen_leads(self.ct.get_leads())

    def add_micro_contacts(self):
        """
        Callback for "Add micro_contact" button in lead panel
        :return:
        """
        self.ct.add_micro_contacts()
        self.view.update_cloud('_leads')
        self.view.contact_panel.set_chosen_leads(self.ct.get_leads())

    def toggle_seeding(self):
        """
        Callback for "Seeding" button in lead panel
        :return:
        """
        self.seeding = not self.seeding
        if self.seeding:
            self.display_seed_contact()
        else:
            self.view.display_message("")

    def display_seed_contact(self):
        next_label = self.selected_lead.next_contact_label()
        next_loc = self.selected_lead.next_contact_loc()

        msg = "Click on contact {}{} ({}, {})".format(self.selected_lead.label, next_label, *next_loc)
        self.view.display_message(msg)

    def set_lead_location(self, lead_location, lead_group):
        self.lead_location = lead_location
        self.lead_group = lead_group

    def set_contact_label(self, label):
        self.contact_label = label
        self.lead_group = 0

    def set_selected_lead(self, lead_name):
        log.debug("Setting selected lead to {}".format(lead_name))
        try:
            self.selected_lead = self.ct.get_lead(lead_name)
            dims = self.selected_lead.dimensions
            self.view.contact_panel.update_lead_dims(*dims)
        except KeyError:
            log.error("Lead {} does not exist".format(lead_name))
        self.select_next_contact_label()

    def toggle_RAS_axes(self,state):
        self.view.toggle_RAS()




    def prompt_for_ct(self):
        """
        Callback for "Load Scan" button. See :load_ct:
        :return:
        """
        file_, filter = QtGui.QFileDialog().getOpenFileName(None, 'Select Scan', '.', "NIFTI files (*.nii.gz)")
        if file_:
            self.load_ct(filename=file_)
            self.view.task_bar.define_leads_button.setEnabled(True)
            self.view.task_bar.save_button.setEnabled(True)
            self.view.task_bar.load_coord_button.setEnabled(True)


    def load_ct(self, filename):
        """
        Loads a CT file and updates the view.
        :param filename: The name of the CT file.
        :return:
        """
        self.ct = CT(self.config)
        self.ct.load(filename,self.config['ct_threshold'])
        self.view.slice_view.set_label(filename)
        self.view.contact_panel.update_contacts()
        self.view.contact_panel.setEnabled(True)
        self.view.add_cloud(self.ct, '_ct', callback=self.select_coordinate)
        self.view.add_cloud(self.ct, '_leads')
        self.view.add_cloud(self.ct, '_selected')
        self.view.add_RAS(self.ct)
        self.view.set_slice_scan(self.ct.data)

    def exec_(self):
        self.app.exec_()

    def assign_callbacks(self):
        self.view.task_bar.load_scan_button.clicked.connect(self.prompt_for_ct)
        self.view.task_bar.define_leads_button.clicked.connect(self.define_leads)
        self.view.task_bar.save_button.clicked.connect(self.save_coordinates)
        self.view.task_bar.load_coord_button.clicked.connect(self.load_coordinates)

    def assign_shortcuts(self):
        """
        Constructs keyboard shortcuts and assigns them to methods
        :return:
        """
        QtGui.QShortcut(QtGui.QKeySequence('S'),self.view).activated.connect(self.add_selection)
        QtGui.QShortcut(QtGui.QKeySequence('Ctrl+O'),self.view).activated.connect(self.prompt_for_ct)
        QtGui.QShortcut(QtGui.QKeySequence('Ctrl+Shift+O'),self.view).activated.connect(self.load_coordinates)
        QtGui.QShortcut(QtGui.QKeySequence('Ctrl+D'),self.view).activated.connect(self.define_leads)
        QtGui.QShortcut(QtGui.QKeySequence('Ctrl+S'),self.view).activated.connect(self.save_coordinates)

    def save_coordinates(self):
        """
        Callback to save the localized coordinates in either JSON or text format
        :return:
        """
        file,file_filter = QtGui.QFileDialog().getSaveFileName(None,'Save as:',os.path.join(os.getcwd(),'voxel_coordinates.json'),
                                                            'JSON (*.json);;TXT (*.txt)','JSON (*.json)')
        if file:
            self.ct.saveas(file,os.path.splitext(file)[-1],self.view.task_bar.bipolar_box.isChecked())

    def load_coordinates(self):
        file = QtGui.QFileDialog().getOpenFileName(None, 'Select voxel_coordinates.json', '.', '(*.json)')
        if file:
            self.ct.from_json(file)
            self.view.update_cloud('_leads')
            self.view.contact_panel.update_contacts()

    def define_leads(self):
        """
        Callback for "Define Leads" button
        :return:
        """
        self.lead_window = QtGui.QMainWindow()
        lead_widget = LeadDefinitionWidget(self, self.config, self.view)
        lead_widget.set_leads(self.ct.get_leads())
        self.lead_window.setCentralWidget(lead_widget)
        self.lead_window.show()
        self.lead_window.resize(200, lead_widget.height())

    def select_coordinate(self, coordinate, do_center=True, allow_seed=True):
        """
        Callback for interacting with CT window.
        When a point in the screen is clicked, highlights the points near the selected point.
        If seeding is enabled, mark the highlighted points as current contact and seed as many additional contacts as possible.
        :param coordinate: The selected point in voxel space
        :param do_center: If true, tteratively select the center of the current selection, to better estimate the center of the contact.
        :param allow_seed: ???
        :return:
        """
        log.debug("Selecting near coordinate {}".format(coordinate))
        self.clicked_coordinate = coordinate
        self.selected_coordinate = coordinate
        radius = self.selected_lead.radius if not self.selected_lead is None else 5
        self.ct.select_points_near(coordinate, radius)
        if do_center:
            log.debug("Centering...")
            self.center_selection(self.config['selection_iterations'], radius)
        panel = self.view.contact_panel
        for i, (_,contact) in enumerate(panel.contacts):
            if self.clicked_coordinate in contact:
                panel.contact_list.setCurrentRow(i)
                break
        else:
            panel.contact_list.setCurrentRow(panel.contact_list.currentRow(),QtGui.QItemSelectionModel.Deselect)

        if not np.isnan(self.selected_coordinate).all():
            if self.seeding and allow_seed:
                log.info("Seeding from coordinate {}".format(self.selected_coordinate))
                self.selected_lead.seed_next_contact(self.selected_coordinate)
                self.ct.clear_selection()
                self.selected_coordinate = np.zeros((3,))
                self.view.update_cloud('_leads')
                self.select_next_contact_label()
                self.view.contact_panel.set_chosen_leads(self.ct.get_leads())
                self.display_seed_contact()
            else:
                self.view.update_ras(self.selected_coordinate)
                log.info("Selected coordinate {}".format(self.selected_coordinate))
        else:
            log.info("No coordinate selected")
        self.view.update_cloud('_selected')
        self.view.update_slices(self.selected_coordinate)

    def center_selection(self, iterations, radius):
        for _ in range(iterations):
            self.selected_coordinate = self.ct.selection_center()
            self.ct.select_points_near(self.selected_coordinate, radius)

    def confirm(self, label):
        reply = QtGui.QMessageBox.question(None, 'Confirmation', label,
                                           QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
        return reply == QtGui.QMessageBox.Yes

    def add_selection(self):
        """
        Callback for "Submit" button on lead panel
        Adds selected pixels as new contact
        :return:
        """
        lead = self.selected_lead
        lead_label = lead.label
        contact_label = self.contact_label
        lead_location = self.lead_location[:]
        lead_group = self.lead_group

        if not self.ct.contact_exists(lead_label, contact_label) and \
                self.ct.lead_location_exists(lead_label, lead_location, lead_group):
            if not self.confirm("Lead location {} already exists. "
                                "Are you sure you want to duplicate?".format(lead_location)):
                return
        if self.config['zero_index_lead']:
            offset = 1
        else:
            offset = 0

        if lead_location[0] + offset > lead.dimensions[0] or \
                                lead_location[1] + offset > lead.dimensions[1]:
            if not self.confirm("Dimensions {} are outside of lead dimensions {}. "
                                "Are you sure you want to continue?".format(lead_location, lead.dimensions)):
                return

        self.ct.add_selection_to_lead(lead_label, contact_label, lead_location, self.lead_group)
        self.view.contact_panel.set_chosen_leads(self.ct.get_leads())
        self.ct.clear_selection()
        self.view.update_cloud('_leads')
        self.view.update_cloud('_selected')

        self.select_next_contact_label()

    def select_next_contact_label(self):
        lead = self.selected_lead

        self.contact_label = lead.next_contact_label()
        self.lead_location = lead.next_contact_loc()

        self.view.update_lead_location(*self.lead_location)
        self.view.update_contact_label(self.contact_label)

    def set_leads(self, labels, lead_types, dimensions, radii, spacings,micros=None):
        self.ct.set_leads(labels, lead_types, dimensions, radii, spacings,micros)
        leads = self.ct.get_leads()
        panel_labels = ['%s (%s x %s)' % (k, v.dimensions[0], v.dimensions[1]) for (k, v) in leads.items()]
        self.view.contact_panel.set_lead_labels(panel_labels)
        self.view.contact_panel.update_contacts()

    def delete_contact(self, lead_label, contact_label):
        try:
            self.ct.get_lead(lead_label).remove_contact(contact_label)
        except KeyError:
            pass
        self.view.contact_panel.set_chosen_leads(self.ct.get_leads())
        self.view.update_cloud('_leads')


class PylocWidget(QtGui.QWidget):
    def __init__(self, controller, config, parent=None):
        """
        The widget controlled by PylocController
        :param controller:
        :param config:
        :param parent:
        """
        QtGui.QWidget.__init__(self, parent)
        self.controller = controller
        self.cloud_widget = CloudWidget(self, config)
        self.task_bar = TaskBarLayout()
        self.slice_view = SliceViewWidget(self)
        self.contact_panel = ContactPanelWidget(controller, config, self)
        self.contact_panel.setEnabled(False)
        self.threshold_panel = ThresholdWidget(controller=controller, config=config, parent=self)

        layout = QtGui.QVBoxLayout(self)
        splitter = QtGui.QSplitter()
        splitter.addWidget(self.contact_panel)
        splitter.addWidget(self.cloud_widget)
        splitter.addWidget(self.slice_view)
        splitter.setSizes([50,400,200])

        layout.addWidget(self.threshold_panel)
        layout.addWidget(splitter)
        layout.addLayout(self.task_bar)

    def clear(self):
        pass

    def display_message(self, msg):
        self.cloud_widget.display_message(msg)

    def update_cloud(self, label):
        self.cloud_widget.update_cloud(label)

    def update_clouds(self):
        self.cloud_widget.viewer.update_all()

    def update_slices(self, coordinates):
        self.slice_view.set_coordinate(coordinates)
        self.slice_view.update()

    def plot_cloud(self,label):
        self.cloud_widget.plot_cloud(label)

    def add_cloud(self, ct, label, callback=None):
        self.cloud_widget.add_cloud(ct, label, callback)

    def add_RAS(self,ct,callback=None):
        self.cloud_widget.add_RAS(ct,callback)

    def toggle_RAS(self):
        self.cloud_widget.toggle_RAS()

    def remove_cloud(self, label):
        self.cloud_widget.remove_cloud(label)

    def set_slice_scan(self, scan):
        self.slice_view.set_image(scan)

    def update_ras(self, coordinate):
        self.contact_panel.display_coordinate(coordinate)

    def update_contact_label(self, contact_label):
        self.contact_panel.set_contact_label(contact_label)

    def update_lead_location(self, x, y):
        self.contact_panel.set_lead_location(x, y)

class NoScrollComboBox(QtGui.QComboBox):
    """
    Subclass of QComboBox that doesn't interact with the scroll wheel.
    """
    def __init__(self,*args,**kwargs):
        super(NoScrollComboBox, self).__init__(*args,**kwargs)
        # Don't want to receive focus via scroll wheel
        self.setFocusPolicy(QtCore.Qt.StrongFocus)

    def wheelEvent(self, QWheelEvent):
        """
        No behavior on wheel events
        :param QWheelEvent:
        :return:
        """
        QWheelEvent.accept()
        return

class ContactPanelWidget(QtGui.QWidget):
    def __init__(self, controller, config, parent=None):
        """
        Panel that displays and interacts with localized contacts
        :param controller: The PylocControl for the app
        :param config: The loaded config dict for the app
        :param parent: A parent widget
        """
        super(ContactPanelWidget, self).__init__(parent)
        self.config = config
        self.controller = controller

        layout = QtGui.QVBoxLayout(self)

        lead_layout = QtGui.QHBoxLayout()
        layout.addLayout(lead_layout)

        self.labels = OrderedDict()
        self.label_dropdown = NoScrollComboBox()
        self.label_dropdown.setMaximumWidth(75)
        add_labeled_widget(lead_layout,
                                "Label :", self.label_dropdown)
        self.contact_name = QtGui.QLineEdit()
        lead_layout.addWidget(self.contact_name)

        loc_layout = QtGui.QHBoxLayout()
        layout.addLayout(loc_layout)

        self.x_lead_loc = QtGui.QLineEdit()
        self.x_loc_max = QtGui.QLabel('')
        add_labeled_widget(loc_layout,
                                "Lead   x:", self.x_lead_loc,self.x_loc_max)

        self.y_lead_loc = QtGui.QLineEdit()
        self.y_loc_max  = QtGui.QLabel('')
        add_labeled_widget(loc_layout,
                                " y:", self.y_lead_loc,self.y_loc_max)

        self.lead_group = QtGui.QLineEdit("0")
        add_labeled_widget(loc_layout,
                                " group:", self.lead_group)

        vox_layout = QtGui.QHBoxLayout()
        layout.addLayout(vox_layout)

        self.r_voxel = QtGui.QLineEdit()
        add_labeled_widget(vox_layout,
                                "R:", self.r_voxel)
        self.a_voxel = QtGui.QLineEdit()
        add_labeled_widget(vox_layout,
                                "A:", self.a_voxel)
        self.s_voxel = QtGui.QLineEdit()
        add_labeled_widget(vox_layout,
                                "S:", self.s_voxel)

        self.axes_checkbox = QtGui.QCheckBox("Show RAS Tags")
        self.axes_checkbox.setChecked(True)
        vox_layout.addWidget(self.axes_checkbox)

        self.submit_button = QtGui.QPushButton("Submit")

        layout.addWidget(self.submit_button)

        contact_label = QtGui.QLabel("Contacts:")
        layout.addWidget(contact_label)

        self.contacts = []
        self.contact_list = QtGui.QListWidget()
        self.contact_list.setSelectionMode(QtGui.QAbstractItemView.ContiguousSelection)
        layout.addWidget(self.contact_list)

        self.interpolate_button = QtGui.QPushButton("Interpolate")
        layout.addWidget(self.interpolate_button)

        self.seed_button = QtGui.QPushButton("Seeding")
        self.seed_button.setCheckable(True)
        layout.addWidget(self.seed_button)

        self.micro_button = QtGui.QPushButton("Add Micro-Contacts")
        layout.addWidget(self.micro_button)

        self.assign_callbacks()

    def display_coordinate(self, coordinate):
        self.r_voxel.setText("%.1f" % coordinate[0])
        self.a_voxel.setText("%.1f" % coordinate[1])
        self.s_voxel.setText("%.1f" % coordinate[2])

    def assign_callbacks(self):
        self.label_dropdown.currentIndexChanged.connect(self.lead_changed)
        self.contact_name.textChanged.connect(self.contact_changed)
        self.submit_button.clicked.connect(self.submit_pressed)
        self.x_lead_loc.textChanged.connect(self.lead_location_changed)
        self.y_lead_loc.textChanged.connect(self.lead_location_changed)
        self.lead_group.textChanged.connect(self.lead_location_changed)
        self.interpolate_button.clicked.connect(self.controller.interpolate_selected_lead)
        self.contact_list.currentItemChanged.connect(self.chosen_lead_selected)
        self.seed_button.clicked.connect(self.controller.toggle_seeding)
        self.micro_button.clicked.connect(self.controller.add_micro_contacts)
        self.axes_checkbox.stateChanged.connect(self.controller.toggle_RAS_axes)

    LEAD_LOC_REGEX = r'\((\d+\.?\d*),\s?(\d+\.?\d*),\s?(\d+\.?\d*)\)'

    def keyPressEvent(self, event):
        super(ContactPanelWidget, self).keyPressEvent(event)
        if event.key() == QtCore.Qt.Key_Delete:
            indices = self.contact_list.selectedIndexes()
            items  = [self.contacts[i.row()] for i in indices ]
            for (lead,contact) in items:
                try:
                    log.debug("Deleting contact {}{}".format(lead.label, contact.label))
                    self.controller.delete_contact(lead.label, contact.label)
                except Exception as e:
                    log.error("Could not delete contact: {}".format(e))
            self.update_contacts()

    def chosen_lead_selected(self):
        current_index = self.contact_list.currentIndex()
        _, current_contact = self.contacts[current_index.row()]
        log.debug("Selecting contact {}".format(current_contact.label))
        self.controller.select_coordinate(current_contact.center, False, False)

    def set_contact_label(self, label):
        self.contact_name.setText(label)

    def set_lead_location(self, x, y):
        self.x_lead_loc.setText(str(x))
        self.y_lead_loc.setText(str(y))

    def update_lead_dims(self,x,y):
        self.x_loc_max.setText('/%s'%x)
        self.y_loc_max.setText('/%s'%y)

    def lead_location_changed(self):
        x = self.find_digit(self.x_lead_loc.text())
        self.x_lead_loc.setText(x)
        y = self.find_digit(self.y_lead_loc.text())
        self.y_lead_loc.setText(y)
        group = self.find_digit(self.lead_group.text())
        self.lead_group.setText(group)

        if len(x) > 0 and len(y) > 0 and len(group) > 0:
            self.controller.set_lead_location([int(x), int(y)], int(group))

    @staticmethod
    def find_digit(label):
        return re.sub(r"[^\d]", "", str(label))

    def lead_changed(self):
        lead_txt = self.label_dropdown.currentText()
        self.controller.set_selected_lead(lead_txt.split()[0])
        self.lead_group.setText("0")
        self.lead_location_changed()

    def contact_changed(self):
        self.controller.set_contact_label(self.contact_name.text())

    def submit_pressed(self):
        self.controller.add_selection()

    def set_chosen_leads(self, leads):
        self.contact_list.clear()
        self.contacts = []
        for lead_name in sorted(leads.keys()):
            lead = leads[lead_name]
            for contact_name in sorted(lead.contacts.keys(), key=lambda x: int(''.join(re.findall('\d+', x)))):
                contact = lead.contacts[contact_name]
                self.add_contact(lead, contact)

    def add_contact(self, lead, contact):
        self.contact_list.addItem(
            QtGui.QListWidgetItem(self.config['lead_display'].format(lead=lead, contact=contact).strip())
        )
        self.contacts.append((lead, contact))

    def update_contacts(self):
        """
        Aligns self.contact_list with self.controller.ct._leads
        :return:
        """
        ct = self.controller.ct
        if ct is not None:
            leads = ct.get_leads()
            self.set_chosen_leads(leads)
            self.controller.view.update_cloud('_leads')
            labels = ['%s (%s x %s)'%(k,v.dimensions[0],v.dimensions[1]) for (k,v) in leads.items()]
            self.set_lead_labels(labels)

    def set_lead_labels(self, lead_labels):
        self.label_dropdown.clear()
        for lead_name in lead_labels:
            self.label_dropdown.addItem(lead_name)


class LeadDefinitionWidget(QtGui.QWidget):
    instance = None

    def __init__(self, controller, config, parent=None):
        super(LeadDefinitionWidget, self).__init__(parent)
        self.config = config
        self.controller = controller

        # Subwidgets
        self.label_edit = QtGui.QLineEdit()
        self.x_size_edit = QtGui.QLineEdit()
        self.y_size_edit = QtGui.QLineEdit()
        self.type_box = QtGui.QComboBox()

        for label, electrode_type in config['lead_types'].items():
            if 'u' not in label:
                self.type_box.addItem("{}: {name}".format(label, **electrode_type))

        self.micro_box = QtGui.QComboBox()
        for micro_lead_type in sorted(config['micros'].keys()):
            self.micro_box.addItem(micro_lead_type)

        self.submit_button = QtGui.QPushButton("Submit")

        self.delete_button = QtGui.QPushButton("Delete")
        self.close_button = QtGui.QPushButton("Confirm")

        self.leads_list = QtGui.QListWidget()

        self.add_callbacks()
        self.set_layout()
        self.set_tab_order()
        self.set_shortcuts()
        self._leads = OrderedDict()

    def set_layout(self):
        layout = QtGui.QVBoxLayout(self)
        add_labeled_widget(layout,
                                "Lead Name: ", self.label_edit)

        size_layout = QtGui.QHBoxLayout()
        size_layout.addWidget(QtGui.QLabel("Dimensions: "))
        add_labeled_widget(size_layout, "x:", self.x_size_edit)
        add_labeled_widget(size_layout, "y:", self.y_size_edit)

        layout.addLayout(size_layout)

        add_labeled_widget(layout, "Type: ", self.type_box)

        add_labeled_widget(layout,"Micro-contacts: ",self.micro_box)
        layout.addWidget(self.submit_button)
        layout.addWidget(self.leads_list)

        bottom_layout = QtGui.QHBoxLayout()

        bottom_layout.addWidget(self.delete_button)
        bottom_layout.addWidget(self.close_button)
        layout.addLayout(bottom_layout)


    def add_callbacks(self):
        self.submit_button.clicked.connect(self.add_current_lead)
        self.close_button.clicked.connect(self.finish)
        self.delete_button.clicked.connect(self.delete_lead)

    def set_tab_order(self):
        self.setTabOrder(self.micro_box,self.submit_button)
        self.setTabOrder(self.submit_button,self.leads_list)
        self.setTabOrder(self.leads_list,self.delete_button)
        self.setTabOrder(self.delete_button,self.close_button)

    def set_shortcuts(self):
        submit_shortcut = QtGui.QShortcut(QtGui.QKeySequence('S'),self)
        submit_shortcut.activated.connect(self.add_current_lead)

        confirm_shortcut = QtGui.QShortcut(QtGui.QKeySequence(QtCore.Qt.Key_Return),self)
        confirm_shortcut.activated.connect(self.finish)
        confirm_shortcut = QtGui.QShortcut(QtGui.QKeySequence( QtCore.Qt.Key_Enter),self)
        confirm_shortcut.activated.connect(self.finish)

        delete_shortcut = QtGui.QShortcut(QtGui.QKeySequence(QtCore.Qt.Key_Delete),self)
        delete_shortcut.activated.connect(self.delete_lead)

        focus_shortcut = QtGui.QShortcut(QtGui.QKeySequence(QtCore.Qt.Key_Escape),self)
        focus_shortcut.activated.connect(self.setFocus)


    @classmethod
    def launch(cls, controller, config, parent=None):
        window = QtGui.QMainWindow()
        widget = cls(controller, config, parent)
        window.setCentralWidget(widget)
        window.show()
        window.resize(200, cls.instance.height())
        return window

    def finish(self):
        leads = self._leads.values()
        labels = [lead['label'] for lead in leads]
        types = [lead['type'] for lead in leads]
        dimensions = [(lead['x'], lead['y']) for lead in leads]
        spacings = [self.config['lead_types'][lead_type]['spacing'] for lead_type in types]
        radii = [self.config['lead_types'][lead_type]['radius'] for lead_type in types]
        micros = [self.config['micros'][str(l.get('micro',' None'))] for l in leads]
        self.controller.set_leads(labels, types, dimensions, radii, spacings,micros)
        self.close()
        self.controller.lead_window.close()

    def set_leads(self, leads):
        self._leads = {lead.label:
                       {"label": lead.label,
                        "x":lead.dimensions[0],
                        "y":lead.dimensions[1],
                        "type":lead.type_,
                        "micro":lead.micros['name']}
                      for lead in leads.values() }
        self.refresh()

    def refresh(self):
        self.leads_list.clear()
        for lead in self._leads.values():
            self.leads_list.addItem(
                QtGui.QListWidgetItem(
                    "{label} ({x} x {y}, {type})".format(**lead)
                )
            )

    def add_current_lead(self):
        x_str = str(self.x_size_edit.text())
        y_str = str(self.y_size_edit.text())

        if not x_str.isdigit() or not y_str.isdigit():
            return

        type_str = self.type_box.currentText()
        label_str = str(self.label_edit.text())
        micro_str = self.micro_box.currentText()
        self._leads[label_str] = dict(
            label=label_str,
            x=int(x_str),
            y=int(y_str),
            type=type_str[0],
            micro=micro_str,
        )
        self.refresh()

    def delete_lead(self):
        lead = self.leads_list.currentItem()
        if lead is not None:
            label = lead.text().split()[0]
            log.debug('Removing lead %s'%label)
            del self._leads[label]
            self.refresh()

    @staticmethod
    def add_labeled_widget(layout, label, widget):
        sub_layout = QtGui.QHBoxLayout()
        label_widget = QtGui.QLabel(label)
        sub_layout.addWidget(label_widget)
        sub_layout.addWidget(widget)
        layout.addLayout(sub_layout)

class ThresholdWidget(QtGui.QWidget):
    """
    Subwindow for changing the threshold
    """
    def __init__(self,controller,config,parent=None):
        super(ThresholdWidget, self).__init__(parent)

        self.controller = controller
        self.config = config
        
        self.set_threshold_button = QtGui.QPushButton("Update")
        self.set_threshold_button.clicked.connect(self.update_pressed)
        self.threshold_selector = QtGui.QDoubleSpinBox()
        self.threshold_selector.setSingleStep(0.5)
        self.threshold_selector.setValue(self.config['ct_threshold'])
        self.threshold_selector.valueChanged.connect(self.update_threshold_value)
        self.threshold_selector.setKeyboardTracking(True)

        layout = QtGui.QVBoxLayout(self)
        layout.setContentsMargins(1,1,1,1)
        add_labeled_widget(layout,'CT Threshold',self.threshold_selector,self.set_threshold_button)

        self.setSizePolicy(QtGui.QSizePolicy.Preferred,QtGui.QSizePolicy.Maximum)

    def update_pressed(self):
        if self.controller.ct:
            self.controller.ct.set_threshold(self.config['ct_threshold'])
            for label in ['_ct','_leads','_selection']:
                self.controller.view.update_clouds()

    def update_threshold_value(self,value):
        self.config['ct_threshold']= value



class TaskBarLayout(QtGui.QHBoxLayout):
    def __init__(self, parent=None):
        super(TaskBarLayout, self).__init__(parent)
        self.load_scan_button = QtGui.QPushButton("Load Scan")
        self.define_leads_button = QtGui.QPushButton("Define Leads")
        self.define_leads_button.setEnabled(False)
        self.load_coord_button = QtGui.QPushButton("Load Coordinates")
        self.load_coord_button.setEnabled(False)
        self.clean_button = QtGui.QPushButton("Clean scan")
        self.save_button=QtGui.QPushButton("Save as...")
        self.save_button.setEnabled(False)
        self.bipolar_box = QtGui.QCheckBox("Include Bipolar Pairs")

        save_layout = QtGui.QVBoxLayout()
        save_layout.addWidget(self.save_button)
        save_layout.addWidget(self.bipolar_box)


        self.addWidget(self.load_scan_button)
        self.addWidget(self.define_leads_button)
        self.addWidget(self.load_coord_button)
        self.addLayout(save_layout)
        self.addWidget(self.clean_button)


class CloudWidget(QtGui.QWidget):
    def __init__(self, controller, config, parent=None):
        super(CloudWidget, self).__init__(parent)
        self.config = config
        layout = QtGui.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.viewer = CloudViewer(config)
        self.ui = self.viewer.edit_traits(parent=self,
                                          kind='subpanel').control

        layout.addWidget(self.ui)
        self.controller = controller

    def update_cloud(self, label):
        self.viewer.update_cloud(label)

    def add_cloud(self, ct, label, callback=None):
        self.viewer.add_cloud(ct, label, callback)

    def add_RAS(self,ct,callback=None):
        self.viewer.add_RAS(ct,callback)

    def toggle_RAS(self):
        RAS = self.viewer.RAS
        if RAS._plots and all([x.visible for x in RAS._plots]):
            RAS.hide()
        else:
            RAS.show()

    def plot_cloud(self,label):
        self.viewer.plot_cloud(label)

    def unplot_cloud(self,label):
        self.viewer.unplot_cloud(label)

    def remove_cloud(self, label):
        self.viewer.remove_cloud(label)

    def display_message(self, msg):
        self.viewer.display_message(msg)

class CloudViewer(HasTraits):
    BACKGROUND_COLOR = (.1, .1, .1)

    scene = Instance(MlabSceneModel, ())

    def __init__(self, config):
        super(CloudViewer, self).__init__()
        self.config = config
        self.figure = self.scene.mlab.gcf()
        mlab.figure(self.figure, bgcolor=self.BACKGROUND_COLOR)
        self.clouds = {}
        self.text_displayed = None
        self.RAS = None

    def update_cloud(self, label):
        if self.clouds:
            self.clouds[label].update()

    def plot_cloud(self,label):
        self.clouds[label].plot()

    def unplot_cloud(self,label):
        self.clouds[label].unplot()

    def add_cloud(self, ct, label, callback=None):
        if label in self.clouds:
            self.remove_cloud(label)
        self.clouds[label] = CloudView(ct, label, self.config, callback)
        self.clouds[label].plot()

    def add_RAS(self,ct,callback=None):
        self.RAS = AxisView(ct,self.config,callback)
        self.RAS.plot()

    def remove_cloud(self, label):
        self.clouds[label].unplot()
        del self.clouds[label]

    @on_trait_change('scene.activated')
    def plot(self):
        self.figure.on_mouse_pick(self.callback)
        for view in self.clouds.values():
            view.plot()

    def update_all(self):
        mlab.figure(self.figure, bgcolor=self.BACKGROUND_COLOR)
        for view in self.clouds.values():
            view.update()

    def callback(self, picker):
        found = False
        for cloud in self.clouds.values():
            if cloud.contains(picker):
                if cloud.callback(picker):
                    return True
                found = True
        return found

    def display_message(self, msg):
        if self.text_displayed is not None:
            self.text_displayed.set(text=msg)
        else:
            self.text_displayed = mlab.text(0.01, 0.95, msg, figure=self.figure, width=1)

    view = View(Item('scene', editor=SceneEditor(scene_class=MayaviScene),
                     height=250, width=300, show_label=False),
                resizable=True)


class CloudView(object):
    def get_colormap(self, label):
        if label == '_ct':
            return self.config['colormaps']['ct']
        elif label == '_selected':
            return self.config['colormaps']['selected']
        else:
            return self.config['colormaps']['default']

    def __init__(self, ct, label, config, callback=None):
        self.ct = ct
        self.config = config
        self.label = label
        self.colormap = self.get_colormap(label)
        self._callback = callback if callback else lambda *_: None
        self._plot = None
        self._glyph_points = None

    def callback(self, picker):
        return self._callback(np.array(picker.pick_position))

    def get_colors(self, labels, x, y, z):
        colors = np.ones(len(x))
        if len(labels) == 0:
            return []
        min_y = float(min(y))
        max_y = float(max(y))
        for i, label in enumerate(labels):
            if label == '_ct':
                colors[i] = ((y[i] - min_y) / max_y) * \
                            (self.config['ct_max_color'] - self.config['ct_min_color']) \
                            + self.config['ct_min_color']
            elif label == '_selected':
                colors[i] = .2
            else:
                seeded_rand = random.Random(label)
                colors[i] = seeded_rand.random() * \
                            (self.config['lead_max_color'] - self.config['lead_min_color']) \
                            + self.config['lead_min_color']
        return colors

    def contains(self, picker):
        return True if self._plot else False  # and picker.pick_position in self.ct.xyz(self.label)

    def plot(self):
        labels, x, y, z = self.ct.xyz(self.label)
        self._plot = mlab.points3d(x, y, z,  # self.get_colors(labels, x, y, z),
                                   mode='cube', resolution=3,
                                   colormap=self.colormap,
                                   opacity=.5,
                                   vmax=1, vmin=0,
                                   scale_mode='none', scale_factor=1)
        self._plot.mlab_source.set(scalars=self.get_colors(labels, x, y, z))

    def unplot(self):
        self._plot.mlab_source.reset(x=[], y=[], z=[], scalars=[])

    def update(self):
        labels, x, y, z = self.ct.xyz(self.label)
        log.debug("Updating cloud {} with {} points".format(self.label, len(labels)))
        self._plot.mlab_source.reset(
            x=x, y=y, z=z, scalars=self.get_colors(labels, x, y, z))


class AxisView(CloudView):

    def __init__(self,ct,config,callback=None):
        super(AxisView, self).__init__(ct,config=config,label='Axis',callback=callback)
        self.scale = 35
        self._plots = []

    def plot(self):
        coords = self.ct._points.coordinates
        center = np.array([0.5*(coords[:,i].max() + coords[:,i].min()) for i in range(3)])
        u,v,w,t = self.ct.affine.T
        max_dist = np.abs(coords-center).max()

        for i,(axis,name_pair) in enumerate(zip((u,v,w),(('R','L'),('A','P'),('S','I')))):
            for name in name_pair:
                location  = center.copy()
                if name is name_pair[0]:
                    location[i] += max_dist*1.25 * np.sign(axis[i])
                else:
                    location[i] -= max_dist * 1.25 * np.sign(axis[i])
                color = [0.,0.,0.]
                color[i] = 1.
                letter = mlab.text3d(location[0], location[1], location[2], name, color=tuple(color), scale=self.scale,
                                     opacity=0.75,
                                     )
                self._plots.append(letter)

    def contains(self, picker):
        return False

    def update(self):
        return

    def hide(self):
        for plot in self._plots:
            plot.visible=False

    def show(self):
        for plot in self._plots:
            plot.visible = True

    def unplot(self):
        for plot in self._plots:
            plot.remove()
        self._plots = []



if __name__ == '__main__':
    # controller = PylocControl(yaml.load(open(os.path.join(os.path.dirname(__file__) , "../config.yml"))))
    #controller = PylocControl()
    controller = PylocControl(yaml.load(open(os.path.join(os.path.dirname(__file__), "../config.yml"))))

    # controller.load_ct("../T01_R1248P_CT.nii.gz")
    # controller.load_ct('/Volumes/rhino_mount/data10/RAM/subjects/R1226D/tal/images/combined/R1226D_CT_combined.nii.gz')
    controller.load_ct('/Users/iped/PycharmProjects/voxTool/R1226D_CT_combined.nii.gz')
    controller.set_leads(
        #    ["sA", "sB", "dA", "dB"], ["S", "S", "D", "D"], ([[6, 1]] * 2) + ([[8, 1]] * 2), ([5] * 2) + ([5] * 2), [10] * 4
        ("G45", "G48"), ("G", "G"), ([4, 5], [4, 8]), [5, 5], [10, 10]
        # ["dA", "dB", "dC"], ["D", "D", "G"], [[8, 1], [8, 1], [4, 4]], [5, 10, 10], [10, 20, 20]
    )
    controller.exec_()

if __name__ == 'x__main__':
    app = QtGui.QApplication.instance()
    x = LeadDefinitionWidget(None, yaml.load(open(os.path.join(os.path.dirname(__file__), "../model/config.yml"))))
    x.show()
    window = QtGui.QMainWindow()
    window.setCentralWidget(x)
    window.show()
    app.exec_()