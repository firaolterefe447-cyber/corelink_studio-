import os
import sys

PROJECT_DIR = '/home/corelink/corelink_studio-'

if PROJECT_DIR not in sys.path:
    sys.path.insert(0, PROJECT_DIR)

os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings'

from config.wsgi import application
