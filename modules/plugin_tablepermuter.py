# -*- coding: utf-8 -*-
# This plugins is licensed under the MIT license: http://www.opensource.org/licenses/mit-license.php
# Authors: Kenji Hosoda <hosoda@s-cubism.jp>
from gluon import *

class TablePermuter(FORM):

    def __init__(self, table_id, submit_button='Update permutations',
                 renderstyle=False, tablepermuter_var='tablepermuter', **attributes):
        FORM.__init__(self, **attributes)
        self.attributes['_class'] = 'tablepermuter'
        self.table_id, self.tablepermuter_var, self.submit_button = (
            table_id, tablepermuter_var, submit_button)
        self._button = '%s_button' % self.tablepermuter_var
            
        _urls = [URL('static','plugin_tablepermuter/jquery.tablednd_0_5.js')]
        if renderstyle:
            _urls.append(URL('static','plugin_tablepermuter/tablepermuter.css'))
        for _url in _urls:
            if _url not in current.response.files:
                current.response.files.append(_url)
        
        self.append(SCRIPT("""
jQuery(document).ready(function(){
    jQuery("#%(table_id)s tbody").tableDnD({
        onDragClass: "tablepermuter_dragging",
        onDrop: function(table, row) {$("#%(button)s").prop('disabled', false);}
    });
    var row_idx = 0;
    jQuery("#%(table_id)s tbody tr").each(function(){
        jQuery.data(this, "row_idx", row_idx++);
    });
});""" % dict(table_id=self.table_id, button=self._button)))
        self.append(INPUT(_type='hidden', _name=self.tablepermuter_var))
        self.append(INPUT(_type='submit', _value=self.submit_button, 
              _onclick=self._get_submit_js(),
              _id=self._button, _disabled='disabled'))
          
    def accepts(self, *args, **kwds):
        accepted = FORM.accepts(self, *args, **kwds)
        if accepted:
            self.vars[self.tablepermuter_var] = map(int, 
                        current.request.vars[self.tablepermuter_var].split(','))
        return accepted
        
    def xml(self): 
        return FORM.xml(self) 
      
    def _get_submit_js(self):
        return """
var val = [];
jQuery("#%(table_id)s tbody tr").each(function(){
    val.push(jQuery.data(this, "row_idx"));
});
jQuery("input[name=%(tablepermuter)s]").val(val);
""" % dict(table_id=self.table_id, tablepermuter=self.tablepermuter_var)
