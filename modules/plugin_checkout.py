# -*- coding: utf-8 -*-
# This plugins is licensed under the MIT license: http://www.opensource.org/licenses/mit-license.php
# Authors: Kenji Hosoda <hosoda@s-cubism.jp>
from gluon import *
from gluon.storage import Storage, Messages

class Checkout(object):
    
    def __init__(self, db):
        self.db = db
        
        settings = self.settings = Storage()
        
        settings.extra_fields = {}
        
        settings.table_purchase_order_name = 'checkout_purchase_order'
        settings.table_purchase_order = None
        
        settings.table_line_item_name = 'checkout_line_item'
        settings.table_line_item = None
        
        settings.price_type = 'integer'
        
        messages = self.messages = Messages(current.T)
        
    def define_tables(self, table_user_name, migrate=True, fake_migrate=False):
        db, settings = self.db, self.settings
        
        if not settings.table_purchase_order_name in db.tables:
            table = db.define_table(
                settings.table_purchase_order_name,
                Field('user', 'integer'),
                Field('status', length=16), 
                migrate=migrate, fake_migrate=fake_migrate,
                *settings.extra_fields.get(settings.table_purchase_order_name, []))
        settings.table_purchase_order = db[settings.table_purchase_order_name]
            
        if not settings.table_line_item_name in db.tables:
            table = db.define_table(
                settings.table_line_item_name,
                Field('purchase_order', 'reference %s' % settings.table_purchase_order_name),
                Field('sku'),
                Field('quantity', 'integer'),
                Field('price', settings.price_type),
                Field('detail', 'text'),
                migrate=migrate, fake_migrate=fake_migrate,
                *settings.extra_fields.get(settings.table_line_item_name, []))
        settings.table_line_item = db[settings.table_line_item_name]
        
    def get_cart(self, user_id):
        #TODO
        pass
              
    def add_cart(self, user_id, sku, quantity, price, detail):
        # TODO
        pass
        
        
            