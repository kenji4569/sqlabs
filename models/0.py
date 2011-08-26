# -*- coding: utf-8 -*-

MODULE_RELOAD = True
SHOW_SOCIAL = False
GOOGLE_ANALYTICS = ""
FACEBOOK_SDK = ""
FACEBOOK_COMMENTS = ""
FACEBOOK_OG_ADMIN = ""
SITE_URL = ""

if 'language' in request.cookies and not (request.cookies['language'] is None):
    T.force(request.cookies['language'].value)