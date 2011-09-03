# -*- coding: utf-8 -*-
# This plugins is licensed under the MIT license: http://www.opensource.org/licenses/mit-license.php
# Authors: Kenji Hosoda <hosoda@s-cubism.jp>
from gluon import *
from gluon.sqlhtml import widget_class, FormWidget, StringWidget
import datetime

NAME = 'plugin_anytime_widget'
FILES = (URL('static','plugin_anytime_widget/anytime.css'),
         URL('static','plugin_anytime_widget/anytime.js'))

def _init(name, files):
    common = """function web2py_plugin_init(name, files) {
var $ = jQuery, n = 0, plugins = $.data(document.body, 'web2py_plugins');
function _set_plugin(value) {plugins[name] = value; $.data(document.body, 'web2py_plugins', plugins);}
function _trigger() {$(document).trigger(name);}
if (plugins == undefined) {plugins = {};} else if (name in plugins) {if (plugins[name] == true) {_trigger()} return;}
_set_plugin(false); if (files == undefined) {$(function(){_set_plugin(true); _trigger();}); return;}
$.each(files, function() {
    if (this.slice(-3) == '.js') {
        ++n; $.ajax({type: 'GET', url: this, success: function(d) {eval(d); --n;}, error: function() {--n;}});
    } else if (this.slice(-4) == '.css') {
        if (document.createStyleSheet){document.createStyleSheet(this);} // for IE
        else {$('<link rel="stylesheet" type="text/css" href="' + this + '" />').prependTo('head');}
    }});
$(function() {var t = setInterval(function() {if (n == 0) {_trigger(); _set_plugin(true); clearInterval(t);}}, 100);});
};"""
    if current.request.ajax:
        return SCRIPT(common + "web2py_plugin_init('%s', %s);" % (name, 
            '[%s]' % ','.join(["'%s'" % f.lower().split('?')[0] for f in files])))
    else:
        current.response.files[:0] = [f for f in files if f not in current.response.files]
        return SCRIPT(common + "web2py_plugin_init('%s');" % (name))

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
            
    script = SCRIPT("""jQuery(document).one('%(plugin)s', function() {
jQuery("#%(id)s").AnyTime_noPicker().AnyTime_picker(
    jQuery.extend({format: "%%H:%%i:%%S", labelTitle: "%(title)s", 
        labelHour: "%(hour)s", labelMinute: "%(minute)s", labelSecond: "%(second)s"}, 
        %(date_option)s));
});""" % dict(plugin=NAME, id=_id, title=current.T('Choose time'), 
           hour=current.T('Hour'), minute=current.T('Minute'), second=current.T('Second'),
           date_option=_get_date_option()))
    
    return SPAN(INPUT(**attr), script, _init(NAME, FILES), **attributes)

    
def anydate_widget(field, value, **attributes): 
    _id = '%s_%s' % (field._tablename, field.name)
    attr = dict(
            _type = 'text', value = (value!=None and str(value)) or '',
            _id = _id, _name = field.name, requires = field.requires,
            _class = 'any%s' % widget_class.match(str(field.type)).group(),
            )
           
    script = SCRIPT("""jQuery(document).one('%(plugin)s', function() {
jQuery("#%(id)s").AnyTime_noPicker().AnyTime_picker( 
    jQuery.extend({format: "%%Y-%%m-%%d", labelTitle: "%(title)s"}, 
                   %(date_option)s));
});""" % dict(plugin=NAME, id=_id, title=current.T('Choose date'), 
           date_option=_get_date_option()))
       
    return SPAN(INPUT(**attr), script, _init(NAME, FILES), **attributes)
    
def anydatetime_widget(field, value, **attributes): 
    _id = '%s_%s' % (field._tablename, field.name)
    attr = dict(
            _type = 'text', value = (value!=None and str(value)) or '',
            _id = _id, _name = field.name, requires = field.requires,
            _class = 'any%s' % widget_class.match(str(field.type)).group(),
            )
            
    script = SCRIPT("""jQuery(document).one('%(plugin)s', function() {
jQuery("#%(id)s").AnyTime_noPicker().AnyTime_picker( 
    jQuery.extend({format: "%%Y-%%m-%%d %%H:%%i:00", labelTitle: "%(title)s", 
                   labelHour: "%(hour)s", labelMinute: "%(minute)s"}, 
                   %(date_option)s));
});""" % dict(plugin='plugin_anytime_widget', id=_id, title=current.T('Choose date time'), 
           hour=current.T('Hour'), minute=current.T('Minute'),
           date_option=_get_date_option()))
    
    return SPAN(INPUT(**attr), script, _init(NAME, FILES), **attributes)
