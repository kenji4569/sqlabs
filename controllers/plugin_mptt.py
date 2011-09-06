# -*- coding: utf-8 -*-
from plugin_mptt import MPTT

db = DAL('sqlite:memory:')

def index():
    mptt = MPTT(db)
    mptt.define_tables()
    db.tree.insert(title='Food', left=1, right=2)
    return dict()
    
def test():
    mptt = MPTT(db)
    mptt.define_tables()
    db.tree.insert(title='Food', left=1, right=2)
    
    mptt.add_node('Fruit', 'Food')
    mptt.add_node('Meat', 'Food')
    mptt.add_node('Red', 'Food')
    mptt.add_node('Rabbit', 'Meat')
    mptt.add_node('Pig', 'Meat')
    print db().select(db.tree.ALL)
        
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
