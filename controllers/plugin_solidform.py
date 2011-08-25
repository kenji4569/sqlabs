# -*- coding: utf-8 -*-
from plugin_solidform import SOLIDFORM
from gluon.contrib.populate import populate

db = DAL('sqlite:memory:')
db.define_table('product', 
    Field('name', requires=IS_NOT_EMPTY()), Field('category'), 
    Field('code', 'integer'), Field('keywords', 'text'), 
    Field('publish_start_date', 'date', label='start'), Field('publish_end_date', 'date', label='end'),
    Field('description', 'text'), Field('price', 'integer'), Field('point', 'integer'), 
    Field('url', requires=IS_URL()), Field('memo', 'text', comment='(memo)'))
populate(db.product, 1)

def index():
################################ The core ######################################
    # Specify structured fields for the multi-line form layout.
    # A "None" indicates an empty line over which the precedent line spans
    fields = [['name', 'category'], 
              ['code', 'keywords'], 
              ['publish_start_date', None], 
              ['publish_end_date', None], 
              'url',
              ['description', 'price'], 
              [None, 'point'], 
              'memo']
    # Standard usage
    form = SOLIDFORM(db.product, fields=fields)
    # Factory usage
    form_factory = SOLIDFORM.factory([Field('xxx'), Field('yyy'), Field('zzz')], Field('aaa'))
    # Readonly usage
    product = db(db.product.id>0).select().first()
    form_readonly = SOLIDFORM(db.product, product, fields=fields, showid=False, readonly=True)
################################################################################

    if form.accepts(request.vars, session):
        session.flash = 'submitted %s' % form.vars
        redirect(URL('index'))
     
    style = STYLE("""input[type="text"], textarea {width:100%; max-height: 50px;} 
                     .w2p_fw {padding-right: 20px; max-width:200px;}
                     .w2p_fl {background: #eee;}""")
    return dict(form=DIV(style, form), form_factory=form_factory, form_readonly=form_readonly)
