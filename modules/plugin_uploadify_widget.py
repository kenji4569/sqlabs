# -*- coding: utf-8 -*-
# This plugins is licensed under the MIT license: http://www.opensource.org/licenses/mit-license.php
# Authors: Kenji Hosoda <hosoda@s-cubism.jp>
from gluon import *
from gluon.validators import translate
from gluon.sqlhtml import UploadWidget
from gluon.storage import Storage
from gluon.contrib import simplejson as json

FILES = ( URL('static', 'plugin_uploadify_widget/uploadify.css'),
          URL('static', 'plugin_uploadify_widget/swfobject.js'),
          URL('static', 'plugin_uploadify_widget/jquery.uploadify.v2.1.4.min.js'),
          URL('static', 'plugin_uploadify_widget/uploadify.css'),
         )
BUTTON_TEXT = 'SELECT FILES'

def _set_files(files):
    if current.request.ajax:
        current.response.js = (current.response.js or '') + """;(function ($) {
var srcs = $('script').map(function(){return $(this).attr('src');}),
    hrefs = $('link').map(function(){return $(this).attr('href');});
$.each(%s, function() {
    if ((this.slice(-3) == '.js') && ($.inArray(this.toString(), srcs) == -1)) {
        var el = document.createElement('script'); el.type = 'text/javascript'; el.src = this;
        document.body.appendChild(el);
    } else if ((this.slice(-4) == '.css') && ($.inArray(this.toString(), hrefs) == -1)) {
        $('<link rel="stylesheet" type="text/css" href="' + this + '" />').prependTo('head');
        if (/* for IE */ document.createStyleSheet){document.createStyleSheet(this);} 
}});})(jQuery);""" % ('[%s]' % ','.join(["'%s'" % f.lower().split('?')[0] for f in files]))
    else:
        current.response.files[:0] = [f for f in files if f not in current.response.files]
    
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
    def __init__(self, maxsize=255, minsize=0,
                 error_message='enter a file from %(min)g to %(max)g KB'):
        IS_LENGTH.__init__(self, maxsize, minsize, error_message)
        
    def _call(self, value): 
        return IS_LENGTH.__call__(self, value)
    def __call__(self, value): 
        if not value:
            return (value, translate(self.error_message) % dict(
                                min=self.minsize / 1024, max=self.maxsize / 1024))
        return (value, None)

def uploadify_widget(field, value, download_url=None, **attributes): 
    _set_files(FILES)
    
    _id = '%s_%s' % (field._tablename, field.name)
    input_el = INPUT(_id = _id, _name = field.name,
                     requires = field.requires, _type='hidden',)
            
    _file_id = '__uploadify__%s_%s' % (field._tablename, field.name)
    file_input_el = INPUT(_id = _file_id, _name = '__uploadify__%s' % field.name, _type='file')
        
    ajaxed = 'Filedata' in current.request.post_vars and current.request.post_vars.name == field.name
        
    fileext = '*.*'
    size_limit = 1000000000000
    
    requires = field.requires
        
    if type(requires) not in (list, tuple):
        requires = [requires]
    for i, r in enumerate(requires):
        
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
        
    script = SCRIPT("""
jQuery(function() { var t = 10; (function run() {if ((function() {
var file_el = jQuery('#%(file_id)s');
if (file_el.uploadify == undefined) { return true; }

var uploadify_uploading = [];
var uploadify_uploaded = [];
var el = jQuery('#%(id)s');

var form_el = jQuery(el.get(0).form);
jQuery.fn.bindFirst = function(name, fn) {
    this.bind(name, fn);
    var handlers = this.data('events')[name.split('.')[0]];
    var handler = handlers.pop();
    handlers.splice(0, 0, handler);
};
form_el.bindFirst('submit', function (e) {
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
var scriptData = {'name': el.attr('name')};
var extraVars = %(extra_vars)s
for (key in extraVars) {
    scriptData[key] = extraVars[key];
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
    'scriptData': scriptData
});
})()) {setTimeout(run, t); t = 2*t;}})();});
""" % dict(id=_id, file_id=_file_id, 
           button_text=BUTTON_TEXT,
           uploader=URL('static', 'plugin_uploadify_widget/uploadify.swf'),
           script=URL(args=current.request.args),
           extra_vars=json.dumps(attributes.get('extra_vars', {})),
           cancel_img=URL('static', 'plugin_uploadify_widget/cancel.png'),
           fileext=fileext,
           size_limit=size_limit,
           ajax='true' if current.request.ajax else 'false',
         ))
         
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
