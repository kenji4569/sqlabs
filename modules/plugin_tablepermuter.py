# -*- coding: utf-8 -*-
# This plugins is licensed under the MIT license: http://www.opensource.org/licenses/mit-license.php
# Authors: Kenji Hosoda <hosoda@s-cubism.jp>
from gluon import *

# For referencing static and views from other application
import os
APP = os.path.basename(os.path.dirname(os.path.dirname(__file__)))


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


class TablePermuter(FORM):

    def __init__(self, table_id, submit_button='Update permutations',
                 renderstyle=False, keyword='tablepermuter',
                 buttons=['submit'],
                 callback=None, **attributes):
        FORM.__init__(self, **attributes)
        self.attributes['_class'] = 'tablepermuter'
        self.table_id, self.keyword, self.submit_button = (
            table_id, keyword, submit_button)
            
        _files = [URL(APP, 'static', 'plugin_tablepermuter/jquery.tablednd_0_5.js')]
        if renderstyle:
            _files.append(URL(APP, 'static', 'plugin_tablepermuter/tablepermuter.css'))
        _set_files(_files)
        
        _callback = callback or ''
        if 'submit' in buttons:
            # TODO elif buttons: ... = DIV(*buttons)
            _button = '%s_button' % self.keyword
            _callback += ';$("#%s").prop("disabled", false);' % _button
            self.append(INPUT(_type='hidden', _name=self.keyword))
            self.append(INPUT(_type='submit', _value=self.submit_button,
                  _onclick=self._get_submit_js(),
                  _id=_button, _disabled='disabled'))
        
        self.append(SCRIPT("""
jQuery(function() { var t = 10; (function run() {if ((function() {
    var el = jQuery("#%(table_id)s tbody");
    if (el.tableDnD == undefined) { return true; }
    el.tableDnD({
        onDragClass: "tablepermuter_dragging",
        onDrop: function(table, row) {%(callback)s}
    });
    var row_idx = 0;
    jQuery("#%(table_id)s tbody tr").each(function(){
        jQuery.data(this, "row_idx", row_idx++);
    });
})()) {setTimeout(run, t); t = 2*t;}})();});
""" % dict(table_id=self.table_id,
           callback=_callback)))
        
    def accepts(self, *args, **kwds):
        accepted = FORM.accepts(self, *args, **kwds)
        if accepted:
            self.vars[self.keyword] = map(int,
                        current.request.vars[self.keyword].split(','))
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
""" % dict(table_id=self.table_id, tablepermuter=self.keyword)
