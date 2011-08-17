# -*- coding: utf-8 -*-
from gluon import *
from gluon.sqlhtml import widget_class, FormWidget, StringWidget
import datetime

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

def _set_files():
    for _url in (URL('static','plugin_anytime_widget/anytime.css'),
                 URL('static','plugin_anytime_widget/anytime.js')):
        if _url not in current.response.files:
            current.response.files.append(_url)
         

def anytime_widget(field, value): 
    _set_files()
    _id = '%s_%s' % (field._tablename, field.name)
    attr = dict(
            _type = 'text', value = (value!=None and str(value)) or '',
            _id = _id, _name = field.name, requires = field.requires,
            _class = 'any%s' % widget_class.match(str(field.type)).group(),
            )
    script = SCRIPT("""
jQuery(document).ready(function() {  
jQuery("#%(id)s").AnyTime_picker( 
jQuery.extend({format: "%%H:%%i:%%S", labelTitle: "%(title)s", 
              labelHour: "%(hour)s", labelMinute: "%(minute)s", labelSecond: "%(second)s"}, 
              %(date_option)s))});
""" % dict(id=_id, title=current.T('Choose date time'), 
           hour=current.T('Hour'), minute=current.T('Minute'), second=current.T('Second'),
           date_option=_get_date_option()))
    
    return SPAN(script, INPUT(**attr))

    
def anydate_widget(field, value): 
    _set_files()
    _id = '%s_%s' % (field._tablename, field.name)
    attr = dict(
            _type = 'text', value = (value!=None and str(value)) or '',
            _id = _id, _name = field.name, requires = field.requires,
            _class = 'any%s' % widget_class.match(str(field.type)).group(),
            )
    script = SCRIPT("""
jQuery(document).ready(function() {  
jQuery("#%(id)s").AnyTime_picker( 
jQuery.extend({format: "%%Y-%%m-%%d", labelTitle: "%(title)s"}, 
              %(date_option)s))});
""" % dict(id=_id, title=current.T('Choose date time'), 
           date_option=_get_date_option()))
    
    return SPAN(script, INPUT(**attr))
    
def anydatetime_widget(field, value): 
    _set_files()
    _id = '%s_%s' % (field._tablename, field.name)
    attr = dict(
            _type = 'text', value = (value!=None and str(value)) or '',
            _id = _id, _name = field.name, requires = field.requires,
            _class = 'any%s' % widget_class.match(str(field.type)).group(),
            )
    script = SCRIPT("""
jQuery(document).ready(function() {  
jQuery("#%(id)s").AnyTime_picker( 
jQuery.extend({format: "%%Y-%%m-%%d %%H:%%i:00", labelTitle: "%(title)s", 
              labelHour: "%(hour)s", labelMinute: "%(minute)s"}, 
              %(date_option)s))});
""" % dict(id=_id, title=current.T('Choose date time'), 
           hour=current.T('Hour'), minute=current.T('Minute'),
           date_option=_get_date_option()))
    
    return SPAN(script, INPUT(**attr))
