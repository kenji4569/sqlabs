# -*- coding: utf-8 -*-

MODULE_RELOAD = True
SHOW_SOCIAL = False
GOOGLE_ANALYTICS = ""
FACEBOOK_SDK = ""
FACEBOOK_COMMENTS = ""
FACEBOOK_OG_ADMIN = ""
SITE_URL = ""

MAIL_SERVER = 'logging' # or 'localhost:25' or 'smtp.gmail.com:587'  
MAIL_SENDER = 'you@gmail.com' 
MAIL_LOGIN = None # or 'username:password'
CONTACT_TO = 'info@gmail.com' 

if 'language' in request.cookies and not (request.cookies['language'] is None):
    T.force(request.cookies['language'].value)