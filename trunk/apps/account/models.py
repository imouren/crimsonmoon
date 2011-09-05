# -*- coding: utf-8 -*-

from datetime import date, datetime, timedelta
from django.db import models
from django.core.cache import cache
from apps.members.constants import *


class MemberAccount(models.Model):
    member_id = models.BigIntegerField(unique=True)
    coins = models.IntegerField(default=0)
    last_recharge_time = models.DateTimeField(auto_now_add=True)
    last_consume_time = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return u'%s<%s>' % (self.member_id, self.coins)

    class Meta:
        db_table = 'member_account'

class MemberPayRecord(models.Model):
    member_id = models.BigIntegerField(db_index=True)
    coins = models.IntegerField(default=0)
    style = models.CharField(max_length=128)
    name =  models.CharField(max_length=512)
    num = models.IntegerField(default=0)
    status = models.BooleanField(default=False)
    create_time = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return u'%s<%s>' % (self.member_id, self.create_time)

    class Meta:
        db_table = 'member_pay_record'

class UserDepositRecord(models.Model):
    member_id = models.BigIntegerField(db_index=True)
    coins = models.IntegerField(default=0)#游戏付费道具钱币
    rmb = models.IntegerField(default=0)#平台币
    verbose = models.CharField(max_length=512)
    status = models.BooleanField(default=False)
    create_time = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return u'%s<%s-%s>' % (self.member_id, self.coins, self.status)

    class Meta:
        db_table = 'member_deposit_record'