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
opts.panels.default_5 = ['link', 'unlink', 'image', 'elfinder','insertorderedlist', 'insertunorderedlist',
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
       
class Dialog(DIV):
        
    def __init__(self, title, content, close='close', width=70, height=70, **attributes):
        DIV.__init__(self, **attributes)
        self.title, self.content, self.close, self.width, self.height = (
            title, content, close, width, height)
        self.attributes['_class'] = 'dialog'
        import uuid
        self.attributes['_id'] = self.attributes.get('_id') or str(uuid.uuid4())
        self.attributes['_style'] = self.attributes.get('_style', 'display:none;z-index:1001;position:absolute;top:0%;left:0%;width:100%;height:100%;')
        
    def get_show_js(self):
        import gluon.contrib.simplejson as json
        return """(function(){
var el = jQuery("#%(id)s");
if (el.length == 0) {el = jQuery(%(xml)s); jQuery(document.body).append(el);}
el.css('zIndex', (parseInt(el.css('zIndex')) || 1000) + 10);
var top  = jQuery(document).scrollTop();
el.css('top', top);
el.show();})"""  % dict(id=self.attributes['_id'], 
                       xml=json.dumps(self.xml().replace('<!--', '').replace('//-->', '')))
        
    def xml(self): 
        self.components += (
            DIV(_style='background-color:black;-moz-opacity:0.5;opacity:.50;opacity:0.5;width:100%;height:100%;',
                _class='dialog-back'),
            DIV(SPAN(self.title, _style='font-weight:bold'),
                SPAN('[', A(self.close, _href='#', 
                           _onclick="jQuery('#%s').hide();return false;" % self.attributes['_id']), ']', 
                     _style='float:right',),
                HR(),
                DIV(self.content, _id='c%s' % self.attributes['_id']),
                _style=('position:absolute;top:%(top)s%%;left:%(left)s%%;width:%(width)s%%;height:%(height)s%%;padding:16px;border:2px solid black;background-color:white;opacity:1.0;z-index:1002;overflow:auto;' %
                    dict(left=(100-self.width)/2,top=(100-self.height)/2,width=self.width,height=self.height)),
                _class='dialog-front',
            ),
        )
        return DIV.xml(self)
