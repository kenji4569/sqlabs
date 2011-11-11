# -*- coding: utf-8 -*-
# This plugins is licensed under the MIT license: http://www.opensource.org/licenses/mit-license.php
# Authors: Kenji Hosoda <hosoda@s-cubism.jp>
from gluon import *
from gluon.storage import Storage, Messages
import gluon.contrib.simplejson as json
import os
from plugin_uploadify_widget import (
    uploadify_widget, IS_UPLOADIFY_IMAGE, IS_UPLOADIFY_LENGTH
)

class ManagedHTML(object):

    LIVE_MODE = '_managed_html_live'
    EDIT_MODE = '_managed_html_edit'
    PREVIEW_MODE = '_managed_html_preview'

    def __init__(self, db, keyword='_managed_html'):
        self.db, self.keyword = db, keyword
    
        settings = self.settings = Storage()
        
        settings.URL = URL
        
        settings.upload = URL('download')
        settings.uploadfolder = os.path.join(self.db._adapter.folder, '..', 'uploads')
        
        settings.home_url = '/'
        settings.home_label = 'Home'
        
        settings.extra_fields = {}
        
        settings.table_content_name = 'managed_html_content'
        settings.table_content = None
        
        settings.table_file_name = 'managed_html_file'
        settings.table_file = None
        
        # TODO versioning
        
        messages = self.messages = Messages(current.T)
        
        self.view_mode = self.LIVE_MODE
        
    def url(self, a=None, c=None, f=None, r=None, args=None, vars=None, **kwds):
        if not r:
            if a and not c and not f: (f,a,c)=(a,c,f)
            elif a and c and not f: (c,f,a)=(a,c,f)
        if c != 'static':
            mode = current.request.args(0)
            if mode in (self.EDIT_MODE, self.PREVIEW_MODE):
                return self._mode_url(mode, a, c, f, r, args, vars, **kwds)
        return self.settings.URL(a, c, f, r, args, vars, **kwds)
        
    def _mode_url(self, mode, a=None, c=None, f=None, r=None, args=None, vars=None, **kwds):
        if args in (None,[]): 
            args = [mode]
        elif not isinstance(args, (list, tuple)):
            args = [mode, args]
        else:
            args = [mode] + args
        return self.settings.URL(a, c, f, r, args=args, vars=vars, **kwds)
        
    def edit_url(self, a=None, c=None, f=None, r=None, args=None, vars=None, **kwds):
        return self._mode_url(self.EDIT_MODE, a, c, f, r, args, vars, **kwds)
    
    def preview_url(self, a=None, c=None, f=None, r=None, args=None, vars=None, **kwds):
        return self._mode_url(self.PREVIEW_MODE, a, c, f, r, args, vars, **kwds)
    
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
            
    def switch_mode(self):
        settings, request, response = self.settings, current.request, current.response
        self.view_mode = request.args(0)
        if self.view_mode not in (self.EDIT_MODE, self.PREVIEW_MODE):
            self.view_mode = self.LIVE_MODE
            return
            
        response.files.append(URL('static', 'plugin_managed_html/managed_html.css'))
        response.files.append(URL('static', 'plugin_managed_html/managed_html.js'))
        response.files.append(URL('static', 'plugin_managed_html/jquery-ui-1.8.16.custom.min.js'))
        
        response.meta.managed_html_home_url = settings.home_url
        response.meta.managed_html_home_label = settings.home_label
        
        response.meta.managed_html_live_url = settings.URL(args=request.args[1:], vars=request.vars)
        
        if self.view_mode == self.EDIT_MODE:
            response.meta.managed_html_preview_url = settings.URL(
                args=[self.PREVIEW_MODE]+request.args[1:], vars=request.vars)
        elif self.view_mode == self.PREVIEW_MODE:
            response.meta.managed_html_edit_url = settings.URL(
                args=[self.EDIT_MODE]+request.args[1:], vars=request.vars)
            
        
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
        inner_el_id = 'managed_html_inner_%s' % name
        
        def _render(func):
            def _func(content):
                if self.view_mode == self.EDIT_MODE:
                    response.write(XML("<div onclick='%s'>" % self._post_js(name, 'edit', inner_el_id)))
                
                if content and content.data:
                    func(Storage(content and content.data and json.loads(content.data) or {}))
                
                if self.view_mode == self.EDIT_MODE:
                    if not content or not content.data:
                        response.write(XML('<div style="height:15px;background:whiteSmoke;">&nbsp;</div>'))
                    response.write(XML('</div>'))
                    
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
                
                    
            def wrapper(*args, **kwds):
                content = self._get_content(name)
                
                if self.view_mode == self.EDIT_MODE:
                    response.write(XML('<div id="%s" class="managed_html_block">' % el_id))
                    
                    response.write(XML("""
<div id="%s" style="min-height:15px;" class="managed_html_content">""" % inner_el_id))
                    _func(content)
                    response.write(XML('</div>'))
                    
                    response.write(XML(DIV(DIV(
                        SPAN(INPUT(_value=T('Back'), _type='button', 
                              _onclick=self._post_js(name, 'back', inner_el_id),
                              _class='managed_html_btn'),
                          _class='managed_html_back_btn',
                          _style='display:none;'),
                        SPAN(INPUT(_value=T('Submit'), _type='button', 
                              _onclick='jQuery("#%s"+" form").submit()' % inner_el_id,
                              _class='managed_html_btn managed_html_primary_btn'),
                          _class='managed_html_submit_btn',
                          _style='display:none;'),
                        SPAN(SPAN(fields[0].comment, _style='white-space:nowrap;margin-right:10px;'),
                           _class='managed_html_main_comment',
                           _style='display:none;') if self._is_simple_form(fields) and fields[0].comment else '',
                        SPAN(INPUT(_value=T('Edit'), _type='button', 
                              _onclick=self._post_js(name, 'edit', inner_el_id),
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
        
    def movable(self, name):
        if not hasattr(self, '_movables'):
            from collections import defaultdict
            self._movables = defaultdict(list)
            self._movable_indices = defaultdict(int)
            self._movable_loaded = {}
    
        request, response, session, T, settings = (
            current.request, current.response, current.session, current.T, self.settings)

        if (self.keyword in request.vars and 
                request.vars[self.keyword] == name):
            action = request.vars.get('_action')
            if action == 'permute':
                content = self._get_content(name)
                if not content:
                    settings.table_content.insert(name=name)
                    content = self._get_content(name)
                    
                indices = request.vars.get('indices[]', [])
                from_idx = request.vars.get('from')
                to_idx = request.vars.get('to')
                arg_from = indices.index(from_idx)
                arg_to = indices.index(to_idx)
                indices[arg_from] = to_idx
                indices[arg_to] = from_idx
                content.update_record(data=json.dumps(indices))
                
                response.flash = T('Moved')
                
                raise HTTP(200, json.dumps(indices))
            
        def _movable(func):
            self._movables[name].append((len(self._movables[name]), func))
                
            def wrapper(*args, **kwds):
                if not self._movable_loaded.get(name):
                    content = self._get_content(name)
                    if content and content.data:
                        indices = json.loads(content.data)
                        permutation = range(len(self._movables[name]))
                        try:
                            indices = map(int, indices)
                            permutation[:len(indices)] = indices
                        except ValueError:
                            pass
                        print permutation
                        self._movables[name] = [self._movables[name][i] for i in permutation]
                    
                    if self.view_mode == self.EDIT_MODE:
                        response.write(XML("""
<script>jQuery(function(){managed_html_movable("%s", [%s], "%s", "%s")})</script>""" % 
                            (name, ','.join([str(i) for i, f in self._movables[name]]),
                             self.keyword, URL(args=current.request.args, vars=current.request.get_vars))))
                    self._movable_loaded[name] = True
                    
                _block_index, _func = self._movables[name].pop(0)
                
                if self.view_mode == self.EDIT_MODE:
                    el_id = 'managed_html_block_%s_%s' % (name, _block_index)
                    inner_el_id = 'managed_html_inner_%s_%s' % (name, _block_index)
                    
                    response.write(XML('<div id="%s" class="managed_html_block">'% el_id))
                    
                    response.write(XML("""
<div id="%s" class="managed_html_movable managed_html_name_%s">""" % 
                        (inner_el_id, name)))
                    
                    _func(*args, **kwds)
                    
                    response.write(XML('</div>'))
                    response.write(XML('</div>'))
                else:
                    _func(*args, **kwds)
                
            return wrapper
        return _movable
            
    
    # def response(self, name):
        # # TODO
        # response = current.response
        # if self.view_mode == self.EDIT_MODE:
            # # response.xxx = xxx
            # return SCRIPT(""" """)
        # else:
            # # response.yyy = yyy
            # return ''

