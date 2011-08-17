# -*- coding: utf-8 -*-
from plugin_anytime_widget import anytime_widget, anydate_widget, anydatetime_widget

db = DAL('sqlite:memory:')
db.define_table('product', 
    Field('event_time', 'time', widget=anytime_widget), 
    Field('publish_date', 'date', widget=anydate_widget), 
    Field('created_at', 'datetime', widget=anydatetime_widget),
)
    
def index():
    form = SQLFORM(db.product)
    if form.accepts(request.vars, session):
        session.flash = 'submitted : event_time=%s publish_date=%s created_at=%s' % (
                            request.vars.event_time, request.vars.publish_date, request.vars.created_at,)
        redirect(URL('index'))
    return dict(form=form)
