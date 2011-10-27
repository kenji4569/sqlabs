# -*- coding: utf-8 -*-
from plugin_mptt import MPTTModel
import unittest
import re
import datetime

if request.function == 'test':
    db = DAL('sqlite:memory:')

### setup core objects #########################################################
mptt = MPTTModel(db)
mptt.settings.table_node_name = 'plugin_mptt_node'
mptt.settings.extra_fields = {
    'plugin_mptt_node': 
        [Field('name'),
         Field('created_on', 'datetime', default=request.now)],
}

### define tables ##############################################################'
mptt.define_tables()
table_node = mptt.settings.table_node
NodeParent = table_node.with_alias('node_parent')
parent_left = NodeParent.on(NodeParent.id==table_node.parent)

### populate records ###########################################################
deleted = db(table_node.created_on<request.now-datetime.timedelta(minutes=30)).delete()
if deleted:
    table_node.truncate()
    session.flash = 'the database has been refreshed'
    redirect(URL('index'))

### demo functions #############################################################
def index():
    return dict(unit_tests=[A('test all', _href=URL('test')),
                            A('test reading', _href=URL('test', args='reading')),
                            A('test reparenting', _href=URL('test', args='reparenting')),
                            A('test deletion', _href=URL('test', args='deletion'))])

### unit tests #################################################################

class TreeTestMixin():
    leading_whitespace_re = re.compile(r'^\s+', re.MULTILINE)
    
    def asserTree(self, nodes, tree_text):
        self.assertEqual(
            '\n'.join(["%s %s %s %s %s %s" % 
                      (node.name, node.parent and node.parent.name, 
                       node.tree_id, node.level, node.left, node.right) 
                            for node in nodes]),
            self.leading_whitespace_re.sub('',tree_text))
            
    def get_all_nodes(self):
        return db(table_node.id > 0).select(left=parent_left, orderby=table_node.tree_id)
    
    def get_node(self, node_id):
        return db(table_node.id == node_id).select().first()
        
    def build_tree1(self):
        self.node1 = mptt.insert_node(None, name='node1')
        self.node2 = mptt.insert_node(self.node1, name='node2')
        self.node3 = mptt.insert_node(self.node2, name='node3')
        self.node4 = mptt.insert_node(self.node2, name='node4')
        self.node5 = mptt.insert_node(self.node2, name='node5')
        self.node6 = mptt.insert_node(self.node1, name='node6')
        self.node7 = mptt.insert_node(self.node6, name='node7')
        self.node8 = mptt.insert_node(self.node6, name='node8')
        self.node9 = mptt.insert_node(None, name='node9')
        self.node10 = mptt.insert_node(self.node9, name='node10')
        self.node11 = mptt.insert_node(self.node9, name='node11')
        
        # name, parent, tree_id, level, left, right,   structure
        # node1 -      1 0 1 16   node1
        # node2 node1  1 1 2 9    +-- node2
        # node3 node2  1 2 3 4    |   |-- node3
        # node4 node2  1 2 5 6    |   |-- node4
        # node5 node2  1 2 7 8    |   +-- node5
        # node6 node1  1 1 10 15  +-- node6
        # node7 node6  1 2 11 12      |-- node7
        # node8 node6  1 2 13 14      +-- node8
        # node9 -      2 0 1 6    node9
        # node10 node9 2 1 2 3    |-- node10
        # node11 node9 2 1 4 5    +-- node11
        
    def build_tree2(self):
        self.node1 = mptt.insert_node(None, name='node1')
        self.node2 = mptt.insert_node(self.node1, name='node2')
        self.node3 = mptt.insert_node(self.node2, name='node3')
        self.node4 = mptt.insert_node(self.node2, name='node4')
        self.node5 = mptt.insert_node(self.node1, name='node5')
        self.node6 = mptt.insert_node(self.node5, name='node6')
        self.node7 = mptt.insert_node(self.node5, name='node7')
        self.node8 = mptt.insert_node(self.node1, name='node8')
        self.node9 = mptt.insert_node(self.node8, name='node9')
        self.node10 = mptt.insert_node(self.node8, name='node10')
        
        # name, parent, tree_id, level, left, right,   structure
        # node1 -      1 0 1 20    node1
        # node2 node1  1 1 2 7     +-- node2
        # node3 node2  1 2 3 4     |   |-- node3
        # node4 node2  1 2 5 6     |   +-- node4
        # node5 node1  1 1 8 13    +-- node5
        # node6 node5  1 2 9 10    |   |-- node6
        # node7 node5  1 2 11 12   |   +-- node7
        # node8 node1  1 1 14 19   +-- node8
        # node9 node8  1 2 15 16       |-- node9
        # node10 node8 1 2 17 18       +-- node10
        
class ReadingTestCase(unittest.TestCase, TreeTestMixin):

    def setUp(self):
        mptt.settings.table_node.truncate()
        self.build_tree1()
        
    def test_ancestors_from_node(self):
        def _get_ancestors(node_id, include_self=False, ascending=False):
            return [node.name for node in 
                        mptt.ancestors_from_node(node_id, include_self
                             ).select(orderby=mptt.asc if ascending else mptt.desc)]
        self.assertEqual(_get_ancestors(self.node1), [])
        self.assertEqual(_get_ancestors(self.node2), ['node1'])
        self.assertEqual(_get_ancestors(self.node3), ['node1', 'node2'])
        self.assertEqual(_get_ancestors(self.node4), ['node1', 'node2'])
        self.assertEqual(_get_ancestors(self.node5), ['node1', 'node2'])
        self.assertEqual(_get_ancestors(self.node6), ['node1'])
        self.assertEqual(_get_ancestors(self.node7), ['node1', 'node6'])
        self.assertEqual(_get_ancestors(self.node9), [])
        self.assertEqual(_get_ancestors(self.node10), ['node9'])
        self.assertEqual(_get_ancestors(self.node11), ['node9'])
        
        self.assertEqual(_get_ancestors(self.node1, include_self=True), ['node1'])
        self.assertEqual(_get_ancestors(self.node2, include_self=True), ['node1', 'node2'])
        self.assertEqual(_get_ancestors(self.node3, include_self=True), ['node1', 'node2', 'node3'])
        self.assertEqual(_get_ancestors(self.node7, include_self=True), ['node1', 'node6', 'node7'])
        
        self.assertEqual(_get_ancestors(self.node3, ascending=True), ['node2', 'node1'])
        self.assertEqual(_get_ancestors(self.node3, ascending=True, include_self=True), ['node3', 'node2', 'node1'])
        
    def test_descendants_from_node(self):
        def _get_descendants(node_id, **kwds):
            return [node.name for node 
                    in mptt.descendants_from_node(node_id).select(orderby=table_node.left)]
        self.assertEqual(_get_descendants(self.node1), ['node2', 'node3', 'node4', 'node5', 'node6', 'node7', 'node8'])
        self.assertEqual(_get_descendants(self.node2), ['node3', 'node4', 'node5'])
        self.assertEqual(_get_descendants(self.node3), [])
        self.assertEqual(_get_descendants(self.node6), ['node7', 'node8'])
        
    def test_count_descendants_from_node(self):
        self.assertEqual(mptt.count_descendants_from_node(self.node1), 7)
        self.assertEqual(mptt.count_descendants_from_node(self.node2), 3)
        self.assertEqual(mptt.count_descendants_from_node(self.node3), 0)
        self.assertEqual(mptt.count_descendants_from_node(self.node4), 0)
        self.assertEqual(mptt.count_descendants_from_node(self.node5), 0)
        self.assertEqual(mptt.count_descendants_from_node(self.node6), 2)
        self.assertEqual(mptt.count_descendants_from_node(self.node7), 0)
        self.assertEqual(mptt.count_descendants_from_node(self.node8), 0)
        self.assertEqual(mptt.count_descendants_from_node(self.node9), 2)
        self.assertEqual(mptt.count_descendants_from_node(self.node10), 0)
    
    def test_leafnodes(self):
        self.assertEqual([node.name for node in mptt.leafnodes().select(orderby=table_node.tree_id|table_node.left)],
                         ['node3', 'node4', 'node5', 'node7', 'node8', 'node10', 'node11'])
    
    def test_roots(self):
        self.assertEqual([node.name for node in mptt.roots().select()],
                         ['node1', 'node9'])
      
    def test_is_root_node(self):
        # id
        self.assertTrue(mptt.is_root_node(self.node1))
        self.assertFalse(mptt.is_root_node(self.node2))
        # Row
        self.assertTrue(mptt.is_root_node(table_node[self.node1]))
        self.assertFalse(mptt.is_root_node(table_node[self.node2]))
                 
    # def test_is_child_node(self):
        # TODO
        # self.assertTrue(mptt.is_child_node(self.node1))
        # self.assertFalse(mptt.is_child_node(self.node2))
        
        
class ReparentingTestCase(unittest.TestCase, TreeTestMixin):

    def setUp(self):
        mptt.settings.table_node.truncate()
        self.build_tree1()
        
    def test_new_root_from_subtree(self):
        mptt._make_child_root_node(self.node6)
        self.asserTree([self.get_node(self.node6)], 'node6 None 3 0 1 6')
        self.asserTree(self.get_all_nodes(),
                      """node1 None 1 0 1 10
                         node2 node1 1 1 2 9
                         node3 node2 1 2 3 4
                         node4 node2 1 2 5 6
                         node5 node2 1 2 7 8
                         node9 None 2 0 1 6
                         node10 node9 2 1 2 3
                         node11 node9 2 1 4 5
                         node6 None 3 0 1 6
                         node7 node6 3 1 2 3
                         node8 node6 3 1 4 5""")
        
    def test_new_root_from_leaf_with_siblings(self):
        mptt._make_sibling_of_root_node(self.node3, self.node9, 'right')
        self.asserTree([self.get_node(self.node3)], 'node3 None 3 0 1 2')
        self.asserTree(self.get_all_nodes(),
                      """node1 None 1 0 1 14
                         node2 node1 1 1 2 7
                         node4 node2 1 2 3 4
                         node5 node2 1 2 5 6
                         node6 node1 1 1 8 13
                         node7 node6 1 2 9 10
                         node8 node6 1 2 11 12
                         node9 None 2 0 1 6
                         node10 node9 2 1 2 3
                         node11 node9 2 1 4 5
                         node3 None 3 0 1 2""")
        
    def test_new_child_from_root(self):
        mptt.move_node(self.node1, self.node9)
        self.asserTree([self.get_node(self.node1)], 'node1 node9 2 1 6 21')
        self.asserTree(self.get_all_nodes(),
                      """node1 node9 2 1 6 21
                         node2 node1 2 2 7 14
                         node3 node2 2 3 8 9
                         node4 node2 2 3 10 11
                         node5 node2 2 3 12 13
                         node6 node1 2 2 15 20
                         node7 node6 2 3 16 17
                         node8 node6 2 3 18 19
                         node9 None 2 0 1 22
                         node10 node9 2 1 2 3
                         node11 node9 2 1 4 5""")
        
    def test_move_leaf_to_other_tree(self):
        mptt.move_node(self.node8, self.node9)
        self.asserTree([self.get_node(self.node8)], 'node8 node9 2 1 6 7')
        self.asserTree(self.get_all_nodes(),
                      """node1 None 1 0 1 14
                         node2 node1 1 1 2 9
                         node3 node2 1 2 3 4
                         node4 node2 1 2 5 6
                         node5 node2 1 2 7 8
                         node6 node1 1 1 10 13
                         node7 node6 1 2 11 12
                         node8 node9 2 1 6 7
                         node9 None 2 0 1 8
                         node10 node9 2 1 2 3
                         node11 node9 2 1 4 5""")
        
    def test_move_subtree_to_other_tree(self):
        mptt.move_node(self.node6, self.node11)
        self.asserTree([self.get_node(self.node6)], 'node6 node11 2 2 5 10')
        self.asserTree(self.get_all_nodes(),
                      """node1 None 1 0 1 10
                         node2 node1 1 1 2 9
                         node3 node2 1 2 3 4
                         node4 node2 1 2 5 6
                         node5 node2 1 2 7 8
                         node6 node11 2 2 5 10
                         node7 node6 2 3 6 7
                         node8 node6 2 3 8 9
                         node9 None 2 0 1 12
                         node10 node9 2 1 2 3
                         node11 node9 2 1 4 11""")
        
    def test_move_child_up_level(self):
        mptt.move_node(self.node8, self.node1)
        self.asserTree([self.get_node(self.node8)], 'node8 node1 1 1 14 15')
        self.asserTree(self.get_all_nodes(),
                      """node1 None 1 0 1 16
                         node2 node1 1 1 2 9
                         node3 node2 1 2 3 4
                         node4 node2 1 2 5 6
                         node5 node2 1 2 7 8
                         node6 node1 1 1 10 13
                         node7 node6 1 2 11 12
                         node8 node1 1 1 14 15
                         node9 None 2 0 1 6
                         node10 node9 2 1 2 3
                         node11 node9 2 1 4 5""")

    def test_move_subtree_down_level(self):
        mptt.move_node(self.node6, self.node2)
        self.asserTree([self.get_node(self.node6)], 'node6 node2 1 2 9 14')
        self.asserTree(self.get_all_nodes(),
                      """node1 None 1 0 1 16
                         node2 node1 1 1 2 15
                         node3 node2 1 2 3 4
                         node4 node2 1 2 5 6
                         node5 node2 1 2 7 8
                         node6 node2 1 2 9 14
                         node7 node6 1 3 10 11
                         node8 node6 1 3 12 13
                         node9 None 2 0 1 6
                         node10 node9 2 1 2 3
                         node11 node9 2 1 4 5""")
        
    def test_move_to(self):
        mptt.move_node(self.node9, self.node1)
        self.assertEqual(self.get_node(self.node9).parent, self.get_node(self.node1).id)

class DeletionTestCase(unittest.TestCase, TreeTestMixin):

    def setUp(self):
        mptt.settings.table_node.truncate()
        self.build_tree2()
        
    def test_delete_root_node(self):
        mptt.insert_node(self.node1, position='left', name='node11')
        mptt.insert_node(self.node1, position='right', name='node12')
        self.asserTree(self.get_all_nodes(),
                      """node11 None 1 0 1 2
                         node1 None 2 0 1 20
                         node2 node1 2 1 2 7
                         node3 node2 2 2 3 4
                         node4 node2 2 2 5 6
                         node5 node1 2 1 8 13
                         node6 node5 2 2 9 10
                         node7 node5 2 2 11 12
                         node8 node1 2 1 14 19
                         node9 node8 2 2 15 16
                         node10 node8 2 2 17 18
                         node12 None 3 0 1 2""")

        mptt.delete_node(self.node1)
        self.asserTree(self.get_all_nodes(),
                      """node11 None 1 0 1 2
                         node12 None 3 0 1 2""")
        
    def test_delete_last_node_with_sibling(self):
        mptt.delete_node(self.node9)
        self.asserTree(self.get_all_nodes(),
                      """node1 None 1 0 1 18
                         node2 node1 1 1 2 7
                         node3 node2 1 2 3 4
                         node4 node2 1 2 5 6
                         node5 node1 1 1 8 13
                         node6 node5 1 2 9 10
                         node7 node5 1 2 11 12
                         node8 node1 1 1 14 17
                         node10 node8 1 2 15 16""")
        
    def test_delete_last_node_with_descendants(self):
        mptt.delete_node(self.node8)
        self.asserTree(self.get_all_nodes(),
                      """node1 None 1 0 1 14
                         node2 node1 1 1 2 7
                         node3 node2 1 2 3 4
                         node4 node2 1 2 5 6
                         node5 node1 1 1 8 13
                         node6 node5 1 2 9 10
                         node7 node5 1 2 11 12""")
        
    def test_delete_node_with_siblings(self):
        mptt.delete_node(self.node6)
        self.asserTree(self.get_all_nodes(),
                      """node1 None 1 0 1 18
                         node2 node1 1 1 2 7
                         node3 node2 1 2 3 4
                         node4 node2 1 2 5 6
                         node5 node1 1 1 8 11
                         node7 node5 1 2 9 10
                         node8 node1 1 1 12 17
                         node9 node8 1 2 13 14
                         node10 node8 1 2 15 16""")

    def test_delete_node_with_descendants_and_siblings(self):
        mptt.delete_node(self.node5)
        self.asserTree(self.get_all_nodes(),
                      """node1 None 1 0 1 14
                         node2 node1 1 1 2 7
                         node3 node2 1 2 3 4
                         node4 node2 1 2 5 6
                         node8 node1 1 1 8 13
                         node9 node8 1 2 9 10
                         node10 node8 1 2 11 12""")
        
def run_test(TestCase):
    import cStringIO
    stream = cStringIO.StringIO()
    suite = unittest.TestLoader().loadTestsFromTestCase(TestCase)
    unittest.TextTestRunner(stream=stream, verbosity=2).run(suite)
    return stream.getvalue()
    
def test():
    test_case_classes = []
    if request.args(0) in ('reading', None):
        test_case_classes.append(ReadingTestCase)
    if request.args(0) in ('reparenting', None):
        test_case_classes.append(ReparentingTestCase)
    if request.args(0) in ('deletion', None):
        test_case_classes.append(DeletionTestCase)
        
    return dict(back=A('back', _href=URL('index')),
                output=CODE(*[run_test(t) for t in test_case_classes]))
              