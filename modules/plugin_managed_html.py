# -*- coding: utf-8 -*-
# This plugins is licensed under the MIT license: http://www.opensource.org/licenses/mit-license.php
# Authors: Kenji Hosoda <hosoda@s-cubism.jp>
from gluon import *
from gluon.storage import Storage
from gluon.validators import Validator
import gluon.contrib.simplejson as json
# from plugin_uploadify_widget import IS_UPLOADIFY_IMAGE as IS_IMAGE
# from plugin_uploadify_widget import IS_UPLOADIFY_LENGTH as IS_LENGTH

# For referencing static and views from other application
import os
APP = os.path.basename(os.path.dirname(os.path.dirname(__file__)))

LIVE_MODE = '_managed_html_live'
EDIT_MODE = '_managed_html_edit'
PREVIEW_MODE = '_managed_html_preview'

IMAGE_EXTENSIONS = ('png', 'jpg', 'jpeg', 'gif', 'bmp')
MOVIE_EXTENSIONS = ('flv', 'mp4', 'm4v', 'avi', 'wmv')
FILE_EXTENSIONS = None


class IS_HTML(Validator):
    def _strip(self, value):
        if value in ('<p>&nbsp;</p>', '&nbsp;'):
            value = ''
        if value:
            value = value.strip(' ')
            while True:
                if value.startswith('\n'):
                    value = value[1:]
                if value.startswith('<div><br /></div>'):
                    value = value[17:]
                elif value.startswith('<br />'):
                    value = value[6:]
                else:
                    break
        return value

    def __call__(self, value):
        try:
            from BeautifulSoup import BeautifulSoup
            _soup = BeautifulSoup
        except ImportError:
            _soup = lambda v: v

        return (self._strip(str(_soup(value))), None)


class ManagedHTML(object):

    def __init__(self, db, keyword='_managed_html'):
        self.db, self.keyword = db, keyword
        self.file_grid_keyword = '_managed_html_%s_grid'
        self.page_grid_keyword = '_managed_html_page_grid'
        self.history_grid_keyword = '_managed_html_history_grid'
        
        self.contents_cache = {}
        
        settings = self.settings = Storage()
        
        settings.URL = URL
        
        settings.home_url = '/'
        settings.home_label = 'Home'
        
        settings.table_content_name = 'managed_html_content'
        settings.table_content = None
        
        settings.table_file_name = 'managed_html_file'
        settings.table_file = None
        
        settings.extra_fields = {}
        
        settings.text_widget_cssfiles = []  # ex) [URL('static', 'css/base.css')]
        
        settings.uploadfolder = os.path.join(self.db._adapter.folder, '..', 'uploads')
        settings.upload = lambda filename: URL('download', args=[filename])  # TODO
        
        settings.page_grid = None
        # settings.page_original_url = ''
        
        settings.editable = True
        settings.publishable = True
        
        def _html(name, parent=None):
            @self.content_block(name, Field('html', 'text'), parent=parent)
            def _(content):
                current.response.write(XML(content.html or '').xml(), escape=False)
            _()
            return ''
        settings.content_types = Storage(html=_html)
        
        self.view_mode = LIVE_MODE
        
    def url(self, a=None, c=None, f=None, r=None, args=None, vars=None, **kwds):
        if not r:
            if a and not c and not f:
                (f, a, c) = (a, c, f)
            elif a and c and not f:
                (c, f, a) = (a, c, f)
        if c != 'static':
            _arg0 = current.request.args(0)
            if _arg0 and (EDIT_MODE in _arg0 or PREVIEW_MODE in _arg0):
                return self._mode_url(_arg0, a, c, f, r, args, vars, **kwds)
        return self.settings.URL(a, c, f, r, args, vars, **kwds)
        
    def _mode_url(self, mode, a=None, c=None, f=None, r=None, args=None, vars=None, **kwds):
        if args in (None, []):
            args = [mode]
        elif not isinstance(args, (list, tuple)):
            args = [mode, args]
        else:
            args = [mode] + args
        return self.settings.URL(a, c, f, r, args=args, vars=vars, **kwds)
        
    def define_tables(self, migrate=True, fake_migrate=False):
        db, settings, T = self.db, self.settings, current.T
        
        if not settings.table_content_name in db.tables:
            db.define_table(settings.table_content_name,
                Field('name', readable=False, writable=False),
                Field('publish_on', 'datetime', readable=False, writable=False),
                Field('data', 'text', default=''),
                migrate=migrate, fake_migrate=fake_migrate,
                *settings.extra_fields.get(settings.table_content_name, []))
        settings.table_content = db[settings.table_content_name]
            
        if not settings.table_file_name in db.tables:
            db.define_table(settings.table_file_name,
                Field('name', 'upload', unique=True,
                       label=T('File'), autodelete=True),
                # Field('original_name'),
                Field('keyword', label=T('Keyword')),
                Field('description', 'text', label=T('Description')),
                Field('extension', label=T('Extension'), length=16, readable=False, writable=False),
                Field('thumbnail', 'upload', autodelete=True, readable=False, writable=False),
                migrate=migrate, fake_migrate=fake_migrate,
                *settings.extra_fields.get(settings.table_file_name, []))
        settings.table_file = db[settings.table_file_name]
        
    def _get_content(self, name, cache=None, id=None):
        
        if self.view_mode == LIVE_MODE:
            loaded_record = self.contents_cache.get(name)
            if loaded_record:
                return loaded_record
            table_content = self.settings.table_content
            return self.db(table_content.name == name)(table_content.publish_on <= current.request.now
                          ).select(orderby=~table_content.id, cache=cache).first()
        else:
            table_content = self.settings.table_content
            query = (table_content.name == name)
            if id:
                query &= (table_content.id == id)
            record = self.db(query).select(orderby=~table_content.id).first()
            
            self.contents_cache[name] = record
            return record
        
    def _is_published(self, content):
        return (content is None) or bool(content.publish_on and
                                         content.publish_on <= current.request.now)
        
    def load_contents(self, content_names):
        if not content_names:
            return
        table_content = self.settings.table_content
        # records = self.db(
            # table_content.name.belongs(content_names))(
            # table_content.publish_on!=None
            # ).select(table_content.ALL,
                     # table_content.publish_on.max(),
                     # groupby=table_content.name)
        
        max_id = table_content.id.max()
        _ids = [r[max_id] for r in self.db(
                        table_content.name.belongs(content_names))(
                        table_content.publish_on <= current.request.now
                          ).select(max_id, groupby=table_content.name)]
        if _ids:
            records = self.db(table_content.id.belongs(_ids)).select(table_content.ALL)
            for r in records:
                self.contents_cache[r.name] = r
        
    def switch_mode(self):
        settings, request, response, T = self.settings, current.request, current.response, current.T
        
        _arg0 = request.args(0)
        if not (_arg0 and (EDIT_MODE in _arg0 or PREVIEW_MODE in _arg0)):
            self.view_mode = LIVE_MODE
            return
        else:
            self.view_mode = _arg0
            if request.args and request.args[-1] == 'managed_html.js':
                # Return javascript
                
                from globals import Response, Storage
                _response = Response()
                _response._view_environment = current.globalenv.copy()
                _response._view_environment.update(
                    request=Storage(folder=os.path.join(os.path.dirname(os.path.dirname(request.folder)), APP)),
                    response=_response,
                )
                
                _response.headers['Content-Type'] = 'text/javascript; charset=utf-8;'
                raise HTTP(200, _response.render('plugin_managed_html/managed_html_ajax.js',
                            dict(
                                home_url=settings.home_url,
                                home_label=settings.home_label,
                                edit_url=settings.URL(args=[self.view_mode.replace(PREVIEW_MODE, EDIT_MODE)] +
                                                            request.args[1:-1], vars=request.vars)
                                            if PREVIEW_MODE in self.view_mode else '',
                                preview_url=settings.URL(args=[self.view_mode.replace(EDIT_MODE, PREVIEW_MODE)] +
                                                                 request.args[1:-1], vars=request.vars)
                                            if EDIT_MODE in self.view_mode else '',
                                live_url=self.settings.URL(args=request.args[1:-1], vars=request.vars, scheme='http'),
                                show_page_grid=self._show_page_grid_js() if settings.page_grid else '',
                            )),
                           **_response.headers)
                           
            response.files.append(URL(args=((request.args or []) + ['managed_html.js'])))
                          
            self.use_grid(args=request.args[:2])
               
    def use_grid(self, args):
        settings, request, response, T = self.settings, current.request, current.response, current.T
        
        from plugin_solidgrid import SolidGrid
        self.solidgrid = SolidGrid(renderstyle=True)
        
        for file_type in ('image', 'movie', 'file'):
            _grid_keyword = self.file_grid_keyword % file_type
            if (_grid_keyword in request.vars or
                    (_grid_keyword in request.args)):
                if not self.settings.editable:
                    raise HTTP(400)
                raise HTTP(200, self._file_grid(file_type=file_type, args=args))
        
        if ((self.history_grid_keyword in request.vars) or
                (self.history_grid_keyword in request.args)):
            if not self.settings.editable:
                raise HTTP(400)
            raise HTTP(200, self._history_grid(args=args))
                
        _files = [
            URL(APP, 'static', 'plugin_managed_html/managed_html.css'),
            URL(APP, 'static', 'plugin_managed_html/jquery.spinner.js'),
            URL(APP, 'static', 'plugin_elrte_widget/js/jquery-ui-1.8.16.custom.min.js'),
        ]
        response.files[:0] = [f for f in _files if f not in response.files]
            
    def _show_page_grid_js(self):
        from plugin_dialog import DIALOG
        T = current.T
        return DIALOG(title=T('+ Page'), close_button=T('close'),
                        content=self.settings.page_grid,
                        _class='managed_html_dialog').show(reload=True)
    
    def _show_history_grid_js(self, content_name, collection=False):
        from plugin_dialog import DIALOG
        T = current.T
        request = current.request
        
        _post_js = self._post_content_js if not collection else self._post_collection_js
        
        return """
jQuery(document.body).one('managed_html_history_selected', function(e, content_id) {
    eval('%(post)s'.replace("__placeholder__", content_id));
    jQuery('.managed_html_dialog').hide();
}); %(show)s; return false;""" % dict(
            post=_post_js(content_name, 'revert', content_id='__placeholder__'),
            show=DIALOG(title=T('History'), close_button=T('close'),
                      content=LOAD(url=URL(args=(request.args or []) + ['history'],
                                           vars={self.history_grid_keyword: content_name}), ajax=True),
                      _class='managed_html_dialog'
                      ).show(reload=True))
                    
    def _history_grid(self, args):
        T = current.T
        request = current.request
        
        table_content = self.settings.table_content
        
        table_content.publish_on.label = T('Publish on')
        table_content.publish_on.represent = lambda v: v and v or '---'
        
        def _represent(v):
            if not v:
                return '---'
            data = json.loads(v)
            if type(data) == dict:
                return DIV([DIV(DIV(k), TEXTAREA(v, _rows=3, _cols=50, _style='width:90%;'))
                            for k, v in data.items()])
            elif type(data) == list:
                return DIV([DIV(k, ':', v) for k, v in data])
            
        table_content.data.represent = _represent
                
        extracolumns = [
            {'label': '', 'width': '150px;',
                'content':lambda row, rc:
                 SPAN(self.solidgrid.settings.recordbutton('ui-icon-circle-arrow-w', T('Revert'),
                            '#', _onclick="""
jQuery(document.body).trigger('managed_html_history_selected', ['%s']);return false;
                            """ % (row.id), _class='ui-btn'))},
        ]
        
        content_name = request.vars.get(self.history_grid_keyword, request.args(2))
        query = (table_content.name == content_name)
        grid = self.solidgrid(
            query,
            columns=[extracolumns[0], table_content.publish_on, table_content.data],
            extracolumns=extracolumns,
            create=False,
            editable=False,
            details=False,
            showid=False,
            searchable=False,
            sortable=[~table_content.id],
            csv=False,
            args=args + [self.history_grid_keyword, content_name],
        )
        
        return DIV(DIV(grid.gridbuttons), DIV(_style='clear:both;'), BR(), HR(),
                 DIV(DIV(_style='clear:both;'), grid),
                 _class='history_grid')
              
    def _file_grid(self, file_type, args):
        T = current.T
        table_file = self.settings.table_file
        request = current.request
       
        if request.vars._hmac_key:
            hmac_key = request.vars._hmac_key
            user_signature = False
            request.get_vars._signature = request.post_vars._signature
        else:
            hmac_key = None
            user_signature = True
            
        from plugin_uploadify_widget import uploadify_widget

        def _uploadify_widget(field, value, download_url=None, **attributes):
            if current.session.auth:
                attributes['extra_vars'] = {'_signature': request.get_vars._signature,
                                            '_hmac_key': current.session.auth.hmac_key}
            return uploadify_widget(field, value, download_url, **attributes)
        table_file.name.widget = _uploadify_widget
        
        table_file.name.uploadfolder = self.settings.uploadfolder
        
        table_file.name.comment = self.settings.get('%s_comment' % file_type)
        table_file.name.requires = self.settings.get('%s_requires' % file_type)

        def _oncreate(form):
            if 'filename' in request.vars.name:
                filename = request.vars.name.filename
                if filename:
                    extension = filename.split('.')[-1].lower()
                    thumbnail = ''
                    if extension in (IMAGE_EXTENSIONS + MOVIE_EXTENSIONS):
                        if extension in IMAGE_EXTENSIONS:
                            # TODO
                            # (nx, ny) = 80, 80
                            # from PIL import Image
                            # img = Image.open(os.path.join(self.settings.uploadfolder, filename))
                            # # print img.size # TODO
                            # img.thumbnail((nx, ny), Image.ANTIALIAS)
                            # root, ext = os.path.splitext(filename)
                            # thumbnail = '%s_thumbnail%s' % (root, ext)
                            # img.save(os.path.join(self.settings.uploadfolder, thumbnail))
                            thumbnail = filename
                        
                    self.db(self.settings.table_file.id == form.vars.id).update(
                        name=filename, extension=extension, thumbnail=thumbnail,
                    )
            
        _grid_keyword = self.file_grid_keyword % file_type
        _extensions = {'image': IMAGE_EXTENSIONS,
                       'movie': MOVIE_EXTENSIONS,
                       'file': FILE_EXTENSIONS,
                       }.get(file_type)
        extracolumns = [
            {'label': '', 'width': '150px;',
                'content':lambda row, rc:
                    SPAN(self.solidgrid.settings.recordbutton('ui-icon-seek-next', T('Select'),
                            '#', _onclick="""
jQuery(document.body).trigger('managed_html_file_selected', ['%s', '%s']);return false;
                            """ % (row.name, row.thumbnail), _class='ui-btn'))},
             {'label': T('File'), 'width': '150px;',
              'content':lambda row, rc: DIV(
                DIV(self._file_represent(row.name, row.thumbnail)),
                TEXTAREA(self.settings.upload(row.name), _rows=1),
                _style='word-break:break-all;')}
        ]
        main_table = table_file
        grid = self.solidgrid((main_table.extension.belongs(_extensions) if _extensions else main_table),
            fields=[main_table.ALL],
            columns=[extracolumns[0], extracolumns[1],
                     main_table.keyword, main_table.description, main_table.extension],
            extracolumns=extracolumns,
            editable=['keyword', 'description'],
            details=False, csv=False, showid=False,
            searchable=[main_table.keyword, main_table.extension],
            args=args + [_grid_keyword],
            user_signature=user_signature,
            hmac_key=hmac_key,
            oncreate=_oncreate,
            formname='managed_html_%s_form' % _grid_keyword,
            upload=self.settings.upload,
        )
        return DIV(DIV(grid.gridbuttons), DIV(_style='clear:both;'), BR(), HR(),
                 DIV(grid.search_form, _class='well search_form') if hasattr(grid, 'search_form') else '',
                 DIV(DIV(_style='clear:both;'), grid),
                 _class='file_grid')
        
    def _file_represent(self, filename, thumbnail, max_width=80, max_height=80):  # TODO set self.settings.thumbnail_size
        if not filename:
            return A('', _href='#')
        if not thumbnail:
            return A('file', _href=self.settings.upload(filename))
        return A(IMG(_src=self.settings.upload(thumbnail),
                     _style='max-width:%spx;max-height:%spx;' % (max_width, max_height)),
                      _href=self.settings.upload(filename), _target='_blank')
        
    def _file_widget(self, field, value, download_url=None, **attributes):
        file_type = attributes.get('file_type')
        T = current.T
        el_id = '%s_%s' % (field._tablename, field.name)
        
        from plugin_dialog import DIALOG
        file_chooser = DIALOG(title=T('Select %s' % file_type), close_button=T('close'),
            content=LOAD(url=URL(args=(current.request.args or []) + ['file_chooser'],
                                 vars={self.file_grid_keyword % file_type: True}), ajax=True),
            onclose='jQuery(document.body).trigger("managed_html_file_selected", "");',
            _id='managed_html_%s_chooser' % file_type, _class='managed_html_dialog')
            
        _record = self.db(self.settings.table_file.name == value
                          ).select(self.settings.table_file.thumbnail).first()
        thumbnail = _record and _record.thumbnail or ''
        
        from gluon.sqlhtml import UploadWidget
        return DIV(INPUT(_type='button', _value='Select',
                         _onclick="""
jQuery(document.body).one('managed_html_file_selected', function(e, name, thumbnail) {
if(name!="") {
    var url = "%(upload)s".replace('__filename__', name);
    jQuery("#%(id)s__hidden").attr('value', name);
    var ext = name.split('.').slice(-1);
    var a = jQuery("#%(id)s__file a");
    a.attr('href', url);
    if(thumbnail!="") {
        var thumbnail_url = "%(upload)s".replace('__filename__', thumbnail);
        a.html("<img src='"+thumbnail_url+"' style='max-width:150px;max-height:150px;'/>");
    } else {
        a.html("file");
    }
    jQuery('.managed_html_dialog').hide();
}
}); %(show)s; return false;""" % dict(id=el_id, show=file_chooser.show(),
                                      upload=self.settings.upload('__filename__'))),
                   DIV(self._file_represent(value, thumbnail, 150, 150), _id='%s__file' % el_id,
                       _style='margin-top:5px;'),
                   DIV(INPUT(_type='checkbox', _onclick="""
if(this.checked) {
    if(!confirm("%(confirm)s")) { this.checked=false; } else {
        jQuery("#%(id)s__hidden").attr('value', '');
        jQuery("#%(id)s a").html("");
    }
}""" % dict(confirm=current.T('Are you sure you want to delete this object?'),
                                   id=el_id),
                             _name=field.name + UploadWidget.ID_DELETE_SUFFIX),
                       UploadWidget.DELETE_FILE, _style='margin-top:5px;'),
                   INPUT(_type='hidden', _value=value,
                         _name=field.name, _id='%s__hidden' % el_id,
                         requires=field.requires),
                   _id=el_id)
        
    def image_widget(self, field, value, download_url=None, **attributes):
        attributes['file_type'] = 'image'
        return self._file_widget(field, value, download_url=None, **attributes)
               
    def movie_widget(self, field, value, download_url=None, **attributes):
        attributes['file_type'] = 'movie'
        return self._file_widget(field, value, download_url=None, **attributes)
          
    def text_widget(self, field, value, **attributes):
        T = current.T
        try:
            lang = T.accepted_language.split('-')[0].replace('ja', 'jp')
        except:
            lang = 'en'
        
        from plugin_dialog import DIALOG
        image_chooser = DIALOG(title=T('Select an image'), close_button=T('close'),
            content=LOAD(url=URL(args=(current.request.args or []) + ['image_chooser'],
                                 vars={self.file_grid_keyword % 'image': True}), ajax=True),
            onclose='jQuery(document.body).trigger("managed_html_file_selected", "");',
            _id='managed_html_image_chooser', _class='managed_html_dialog')
        file_chooser = DIALOG(title=T('Select a file'), close_button=T('close'),
            content=LOAD(url=URL(args=(current.request.args or []) + ['file_chooser'],
                                 vars={self.file_grid_keyword % 'file': True}), ajax=True),
            onclose='jQuery(document.body).trigger("managed_html_file_selected", "");',
            _id='managed_html_file_chooser', _class='managed_html_dialog')
                              
        fm_open = """function(callback, kind) {
if (kind == 'elfinder') {%s;} else {%s;}
jQuery(document.body).one('managed_html_file_selected', function(e, filename) {
if(filename != "") {
    var data = '%s'.replace('__filename__', filename);
    if (kind == 'elfinder') {
        data = '<a href="'+data+'" >FILE</a>';
    }
    callback(data); jQuery('.managed_html_dialog').hide();
}});
}""" % (file_chooser.show(),
        image_chooser.show(), self.settings.upload('__filename__'))  # TODO setting for managed_html_file_selected

        from plugin_elrte_widget import ElrteWidget
        widget = ElrteWidget()
        widget.settings.lang = lang
        widget.settings.cssfiles = self.settings.text_widget_cssfiles
        widget.settings.fm_open = fm_open
        return widget(field, value, **attributes)
       
    def _post_js(self, target, name, action, **attrs):
        data = {self.keyword: name, '_action': action}
        data.update(**attrs)
        return 'managed_html_ajax_page("%(url)s", %(data)s, "%(target)s");' % dict(
                          url=URL(args=current.request.args),  # , vars=current.request.get_vars
                          data=json.dumps(data), target=target)
       
    def _post_content_js(self, name, action, **attrs):
        return self._post_js('managed_html_content_%s' % name, name, action, **attrs)

    def content_block(self, name, *fields, **kwargs):
        request, response, session, T, settings = (
            current.request, current.response, current.session, current.T, self.settings)
        el_id = 'managed_html_content_block_%s' % name
        content_el_id = 'managed_html_content_%s' % name
        
        def _decorator(func):
            def _func(content):
                if EDIT_MODE in self.view_mode:
                    response.write(XML("""<script>
jQuery(function(){
    jQuery('#%s a').unbind("click").click(function(e) {e.preventDefault();});
});</script>""" % content_el_id))

                    response.write(XML("<div class='%s' onclick='%s'>&nbsp;</div>" %
                                       (('managed_html_content_anchor' if self._is_published(content)
                                            else 'managed_html_content_anchor_pending'),
                                        (self._post_content_js(name, 'edit') if settings.editable else ''))))

                    response.write(XML("<div onclick='%s' class='managed_html_content_inner'>" %
                                        (self._post_content_js(name, 'edit') if settings.editable else '')))
                    _body_len = len(response.body.getvalue())
                    
                func(Storage(content and content.data and json.loads(content.data) or {}))
                
                if EDIT_MODE in self.view_mode:
                    if len(response.body.getvalue()) == _body_len:
                        response.write(XML("<div class='managed_html_empty_content' >&nbsp;</div>"))
                    response.write(XML('</div>'))
                    
            if (EDIT_MODE in self.view_mode and request.ajax and
                    self.keyword in request.vars and request.vars[self.keyword] == name):
                    
                import cStringIO
                action = request.vars.get('_action')
                if action in ('edit', 'revert'):
                    if not settings.editable:
                        raise HTTP(400)
                        
                    if action == 'revert':
                        response.flash = T('Reverted')
                        content = self._get_content(name, id=request.vars.content_id)
                    else:
                        content = self._get_content(name)
                        
                    if not content:
                        content = self._get_content(name)
                    data = content and content.data and json.loads(content.data) or {}
                    
                    virtual_record = Storage(id=0)
                    for field in fields:
                        virtual_record[field.name] = data[field.name] if field.name in data else field.default
                        
                        if type(virtual_record[field.name]) == unicode:
                            virtual_record[field.name] = virtual_record[field.name].encode('utf-8', 'ignore')
                        
                        if field.type == 'text':
                            field.widget = field.widget or self.text_widget
                            field.requires = IS_HTML()
                            
                            # if field.name in request.vars:
                                # from plugin_elrte_widget import strip
                                # request.vars[field.name] = strip(request.vars[field.name])
        
                        elif field.type.startswith('list:'):
                            if field.name + '[]' in request.vars:
                                request.vars[field.name] = [v for v in request.vars[field.name + '[]'] if v]
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
                            data[field.name] = field_value
                            
                        table_content = settings.table_content
                        self.db(table_content.name == name)(table_content.publish_on == None).delete()
                        table_content.insert(name=name, data=json.dumps(data))
                        content = self._get_content(name)
                        
                        response.flash = T('Edited')
                        response.js = 'managed_html_published("%s", false);' % el_id
                        response.js += 'managed_html_editing("%s", false);' % el_id
                        
                        response.body = cStringIO.StringIO()
                        _func(content)
                        raise HTTP(200, response.body.getvalue())
                        
                    if len(fields) == 1:
                        form.components = [form.custom.widget[fields[0].name]]
                        
                    form.components += [INPUT(_type='hidden', _name=self.keyword, _value=name),
                               INPUT(_type='hidden', _name='_action', _value='edit')]
                    raise HTTP(200, DIV(form, _class='managed_html_content_inner'))
                    
                elif action in ('back', 'publish_now'):
                    content = self._get_content(name)
                    if action == 'publish_now':
                        if not settings.publishable:
                            raise HTTP(400)
                        content.update_record(publish_on=request.now)
                        response.js = 'managed_html_published("%s", true);' % el_id
                        response.flash = T('Published')
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
                
                if EDIT_MODE in self.view_mode:
                    is_published = self._is_published(content)
                    
                    response.write(XML('<div id="%s" class="managed_html_content_block %s">' %
                                        (el_id, 'managed_html_content_block_pending' if not is_published else '')))
                    
                    # === write content ===
                    response.write(XML('<div id="%s" class="managed_html_content">' % content_el_id))
                    _func(content)
                    response.write(XML('</div>'))  # <div style="clear:both;"></div>
                    
                    # === write action buttons ===
                    response.write(XML(DIV(DIV(
                        SPAN(INPUT(_value=T('Back'), _type='button',
                              _onclick=self._post_content_js(name, 'back'),
                              _class='managed_html_btn'),
                          _class='managed_html_back_btn',
                          _style='display:none;') if settings.editable else '',
                        SPAN(INPUT(_value=T('Submit'), _type='button',
                              _onclick='jQuery("#%s"+" form").submit()' % content_el_id,
                              _class='managed_html_btn managed_html_primary_btn'),
                          _class='managed_html_submit_btn',
                          _style='display:none;') if settings.editable else '',
                        SPAN(INPUT(_value=T('Edit'), _type='button',
                              _onclick=self._post_content_js(name, 'edit'),
                              _class='managed_html_btn'),
                           _class='managed_html_edit_btn') if settings.editable else '',
                        SPAN(INPUT(_value=T('Publish'), _type='button',
                              _onclick=self._post_content_js(name, 'publish_now'),
                              _class='managed_html_btn managed_html_success_btn'),
                           _class='managed_html_publish_now_btn',
                           _style='display:none;' if is_published else '') if settings.publishable else '',
                        SPAN(INPUT(_value=T('History'), _type='button',
                              _onclick=self._show_history_grid_js(name),
                              _class='managed_html_btn managed_html_info_btn'),
                           _class='managed_html_history_btn',
                           _style='display:none;')  if settings.editable else '',
                       SPAN(SPAN(T('Move'),
                              _title=T('Drag me'),
                              _class='managed_html_btn managed_html_warning_btn'),
                           _class='managed_html_move_btn')  if kwargs.get('parent') else '',
                       SPAN(INPUT(_value=T('Delete'), _type='button',
                              _onclick='if(confirm("%s")){%s;}' % (
                                            T('Are you sure you want to delete this object?'),
                                            self._post_collection_js(kwargs['parent'], 'delete', content=name)),  # 'alert("%s")' % kwargs['parent'],
                              _class='managed_html_btn managed_html_danger_btn'),
                           _class='managed_html_delete_btn')  if kwargs.get('parent') else '',
                    ), _class='managed_html_content_ctrl')))
                    
                    response.write(XML('</div>'))
                    
                else:
                    # === write content ===
                    response.write(XML('<div id="%s">' % el_id))
                    _func(content)
                    response.write(XML('</div>'))
            return wrapper
        return _decorator
        
    def _show_add_form_js(self, name):
        from plugin_dialog import DIALOG
        T = current.T
        request = current.request
        return DIALOG(title=T('Select'), close_button=T('close'),
                        content=LOAD(url=URL(args=request.args,
                                     vars={self.keyword: name, '_action': 'show_add_form'}),
                                     ajax=True),
                        _class='managed_html_dialog').show(reload=True)
         
    def _post_collection_js(self, name, action, **attrs):
        return self._post_js('managed_html_collection_%s' % name, name, action, **attrs)
                       
    def _add_form(self, name):
        T = current.T
        form = SQLFORM.factory(
            Field('content_type',
                  requires=IS_IN_SET(self.settings.content_types.keys(), zero=None)),
            submit_button=T('Submit'),
        )
        
        if form.validate():
            current.response.flash = ''
            return DIV(SCRIPT('jQuery(".managed_html_dialog").hide();' +
                              self._post_collection_js(name, 'add', content_type=form.vars.content_type)))
            
        return form
        
    def collection_block(self, name, **kwargs):
        request, response, session, T, settings = (
            current.request, current.response, current.session, current.T, self.settings)
        el_id = 'managed_html_collection_block_%s' % name
        collection_el_id = 'managed_html_collection_%s' % name
        
        def _decorator(func):
            
            def _func(collection):
                if EDIT_MODE in self.view_mode:
                    response.write(XML("<div class='managed_html_collection_inner'><div>"))
                
                _collection = []
                from functools import partial
                for content_type, content_name in collection and collection.data and json.loads(collection.data) or []:
                    _content_func = settings.content_types.get(content_type, lambda name, parent=None: '')
                    _collection.append(partial(_content_func, content_name, parent=name))
                func(_collection)
                
                if EDIT_MODE in self.view_mode:
                    response.write(XML('<div class="%s">&nbsp;</div>' %
                                        ('managed_html_collection_anchor' if collection and collection.publish_on
                                            else 'managed_html_collection_anchor_pending')))
                    response.write(XML("""
<script>jQuery(function(){managed_html_move("%s", "%s", "%s", "%s")})</script>""" %
                            (name, self.keyword, URL(args=request.args),  # , vars=request.get_vars
                             current.T('Sure you want to move them?'))))
                    response.write(XML('</div></div>'))
            
            if (EDIT_MODE in self.view_mode and request.ajax and
                    self.keyword in request.vars and request.vars[self.keyword] == name):
                
                import cStringIO
                table_content = settings.table_content
                action = request.vars.get('_action')
                response.js = 'managed_html_init_blocks();'
                
                if action in ('add', 'revert'):
                    if not settings.editable:
                        raise HTTP(400)
                        
                    collection = self._get_content(name, id=request.vars.content_id if action == 'revert' else None)
                    if not collection:
                        collection = self._get_content(name)
                    data = collection and collection.data and json.loads(collection.data) or []
                    
                    if action == 'add':
                        from gluon.utils import web2py_uuid
                        new_content_name = web2py_uuid()
                        data.append([request.vars.content_type, new_content_name])
                        response.flash = T('Added')
                        
                    elif action == 'revert':
                        response.flash = T('Reverted')
                      
                    response.js += 'managed_html_collection_published("%s", false);' % el_id
                        
                    self.db(table_content.name == name)(table_content.publish_on == None).delete()
                    table_content.insert(name=name, data=json.dumps(data))
                    collection = self._get_content(name)
                        
                    response.body = cStringIO.StringIO()
                    _func(collection)
                    raise HTTP(200, response.body.getvalue())
                    
                elif action in ('publish_now', 'delete', 'move'):
                    collection = self._get_content(name)
                    
                    if action == 'publish_now':
                        collection.update_record(publish_on=request.now)
                        response.js += 'managed_html_collection_published("%s", true);' % el_id
                        response.flash = T('Published')
                    
                    elif action in ('delete', 'move'):
                        _data = json.loads(collection.data)
                        
                        if action == 'delete':
                            _data = [c for c in _data if c[1] != request.vars.content]
                            response.flash = T('Deleted')
                        
                        elif action == 'move':
                            from_name = request.vars.get('from')
                            to_name = request.vars.get('to')
                            from_idx = to_idx = -1
                            for i, c in enumerate(_data):
                                if c[1] == from_name:
                                    from_idx = i
                                elif c[1] == to_name:
                                    to_idx = i

                            if from_idx >= 0 and to_idx >= 0:
                                _tmp = _data[from_idx]
                                _data[from_idx] = _data[to_idx]
                                _data[to_idx] = _tmp
                                response.flash = T('Moved')

                        self.db(table_content.name == name)(table_content.publish_on == None).delete()
                        table_content.insert(name=name, data=json.dumps(_data))
                        collection = self._get_content(name)
                        
                        response.js += 'managed_html_collection_published("%s", false);' % el_id
                        
                    response.body = cStringIO.StringIO()
                    _func(collection)
                    raise HTTP(200, response.body.getvalue())
                    
                elif action == 'show_add_form':
                    if not settings.editable:
                        raise HTTP(400)
                    raise HTTP(200, self._add_form(name))
                    
                else:
                    raise RuntimeError
                    
            def wrapper(*args, **kwds):
                #self.db(self.settings.table_content.name==name).delete()
                
                collection = self._get_content(name, cache=kwargs.get('cache'))
                
                if EDIT_MODE in self.view_mode:
                    is_published = self._is_published(collection)
                    
                    response.write(XML('<div id="%s" class="managed_html_collection_block %s">' %
                                        (el_id, 'managed_html_collection_block_pending' if not is_published else '')))
                    
                    response.write(XML('<div id="%s" class="managed_html_collection">' % collection_el_id))
                    
                    _func(collection)
                    
                    response.write(XML('</div>'))
                    
                    # TODO refactoring
                    response.write(XML(DIV(DIV(
                                SPAN(INPUT(_value=T('Add'), _type='button',
                                      _onclick=self._show_add_form_js(name),
                                      _class='managed_html_btn'),
                                   _class='managed_html_edit_btn') if settings.editable else '',
                                SPAN(INPUT(_value=T('Publish'), _type='button',
                                      _onclick=self._post_collection_js(name, 'publish_now'),
                                      _class='managed_html_btn managed_html_success_btn'),
                                   _class='managed_html_publish_now_btn',
                                   _style='display:none;' if is_published else '') if settings.publishable else '',
                                SPAN(INPUT(_value=T('History'), _type='button',
                                      _onclick=self._show_history_grid_js(name, collection=True),
                                      _class='managed_html_btn managed_html_info_btn'),
                                   _class='managed_html_history_btn')  if settings.editable else '',
                            ), _class='managed_html_collection_ctrl')))
                    
                    response.write(XML('</div>'))
                else:
                    response.write(XML('<div id="%s">' % el_id))
                    _func(collection)
                    response.write(XML('</div>'))
            return wrapper
        return _decorator
