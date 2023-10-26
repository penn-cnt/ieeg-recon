import numpy as np
from model.pointcloud import PointCloud
from mayavi import mlab
from traits.api import HasTraits, Instance, on_trait_change
from traitsui.api import View, Item
from mayavi.core.ui.api import MayaviScene, MlabSceneModel, \
        SceneEditor
from pyface.qt import QtGui, QtCore
import random

__author__ = 'iped'

class PointCloudController(object):

    def __init__(self, parent):
        self.parent = parent
        self.view = PointCloudWidget(self)



