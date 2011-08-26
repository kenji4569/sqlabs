# -*- coding: utf-8 -*-

@cache('%s-%s' % (request.env.path_info, T.accepted_language), time_expire=10, cache_model=cache.ram)
def index():
    d = dict(
        products=[
            (k, info_products[k])
                for k in ['web2py_plugins', 'cloudmap', 
                          'nanahoshi_cms', 'nanahoshi_db']
        ],
    )
    return response.render(d)
    
def contact():
    from gluon.tools import Mail
    from plugin_solidform import SOLIDFORM
    from plugin_notemptymarker import mark_not_empty
    
    mail = Mail()   
    mail.settings.server = MAIL_SERVER
    mail.settings.sender = MAIL_SENDER
    mail.settings.login = MAIL_LOGIN

    
    fields = [
        Field('name', label=T('Name'), requires=IS_NOT_EMPTY()),
        Field('email', label=T('Email'), requires=IS_EMAIL()),
        Field('subject', label=T('Subject'), requires=IS_LENGTH(200, 1)),
        Field('message', 'text', label=T('Message'), requires=IS_LENGTH(5000)),
    ]
    mark_not_empty(fields)
    form = SOLIDFORM.factory(submit_button=T('Send'), *fields)
    if form.accepts(request.vars, session):
        mail.send(
            to=CONTACT_TO,
            subject='sqlabs contact subject: %s' % form.vars.subject,
            message='name: %s\nemail: %s\nmessage: \n%s' % (form.vars.name, form.vars.email, form.vars.message),
        )
        session.flash = '%s %s' % (T('Your message has been sent.'), T('Thank you for your inquiry.'))
        redirect(request.vars.redirect or URL('default', 'index'))
        
    style = STYLE(""".w2p_fl {background: #eee;}""")
    return dict(form=DIV(style, form))
    