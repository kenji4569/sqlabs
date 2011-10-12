# -*- coding: utf-8 -*-
# This plugins is licensed under the MIT license: http://www.opensource.org/licenses/mit-license.php
# Authors: Kenji Hosoda <hosoda@s-cubism.jp>
from gluon import *
from gluon.storage import Storage

class Catalog(object):
    
    def __init__(self, db):
        self.db = db
        
        settings = self.settings = Storage()
        
        settings.max_options = 2
        
        settings.extra_fields = {}
        
        settings.table_product_name = 'product'
        settings.table_product = None
        
        settings.table_variant_name = 'product_variant'
        settings.table_variant = None
        
        settings.table_option_group_name = 'product_option_group'
        settings.table_option_group = None
        
        settings.table_option_name = 'product_option'
        settings.table_option = None
        
    def define_tables(self, migrate=True, fake_migrate=False):
        db, settings = self.db, self.settings
        
        if not settings.table_product_name in db.tables:
            settings.table_product = db.define_table(
                settings.table_product_name,
                Field('name'),
                Field('available', 'boolean', default=False),
                migrate=migrate, fake_migrate=fake_migrate,
                *settings.extra_fields.get(settings.table_product_name, []))
                
        if not settings.table_variant_name in db.tables:
            _fields = []
            for option_no in range(1, max(settings.max_options+1, 2)):
                _fields.append(
                    Field('option_%s' % option_no, 'reference %s' % settings.table_option_name,
                          readable=False, writable=False))
            _fields.extend(settings.extra_fields.get(settings.table_variant_name, []))
            settings.table_variant = db.define_table(
                settings.table_variant_name,
                Field('product', 'reference %s' % settings.table_product_name,
                      readable=False, writable=False),
                Field('name'),
                migrate=migrate, fake_migrate=fake_migrate,
                *_fields)
        
        if not settings.table_option_group_name in db.tables:
            settings.table_option_group = db.define_table(
                settings.table_option_group_name,
                Field('name'),
                migrate=migrate, fake_migrate=fake_migrate,
                *settings.extra_fields.get(settings.table_option_group_name, []))
        
        if not settings.table_option_name in db.tables:
            settings.table_option = db.define_table(
                settings.table_option_name,
                Field('name'),
                migrate=migrate, fake_migrate=fake_migrate,
                *settings.extra_fields.get(settings.table_option_name, []))
                
    # def create_variants(self, product_id, options=None):
        # pass
        
    # def variants(self, product_id):
        # pass
        
    # def is_master_variant(self, variant):
        # pass
        
    # def options(self, option_group_id):
        # pass
        
    # def product_option_info(self, product_id):
        # pass
    
    