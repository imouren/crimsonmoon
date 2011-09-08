# -*- coding: utf-8-*-

from settings import *
from platforms.conf.settings_fixed import *

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'crimsonmoon',
        'USER': 'root',
        'PASSWORD': 'mourenmouren',
        'HOST': '',
    },
}

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
        'LOCATION': 'd:/game_cache/crimsonmoon',
        'TIMEOUT': 60,
        'OPTIONS': {
            'MAX_ENTRIES': 1000
        }
    }
}

LIST_APPS = list(INSTALLED_APPS)
LIST_APPS.extend([
    'platforms.test.users',
])
INSTALLED_APPS = tuple(set(LIST_APPS))



TIME_ZONE = 'Asia/Shanghai'
LANGUAGE_CODE = 'zh-cn'
SITE_URL = 'http://127.0.0.1:8000'
MEDIA_ROOT = '/'
MEDIA_URL = '/media/'
ADMIN_MEDIA_PREFIX = '/media/admin/'
SECRET_KEY = '2k4aa7q-tqr@!%m*4da2p2@9qzg=-4lr7)w(b2!yh1zvaq_=9&'

LOGIN_URL = '/users/login/'
LOGOUT_URL = '/users/logout/'


