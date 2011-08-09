# -*- coding: utf-8 -*-
from plugin_multiselect_widget import multiselect_widget
db = DAL('sqlite:memory:')
db.define_table('product', Field('colors', 'list:integer'))
db.product.colors.requires = IS_EMPTY_OR(IS_IN_SET([(1, 'red'), (2, 'blue'), (3, 'green')],
                                                  multiple=True)) 
db.product.colors.widget = multiselect_widget

def index():
    form = SQLFORM(db.product)
    if form.accepts(request.vars, session):
        session.flash = 'submitted : %s' % request.vars.colors
        redirect(URL('index'))
    return form
