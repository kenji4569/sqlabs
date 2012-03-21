# -*- coding: utf-8 -*-
from plugin_solidtable import SOLIDTABLE, OrderbySelector
from gluon.contrib.populate import populate

db = DAL('sqlite:memory:')
db.define_table('product',
    Field('name'),  Field('status', requires=IS_IN_SET(['new', 'old'])),
    Field('description', 'text'),
    Field('publish_start_date', 'date', label='start'),
    Field('publish_end_date', 'date', label='end'),
    Field('price', 'integer', represent=lambda v: '$%s' % v),
    )
populate(db.product, 10)


def index():
    tax = db.product.price * 5 / 100
    tax.represent = db.product.price.represent
    pretax_price = db.product.price + tax
    pretax_price.represent = db.product.price.represent
    
    request_headers = request.vars.headers or 'default'
    request_columns = request.vars.columns or 'default'
    
################################ The core ######################################
    # A custom orderby selector for the solidtable.
    orderby_selector = OrderbySelector([db.product.id, db.product.name,
                                        ~db.product.publish_start_date, ~pretax_price])
    
    rows = db().select(db.product.ALL, tax, pretax_price,
                       orderby=orderby_selector.orderby())
             
    if request_headers == 'default':
        # The "headers" is a dictionary of dictionaries for updating default values.
        # Custom fields such as "tax" can be passed to the dictionary keys.
        headers = {'product.name': {'selected': True},
                   'product.description': {'label': 'Details', 'class': 'italic',
                                           'width': '200px', 'truncate': 38},
                   tax: {'label': 'Tax'},
                   pretax_price: {'label': 'Pretax Price'}
                   }
    else:
        # The "headers" can be 'labels' or 'fieldname:capitalize'
        headers = request_headers
               
    extracolumns = [{'label': A('Edit', _href='#'),
                     'content': lambda row, rc: A('Edit', _href='edit/%s' % row.product.id)},
                    {'label': A('Delete', _href='#'),
                     'content': lambda row, rc: A('Delete', _href='delete/%s' % row.product.id)},
                    ]
                    
    # The structure of "columns" defines the multi-line table layout
    # A "None" indicates an empty line over which the precedent line spans
    # Custom fields such as "tax" and extracolumns can be passed to the list of lists.
    if request_columns == 'default':
        columns = [[db.product.name, extracolumns[0]],
                     'product.id',
                     ['product.status', 'product.publish_start_date'],
                     [None, 'product.publish_end_date'],
                     [pretax_price, 'product.description'],
                     [tax, None],
                     ['product.price', None],
                 ]
    elif request_columns == 'columns_2':
        columns = [[db.product.name, extracolumns[0]],
                     None,
                     [pretax_price, 'product.description'],
                     None,
                     [tax, None],
                    ]
    elif request_columns == 'columns_3':
        columns = [[db.product.name, extracolumns[0]],
                     [None, 'product.description'],
                     [None, tax],
                   ]

    table = SOLIDTABLE(rows,
            columns=columns, extracolumns=extracolumns,
            headers=headers,
            orderby=orderby_selector,
            renderstyle=True, linkto=URL('show'), selectid=lambda r: r.product.id == 7)
################################################################################
            
    return dict(table=DIV(table, STYLE('.italic {font-style: italic;}')),
                table_args=DIV(A('headers=default', _href=URL(vars={'headers': 'default'})), ' ',
                               A('headers=labels', _href=URL(vars={'headers': 'labels'})), ' ',
                               A('headers=fieldname:capitalize', _href=URL(vars={'headers': 'fieldname:capitalize'})), ' ',
                               A('columns=default', _href=URL(vars={'columns': 'default'})), ' ',
                               A('columns=columns_2', _href=URL(vars={'columns': 'columns_2'})), ' ',
                               A('columns=columns_3', _href=URL(vars={'columns': 'columns_3'})), ' ',
                               ))
