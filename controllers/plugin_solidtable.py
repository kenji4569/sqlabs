# -*- coding: utf-8 -*-
from plugin_solidtable import SOLIDTABLE, OrderbySelector
from gluon.contrib.populate import populate

db = DAL('sqlite:memory:')
db.define_table('product', 
    Field('name'), 
    Field('status', requires=IS_IN_SET(['new', 'old'])), 
    Field('description', 'text'), 
    Field('publish_date', 'date'),
    Field('price', 'integer', represent=lambda v: '$%s' % v ), 
    )
populate(db.product, 10)

def index():
    orderby_selector = OrderbySelector('product.id')
    
    tax = db.product.price*5/100
    tax.represent = db.product.price.represent
    taxed_price = db.product.price + tax
    taxed_price.represent = db.product.price.represent
    
    rows = db().select(db.product.ALL, tax, taxed_price,
                       orderby=orderby_selector.orderby())
    headers = {'product.name':{'selected': True},
               'product.description':{'label':'Details', 'class':'italic', 
                                      'width':'200px', 'truncate':38,},
               tax:{'label': 'Tax'},
               taxed_price:{'label': 'Taxed Price'}
               }
    extracolumns = [{'label':A('Edit', _href='#'),
                     'content':lambda row, rc: A('Edit',_href='edit/%s'%row.product.id)},
                    {'label':A('Delete', _href='#'),
                     'content':lambda row, rc: A('Delete',_href='delete/%s'%row.product.id)},     
                    ]
    # --- the structure of "columns" defines the multi-line header layout ---
    table = SOLIDTABLE(rows,  
            columns=[extracolumns[0], 
                     'product.id', 
                     'product.name',
                     ['product.status','product.publish_date'], 
                     ['product.price', 'product.description'], 
                     [tax, None],
                     [taxed_price, None],
                    ], 
            headers=headers,
            extracolumns=extracolumns,
            orderby=orderby_selector,
            renderstyle=True, linkto=URL('show'), 
            selectid=lambda r: r.product.id==7)
    return dict(table=DIV(table, STYLE('.italic {font-style: italic;}')))



