# -*- coding: utf-8 -*-
from plugin_solidgrid import SolidGrid

### define tables ##############################################################
table_product = db.define_table('plugin_solidgrid_product', 
    Field('name', notnull=True),  
    Field('status', requires=IS_IN_SET(['new', 'old'])), 
    Field('description', 'text', represent=lambda v: v or '---'), 
    Field('publish_date', 'date', represent=lambda v: v or '---'), 
    Field('price', 'integer', represent=lambda v: '$%s' % v if v else '---' ), 
    Field('created_on', 'datetime', default=request.now, readable=False, writable=False),
)

### populate records ###########################################################

import datetime
if (db(table_product.created_on<request.now-datetime.timedelta(minutes=60)).count() or 
        not db(table_product.id>0).count()):
    table_product.truncate()
    for i in range(5):
        table_product.insert(name='p%s' % i, status='old')
    for i in range(5, 12):
        table_product.insert(name='p%s' % i, status='new')
    session.flash = 'the database has been refreshed'
    redirect(URL('index'))
    
### fake authentication ########################################################

from gluon.storage import Storage
session.auth = Storage(hmac_key='test')

### demo functions #############################################################

def index():
    SQLFORM.grid = SolidGrid(renderstyle=True) # override the original grid function
    
    from plugin_tablecheckbox import TableCheckbox
    tablecheckbox = TableCheckbox()
    
    # Insert an extra element to select an action
    tablecheckbox.components.insert(0, 
        SELECT('new', 'old', _name='action', _style='width:70px;',
                requires=IS_IN_SET(['new', 'old'])))
    if tablecheckbox.accepts(request.vars):
        db(table_product.id.belongs(tablecheckbox.vars.tablecheckbox)).update(status=tablecheckbox.vars.action)
        session.flash = 'Updated'
        redirect(URL('index'))
    extracolumns = [tablecheckbox.column()]
    
    grid = SQLFORM.grid(table_product, 
        #fields=[table_product.ALL],
        columns=[extracolumns[0], table_product.id, 
                 (table_product.name, table_product.status),
                  table_product.description,
                 (table_product.publish_date, table_product.price)],
        extracolumns=extracolumns,
        scope=table_product.status, 
        )
        
    return dict(buttons=grid.gridbuttons, 
                search=grid.search_form if hasattr(grid, 'search_form') else '',
                status=DIV(tablecheckbox) if hasattr(grid, 'records') else '',
                table=grid)
    