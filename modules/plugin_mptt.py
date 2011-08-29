# -*- coding: utf-8 -*-
# This plugins is licensed under the MIT license: http://www.opensource.org/licenses/mit-license.php
# Authors: Kenji Hosoda <hosoda@s-cubism.jp>
from gluon import *
from gluon.storage import Storage

class MPTT(object):

    def __init__(self, db):
        self.db = db
        
        self.settings = Storage()
        self.settings.table_tree = None
        self.settings.table_tree_name = 'tree'
        
    def define_tables(self, migrate = True, fake_migrate = False):
        
        tree_name = self.settings.table_tree_name
        
        self.settings.table_tree = self.db.define_table(
                                                        tree_name, 
                                                        Field('title'), 
                                                        Field('left', 'integer'), 
                                                        Field('right', 'integer'), 
                                                        migrate = migrate, 
                                                        fake_migrate = fake_migrate)
        
        #self.settings.table_tree.tree.requires = (IS_NOT_EMPTY())
         
    def add_node(self, title, parent_title):
        db = self.db
        #table = table
        parent = db(db.tree.title == parent_title).select()[0]
        db(db.tree.right >= parent.right).update(right=db.tree.right + 2)
        db(db.tree.left >= parent.right).update(left=db.tree.left + 2)
        db.tree.insert(title=title, left=parent.right, right=parent.right + 1)
    
    def get_ancestors(self, title, *fields):
        db = self.db
        """print ancestors('Red', db.tree.title)"""
        node = db(db.tree.title == title).select()[0]
        return db(db.tree.left < node.left)(db.tree.right > node.right).select(orderby=db.tree.left, *fields)
    
    def get_descendants(self, title, *fields):
        db = self.db
        """print descendants('Fruit', db.tree.title)"""
        node = db(db.tree.title == title).select()[0]
        return db(db.tree.left > node.left)(db.tree.right < node.right).select(orderby=db.tree.left, *fields)
    
    def get_descendant_count(self, title):
        db = self.db
        node = db(db.tree.title == title).select()[0]
        return (node.right - node.left - 1) / 2   
    
    def get_leafnodes(self):
        db = self.db
        return db(db.tree.right == db.tree.left+1).select(orderby=db.tree.left)
    
    def get_root(self):
        db = self.db
        return db(db.tree.left == 1).select()
    
    def is_child(self, title):
        db = self.db
        if db(db.tree.title == title)(db.tree.left > 1).select().first():
            return True
        else:
            return False
        
    def is_root_node(self, title):
        db = self.db
        if db(db.tree.title == title)(db.tree.left == 1).select().first():
            return True
        else:
            return False
    
    def is_leaf_node(self, title):
        db = self.db
        if db(db.tree.title == title)(db.tree.right == db.tree.left+1).select().first():
            return True
        else:
            return False

    def remove_node(self, title):
        db = self.db
        tmp = db(db.tree.title == title).select().first()
            
    def test(self):
        db = self.db
        print db().select(db.tree.ALL)
        self.add_node('Fruit', 'Food')
        print db().select(db.tree.ALL)
        self.add_node('Meat', 'Food')
        print db().select(db.tree.ALL)
        self.add_node('Red', 'Food')
        print db().select(db.tree.ALL)
        self.add_node('Rabbit', 'Meat')
        print db().select(db.tree.ALL)

        print self.get_ancestors('Red', db.tree.title)
        print self.get_descendants('Food', db.tree.title)
        print self.get_descendant_count('Meat')
        print self.get_leafnodes()
        print self.get_root()
        print self.is_child('Food')
        print self.is_child('Rabbit')
        print self.is_root_node('Rabbit')
        print self.is_root_node('Food')
        print self.is_leaf_node('Rabbit')
        print self.is_leaf_node('Meat')
        
        print self.remove_node('Food')