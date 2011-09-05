# -*- coding: utf-8 -*-

from django.conf import settings

url_file = 'from platforms.conf.urls_%s import *' % settings.SNS

try:
    exec(url_file)
except ImportError:
    import sys
    sys.stderr.write("Error: Can't find the file 'urls_%s.py' in the directory platforms/conf/\n" % settings.SNS)
    sys.exit(1)
