# -*- coding: utf-8 -*-
from plugin_multiselect_widget import (
    hmultiselect_widget, vmultiselect_widget,
    rhmultiselect_widget, rvmultiselect_widget,
)
db = DAL('sqlite:memory:')
db.define_table('product',
    Field('colors', 'list:integer',
          requires=[IS_NOT_EMPTY(), IS_IN_SET([(1, 'red'), (2, 'blue'), (3, 'green')], multiple=True)]),
    Field('shapes',
          requires=IS_IN_SET(['circle', 'square', 'triangle'], multiple=True)),
    Field('colors2', 'list:integer',
          requires=IS_IN_SET([(1, 'red'), (2, 'blue'), (3, 'green')], multiple=True)),
    Field('shapes2',
          requires=IS_IN_SET(['circle', 'square', 'triangle'], multiple=True)),
)

################################ The core ######################################
# Inject the horizontal multiple select widget
db.product.colors.widget = hmultiselect_widget
# Inject the vertical multiple select widget
db.product.shapes.widget = vmultiselect_widget
# Inject the reversed horizontal multiple select widget
db.product.colors2.widget = rhmultiselect_widget
# Inject the reversed vertical multiple select widget
db.product.shapes2.widget = rvmultiselect_widget
################################################################################


def index():
    form = SQLFORM(db.product)
    if form.accepts(request.vars, session):
        session.flash = 'submitted %s' % form.vars
        redirect(URL('index'))
    return dict(form=form)
