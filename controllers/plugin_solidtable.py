# -*- coding: utf-8 -*-
from plugin_solidtable import SOLIDTABLE
from gluon.contrib.populate import populate

db = DAL('sqlite:memory:')
db.define_table('product', 
    Field('name'), Field('status', requires=IS_IN_SET(['new', 'old'])), 
    Field('description', 'text'), 
    Field('publish_date', 'date'),
    Field('price', 'integer', represent=lambda v: '$%s' % v ), 
    )
populate(db.product, 10)

def index():
    rows = db().select(db.product.ALL)
    headers = {'product.name':{'selected': True},
               'product.description':{'label':'Details', 'class':'italic', 
                                      'width':'200px', 'truncate':38,},
               }
    extracolumns = [{'label':A('Edit', _href='#'),
                     'content':lambda row, rc: A('Edit',_href='edit/%s'%row.id)},
                    {'label':A('Delete', _href='#'),
                     'content':lambda row, rc: A('Delete',_href='delete/%s'%row.id)},     
                    ]
    
    table = SOLIDTABLE(rows,  
            headers=headers,
            columns=[extracolumns[0], 
                     'product.id', 
                     ['product.name', 'product.status',], 
                     ['product.publish_date', 'product.description'], 
                     ['product.price', None]
                    ], 
            extracolumns=extracolumns,
            renderstyle=True, linkto=URL('show'), selectid=7)
    return dict(table=DIV(table, STYLE('.italic {font-style: italic;}')))



