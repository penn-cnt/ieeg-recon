__author__ = 'iped'

from traits.api import HasTraits, Instance, on_trait_change
from traitsui.api import View, Item
from mayavi.core.ui.api import MayaviScene, MlabSceneModel, \
        SceneEditor
from mayavi import mlab
from pyface.qt import QtGui, QtCore
import matplotlib.pyplot as plt

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

import numpy as np

class SliceViewWidget(QtGui.QWidget):

    def __init__(self, parent=None, scan=None):
        QtGui.QWidget.__init__(self, parent)
        self.label = QtGui.QLabel('')
        self.label.setWordWrap(True)
        data = scan.data if scan else None
        self.views = [
            SliceView(self, data, axis=0, subplot=311),
            SliceView(self, data, axis=1, subplot=312),
            SliceView(self, data, axis=2, subplot=313)
        ]

        splitter = QtGui.QSplitter(QtCore.Qt.Vertical)
        for view in self.views:
            splitter.addWidget(view)

        self.ct = None
        p = self.palette()
        p.setColor(self.backgroundRole(), QtCore.Qt.black)
        self.setPalette(p)

        layout = QtGui.QVBoxLayout(self)
        layout.addWidget(self.label)
        layout.addWidget(splitter)

    def set_coordinate(self, coordinate):
        for slice_view in self.views:
            slice_view.coordinate = coordinate

    def set_image(self, image):
        for slice_view in self.views:
            slice_view.set_image(image)

    def set_label(self,label):
        self.label.setText('File: \n%s'%label)

    def update(self):
        for slice_view in self.views:
            slice_view.plot()

class SliceView(FigureCanvas):

    scene = Instance(MlabSceneModel, ())

    def __init__(self, parent=None, image=None, axis=None, subplot=1):
        self.fig = Figure(facecolor='black')
        self.axes = self.fig.add_subplot(1, 1, 1)

        self.image = image
        self.axis = axis
        self.plotted = False
        self.coordinate = (0,0,0)
        #self.figure = self.scene.mlab.gcf()
        self.radius = None
        self._plot = None
        self.subplot = subplot

        FigureCanvas.__init__(self, self.fig)
        self.setParent(parent)

        FigureCanvas.setSizePolicy(self,
                                   QtGui.QSizePolicy.Expanding,
                                   QtGui.QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)


    def set_image(self, image):
        self.image = image

    def set_axis(self, axis):
        self.axis = axis

    def plot(self):
        if self.axis is None or self.image is None:
            return
        plot_plane = [slice(0, self.image.shape[i]) for i in range(3)]
        plot_plane[self.axis] = int(self.coordinate[self.axis])
        print(plot_plane)

        plotted_image = self.image[tuple(plot_plane)]
        plotted_image = np.flipud(plotted_image.T)
        extent = [0, plotted_image.shape[0], 0, plotted_image.shape[1], 0, 0]
        self.axes.cla()
        self.axes.set_xlabel('')
        self.axes.set_ylabel('')
        self.axes.set_xticklabels([])
        self.axes.set_yticklabels([])
        self.axes.set_facecolor((0,0,0))
        self._plot = self.axes.imshow(plotted_image, cmap=plt.get_cmap('bone'))
        plt.axis('off')
        circl_coords = list(self.coordinate)
        del circl_coords[self.axis]
        radius = 10 if self.axis != 3 else 40

        if self.axis != 2:
            circl_coords[0], circl_coords[1] = circl_coords[0], plotted_image.shape[0] - circl_coords[1]
        else:
            circl_coords[1] = plotted_image.shape[0] - circl_coords[1]

        self.circ = plt.Circle(circl_coords, radius=radius, edgecolor='r', fill=False)
        self.axes.add_patch(self.circ)
        #plt.tight_layout()
        #self._plot = plt.imshow(self.image[plot_plane], colormap='bone')#, aspect='auto')
        #src = self._plot.mlab_source
        #src.x = 100*(src.x - src.x.min())/(src.x.max() - src.x.min())
        #src.y = 100*(src.y - src.y.min())/(src.x.max() - src.y.min())
        self.draw()


    #@on_trait_change('scene.activated')
    #def update(self):
    #    self.plot()

    #view = View(Item('scene', editor=SceneEditor(scene_class=MayaviScene),
    #                 height=250, width=300, show_label=False),
    #            resizable=True  # We need this to resize with the parent widget
    #            )