 # -*- coding: utf-8 -*-
from plugin_paginator import Paginator, PagenateSelector, PagingInfo
from plugin_solidtable import SOLIDTABLE
from gluon.contrib.populate import populate

db = DAL('sqlite:memory:')
db.define_table('product', Field('name'))
populate(db.product, 99)

def index():
    query = db.product.id > 0
    
    pagenate_selector = PagenateSelector()
    paginator = Paginator(pagenate=pagenate_selector.pagenate, renderstyle=True) 
    paginator.records = db(query).count()
    paging_info = PagingInfo(paginator.page, paginator.pagenate, paginator.records)
    
    rows = db(query).select(limitby=paginator.limitby()) 
    table = SOLIDTABLE(rows, renderstyle=True)
    
    return dict(table=table, paginator=paginator, 
                pagenate_selector=pagenate_selector, paging_info=paging_info) 