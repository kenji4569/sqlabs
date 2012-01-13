# -*- coding: utf-8 -*-
from plugin_rating_widget import RatingWidget

db = DAL('sqlite:memory:')
db.define_table('product', 
    Field('rating', 'integer', 
          requires=IS_IN_SET(range(1,5)), # "requires" is necessary for the rating widget
))

################################ The core ######################################
# Inject the horizontal radio widget
db.product.rating.widget = RatingWidget()
################################################################################

def index():
    form = SQLFORM(db.product)
    if form.accepts(request.vars, session):
        session.flash = 'submitted %s' % form.vars
        redirect(URL('index'))
    return dict(form=form)
