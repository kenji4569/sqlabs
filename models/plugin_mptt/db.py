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
         Field('node_type'),
         Field('created_on', 'datetime', default=request.now)],
}

### define tables ##############################################################'
mptt.define_tables()
table_node = mptt.settings.table_node

### populate records ###########################################################
deleted = db(table_node.created_on<request.now-datetime.timedelta(minutes=10)).delete()
if deleted:
    table_node.truncate()
    session.flash = 'the database has been refreshed'
    redirect(URL('index'))

if not mptt.roots().count():
    mptt.insert_node(None, name='master', node_type='root')
        
### helper functions ##########################################################

def recordbutton(buttonclass, buttontext, buttonurl, showbuttontext=True, **attr):
    if showbuttontext:
        inner = SPAN(buttontext, _class='ui-button-text') 
    else:
        inner = SPAN(XML('&nbsp'), _style='padding:6px;')
    return A(SPAN(_class='ui-icon ' + buttonclass), 
             inner, 
             _title=buttontext, _href=buttonurl, _class='ui-btn', **attr)
    
def build_tree_objects(initially_select):
    initially_open = []
    def _traverse(node):
        node_el_id = 'node_%s' % node.id
        children = []
        if not mptt.is_leaf_node(node):
            initially_open.append(node_el_id)
            for child in mptt.descendants_from_node(node)(
                            table_node.level==node.level+1).select(orderby=mptt.desc):
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
        recordbutton('%(buttonadd)s' % ui, T('Add'), '#', False, _id='add_node_button'), 
        recordbutton('%(buttonedit)s' % ui, T('Edit'),'#', False, _id='edit_node_button'),
        recordbutton('%(buttondelete)s' % ui, T('Delete'),'#', False, _id='delete_node_button'),
        _id='tree_crud_buttons', _style='display:none;position:absolute;',
        _class='tree_crud_button alert-message info',
    )

# def build_flatten_nodes(root_node):
    # # TODO include mptt
    # flatten_nodes = []
    # def _traverse(node, ancestors=None):
        # ancestors = ancestors or []
        # for child in mptt.descendants_from_node(node)(
                            # table_category.level==node.level+1).select(orderby=mptt.desc):
            # self_and_ancestors = ancestors + [child] 
            # if not mptt.is_leaf_node(child):
                # _traverse(child, self_and_ancestors)
            # flatten_nodes.append(self_and_ancestors)
    # _traverse(root_node)
    # return flatten_nodes
    
def get_root_node():
    # TODO for multitetant
    return mptt.roots().select().first()