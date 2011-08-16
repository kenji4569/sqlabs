# -*- coding: utf-8 -*-
from plugin_anytime_widget import AnytimeStringWidget

SQLFORM.widgets.string = AnytimeStringWidget

db = DAL('sqlite:memory:')
db.define_table('product', 
    Field('event_time', 'time'), Field('publish_date', 'date'), Field('created_at', 'datetime'),
)
    
def index():
    form = SQLFORM(db.product)
    if form.accepts(request.vars, session):
        session.flash = 'submitted : event_time=%s publish_date=%s created_at=%s' % (
                            request.vars.event_time, request.vars.publish_date, request.vars.created_at,)
        redirect(URL('index'))
    return dict(form=form)
