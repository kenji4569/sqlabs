# -*- coding: utf-8 -*-
# This plugins is licensed under the MIT license: http://www.opensource.org/licenses/mit-license.php
# Authors: Kenji Hosoda <hosoda@s-cubism.jp>
from gluon import *

# For referencing static and views from other application
import os
APP = os.path.basename(os.path.dirname(os.path.dirname(__file__)))

class DIALOG(DIV):
        
    def __init__(self, content, title=None, close_button=None,
                 width=90, height=80, onclose='', renderstyle=False, **attributes):
        DIV.__init__(self, **attributes)
        self.title, self.content, self.close_button, self.width, self.height, self.onclose = (
            title, content, close_button, width, height, onclose)
        self.attributes['_class'] = self.attributes.get('_class', 'dialog')
        
        import uuid
        self.attributes['_id'] = self.attributes.get('_id') or str(uuid.uuid4())
        self.attributes['_style'] = self.attributes.get('_style',
            'display:none; z-index:1001; position:fixed; top:0%;left:0%;width:100%;height:100%;')
        
        if renderstyle:
            _url = URL(APP, 'static', 'plugin_dialog/dialog.css')
            if _url not in current.response.files:
                current.response.files.append(_url)
                
    def show(self, reload=False):
        import gluon.contrib.simplejson as json
        return ("""(function(){
var el = jQuery("#%(id)s");""" +
    ("""
el.remove(); el = [];
    """ if reload else '') +
"""
if (el.length == 0) {
    el = jQuery(%(xml)s); jQuery(document.body).append(el);
}
el.css('zIndex', (parseInt(el.css('zIndex')) || 1000) + 10);
el.show();})();""") % dict(id=self.attributes['_id'],
                       xml=json.dumps(self.xml().replace('<!--', '').replace('//-->', '')))
        
    def close(self):
        return '%s;jQuery("#%s").hide();' % (self.onclose, self.attributes['_id'])
        
    def xml(self):
        self.components += [
            DIV(_style='width:100%;height:100%;',
                _class='dialog-back',
                _onclick='%s;return false;' % self.close()),
            DIV(DIV(
                SPAN(self.title, _style='font-weight:bold:font-size:18px;') if self.title else '',
                SPAN('[', A(self.close_button, _href='#', _onclick='%s;return false;' % self.close()), ']',
                     _style='float:right'
                     ) if self.close_button else '',
                HR() if self.title else '',
                self.content, _id='c%s' % self.attributes['_id'],
                    _style=("""
position:absolute;top:%(top)s%%;left:%(left)s%%;
width:%(width)s%%;height:%(height)s%%;
z-index:1100;overflow:auto;
""" % dict(left=(100 - self.width) / 2, top=(100 - self.height) / 2, width=self.width, height=self.height)),
                    _class='dialog-front',
                    _onclick="""
var e = arguments[0] || window.event;
if (jQuery(e.target).parent().attr('id') == "c%s") {%s;};
""" % (self.attributes['_id'], self.close())
                ),
            )]
        return DIV.xml(self)
