# -*- coding: utf-8 -*-
from plugin_mptt import MPTT

db = DAL('sqlite:memory:')

def index():
    mptt = MPTT(db)
    mptt.define_tables()
    db.tree.insert(title='Food', left=1, right=2)
    mptt.test()
    return dict()
    

