# -*- coding: utf-8 -*-
# This plugins is licensed under the MIT license: http://www.opensource.org/licenses/mit-license.php
# Authors: Kenji Hosoda <hosoda@s-cubism.jp>
from gluon import *

class ElrteWidget(object):
    
    def __init__(self, lang=None, toolbar='default', fm_open="''"):
        self.lang, self.toolbar, self.fm_open = lang, toolbar, fm_open

    def __call__(self, field, value, **attributes):   
        _urls = [URL('static','plugin_elrte_widget/css/smoothness/jquery-ui-1.8.13.custom.css'),
                 URL('static','plugin_elrte_widget/css/elrte.min.css'),
                 URL('static','plugin_elrte_widget/css/elrte-inner.css'),
                 URL('static','plugin_elrte_widget/js/jquery-ui-1.8.13.custom.min.js'),
                 URL('static','plugin_elrte_widget/js/elrte.min.js')]
        if self.lang:
            _urls.append(URL('static','plugin_elrte_widget/js/i18n/elrte.%s.js' % self.lang))        
         
        for _url in _urls:
            if _url not in current.response.files:
                current.response.files.append(_url)
                
        if current.request.vars.description in ('<p>&nbsp;</p>', '&nbsp;'):
            current.request.vars.description = ''
        if current.request.vars.description:
            current.request.vars.description = current.request.vars.description.strip(' ')
        
        _id = '%s_%s' % (field._tablename, field.name)
        attr = dict(
                _id = _id, _name = field.name, requires = field.requires,
                _class = 'text',
                )
                
        script = SCRIPT(""" 
(function($) {
$(document).ready(function() {
var opts = elRTE.prototype.options;
opts.panels.default_1 = ['pastetext', 'pasteformattext', 'removeformat', 'undo', 'redo'];
opts.panels.default_2 = ['formatblock', 'fontsize', 'fontname'];
opts.panels.default_3 = ['bold', 'italic', 'underline', 'strikethrough', 'subscript', 'superscript'];
opts.panels.default_4 = ['forecolor', 'hilitecolor', 'justifyleft', 'justifyright',
                  'justifycenter', 'justifyfull', 'outdent', 'indent'];
opts.panels.default_5 = ['link', 'unlink', 'image', 'insertorderedlist', 'insertunorderedlist',
                  'horizontalrule', 'blockquote', 'div', 'stopfloat', 'css', 'nbsp'];
opts.toolbars = {'default': ['default_1', 'default_2', 'default_3', 'default_4', 'default_5', 'tables']};

if(typeof String.prototype.trim !== 'function') {
  String.prototype.trim = function() {
    return this.replace(/^\s+|\s+$/g, ''); 
  }
}
var el = $('#%(id)s');
if(!$.support.opacity){
   if (el.text() == '') { el.text('<p>&nbsp;</p>')} 
}
el.elrte({cssClass: 'el-rte', lang: '%(lang)s', toolbar: '%(toolbar)s', fmOpen : %(fm_open)s }); 
});})(jQuery);""" % dict(id=_id, lang=self.lang or '', toolbar=self.toolbar, fm_open=self.fm_open))
        
        return SPAN(script, TEXTAREA((value!=None and str(value)) or '', **attr), **attributes)
       