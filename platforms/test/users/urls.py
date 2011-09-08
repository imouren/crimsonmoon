# -*- coding: utf-8 -*-

from django.conf.urls.defaults import *

urlpatterns = patterns('platforms.test.users.views',
    (r'^$', 'index'),
    (r'^logout/$', 'user_logout'),
    (r'^login/$', 'user_login'),
    (r'^register/$', 'register'),
    (r'^active_account/$', 'active_account'),
    (r'^forgot_password/$', 'forgot_password'),
    (r'^reset_password/$', 'reset_password'),
)