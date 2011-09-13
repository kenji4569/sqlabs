# -*- coding: utf-8 -*-

from plugin_mptt import MPTTModel
import random
import unittest

db = DAL('sqlite:memory:')
mptt = MPTTModel(db)
mptt.define_tables()

def get_tree_details(nodes_id):
    
    

class TestMPTT(unittest.TestCase):

    def setUp(self):
        mptt.settings.table_tree.truncate()
#here for the initialization of Database

    def test_shuffle(self):
        db.tree.insert(title='Food', left=1, right=2)
        # make sure the shuffled sequence does not lose any elements
        random.shuffle(self.seq)
        self.seq.sort()
        self.assertEqual(self.seq, range(10))
        # should raise an exception for an immutable sequence
        self.assertRaises(TypeError, random.shuffle, (1,2,3))
    
    def test_shuffle2(self):
        # make sure the shuffled sequence does not lose any elements
        random.shuffle(self.seq)
        self.seq.sort()
        self.assertEqual(self.seq, range(9))
        # should raise an exception for an immutable sequence
        self.assertRaises(TypeError, random.shuffle, (1,2,3))
    
def run_test(TestCase):
    import cStringIO
    stream = cStringIO.StringIO()
    suite = unittest.TestLoader().loadTestsFromTestCase(TestCase)
    unittest.TextTestRunner(stream=stream, verbosity=2).run(suite)
    return stream.getvalue()

def index():
    return dict(output=CODE(run_test(TestSequenceFunctions)))

def test():
    mptt.add_node('Fruit', 'Food')
    mptt.add_node('Meat', 'Food')
    mptt.add_node('Red', 'Food')
    mptt.add_node('Rabbit', 'Meat')
    mptt.add_node('Pig', 'Meat')
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

