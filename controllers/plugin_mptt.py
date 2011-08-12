'''
Created on 2011/08/12

@author: yusuke.kishita
'''

# -*- coding: utf-8 -*-
from gluon import *

db = DAL('sqlite:memory:')
db.define_table('tree', 
    Field('title'),  Field('left', 'integer'), 
    Field('right', 'integer'),
    )
db.tree.insert(title='Food',left=1,right=2)

def add_node(title,parent_title):
    """
    add_node('Fruit','Food')
    add_node('Meat','Food')
    add_node('Red','Food')
    """
    parent = db(db.tree.title == parent_title).select()[0]
    db(db.tree.right >= parent.right).update(right = db.tree.right+2)
    db(db.tree.left >= parent.right).update(left = db.tree.left+2)
    db.tree.insert(title = title, left = parent.right, right = parent.right + 1)
    
def ancestors(title, *fields):
    """print ancestors('Red', db.tree.title)"""
    node = db(db.tree.title == title).select()[0]
    return db(db.tree.left < node.left)(db.tree.right > node.right).select(orderby = db.tree.left, *fields)  
    
def descendants(title, *fields):
    """print descendants('Fruit', db.tree.title)"""
    node = db(db.tree.title == title).select()[0]
    return db(db.tree.left > node.left)(db.tree.right < node.right).select(orderby=db.tree.left, *fields)

def test():
    print db().select(db.tree.ALL)
    add_node('Fruit', 'Food')
    print db().select(db.tree.ALL)
    add_node('Meat', 'Food')
    print db().select(db.tree.ALL)
    add_node('Red', 'Food')
    print db().select(db.tree.ALL)
    print ancestors('Red', db.tree.title)
    print descendants('Fruit', db.tree.title)
    
test()