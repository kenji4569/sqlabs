# -*- coding: utf-8 -*-
# This plugins is licensed under the MIT license: http://www.opensource.org/licenses/mit-license.php
# Authors: Yusuke Kishita <yuusuuke.kishiita@gmail.com>, Kenji Hosoda <hosoda@s-cubism.jp>
from gluon import *
from gluon.storage import Storage

class JsTree(object):
    
    def __init__(self, tree_model, renderstyle=False):
        self.tree_model = tree_model # tree_model could be an MPTT object of plugin_mptt
        
        _urls = [URL('static', 'plugin_jstree/jstree/jquery.hotkeys.js'),
                 URL('static', 'plugin_jstree/jstree/jquery.jstree.js')]
        if renderstyle:
            _urls.append(URL('static', 'plugin_jstree/main.css'))
        for _url in _urls:
            if _url not in current.response.files:
                current.response.files.append(_url)
        
    def recordbutton(self, buttonclass, buttontext, buttonurl, showbuttontext=True, **attr):
        if showbuttontext:
            inner = SPAN(buttontext, _class='ui-button-text') 
        else:
            inner = SPAN(XML('&nbsp'), _style='padding: 0px 7px 0px 6px;')
        return A(SPAN(_class='ui-icon ' + buttonclass), 
                 inner, 
                 _title=buttontext, _href=buttonurl, _class='ui-btn', **attr)

    def build_tree_objects(self, initially_select):
        initially_open=[]
        data = []
        
        for child in self.tree_model.descendants_from_node(initially_select, include_self=True
                                                           ).select(orderby=self.tree_model.desc):
            node_el_id = 'node_%s' % child.id
            if not self.tree_model.is_leaf_node(child):
                initially_open.append(node_el_id)
            
            if child.level == 0:
                data.append(dict(data=child.name, 
                             attr=dict(id=node_el_id, rel=child.node_type),
                             children=[],
                             ))        
            elif child.level >= 1:        
                _data = data[:]
                for depth in range(child.level):
                    _data = _data[-1]['children']
                
                _data.append(dict(data=child.name, 
                                 attr=dict(id=node_el_id, rel=child.node_type),
                                 children=[],
                                 ))
        return data, initially_open

    def render_tree_crud_buttons(self):
        T = current.T
        ui = dict(buttonadd='ui-icon-plusthick',
                  buttondelete='ui-icon-close',
                  buttonedit='ui-icon-pencil')
        return DIV(
            A('x', _class='close', _href='#', _onclick='jQuery(this).parent().hide();'),
            self.recordbutton('%(buttonadd)s' % ui, T('Add'), '#', False, _id='add_node_button'), 
            self.recordbutton('%(buttonedit)s' % ui, T('Edit'),'#', False, _id='edit_node_button'),
            self.recordbutton('%(buttondelete)s' % ui, T('Delete'),'#', False, _id='delete_node_button'),
            _id='tree_crud_buttons', _style='display:none;position:absolute;',
            _class='tree_crud_button alert-message info',
        )

    def __call__(self, 
                 args=[],
                 user_signature=True, 
                 hmac_key=None, 
                 ):
        request = current.request
        response = current.response
        
        def url(**b):
            b['args'] = args + b.get('args',[])
            b['user_signature'] = user_signature
            b['hmac_key'] = hmac_key
            return URL(**b)
        
        def check_authorization():
            if not URL.verify(request, user_signature=user_signature, hmac_key=hmac_key):
                raise HTTP(403)
                
        action = request.args and request.args[-1]     
      
        if action=='new':
            check_authorization()
            vars = request.post_vars
            if not vars.name or vars.name == '---':
                raise HTTP(406)
            node_id = self.tree_model.insert_node(vars.target, name=vars.name)
            raise HTTP(200, node_id)
            
        elif action=='edit':
            check_authorization()
            vars = request.post_vars
            if not vars.name or vars.name == '---':
                raise HTTP(406)
            node = self.tree_model.get_node(vars.id)
            if not node:
                raise HTTP(404)
            if node.name == vars.name:
                raise HTTP(406)
            node.update_record(name=vars.name)
            raise HTTP(200)
            
        elif action=='delete':
            check_authorization()
            vars = request.post_vars
            node = self.tree_model.get_node(vars.id)
            if not self.tree_model.is_leaf_node(node) or not node:
                raise HTTP(404)
            self.tree_model.delete_node(node)
            raise HTTP(200)
            
        elif action=='move':
            check_authorization()
            vars = request.post_vars
            node = self.tree_model.get_node(vars.id)
            if self.tree_model.is_root_node(node):
                raise HTTP(406)
            
            parent_node = self.tree_model.get_node(vars.parent)
            position = int(vars.position)
            
            target_child = self.tree_model.get_first_child(parent_node)
            if target_child:
                tmp = None
                end_flag = False
                for i in range(position):
                    tmp = self.tree_model.get_next_sibling(target_child)
                    if tmp is False:
                        self.tree_model.move_node(node,target_child,'right')
                        end_flag = True
                    target_child = tmp
                if end_flag is False:  
                    self.tree_model.move_node(node,target_child,'left')
            else:
                self.tree_model.move_node(node,parent_node)
            raise HTTP(200)

        root_nodes = self.tree_model.roots().select()
        data = []
        initially_open = []
        for i, root_node in enumerate(root_nodes):
            _data, _initially_open = self.build_tree_objects(root_node)
            data.append(_data)
            initially_open += _initially_open
        
        from gluon.utils import web2py_uuid
        element_id = web2py_uuid()
        return XML(response.render('plugin_jstree/block.html',
                                   dict(url=url, data=data,
                                        initially_open=initially_open,
                                        tree_crud_buttons=self.render_tree_crud_buttons(),
                                        element_id=element_id)))
                        