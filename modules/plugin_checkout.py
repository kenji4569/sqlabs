# -*- coding: utf-8 -*-
# This plugins is licensed under the MIT license: http://www.opensource.org/licenses/mit-license.php
# Authors: Kenji Hosoda <hosoda@s-cubism.jp>
from gluon import *
from gluon.storage import Storage, Messages
from gluon.utils import web2py_uuid
    
class Checkout(object):
    
    def __init__(self, db):
        self.db = db
        
        settings = self.settings = Storage()
        
        settings.extra_fields = {}
        
        settings.table_purchase_order_name = 'checkout_purchase_order'
        settings.table_purchase_order = None
        
        settings.table_line_item_name = 'checkout_line_item'
        settings.table_line_item = None
        
        settings.table_shipping_address_name = 'checkout_shipping_address'
        settings.table_shipping_address = None
        
        settings.price_type = 'integer'
        
        messages = self.messages = Messages(current.T)
        
    def define_tables(self, basetable_address, migrate=True, fake_migrate=False):
        db, settings = self.db, self.settings
        
        if not settings.table_purchase_order_name in db.tables:
            table = db.define_table(
                settings.table_purchase_order_name,
                Field('uuid', length=256, unique=True, writable=False, readable=False), 
                Field('is_active', 'boolean', default=False, writable=False, readable=False),
                Field('purchased_on', 'datetime', writable=False, readable=True),
                Field('paid_on', 'datetime', writable=False, readable=True),
                Field('shipped_on', 'datetime', writable=False, readable=True),
                Field('status', length=16), 
                Field('customer', 'integer', writable=False),
                basetable_address,
                Field('deep_copy', 'text', writable=False),
                migrate=migrate, fake_migrate=fake_migrate,
                *settings.extra_fields.get(settings.table_purchase_order_name, []))
        settings.table_purchase_order = db[settings.table_purchase_order_name]
            
        if not settings.table_line_item_name in db.tables:
            table = db.define_table(
                settings.table_line_item_name,
                Field('purchase_order', 'reference %s' % settings.table_purchase_order_name,
                      writable=False, readable=False),
                Field('sku'),
                Field('price', 'integer'),
                Field('quantity', 'integer'),
                migrate=migrate, fake_migrate=fake_migrate,
                *settings.extra_fields.get(settings.table_line_item_name, []))
        settings.table_line_item = db[settings.table_line_item_name]
        
        if not settings.table_shipping_address_name in db.tables:
            table = db.define_table(
                settings.table_shipping_address_name,
                Field('purchase_order', 'reference %s' % self.settings.table_purchase_order_name,
                      readable=False, writable=False),
                basetable_address,
                migrate=migrate, fake_migrate=fake_migrate,
                *settings.extra_fields.get(settings.table_shipping_address_name, []))
        settings.table_shipping_address = db[settings.table_shipping_address_name]
        
    def get_hmac_key(self):
        return current.session.get('checkout_hmac_key')
        
    def get_cart(self):
        session = current.session
        
        line_items = session.checkout_line_items or []
        summary = session.checkout_summary or Storage(subtotal_price=0, total_quantity=0)
        
        # === type check for safe ===
        is_valid = True
        if type(line_items) != list:
            is_valid = False
        else:
            for line_item in line_items:
                if not isinstance(line_item, Storage):
                    is_valid = False
                    break
            else:
                if not isinstance(summary, Storage):
                    is_valid = False
        if not is_valid:
            self.clear_cart()
            
        return line_items, summary
         
    def clear_cart(self):
        session = current.session
        self.update_cart([])
        
    def add_to_cart(self, sku, price, quantity):
        session = current.session
        line_items, summary = self.get_cart()
        
        summary.subtotal_price += quantity * price
        for line_item in line_items:
            if line_item.sku == sku:
                if line_item.price != price:
                    raise ValueError
                line_item.quantity += quantity
                break
        else:
            line_items.append(Storage(
                id=line_items and (line_items[-1].id+1) or 0,
                sku=sku, price=price, quantity=quantity))
        
        self.update_cart(line_items)
        
    def remove_from_cart(self, *skus):
        session = current.session
        line_items, summary = self.get_cart()
        skus = [sku for sku in skus]
        line_items = [line_item for line_item in line_items if line_item.sku not in skus]
        self.update_cart(line_items)
        
    def change_hmac_key(self):
        current.session['checkout_hmac_key'] = web2py_uuid()
        
    def update_cart(self, line_items):
        session = current.session
        
        # Delete temporary purchase order (need it?)
        # _old_hmac_key = self.get_hmac_key()
        # if _old_hmac_key and db(table_purchase_order.uuid==_old_hmac_key).count():
            # db(table_purchase_order.uuid==_old_hmac_key).delete()
            
        self.change_hmac_key()
        session.checkout_line_items = line_items
        
        subtotal_price = 0
        total_quantity = 0
        for line_item in line_items:
            subtotal_price += line_item.price * line_item.quantity
            total_quantity += line_item.quantity
        
        session.checkout_summary = Storage(subtotal_price=subtotal_price,
                                           total_quantity=total_quantity)
                           
        
    def set_shipping_address_id(self, address_id):
        current.session.checkout_shipping_address_id = address_id
   
    def get_shipping_address_id(self):
        return current.session.checkout_shipping_address_id
       
    def set_payment_method_id(self, payment_method_id):
        current.session.checkout_payment_method_id = payment_method_id
    
    def get_payment_method_id(self):
        return current.session.checkout_payment_method_id
        
    def set_order_options(self, **order_options):
        current.session.checkout_order_options = Storage(order_options)
       
    def get_order_options(self):
        return current.session.checkout_order_options
        
    def clear_all(self):
        self.clear_cart()
        session = current.session
        session.checkout_shipping_address_id = None
        session.checkout_payment_method_id = None
        session.checkout_order_options = None
        
         