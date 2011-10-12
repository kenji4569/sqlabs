# -*- coding: utf-8 -*-
from plugin_catalog import Catalog
from gluon.tools import Auth
import unittest
from gluon.contrib.populate import populate
from plugin_solidtable import SOLIDTABLE

if request.function == 'test':
    db = DAL('sqlite:memory:')
    
### setup core objects #########################################################
auth = Auth(db)
catalog = Catalog(db)
catalog.settings.table_product_name = 'plugin_catalog_product'
catalog.settings.table_variant_name = 'plugin_catalog_product_variant'
catalog.settings.table_option_group_name = 'plugin_catalog_product_option_group'
catalog.settings.table_option_name = 'plugin_catalog_product_option'
catalog.settings.extra_fields = {
    'plugin_catalog_product': [
        Field('long_description', 'text'),
        Field('created_on', 'datetime', default=request.now,
              readable=False, writable=False),
        # --- Other possible fields ---
        # Field('status'),
        # Field('short_description', 'text'),
        # Field('large_image', 'upload'),
        # Field('small_image', 'upload'),
        # Field('manufacturer'),
        # Field('brand'),
        # Field('reward_point_rate'),
    ],
    'plugin_catalog_product_variant': [
        Field('sku'),
        Field('retail_price', 'integer'),
        Field('sale_price', 'integer'),
        Field('inventory_quantity', 'integer'),
        # --- Other possible fields ---
        # Field('inventory_level', 'integer'),
        # Field('weight', 'integer'),
        # Field('taxable', 'boolean'),
    ],
    # 'plugin_catalog_product_option': [
        # Field('price_charge'),],
}

### define tables ##############################################################
catalog.define_tables()
table_product = catalog.settings.table_product
table_variant = catalog.settings.table_variant
table_option_group = catalog.settings.table_option_group
table_option = catalog.settings.table_option

### populate records ###########################################################
import datetime
deleted = db(table_product.created_on<request.now-datetime.timedelta(minutes=30)).delete()
if deleted:
    session.flash = 'the database has been refreshed'
    redirect(URL('index'))

### demo functions #############################################################
def index():
    unit_tests = [A('basic test', _href=URL('test'))]
    
    if not request.args(0):
        form = SQLFORM.factory(table_product, table_variant)
        if form.process().accepted:
            id = table_product.insert(**table_product._filter_fields(form.vars))
            form.vars.product = id
            id = table_variant.insert(**table_variant._filter_fields(form.vars))
            session.flash = T('Record Created')
            redirect(URL('index'))
        
        extracolumns = [{'label':'Options',
                         'content':lambda row, rc: A('Options',
                            _href=URL('index', args=['options', row.id]))},     
                    ]
        products = SOLIDTABLE(db(table_product.id>0).select(), 
                              headers='labels', extracolumns=extracolumns)
        return dict(product_form=form, 
                    products=products,
                    unit_tests=unit_tests)
    elif request.args(0) == 'options':
        return dict(back=A('back', _href=URL('index')))
        
  
### unit tests #################################################################
class TestCatalog(unittest.TestCase):

    def setUp(self):
        table_product.truncate()
        
    def test_basic(self):
        pass
        
def run_test(TestCase):
    import cStringIO
    stream = cStringIO.StringIO()
    suite = unittest.TestLoader().loadTestsFromTestCase(TestCase)
    unittest.TextTestRunner(stream=stream, verbosity=2).run(suite)
    return stream.getvalue()
    
def test():
    return dict(back=A('back', _href=URL('index')),
                output=CODE(run_test(TestCatalog)))
        