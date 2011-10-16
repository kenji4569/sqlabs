# -*- coding: utf-8 -*-
# This plugins is licensed under the MIT license: http://www.opensource.org/licenses/mit-license.php
# Authors: Kenji Hosoda <hosoda@s-cubism.jp>
from gluon import *
from gluon.storage import Storage, Messages

class _BulkLoader(object):
    def __init__(self):
        self.flattened = []
        self.sizes = []
    def register(self, values):
        self.flattened.extend(values)
        self.sizes.append(len(values))
    def load(self, fn):
        self.flattened = fn(self.flattened)
    def retrieve(self):
        size = self.sizes.pop(0)
        objects = self.flattened[:size]
        self.flattened = self.flattened[size:]
        return objects
        
class Catalog(object):
    
    def __init__(self, db):
        self.db = db
        
        settings = self.settings = Storage()
        
        settings.extra_fields = {}
        
        settings.table_product_name = 'catalog_product'
        settings.table_product = None
        
        settings.table_variant_name = 'catalog_variant'
        settings.table_variant = None
        
        settings.table_option_group_name = 'catalog_option_group'
        settings.table_option_group = None
        
        settings.table_option_name = 'catalog_option'
        settings.table_option = None
        
        messages = self.messages = Messages(current.T)
        messages.is_empty = 'Cannot be empty'
        self.messages.label_name = 'Name'
        self.messages.label_available = 'Available'
        self.messages.label_sku = 'SKU'
        
        self.init_record_pool()
        
    def init_record_pool(self):
        self._option_pool = {}
        self._option_group_pool = {}
        
    def define_tables(self, migrate=True, fake_migrate=False):
        db, settings = self.db, self.settings
        
        if not settings.table_product_name in db.tables:
            table = db.define_table(
                settings.table_product_name,
                Field('name', label=self.messages.label_name),
                Field('available', 'boolean', default=False, 
                      label=self.messages.label_available,
                      widget=SQLFORM.widgets.boolean.widget), # not properly working without it? 
                migrate=migrate, fake_migrate=fake_migrate,
                *settings.extra_fields.get(settings.table_product_name, []))
            table.name.requires = \
                IS_NOT_EMPTY(error_message=self.messages.is_empty)
        settings.table_product = db[settings.table_product_name]
                
        if not settings.table_variant_name in db.tables:
            table = db.define_table(
                settings.table_variant_name,
                Field('product', 'reference %s' % settings.table_product_name,
                      readable=False, writable=False),
                Field('sku', label=self.messages.label_sku),
                Field('options', 'list:reference %s' % settings.table_option_name,
                      readable=False, writable=False),
                Field('sort_order', 'integer'),
                migrate=migrate, fake_migrate=fake_migrate,
                *settings.extra_fields.get(settings.table_variant_name, []))
            table.sku.requires = \
                IS_NOT_EMPTY(error_message=self.messages.is_empty)
        settings.table_variant = db[settings.table_variant_name]
                
        if not settings.table_option_group_name in db.tables:
            table = db.define_table(
                settings.table_option_group_name,
                Field('name', label=self.messages.label_name),
                migrate=migrate, fake_migrate=fake_migrate,
                *settings.extra_fields.get(settings.table_option_group_name, []))
            table.name.requires = \
                IS_NOT_EMPTY(error_message=self.messages.is_empty)
        settings.table_option_group = db[settings.table_option_group_name]
        
        if not settings.table_option_name in db.tables:
            table = db.define_table(
                settings.table_option_name,
                Field('option_group', 'reference %s' % settings.table_option_group_name,
                      readable=False, writable=False),
                Field('name', label=self.messages.label_name),
                migrate=migrate, fake_migrate=fake_migrate,
                *settings.extra_fields.get(settings.table_option_name, []))
            table.name.requires = \
                IS_NOT_EMPTY(error_message=self.messages.is_empty)
        settings.table_option = db[settings.table_option_name]
                
    def add_product(self, product_vars, variant_vars_list):
        if not variant_vars_list:
            raise ValueError
        product_id = self.settings.table_product.insert(**product_vars)
        for variant_vars in variant_vars_list:
            self.settings.table_variant.insert(product=product_id, **variant_vars)  
        return product_id
        
    def edit_product(self, product_id, product_vars, variant_vars_list):
        self.db(self.settings.table_product.id==product_id).update(**product_vars)
        table_variant = self.settings.table_variant
        self.db(table_variant.product==product_id).delete()
        for variant_vars in variant_vars_list:
            table_variant.insert(product=product_id, **variant_vars)  
        
    def remove_product(self, product_id):
        self.db(self.settings.table_variant.product==product_id).delete()
        return self.db(self.settings.table_product.id==product_id).delete()
        
    def get_options(self, option_ids, *fields, **attributes):
        return self._get_records(self.settings.table_option, 
                                 option_ids, self._option_pool,
                                 *fields, **attributes)
                                 
    def get_option_groups(self, option_group_ids, *fields, **attributes):
        return self._get_records(self.settings.table_option_group, 
                                 option_group_ids, self._option_group_pool,
                                 *fields, **attributes)
        
    def _get_records(self, table, ids, pool, *fields, **attributes):
        if not ids:
            return []
        _ids = [e for e in ids if e not in pool]
        if _ids:
            records = self.db(table.id.belongs(set(_ids))).select(*fields, **attributes)
            pool.update(**dict([(r.id, r) for r in records]))
        return [pool[id] for id in ids]
    
    def get_product(self, product_id, load_variants=True, load_options=True, 
                    load_option_groups=True, 
                    variant_fields=[], variant_attributes={},
                    *fields, **attributes):
        settings = self.settings
        product = self.db(settings.table_product.id==product_id).select(*fields, **attributes).first()
        if not product:
            return None
            
        if load_variants:
            product.variants = self.variants_from_product(product_id
                    ).select(orderby=settings.table_variant.sort_order, 
                             *variant_fields, **variant_attributes)
            if load_options:
                for variant in product.variants:
                    variant.options = self.get_options(variant.options)
                product.option_groups = [option.option_group for option 
                        in product.variants and product.variants[0].options or []]
                if load_option_groups:       
                    product.option_groups = self.get_option_groups(product.option_groups)
            
        return product
        
    def get_products_by_query(self, query, load_variants=True, load_options=True, 
                              load_option_groups=True, 
                              variant_fields=[], variant_attributes={},
                              *fields, **attributes):
        db = self.db
        table_product = self.settings.table_product
        table_variant = self.settings.table_variant
        
        products = db(table_product.id>0).select(*fields, **attributes)
        
        if not products or not load_variants:
            return products
            
        from itertools import groupby
        variants = db(table_variant.product.belongs([r.id for r in products])
                      ).select(orderby=table_variant.product|table_variant.sort_order,
                               *variant_fields, **variant_attributes)
        _variants = {}
        for k, g in groupby(variants, key=lambda r: r.product):
            _variants[k] = list(g)
           
        for product in products:
            product.variants = _variants.get(product.id, [])
            
        if not load_options:
            return products
            
        bulk_loader = _BulkLoader()        
        for product in products:
            for variant in product.variants:
                bulk_loader.register(variant.options or [])
        bulk_loader.load(self.get_options)
        for product in products:
            for variant in product.variants:
                variant.options = bulk_loader.retrieve()
        
        if load_option_groups:        
            bulk_loader = _BulkLoader()
        for product in products:
            product.option_groups = [option.option_group for option 
                    in product.variants and product.variants[0].options or []]
            if load_option_groups:
                bulk_loader.register(product.option_groups)
        if load_option_groups:
            bulk_loader.load(self.get_option_groups)
            for product in products:
                product.option_groups = bulk_loader.retrieve()
                    
        return products
        
    def variants_from_product(self, product_id):
        return self.db(self.settings.table_variant.product==product_id)
        
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
    