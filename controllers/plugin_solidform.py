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
    request_fields = request.vars.fields or 'default'

################################ The core ######################################
    # Specify structured fields for the multi-line form layout.
    # A "None" indicates an empty line over which the precedent line spans
    if request_fields == 'default':
        fields = [['name', 'category'],
                  ['code', 'keywords'],
                  ['publish_start_date', None],
                  ['publish_end_date', None],
                  'url',
                  ['description', 'price'],
                  [None, 'point'],
                  'memo']
    elif request_fields == 'fields_2':
        fields = [['name', 'category'],
                  None,
                  ['code', 'keywords']]
    elif request_fields == 'fields_3':
        fields = [['name', 'category'],
                  [None, 'code'],
                  [None, 'keywords']]
    elif request_fields == 'fields_4':
        fields = [['id', 'name'],
                  ['category', 'code'],
                  [None, 'keywords']]
    elif request_fields == 'fields_5':
        fields = [['name', 'category'],
                  ['id', 'code'],
                  [None, 'keywords']]
    # Standard usage
    form = SOLIDFORM(db.product, fields=fields)
    # Factory usage
    form_factory = SOLIDFORM.factory([Field('xxx'), Field('yyy'), Field('zzz')], Field('aaa'))
    # Readonly usage
    product = db(db.product.id > 0).select().first()
    form_readonly = SOLIDFORM(db.product, product, fields=fields, showid=False, readonly=True)
    # edit form
    form_edit = SOLIDFORM(db.product, product, fields=fields)
################################################################################

    if form.accepts(request.vars, session):
        session.flash = 'submitted %s' % form.vars
        redirect(URL('index'))
    if form_factory.accepts(request.vars, session, formname='factory'):
        session.flash = 'submitted %s' % form_factory.vars
        redirect(URL('index'))
     
    style = STYLE("""input[type="text"], textarea {width:100%; max-height: 50px;}
                     .w2p_fw {padding-right: 20px; max-width:200px;}
                     .w2p_fl {background: #eee;}""")
    return dict(form=DIV(style, form),
                form__factory=form_factory, form__readonly=form_readonly, form__edit=form_edit,
                form_args=DIV(A('fields=default', _href=URL(vars={'fields': 'default'})), ' ',
                              A('fields=fields_2', _href=URL(vars={'fields': 'fields_2'})), ' ',
                              A('fields=fields_3', _href=URL(vars={'fields': 'fields_3'})), ' ',
                              A('fields=fields_4', _href=URL(vars={'fields': 'fields_4'})), ' ',
                              A('fields=fields_5', _href=URL(vars={'fields': 'fields_5'})), ' ',
                               ))
