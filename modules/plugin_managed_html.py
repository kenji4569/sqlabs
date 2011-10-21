# -*- coding: utf-8 -*-
# This plugins is licensed under the MIT license: http://www.opensource.org/licenses/mit-license.php
# Authors: Kenji Hosoda <hosoda@s-cubism.jp>
from gluon import *
from gluon.storage import Storage, Messages

LIVE_MODE = 'live'
EDIT_MODE = 'edit'
PREVIEW_MODE = 'preview'

HTML_TYPE = 'html'
# TODO
# TEXT_TYPE = 'text'
# MENU_TYPE = 'menu'
# IMAGE_TYPE = 'image'

class ManagedHTML(object):

    def __init__(self, db):
        self.db = db
        
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
                Field('name', unique=True),
                Field('data_type'), 
                Field('data', 'text'), 
                Field('active', 'boolean', default=False), 
                migrate=migrate, fake_migrate=fake_migrate,
                *settings.extra_fields.get(settings.table_content_name, []))
            table.name.requires = IS_NOT_IN_DB(db, table.name)
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
        
    def _get_contents(self, name, active=None):
        table_content  = self.settings.table_content
        dataset = self.db(table_content.name==name)
        if active is not None:
            dataset = dataset(table_content.active==active)
        return dataset.select()
        
    def __call__(self, name=None, wrapper=None, default=None):
        # TODO db access, setting element ids, setting class
        settings = self.settings
        contents = None
        if name:
            active = (self.view_mode == LIVE_MODE) or None
            contents = self._get_contents(name, active)
            
            if self.view_mode == EDIT_MODE:
                pass
                #contents =
                #contents = DIV()
            elif self.view_mode == PREVIEW_MODE:
                pass
                #contents = DIV()
          
        if not contents and default is not None:
            contents = [default]
            
        if contents:
            contents = DIV(
                DIV(DIV(
                    INPUT(_value='Add', _type='button', _class='managed_html_btn')),
                   _class='managed_html_tabs'),
                DIV(_class='managed_html_content_inner', *[c for c in contents]),
                _class='managed_html_content')
        
            if wrapper:
                contents = wrapper(contents)
        else:
            contents = ''
            
        return contents
        
    def response(self, name):
        # TODO
        response = current.response
        if self.view_mode == EDIT_MODE:
            # response.xxx = xxx
            return SCRIPT(""" """)
        else:
            # response.yyy = yyy
            return ''

