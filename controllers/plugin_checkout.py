# -*- coding: utf-8 -*-
from plugin_checkout import Checkout
from plugin_catalog import Catalog
from gluon.tools import Auth
import unittest
from gluon.contrib.populate import populate

if request.function == 'test':
    db = DAL('sqlite:memory:')
    
### setup core objects #########################################################
auth = Auth(db)

checkout = Checkout(db)
checkout.settings.table_purchase_order_name = 'plugin_checkout_purchase_order'
checkout.settings.table_line_item = 'plugin_checkout_line_item'
checkout.settings.extra_fields = {
    'plugin_checkout_purchase_order': 
        [Field('billing_address', 'text'),
         Field('shipping_address', 'text'),
         Field('created_on', 'datetime', default=request.now)],
}

catalog = Catalog(db)
catalog.settings.table_product_name = 'plugin_checkout_product'
catalog.settings.table_variant_name = 'plugin_checkout_variant'
catalog.settings.table_option_group_name = 'plugin_checkout_option_group'
catalog.settings.table_option_name = 'plugin_checkout_option'

### define tables ##############################################################
auth.define_tables()
table_user = auth.settings.table_user

checkout.define_tables(str(table_user))
table_purchase_order = checkout.settings.table_purchase_order
table_line_item = checkout.settings.table_line_item

catalog.define_tables()
table_product = catalog.settings.table_product
table_variant = catalog.settings.table_variant
table_option_group = catalog.settings.table_option_group
table_option = catalog.settings.table_option

### populate records ###########################################################
num_users = 3
user_ids = {}
for user_no in range(1, num_users+1):   
    email = 'user%s@test.com' % user_no
    user = db(auth.settings.table_user.email==email).select().first()
    user_ids[user_no] = user and user.id or auth.settings.table_user.insert(email=email)
    
import datetime
if db(table_purchase_order.created_on<request.now-datetime.timedelta(minutes=60)).count():
    for table in (table_purchase_order, table_line_item, 
                  table_product, table_variant, table_option_group, table_option):
        table.truncate()
    session.flash = 'the database has been refreshed'
    redirect(URL('index'))
    
if not db(table_product.id>0).count():
    option_ids = {}
    id = table_option_group.insert(name='size')
    for option_name in ('small', 'large'):
        _option_id = table_option.insert(option_group=id, name=option_name)
        option_ids[option_name] = _option_id
            
    catalog.add_product(dict(name='product_1', available=True),
                        [dict(sku='product_1_master', price=100, quantity=10,
                              options=[])])
    catalog.add_product(dict(name='product_2', available=True),
                        [dict(sku='product_2_small', price=1000, quantity=3, 
                              options=[option_ids['small']]),
                         dict(sku='product_2_large', price=2000, quantity=1, 
                              options=[option_ids['large']])])
                  
### demo functions #############################################################
def index():
    user_no = int(request.args(0) or 1)
    user_id = user_ids[user_no]
    
    user_chooser = []
    for i in range(1, num_users+1):
        if i == user_no:
            user_chooser.append(SPAN('user%s' % user_no))
        else:
            user_chooser.append(A('user%s' % i, _href=URL('index', args=i)))
    user_chooser = DIV(XML(' '.join([r.xml() for r in user_chooser])), _style='font-weight:bold')
    
    if not request.args(0):
        response.flash = 'test'
        
        products = catalog.get_products_by_query(table_product.id>0)
        
        return dict(current_user=user_chooser,
                    products=products,
                    unit_tests=[A('basic test', _href=URL('test'))])
        
  
### unit tests #################################################################
class TestCheckout(unittest.TestCase):

    def setUp(self):
        table_product.truncate()
        
    def test_basic(self):
        # TODO
        raise NotImplementedError
        
def run_test(TestCase):
    import cStringIO
    stream = cStringIO.StringIO()
    suite = unittest.TestLoader().loadTestsFromTestCase(TestCase)
    unittest.TextTestRunner(stream=stream, verbosity=2).run(suite)
    return stream.getvalue()
    
def test():
    return dict(back=A('back', _href=URL('index')),
                output=CODE(run_test(TestCheckout)))
        