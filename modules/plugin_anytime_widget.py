# -*- coding: utf-8 -*-
# This plugins is licensed under the MIT license: http://www.opensource.org/licenses/mit-license.php
# Authors: Kenji Hosoda <hosoda@s-cubism.jp>
from gluon import *
from gluon.sqlhtml import widget_class, FormWidget, StringWidget
import datetime

FILES = (URL('static','plugin_anytime_widget/anytime.css'),
         URL('static','plugin_anytime_widget/anytime.js'))

def _set_files(files):
    for f in files:
        if f not in current.response.files:
            current.response.files.append(f)
            
def _get_init_js(setup_js, core_js, check_js, files):
    if current.request.ajax:
        return """
var %(name)s_files = [];
function load_%(name)s_file(file) {
    if (%(name)s_files.indexOf(file) != -1) {return;}
    %(name)s_files.push(file);
    if (file.slice(-3) == '.js') {
        jQuery.get(file);
    } else if (file.slice(-4) == '.css') {
        jQuery('head').append(jQuery('<link rel="stylesheet" type="text/css" href="' + file + '">'));
    }
}
jQuery(document).ready(function() {  
    %(setup_js)s; var _interval = null;
    function _init() {%(core_js)s; if (_interval!=null) {clearInterval(_interval)}}
    if (%(check_js)s) {
        var files = %(files_code)s;
        for (var i=0; i<files.length; ++i) {
            load_%(name)s_file(files[i]);
        }
        _interval = setInterval(function(){if (!(%(check_js)s)){_init();}}, 100)
    } else{
        _init();
    }
});
""" % dict(name='plugin_anytime_widget', setup_js=setup_js, check_js=check_js, core_js=core_js, 
           files_code='[%s]' % ','.join(["'%s'" % f.lower().split('?')[0] for f in files]))
    else:
        return """
jQuery(document).ready(function() {%(setup_js)s;%(core_js)s;})
""" % dict(setup_js=setup_js, core_js=core_js)
             
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
    _set_files(FILES)
    _id = '%s_%s' % (field._tablename, field.name)
    attr = dict(
            _type = 'text', value = (value!=None and str(value)) or '',
            _id = _id, _name = field.name, requires = field.requires,
            _class = 'any%s' % widget_class.match(str(field.type)).group(),
            )
            
    setup_js = 'var el = jQuery("#%(id)s");' % dict(id=_id)
    core_js = """
el.AnyTime_picker(
    jQuery.extend({format: "%%H:%%i:%%S", labelTitle: "%(title)s", 
        labelHour: "%(hour)s", labelMinute: "%(minute)s", labelSecond: "%(second)s"}, 
        %(date_option)s));"""% dict(title=current.T('Choose time'), 
           hour=current.T('Hour'), minute=current.T('Minute'), second=current.T('Second'),
           date_option=_get_date_option())
    check_js = 'el.AnyTime_picker==undefined'
    
    init_js = _get_init_js(setup_js=setup_js, core_js=core_js, check_js=check_js, files=FILES)
    
    return SPAN(SCRIPT(init_js), INPUT(**attr), **attributes)

    
def anydate_widget(field, value, **attributes): 
    _set_files(FILES)
    _id = '%s_%s' % (field._tablename, field.name)
    attr = dict(
            _type = 'text', value = (value!=None and str(value)) or '',
            _id = _id, _name = field.name, requires = field.requires,
            _class = 'any%s' % widget_class.match(str(field.type)).group(),
            )
            
    setup_js = 'var el = jQuery("#%(id)s");' % dict(id=_id)
    core_js = """
el.AnyTime_picker( 
    jQuery.extend({format: "%%Y-%%m-%%d", labelTitle: "%(title)s"}, 
                   %(date_option)s));
""" % dict(id=_id, title=current.T('Choose date'), 
           date_option=_get_date_option())
    check_js = 'el.AnyTime_picker==undefined'
    
    init_js = _get_init_js(setup_js=setup_js, core_js=core_js, check_js=check_js, files=FILES)
       
    return SPAN(SCRIPT(init_js), INPUT(**attr), **attributes)
    
def anydatetime_widget(field, value, **attributes): 
    _set_files(FILES)
    _id = '%s_%s' % (field._tablename, field.name)
    attr = dict(
            _type = 'text', value = (value!=None and str(value)) or '',
            _id = _id, _name = field.name, requires = field.requires,
            _class = 'any%s' % widget_class.match(str(field.type)).group(),
            )
            
    setup_js = 'var el = jQuery("#%(id)s");' % dict(id=_id)
    core_js = """
el.AnyTime_picker( 
    jQuery.extend({format: "%%Y-%%m-%%d %%H:%%i:00", labelTitle: "%(title)s", 
                   labelHour: "%(hour)s", labelMinute: "%(minute)s"}, 
                   %(date_option)s));
""" % dict(id=_id, title=current.T('Choose date time'), 
           hour=current.T('Hour'), minute=current.T('Minute'),
           date_option=_get_date_option())
    check_js = 'el.AnyTime_picker==undefined'
    
    init_js = _get_init_js(setup_js=setup_js, core_js=core_js, check_js=check_js, files=FILES)
       
    return SPAN(SCRIPT(init_js), INPUT(**attr), **attributes)
