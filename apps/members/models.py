# -*- coding: utf-8 -*-

from datetime import date, datetime, timedelta
from django.db import models
from django.core.cache import cache
from apps.members.constants import *


class Member(models.Model):
    #human,vampire,wolf-human
    PLAYER_TYPE = (
        ('H', u'人类'),
        ('V', u'吸血鬼'),
        ('W', u'狼人'),
    )
    sns_id = models.BigIntegerField(unique=True) #SNS平台唯一数字标识
    open_id = models.CharField(max_length=128, unique=True) #SNS平台唯一非数字标识
    avatar = models.CharField(max_length=256, default='') #头像，应该给个默认的
    nickname = models.CharField(max_length=64) #昵称
    player_type = models.CharField(max_length=1, choices=PLAYER_TYPE)
    gold = models.IntegerField(default=0) #金币，游戏内交易和获得
    tutorial_tempo = models.IntegerField(default=0) # 新手教程进度，由客户端传入并保存
    power = models.IntegerField(default = 30) #体力值
    last_power_time = models.DateTimeField(auto_now_add=True) #最后更新体力时间
    
    def __unicode__(self):
        return u'%s<%s>' % (self.sns_id, self.nickname)

    class Meta:
        db_table = 'member'

class MemberRegisterAction(models.Model):
    REG_FROM_TYEP = (
        ('ME', u'自己注册'),
        ('IV', u'邀请注册'),
        ('AD', u'广告注册'),
    )
    member_id = models.BigIntegerField(unique=True) #SNS平台唯一数字标识
    come_from = models.CharField(max_length=2, choices=REG_FROM_TYEP) #用户注册来源，自己注册，邀请，广告等
    verbose = models.CharField(max_length=256) #来源或消费的详细
    reg_time = models.DateTimeField(auto_now_add=True) #注册时间
    reg_ip = models.CharField(max_length=32) #注册IP
    
    def __unicode__(self):
        return u'%s<%s-%s>' % (self.member_id, self.come_from, self.reg_time)

    class Meta:
        db_table = 'member_register_action'

class MemberLoginAction(models.Model):
    member_id = models.BigIntegerField() #用户的SNS_ID
    login_time = models.DateTimeField(auto_now_add=True) #登陆时间
    login_ip = models.CharField(max_length=32) #登陆IP
    
    def __unicode__(self):
        return u'%s<%s>' % (self.member_id, self.login_time)

    class Meta:
        db_table = 'member_login_action'

class MemberGameScores(models.Model):
    member_id = models.BigIntegerField(unique=True)
    scores = models.IntegerField(default=0)
    last_earn_time = models.DateTimeField(auto_now_add=True)
    last_consume_time = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return u'%s<%s>' % (self.member_id, self.scores)

    class Meta:
        db_table = 'member_game_scores'

class MemberGameScoreRecord(models.Model):
    GAME_SCORE_TYPE = (
        ('E',u'获得积分'),
        ('C',u'消费积分'),
    )
    member_id = models.BigIntegerField()
    scores = models.IntegerField(default=0)
    type = models.CharField(max_length=3, choices=GAME_SCORE_TYPE) #类型：消费或者获得
    verbose = models.CharField(max_length=128) #来源或消费的详细
    create_time = models.DateTimeField(auto_now_add=True)
    
    def __unicode__(self):
        return u'%s<%s-%s-%s>' % (self.member_id, self.scores, self.type, self.create_time)

    class Meta:
        db_table = 'member_game_score_record'
