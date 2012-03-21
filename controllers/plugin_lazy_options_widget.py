# -*- coding: utf-8 -*-
from plugin_lazy_options_widget import lazy_options_widget
from plugin_suggest_widget import suggest_widget

db = DAL('sqlite:memory:')
db.define_table('category', Field('name'))
db.define_table('color', Field('category', db.category), Field('name'))
db.define_table('product',
    Field('category', db.category, comment='<- type "A" or "B"'),
    Field('color', db.color,
          requires=IS_EMPTY_OR(IS_IN_DB(db(db.color.id > 0), 'color.id', 'color.name', zero='---')),
          comment='<- select category first'),
    )
    
db.category.bulk_insert([{'name':'A'}, {'name':'B'}])
for category in db(db.category.id > 0).select():
    _id = category.id
    if category.name == 'A':
        db.color.bulk_insert([{'category': _id, 'name':'red'}, {'category': _id, 'name':'blue'}])
    elif category.name == 'B':
        db.color.bulk_insert([{'category': _id, 'name':'green'}])
     
db.product.category.widget = suggest_widget(db.category.name, id_field=db.category.id,
                                          limitby=(0, 10), min_length=1)
     
from gluon.storage import Storage
session.auth = Storage(hmac_key='test')
                                        
################################ The core ######################################
# The lazy_options_widget receives js events
# called "product_category__selected" and "product_category__unselected"
# which will be triggered by the above suggest_widget.]
# You can also pass user_signature and hmac_key arguments for authorization in ajax
db.product.color.widget = lazy_options_widget(
                  'product_category__selected', 'product_category__unselected',
                  lambda category_id: (db.color.category == category_id),
                  request.vars.category,
                  orderby=db.color.id,
                  user_signature=True,
                  # If you want to process ajax requests at the time of the object construction (not at the form rendered),
                  # specify your target field in the following:
                  field=db.product.color,
                  )
################################################################################


def index():
    form = SQLFORM(db.product)
    if form.accepts(request.vars, session):
        session.flash = 'submitted %s' % form.vars
        redirect(URL('index'))
    return dict(form=form,
                categories=SQLTABLE(db().select(db.category.ALL)),
                colors=SQLTABLE(db(db.color.id > 0)(db.color.category == db.category.id
                                ).select(db.color.id, db.category.name, db.color.name)))
