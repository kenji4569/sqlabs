# -*- coding: utf-8 -*-
# This plugins is licensed under the MIT license: http://www.opensource.org/licenses/mit-license.php
# Authors: Kenji Hosoda <hosoda@s-cubism.jp>
from gluon import *
from gluon.sqlhtml import AutocompleteWidget

# For referencing static and views from other application
import os
APP = os.path.basename(os.path.dirname(os.path.dirname(__file__)))


class suggest_widget(AutocompleteWidget):

    def __init__(self, field, id_field=None, db=None,
                 orderby=None, limitby=(0, 10),
                 keyword='_autocomplete_%(fieldname)s',
                 min_length=2,
                 user_signature=False, hmac_key=None):
        self.keyword = keyword % dict(fieldname=field.name)
        self.db = db or field._db
        self.orderby, self.limitby, self.min_length = orderby, limitby, min_length
        self.user_signature, self.hmac_key = user_signature, hmac_key
        self.fields = [field]
        if id_field:
            self.is_reference = True
            self.fields.append(id_field)
        else:
            self.is_reference = False
            
        request = current.request
        if hasattr(request, 'application'):
            self.url = URL(r=request, args=request.args,
                           user_signature=user_signature, hmac_key=hmac_key)
            self.callback()
        else:
            self.url = request

    def _create_item(self, field, row):
        return B(row[field.name])
        
    def callback(self):
        if self.keyword in current.request.vars:
            if self.user_signature:
                if not URL.verify(current.request, user_signature=self.user_signature, hmac_key=self.hmac_key):
                    raise HTTP(400)
                    
            field = self.fields[0]
            rows = self.db(field.like(current.request.vars[self.keyword] + '%')
                          ).select(orderby=self.orderby, limitby=self.limitby, *self.fields)
            if rows:
                if self.is_reference:
                    id_field = self.fields[1]
                    raise HTTP(200, UL(*[LI(self._create_item(field, row), SPAN(row[id_field.name]))
                                                            for row in rows]).xml())
                else:
                    raise HTTP(200, UL(*[LI(self._create_item(field, row)) for row in rows]).xml())
            else:
                raise HTTP(200, '')
                
    def __call__(self, field, value, **attributes):
        for _url in (URL(APP, 'static', 'plugin_suggest_widget/suggest.css'),
                     URL(APP, 'static', 'plugin_suggest_widget/suggest.js')):
            if _url not in current.response.files:
                current.response.files.append(_url)
        
        default = dict(
            _type='text',
            value=(value != None and str(value)) or '',
            )
        attr = SQLFORM.widgets.string._attributes(field, default, **attributes)
        div_id = '%s__div' % self.keyword
        attr['_autocomplete'] = 'off'
        if self.is_reference:
            key2 = '%s__aux' % self.keyword
            key3 = '%s__auto' % self.keyword
            attr['_class'] = 'text_32'
            if 'requires' in attr:
                del attr['requires']
            attr['_name'] = key2
            value = attr['value']
            record = self.db(self.fields[1] == value).select(self.fields[0]).first()
            attr['value'] = record and record[self.fields[0].name]
            attr['_onfocus'] = ("""
jQuery('#%(id)s').suggest(
    '%(url)s',{name:'%(name)s', keyword:'%(keyword)s',
               resultsId:'%(div_id)s', minchars:'%(min_length)s'})""" %
                             dict(id=attr['_id'], url=self.url, name=field.name, div_id=div_id,
                                  keyword=self.keyword, min_length=self.min_length))
            return TAG[''](INPUT(**attr), INPUT(_type='hidden', _id=key3, _value=value,
                                               _name=field.name, requires=field.requires),
                           DIV(_id=div_id, _style='position:absolute;'))
        else:
            attr['_name'] = field.name
            attr['_onfocus'] = ("""
jQuery('#%(id)s').suggest(
    '%(url)s',{keyword:'%(keyword)s',
               resultsId:'%(div_id)s', minchars:'%(min_length)s'})""" %
                             dict(id=attr['_id'], url=self.url, div_id=div_id,
                                  keyword=self.keyword, min_length=self.min_length))
            return TAG[''](INPUT(**attr), DIV(_id=div_id, _style='position:absolute;'))
