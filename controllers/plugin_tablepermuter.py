# -*- coding: utf-8 -*-
from plugin_tablepermuter import TablePermuter
from plugin_solidtable import SOLIDTABLE
from gluon.contrib.populate import populate

db = DAL('sqlite:memory:') 
db.define_table('product', Field('name'))
populate(db.product, 5)

def index():
    records = db(db.product.id>0).select()
    table = SOLIDTABLE(records, renderstyle=True, _id='solidtable')
    
################################ The core ######################################
    tablepermuter = TablePermuter(table.attributes['_id'], renderstyle=True)
    
    if tablepermuter.accepts(request.vars):
        # Permuted row indices will be submitted
        permuted_record_ids = [records[idx].id for idx in tablepermuter.vars.tablepermuter]
        session.flash = 'submitted : permuted_record_ids=%s' % permuted_record_ids
        redirect(URL('index'))
################################################################################
    
    return dict(table=table, tablepermuter=tablepermuter)