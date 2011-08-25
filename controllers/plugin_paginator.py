 # -*- coding: utf-8 -*-
from plugin_paginator import Paginator, PagenateSelector, PaginateInfo
from plugin_solidtable import SOLIDTABLE
from gluon.contrib.populate import populate

db = DAL('sqlite:memory:')
db.define_table('product', Field('name'))
populate(db.product, 99)

def index():
    query = db.product.id > 0
    
################################ The core ######################################
    pagenate_selector = PagenateSelector()
    paginator = Paginator(pagenate=pagenate_selector.pagenate, renderstyle=True) 
    paginator.records = db(query).count()
    paginate_info = PaginateInfo(paginator.page, paginator.pagenate, paginator.records)
    
    rows = db(query).select(limitby=paginator.limitby()) 
################################################################################

    table = SOLIDTABLE(rows, renderstyle=True)
    
    return dict(table=table, paginator=paginator, 
                pagenate_selector=pagenate_selector, paginate_info=paginate_info) 