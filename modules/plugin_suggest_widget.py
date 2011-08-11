# -*- coding: utf-8 -*-
from gluon import *
from gluon.sqlhtml import AutocompleteWidget

class suggest_widget(AutocompleteWidget):
    def callback(self):
        print self.keyword
        if self.keyword in self.request.vars:
            field = self.fields[0]
            rows = self.db(field.like(self.request.vars[self.keyword]+'%'))\
                .select(orderby=self.orderby,limitby=self.limitby,*self.fields)
            if rows:
                if self.is_reference:
                    id_field = self.fields[1]
                    raise HTTP(200,UL(*[LI(B(s[field.name]), SPAN(s[id_field.name])) \
                                                for s in rows]).xml())
                else:
                    raise HTTP(200,UL(*[LI(B(s[field.name])) for s in rows]).xml())
            else:
                raise HTTP(200,'')
                
    def __call__(self,field,value,**attributes):
        current.response.files.append(URL('static','plugin_suggest_widget/suggest.css'))
        current.response.files.append(URL('static','plugin_suggest_widget/suggest.js'))
        
        default = dict(
            _type = 'text',
            value = (value!=None and str(value)) or '',
            )
        attr = SQLFORM.widgets.string._attributes(field, default, **attributes)
        div_id = '%s__div' % self.keyword
        attr['_autocomplete']='off'
        if self.is_reference:
            key2 = '%s__aux' % self.keyword
            key3 = '%s__auto' % self.keyword
            attr['_class']='text_32'
            if 'requires' in attr: del attr['requires']
            attr['_name'] = key2
            value = attr['value']
            record = self.db(self.fields[1]==value).select(self.fields[0]).first()
            attr['value'] = record and record[self.fields[0].name]
            attr['_onfocus'] = ("""
jQuery('#%(id)s').suggest(
    '%(url)s',{name:'%(name)s', keyword:'%(keyword)s', 
               resultsId:'%(div_id)s', minchars:'%(min_length)s'})""" % 
                             dict(id=attr['_id'], url=self.url, name=field.name, div_id=div_id,
                                  keyword=self.keyword, min_length=self.min_length))
            return TAG[''](INPUT(**attr),INPUT(_type='hidden',_id=key3,_value=value,
                                               _name=field.name,requires=field.requires),
                           DIV(_id=div_id,_style='position:absolute;'))
        else:
            attr['_name']=field.name
            attr['_onfocus'] = ("""
jQuery('#%(id)s').suggest(
    '%(url)s',{keyword:'%(keyword)s', 
               resultsId:'%(div_id)s', minchars:'%(min_length)s'})""" %
                             dict(id=attr['_id'], url=self.url, div_id=div_id,
                                  keyword=self.keyword, min_length=self.min_length))
            return TAG[''](INPUT(**attr),DIV(_id=div_id,_style='position:absolute;'))
            