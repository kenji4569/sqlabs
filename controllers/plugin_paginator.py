 # -*- coding: utf-8 -*-
from plugin_paginator import Paginator, PerpageSelector, PagingInfo
from plugin_solidtable import SOLIDTABLE
from gluon.contrib.populate import populate

db = DAL('sqlite:memory:')
db.define_table('product', Field('name'))
populate(db.product, 99)

def index():
    query = db.product.id > 0
    
    perpage_selector = PerpageSelector()
    paginator = Paginator(perpage=perpage_selector.perpage, renderstyle=True) 
    paginator.records = db(query).count()
    paging_info = PagingInfo(paginator.page, paginator.perpage, paginator.records)
    
    rows = db(query).select(limitby=paginator.limitby()) 
    table = SOLIDTABLE(rows, renderstyle=True)
    
    return dict(table=table, paginator=paginator, 
                perpage_selector=perpage_selector, paging_info=paging_info) 