# -*- coding: utf-8 -*-

from datetime import date, datetime
import md5
import hashlib
import random
import string
import time

from django.shortcuts import render_to_response
from django.template import RequestContext, Context
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth import login, logout
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.http import Http404
from django.utils import simplejson
from apps.utils import *
from platforms.test.users.models import *
from platforms.test.users.helper import *
from platforms.test.users.forms import *



def register(request):
    if request.method == 'GET':
        form = RegForm(initial={'inviter_email':request.GET.get('i')})
        data = {'form':form, 'media_url':settings.MEDIA_URL}
        return render_to_response('users/register.html',data,
                                  context_instance=RequestContext(request))
    else:
        form = RegForm(request.POST)
        data = {'form':form, 'media_url':settings.MEDIA_URL}
        if form.is_valid():
            if settings.DEBUG:
                user = User(username=form.cleaned_data['username'], is_active=True)
            else:
                user = User(username=form.cleaned_data['username'], is_active=False)
            user.set_password(form.cleaned_data['password1'])
            user.save(using='userdb')

            profile = UserProfile(user_id=user.id, nickname=form.cleaned_data['nickname'],
                                  true_name=form.cleaned_data['true_name'],
                                  identity_card_code=form.cleaned_data['identity_card_code'])
            profile.save()
            
            # 如果存在邀请email则直接建立好友关系
            if form.cleaned_data['inviter_email']:
                try:
                    inviter_user = User.objects.using('userdb').get(username=form.cleaned_data['inviter_email'])
                    if inviter_user.id != user.id:
                        # 如果是邀请而来，自动建立好友关系
                        try:
                            own_friend_ids = get_friend_ids_office(inviter_user.id)
                            other_friend_ids = get_friend_ids_office(user.id)
                            if len(own_friend_ids) >= 500 or len(other_friend_ids) >= 500:
                                pass
                            else:
                                fs = FriendShip(from_user=inviter_user.id, to_user=user.id)
                                fs.save()
                        except:
                            pass
                        # 记录邀请信息
                        try:
                            invite = Invitation.objects.get(sender_id=inviter_user.id, invitee_id=user.id)
                        except:
                            invite = Invitation(sender_id=inviter_user.id, invitee_id=user.id)
                            invite.save()
                except:
                    import sys
                    print sys.exc_info()
            #insert user into ucenter db
            insert_flag = False
            try:
                member = UCenterMember.objects.using('ucenter').get(username=user.username)
            except UCenterMember.DoesNotExist:
                insert_flag = True
            except UCenterMember.MultipleObjectsReturned:
                insert_flag = False
            except:
                insert_flag = False
            
            if insert_flag:
                regip = get_client_ip(request)
                now_time = int(time.time())
                salt = get_salt()
                username = form.cleaned_data['username']
                password_str = form.cleaned_data['password1']
                password_one = hashlib.new('md5', password_str).hexdigest()
                password = hashlib.new('md5', (password_one+salt)).hexdigest()
                uc_member = UCenterMember(username=username,
                            password=password,
                            email=username,
                            salt=salt,
                            regip=regip,
                            regdate=now_time,
                            lastlogintime=now_time
                            )
                uc_member.save(using='ucenter')

            # 发送激活邮件
            if not settings.DEBUG:
                send_active_mail(user)
                common_mail = ['126.com', '163.com', 'sina.com', 'sohu.com', 'yahoo.com', 'qq.com']
                if user.username.split('@')[1].lower() in common_mail:
                    data['mail_login_url'] = 'mail.' + user.username.split('@')[1].lower()
                elif user.username.split('@')[1].lower() == 'hotmail.com':
                    data['mail_login_url'] = 'login.live.com'
                elif user.username.split('@')[1].lower() == 'gmail.com':
                    data['mail_login_url'] = 'mail.google.com'
                else:
                    data['mail_login_url'] = None
            return render_to_response('users/register_success.html', data,
                                      context_instance=RequestContext(request))
        else:
            return render_to_response('users/register.html', data,
                                      context_instance=RequestContext(request))


def active_account(request):
    mail = request.GET.get('mail', None)
    sig = request.GET.get('sig', None)
    try:
        user = User.objects.using('userdb').get(username=mail)
    except:
        raise Http404
    m = md5.new()
    u_sig = user.username.split('@')
    u_sig.insert(1, str(user.id))
    m.update(''.join(u_sig))
    confirm_sig = m.hexdigest()
    if sig == confirm_sig:
        user.is_active = True
        user.save(using='userdb')
        data = {'media_url':settings.MEDIA_URL}
        return render_to_response('users/active_account_success.html', data,
                                      context_instance=RequestContext(request))
    else:
        raise Http404


def user_login(request):
    data = {'media_url':settings.MEDIA_URL}
    if request.method == 'GET':
        form = AuthenticationForm()
        data['form'] = form
        return render_to_response('users/index.html',data,
                                  context_instance=RequestContext(request))
    else:
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            #ucenter
            username = form.cleaned_data.get("username", "")
            password_str = form.cleaned_data.get("password", "")
            insert_flag = False
            try:
                member = UCenterMember.objects.using('ucenter').get(username=username)
            except UCenterMember.DoesNotExist:
                insert_flag = True
            except UCenterMember.MultipleObjectsReturned:
                insert_flag = False
            except:
                insert_flag = False
            
            if insert_flag:
                regip = get_client_ip(request)
                now_time = int(time.time())
                salt = get_salt()
                password_one = hashlib.new('md5', password_str).hexdigest()
                password = hashlib.new('md5', (password_one+salt)).hexdigest()
                uc_member = UCenterMember(username=username,
                            password=password,
                            email=username,
                            salt=salt,
                            regip=regip,
                            regdate=now_time,
                            lastlogintime=now_time
                            )
                uc_member.save(using='ucenter')
                
            login(request, form.get_user())
            if request.session.test_cookie_worked():
                request.session.delete_test_cookie()
            request.session.set_expiry(3600*12)
            return HttpResponseRedirect('/play/')
        else:
            user = form.get_user()
            if user and not user.is_active:
                # 重新发送激活邮件
                try:
                    send_active_mail(user)
                    common_mail = ['126.com', '163.com', 'sina.com', 'sohu.com', 'yahoo.com', 'qq.com']
                    if user.username.split('@')[1].lower() in common_mail:
                        data['mail_login_url'] = 'mail.' + user.username.split('@')[1].lower()
                    elif user.username.split('@')[1].lower() == 'hotmail.com':
                        data['mail_login_url'] = 'login.live.com'
                    elif user.username.split('@')[1].lower() == 'gmail.com':
                        data['mail_login_url'] = 'mail.google.com'
                    else:
                        data['mail_login_url'] = None
                except:
                    pass
                login(request, user)
                return render_to_response('users/account_not_active_failed.html',data,
                                          context_instance=RequestContext(request))
            else:
                return render_to_response('users/login_failed.html',data,
                                  context_instance=RequestContext(request))


def user_logout(request):
    if request.user.is_authenticated():
        logout(request)
    hr = HttpResponseRedirect('/users/login/')
    hr.delete_cookie('kx_connect_session_key', path='/', domain='.dandanlong.com')

    return hr


@login_required
def basic_settings(request):
    up = get_up(request.user.id)
    if request.method == 'GET':
        data = {'city':up.city,
                'address':up.address,
                'msn':up.msn,
                'qq':up.qq,
                'gtalk':up.gtalk,
                'mobile':up.mobile,
                'description':up.description
                }
        form = BasicForm(data)
        data = {'form':form,'media_url':settings.MEDIA_URL}
        return render_to_response('users/settings.html', data,
                                  context_instance=RequestContext(request))
    else:
        form = BasicForm(request.POST)
        if form.is_valid():
            up.city = request.POST['city']
            up.address = request.POST['address']
            up.msn = request.POST['msn']
            up.qq = request.POST['qq']
            up.gtalk = request.POST['gtalk']
            up.mobile = request.POST['mobile']
            up.description = request.POST['description']
            up.save(using='userdb')
            return HttpResponseRedirect('/users/basic_settings/')

@login_required
def account_settings(request):
    if request.method == 'GET':
        form = PasswordChangeForm(request.user)
        data = {'form':form, 'media_url':settings.MEDIA_URL}
        return render_to_response('users/change_password.html', data,
                                  context_instance=RequestContext(request))
    else:
        form = PasswordChangeForm(request.user,request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.save(using='userdb')
            #ucenter
            salt = get_salt()
            password_str = form.cleaned_data.get("new_password1", "")
            password_one = hashlib.new('md5', password_str).hexdigest()
            password = hashlib.new('md5', (password_one+salt)).hexdigest()
            uc_member = None
            try:
                uc_member = UCenterMember.objects.using('ucenter').get(username=user.username)
            except:
                uc_member = None
            if uc_member is not None:
                uc_member.password = password
                uc_member.salt = salt
                uc_member.save(using='ucenter')
                
            data = {'info':'密码修改成功！', 'form':form, 'media_url':settings.MEDIA_URL}
            return render_to_response('users/change_password.html',data,
                                  context_instance=RequestContext(request))
        else:
            data = {'info':'密码修改失败！', 'form':form, 'media_url':settings.MEDIA_URL}
            return render_to_response('users/change_password.html',data,
                                  context_instance=RequestContext(request))

@login_required
def justforfun_settings(request):
    up = get_up(request.user.id)
    if request.method == 'GET':
        data = {'true_name':up.true_name,
                'identity_card_code':up.identity_card_code,
                }
        form = JustForFunForm(data)
        data = {'form':form, 'media_url':settings.MEDIA_URL}
        return render_to_response('users/just_for_fun.html', data,
                                  context_instance=RequestContext(request))
    else:
        form = JustForFunForm(request.POST)
        if form.is_valid():
            up.true_name = request.POST['true_name']
            up.identity_card_code = request.POST['identity_card_code']
            up.save(using='userdb')
            data = {'info':'防沉迷信息修改成功！', 'form':form, 'media_url':settings.MEDIA_URL}
            return render_to_response('users/just_for_fun.html',data,
                                  context_instance=RequestContext(request))
        else:
            data = {'info':'防沉迷信息修改失败！', 'form':form, 'media_url':settings.MEDIA_URL}
            return render_to_response('users/just_for_fun.html',data,
                                  context_instance=RequestContext(request))

def forgot_password(request):
    if request.method == 'GET':
        form = ForgotPasswordForm()
        data = {'form':form, 'media_url':settings.MEDIA_URL}
        return render_to_response('users/forgot_password.html', data,
                                  context_instance=RequestContext(request))
    else:
        form = ForgotPasswordForm(request.POST)
        data = {'form':form, 'media_url':settings.MEDIA_URL}
        if form.is_valid():
            user = User.objects.using('userdb').get(username=form.cleaned_data['username'])
            m = md5.new()
            u_sig = user.username.split('@')
            u_sig.insert(0, str(user.id))
            m.update(''.join(u_sig))
            sig = m.hexdigest()
            reset_url = "%s/users/reset_password/?mail=%s&sig=%s" %(settings.SITE_URL, user.username, sig)
            # 发送重置密码邮件
            subject = "《蛋蛋龙》游戏密码重置链接"
            t = loader.get_template('users/forgot_password_email.html')
            c = Context({
                    'nickname': get_up(user.id).nickname,
                    'reset_url':reset_url,
                })
            send_mail(subject, t.render(c), '"蛋蛋龙"<administrator@dandanlong.com>', [user.username,])
            common_mail = ['126.com', '163.com', 'sina.com', 'sohu.com', 'yahoo.com', 'qq.com']
            if user.username.split('@')[1].lower() in common_mail:
                data['mail_login_url'] = 'mail.' + user.username.split('@')[1].lower()
            elif user.username.split('@')[1].lower() == 'hotmail.com':
                data['mail_login_url'] = 'login.live.com'
            elif user.username.split('@')[1].lower() == 'gmail.com':
                data['mail_login_url'] = 'mail.google.com'
            else:
                data['mail_login_url'] = None
            return render_to_response('users/reset_password.html', data,
                                      context_instance=RequestContext(request))
        else:
            return render_to_response('users/forgot_password.html', data,
                                      context_instance=RequestContext(request))


def reset_password(request):
    mail = request.GET.get('mail', None)
    sig = request.GET.get('sig', None)
    try:
        user = User.objects.using('userdb').get(username=mail)
    except:
        raise Http404
    m = md5.new()
    u_sig = user.username.split('@')
    u_sig.insert(0, str(user.id))
    m.update(''.join(u_sig))
    confirm_sig = m.hexdigest()
    if sig == confirm_sig:
        new_password = User.objects.make_random_password(8)
        user.set_password(new_password)
        user.save(using='userdb')
        #ucenter
        salt = get_salt()
        password_one = hashlib.new('md5', new_password).hexdigest()
        password = hashlib.new('md5', (password_one+salt)).hexdigest()
        uc_member = None
        try:
            uc_member = UCenterMember.objects.using('ucenter').get(username=user.username)
        except:
            uc_member = None
        if uc_member is not None:
            uc_member.password = password
            uc_member.salt = salt
            uc_member.save(using='ucenter')
        # 发送重置密码邮件
        subject = "《蛋蛋龙》游戏密码重置"
        t = loader.get_template('users/reset_password_email.html')
        c = Context({
                'nickname': get_up(user.id).nickname,
                'username': user.username,
                'new_password': new_password
            })
        send_mail(subject, t.render(c), '"蛋蛋龙"<administrator@dandanlong.com>', [user.username,])
        common_mail = ['126.com', '163.com', 'sina.com', 'sohu.com', 'yahoo.com', 'qq.com']
        data = {'media_url':settings.MEDIA_URL}
        if user.username.split('@')[1].lower() in common_mail:
            data['mail_login_url'] = 'mail.' + user.username.split('@')[1].lower()
        elif user.username.split('@')[1].lower() == 'hotmail.com':
            data['mail_login_url'] = 'login.live.com'
        elif user.username.split('@')[1].lower() == 'gmail.com':
            data['mail_login_url'] = 'mail.google.com'
        else:
            data['mail_login_url'] = None
        return render_to_response('users/reset_password_success.html', data,
                                  context_instance=RequestContext(request))
    else:
        raise Http404


@login_required
def users_invite(request):
    from apps.members.cache import get_or_create_member_property
    member = get_member_by_sns_id(request.user.id)
    member_property = get_or_create_member_property(member.id)
    invite_score = member_property.invite_score
    msg=u'''成功邀请1个好友玩蛋蛋龙，可获得1点积分。积分在游戏中可用于任务兑换，您现在的积分为%s分''' % invite_score
    invite_url = '%s/users/register/?i=%s' % (settings.SITE_URL, request.user.username)
    return render_to_response('users/invite.html', 
                              {'media_url':settings.MEDIA_URL,
                               'invite_url':invite_url,
                               'msg':msg},
                               context_instance=RequestContext(request))


def requestFriendAMF(request, owner_sns_id, friend_sns_id):
    to_id = int(friend_sns_id)
    from_id = int(owner_sns_id)
    up = get_up(to_id)
    if not up:
        return {'error':'user does not exist'}

    if from_id == to_id:
        return {'error':'can not add self as friend'}

    f1 = FriendShip.objects.using('userdb').filter(from_user=from_id, to_user=to_id)
    f2 = FriendShip.objects.using('userdb').filter(from_user=to_id, to_user=from_id)
    friendship = f1 or f2
    if friendship:
        if friendship[0].confirmed:
            return {'error':'friend already exist'}
        else:
            return {'error':'invitation already send'}
    fs = FriendShip(from_user=from_id, to_user=to_id)
    fs.save()
    own_friend_ids = get_all_friends(to_id)
    if from_id not in own_friend_ids:
        own_friend_ids.append(from_id)
        set_all_friends(to_id, own_friend_ids)
    return {'status':'success'}


def confirmFriendAMF(request, owner_sns_id, friend_sns_id):
    from_id = int(friend_sns_id)
    to_id = int(owner_sns_id)
    try:
        friendship = FriendShip.objects.using('userdb').get(from_user=from_id, to_user=to_id)
        if not friendship.confirmed:
            own_friend_ids = get_friend_ids_office(to_id)
            other_friend_ids = get_friend_ids_office(from_id)
            if len(own_friend_ids) >= 500:
                return {'error': 'own friends is full'}
            if len(other_friend_ids) >= 500:
                return {'error': 'other friends is full'}
            friendship.confirmed = True
            friendship.save()
            if from_id not in own_friend_ids:
                own_friend_ids.append(from_id)
                set_friend_ids_office(to_id, own_friend_ids)
            if to_id not in other_friend_ids:
                other_friend_ids.append(to_id)
                set_friend_ids_office(from_id, other_friend_ids)
            other_all_friend_ids = get_all_friends(from_id)
            if to_id not in other_all_friend_ids:
                other_all_friend_ids.append(to_id)
                set_all_friends(from_id, other_all_friend_ids)
            return {'status':'success'}
        else:
            return {'error':'friend already exist'}
    except FriendShip.DoesNotExist:
        import sys
        print sys.exc_info()
        return {'error':'friend does not exist'}


def deleteFriendAMF(request, owner_sns_id, friend_sns_id):
    to_id = int(owner_sns_id)
    from_id = int(friend_sns_id)
    fps = []
    fp1 = FriendShip.objects.using('userdb').filter(from_user=from_id, to_user=to_id)
    fp2 = FriendShip.objects.using('userdb').filter(from_user=to_id, to_user=from_id)
    fps.extend(fp1)
    fps.extend(fp2)
    if not fps:
       return {'error':'friend does not exist'}
    else:
        for fp in fps:
            fp.delete()
        own_friend_ids = get_friend_ids_office(to_id)
        other_friend_ids = get_friend_ids_office(from_id)
        own_all_friend_ids = get_all_friends(to_id)
        other_all_friend_ids = get_all_friends(from_id)
        if from_id in own_friend_ids:
            own_friend_ids.remove(from_id)
            set_friend_ids_office(to_id, own_friend_ids)
        if to_id in other_friend_ids:
            other_friend_ids.remove(to_id)
            set_friend_ids_office(from_id, other_friend_ids)

        if from_id in own_all_friend_ids:
            own_all_friend_ids.remove(from_id)
            set_all_friends(to_id, own_all_friend_ids)
        if to_id in other_all_friend_ids:
            other_all_friend_ids.remove(to_id)
            set_all_friends(from_id, other_all_friend_ids)
        return {'status':'success'}


def disableUserAMF(request, mem_id):
    member = get_member(int(mem_id))
    if settings.SNS == 'office':
        up = get_up(member.sns_id)
        up.disabled_time = datetime.now()
        up.save()
    else:
        from apps.members.helper import update_member_disable_time
        update_member_disable_time(member.id)

@login_required
def users_sync(request):
    from apps.sns.sns_msg_sina import is_send_feed
    status = is_send_feed(request.user.id)
    data = {'sns_url': settings.SNS_URL, 'media_url':settings.MEDIA_URL, 'status': str(status)}
    return render_to_response('users/sync_bind.html', data, context_instance=RequestContext(request))

