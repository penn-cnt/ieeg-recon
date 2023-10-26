#! /usr/bin/env python

__author__ = 'iped'
import os
os.environ['ETS_TOOLKIT'] = 'qt4'
from view.pyloc import PylocControl
import yaml

if __name__ == '__main__':
    config = yaml.load(open(os.path.join(os.path.dirname(__file__), 'config.yml')))
    controller = PylocControl(config)
    controller.exec_()
