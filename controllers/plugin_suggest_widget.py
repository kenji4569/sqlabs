# -*- coding: utf-8 -*-
from plugin_suggest_widget import suggest_widget

db = DAL('sqlite:memory:') 
db.define_table('category', Field('name'))
db.define_table('product', 
    Field('category_1'),
    Field('category_2', db.category),
    )
    
db.category.bulk_insert([{'name':'AAA'}, {'name':'AAC'}, {'name':'ABC'}, 
                         {'name':'BBB'}, {'name':'CCC'}])
                         
db.product.category_1.widget = suggest_widget(db.category.name, limitby=(0,10), min_length=1,
    keyword='_autocomplete_category_1_%(fieldname)s')
db.product.category_2.widget = suggest_widget(db.category.name, id_field=db.category.id, limitby=(0,10), min_length=1,
    keyword='_autocomplete_category_2_%(fieldname)s') 
     
def index():
    form = SQLFORM(db.product)
    if form.accepts(request.vars, session):
        session.flash = 'submitted %s' % form.vars
        redirect(URL('index'))
    return dict(form=form, categories=SQLTABLE(db().select(db.category.ALL)))