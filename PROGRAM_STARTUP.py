# -*- coding: utf-8 -*-
"""
Created on Sun Oct 17 09:58:32 2021

@author: Balazs
"""

import os

ROOT_FOLDER = 'E:\\Software Engineering\\SmartPurse'


os.chdir(ROOT_FOLDER)


# Methods
METHODS_FOLDER = ROOT_FOLDER + '\\methods'

RESOURCES_FOLDER = ROOT_FOLDER + '\\resources'


exec(open(METHODS_FOLDER + "\\libraries.py").read())

