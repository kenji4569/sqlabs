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
                Field('option_group', 'reference %s' % settings.table_option_group_name,
                      readable=False, writable=False),
                Field('name'),
                migrate=migrate, fake_migrate=fake_migrate,
                *settings.extra_fields.get(settings.table_option_name, []))
                
    def add_product(self, vars):
        table_product = self.settings.table_product
        table_variant = self.settings.table_variant
        product_id = table_product.insert(**table_product._filter_fields(vars))
        master_variant_id = table_variant.insert(product=product_id, 
                                                 **table_variant._filter_fields(vars))
        return product_id, master_variant_id
        
    def options_from_option_group(self, option_group_id):
        return self.db(self.settings.table_option.option_group==option_group_id)
    
    def get_option_sets(self, option_group_ids):
        options_list = [self.options_from_option_group(option_group_id).select()
                        for option_group_id in option_group_ids]
        if not options_list:
            return []
            
        def itertools_product(*args, **kwds): # for python < 2.6
            pools = map(tuple, args) * kwds.get('repeat', 1)
            result = [[]]
            for pool in pools:
                result = [x+[y] for x in result for y in pool]
            for prod in result:
                yield tuple(prod)
                
        return list(itertools_product(*options_list))
    # def variants(self, product_id):
        # pass
        
    # def is_master_variant(self, variant):
        # pass
        
    # def options(self, option_group_id):
        # pass
        
    # def product_option_info(self, product_id):
        # pass
    
    