# -*- coding: utf-8 -*-
# This plugins is licensed under the MIT license: http://www.opensource.org/licenses/mit-license.php
# Authors: Kenji Hosoda <hosoda@s-cubism.jp>
from gluon import *
from gluon.storage import Storage

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


class RatingWidget(object):

    def __init__(self):
        settings = self.settings = Storage()
        settings.files = None

    def __call__(self, field, value, **attributes):
        if self.settings.files is None:
            _files = [URL(APP, 'static', 'plugin_rating_widget/rating_widget.css'),
                      URL(APP, 'static', 'plugin_rating_widget/jquery.rating.pack.js')]
        else:
            _files = self.settings.files
        _set_files(_files)
             
        _id = '%s_%s' % (field._tablename, field.name)
        attr = dict(_id=_id, _name=field.name, requires=field.requires, _class='text')
              
        opts = [INPUT(_type='radio', _name=field.name, _value=k, value=value, _class='star')
                for k, v in field.requires.options() if str(v)]
                
        script = SCRIPT("""
jQuery(function() { var t = 10; (function run() {if ((function() {
    var el = jQuery('#%(id)s .star');
    if (el.rating == undefined) { return true; }
    el.rating();
})()) {setTimeout(run, t); t = 2*t;}})();});
""" % dict(id=_id))
        
        return SPAN(script, SPAN(*opts, **attr), **attributes)
