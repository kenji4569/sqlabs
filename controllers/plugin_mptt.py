# -*- coding: utf-8 -*-
#import unittest
from plugin_mptt import MPTTModel

db = DAL('sqlite:memory:')

def index():
    mptt = MPTTModel(db)
    mptt.define_tables()
    db.tree.insert(title='Food', left=1, right=2)
    return dict()

#class ReparentingTestCase(unittest.TestCase):
    
#    def test_new_root_from_subtree(self):
        

    
def test():
    mptt = MPTTModel(db)
    mptt.define_tables()
    db.tree.insert(title='Food', left=1, right=2)
    
    mptt.insert_node('Fruit', 'Food')
    mptt.insert_node('Meat', 'Food')
    mptt.insert_node('Red', 'Food')
    mptt.insert_node('Rabbit', 'Meat')
    mptt.insert_node('Pig', 'Meat')
    #mptt.delete_node('Pig')
    print db().select(db.tree.ALL)
    
    print mptt.get_ancestors(3, db.tree.title)
    print mptt.get_root()
        
    #print self.get_ancestors('Pig', db.tree.title)
    #print self.get_descendants('Fruit', db.tree.title)
    #print self.get_descendant_count('Food')
    #print mptt.get_leafnodes(db.tree.title)
    #print mptt.get_root()
    #print self.is_child('Food')
    #print self.is_child('Rabbit')
    #print self.is_root_node('Rabbit')
    #print self.is_root_node('Food')
    #print self.is_leaf_node('Rabbit')
    #print self.is_leaf_node('Meat')
    #print self.remove_node('Food')

    output = db().select(db.tree.ALL)
    return dict(output=output)

