# -*- coding: utf-8 -*-
# This plugins is licensed under the MIT license: http://www.opensource.org/licenses/mit-license.php
# Authors: Yusuke Kishita <yuusuuke.kishiita@gmail.com>, Kenji Hosoda <hosoda@s-cubism.jp>
# Original by: http://code.google.com/p/django-mptt/
from gluon import *
from gluon.dal import Row
from gluon.storage import Storage
from email._parseaddr import SPACE

def update_args(func):
    def wrapper(self, *args, **kwds):
        output = func(self, *args, **kwds)
        for arg in args:
            if isinstance(arg, Row):
                table_node = self.settings.table_node
                latest_node = self.db(table_node.id == arg[table_node.id]).select().first()
                arg.lft = latest_node.lft
                arg.rgt = latest_node.rgt
                arg.level = latest_node.level
                arg.parent = latest_node.parent
                arg.tree_id = latest_node.tree_id
        return output
    return wrapper
                
        
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
                Field('lft', 'integer'), 
                Field('rgt', 'integer'), 
                migrate=migrate, fake_migrate=fake_migrate,
                *settings.extra_fields.get(settings.table_node_name, []))
        settings.table_node = db[settings.table_node_name]
        
    @property
    def asc(self):
        return ~self.settings.table_node.lft
    
    @property
    def desc(self):
        return self.settings.table_node.lft
        
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
                
        left, right = node.lft, node.rgt
        if include_self:
            left += 1
            right -= 1
            
        return db(table_node.lft < left)(table_node.rgt > right)(
                  table_node.tree_id == node.tree_id)
    
    def descendants_from_node(self, node, include_self=False):
        db, table_node = self.db, self.settings.table_node
        node = self._load_node(node)
        
        left, right = node.lft, node.rgt
        if include_self:
            left -= 1
            right += 1
            
        return db(table_node.lft > left)(table_node.rgt < right)(
                  table_node.tree_id == node.tree_id)
    
    def count_descendants_from_node(self, node):
        db, table_node = self.db, self.settings.table_node
        node = self._load_node(node)
        return (node.rgt - node.lft - 1) / 2   
    
    def leafnodes(self):
        db, table_node = self.db, self.settings.table_node
        return db(table_node.rgt == table_node.lft+1)
    
    def get_first_child(self, node):
        db, table_node = self.db, self.settings.table_node
        node = self._load_node(node)
        if not self.is_leaf_node(node):
            first_child = db(table_node.lft == node.lft + 1)(table_node.tree_id == node.tree_id).select().first()
        else:
            return None  
        return first_child.id
            
    def get_next_sibling(self, node):
        db, table_node = self.db, self.settings.table_node
        node = self._load_node(node)
        if self.is_root_node(node):
            next_sib = db(table_node.lft == 1)(table_node.tree_id == node.tree_id + 1).select().first()
        else:
            next_sib = db(table_node.lft == node.rgt + 1)(table_node.tree_id == node.tree_id).select().first()
        if next_sib:
            return next_sib.id
        else:
            return False
    
    def get_previous_sibling(self, node):
        db, table_node = self.db, self.settings.table_node
        node = self._load_node(node)
        if self.is_root_node(node):
            previous_sib = db(table_node.lft == 1)(table_node.tree_id == node.tree_id - 1).select().first()
        else:
            previous_sib = db(table_node.rgt == node.lft - 1)(table_node.tree_id == node.tree_id).select().first()
        if previous_sib:
            return previous_sib.id
        else:
            return False
    
    def roots(self):
        db, table_node = self.db, self.settings.table_node
        return db(table_node.lft == 1)
    
    def is_root_node(self, node_or_node_id):
        db, table_node = self.db, self.settings.table_node
        if isinstance(node_or_node_id, Row):
            return node_or_node_id.lft == 1
        else:
            return bool(db(table_node.id == node_or_node_id)(table_node.lft == 1).count())
            
    def is_child_node(self, node_or_node_id):
        db, table_node = self.db, self.settings.table_node
        if isinstance(node_or_node_id, Row):
            return node_or_node_id.lft > 1
        else:
            return bool(db(table_node.id == node_or_node_id)(table_node.lft > 1).count())
        
    def is_leaf_node(self, node_or_node_id):
        db, table_node = self.db, self.settings.table_node
        if isinstance(node_or_node_id, Row):
            return node_or_node_id.rgt == node_or_node_id.lft+1
        else:
            return bool(db(table_node.id == node_or_node_id)(
                           table_node.rgt == table_node.lft+1).count())
        
    def is_ancestor_of(self, node1, node2):
        db, table_node = self.db, self.settings.table_node
        node1 = self._load_node(node1)
        node2 = self._load_node(node2)
        
        return (node1.lft < node2.lft) and (node1.rgt > node2.rgt)
        
    def is_descendant_of(self, node1, node2):
        db, table_node = self.db, self.settings.table_node
        node1 = self._load_node(node1)
        node2 = self._load_node(node2)
        return (node1.lft > node2.lft) and (node1.rgt < node2.rgt)
        
    @update_args        
    def delete_node(self, node):
        db, table_node = self.db, self.settings.table_node
        node = self._load_node(node)
        
        current_tree_id = node.tree_id
        left = node.lft
        right = node.rgt
        tree_width = right - left + 1

        db(table_node.lft >= left)(table_node.lft <= right)(
           table_node.tree_id == current_tree_id).delete()            

        db(table_node.rgt >= node.rgt)(table_node.tree_id == current_tree_id
           ).update(rgt=table_node.rgt - tree_width)
        db(table_node.lft >= node.rgt)(table_node.tree_id == current_tree_id
           ).update(lft=table_node.lft - tree_width)
        
############################ tree_manager #########################################

    def _calculate_inter_tree_move_values(self, node, target, position):
        db, table_node = self.db, self.settings.table_node
        
        node = self._load_node(node)
        target = self._load_node(target)
        
        left = node.lft
        level = node.level
        target_left = target.lft
        target_right = target.rgt
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
        
        left = node.lft
        right = node.rgt
        gap_size = right - left + 1
        gap_target_left = left - 1
        
        for beta_node in db(table_node.tree_id == node.tree_id).select():
            if (beta_node.lft >= left and beta_node.lft <= right):  
                beta_node.update_record(level=beta_node.level - level_change)

            if (beta_node.lft >= left and beta_node.lft <= right):
                beta_node.update_record(tree_id=new_tree_id)

            if (beta_node.lft >= left and beta_node.lft <= right):
                beta_node.update_record(lft=beta_node.lft - left_right_change)
            elif (beta_node.lft > gap_target_left):
                beta_node.update_record(lft=beta_node.lft - gap_size)
            
            if (beta_node.rgt >= left and beta_node.rgt <= right):
                beta_node.update_record(rgt=beta_node.rgt - left_right_change)
            elif (beta_node.rgt > gap_target_left):
                beta_node.update_record(rgt=beta_node.rgt - gap_size)
                
            if beta_node.id == node.id:
                beta_node.update_record(parent=parent)
                    
    @update_args
    def insert_node(self, target, position='last-child', **extra_vars):
        db, table_node = self.db, self.settings.table_node
        target = self._load_node(target)
        
        if target is None:
            if self._get_next_tree_id():
                next_tid = self._get_next_tree_id()
                return table_node.insert(parent=None, tree_id=next_tid,
                                  level=0, lft=1, rgt=2, 
                                  **extra_vars)
            # if there is no trees
            else:
                return table_node.insert(parent=None, tree_id=1,
                                  level=0, lft=1, rgt=2, 
                                  **extra_vars)
        
        else:
            if position == 'last-child':
                db(table_node.rgt >= target.rgt)(table_node.tree_id == target.tree_id
                   ).update(rgt=table_node.rgt + 2)
                db(table_node.lft >= target.rgt)(table_node.tree_id == target.tree_id
                   ).update(lft=table_node.lft + 2)
                return table_node.insert(parent=target and target.id,
                                  tree_id=target.tree_id, 
                                  level=target.level+1,
                                  lft=target.rgt,
                                  rgt=target.rgt + 1, 
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
                                  lft=1,
                                  rgt=2,
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
            
            # node.update_record(lft=1,
                           # rgt=2,
                           # level=0,
                           # tree_id=tree_id,
                           # parent=None)
        # else:
            # node.update_record(lft=0,
                               # level=0)

            # space_target, level, left, parent, right_shift = (
                # self._calculate_inter_tree_move_values(node_id, target_id, position))
            # parent = db(table_node.id == parent).select().first()
            # tree_id = parent.tree_id
            
            # self._create_space(2, space_target, tree_id)
            
            # node.update_record(lft=node.lft - left,
                               # rgt=node.rgt - left + 1,
                               # level=node.level - level,
                               # tree_id=tree_id,
                               # parent=parent)
            
    @update_args            
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
                
        left = node.lft
        right = node.rgt
        level = node.level
        if not new_tree_id:
            new_tree_id = self._get_next_tree_id()
        left_right_change = left - 1
        
        self._inter_tree_move_and_close_gap(node, level, left_right_change, new_tree_id)
        node.update_record(lft=left - left_right_change,
                           rgt=right - left_right_change,
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
        db(table_node.lft > space_target)(table_node.tree_id == tree_id).update(lft=table_node.lft + size)
        db(table_node.rgt > space_target)(table_node.tree_id == tree_id).update(rgt=table_node.rgt + size)
            
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
        
        left = node.lft
        right = node.rgt
        level = node.level
        new_tree_id = target.tree_id
                        
        space_target, level_change, left_right_change, parent, new_parent_right = (
            self._calculate_inter_tree_move_values(node, target, position))

        tree_width = right - left + 1
        
        self._create_space(tree_width, space_target, new_tree_id)
        self._inter_tree_move_and_close_gap(node, level_change, left_right_change, new_tree_id, parent)
        node.update_record(lft=node.lft - left_right_change,
                           rgt=node.rgt - left_right_change,
                           level=node.level - level_change,
                           tree_id=new_tree_id,
                           parent=parent)
            
    def _move_child_within_tree(self, node, target, position):
        db, table_node = self.db, self.settings.table_node
        node = self._load_node(node)
        target = self._load_node(target)
        left = node.lft
        right = node.rgt
        level = node.level
        current_tree_id = node.tree_id
        tree_width = right - left + 1
        target_left = target.lft
        target_right = target.rgt
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
            if (beta_node.lft >= left and beta_node.lft <= right):
                beta_node.update_record(level=beta_node.level - level_change,
                                    lft=beta_node.lft + left_right_change)
            
            elif (beta_node.lft >= left_boundary and beta_node.lft <= right_boundary):
                beta_node.update_record(lft=beta_node.lft + gap_size)
                
            if (beta_node.rgt >= left and beta_node.rgt <= right):
                beta_node.update_record(rgt=beta_node.rgt + left_right_change)
            
            elif (beta_node.rgt >= left_boundary and beta_node.rgt <= right_boundary):
                beta_node.update_record(rgt=beta_node.rgt + gap_size)
                                
        node.update_record(lft=new_left,
                           rgt=new_right,
                           level=node.level - level_change,
                           parent=parent)
        
    def _move_root_node(self, node, target, position):
        db, table_node = self.db, self.settings.table_node
        node = self._load_node(node)
        target = self._load_node(target)
        if not node:
            raise ValueError
        
        left = node.lft
        right = node.rgt
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
        
        for beta_node in db(table_node.lft >= left)(table_node.lft <= right)(
                            table_node.tree_id == current_tree_id).select():
            beta_node.update_record(level=beta_node.level - level_change,
                                    lft=beta_node.lft - left_right_change,
                                    rgt=beta_node.rgt - left_right_change,
                                    tree_id=new_tree_id)
            if beta_node.id == node.id:
                beta_node.update_record(parent=parent_pk)
        
        node.update_record(lft=node.lft - left_right_change,
                           rgt=node.rgt - left_right_change,
                           level=node.level - level_change,
                           tree_id=new_tree_id,
                           parent=parent_pk)

