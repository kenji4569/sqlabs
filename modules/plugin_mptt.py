# -*- coding: utf-8 -*-
# This plugins is licensed under the MIT license: http://www.opensource.org/licenses/mit-license.php
# Authors: Yusuke Kishita <yuusuuke.kishiita@gmail.com>
# Authors: Kenji Hosoda <hosoda@s-cubism.jp>
# Original by: http://code.google.com/p/django-mptt/
from gluon import *
from gluon.storage import Storage

class MPTTModel(object):
    
    def __init__(self, db):
        self.db = db        
        
        settings = self.settings = Storage()
        settings.table_tree_name = 'tree'
        settings.table_tree = None
        
    def define_tables(self, migrate = True, fake_migrate = False):
        db, settings = self.db, self.settings
        
        settings.table_tree = db.define_table(
                                              settings.table_tree_name, 
                                              Field('title'), 
                                              Field('parent_id', 'integer'),
                                              Field('left', 'integer'), 
                                              Field('right', 'integer'),
                                              Field('level', 'integer'),
                                              Field('tree_id', 'integer'),
                                              Field('value', 'integer'), 
                                              migrate = migrate, 
                                              fake_migrate = fake_migrate)
        
    def get_raw_field_value(self, node_id, *fields):
        db, table_tree = self.db, self.settings.table_tree
        node = db(table_tree.id == node_id).select().first()
        if not node:
            raise ValueError
        return db(table_tree.id == node.id).select(*fields)
        
    def set_raw_field_value(self, node_id, value, *fields):
        db, table_tree = self.db, self.settings.table_tree
        node = db(table_tree.id == node_id).select().first()
        if not node:
            raise ValueError
        node.value = value
        return

    def get_ancestors(self, node_id, *fields):
        db, table_tree = self.db, self.settings.table_tree
        """print get_ancestors('3', table_tree.title)"""
        node = db(table_tree.id == node_id).select().first()
        if not node:
            raise ValueError
        return db(table_tree.left < node.left)(table_tree.right > node.right).select(orderby=table_tree.left, *fields)
    
    def get_descendants(self, node_id, *fields):
        db, table_tree = self.db, self.settings.table_tree
        """print get_descendants('2', table_tree.title)"""
        node = db(table_tree.id == node_id).select().first()
        if not node:
            raise ValueError
        return db(table_tree.left > node.left)(table_tree.right < node.right).select(orderby=table_tree.left, *fields)
    
    def get_descendant_count(self, node_id):
        db, table_tree = self.db, self.settings.table_tree
        node = db(table_tree.id == node_id).select().first()
        if not node:
            raise ValueError
        return (node.right - node.left - 1) / 2,   
    
    def get_leafnodes(self, *fields):
        db, table_tree = self.db, self.settings.table_tree
        return db(table_tree.right == table_tree.left+1).select(orderby=table_tree.left, *fields)
    
    def get_next_sibling(self, node_id, *fields):
        db, table_tree = self.db, self.settings.table_tree
        node = db(table_tree.id == node_id).select().first()
        if not node:
            raise ValueError
        return db(table_tree.left == node.right + 1).select(orderby=table_tree.title, *fields)
    
    def get_previous_sibling(self, node_id, *fields):
        db, table_tree = self.db, self.settings.table_tree
        node = db(table_tree.id == node_id).select().first()
        if not node:
            raise ValueError
        return db(table_tree.right == node.left - 1).select(orderby=table_tree.title, *fields)
    
    def get_root(self):
        db, table_tree = self.db, self.settings.table_tree
        root = db(table_tree.left == 1).select().first()
        if not root:
            raise ValueError
        return db(table_tree.left == 1).select()
    
    def is_child_node(self, node_id):
        db, table_tree = self.db, self.settings.table_tree
        node = db(table_tree.id == node_id).select().first()
        if not node:
            raise ValueError
        if db(table_tree.id == node_id)(table_tree.left > 1).select().first():
            return True
        else:
            return False
        
    def is_leaf_node(self, node_id):
        db, table_tree = self.db, self.settings.table_tree
        node = db(table_tree.id == node_id).select().first()
        if not node:
            raise ValueError
        if db(table_tree.id == node_id)(table_tree.right == table_tree.left+1).select().first():
            return True
        else:
            return False
        
    def is_root_node(self, node_id):
        db, table_tree = self.db, self.settings.table_tree
        node = db(table_tree.id == node_id).select().first()
        if not node:
            raise ValueError        
        if db(table_tree.id == node_id)(table_tree.left == 1).select().first():
            return True
        else:
            return False
        
    def is_ancestor_of(self, node1_id, node2_id):
        db, table_tree = self.db, self.settings.table_tree
        node1 = db(table_tree.id == node1_id).select().first()
        if not node1:
            raise ValueError
        node2 = db(table_tree.id == node2_id).select().first()
        if not node1:
            raise ValueError
        if (node1.left < node2.left) and (node1.right > node2.right): 
            return True
        else:
            return False
        
    def is_descendant_of(self, node1_id, node2_id):
        db, table_tree = self.db, self.settings.table_tree
        node1 = db(table_tree.id == node1_id).select().first()
        if not node1:
            raise ValueError
        node2 = db(table_tree.id == node2_id).select().first()
        if not node1:
            raise ValueError
        if (node1.left > node2.left) and (node1.right < node2.right): 
            return True
        else:
            return False
        
    def add_node(self, node_id, parent_node_id, node_level):
        db, table_tree = self.db, self.settings.table_tree
        parent = db(table_tree.id == parent_node_id).select().first()
        if not parent:
            raise ValueError
        db(table_tree.id == node_id).update(parent_id = parent_node_id)
        db(table_tree.id == node_id).update(level = node_level)
        db(table_tree.right >= parent.right).update(right=table_tree.right + 2)
        db(table_tree.left >= parent.right).update(left=table_tree.left + 2)
        table_tree.insert(id=node_id, left=parent.right, right=parent.right + 1)
    
    def delete_node(self, node_id):
        db, table_tree = self.db, self.settings.table_tree
        node = db(table_tree.id == node_id).select().first()
        if not node:
            raise ValueError
        db(table_tree.right >= node.right).update(right=table_tree.right - 2)
        db(table_tree.left >= node.right).update(left=table_tree.left - 2)
        db(table_tree.id == node_id).delete()
        
        

            
