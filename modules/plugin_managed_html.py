# -*- coding: utf-8 -*-
# This plugins is licensed under the MIT license: http://www.opensource.org/licenses/mit-license.php
# Authors: Kenji Hosoda <hosoda@s-cubism.jp>
from gluon import *
from gluon.storage import Storage, Messages
import gluon.contrib.simplejson as json

LIVE_MODE = 'live'
EDIT_MODE = 'edit'
PREVIEW_MODE = 'preview'

HTML_TYPE = 'html'
# TODO
# TEXT_TYPE = 'text'
# MENU_TYPE = 'menu'
# IMAGE_TYPE = 'image'

class ManagedHTML(object):

    def __init__(self, db, keyword='_managed_html'):
        self.db, self.keyword = db, keyword
    
        settings = self.settings = Storage()
        
        settings.extra_fields = {}
        
        settings.table_content_name = 'managed_html_content'
        settings.table_content = None
        
        settings.table_response_name = 'managed_html_response'
        settings.table_response = None
        
        # TODO versioning
        
        messages = self.messages = Messages(current.T)
        
        self.switch_to_live_mode()
        
    def define_tables(self, migrate=True, fake_migrate=False):
        db, settings = self.db, self.settings
        
        if not settings.table_content_name in db.tables:
            table = db.define_table(
                settings.table_content_name,
                Field('name'),
                Field('data_type', default=HTML_TYPE), 
                Field('data', 'text', default=''), 
                Field('active', 'boolean', default=False), 
                migrate=migrate, fake_migrate=fake_migrate,
                *settings.extra_fields.get(settings.table_content_name, []))
            table.name.requires = IS_NOT_IN_DB(db, table.name)
        settings.table_content = db[settings.table_content_name]
        
        if not settings.table_response_name in db.tables:
            table = db.define_table(
                settings.table_response_name,
                Field('name'),
                migrate=migrate, fake_migrate=fake_migrate,
                *settings.extra_fields.get(settings.table_response_name, []))
            table.name.requires = IS_NOT_IN_DB(db, table.name)
        settings.table_response = db[settings.table_response_name]
        
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
        
    def _get_contents(self, name, active=None):
        table_content  = self.settings.table_content
        dataset = self.db(table_content.name==name)
        if active is not None:
            dataset = dataset(table_content.active==active)
        return dataset.select()
        
    def _post_contents_js(self, name, data, target):
        url = URL(args=current.request.args, vars=current.request.get_vars)
        data[self.keyword] = name
        return """
managed_html_ajax_page('%(url)s', %(data)s, '%(target)s');
""" % dict(url=url, data=json.dumps(data), target=target)

    def _render_edit_ctrl(self, name, contents_el_id):
        return DIV(INPUT(_value=current.T('Add'), _type='button', 
                  _onclick=self._post_contents_js(
                            name, dict(action='add_content'), contents_el_id),
                  _class='managed_html_btn'))
        
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
        active = (self.view_mode == LIVE_MODE) or None
        
        contents = self._get_contents(name, active)
        
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
            
    def response(self, name):
        # TODO
        response = current.response
        if self.view_mode == EDIT_MODE:
            # response.xxx = xxx
            return SCRIPT(""" """)
        else:
            # response.yyy = yyy
            return ''

