# -*- coding: utf-8 -*-

import os
import dummy

DEBUG = True
TEMPLATE_DEBUG = DEBUG

SNS = 'test'
MEDIA_VER = 'v1'

SITE_ROOT = os.path.dirname(os.path.realpath(dummy.__file__))
SITE_PROJECT_NAME = os.path.basename(SITE_ROOT)

import_settings_file = 'from platforms.conf.settings_%s import *' % SNS

try:
    exec(import_settings_file)
except ImportError:
    import sys
    sys.stderr.write("Error: Can't find the file 'settings_%s.py' in the directory platforms/conf/\n" % SNS)
    sys.exit(1)

