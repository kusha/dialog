import sys
import os
sys.path.append(os.path.dirname(__file__))

STORAGEPATH = "tmp"
MODELDIR = "/usr/local/share/pocketsphinx/model"

from interpreter import Dialog, handle
