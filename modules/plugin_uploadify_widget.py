# -*- coding: utf-8 -*-
# This plugins is licensed under the MIT license: http://www.opensource.org/licenses/mit-license.php
# Authors: Kenji Hosoda <hosoda@s-cubism.jp>
from gluon import *
from gluon.validators import translate
from gluon.sqlhtml import UploadWidget
from gluon.storage import Storage

BUTTON_TEXT = 'SELECT FILES'
FILES = ( URL('static', 'plugin_uploadify_widget/uploadify.css'),
          URL('static', 'plugin_uploadify_widget/swfobject.js'),
          URL('static', 'plugin_uploadify_widget/jquery.uploadify.v2.1.4.min.js'),
          URL('static', 'plugin_uploadify_widget/uploadify.css'),
         )

def _plugin_init(name, callback, files):
    js = """
function web2py_plugin_init(name, callback, files) {
    var plugins = jQuery.data(document.body, 'web2py_plugins');
    function _set_plugins(plugins) { jQuery.data(document.body, 'web2py_plugins', plugins); }
    if (plugins == undefined) { plugins = {}; }
    if (name in plugins) {
        if (plugins[name].loaded == true) {jQuery(document).ready(callback); return; }
        else {plugins[name].callbacks.push(callback); _set_plugins(plugins); return; }
    }
    if (files == undefined) {
        plugins[name] = {loaded: true}; _set_plugins(plugins); jQuery(document).ready(callback); return;
    }
    plugins[name] = {loaded: false, callbacks:[callback]}; _set_plugins(plugins);
    var loadings = 0;
    jQuery.each(files, function() {
        if (this.slice(-3) == '.js') { 
            ++loadings;
            jQuery.ajax({type: 'GET', url: this, 
                         success: function(data) { eval(data); --loadings; },
                         error: function() { --loadings; } });
        } else if (this.slice(-4) == '.css') {
            if (document.createStyleSheet){ document.createStyleSheet(this); } // for IE
            else {jQuery('<link rel="stylesheet" type="text/css" href="' + this + '" />').prependTo('head');}
        }
    });
    jQuery(document).ready(function() { 
        var interval = setInterval(function() {
            if (loadings == 0) { 
                plugins[name].loaded = true; _set_plugins(plugins);
                jQuery.each(plugins[name].callbacks, function() { this(); });
                if (interval != null) { clearInterval(interval) } 
            }
        }, 100);
    });
};"""
    if current.request.ajax:
        js += "web2py_plugin_init('%s', %s, %s);" % (name, callback, 
                        '[%s]' % ','.join(["'%s'" % f.lower().split('?')[0] for f in files]))
    else:
        for f in reversed(files):
            if f not in current.response.files:
                current.response.files.insert(0, f)
        js += "web2py_plugin_init('%s', %s);" % (name, callback)
    return js
             
class IS_UPLOADIFY_IMAGE(IS_IMAGE):
    def _call(self, value): 
        return IS_IMAGE.__call__(self, value)
    def __call__(self, value): 
        if not value:
            return (value, translate(self.error_message))
        return (value, None)
        
class IS_UPLOADIFY_FILENAME(IS_UPLOAD_FILENAME):
    def __init__(self, filename=None, extension=None, lastdot=True, case=1,
                    error_message='enter valid filename'):
        import re
        if extension and re.match('^[0-9a-zA-Z\.]+$', extension):
            self._extension = extension
        else:
            self._extension = None
        IS_UPLOAD_FILENAME.__init__(self, filename, extension, lastdot, case, error_message)
        
    def _call(self, value): 
        return IS_UPLOAD_FILENAME.__call__(self, value)
    def __call__(self, value): 
        if not value:
            return (value, translate(self.error_message))
        return (value, None)
        
class IS_UPLOADIFY_LENGTH(IS_LENGTH):
    def _call(self, value): 
        return IS_LENGTH.__call__(self, value)
    def __call__(self, value): 
        if not value:
            return (value, translate(self.error_message))
        return (value, None)

def uploadify_widget(field, value, download_url=None, **attributes): 
    
    _id = '%s_%s' % (field._tablename, field.name)
    input_el = INPUT(_id = _id, _name = field.name,
                     requires = field.requires, _type='hidden',)
            
    _file_id = '__uploadify__%s_%s' % (field._tablename, field.name)
    file_input_el = INPUT(_id = _file_id, _name = '__uploadify__%s' % field.name, _type='file')
        
    ajaxed = 'Filedata' in current.request.post_vars and current.request.post_vars.name == field.name
        
    fileext = '*.*'
    size_limit = 1000000000000
    not_empty_message = None
    
    requires = field.requires
    if isinstance(requires, IS_EMPTY_OR):
        requires = requires.other
        not_empty_message = ''
        
    if type(requires) not in (list, tuple):
        requires = [requires]
    for i, r in enumerate(requires):
        if i == 0 and not_empty_message is None and not value:
            not_empty_message = r.error_message
        
        if isinstance(r, IS_UPLOADIFY_IMAGE):
            fileext = ';'.join(['*.%s' % ext if ext!='jpeg' else '*.jpeg;*.jpg' for ext in r.extensions])
        elif isinstance(r, IS_UPLOADIFY_FILENAME):
            if r._extension:
                fileext = '*.%s' % r._extension
        elif isinstance(r, IS_UPLOADIFY_LENGTH):
            size_limit = r.maxsize
        
        if isinstance(r, (IS_UPLOADIFY_IMAGE, IS_UPLOADIFY_FILENAME, IS_UPLOADIFY_LENGTH)) and ajaxed:
            f = current.request.post_vars.Filedata
            (value, error) = r._call(f)
            if error:
                raise HTTP(507, error)
    
    if ajaxed:
        f = current.request.post_vars.Filedata
        newfilename = field.store(f.file, f.filename)
        raise HTTP(200, newfilename)
        
    callback = """function() {
var uploadify_uploading = [];
var uploadify_uploaded = [];
var el = jQuery('#%(id)s');
var file_el = jQuery('#%(file_id)s');
var form_el = jQuery(el.get(0).form);

jQuery.fn.bindFirst = function(name, fn) {
    this.bind(name, fn);
    var handlers = this.data('events')[name.split('.')[0]];
    var handler = handlers.pop();
    handlers.splice(0, 0, handler);
};
form_el.bindFirst('submit', function (e) {
    var not_empty_message = "%(not_empty_message)s";
    if (not_empty_message!="" && uploadify_uploading.indexOf(file_el.attr('id'))==-1) {
        el.parent().prepend(jQuery("<div class='error'>"+not_empty_message+"</div>"));
        return false;
    }
    if (uploadify_uploading.length != 0){
        if (uploadify_uploading.length == uploadify_uploaded.length) {
            return !%(ajax)s;
        } else {
            if (%(ajax)s) { e.stopImmediatePropagation(); }
            file_el.uploadifyUpload(); 
            return false;
        }
    }
    return !%(ajax)s;
});
function cancel() {
    var idx = uploadify_uploading.indexOf(file_el.attr('id'));
    if (idx != -1) {
        delete uploadify_uploading[idx];
        uploadify_uploaded.push(undefined);
    }
}
file_el.uploadify({
    'buttonText': '%(button_text)s',
    'uploader'  : '%(uploader)s',
    'script'    : '%(script)s',
    'cancelImg' : '%(cancel_img)s',
    'auto'      : false,
    'onSelect'    : function(event, ID, fileObj) {
        uploadify_uploading.push(file_el.attr('id'));
    },
    'onCancel'  : function(event, ID, fileObj, data) { cancel() },
    'onError'   : function (event, ID, fileObj, errorObj) { cancel() },
    'onComplete': function(event, ID, fileObj, response, data) {
        el.val(response);
        uploadify_uploaded.push(file_el.attr('id'));
        if (uploadify_uploading.length == uploadify_uploaded.length) {
            setTimeout(function(){form_el.submit();}, 200);
        }
    },
    'fileExt'   : '%(fileext)s',
    'fileDesc'  : '%(fileext)s',
    'sizeLimit' : %(size_limit)i,
    'scriptData': {'name': el.attr('name')}
});
}""" % dict(id=_id, file_id=_file_id, 
              button_text=BUTTON_TEXT,
              uploader=URL('static', 'plugin_uploadify_widget/uploadify.swf'),
              script=URL(args=current.request.args, vars=current.request.vars),
              cancel_img=URL('static', 'plugin_uploadify_widget/cancel.png'),
              fileext=fileext,
              size_limit=size_limit,
              not_empty_message=not_empty_message or '',
              ajax='true' if current.request.ajax else 'false',
         )
         
    script = SCRIPT(_plugin_init('plugin_uploadify_widget', callback=callback, files=FILES))
    
    if '_formkey' in current.request.vars:
        filename = current.request.vars[field.name]
        if filename:
            current.request.vars[field.name] = Storage(file=None, filename=filename) # TODO file
            field.store = lambda source_file, original_filename: original_filename
        
    inp = SPAN(input_el, file_input_el)
    
    if download_url and value:
        url = download_url + '/' + value
        (br, image) = ('', '')
        if UploadWidget.is_image(value):
            br = BR()
            image = IMG(_src = url, _width = UploadWidget.DEFAULT_WIDTH)

        requires = field.requires
        if requires == [] or isinstance(requires, IS_EMPTY_OR):
            inp = DIV(inp, '[',
                      A(UploadWidget.GENERIC_DESCRIPTION, _href = url),
                      '|',
                      INPUT(_type='checkbox',
                            _name=field.name + UploadWidget.ID_DELETE_SUFFIX),
                      UploadWidget.DELETE_FILE,
                      ']', br, image)
        else:
            inp = DIV(inp, '[',
                      A(UploadWidget.GENERIC_DESCRIPTION, _href = url),
                      ']', br, image)
            
    return DIV(script, inp, **attributes)
