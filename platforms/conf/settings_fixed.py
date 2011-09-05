# -*- coding: utf-8 -*-

import os
from settings import *

ADMINS = (
    ('gmouren', 'gmouren@gmail.com'),
)

MANAGERS = ADMINS
USE_I18N = True
SITE_ID = 1
ROOT_URLCONF = '%s.urls' % SITE_PROJECT_NAME

SECRET_KEY = '2k4aa7q-tqr@!%m*4da2p2@9qzg=-4lr7)w(b2!yh1zvaq_=9&'
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
)
MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    #'amf.django.middleware.AMFMiddleware',
    'django.contrib.flatpages.middleware.FlatpageFallbackMiddleware',
)
TEMPLATE_DIRS = (
    os.path.join(SITE_ROOT, 'templates'),
)
INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.admin',
    'apps.account',
    'apps.members',
    'apps.system',
)


