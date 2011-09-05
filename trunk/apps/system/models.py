# -*- coding: utf-8 -*-

from datetime import date, datetime, timedelta
from django.db import models
from django.core.cache import cache
from apps.members.constants import *


class MultiDB(models.Model):
    member_id = models.IntegerField()

    def save(self):
        if self.member_id <= LIMIT_USERS_ONE_DB:
            super(MultiDB,self).save(using='default')
        elif self.member_id <= 2*LIMIT_USERS_ONE_DB:
            super(MultiDB,self).save(using='second')
        elif self.member_id <= 3*LIMIT_USERS_ONE_DB:
            super(MultiDB,self).save(using='third')
            
    
    def delete(self):
        if self.member_id <= LIMIT_USERS_ONE_DB:
            super(MultiDB,self).delete(using='default')
        elif self.member_id <= 2*LIMIT_USERS_ONE_DB:
            super(MultiDB,self).delete(using='second')
        elif self.member_id <= 3*LIMIT_USERS_ONE_DB:
            super(MultiDB,self).delete(using='third')
    
    class Meta:
        abstract = True