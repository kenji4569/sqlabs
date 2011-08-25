# -*- coding: utf-8 -*-
from plugin_hradio_widget import hradio_widget

db = DAL('sqlite:memory:')
db.define_table('product', Field('color', 'integer'))
db.product.color.requires = IS_EMPTY_OR(IS_IN_SET([(1, 'red'), (2, 'blue'), (3, 'green')])) 

################################ The core ######################################
# Inject the horizontal radio widget
db.product.color.widget = hradio_widget
################################################################################

def index():
    form = SQLFORM(db.product)
    if form.accepts(request.vars, session):
        session.flash = 'submitted %s' % form.vars
        redirect(URL('index'))
    return dict(form=form)
