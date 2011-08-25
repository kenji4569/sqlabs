# -*- coding: utf-8 -*-
from plugin_anytime_widget import anytime_widget, anydate_widget, anydatetime_widget

db = DAL('sqlite:memory:')
db.define_table('product', 
    Field('event_time', 'time'), Field('publish_date', 'date'), Field('created_at', 'datetime'),
)

################################ The core ######################################
# Inject the corresponding anytime widgets for time, date, and datetime fields
db.product.event_time.widget = anytime_widget
db.product.publish_date.widget = anydate_widget
db.product.created_at.widget = anydatetime_widget
################################################################################

def index():
    form = SQLFORM(db.product)
    if form.accepts(request.vars, session):
        session.flash = 'submitted %s' % form.vars
        redirect(URL('index'))
    return dict(form=form)
