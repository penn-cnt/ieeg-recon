#! /usr/bin/env python

__author__ = 'bschied+allucas'
import os
import sys
import yaml
from voxtool.view.pyloc import PylocControl

def main():
    print('Running voxtool...')
    config_path = os.path.join(os.path.dirname(__file__), 'config.yml')
    with open(config_path) as config_file:
        config = yaml.safe_load(config_file)
    controller = PylocControl(config)
    controller.exec_()

if __name__ == '__main__':
    main()
