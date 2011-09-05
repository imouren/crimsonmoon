# -*- coding: utf-8 -*-


def get_client_referer(request):
    referer = request.META.get('HTTP_REFERER', None)
    return referer

def get_client_ip(request):
    try:
        if req.META.has_key('HTTP_X_FORWARDED_FOR'):
            real_ip =  req.META['HTTP_X_FORWARDED_FOR']
            ip = real_ip.split(",")[0]
        else:
            ip = req.META['REMOTE_ADDR']
    except:
        ip = None
    return ip

