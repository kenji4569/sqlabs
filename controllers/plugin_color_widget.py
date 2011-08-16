# -*- coding: utf-8 -*-
from plugin_color_widget import color_widget

db = DAL('sqlite:memory:')
db.define_table('product', Field('color', widget=color_widget))

# --- inject the color widget ---
db.product.color.widget = color_widget
# -------------------------------

def index():
    form = SQLFORM(db.product)
    if form.accepts(request.vars, session):
        session.flash = 'submitted : %s' % request.vars.color
        redirect(URL('index'))
    return dict(form=form)
