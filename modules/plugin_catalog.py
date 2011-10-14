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
                Field('name', requires=IS_NOT_EMPTY()),
                Field('available', 'boolean', default=False, 
                      widget=SQLFORM.widgets.boolean.widget), # not properly working without it? 
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
                Field('sku', requires=IS_NOT_EMPTY()),
                migrate=migrate, fake_migrate=fake_migrate,
                *_fields)
        
        if not settings.table_option_group_name in db.tables:
            settings.table_option_group = db.define_table(
                settings.table_option_group_name,
                Field('name', requires=IS_NOT_EMPTY()),
                migrate=migrate, fake_migrate=fake_migrate,
                *settings.extra_fields.get(settings.table_option_group_name, []))
        
        if not settings.table_option_name in db.tables:
            settings.table_option = db.define_table(
                settings.table_option_name,
                Field('option_group', 'reference %s' % settings.table_option_group_name,
                      readable=False, writable=False),
                Field('name', requires=IS_NOT_EMPTY()),
                migrate=migrate, fake_migrate=fake_migrate,
                *settings.extra_fields.get(settings.table_option_name, []))
                
    def add_product(self, vars, variant_vars_list):
        if not variant_vars_list:
            raise ValueError
        table_product = self.settings.table_product
        table_variant = self.settings.table_variant
        product_id = table_product.insert(**table_product._filter_fields(vars))
        for variant_vars in variant_vars_list:
            table_variant.insert(product=product_id, **table_variant._filter_fields(variant_vars))  
        return product_id
        
    def edit_product(self, product_id, vars, variant_vars_list):
        table_product = self.settings.table_product
        table_variant = self.settings.table_variant
        self.db(table_product.id==product_id).update(**table_product._filter_fields(vars))
        self.db(table_variant.product==product_id).delete()
        for variant_vars in variant_vars_list:
            table_variant.insert(product=product_id, **table_variant._filter_fields(variant_vars))  
        
    def remove_product(self, product_id):
        self.db(self.settings.table_variant.product==product_id).delete()
        return self.db(self.settings.table_product.id==product_id).delete()
        
    def get_product(self, product_id, load_variants=True, load_options=True, 
                    load_option_groups=True, *fields, **attributes):
        settings = self.settings
        product = self.db(settings.table_product.id==product_id).select(*fields, **attributes).first()
        if not product:
            return None
            
        if load_variants:
            if load_options:
                for option_no in range(1, settings.max_options + 1):
                    key = 'option_%s' % option_no 
                    alias = settings.table_option.with_alias(key)
                    left = alias.on(alias.id==settings.table_variant[key])
            else:
                left = None
            product.variants = self.variants_from_product(product_id).select(left=left)
            
            if load_option_groups:
                option_group_ids = []
                for i, variant in enumerate(product.variants):
                    variant.options = []
                    for option_no in range(1, settings.max_options + 1):
                        option = variant['option_%s' % option_no]
                        if not option:
                            break
                        variant.options.append(option)
                        if i == 0:
                            option_group_ids.append(option.option_group)
                    
                if option_group_ids:
                    product.option_groups = self.get_option_groups(option_group_ids)
                else:
                    product.option_groups = []
                
        return product
    
    def get_products_by_query(self, query, load_variants=True, load_options=True, 
                              load_option_groups=True, *fields, **attributes):
        db = self.db
        table_product = self.settings.table_product
        table_variant = self.settings.table_variant
        
        products = db(table_product.id>0).select(*fields, **attributes)
        if products:
            option_group_pools = {}
            from itertools import groupby
            variants = db(table_variant.product.belongs([r.id for r in products])
                          ).select(orderby=table_variant.product)
            _variants = {}
            for k, g in groupby(variants, key=lambda r: r.product):
                _variants[k] = list(g)
            for product in products:
                product.variants = _variants[product.id]
                # option_group_ids = []
                # for i, variant in enumerate(product.variants):
                    # variant.options = []
                    # for option_no in range(1, settings.max_options + 1):
                        # option = variant['option_%s' % option_no]
                        # if not option:
                            # break
                        # variant.options.append(option)
                        # if i == 0:
                            # option_group_ids.append(option.option_group)
        return products
        
    def variants_from_product(self, product_id):
        return self.db(self.settings.table_variant.product==product_id)
        
    def options_from_option_group(self, option_group_id):
        return self.db(self.settings.table_option.option_group==option_group_id)
        
    def get_option_groups(self, option_group_ids, *fields, **attributes):
        option_groups = self.db(self.settings.table_option_group.id.belongs(option_group_ids)
                               ).select(*fields, **attributes)
        option_groups = dict((r.id, r) for r in option_groups)
        return [option_groups[id] for id in option_group_ids]
        
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
    