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
        
    def define_tables(self, migrate=True, fake_migrate=False):
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
        
    def get_cart(self):
        session = current.session
        line_items = session.checkout_line_items or {}
        total_price = session.checkout_total_price or 0
        return line_items, total_price
         
    def clear_cart(self):
        session = current.session
        self.update_cart({}, 0)
        
    def add_to_cart(self, item_id, price, quantity):
        item_id = int(item_id)
        session = current.session
        line_items, total_price = self.get_cart()
        
        total_price += quantity*price
        line_items[item_id] = line_items.get(item_id, 0) + quantity
        
        self.update_cart(line_items, total_price)
        
    def remove_from_cart(self, item_id, price):
        item_id = int(item_id)
        session = current.session
        line_items, total_price = self.get_cart()
        quantity = line_items.get(item_id, 0)
        
        total_price -= quantity*price
        if item_id in line_items:
            del line_items[item_id]
        if not line_items:
            total_price = 0
        
        self.update_cart(line_items, total_price)
        
    def update_cart(self, line_items, total_price):
        session = current.session
        session.checkout_line_items = line_items
        session.checkout_total_price = total_price    