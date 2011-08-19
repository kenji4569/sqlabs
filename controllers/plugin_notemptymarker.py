# -*- coding: utf-8 -*-
from plugin_notemptymarker import mark_not_empty

db = DAL('sqlite:memory:')
db.define_table('product', 
    Field('name', requires=IS_NOT_EMPTY()),
    Field('category', requires=IS_IN_SET(['A', 'B', 'C']), label='Genre'),
    Field('publish_start_date', 'date', requires=IS_DATE()),
    Field('publish_end_date', 'date', requires=IS_EMPTY_OR(IS_DATE())),
    Field('code', 'integer', requires=[IS_NOT_EMPTY(), IS_INT_IN_RANGE(1000)]),
    Field('description', 'text'),
)

def index():
    mark_not_empty(db.product)
    
    form = SQLFORM(db.product, separator='')
    if form.accepts(request.vars, session):
        session.flash = 'submitted %s' % form.vars
        redirect(URL('index'))
    style = STYLE("""input[type="text"], select, textarea {width:100%; max-height: 50px;} 
                     .w2p_fw {padding-right: 20px; max-width:200px;}
                     .w2p_fl {background: #eee;}""")
    return dict(form=DIV(style, form))
