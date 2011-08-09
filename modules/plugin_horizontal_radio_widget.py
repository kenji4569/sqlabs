# -*- coding: utf-8 -*-
from gluon import *

def horizontal_radio_widget(field, value): 
    rows = SQLFORM.widgets.radio.widget(field,value).elements('tr') 
    inner = []
    for row in rows:
        button, label = row.elements('td')[0]
        button.attributes['_style'] = 'cursor:pointer;'
        inner.append(SPAN(button, ' ', 
                          SPAN(label, _onclick='jQuery(this).parent().children("input").click();', 
                               _style='cursor:pointer;'), 
                          _style='padding-right:10px;'))
    return DIV(*inner)
