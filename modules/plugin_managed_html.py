# -*- coding: utf-8 -*-
# This plugins is licensed under the MIT license: http://www.opensource.org/licenses/mit-license.php
# Authors: Kenji Hosoda <hosoda@s-cubism.jp>
from gluon import *
from gluon.storage import Storage, Messages
import gluon.contrib.simplejson as json
from collections import defaultdict
import os
from plugin_uploadify_widget import (
    uploadify_widget, IS_UPLOADIFY_IMAGE, IS_UPLOADIFY_LENGTH
)

LIVE_MODE = 'live'
EDIT_MODE = 'edit'
PREVIEW_MODE = 'preview'

class ManagedHTML(object):

    def __init__(self, db, keyword='_managed_html'):
        self.db, self.keyword = db, keyword
    
        settings = self.settings = Storage()
        
        settings.upload = URL('download')
        settings.uploadfolder = os.path.join(self.db._adapter.folder, '..', 'uploads')
        
        settings.extra_fields = {}
        
        settings.table_content_name = 'managed_html_content'
        settings.table_content = None
        
        settings.table_file_name = 'managed_html_file'
        settings.table_file = None
        
        # TODO versioning
        
        messages = self.messages = Messages(current.T)
        
        self.switch_to_live_mode()
        
        self._draggables = defaultdict(list)
        
    def define_tables(self, migrate=True, fake_migrate=False):
        db, settings = self.db, self.settings
        
        if not settings.table_content_name in db.tables:
            table = db.define_table(settings.table_content_name,
                Field('name', readable=False, writable=False),
                Field('data', 'text', default=''), 
                migrate=migrate, fake_migrate=fake_migrate,
                *settings.extra_fields.get(settings.table_content_name, []))
        settings.table_content = db[settings.table_content_name]
            
        if not settings.table_file_name in db.tables:
            table = db.define_table(settings.table_file_name,
                Field('name', 'upload', autodelete=True),
                migrate=migrate, fake_migrate=fake_migrate,
                *settings.extra_fields.get(settings.table_file_name, []))
        settings.table_file = db[settings.table_file_name]
            
        
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
        
        current.response.files.append(URL('static', 'plugin_managed_html/jquery-ui-1.8.16.custom.min.js'))
        
    def _post_js(self, name, action, target):
        data = {self.keyword:name, '_action':action}
        return """managed_html_ajax_page("%(url)s", %(data)s, "%(target)s");
               """ % dict(url=URL(args=current.request.args, vars=current.request.get_vars), 
                          data=json.dumps(data), target=target)

    def _get_content(self, name):
        return self.db(self.settings.table_content.name==name).select().first()
        
    def _is_simple_form(self, fields):
        return len(fields) == 1 and fields[0].name in ('string', 'text', 'integer', 'double', 
                                                       'time', 'date', 'datetime')
        
    def render(self, name, *fields):
        request, response, session, T, settings = (
            current.request, current.response, current.session, current.T, self.settings)
        el_id = 'managed_html_block_%s' % name
        _inner_el_id = 'managed_html_inner_%s' % name
        
        def _render(func):
            def _func(content):
                if self.view_mode == EDIT_MODE:
                    response.write(XML("<div onclick='%s'>" % self._post_js(name, 'edit', _inner_el_id)))
                
                func(Storage(content and content.data and json.loads(content.data) or {}))
                
                if self.view_mode == EDIT_MODE:
                    if not content or not content.data:
                        response.write(XML('<div style="height:15px;background:whiteSmoke;">&nbsp;</div>'))
                    response.write(XML('</div>'))
                    
            def wrapper(*args, **kwds):
                if (self.keyword in request.vars and 
                        request.vars[self.keyword] == name):
                        
                    def _uploadify_widget(field, value, download_url=None, **attributes):
                        attributes['extra_vars'] = {self.keyword:name, '_action':'edit'}
                        
                        def _custom_store(file,filename,path):
                            return settings.table_file.name.store(file,filename,path)
                        field.custom_store = _custom_store
                        
                        return uploadify_widget(field, value, download_url, **attributes)
                        
                    import cStringIO
                    action = request.vars.get('_action')
                    if action == 'edit':
                        content = self._get_content(name)
                        if not content:
                            settings.table_content.insert(name=name)
                            content = self._get_content(name)
                        data = content.data and json.loads(content.data) or {}
                        virtual_record = Storage(id=0)
                        for field in fields:
                            virtual_record[field.name] = data[field.name] if field.name in data else None
                               
                            if field.type == 'upload':
                                field.uploadfolder = field.uploadfolder or settings.uploadfolder
                                field.widget = _uploadify_widget
                        form = SQLFORM(
                            DAL(None).define_table('no_table', *fields),
                            virtual_record,
                            upload=settings.upload,
                            showid=False,
                        )
                        if form.accepts(request.vars, session):
                            data = {}
                            for field in fields:
                                filename = form.vars[field.name]
                                filename.replace('no_table.image.', '%s.name.' % settings.table_file)
                                
                                data[field.name] = filename
                                if field.type == 'upload':
                                    settings.table_file.insert(name=filename)
                        
                            content.update_record(data=json.dumps(data))
                            response.flash = T('Edited')
                            response.js = 'managed_html_editing("%s", false);' % el_id
                            
                            response.body = cStringIO.StringIO()
                            _func(content)
                            raise HTTP(200, response.body.getvalue())
                            
                        if self._is_simple_form(fields):
                            form.components = [form.custom.widget[fields[0].name]]
                        form.components += [INPUT(_type='hidden', _name=self.keyword, _value=name),
                                   INPUT(_type='hidden', _name='_action', _value='edit')]
                        raise HTTP(200, form)
                    elif action == 'back':
                        content = self._get_content(name)
                        
                        response.body = cStringIO.StringIO()
                        _func(content)
                        raise HTTP(200, response.body.getvalue())
                    else:
                        raise RuntimeError
                    
                content = self._get_content(name)
                
                if self.view_mode == EDIT_MODE:
                    response.write(XML('<div id="%s" class="managed_html_block">' % el_id))
                    
                    response.write(XML("""
<div id="%s" style="min-height:15px;" class="managed_html_content">""" % _inner_el_id))
                    _func(content)
                    response.write(XML('</div>'))
                    
                    response.write(XML(DIV(DIV(
                        SPAN(INPUT(_value=T('Back'), _type='button', 
                              _onclick=self._post_js(name, 'back', _inner_el_id),
                              _class='managed_html_btn'),
                          _class='managed_html_back_btn',
                          _style='display:none;'),
                        SPAN(INPUT(_value=T('Submit'), _type='button', 
                              _onclick='jQuery("#%s"+" form").submit()' % _inner_el_id,
                              _class='managed_html_btn managed_html_primary_btn'),
                          _class='managed_html_submit_btn',
                          _style='display:none;'),
                        SPAN(SPAN(fields[0].comment, _style='white-space:nowrap;margin-right:10px;'),
                           _class='managed_html_main_comment',
                           _style='display:none;') if self._is_simple_form(fields) and fields[0].comment else '',
                        SPAN(INPUT(_value=T('Edit'), _type='button', 
                              _onclick=self._post_js(name, 'edit', _inner_el_id),
                              _class='managed_html_btn'),
                           _class='managed_html_edit_btn'),
                    ), _class='managed_html_contents_ctrl')))
                    
                    response.write(XML('</div>'))
                else:
                    response.write(XML('<div id="%s">' % el_id))
                    _func(content)
                    response.write(XML('</div>'))
                
            return wrapper
        return _render
        
    def draggable(self, name):
        request, response, session, T, settings = (
            current.request, current.response, current.session, current.T, self.settings)
        el_id = 'managed_html_block_%s' % name
        _inner_el_id = 'managed_html_inner_%s' % name
        
        def _draggable(func):
            self._draggables[name].append(func)
            def wrapper(*args, **kwds):
                if self.view_mode == EDIT_MODE:
                    response.write(XML("""
<div id="%s" class="managed_html_block managed_html_draggable managed_html_name_%s">""" % (el_id, name)))
                    self._draggables[name].pop()(*args, **kwds)
                    response.write(XML('</div>'))
                else:
                    self._draggables[name].pop()(*args, **kwds)
                
            return wrapper
        return _draggable
            
    
    # def response(self, name):
        # # TODO
        # response = current.response
        # if self.view_mode == EDIT_MODE:
            # # response.xxx = xxx
            # return SCRIPT(""" """)
        # else:
            # # response.yyy = yyy
            # return ''

