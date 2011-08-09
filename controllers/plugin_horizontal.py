# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

def horizontal_widget():
    form = SQLFORM(db.horizontal_demo)
    
    code = CODE(
"""def horizontal_radio_widget(field, value): 
    rows = SQLFORM.widgets.radio.widget(field,value).elements('tr') 
    inner = []
    for row in rows:
        elem = row.elements('td')[0]
        button = elem[0]
        label = elem[1]
        label = SPAN(label, 
                     _onclick='jQuery(this).parent().children("input").click();', _style='cursor:pointer;')
        inner.append(SPAN(button, ' ', label, _style='padding-right:10px;'))
    return DIV(*inner)""")
    return dict(form=form, code=code)

def horizontal_radio_widget(field, value): 
    rows = SQLFORM.widgets.radio.widget(field,value).elements('tr') 
    inner = []
    for row in rows:
        elem = row.elements('td')[0]
        button = elem[0]
        label = elem[1]
        label = SPAN(label, 
                     _onclick='jQuery(this).parent().children("input").click();', _style='cursor:pointer;')
        inner.append(SPAN(button, ' ', label, _style='padding-right:10px;'))
    return DIV(*inner)

db.define_table('horizontal_demo',
   Field('bank_account_type', 'integer', label='口座区分', 
          requires=IS_EMPTY_OR(IS_IN_SET([(1, '普通'), (2, '当座')])), 
          widget=horizontal_radio_widget))
