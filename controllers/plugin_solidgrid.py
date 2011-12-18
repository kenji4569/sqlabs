# -*- coding: utf-8 -*-
from plugin_solidgrid import SolidGrid

### define tables ##############################################################
table_product = db.define_table('plugin_solidgrid_product', 
    Field('name', notnull=True),  
    Field('status', requires=IS_IN_SET(['new', 'old'])), 
    Field('description', 'text'), 
    Field('publish_date', 'date', represent=lambda v: v or '---'), 
    Field('price', 'integer', represent=lambda v: '$%s' % v if v else '---' ), 
    Field('created_on', 'datetime', default=request.now, readable=False, writable=False),
)

### populate records ###########################################################

import datetime
if db(table_product.created_on<request.now-datetime.timedelta(minutes=60)).count():
    table_product.truncate()
    session.flash = 'the database has been refreshed'
    redirect(URL('index'))

### fake authentication ########################################################

from gluon.storage import Storage
session.auth = Storage(hmac_key='test')

### demo functions #############################################################

def index():
    SQLFORM.grid = SolidGrid(renderstyle=True) # override the original grid function
    grid = SQLFORM.grid(table_product)
    return dict(buttons=grid.gridbuttons, 
                search=grid.search_form if hasattr(grid, 'search_form') else '',
                grid=grid)
    