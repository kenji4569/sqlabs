# -*- coding: utf-8 -*-
from gluon import *

def _set_files():
    for _url in ( URL('static', 'plugin_uploadify_widget/uploadify.css'),
                  URL('static', 'plugin_uploadify_widget/swfobject.js'),
                  URL('static', 'plugin_uploadify_widget/jquery.uploadify.v2.1.4.min.js'),
                  URL('static', 'plugin_uploadify_widget/uploadify.css'),
                 ):
        if _url not in current.response.files:
            current.response.files.append(_url)
            
def uploadify_widget(field, value, download_url=None, **attributes): 
    _set_files()
    
    _id = '%s_%s' % (field._tablename, field.name)
    input_el = INPUT(_id = _id, _name = field.name,
                     requires = field.requires, _type='hidden',)
            
    _file_id = '__uploadify__%s_%s' % (field._tablename, field.name)
    file_input_el = INPUT(_id = _file_id, _name = '__uploadify__%s' % field.name, _type='file')
            
    script = SCRIPT("""
jQuery(document).ready(function() {
var el = jQuery('#%(id)s');
var file_el = jQuery('#%(file_id)s');
var form = jQuery(el.get(0).form);
file_el.uploadify({
'uploader'  : '%(uploader)s',
'script'    : '%(script)s',
'cancelImg' : '%(cancel_img)s',
'auto'      : true,
'scriptData': {'formkey': form.find('input[name=_formkey]').val(),
               'formname': form.find('input[name=_formname]').val()},
'onComplete'  : function(event, ID, fileObj, response, data) {
      el.val(response);
    }
});

});""" % dict(id=_id, file_id=_file_id, 
              uploader=URL('static', 'plugin_uploadify_widget/uploadify.swf'),
              script=URL(args=current.request.args, vars=current.request.vars),
              cancel_img=URL('static', 'plugin_uploadify_widget/cancel.png'),
         ))
          
    print field.uploadfolder
    if 'Filedata' in current.request.post_vars:
        print '===' # TODO verify
        print current.session
        print current.request.post_vars
        f = current.request.post_vars.Filedata
        newfilename = field.store(f.file, f.filename)
        raise HTTP(200, newfilename)
        
    if '_formkey' in current.request.vars:
        field.type = 'string'
            
    return DIV(script, input_el, file_input_el, **attributes)
