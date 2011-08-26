# -*- coding: utf-8 -*-
from plugin_notemptymarker import mark_not_empty, unmark_not_empty

db = DAL('sqlite:memory:')
db.define_table('product', 
    Field('name', requires=IS_NOT_EMPTY()),
    Field('category', requires=IS_IN_SET(['A', 'B', 'C']), label='Genre'),
    Field('publish_start_date', 'date', requires=IS_DATE()),
    Field('publish_end_date', 'date', requires=IS_EMPTY_OR(IS_DATE())),
    Field('code', 'integer', requires=[IS_NOT_EMPTY(), IS_INT_IN_RANGE(1000)]),
    Field('description', 'text', requires=IS_LENGTH(100, 1)),
)

def index():
################################ The core ######################################
    # Modify the filed labels of the db.product attaching not-empty markers
    mark_not_empty(db.product)
    form_marked = SQLFORM(db.product, separator='')
    # Unmark the filed labels
    unmark_not_empty(db.product)
    form_unmarked = SQLFORM(db.product, separator='')
################################################################################

    if form_marked.accepts(request.vars, session):
        session.flash = 'submitted %s' % form_marked.vars
        redirect(URL('index'))
    if form_unmarked.accepts(request.vars, session, formname='unmarked'):
        session.flash = 'submitted %s' % form_unmarked.vars
        redirect(URL('index'))
    style = STYLE("""input[type="text"], select, textarea {width:100%; max-height: 50px;} 
                     .w2p_fw {padding-right: 20px; max-width:200px;}
                     .w2p_fl {background: #eee;}""")
    return dict(form_marked=DIV(style, form_marked), 
                form_unmarked=form_unmarked)
