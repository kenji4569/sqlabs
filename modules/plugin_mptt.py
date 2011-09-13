# -*- coding: utf-8 -*-
# This plugins is licensed under the MIT license: http://www.opensource.org/licenses/mit-license.php
# Authors: Kenji Hosoda <hosoda@s-cubism.jp>
from gluon import *
from gluon.storage import Storage

class MPTTModelBase(type):
    """
    Metaclass for MPTT models
    """
    
    def __new__(self, class_name, bases, class_dict):
        """
        Create subclasses of MPTTModel. 
        """
        class_dict['_mptt_meta'] = MPTTOptions(class_dict.pop('MPTTMeta', None))
        cls = super(MPTTModelBase, self).__new__(self, class_name, bases, class_dict)
        
        return self.register(cls)
    
    @classmethod
    def register(self, cls, **kwargs):
        """
        For the weird cases when you need to add tree-ness to an *existing*
        class. For other cases you should subclass MPTTModel instead of calling this.
        """
        
        if not issubclass(cls, models.Model):
            raise ValueError, "register() expects a Django model class argument"
        
        if not hasattr(cls, '_mptt_meta'):
            cls._mptt_meta = MPTTOptions(**kwargs)
        
        abstract = getattr(cls._meta, 'abstract', False)
        
        try:
            MPTTModel
        except NameError:
            # We're defining the base class right now, so don't do anything
            # We only want to add this stuff to the subclasses.
            # (Otherwise if field names are customized, we'll end up adding two
            # copies)
            pass
        else:
            if not issubclass(cls, MPTTModel):
                bases = list(cls.__bases__)
                
                # strip out bases that are strict superclasses of MPTTModel.
                # (i.e. Model, object)
                # this helps linearize the type hierarchy if possible
                for i in range(len(bases)-1, -1, -1):
                    if issubclass(MPTTModel, bases[i]):
                        del bases[i]
                
                bases.insert(0, MPTTModel)
                cls.__bases__ = tuple(bases)
            
            for key in ('left_attr', 'right_attr', 'tree_id_attr', 'level_attr'):
                field_name = getattr(cls._mptt_meta, key)
                try:
                    cls._meta.get_field(field_name)
                except models.FieldDoesNotExist:
                    field = models.PositiveIntegerField(db_index=True, editable=False)
                    field.contribute_to_class(cls, field_name)
            
            # Add a tree manager, if there isn't one already
            if not abstract:
                tree_manager_attr = cls._mptt_meta.tree_manager_attr
                manager = getattr(cls, tree_manager_attr, None)
                if (not manager) or manager.model != cls:
                    if not manager:
                        manager = TreeManager()
                    else:
                        # manager.model might already be set if this is a proxy model
                        # (in that case, we need to create a new manager, or _base_manager will be wrong)
                        manager = manager.__class__()
                    manager.contribute_to_class(cls, tree_manager_attr)
                manager.init_from_model(cls)
                setattr(cls, '_tree_manager', manager)

        return cls
    
class MPTTModel(object):
    
    __metaclass__ = MPTTModelBase

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
                         
    def get_ancestors(self, node_id, *fields):
        db = self.db
        """print get_ancestors('3', db.tree.title)"""
        node = db(db.tree.id == node_id).select().first()
        if not node:
            raise ValueError
        return db(db.tree.left < node.left)(db.tree.right > node.right).select(orderby=db.tree.left, *fields)
    
    def get_descendants(self, node_id, *fields):
        db = self.db
        """print get_descendants('2', db.tree.title)"""
        node = db(db.tree.id == node_id).select().first()
        if not node:
            raise ValueError
        return db(db.tree.left > node.left)(db.tree.right < node.right).select(orderby=db.tree.left, *fields)
    
    def get_descendant_count(self, node_id):
        db = self.db
        node = db(db.tree.id == node_id).select().first()
        if not node:
            raise ValueError
        return (node.right - node.left - 1) / 2,   
    
    def get_leafnodes(self, *fields):
        db = self.db
        return db(db.tree.right == db.tree.left+1).select(orderby=db.tree.left, *fields)
    
    def get_next_sibling(self, node_id, *fields):
        db = self.db
        node = db(db.tree.id == node_id).select().first()
        if not node:
            raise ValueError
        return db(db.tree.left == node.right + 1).select(orderby=db.tree.title, *fields)
    
    def get_previous_sibling(self, node_id, *fields):
        db = self.db
        node = db(db.tree.id == node_id).select().first()
        if not node:
            raise ValueError
        return db(db.tree.right == node.left - 1).select(orderby=db.tree.title, *fields)
    
    def get_root(self):
        db = self.db
        root = db(db.tree.left == 1).select().first()
        if not root:
            raise ValueError
        return db(db.tree.left == 1).select()
    
    def is_child_node(self, node_id):
        db = self.db
        node = db(db.tree.id == node_id).select().first()
        if not node:
            raise ValueError
        if db(db.tree.id == node_id)(db.tree.left > 1).select().first():
            return True
        else:
            return False
        
    def is_leaf_node(self, node_id):
        db = self.db
        node = db(db.tree.id == node_id).select().first()
        if not node:
            raise ValueError
        if db(db.tree.id == node_id)(db.tree.right == db.tree.left+1).select().first():
            return True
        else:
            return False
        
    def is_root_node(self, node_id):
        db = self.db
        node = db(db.tree.id == node_id).select().first()
        if not node:
            raise ValueError        
        if db(db.tree.id == node_id)(db.tree.left == 1).select().first():
            return True
        else:
            return False
        
    def is_ancestor_of(self, node1_id, node2_id):
        db = self.db
        node1 = db(db.tree.id == node1_id).select().first()
        if not node1:
            raise ValueError
        node2 = db(db.tree.id == node2_id).select().first()
        if not node1:
            raise ValueError
        if (node1.left < node2.left) and (node1.right > node2.right): 
            return True
        else:
            return False
        
    def is_descendant_of(self, node1_id, node2_id):
        db = self.db
        node1 = db(db.tree.id == node1_id).select().first()
        if not node1:
            raise ValueError
        node2 = db(db.tree.id == node2_id).select().first()
        if not node1:
            raise ValueError
        if (node1.left > node2.left) and (node1.right < node2.right): 
            return True
        else:
            return False
        
    def insert_node(self, title, parent_title):
        db = self.db
        
        parent = db(db.tree.title == parent_title).select().first()
        if not parent:
            raise ValueError
        
        db(db.tree.right >= parent.right).update(right=db.tree.right + 2)
        db(db.tree.left >= parent.right).update(left=db.tree.left + 2)
        db.tree.insert(title=title, left=parent.right, right=parent.right + 1)
    
    def delete_node(self, title):
        db = self.db
        node = db(db.tree.title == title).select().first()
        if not node:
            raise ValueError
        
        node_id = node.id
        
        db(db.tree.right >= node.right).update(right=db.tree.right - 2)
        db(db.tree.left >= node.right).update(left=db.tree.left - 2)
        db(db.tree.id == node_id).delete()
        
        

            
