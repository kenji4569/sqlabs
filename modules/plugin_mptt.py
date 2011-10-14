# -*- coding: utf-8 -*-
# This plugins is licensed under the MIT license: http://www.opensource.org/licenses/mit-license.php
# Authors: Yusuke Kishita <yuusuuke.kishiita@gmail.com>
# Authors: Kenji Hosoda <hosoda@s-cubism.jp>
# Original by: http://code.google.com/p/django-mptt/

from gluon import *
from gluon.storage import Storage
from email._parseaddr import SPACE

class MPTTModel(object):
    
    def __init__(self, db):
        self.db = db        
        
        settings = self.settings = Storage()
        settings.table_tree_name = 'node'
        settings.table_tree = None
        
    def define_tables(self, migrate = True, fake_migrate = False):
        db, settings = self.db, self.settings
        
        settings.table_tree = db.define_table(
                                              settings.table_tree_name, 
                                              Field('title'),
                                              Field('parent_id', 'integer'),
                                              Field('tree_id', 'integer'),
                                              Field('level', 'integer'), 
                                              Field('left', 'integer'), 
                                              Field('right', 'integer'),
                                              #Field('value', 'integer'), 
                                              migrate = migrate, 
                                              fake_migrate = fake_migrate)
        
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
        return (node.right - node.left - 1) / 2   
    
    def get_leafnodes(self, *fields):
        db, table_tree = self.db, self.settings.table_tree
        return db(table_tree.right == table_tree.left+1).select(orderby=table_tree.left, *fields)
    
    def get_next_sibling(self, node_id):
        db, table_tree = self.db, self.settings.table_tree
        node = db(table_tree.id == node_id).select().first()
        if not node:
            raise ValueError
        if self.is_root_node(node_id):
            next_sib = db(table_tree.left == 1)(table_tree.tree_id == node.tree_id + 1).select()
        else:
            next_sib = db(table_tree.left == node.right + 1)(table_tree.tree_id == node.tree_id).select()
        return next_sib.id
    
    def get_previous_sibling(self, node_id):
        db, table_tree = self.db, self.settings.table_tree
        node = db(table_tree.id == node_id).select().first()
        if not node:
            raise ValueError
        if self.is_root_node(node_id):
            previous_sib = db(table_tree.left == 1)(table_tree.tree_id == node.tree_id - 1).select()
        else:
            previous_sib = db(table_tree.right == node.left - 1)(table_tree.tree_id == node.tree_id).select()
        return previous_sib.id
    
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
        
    def add_node(self, node_id, target_id, position='last-child'):
        db, table_tree = self.db, self.settings.table_tree
        target = db(table_tree.id == target_id).select().first()
        if not target:
            raise ValueError
        self._update_tree(node_id, target_id, position)
        return
        
    def _update_tree(self, node_id, target_id, position):
        db, table_tree = self.db, self.settings.table_tree
        target = db(table_tree.id == target_id).select().first()
        if position == 'last-child':
            db(table_tree.right >= target.right)(table_tree.tree_id == target.tree_id).update(right=table_tree.right + 2)
            db(table_tree.left >= target.right)(table_tree.tree_id == target.tree_id).update(left=table_tree.left + 2)
            table_tree.insert(id=node_id, parent_id=target_id, tree_id=target.tree_id, 
                              level=target.level+1, left=target.right, right=target.right + 1)
        else:
            raise ValueError
    
    def delete_node(self, node_id):
        db, table_tree = self.db, self.settings.table_tree
        node = db(table_tree.id == node_id).select().first()
        if not node:
            raise ValueError

        left = node.left
        right = node.right
        tree_width = right - left + 1

        db(table_tree.right >= node.right).update(right=table_tree.right - tree_width)
        db(table_tree.left >= node.right).update(left=table_tree.left - tree_width)
        db(table_tree.id == node_id).delete()
        
############################ tree_manager #########################################

    def _calculate_inter_tree_move_values(self, node_id, target_id, position):
        db, table_tree = self.db, self.settings.table_tree
        node = db(table_tree.id == node_id).select().first()
        target = db(table_tree.id == target_id).select().first()
        
        left = node.left
        level = node.level
        target_left = target.left
        target_right = target.right
        target_level = target.level
        
        if position == 'last-child' or position == 'first-child':
            if position == 'last-child':
                space_target = target_right - 1
            else:
                space_target = target_left
            level_change = level - target_level - 1
            parent = target_id
        elif position == 'left' or position == 'right':
            if position == 'left':
                space_target = target_left - 1
            else:
                space_target = target_right
            level_change = level - target_level
            parent = target.parent_id
        else:
            raise ValueError

        left_right_change = left - space_target - 1
        
        right_shift = 0
        if parent:
            right_shift = 2 * (int(self.get_descendant_count(node_id)) + 1)
        
        return space_target, level_change, left_right_change, parent, right_shift

    def _create_space(self, size, space_target, tree_id):
        self._manage_space(size, space_target, tree_id)
        
    def _create_tree_space(self, target_tree_id):
        db, table_tree = self.db, self.settings.table_tree
        db(table_tree.tree_id > target_tree_id).update(tree_id=table_tree.tree_id + 1)
            
    def _get_next_tree_id(self):
        db, table_tree = self.db, self.settings.table_tree
        max_tid = db().select(table_tree.ALL,orderby=~table_tree.tree_id).first()
        if max_tid:
            return max_tid.tree_id + 1
        else:
            return False
        
    def _inter_tree_move_and_close_gap(self, node_id, level_change, left_right_change, new_tree_id, parent_id=None):
        db, table_tree = self.db, self.settings.table_tree
        node = db(table_tree.id == node_id).select().first()
        
        left = node.left
        right = node.right
        gap_size = right - left + 1
        gap_target_left = left - 1
        
        for beta_node in db(table_tree.tree_id == node.tree_id).select():
            if (beta_node.left >= left and beta_node.left <= right):  
                beta_node.update_record(level=beta_node.level - level_change)

            if (beta_node.left >= left and beta_node.left <= right):
                beta_node.update_record(tree_id=new_tree_id)

            if (beta_node.left >= left and beta_node.left <= right):
                beta_node.update_record(left=beta_node.left - left_right_change)
            elif (beta_node.left > gap_target_left):
                beta_node.update_record(left=beta_node.left - gap_size)
            
            if (beta_node.right >= left and beta_node.right <= right):
                beta_node.update_record(right=beta_node.right - left_right_change)
            elif (beta_node.right > gap_target_left):
                beta_node.update_record(right=beta_node.right - gap_size)
                
            if beta_node.id == node.id:
                beta_node.update_record(parent_id=parent_id)
                    
    def insert_node(self, node_id, target_id, position='last-child'):
        db, table_tree = self.db, self.settings.table_tree
        node = db(table_tree.id == node_id).select().first()
        target = db(table_tree.id == target_id).select().first()
        
        if target is None:
            if self._get_next_tree_id():
                next_tid = self._get_next_tree_id()
                table_tree.insert(id=node_id,parent_id=None,tree_id=next_tid,
                                  level=0,left=1,right=2)
            # if there is no trees
            else:
                table_tree.insert(id=node_id,parent_id=None,tree_id=1,
                                  level=0,left=1,right=2)
        
        elif not node:
            self._update_tree(node_id, target_id, position)

        elif self.is_root_node(target_id) and position in ['left','right']:
            target_tree_id = target.tree_id
            if position == 'left':
                tree_id = target_tree_id
                space_target = target_tree_id - 1
            else:
                tree_id = target_tree_id + 1
                space_target = target_tree_id
                
            self._create_tree_space(space_target)
            
            node.update_record(left=1,
                           right=2,
                           level=0,
                           tree_id=tree_id,
                           parent_id=None)
        else:
            node.update_record(left=0,
                               level=0)

            space_target, level, left, parent_id, right_shift = self._calculate_inter_tree_move_values(node_id, target_id, position)
            parent = db(table_tree.id == parent_id).select().first()
            tree_id = parent.tree_id
            
            self._create_space(2, space_target, tree_id)
            
            node.update_record(left=node.left - left,
                               right=node.right - left + 1,
                               level=node.level - level,
                               tree_id=tree_id,
                               parent_id=parent_id)
            
#    def _post_insert_update_cached_parent_right(self, instance_id, right_shift):
#        db, table_tree = self.db, self.settings.table_tree
#        instance = db(table_tree.id == instance_id).select().first()
#        instance.update_record(right=instance.right + right_shift)
#        
#        setattr(instance, self.right_attr, getattr(instance, self.right_attr) + right_shift)
#        attr = '_%s_cache' % instance.parent_id
#        if hasattr(instance, attr):
#            parent = getattr(instance, attr)
#            if parent:
#                self._post_insert_update_cached_parent_right(parent, right_shift)            


#    def insert_node(self, node_id, target_id, position='last-child'):
#        db, table_tree = self.db, self.settings.table_tree
#        node = db(table_tree.id == node_id).select().first()
#        target = db(table_tree.id == target_id).select().first()
#        
#        if target is None:
#            if self._get_next_tree_id():
#                next_tid = self._get_next_tree_id()
#                table_tree.insert(id=node_id,parent_id=None,tree_id=next_tid,
#                                  level=0,left=1,right=2)
#            # if there is no trees
#            else:
#                table_tree.insert(id=node_id,parent_id=None,tree_id=1,
#                                  level=0,left=1,right=2)
#            return
#        
#        elif not node:
#            self._update_tree(node_id, target_id, position)
#            return
#        
#        left = node.left
#        right = node.right
#        level = node.level
#        current_tree_id = node.tree_id
#        tree_width = right - left + 1
#
#        # root node の　兄弟を作る
#        if self.is_root_node(target.id) and position in ['left', 'right']:
#            if position == 'left':
#                db(table_tree.right >= target.left)(table_tree.tree_id == target.tree_id).update(left=table_tree.left + tree_width + 1)
#                db(table_tree.right >= target.left)(table_tree.tree_id == target.tree_id).update(right=table_tree.right + tree_width + 1)
#            else:
#                db(table_tree.right >= target.right)(table_tree.tree_id == target.tree_id).update(left=table_tree.left + tree_width + 1)
#                db(table_tree.right >= target.right)(table_tree.tree_id == target.tree_id).update(right=table_tree.right + tree_width + 1)
#                #続きを書く  新しいルートの作成
#        
#        else:
#            if position == 'last-child':
#                #calculate  サブツリー以外への影響 　last-child
#                node.update_record(parent_id=target.id)
#                db(table_tree.right >= target.right)(table_tree.tree_id == target.tree_id).update(right=table_tree.right + tree_width)
#                db(table_tree.left >= target.right)(table_tree.tree_id == target.tree_id).update(left=table_tree.left + tree_width)
#            elif position == 'first-child':
#                #calculate  サブツリー以外への影響 　first-child                           
#                node.update_record(parent_id=target.id)
#                db(table_tree.right >= target.left)(table_tree.tree_id == target.tree_id).update(right=table_tree.right + tree_width)
#                db(table_tree.left >= target.left)(table_tree.tree_id == target.tree_id).update(left=table_tree.left + tree_width)
#            elif position == 'left':
#                #calculate  サブツリー以外への影響 　sibling-left
#                node.update_record(parent_id=target.parent_id)
#                db(table_tree.right >= target.left)(table_tree.tree_id == target.tree_id).update(right=table_tree.right + tree_width)
#                db(table_tree.left >= target.left)(table_tree.tree_id == target.tree_id).update(left=table_tree.left + tree_width)
#            elif position == 'right':
#                #calculate  サブツリー以外への影響 　sibling-right
#                node.update_record(parent_id=target.parent_id)
#                db(table_tree.right >= target.right)(table_tree.tree_id == target.tree_id).update(right=table_tree.right + tree_width)
#                db(table_tree.left >= target.right)(table_tree.tree_id == target.tree_id).update(left=table_tree.left + tree_width)
#            else:
#                raise ValueError
#            
#            #calculate  サブツリー内への影響
#            for beta_node in db(table_tree.left >= node.left)(table_tree.left <= node.right)(table_tree.tree_id == current_tree_id).select():
#                beta_node.update_record(level=beta_node.level + target.level + 1,
#                                        left=beta_node.left + target.right - 1,
#                                        right=beta_node.right + target.right - 1,
#                                        tree_id=target.tree_id)
                
    def move_node(self, node_id, target_id, position='last-child'):
        db, table_tree = self.db, self.settings.table_tree
        node = db(table_tree.id == node_id).select().first()
        target = db(table_tree.id == target_id).select().first()
        
        if not node:
            raise ValueError
        
        if target is None:
            if self.is_child_node(node_id):
                self._make_child_root_node(node_id)
        elif self.is_root_node(target_id) and position in ['left','right']:
            self._make_sibling_of_root_node(node_id, target_id, position)
        else:
            if self.is_root_node(node_id):
                self._move_root_node(node_id, target_id, position)
            else:
                self._move_child_node(node_id, target_id, position)

    def _make_child_root_node(self, node_id, new_tree_id=None):
        db, table_tree = self.db, self.settings.table_tree
        node = db(table_tree.id == node_id).select().first()
                
        left = node.left
        right = node.right
        level = node.level
        if not new_tree_id:
            new_tree_id = self._get_next_tree_id()
        left_right_change = left - 1
        
        self._inter_tree_move_and_close_gap(node_id, level, left_right_change, new_tree_id)
        node.update_record(left=left - left_right_change,
                           right=right - left_right_change,
                           level=0,
                           tree_id=new_tree_id,
                           parent_id=None)
        
    def _make_sibling_of_root_node(self, node_id, target_id, position):
        db, table_tree = self.db, self.settings.table_tree
        node = db(table_tree.id == node_id).select().first()
        target = db(table_tree.id == target_id).select().first()
        
        if node == target:
            raise ValueError
        
        tree_id = node.tree_id
        target_tree_id = target.tree_id
        
        if self.is_child_node(node_id):
            if position == 'left':
                space_target = target_tree_id - 1
                new_tree_id = target_tree_id
            elif position == 'right':
                space_target = target_tree_id
                new_tree_id = target_tree_id + 1
            else:
                raise ValueError

            self._create_tree_space(space_target)
        
            if tree_id > space_target:
                node.update_record(tree_id=tree_id + 1)
            self._make_child_root_node(node_id, new_tree_id)
        else:
            if position == 'left':
                if target_tree_id > tree_id:
                    left_sibling = self.get_previous_sibling(target_id)
                    if node_id == left_sibling:
                        return
                    new = db(table_tree.id == left_sibling).select().first()
                    new_tree_id = new.tree_id
                    lower_bound, upper_bound = tree_id, new_tree_id
                    shift = -1
                else:
                    new_tree_id = target_tree_id
                    lower_bound, upper_bound = new_tree_id, tree_id
                    shift = 1
            elif position == 'right':
                if target_tree_id > tree_id:
                    new_tree_id = target_tree_id
                    lower_bound, upper_bound = tree_id, target_tree_id
                    shift = -1
                else:
                    right_sibling = self.get_next_sibling(target_id)
                    if node_id == right_sibling:
                        return
                    new = db(table_tree.id == right_sibling).select().first()
                    new_tree_id = new.tree_id
                    lower_bound, upper_bound = new_tree_id, tree_id
                    shift = 1
            else:
                raise ValueError
            
            for beta_node in db(table_tree.tree_id >= lower_bound)(table_tree.tree_id <= upper_bound).select():
                if beta_node.tree_id == tree_id:
                    beta_node.update_record(tree_id=new_tree_id)
                else:
                    beta_node.update_record(tree_id=beta_node.tree_id + shift)
                
#    def _make_sibling_of_root_node(self, node_id, target_id, position):
#        db, table_tree = self.db, self.settings.table_tree
#        node = db(table_tree.id == node_id).select().first()
#        target = db(table_tree.id == target_id).select().first()
#        current_tree_id = node.tree_id
#        target_tree_id = target.tree_id
#        
#        if self.is_child_node(node.id):
#            if position == 'left':
#                space_target = target_tree_id - 1
#                new_tree_id = target_tree_id
#            elif position == 'right':
#                space_target = target_tree_id
#                new_tree_id = target_tree_id + 1
#            else:
#                raise ValueError
#            
#            if current_tree_id > space_target:
#                node.update_record(tree_id = current_tree_id + 1)
#            
#            self._make_child_root_node(node.id, new_tree_id)
#        else:
#            if position == 'left':
#                if target_tree_id > current_tree_id:
#                    pass


    def _manage_space(self, size, space_target, tree_id):
            db, table_tree = self.db, self.settings.table_tree
            
            for node in db((table_tree.left >= space_target) | (table_tree.left <= space_target))(table_tree.tree_id == tree_id).select():
                if node.left > space_target:
                    node.update_record(left=node.left + size)
                if node.right > space_target:
                    node.update_record(right=node.right + size)
        
    def _move_child_node(self, node_id, target_id, position):
        db, table_tree = self.db, self.settings.table_tree
        node = db(table_tree.id == node_id).select().first()
        target = db(table_tree.id == target_id).select().first()
        node_tree_id = node.tree_id
        target_tree_id = target.tree_id
                                        
        if node_tree_id == target_tree_id:
            self._move_child_within_tree(node_id, target_id, position)
        else:
            self._move_child_to_new_tree(node_id, target_id, position)
            
    def _move_child_to_new_tree(self, node_id, target_id, position):
        db, table_tree = self.db, self.settings.table_tree
        node = db(table_tree.id == node_id).select().first()
        target = db(table_tree.id == target_id).select().first()
        
        left = node.left
        right = node.right
        level = node.level
        new_tree_id = target.tree_id
                        
        space_target, level_change, left_right_change, parent_id, new_parent_right = self._calculate_inter_tree_move_values(node_id, target_id, position)

        tree_width = right - left + 1
        
        self._create_space(tree_width, space_target, new_tree_id)
        self._inter_tree_move_and_close_gap(node_id, level_change, left_right_change, new_tree_id, parent_id)
        node.update_record(left=node.left - left_right_change,
                           right=node.right - left_right_change,
                           level=node.level - level_change,
                           tree_id=new_tree_id,
                           parent_id=parent_id)
            
    def _move_child_within_tree(self, node_id, target_id, position):
        db, table_tree = self.db, self.settings.table_tree
        node = db(table_tree.id == node_id).select().first()
        target = db(table_tree.id == target_id).select().first()
        left = node.left
        right = node.right
        level = node.level
        current_tree_id = node.tree_id
        tree_width = right - left + 1
        target_left = target.left
        target_right = target.right
        target_level = target.level
        
        if position == 'last-child' or position == 'first-child':
            if node == target:
                raise ValueError
            elif left < target_left < right:
                raise ValueError
            if position == 'last-child':
                if target_right > right:
                    new_left = target_right - tree_width
                    new_right = target_right - 1
                else:
                    new_left = target_right
                    new_right = target_right + tree_width - 1
            else: #if position == 'first-child'
                if target_left > left:
                    new_left = target_left - tree_width + 1
                    new_right = target_left
                else:
                    new_left = target_left + 1
                    new_right = target_left + tree_width
            level_change = level - target_level - 1
            parent = target.id
        elif position == 'left' or position == 'right':
            if node == target:
                raise ValueError
            elif left < target_left < right:
                raise ValueError
            if position == 'left':
                if target_left > left:
                    new_left = target_left - tree_width
                    new_right = target_left - 1
                else:
                    new_left = target_left
                    new_right = target_left + tree_width - 1
            else:
                if target_right > right:
                    new_left = target_right - tree_width + 1
                    new_right = target_right
                else:
                    new_left = target_right + 1
                    new_right = target_right + tree_width
            level_change = level - target_level
            parent = target.parent_id
        else:
            raise ValueError
        
        left_boundary = min(left, new_left)
        right_boundary = max(right, new_right)
        left_right_change = new_left - left
        gap_size = tree_width
        if left_right_change > 0:
            gap_size = -gap_size

        for beta_node in db(table_tree.tree_id == current_tree_id).select():
            if (beta_node.left >= left and beta_node.left <= right):
                beta_node.update_record(level=beta_node.level - level_change,
                                    left=beta_node.left + left_right_change)
            
            elif (beta_node.left >= left_boundary and beta_node.left <= right_boundary):
                beta_node.update_record(left=beta_node.left + gap_size)
                
            if (beta_node.right >= left and beta_node.right <= right):
                beta_node.update_record(right=beta_node.right + left_right_change)
            
            elif (beta_node.right >= left_boundary and beta_node.right <= right_boundary):
                beta_node.update_record(right=beta_node.right + gap_size)
                                
        node.update_record(left=new_left,
                           right=new_right,
                           level=node.level - level_change,
                           parent_id=parent)
        
    def _move_root_node(self, node_id, target_id, position):
        db, table_tree = self.db, self.settings.table_tree
        node = db(table_tree.id == node_id).select().first()
        target = db(table_tree.id == target_id).select().first()
        if not node:
            raise ValueError
        
        left = node.left
        right = node.right
        level = node.level
        current_tree_id = node.tree_id
        new_tree_id = target.tree_id
        tree_width = right - left + 1
        
        if node == target:
            raise ValueError
        elif current_tree_id == new_tree_id:
            raise ValueError
        
        space_target, level_change, left_right_change, parent_pk, right_shift = self._calculate_inter_tree_move_values(node_id, target_id, position)
        self._create_space(tree_width, space_target, new_tree_id)
        
        for beta_node in db(table_tree.left >= left)(table_tree.left <= right)(table_tree.tree_id == current_tree_id).select():
            beta_node.update_record(level=beta_node.level - level_change,
                                    left=beta_node.left - left_right_change,
                                    right=beta_node.right - left_right_change,
                                    tree_id=new_tree_id)
            if beta_node.id == node.id:
                beta_node.update_record(parent_id=parent_pk)
        
        node.update_record(left=node.left - left_right_change,
                           right=node.right - left_right_change,
                           level=node.level - level_change,
                           tree_id=new_tree_id,
                           parent_id=parent_pk)
