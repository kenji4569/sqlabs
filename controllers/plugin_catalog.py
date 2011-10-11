# -*- coding: utf-8 -*-
from plugin_catalog import Catalog
from gluon.tools import Auth
import unittest
from gluon.contrib.populate import populate

if request.function == 'test':
    db = DAL('sqlite:memory:')
    
### setup core objects #########################################################
auth = Auth(db)
catalog = catalog(db)
catalog.settings.table_product_name = 'plugin_catalog_product'
catalog.settings.table_product_variant_name = 'plugin_catalog_product_variant'
catalog.settings.table_product_variant_group_name = 'plugin_catalog_product_variant_group'
catalog.settings.extra_fields = {
    'plugin_catalog_product': [
        # Field('status'),
        Field('long_description', 'text'),
        # Field('short_description', 'text'),
        # Field('large_image', 'upload'),
        # Field('small_image', 'upload'),
        # Field('manufacturer'),
        # Field('brand'),
        # Field('reward_point_rate'),
        Field('created_on', 'datetime', default=request.now)
    ],
    'plugin_catalog_product_variant': [
        Field('sku'),
        # Field('retail_price', 'decimal'),
        Field('sale_price', 'decimal'),
        Field('inventory_quantity', 'integer'),
        # Field('inventory_level', 'integer'),
        # Field('shipping_cost', 'integer'),
        # Field('taxable', 'boolean'),
    ],
    # 'plugin_catalog_product_option': [
        # Field('price_charge'),],
}

### define tables ##############################################################
catalog.define_tables()
table_product = catalog.settings.table_product
table_product_variant = catalog.settings.table_product_variant
table_product_variant_group = catalog.settings.table_product_variant_group

### populate records ###########################################################
import datetime
deleted = db(table_product.created_on<request.now-datetime.timedelta(minutes=30)).delete()
if deleted:
    session.flash = 'the database has been refreshed'
    redirect(URL('index'))
    

### demo functions #############################################################
def index():
    unit_tests = [A('product test', _href=URL('test', args='product'))]
    
    if not request.args(0):
        response.flash = 'test'
        return dict(unit_tests=unit_tests)
    else:
        return dict(unit_tests=unit_tests)
        
  
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
        