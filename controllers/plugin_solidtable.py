# -*- coding: utf-8 -*-
from plugin_solidtable import SOLIDTABLE, OrderbySelector
from gluon.contrib.populate import populate

db = DAL('sqlite:memory:')
db.define_table('product', 
    Field('name'),  Field('status', requires=IS_IN_SET(['new', 'old'])), 
    Field('description', 'text'),  Field('publish_date', 'date'),
    Field('price', 'integer', represent=lambda v: '$%s' % v ), 
    )
populate(db.product, 10)

def index():
    tax = db.product.price*5/100
    tax.represent = db.product.price.represent
    pretax_price = db.product.price + tax
    pretax_price.represent = db.product.price.represent
    
    orderby_selector = OrderbySelector([db.product.id, db.product.name, 
                                        ~db.product.publish_date, ~pretax_price])
    
    # import md5
    # print md5.new(str(db.product.id)).hexdigest()
    # print md5.new(str(~db.product.id)).hexdigest()
    # print md5.new(str(pretax_price)).hexdigest()
    # print md5.new(str(~pretax_price)).hexdigest()
    
    rows = db().select(db.product.ALL, tax, pretax_price,
                       orderby=orderby_selector.orderby())
    headers = {'product.name':{'selected': True},
               'product.description':{'label':'Details', 'class':'italic', 
                                      'width':'200px', 'truncate':38,},
               tax:{'label': 'Tax'},
               pretax_price:{'label': 'Pretax Price'}
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
                     db.product.name,
                     ['product.publish_date', 'product.status'], 
                     [pretax_price, 'product.description'], 
                     [tax, None],
                     ['product.price', None],
                    ], 
            headers=headers,
            extracolumns=extracolumns,
            orderby=orderby_selector,
            renderstyle=True, linkto=URL('show'), 
            selectid=lambda r: r.product.id==7)
    return dict(table=DIV(table, STYLE('.italic {font-style: italic;}')))



