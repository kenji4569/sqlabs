# -*- coding: utf-8 -*-
# This plugins is licensed under the MIT license: http://www.opensource.org/licenses/mit-license.php
# Authors: Kenji Hosoda <hosoda@s-cubism.jp>
from gluon import *
from gluon.storage import Storage, Messages
import gluon.contrib.simplejson as json
from collections import defaultdict

LIVE_MODE = 'live'
EDIT_MODE = 'edit'
PREVIEW_MODE = 'preview'

class ManagedHTML(object):

    def __init__(self, db, keyword='_managed_html'):
        self.db, self.keyword = db, keyword
    
        settings = self.settings = Storage()
        
        settings.extra_fields = {}
        
        settings.table_content_name = 'managed_html_content'
        settings.table_content = None
        
        # TODO versioning
        
        messages = self.messages = Messages(current.T)
        
        self.switch_to_live_mode()
        
        self._sortables = defaultdict(list)
        
    def define_tables(self, migrate=True, fake_migrate=False):
        db, settings = self.db, self.settings
        
        if not settings.table_content_name in db.tables:
            table = db.define_table(settings.table_content_name,
                Field('name', unique=True, readable=False, writable=False),
                Field('data', 'text', default=''), 
                migrate=migrate, fake_migrate=fake_migrate,
                *settings.extra_fields.get(settings.table_content_name, []))
            # table.name.requires = IS_NOT_IN_DB(db, table.name)
        settings.table_content = db[settings.table_content_name]
        
    def switch_to_live_mode(self):
        self.view_mode = LIVE_MODE
        
    def switch_to_edit_mode(self):
        self.view_mode = EDIT_MODE
        self._show_navbar()
        
    def switch_to_preview_mode(self):
        self.view_mode = PREVIEW_MODE
        self._show_navbar()
        
    def _show_navbar(self):
        current.response.files.append(URL('static', 'plugin_managed_html/managed_html.css'))
        current.response.files.append(URL('static', 'plugin_managed_html/managed_html.js'))
        
    def _post_js(self, name, action, target):
        data = {self.keyword:name, 'action':action}
        return """managed_html_ajax_page('%(url)s', %(data)s, '%(target)s');
               """ % dict(url=URL(args=current.request.args, vars=current.request.get_vars), 
                          data=json.dumps(data), target=target)

    def _xml(self, represent, edit, name, wrapper):
        el_id = 'managed_html_block_%s' % name
        
        if (self.keyword in current.request.vars and 
                current.request.vars[self.keyword] == name):
            action = current.request.vars.get('action')
            if action == 'edit':
                content = self._get_content(name)
                if not content:
                    self.settings.table_content.insert(name=name)
                    content = self._get_content(name)
                form = edit(content)
                if form.accepts(current.request.vars, current.session):
                    content.data = form.vars.data
                    current.response.flash = current.T('Edited')
                    current.response.js = 'managed_html_editing("%s", false);' % el_id
                    raise HTTP(200, represent(content))
                form.components += [
                    INPUT(_type='hidden', _name=self.keyword, _value=name),
                    INPUT(_type='hidden', _name='action', _value='edit')]
                raise HTTP(200, form)
            elif action == 'back':
                content = self._get_content(name)
                raise HTTP(200, represent(content))
            else:
                raise RuntimeError
            
        content = self._get_content(name)
        el = represent(content)
        
        if self.view_mode == EDIT_MODE:
            _inner_el_id = 'managed_html_inner_%s' % name
            
            _ctrl = DIV(
                INPUT(_value=current.T('Back'), _type='button', 
                      _onclick=self._post_js(name, 'back', _inner_el_id),
                      _class='managed_html_btn managed_html_back_btn',
                      _style='display:none;'),
                INPUT(_value=current.T('Edit'), _type='button', 
                      _onclick=self._post_js(name, 'edit', _inner_el_id),
                      _class='managed_html_btn managed_html_edit_btn'),
            )
            
            return wrapper(DIV(el or '', _id=_inner_el_id), 
                           DIV(_ctrl, _class='managed_html_contents_ctrl'),
                           _class=' managed_html_block', _id=el_id)
                     
        elif not el:
            return ''
        
        return wrapper(el, _id=el_id)
        
    def _get_content(self, name):
        return self.db(self.settings.table_content.name==name).select().first()
        
    def html(self, name, wrapper=DIV, default=None):
        
        def represent(content):
            return content and XML(content.data) or default
            
        def edit(content):
            form = SQLFORM(self.settings.table_content, content, showid=False)
            return form
            
        return self._xml(represent, edit, name, wrapper)
        
    def sortable(self, name):
        def _sortable(func):
            self._sortables[name].append(func)
            def wrapper(*args, **kwds):
                self._sortables[name].pop()(*args, **kwds)
            return wrapper
        return _sortable
            
    
        
    def __call__(self, name, wrapper=None, default=None):
        el_id = 'managed_html_block_%s' % name
        contents_el_id = 'managed_html_contents_%s' % name
        
        if self.keyword in current.request.vars and current.request.vars[self.keyword] == name:
            settings = self.settings
            action = current.request.vars.get('action')
            if action == 'add_content':
                settings.table_content.insert(name=name)
                raise HTTP(200, self._render_contents(name, wrapper, default, contents_el_id))
            elif action == 'edit_content':
                content_id = current.request.vars.get('content')
                content = settings.table_content(content_id)
                form = SQLFORM(settings.table_content, content)
                raise HTTP(200, form)
            else:
                raise HTTP(404)
        else:
            contents_el = self._render_contents(name, wrapper, default, contents_el_id)
            if not contents_el:
                return ''
            contents_el.attributes['_id'] = contents_el_id
            
            inner = [contents_el]
            if self.view_mode == EDIT_MODE:
                el = DIV(contents_el,
                         DIV(self._render_edit_ctrl(name, contents_el_id),
                            _class='managed_html_contents_ctrl'),
                         _class=' managed_html_block', _id=el_id)
            else:
                el = contents_el
            if wrapper:
                el = wrapper(el)
            return el
        
    def _render_content(self, name, content, content_el_id):
        return DIV('hoge', _id=content_el_id)
        
    def _render_contents(self, name, wrapper, default, el_id):
        contents = self._get_contents(name)
        
        inner = []
        if self.view_mode == EDIT_MODE:
            default = default or XML('&nbsp;')
            for content in contents:
                content_el_id = 'managed_html_content_%s' % content.id
                content_el = self._render_content(name, content, content_el_id)
                content_el.attributes['_onclick'] = self._post_contents_js(
                            name, dict(action='edit_content',
                                       content=content.id), content_el_id)
                inner.append(DIV(content_el, _class='managed_html_content'))
        else:
            for content in contents:
                content_el_id = 'managed_html_content_%s' % content.id
                inner.append(self._render_content(name, content, content_el_id))
        
        if not inner and default is not None:
            inner.append(default)
        
        if not inner:
            return ''
        else:
            return DIV(_class='managed_html_contents_inner', *[c for c in inner])
            
    # def response(self, name):
        # # TODO
        # response = current.response
        # if self.view_mode == EDIT_MODE:
            # # response.xxx = xxx
            # return SCRIPT(""" """)
        # else:
            # # response.yyy = yyy
            # return ''

