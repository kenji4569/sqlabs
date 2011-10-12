# -*- coding: utf-8 -*-

from plugin_mptt import MPTTModel
import random
import unittest
import re

db = DAL('sqlite:memory:')
mptt = MPTTModel(db)
mptt.define_tables()
db, table_tree = mptt.db, mptt.settings.table_tree

def get_tree_details(nodes):
        return '\n'.join(["%s %s %s %s %s %s" % (node.id, node.parent_id, node.tree_id, node.level, node.left, node.right) for node in nodes])
    
leading_whitespace_re = re.compile(r'^\s+', re.MULTILINE)
    
def tree_details(text):
    return leading_whitespace_re.sub('',text) 
    
class TestMPTT(unittest.TestCase):

    def setUp(self):
        mptt.settings.table_tree.truncate()
        #here for the initialization of Database
        mptt.insert_node(node_id=1,target_id=None,position='last-child')
        mptt.insert_node(node_id=2,target_id=1,position='last-child')
        mptt.insert_node(node_id=3,target_id=2,position='last-child')
        mptt.insert_node(node_id=4,target_id=2,position='last-child')
        mptt.insert_node(node_id=5,target_id=2,position='last-child')
        mptt.insert_node(node_id=6,target_id=1,position='last-child')
        mptt.insert_node(node_id=7,target_id=6,position='last-child')
        mptt.insert_node(node_id=8,target_id=6,position='last-child')
        mptt.insert_node(node_id=9,target_id=None,position='last-child')
        mptt.insert_node(node_id=10,target_id=9,position='last-child')
        mptt.insert_node(node_id=11,target_id=9,position='last-child')

#    def test_shuffle(self):
#        # make sure the shuffled sequence does not lose any elements
#        random.shuffle(self.seq)
#        self.seq.sort()
#        self.assertEqual(self.seq, range(10))
#        # should raise an exception for an immutable sequence
#        self.assertRaises(TypeError, random.shuffle, (1,2,3))
#    
#    def test_shuffle2(self):
#        # make sure the shuffled sequence does not lose any elements
#        random.shuffle(self.seq)
#        self.seq.sort()
#        self.assertEqual(self.seq, range(9))
#        # should raise an exception for an immutable sequence
#        self.assertRaises(TypeError, random.shuffle, (1,2,3))

        # 1 - 1 0 1 16   action
        # 2 1 1 1 2 9    +-- platformer
        # 3 2 1 2 3 4    |   |-- platformer_2d
        # 4 2 1 2 5 6    |   |-- platformer_3d
        # 5 2 1 2 7 8    |   +-- platformer_4d
        # 6 1 1 1 10 15  +-- shmup
        # 7 6 1 2 11 12      |-- shmup_vertical
        # 8 6 1 2 13 14      +-- shmup_horizontal
        # 9 - 2 0 1 6    rpg
        # 10 9 2 1 2 3   |-- arpg
        # 11 9 2 1 4 5   +-- trpg
        
    def test_new_root_from_subtree(self):
        self.setUp()
        mptt._make_child_root_node(6)
        shmup = db(table_tree.id == 6).select()
        show_db_all = db().select(table_tree.ALL,orderby=table_tree.tree_id)
        
#        print 'test_new_root_from_subtree'
#        print get_tree_details(show_db_all)
        self.assertEqual(get_tree_details(shmup), '6 None 3 0 1 6')
        self.assertEqual(get_tree_details(show_db_all),
                         tree_details("""1 None 1 0 1 10
                                         2 1 1 1 2 9
                                         3 2 1 2 3 4
                                         4 2 1 2 5 6
                                         5 2 1 2 7 8
                                         9 None 2 0 1 6
                                         10 9 2 1 2 3
                                         11 9 2 1 4 5
                                         6 None 3 0 1 6
                                         7 6 3 1 2 3
                                         8 6 3 1 4 5"""))
        
    def test_new_root_from_leaf_with_siblings(self):
        self.setUp()
        mptt._make_child_root_node(3)
        platformer_2d = db(table_tree.id == 3).select()
        show_db_all = db().select(table_tree.ALL,orderby=table_tree.tree_id)
        
#        print 'test_new_root_from_leaf_with_sibling'
#        print get_tree_details(show_db_all)
        self.assertEqual(get_tree_details(platformer_2d), '3 None 3 0 1 2')
        self.assertEqual(get_tree_details(show_db_all),
                         tree_details("""1 None 1 0 1 14
                                         2 1 1 1 2 7
                                         4 2 1 2 3 4
                                         5 2 1 2 5 6
                                         6 1 1 1 8 13
                                         7 6 1 2 9 10
                                         8 6 1 2 11 12
                                         9 None 2 0 1 6
                                         10 9 2 1 2 3
                                         11 9 2 1 4 5
                                         3 None 3 0 1 2"""))
        
    def test_new_child_from_root_by_insert(self):
        self.setUp()
        mptt.insert_node(1, 9)
        action = db(table_tree.id == 1).select()
        rpg = db(table_tree.id == 9).select()
        show_db_all = db().select(table_tree.ALL,orderby=table_tree.tree_id)
        
#        print 'test_new_child_from_root_by_insert'
#        print get_tree_details(show_db_all)
        self.assertEqual(get_tree_details(action), '1 9 2 1 6 21')
        self.assertEqual(get_tree_details(show_db_all),
                         tree_details("""1 9 2 1 6 21
                                         2 1 2 2 7 14
                                         3 2 2 3 8 9
                                         4 2 2 3 10 11
                                         5 2 2 3 12 13
                                         6 1 2 2 15 20
                                         7 6 2 3 16 17
                                         8 6 2 3 18 19
                                         9 None 2 0 1 22
                                         10 9 2 1 2 3
                                         11 9 2 1 4 5"""))
        
    def test_new_child_from_root_by_move(self):
        self.setUp()
        mptt.move_node(1, 9)
        action = db(table_tree.id == 1).select()
        rpg = db(table_tree.id == 9).select()
        show_db_all = db().select(table_tree.ALL,orderby=table_tree.tree_id)
        
#        print 'test_new_child_from_root_by_move'
#        print get_tree_details(show_db_all)
        self.assertEqual(get_tree_details(action), '1 9 2 1 6 21')
        self.assertEqual(get_tree_details(show_db_all),
                         tree_details("""1 9 2 1 6 21
                                         2 1 2 2 7 14
                                         3 2 2 3 8 9
                                         4 2 2 3 10 11
                                         5 2 2 3 12 13
                                         6 1 2 2 15 20
                                         7 6 2 3 16 17
                                         8 6 2 3 18 19
                                         9 None 2 0 1 22
                                         10 9 2 1 2 3
                                         11 9 2 1 4 5"""))
        
    def test_move_leaf_to_other_tree(self):
        self.setUp()
        mptt.move_node(8, 9)
        shmup_horizontal = db(table_tree.id == 8).select()
        rpg = db(table_tree.id == 9).select()
        show_db_all = db().select(table_tree.ALL,orderby=table_tree.tree_id)
        
#        print 'test_move_leaf_to_other_tree'
#        print get_tree_details(show_db_all)
        self.assertEqual(get_tree_details(shmup_horizontal), '8 9 2 1 6 7')
        self.assertEqual(get_tree_details(show_db_all),
                         tree_details("""1 None 1 0 1 14
                                         2 1 1 1 2 9
                                         3 2 1 2 3 4
                                         4 2 1 2 5 6
                                         5 2 1 2 7 8
                                         6 1 1 1 10 13
                                         7 6 1 2 11 12
                                         8 9 2 1 6 7
                                         9 None 2 0 1 8
                                         10 9 2 1 2 3
                                         11 9 2 1 4 5"""))
        
    def test_move_subtree_to_other_tree(self):
        self.setUp()
        mptt.move_node(6, 11)
        shmup = db(table_tree.id == 6).select()
        trpg = db(table_tree.id == 11).select()
        show_db_all = db().select(table_tree.ALL,orderby=table_tree.tree_id)
        
#        print 'test_move_subtree_to_other_tree'
#        print get_tree_details(show_db_all)
        self.assertEqual(get_tree_details(shmup), '6 11 2 2 5 10')
        self.assertEqual(get_tree_details(show_db_all),
                         tree_details("""1 None 1 0 1 10
                                         2 1 1 1 2 9
                                         3 2 1 2 3 4
                                         4 2 1 2 5 6
                                         5 2 1 2 7 8
                                         6 11 2 2 5 10
                                         7 6 2 3 6 7
                                         8 6 2 3 8 9
                                         9 None 2 0 1 12
                                         10 9 2 1 2 3
                                         11 9 2 1 4 11"""))
        
    def test_move_subtree_down_level(self):
        self.setUp()
        mptt.move_node(8, 1)
        shmup = db(table_tree.id == 6).select()
        action = db(table_tree.id == 1).select()
        show_db_all = db().select(table_tree.ALL,orderby=table_tree.tree_id)
        
        print 'test_move_child_up_level'
        print get_tree_details(show_db_all)
        self.assertEqual(get_tree_details(shmup_horizontal), '8 1 1 1 14 15')
        self.assertEqual(get_tree_details(show_db_all),
                         tree_details("""1 None 1 0 1 16
                                         2 1 1 1 2 9
                                         3 2 1 2 3 4
                                         4 2 1 2 5 6
                                         5 2 1 2 7 8
                                         6 1 1 1 10 13
                                         7 6 1 2 11 12
                                         8 1 1 1 14 15
                                         9 None 2 0 1 6
                                         10 9 2 1 2 3
                                         11 9 2 1 4 5"""))
        
    def test_move_child_up_level(self):
        self.setUp()
        mptt.move_node(8, 1)
        shmup = db(table_tree.id == 6).select()
        platformer = db(table_tree.id == 2).select()
        show_db_all = db().select(table_tree.ALL,orderby=table_tree.tree_id)

    
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

