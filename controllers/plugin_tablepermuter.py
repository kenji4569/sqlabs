# -*- coding: utf-8 -*-
from plugin_solidtable import SOLIDTABLE
from gluon.contrib.populate import populate

db = DAL('sqlite:memory:') 
db.define_table('product', Field('name'))
populate(db.product, 10)

def index():
    table = SOLIDTABLE(db(db.product.id>0).select(), renderstyle=True)
    return dict(table=table)