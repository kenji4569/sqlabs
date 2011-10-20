# -*- coding: utf-8 -*-

from plugin_mptt import MPTTModel
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
    
class ReparentingTestCase(unittest.TestCase):

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
        mptt._make_sibling_of_root_node(3,9,'right')
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
        
    def test_new_child_from_root(self):
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
        
    def test_move_child_up_level(self):
        self.setUp()
        mptt.move_node(8, 1)
        shmup_horizontal = db(table_tree.id == 8).select()
        action = db(table_tree.id == 1).select()
        show_db_all = db().select(table_tree.ALL,orderby=table_tree.tree_id)

#        print 'test_move_child_up_level'
#        print get_tree_details(show_db_all)
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

    def test_move_subtree_down_level(self):
        self.setUp()
        mptt.move_node(6, 2)
        shmup = db(table_tree.id == 6).select()
        platformer = db(table_tree.id == 2).select()
        show_db_all = db().select(table_tree.ALL,orderby=table_tree.tree_id)
        
#        print 'test_move_subtree_down_level'
#        print get_tree_details(show_db_all)
        self.assertEqual(get_tree_details(shmup), '6 2 1 2 9 14')
        self.assertEqual(get_tree_details(show_db_all),
                         tree_details("""1 None 1 0 1 16
                                         2 1 1 1 2 15
                                         3 2 1 2 3 4
                                         4 2 1 2 5 6
                                         5 2 1 2 7 8
                                         6 2 1 2 9 14
                                         7 6 1 3 10 11
                                         8 6 1 3 12 13
                                         9 None 2 0 1 6
                                         10 9 2 1 2 3
                                         11 9 2 1 4 5"""))
        
    def test_move_to(self):
        self.setUp()
        mptt.insert_node(9,1)
        rpg = db(table_tree.id == 9).select().first()
        action = db(table_tree.id == 1).select().first()
        show_db_all = db().select(table_tree.ALL,orderby=table_tree.tree_id)
        
        self.assertEqual(rpg.parent_id, action.id)

class DeletionTestCase(unittest.TestCase):

    def setUp(self):
        mptt.settings.table_tree.truncate()
        #here for the initialization of Database
        mptt.insert_node(node_id=1,target_id=None,position='last-child')
        mptt.insert_node(node_id=2,target_id=1,position='last-child')
        mptt.insert_node(node_id=3,target_id=2,position='last-child')
        mptt.insert_node(node_id=4,target_id=2,position='last-child')
        mptt.insert_node(node_id=5,target_id=1,position='last-child')
        mptt.insert_node(node_id=6,target_id=5,position='last-child')
        mptt.insert_node(node_id=7,target_id=5,position='last-child')
        mptt.insert_node(node_id=8,target_id=1,position='last-child')
        mptt.insert_node(node_id=9,target_id=8,position='last-child')
        mptt.insert_node(node_id=10,target_id=8,position='last-child')
        
        # 1 - 1 0 1 20    games
        # 2 1 1 1 2 7     +-- wii
        # 3 2 1 2 3 4     |   |-- wii_games
        # 4 2 1 2 5 6     |   +-- wii_hardware
        # 5 1 1 1 8 13    +-- xbox360
        # 6 5 1 2 9 10    |   |-- xbox360_games
        # 7 5 1 2 11 12   |   +-- xbox360_hardware
        # 8 1 1 1 14 19   +-- ps3
        # 9 8 1 2 15 16       |-- ps3_games
        # 10 8 1 2 17 18      +-- ps3_hardware
        
    def test_delete_root_node(self):
        self.setUp()
        mptt.insert_node(node_id=11,target_id=1,position='left')
        mptt.insert_node(node_id=12,target_id=1,position='right')
        show_db_all = db().select(table_tree.ALL,orderby=table_tree.tree_id)
        
        self.assertEqual(get_tree_details(show_db_all),
                         tree_details("""11 None 1 0 1 2
                                         1 None 2 0 1 20
                                         2 1 2 1 2 7
                                         3 2 2 2 3 4
                                         4 2 2 2 5 6
                                         5 1 2 1 8 13
                                         6 5 2 2 9 10
                                         7 5 2 2 11 12
                                         8 1 2 1 14 19
                                         9 8 2 2 15 16
                                         10 8 2 2 17 18
                                         12 None 3 0 1 2"""),
                         'Setup for test produced unexpected result')

        mptt.delete_node(1)
        show_db_all = db().select(table_tree.ALL,orderby=table_tree.tree_id)
        self.assertEqual(get_tree_details(show_db_all),
                         tree_details("""11 None 1 0 1 2
                                         12 None 3 0 1 2"""))
        
    def test_delete_last_node_with_sibling(self):
        self.setUp()
        mptt.delete_node(9)
        show_db_all = db().select(table_tree.ALL,orderby=table_tree.tree_id)
#        print 'test_delete_last_node_with_sibling'
#        print get_tree_details(show_db_all)

        self.assertEqual(get_tree_details(show_db_all),
                         tree_details("""1 None 1 0 1 18
                                         2 1 1 1 2 7
                                         3 2 1 2 3 4
                                         4 2 1 2 5 6
                                         5 1 1 1 8 13
                                         6 5 1 2 9 10
                                         7 5 1 2 11 12
                                         8 1 1 1 14 17
                                         10 8 1 2 15 16"""))
        
    def test_delete_last_node_with_descendants(self):
        self.setUp()
        mptt.delete_node(8)
        show_db_all = db().select(table_tree.ALL,orderby=table_tree.tree_id)
#       print 'test_delete_last_node_with_descendants'
#        print get_tree_details(show_db_all)
        
        self.assertEqual(get_tree_details(show_db_all),
                         tree_details("""1 None 1 0 1 14
                                         2 1 1 1 2 7
                                         3 2 1 2 3 4
                                         4 2 1 2 5 6
                                         5 1 1 1 8 13
                                         6 5 1 2 9 10
                                         7 5 1 2 11 12"""))
        
    def test_delete_node_with_siblings(self):
        self.setUp()
        mptt.delete_node(6)
        show_db_all = db().select(table_tree.ALL,orderby=table_tree.tree_id)
#        print 'test_delete_node_with_siblings'
#        print get_tree_details(show_db_all)
        
        self.assertEqual(get_tree_details(show_db_all),
                         tree_details("""1 None 1 0 1 18
                                         2 1 1 1 2 7
                                         3 2 1 2 3 4
                                         4 2 1 2 5 6
                                         5 1 1 1 8 11
                                         7 5 1 2 9 10
                                         8 1 1 1 12 17
                                         9 8 1 2 13 14
                                         10 8 1 2 15 16"""))

    def test_delete_node_with_descendants_and_siblings(self):
        self.setUp()
        mptt.delete_node(5)
        show_db_all = db().select(table_tree.ALL,orderby=table_tree.tree_id)
        
#        print 'test_delete_node_with_descendants_and_siblings'
#        print get_tree_details(show_db_all)
        self.assertEqual(get_tree_details(show_db_all),
                         tree_details("""1 None 1 0 1 14
                                         2 1 1 1 2 7
                                         3 2 1 2 3 4
                                         4 2 1 2 5 6
                                         8 1 1 1 8 13
                                         9 8 1 2 9 10
                                         10 8 1 2 11 12"""))
        
        
def run_test(TestCase):
    import cStringIO
    stream = cStringIO.StringIO()
    suite = unittest.TestLoader().loadTestsFromTestCase(TestCase)
    unittest.TextTestRunner(stream=stream, verbosity=2).run(suite)
    return stream.getvalue()

def index():
    
    return dict(test1=CODE(run_test(ReparentingTestCase)),test2=CODE(run_test(DeletionTestCase)))
