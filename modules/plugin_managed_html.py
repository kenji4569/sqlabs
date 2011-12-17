# -*- coding: utf-8 -*-
# This plugins is licensed under the MIT license: http://www.opensource.org/licenses/mit-license.php
# Authors: Kenji Hosoda <hosoda@s-cubism.jp>
from gluon import *
from gluon.storage import Storage, Messages
import gluon.contrib.simplejson as json
import os

LIVE_MODE = '_managed_html_live'
EDIT_MODE = '_managed_html_edit'
PREVIEW_MODE = '_managed_html_preview'

class ManagedHTML(object):

    def __init__(self, db, keyword='_managed_html'):
        self.db, self.keyword = db, keyword
    
        settings = self.settings = Storage()
        
        settings.URL = URL
        
        settings.home_url = '/'
        settings.home_label = 'Home'
        
        settings.page_crud = ''
        settings.image_crud = ''
        settings.file_crud = ''
        
        settings.table_content_name = 'managed_html_content'
        settings.table_content = None
        
        settings.table_image_name = 'managed_html_image'
        settings.table_image = None
        
        settings.extra_fields = {}
        
        settings.text_widget = None
        # settings.upload_widget = None
        
        settings.text_widget_cssfiles = [] # ex) [URL('static', 'css/base.css')]
        
        settings.uploadfolder = os.path.join(self.db._adapter.folder, '..', 'uploads')
        settings.upload = lambda filename: URL('download', args=[filename]) # TODO
        
        messages = self.messages = Messages(current.T)
        
        self.view_mode = LIVE_MODE
        
    def url(self, a=None, c=None, f=None, r=None, args=None, vars=None, **kwds):
        if not r:
            if a and not c and not f: (f,a,c)=(a,c,f)
            elif a and c and not f: (c,f,a)=(a,c,f)
        if c != 'static':
            mode = current.request.args(0)
            if mode in (EDIT_MODE, PREVIEW_MODE):
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
        return self._mode_url(EDIT_MODE, a, c, f, r, args, vars, **kwds)
    
    def preview_url(self, a=None, c=None, f=None, r=None, args=None, vars=None, **kwds):
        return self._mode_url(PREVIEW_MODE, a, c, f, r, args, vars, **kwds)
    
    def define_tables(self, migrate=True, fake_migrate=False):
        db, settings = self.db, self.settings
        
        if not settings.table_content_name in db.tables:
            table = db.define_table(settings.table_content_name,
                Field('name', readable=False, writable=False),
                Field('publish_on', 'datetime', readable=False, writable=False),
                Field('data', 'text', default=''), 
                migrate=migrate, fake_migrate=fake_migrate,
                *settings.extra_fields.get(settings.table_content_name, []))
        settings.table_content = db[settings.table_content_name]
            
        if not settings.table_image_name in db.tables:
            table = db.define_table(settings.table_image_name,
                Field('name', 'upload', autodelete=True),
                # Field('original_name'),
                Field('keyword'),
                Field('description', 'text'),
                Field('extension', length=16, readable=False, writable=False),
                Field('thumbnail', 'upload', autodelete=True, readable=False, writable=False),
                migrate=migrate, fake_migrate=fake_migrate,
                *settings.extra_fields.get(settings.table_image_name, []))
        settings.table_image = db[settings.table_image_name]
            
    def switch_mode(self):
        settings, request, response = self.settings, current.request, current.response
        self.view_mode = request.args(0)
        if self.view_mode not in (EDIT_MODE, PREVIEW_MODE):
            self.view_mode = LIVE_MODE
            return
           
        response.files.append(URL('static', 'plugin_managed_html/managed_html.css'))
        response.files.append(URL('static', 'plugin_managed_html/managed_html.js'))
        response.files.append(URL('static', 'plugin_managed_html/jquery-ui-1.8.16.custom.min.js'))
        
        response.meta.managed_html_home_url = settings.home_url
        response.meta.managed_html_home_label = settings.home_label
        
        response.meta.managed_html_live_url = settings.URL(args=request.args[1:], vars=request.vars, scheme='http')
        
        if self.view_mode in (EDIT_MODE, PREVIEW_MODE):
            if self.view_mode == EDIT_MODE:
                response.meta.managed_html_preview_url = settings.URL(
                    args=[PREVIEW_MODE]+request.args[1:], vars=request.vars)
            elif self.view_mode == PREVIEW_MODE:
                response.meta.managed_html_edit_url = settings.URL(
                    args=[EDIT_MODE]+request.args[1:], vars=request.vars)
            
            from plugin_dialog import DIALOG
            T = current.T
            response.meta.managed_html_show_page_crud = DIALOG(
                title=T('+ Page'), close_button=T('close'), renderstyle=True,
                content=settings.page_crud).show()
        
    def _post_js(self, name, action, target):
        data = {self.keyword:name, '_action':action}
        return """managed_html_ajax_page("%(url)s", %(data)s, "%(target)s");
               """ % dict(url=URL(args=current.request.args, vars=current.request.get_vars), 
                          data=json.dumps(data), target=target)

    def _get_content(self, name, cache=None):
        table_content = self.settings.table_content
        query = (table_content.name==name)
        if self.view_mode == LIVE_MODE:
            return self.db(query)(table_content.publish_on<=current.request.now
                                 ).select(orderby=~table_content.publish_on, cache=cache).first()
        else:
            return self.db(query).select(orderby=~table_content.id).first()
        
    def _is_simple_form(self, fields):
        return len(fields) == 1
        
    def _get_elrte_widget(self):
        T = current.T
        try:
            lang = T.accepted_language.split('-')[0].replace('ja', 'jp')
        except:
            lang = 'en'
        
        from plugin_dialog import DIALOG
        image_chooser = DIALOG(title=T('Select an image'), close_button=T('close'),
                               content=self.settings.image_crud)
        file_chooser = DIALOG(title=T('Select a file'), close_button=T('close'),
                              content=self.settings.file_crud, ajax=True)
                              
        fm_open = """function(callback, kind) {
if (kind == 'elfinder') {%s;} else {%s;}
jQuery(document.body).bind('managed_html_file_selected managed_html_image_selected', function(e, filename) {
    callback('%s'.replace('__filename__', filename)); jQuery('.dialog').hide(); 
});
}""" % (file_chooser.show(), image_chooser.show(), self.settings.upload('__filename__')) # TODO setting for managed_html_file_selected

        from plugin_elrte_widget import ElrteWidget
        widget =  ElrteWidget(lang=lang, cssfiles=self.settings.text_widget_cssfiles,
                              fm_open=fm_open)
        
        _files = [URL('static','plugin_elrte_widget/css/elrte.min.css'),
                 URL('static','plugin_elrte_widget/css/elrte-inner.css'),
                 URL('static','plugin_elrte_widget/css/smoothness/jquery-ui-1.8.13.custom.css'),
                 # URL('static','plugin_elrte_widget/js/jquery-ui-1.8.13.custom.min.js'), # do not use elrte's jquery-ui
                 URL('static','plugin_elrte_widget/js/elrte.min.js')]
        if lang:
            _files.append(URL('static','plugin_elrte_widget/js/i18n/elrte.%s.js' % lang))  
        
        widget.settings.files = _files
        return widget
        
    def file_represent(self, filename, nx=80, ny=80):
        if not filename:
            return A('', _href='#')
        extension = filename.split('.')[-1].lower()
        return A(IMG(_src=self.settings.upload(filename), _style='max-width:%spx;max-height:%spx;' % (nx, ny)) # TODO setting
                        if extension in ('png', 'jpg', 'jpeg', 'gif', 'bmp') else 'file',
                      _href=self.settings.upload(filename), _target='_blank')
        
    def get_thumbnail(self, filename):
        root, ext = os.path.splitext(filename)
        return '%s_thumbnail%s' % (root, ext)
        
    def oncreate_image(self, form):
        request = current.request
        if 'filename' in request.vars.name:
            filename = request.vars.name.filename
            
            if filename and filename.split('.')[-1].lower() in ('png', 'jpg', 'jpeg', 'gif', 'bmp'):
                # (nx, ny) = 80, 80 # TODO setting
                # from PIL import Image
                # img = Image.open(os.path.join(self.settings.uploadfolder, filename))
                
                # # print img.size # TODO
                
                # img.thumbnail((nx, ny), Image.ANTIALIAS)
                # thumbnail = self.get_thumbnail(filename)
                # img.save(os.path.join(self.settings.uploadfolder, thumbnail))
                thumbnail = filename
                
                extension = filename and filename.split('.')[-1]
                extension = extension and extension.lower()
                self.db(self.settings.table_image.id==form.vars.id).update(
                    name=filename, extension=extension, thumbnail=thumbnail,
                )
        
    #def get_uploadify_widget(self, name):
        # def _uploadify_widget(field, value, download_url=None, **attributes):
            # settings = self.settings
            # attributes['extra_vars'] = {self.keyword:name, '_action':'edit'}
            
            # def _custom_store(file,filename,path):
                # return settings.table_image.name.store(file,filename,path)
            # field.custom_store = _custom_store
            
            # if not settings.upload_widget:       
                # from plugin_uploadify_widget import (
                    # uploadify_widget, IS_UPLOADIFY_IMAGE, IS_UPLOADIFY_LENGTH
                # )
                # settings.upload_widget = uploadify_widget

            # return settings.upload_widget(field, value, download_url, **attributes)
        # return _uploadify_widget
            
    def image_widget(self, field, value, download_url=None, **attributes):
        T = current.T
        el_id = '%s_%s' % (field._tablename, field.name)
        
        from plugin_dialog import DIALOG
        image_chooser = DIALOG(title=T('Select an image'), close_button=T('close'),
                               content=self.settings.image_crud,
                               onclose="""
jQuery(document.body).trigger("managed_html_file_selected", "");""",
                               _id='managed_html_file_chooser')
               
        from gluon.sqlhtml import UploadWidget
        return DIV(INPUT(_type='button', _value='Select', 
                         _onclick="""
jQuery(document.body).one('managed_html_file_selected', function(e, filename) {
if(filename!="") {
    var url = "%(upload)s".replace('__filename__', filename);
    jQuery("#%(id)s__hidden").attr('value', filename);
    var ext = filename.split('.').slice(-1);
    var a = jQuery("#%(id)s__file a");
    a.attr('href', url);
    if (ext=='png' || ext=='jpg' || ext=='jpeg' || ext=='gif'|| ext=='bmp') {
        a.html("<img src='"+url+"' style='max-width:150px;max-height:150px;'/>");
    } else {
        a.html("file");
    }
    jQuery('.dialog').hide();
}
}); %(show)s; return false;""" % dict(id=el_id, show=image_chooser.show(),
                                  upload=self.settings.upload('__filename__'))), 
                   DIV(self.file_represent(value, 150, 150), _id='%s__file' % el_id, _style='margin-top:5px;'),
                   DIV(INPUT(_type='checkbox', _onclick="""
if(this.checked) {
    if(!confirm("%(confirm)s")) { this.checked=false; } else { 
        jQuery("#%(id)s__hidden").attr('value', '');
        jQuery("#%(id)s a").html("");
    }
}
                        """ % dict(confirm=current.T('Are you sure you want to delete this object?'), 
                                   id=el_id), 
                             _name=field.name + UploadWidget.ID_DELETE_SUFFIX),
                       UploadWidget.DELETE_FILE, _style='margin-top:5px;'),
                   INPUT(_type='hidden', _value=value,
                         _name=field.name, _id='%s__hidden' % el_id, 
                         requires=field.requires), 
                   _id=el_id)
        
    def _is_published(self, content):
        return (content is None) or bool(content.publish_on and 
                                         content.publish_on<=current.request.now)
        
    def render(self, name, *fields, **kwargs):
        request, response, session, T, settings = (
            current.request, current.response, current.session, current.T, self.settings)
        el_id = 'managed_html_block_%s' % name
        inner_el_id = 'managed_html_inner_%s' % name
        
        def _render(func):
            def _func(content):
                if self.view_mode == EDIT_MODE:
                    response.write(XML("""<script>
jQuery(function(){
    $('#%s a').unbind("click").click(function(e) {e.preventDefault();});
});</script>""" % inner_el_id))
                    response.write(XML("<div onclick='%s'>" % self._post_js(name, 'edit', inner_el_id)))
                
                func(Storage(content and content.data and json.loads(content.data) or {}))
                
                if self.view_mode == EDIT_MODE:
                    # if not content or not content.data:
                    response.write(XML('<div style="height:7px;background:white;">&nbsp;</div><div style="clear:both;"></div>'))
                    response.write(XML('</div>'))
                    
            if (self.keyword in request.vars and 
                    request.vars[self.keyword] == name):
                # === Ajax request for the name ===
                import cStringIO
                action = request.vars.get('_action')
                if action == 'edit':
                    content = self._get_content(name)
                    if not content:
                        #settings.table_content.insert(name=name)
                        content = self._get_content(name)
                    data = content and content.data and json.loads(content.data) or {}
                    
                    virtual_record = Storage(id=0)
                    for field in fields:
                        virtual_record[field.name] = data[field.name] if field.name in data else None
                        
                        if type(virtual_record[field.name]) == unicode:
                            virtual_record[field.name] = virtual_record[field.name].encode('utf-8', 'ignore')
                        
                        # if field.type == 'upload':
                            # field.uploadfolder = field.uploadfolder or settings.uploadfolder
                            # settings.table_image.name.uploadfolder = field.uploadfolder
                            # field.widget = self.file_widget  # self.get_uploadify_widget(name)
                        if field.type == 'text':
                            if not settings.text_widget:       
                                settings.text_widget = self._get_elrte_widget() # , fm_open=None
                            field.widget = field.widget or settings.text_widget
                        elif field.type.startswith('list:'):
                            if field.name+'[]' in request.vars:
                                request.vars[field.name] = [v for v in request.vars[field.name+'[]'] if v]
                                if field.type == 'list:integer' or field.type.startswith('list:reference'):
                                    request.vars[field.name] = map(int, request.vars[field.name])
                            
                    form = SQLFORM(
                        DAL(None).define_table('no_table', *fields),
                        virtual_record,
                        upload=settings.upload,
                        showid=False,
                        buttons=[],
                    )
                    if form.accepts(request.vars, session, formname='managed_html_content_form_%s' % name):
                        data = {}
                        for field in fields:
                            field_value = form.vars[field.name]
                            #if field.type == 'upload' and field_value:
                                # field_value.replace('no_table.image.', '%s.name.' % settings.table_image)
                            data[field.name] = field_value
                            
                        #content.update_record(data=json.dumps(data))
                        content_id = settings.table_content.insert(name=name, data=json.dumps(data))
                        content = self._get_content(name)
                        
                        # for field in fields:
                            # if field.type == 'upload':
                                # settings.table_image.insert(name=field_value)
                        
                        response.flash = T('Edited')
                        response.js = 'managed_html_published("%s", false);' % el_id
                        response.js += 'managed_html_editing("%s", false);' % el_id
                        
                        response.body = cStringIO.StringIO()
                        _func(content)
                        raise HTTP(200, response.body.getvalue())
                        
                    if self._is_simple_form(fields):
                        form.components = [form.custom.widget[fields[0].name]]
                        
                    form.components += [INPUT(_type='hidden', _name=self.keyword, _value=name),
                               INPUT(_type='hidden', _name='_action', _value='edit')]
                    raise HTTP(200, form)
                    
                elif action in ('back', 'publish_now'):
                    content = self._get_content(name)
                    if action == 'publish_now':
                        content.update_record(publish_on=request.now)
                        response.js = 'managed_html_published("%s", true);' % el_id
                        response.flash = current.T('Published')
                    elif action == 'back':
                        response.js = 'managed_html_published("%s", %s);' % (
                                        el_id, 'true' if self._is_published(content) else 'false')
                    
                    response.body = cStringIO.StringIO()
                    _func(content)
                    raise HTTP(200, response.body.getvalue())
                else:
                    raise RuntimeError
                
            def wrapper(*args, **kwds):
                content = self._get_content(name, cache=kwargs.get('cache'))
                
                if self.view_mode == EDIT_MODE:
                    is_published = self._is_published(content)
                    
                    response.write(XML('<div id="%s" class="managed_html_block  %s">' %
                                        (el_id, 'managed_html_block_pending' if not is_published else '')))
                    
                    # === write content ===
                    response.write(XML("""<div id="%s" class="managed_html_content">""" % (inner_el_id)))
                    _func(content)
                    response.write(XML('<div style="clear:both;"></div></div>'))
                    
                    # === write action buttons ===
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
                        SPAN(INPUT(_value=T('Edit'), _type='button', 
                              _onclick=self._post_js(name, 'edit', inner_el_id),
                              _class='managed_html_btn'),
                           _class='managed_html_edit_btn'),
                       SPAN(INPUT(_value=T('Publish Now'), _type='button', 
                              _onclick=self._post_js(name, 'publish_now', inner_el_id),
                              _class='managed_html_btn managed_html_success_btn'),
                           _class='managed_html_publish_now_btn',
                           _style='display:none;' if is_published else ''),
                       SPAN(SPAN(fields[0].comment, _style='white-space:nowrap;margin-right:10px;'),
                           _class='managed_html_main_comment',
                           _style='display:none;') if self._is_simple_form(fields) and fields[0].comment else '',
                    ), _class='managed_html_contents_ctrl')))
                    
                    response.write(XML('</div>'))
                    
                else:
                    # === write content ===
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
                    settings.table_content.insert(name=name, publish_on=request.now) # remove if append archive
                    content = self._get_content(name)
                    
                indices = request.vars.get('indices[]', [])
                from_idx = request.vars.get('from')
                to_idx = request.vars.get('to')
                arg_from = indices.index(from_idx)
                arg_to = indices.index(to_idx)
                indices[arg_from] = to_idx
                indices[arg_to] = from_idx
                
                content.update_record(data=json.dumps(indices), publish_on=request.now) # remove if append archive
                # settings.table_content.insert(name=name, data=json.dumps(indices))
                # content = self._get_content(name)
                        
                response.flash = T('Moved')
                
                raise HTTP(200, json.dumps(indices))
            
        def _movable(func):
            self._movables[name].append((len(self._movables[name]), func))
                
            def wrapper(*args, **kwds):
                # is_published = False
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
                        self._movables[name] = [self._movables[name][i] for i in permutation]
                        
                        # is_published = bool(content.publish_on and content.publish_on<=request.now)
                        
                    if self.view_mode == EDIT_MODE:
                        response.write(XML("""
<script>jQuery(function(){managed_html_movable("%s", [%s], "%s", "%s", "%s")})</script>""" % 
                            (name, ','.join([str(i) for i, f in self._movables[name]]),
                             self.keyword, URL(args=request.args, vars=request.get_vars),
                             current.T('Sure you want to move them?'))))
                    self._movable_loaded[name] = True
                    
                _block_index, _func = self._movables[name].pop(0)
                
                if self.view_mode == EDIT_MODE:
                    el_id = 'managed_html_block_%s_%s' % (name, _block_index)
                    inner_el_id = 'managed_html_inner_%s_%s' % (name, _block_index)
                    
                    response.write(XML('<div id="%s" class="managed_html_block managed_html_block_movable">'% el_id))
                    
                    response.write(XML("""
<div id="%s" class="managed_html_movable managed_html_name_%s">
""" % (inner_el_id, name))) #  %s .. , 'managed_html_content_published' if is_published else ''
                    
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
        # if self.view_mode == EDIT_MODE:
            # # response.xxx = xxx
            # return SCRIPT(""" """)
        # else:
            # # response.yyy = yyy
            # return ''

