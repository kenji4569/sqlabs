# -*- coding: utf-8 -*-
from plugin_horizontal_radio_widget import horizontal_radio_widget
db = DAL('sqlite:memory:')
db.define_table('product', Field('color', 'integer'))
db.product.color.requires = IS_EMPTY_OR(IS_IN_SET([(1, 'red'), (2, 'blue'), (3, 'green')])) 
db.product.color.widget = horizontal_radio_widget

def index():
    form = SQLFORM(db.product)
    if form.accepts(request.vars, session):
        session.flash = 'submitted : %s' % request.vars.color
        redirect(URL('index'))
    return dict(form=form)
