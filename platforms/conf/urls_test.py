# -*- coding: utf-8 -*-

from django.conf.urls.defaults import *
from django.contrib import admin
from django.conf import settings

admin.autodiscover()

urlpatterns = patterns('',
    (r'^media/(?P<path>.*)$','django.views.static.serve',{'document_root': settings.MEDIA_ROOT}),
    (r'^jidi/', include(admin.site.urls)),
    (r'^(crossdomain.xml)$','django.views.static.serve',{'document_root': settings.SITE_ROOT}),
    #(r'^getCaptchaImage/$', 'apps.webservice.catchfish.getCaptchaImage'),
    #(r'^gateway/amfService/(.*)', 'amf.django.views', {'views':'platforms.login.login_sohu'}),
    #(r'^gateway/snsService/(.*)', 'amf.django.views', {'views':'platforms.sns_api.views'}),

)