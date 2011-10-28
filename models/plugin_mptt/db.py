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

 if not category_tree.roots().count():
    category_tree.insert_node(None, name='master', node_type='root')
        
### helper functions ##########################################################

def build_tree_objects(initially_select):

    initially_open = []
    def _traverse(node):
        node_el_id = 'category_%s' % node.id
        children = []
        if not category_tree.is_leaf_node(node):
            initially_open.append(node_el_id)
            for child in category_tree.descendants_from_node(node)(
                            table_category.level==node.level+1).select(orderby=category_tree.desc):
                children.append(_traverse(child))
        return dict(data=node.name, 
                    attr=dict(id=node_el_id, rel=node.node_type),
                    children=children,
                    )
    data = [_traverse(initially_select)]
    return data, initially_open
    
def render_tree_crud_buttons(tablename):
    ui = dict(buttonadd='ui-icon-plusthick',
              buttondelete='ui-icon-close',
              buttonedit='ui-icon-pencil')
    return DIV(
        A('x', _class='close', _href='#', _onclick='jQuery(this).parent().hide();'),
        SOLIDFORM.recordbutton('%(buttonadd)s' % ui, T('Add'), '#', False, _id='add_node_button'), 
        SOLIDFORM.recordbutton('%(buttonedit)s' % ui, T('Edit'),'#', False, _id='edit_node_button'),
        SOLIDFORM.recordbutton('%(buttondelete)s' % ui, T('Delete'),'#', False, _id='delete_node_button'),
        _id='tree_crud_buttons', _style='display:none;position:absolute;',
        _class='tree_crud_button alert-message info',
    )

# def build_flatten_nodes(root_node):
    # # TODO include mptt
    # flatten_nodes = []
    # def _traverse(node, ancestors=None):
        # ancestors = ancestors or []
        # for child in category_tree.descendants_from_node(node)(
                            # table_category.level==node.level+1).select(orderby=category_tree.desc):
            # self_and_ancestors = ancestors + [child] 
            # if not category_tree.is_leaf_node(child):
                # _traverse(child, self_and_ancestors)
            # flatten_nodes.append(self_and_ancestors)
    # _traverse(root_node)
    # return flatten_nodes
    
def get_root_node():
    # TODO for multitetant
    return category_tree.roots().select().first()
    