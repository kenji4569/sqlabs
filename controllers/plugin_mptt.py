# -*- coding: utf-8 -*-

from plugin_mptt import MPTTModel
import random
import unittest

db = DAL('sqlite:memory:')
mptt = MPTTModel(db)
mptt.define_tables()

class TestMPTT(unittest.TestCase):

    def setUp(self):
        mptt.settings.table_tree.truncate()
        #here for the initialization of Database

    def test_shuffle(self):
        mptt.insert(title='Food', left=1, right=2)
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
    return dict(output=CODE(run_test(TestMPTT)))

def test():
    db, table_tree = mptt.db, mptt.settings.table_tree
    #db.tree.insert(title='Food', left=1, right=2)
    mptt.add_node(node_id=1, parent_node_id=0, tree_id=1, node_level=0)
    mptt.add_node(node_id=2, parent_node_id=1, tree_id=1, node_level=1)
    mptt.add_node(node_id=3, parent_node_id=1, tree_id=1, node_level=1)
    mptt.add_node(node_id=4, parent_node_id=1, tree_id=1, node_level=1)
    mptt.add_node(node_id=5, parent_node_id=2, tree_id=1, node_level=2)
    #mptt.delete_node(2)
    print db().select(table_tree.ALL)
    
    print "get_ancestors:", mptt.get_ancestors(5, table_tree.id)
    print "get_leafnodes:", mptt.get_leafnodes(table_tree.id)
    print "get_next_sibling:", mptt.get_next_sibling(3,table_tree.id)
    print "get_previous_sibling:", mptt.get_previous_sibling(3,table_tree.id)
    print "get_root:", mptt.get_root()
    print "is_child_node:", mptt.is_child_node(2)
    print "is_leaf_node:", mptt.is_leaf_node(2)
    print "is_root_node:", mptt.is_root_node(2)
    print "is_ancestor_of:", mptt.is_ancestor_of(1,2)
    print "is_descendant_of:", mptt.is_descendant_of(1,2)
    
    output = db().select(table_tree.ALL)
    return dict(output=output)

