# -*- coding: utf-8 -*-
from gluon import *

class ElrteWidget(object):
    
    def __init__(self, lang=None):
        self.lang = lang

    def __call__(self, field, value):   
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
                
        if current.request.vars.description == '&nbsp;':
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
    elRTE.prototype.options.panels.web2pyPanel1 = [
        'pastetext', 'pasteformattext', 'removeformat', 'undo', 'redo'];
    elRTE.prototype.options.panels.web2pyPanel2 = [
        'formatblock', 'fontsize', 'fontname'];
    elRTE.prototype.options.panels.web2pyPanel3 = [
        'bold', 'italic', 'underline', 'strikethrough', 'subscript', 'superscript'];
    elRTE.prototype.options.panels.web2pyPanel4 = [
        'forecolor', 'hilitecolor', 'justifyleft', 'justifyright',
        'justifycenter', 'justifyfull', 'outdent', 'indent'];
    elRTE.prototype.options.panels.web2pyPanel5 = [
    'link', 'unlink', 'image', 'insertorderedlist', 'insertunorderedlist',
    'horizontalrule', 'blockquote', 'div', 'stopfloat', 'css', 'nbsp'];
    elRTE.prototype.options.toolbars.web2pyToolbar = [
        'web2pyPanel1', 'web2pyPanel2', 'web2pyPanel3', 
        'web2pyPanel4', 'web2pyPanel5', 'tables'];
    $('#%(id)s').elrte({cssClass: 'el-rte', lang: '%(lang)s', toolbar:  'web2pyToolbar'});
});})(jQuery);""" % dict(id=_id, lang=self.lang or ''))

        return SPAN(script, TEXTAREA((value!=None and str(value)) or '', **attr))
       