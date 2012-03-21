# -*- coding: utf-8 -*-

from plugin_jstree import JsTree
from plugin_mptt import MPTT
import datetime

### setup core objects #########################################################
mptt = MPTT(db)
mptt.settings.table_node_name = 'plugin_mptt_node'
mptt.settings.extra_fields = {
    'plugin_mptt_node':
        [Field('name'),
         Field('node_type'),
         Field('created_on', 'datetime', default=request.now)],
}

### inject the mptt tree model to the jstree plugin ###
jstree = JsTree(tree_model=mptt, renderstyle=True)

### define tables ##############################################################'
mptt.define_tables()
table_node = mptt.settings.table_node

### populate records ###########################################################
deleted = db(table_node.created_on < request.now - datetime.timedelta(minutes=30)).delete()
if deleted:
    table_node.truncate()
    session.flash = 'the database has been refreshed'
    redirect(URL('index'))

if not mptt.roots().count():
    _root1 = mptt.insert_node(None, name='root1', node_type='root')
    _child1 = mptt.insert_node(_root1, name='child1')
    mptt.insert_node(_root1, name='child2')
    mptt.insert_node(_child1, name='grandchild1')
    mptt.insert_node(None, name='root2', node_type='root')

### fake authentication ########################################################

from gluon.storage import Storage
session.auth = Storage(hmac_key='test', user=Storage(email='user@test.com'))


### demo functions #############################################################

def index():
    return dict(tree_block=DIV(jstree(), _style='width:500px;'))
