import os

from globals.location import LOCATION

DATA_ROOT_FOLDER = LOCATION
LOG_FOLDER = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), ".logs")