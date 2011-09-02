# -*- coding: utf-8 -*-
# This plugins is licensed under the MIT license: http://www.opensource.org/licenses/mit-license.php
# Authors: Kenji Hosoda <hosoda@s-cubism.jp>
from gluon import *
from gluon.sqlhtml import widget_class, FormWidget, StringWidget
import datetime

FILES = (URL('static','plugin_anytime_widget/anytime.css'),
         URL('static','plugin_anytime_widget/anytime.js'))

def _plugin_init(name, callback, files):
    js = """
function web2py_plugin_init(name, callback, files) {
    var plugins = jQuery.data(document.body, 'web2py_plugins');
    function _set_plugins(plugins) { jQuery.data(document.body, 'web2py_plugins', plugins); }
    if (plugins == undefined) { plugins = {}; }
    if (name in plugins) {
        if (plugins[name].loaded == true) {jQuery(callback); return; }
        else {plugins[name].callbacks.push(callback); _set_plugins(plugins); return; }
    }
    if (files == undefined) {
        plugins[name] = {loaded: true}; _set_plugins(plugins); jQuery(callback); return;
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
    jQuery(function() { 
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
             
def _get_date_option():
    return """{
labelYear: "%(year)s", labelMonth: "%(month)s", labelDay: "%(day)s", 
labelDayOfMonth: "%(calendar)s",
monthAbbreviations: ["%(jan)s", "%(feb)s", "%(mar)s",
  "%(apr)s", "%(may)s", "%(jun)s",  "%(jul)s",
  "%(aug)s", "%(sep)s", "%(oct)s", "%(nov)s", "%(dec)s"],
dayAbbreviations: ["%(sun)s", "%(mon)s", "%(tue)s", "%(wed)s", 
                   "%(thu)s", "%(fri)s", "%(sat)s"],
labelDismiss: "%(ok)s" }""" % dict(
        year=current.T('Year'), month=current.T('Month'), day=current.T('Day'),
        calendar=current.T('Calendar'),
        jan=current.T('Jan'), feb=current.T('Feb'), mar=current.T('Mar'),
        apr=current.T('Apr'), may=current.T('May'), jun=current.T('Jun'),
        jul=current.T('Jul'), aug=current.T('Aug'), sep=current.T('Sep'),
        oct=current.T('Oct'), nov=current.T('Nov'), dec=current.T('Dec'),
        sun=current.T('Sun'), mon=current.T('Mon'), tue=current.T('Tue'),
        wed=current.T('Wed'), thu=current.T('Thu'), fri=current.T('Fri'),
        sat=current.T('Sat'), ok=current.T('OK'), 
    )

def anytime_widget(field, value, **attributes): 
    _id = '%s_%s' % (field._tablename, field.name)
    attr = dict(
            _type = 'text', value = (value!=None and str(value)) or '',
            _id = _id, _name = field.name, requires = field.requires,
            _class = 'any%s' % widget_class.match(str(field.type)).group(),
            )
            
    callback = """function() {
jQuery("#%(id)s").AnyTime_picker(
    jQuery.extend({format: "%%H:%%i:%%S", labelTitle: "%(title)s", 
        labelHour: "%(hour)s", labelMinute: "%(minute)s", labelSecond: "%(second)s"}, 
        %(date_option)s));
}""" % dict(id=_id, title=current.T('Choose time'), 
           hour=current.T('Hour'), minute=current.T('Minute'), second=current.T('Second'),
           date_option=_get_date_option())
    
    script = SCRIPT(_plugin_init('plugin_anytime_widget', callback=callback, files=FILES))
    
    return SPAN(script, INPUT(**attr), **attributes)

    
def anydate_widget(field, value, **attributes): 
    _id = '%s_%s' % (field._tablename, field.name)
    attr = dict(
            _type = 'text', value = (value!=None and str(value)) or '',
            _id = _id, _name = field.name, requires = field.requires,
            _class = 'any%s' % widget_class.match(str(field.type)).group(),
            )
            
    callback = """function() {
jQuery("#%(id)s").AnyTime_picker( 
    jQuery.extend({format: "%%Y-%%m-%%d", labelTitle: "%(title)s"}, 
                   %(date_option)s));
}""" % dict(id=_id, title=current.T('Choose date'), 
           date_option=_get_date_option())
    
    script = SCRIPT(_plugin_init('plugin_anytime_widget', callback=callback, files=FILES))
       
    return SPAN(script, INPUT(**attr), **attributes)
    
def anydatetime_widget(field, value, **attributes): 
    _id = '%s_%s' % (field._tablename, field.name)
    attr = dict(
            _type = 'text', value = (value!=None and str(value)) or '',
            _id = _id, _name = field.name, requires = field.requires,
            _class = 'any%s' % widget_class.match(str(field.type)).group(),
            )
            
    callback = """function() {
jQuery("#%(id)s").AnyTime_picker( 
    jQuery.extend({format: "%%Y-%%m-%%d %%H:%%i:00", labelTitle: "%(title)s", 
                   labelHour: "%(hour)s", labelMinute: "%(minute)s"}, 
                   %(date_option)s));
}""" % dict(id=_id, title=current.T('Choose date time'), 
           hour=current.T('Hour'), minute=current.T('Minute'),
           date_option=_get_date_option())
    
    script = SCRIPT(_plugin_init('plugin_anytime_widget', callback=callback, files=FILES))
       
    return SPAN(script, INPUT(**attr), **attributes)
