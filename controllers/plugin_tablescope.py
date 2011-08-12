# -*- coding: utf-8 -*-
from plugin_tablescope import TableScope
from plugin_solidtable import SOLIDTABLE
from gluon.contrib.populate import populate

db = DAL('sqlite:memory:') 
db.define_table('product', 
    Field('status', requires=IS_IN_SET([(1, 'Reserve'), (2, 'Available'), (3, ' Terminate')])))
_status_options = dict(db.product.status.requires.options())
db.product.status.represent = lambda v: _status_options[v]
db.product.bulk_insert([{'status':1}, {'status':1}, {'status':1}, {'status':2}, 
                         {'status':2}, {'status':3}])

def index():
    dataset = db(db.product.id>0)
    
    scope_1 = TableScope(dataset, db.product.status, renderstyle=True)
    table_1 = SOLIDTABLE(scope_1.scoped_dataset.select(), renderstyle=True)
    
    scope_2 = TableScope(dataset, db.product.status, all=False, default=2, 
                         scope_var='scope_2', renderstyle=True)
    table_2 = SOLIDTABLE(scope_2.scoped_dataset.select(), renderstyle=True)
    
    return dict(sample_1=dict(table=table_1, scope=scope_1),
                sample_2=dict(table=table_2, scope=scope_2))