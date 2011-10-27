# -*- coding: utf-8 -*-
# This plugins is licensed under the MIT license: http://www.opensource.org/licenses/mit-license.php
# Authors: Yusuke Kishita <yuusuuke.kishiita@gmail.com>, Kenji Hosoda <hosoda@s-cubism.jp>
# Original by: http://code.google.com/p/django-mptt/
from gluon import *
from gluon.dal import Row
from gluon.storage import Storage
from email._parseaddr import SPACE

class MPTTModel(object):
    
    def __init__(self, db):
        self.db = db        
        
        settings = self.settings = Storage()
        
        settings.extra_fields = {}
        
        settings.table_node_name = 'node'
        settings.table_node = None
        
    def define_tables(self, migrate = True, fake_migrate = False):
        db, settings = self.db, self.settings
        
        if not settings.table_node_name in db.tables:
            table = db.define_table(
                settings.table_node_name, 
                Field('parent', 'reference %s' % settings.table_node_name),
                Field('tree_id', 'integer'),
                Field('level', 'integer'), 
                Field('left', 'integer'), 
                Field('right', 'integer'), 
                migrate=migrate, fake_migrate=fake_migrate,
                *settings.extra_fields.get(settings.table_node_name, []))
        settings.table_node = db[settings.table_node_name]
        
    @property
    def asc(self):
        return ~self.settings.table_node.left
    
    @property
    def desc(self):
        return self.settings.table_node.left
        
    def _load_node(self, node_or_node_id):
        if node_or_node_id is None:
            return node_or_node_id
        db, table_node = self.db, self.settings.table_node
        if isinstance(node_or_node_id, Row):
            return node_or_node_id
        else:
            return db(table_node.id == node_or_node_id).select().first()
        
    def ancestors_from_node(self, node, include_self=False):
        db, table_node = self.db, self.settings.table_node
        node = self._load_node(node)
                
        left, right = node.left, node.right
        if include_self:
            left += 1
            right -= 1
            
        return db(table_node.left < left)(table_node.right > right)(
                  table_node.tree_id == node.tree_id)
    
    def descendants_from_node(self, node):
        db, table_node = self.db, self.settings.table_node
        node = self._load_node(node)
            
        return db(table_node.left > node.left)(table_node.right < node.right)(
                  table_node.tree_id == node.tree_id)
    
    def count_descendants_from_node(self, node):
        db, table_node = self.db, self.settings.table_node
        node = self._load_node(node)
        return (node.right - node.left - 1) / 2   
    
    def leafnodes(self):
        db, table_node = self.db, self.settings.table_node
        return db(table_node.right == table_node.left+1)
    
    def get_next_sibling(self, node):
        db, table_node = self.db, self.settings.table_node
        node = self._load_node(node)
        if self.is_root_node(node):
            next_sib = db(table_node.left == 1)(table_node.tree_id == node.tree_id + 1).select(table_node.id)
        else:
            next_sib = db(table_node.left == node.right + 1)(table_node.tree_id == node.tree_id).select(table_node.id)
        return next_sib.id
    
    def get_previous_sibling(self, node):
        db, table_node = self.db, self.settings.table_node
        node = self._load_node(node)
        if self.is_root_node(node):
            previous_sib = db(table_node.left == 1)(table_node.tree_id == node.tree_id - 1).select(table_node.id)
        else:
            previous_sib = db(table_node.right == node.left - 1)(table_node.tree_id == node.tree_id).select(table_node.id)
        return previous_sib.id
    
    def roots(self):
        db, table_node = self.db, self.settings.table_node
        return db(table_node.left == 1)
    
    def is_root_node(self, node_or_node_id):
        db, table_node = self.db, self.settings.table_node
        if isinstance(node_or_node_id, Row):
            return node_or_node_id.left == 1
        else:
            return bool(db(table_node.id == node_or_node_id)(table_node.left == 1).count())
            
    def is_child_node(self, node_or_node_id):
        db, table_node = self.db, self.settings.table_node
        if isinstance(node_or_node_id, Row):
            return node_or_node_id.left > 1
        else:
            return bool(db(table_node.id == node_or_node_id)(table_node.left > 1).count())
        
    def is_leaf_node(self, node_or_node_id):
        db, table_node = self.db, self.settings.table_node
        if isinstance(node_or_node_id, Row):
            return node_or_node_id.right == node_or_node_id.left+1
        else:
            return bool(db(table_node.id == node_or_node_id)(
                           table_node.right == table_node.left+1).count())
        
    def is_ancestor_of(self, node1, node2):
        db, table_node = self.db, self.settings.table_node
        node1 = self._load_node(node1)
        node2 = self._load_node(node2)
        
        return (node1.left < node2.left) and (node1.right > node2.right)
        
    def is_descendant_of(self, node1, node2):
        db, table_node = self.db, self.settings.table_node
        node1 = self._load_node(node1)
        node2 = self._load_node(node2)
        return (node1.left > node2.left) and (node1.right < node2.right)
        
    def delete_node(self, node):
        db, table_node = self.db, self.settings.table_node
        node = self._load_node(node)
        
        current_tree_id = node.tree_id
        left = node.left
        right = node.right
        tree_width = right - left + 1

        db(table_node.left >= left)(table_node.left <= right)(
           table_node.tree_id == current_tree_id).delete()            

        db(table_node.right >= node.right)(table_node.tree_id == current_tree_id
           ).update(right=table_node.right - tree_width)
        db(table_node.left >= node.right)(table_node.tree_id == current_tree_id
           ).update(left=table_node.left - tree_width)
        
############################ tree_manager #########################################

    def _calculate_inter_tree_move_values(self, node, target, position):
        db, table_node = self.db, self.settings.table_node
        
        node = self._load_node(node)
        target = self._load_node(target)
        
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
            parent = target.id
        elif position == 'left' or position == 'right':
            if position == 'left':
                space_target = target_left - 1
            else:
                space_target = target_right
            level_change = level - target_level
            parent = target.parent
        else:
            raise ValueError

        left_right_change = left - space_target - 1
        
        right_shift = 0
        if parent:
            right_shift = 2 * (int(self.count_descendants_from_node(node.id)) + 1)
        
        return space_target, level_change, left_right_change, parent, right_shift

    def _create_space(self, size, space_target, tree_id):
        self._manage_space(size, space_target, tree_id)
        
    def _create_tree_space(self, target_tree_id):
        db, table_node = self.db, self.settings.table_node
        db(table_node.tree_id > target_tree_id).update(tree_id=table_node.tree_id + 1)
            
    def _get_next_tree_id(self):
        db, table_node = self.db, self.settings.table_node
        max_tid = db().select(table_node.tree_id, orderby=~table_node.tree_id).first()
        if max_tid:
            return max_tid.tree_id + 1
        else:
            return False
        
    def _inter_tree_move_and_close_gap(self, node, level_change, left_right_change, 
                                       new_tree_id, parent=None):
        db, table_node = self.db, self.settings.table_node
        
        node = self._load_node(node)
        
        left = node.left
        right = node.right
        gap_size = right - left + 1
        gap_target_left = left - 1
        
        for beta_node in db(table_node.tree_id == node.tree_id).select():
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
                beta_node.update_record(parent=parent)
                    
    def insert_node(self, target, position='last-child', **extra_vars):
        db, table_node = self.db, self.settings.table_node
        target = self._load_node(target)
        
        if target is None:
            if self._get_next_tree_id():
                next_tid = self._get_next_tree_id()
                return table_node.insert(parent=None, tree_id=next_tid,
                                  level=0, left=1, right=2, 
                                  **extra_vars)
            # if there is no trees
            else:
                return table_node.insert(parent=None, tree_id=1,
                                  level=0, left=1, right=2, 
                                  **extra_vars)
        
        else:
            if position == 'last-child':
                db(table_node.right >= target.right)(table_node.tree_id == target.tree_id
                   ).update(right=table_node.right + 2)
                db(table_node.left >= target.right)(table_node.tree_id == target.tree_id
                   ).update(left=table_node.left + 2)
                return table_node.insert(parent=target and target.id,
                                  tree_id=target.tree_id, 
                                  level=target.level+1,
                                  left=target.right,
                                  right=target.right + 1, 
                                  **extra_vars)
            elif self.is_root_node(target) and position in ('left','right'):
                target_tree_id = target.tree_id
                if position == 'left':
                    tree_id = target_tree_id
                    space_target = target_tree_id - 1
                else:
                    tree_id = target_tree_id + 1
                    space_target = target_tree_id
                    
                self._create_tree_space(space_target)
                
                return table_node.insert(parent=None,
                                  tree_id = tree_id,
                                  level=0,
                                  left=1,
                                  right=2,
                                  **extra_vars)
            else:
                raise ValueError
            
    # def update_node(self, node_id, target_id, position='last-child', **extra_vars):
        # db, table_node = self.db, self.settings.table_node
        # node = self._load_node(node)
        # target = self._load_node(target)
        
        # if self.is_root_node(target) and position in ('left','right'):
            # target_tree_id = target.tree_id
            # if position == 'left':
                # tree_id = target_tree_id
                # space_target = target_tree_id - 1
            # else:
                # tree_id = target_tree_id + 1
                # space_target = target_tree_id
                
            # self._create_tree_space(space_target)
            
            # node.update_record(left=1,
                           # right=2,
                           # level=0,
                           # tree_id=tree_id,
                           # parent=None)
        # else:
            # node.update_record(left=0,
                               # level=0)

            # space_target, level, left, parent, right_shift = (
                # self._calculate_inter_tree_move_values(node_id, target_id, position))
            # parent = db(table_node.id == parent).select().first()
            # tree_id = parent.tree_id
            
            # self._create_space(2, space_target, tree_id)
            
            # node.update_record(left=node.left - left,
                               # right=node.right - left + 1,
                               # level=node.level - level,
                               # tree_id=tree_id,
                               # parent=parent)
            
    def move_node(self, node, target, position='last-child'):
        db, table_node = self.db, self.settings.table_node
        node = self._load_node(node)
        target = self._load_node(target)
        
        if not node:
            raise ValueError
        
        if target is None:
            if self.is_child_node(node):
                self._make_child_root_node(node)
        elif self.is_root_node(target) and position in ['left','right']:
            self._make_sibling_of_root_node(node, target, position)
        else:
            if self.is_root_node(node):
                self._move_root_node(node, target, position)
            else:
                self._move_child_node(node, target, position)

    def _make_child_root_node(self, node, new_tree_id=None):
        db, table_node = self.db, self.settings.table_node
        node = self._load_node(node)
                
        left = node.left
        right = node.right
        level = node.level
        if not new_tree_id:
            new_tree_id = self._get_next_tree_id()
        left_right_change = left - 1
        
        self._inter_tree_move_and_close_gap(node, level, left_right_change, new_tree_id)
        node.update_record(left=left - left_right_change,
                           right=right - left_right_change,
                           level=0,
                           tree_id=new_tree_id,
                           parent=None)
        
    def _make_sibling_of_root_node(self, node, target, position):
        db, table_node = self.db, self.settings.table_node
        node = self._load_node(node)
        target = self._load_node(target)
        
        if node == target:
            raise ValueError
        
        tree_id = node.tree_id
        target_tree_id = target.tree_id
        
        if self.is_child_node(node):
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
            self._make_child_root_node(node, new_tree_id)
        else:
            if position == 'left':
                if target_tree_id > tree_id:
                    left_sibling = self.get_previous_sibling(target)
                    if node.id == left_sibling:
                        return
                    new = db(table_node.id == left_sibling).select().first()
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
                    right_sibling = self.get_next_sibling(target)
                    if node.id == right_sibling:
                        return
                    new = db(table_node.id == right_sibling).select().first()
                    new_tree_id = new.tree_id
                    lower_bound, upper_bound = new_tree_id, tree_id
                    shift = 1
            else:
                raise ValueError
            
            for beta_node in db(table_node.tree_id >= lower_bound)(
                                table_node.tree_id <= upper_bound).select():
                if beta_node.tree_id == tree_id:
                    beta_node.update_record(tree_id=new_tree_id)
                else:
                    beta_node.update_record(tree_id=beta_node.tree_id + shift)

    def _manage_space(self, size, space_target, tree_id):
            db, table_node = self.db, self.settings.table_node
            
            for node in db((table_node.left >= space_target) | (table_node.left <= space_target))(
                           table_node.tree_id == tree_id).select():
                if node.left > space_target:
                    node.update_record(left=node.left + size)
                if node.right > space_target:
                    node.update_record(right=node.right + size)
        
    def _move_child_node(self, node, target, position):
        db, table_node = self.db, self.settings.table_node
        node = self._load_node(node)
        target = self._load_node(target)
        node_tree_id = node.tree_id
        target_tree_id = target.tree_id
                                        
        if node_tree_id == target_tree_id:
            self._move_child_within_tree(node, target, position)
        else:
            self._move_child_to_new_tree(node, target, position)
            
    def _move_child_to_new_tree(self, node, target, position):
        db, table_node = self.db, self.settings.table_node
        node = self._load_node(node)
        target = db(table_node.id == target).select().first()
        
        left = node.left
        right = node.right
        level = node.level
        new_tree_id = target.tree_id
                        
        space_target, level_change, left_right_change, parent, new_parent_right = (
            self._calculate_inter_tree_move_values(node, target, position))

        tree_width = right - left + 1
        
        self._create_space(tree_width, space_target, new_tree_id)
        self._inter_tree_move_and_close_gap(node, level_change, left_right_change, new_tree_id, parent)
        node.update_record(left=node.left - left_right_change,
                           right=node.right - left_right_change,
                           level=node.level - level_change,
                           tree_id=new_tree_id,
                           parent=parent)
            
    def _move_child_within_tree(self, node, target, position):
        db, table_node = self.db, self.settings.table_node
        node = self._load_node(node)
        target = self._load_node(target)
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
            parent = target.parent
        else:
            raise ValueError
        
        left_boundary = min(left, new_left)
        right_boundary = max(right, new_right)
        left_right_change = new_left - left
        gap_size = tree_width
        if left_right_change > 0:
            gap_size = -gap_size

        for beta_node in db(table_node.tree_id == current_tree_id).select():
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
                           parent=parent)
        
    def _move_root_node(self, node, target, position):
        db, table_node = self.db, self.settings.table_node
        node = self._load_node(node)
        target = self._load_node(target)
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
        
        space_target, level_change, left_right_change, parent_pk, right_shift = (
            self._calculate_inter_tree_move_values(node, target, position))
        self._create_space(tree_width, space_target, new_tree_id)
        
        for beta_node in db(table_node.left >= left)(table_node.left <= right)(
                            table_node.tree_id == current_tree_id).select():
            beta_node.update_record(level=beta_node.level - level_change,
                                    left=beta_node.left - left_right_change,
                                    right=beta_node.right - left_right_change,
                                    tree_id=new_tree_id)
            if beta_node.id == node.id:
                beta_node.update_record(parent=parent_pk)
        
        node.update_record(left=node.left - left_right_change,
                           right=node.right - left_right_change,
                           level=node.level - level_change,
                           tree_id=new_tree_id,
                           parent=parent_pk)
