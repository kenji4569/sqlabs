# -*- coding: utf-8 -*-
# This plugins is licensed under the MIT license: http://www.opensource.org/licenses/mit-license.php
# Authors: Kenji Hosoda <hosoda@s-cubism.jp>
# original by http://groups.google.com/group/web2py/browse_frm/thread/d1ec3ded48839071#
from gluon import *

class Paginator(DIV): 

    def __init__(self, pagenate=10, records=100, 
                 renderstyle=False, page_var='page', **attributes):
        DIV.__init__(self, **attributes)
        self.attributes['_class'] = 'paginator'
        self.pagenate, self.records, self.page_var = (
            pagenate, records, page_var
        )
        self.page = int(current.request.get_vars.get(self.page_var) or 1)
        
        if renderstyle:
            _url = URL('static','plugin_paginator/paginator.css')
            if _url not in current.response.files:
                current.response.files.append(_url)
            
    def _url(self, page):
        vars = current.request.get_vars.copy()
        vars[self.page_var] = page
        return URL(args=current.request.args, vars=vars)

    def limitby(self): 
        return (self.pagenate*(self.page-1), self.pagenate*self.page)
      
    def xml(self): 
        pages = (self.records - 1) / self.pagenate + 1
        if (self.records > self.pagenate and
            pages == 1 and pages * self.pagenate != self.records):
            pages = 2
        elif pages == 0 and self.records != 0:
            pages = 1 
        
        if pages > 1:
            def _get_page_el(page):
                if self.page == page:
                    return EM(page)
                else:
                    return A(page, _title=page, 
                              _href=self._url(page))
                              
            if self.page != 1:
                self.append(
                    A(current.T('Prev') , _href=self._url(self.page - 1),
                         _title=(self.page - 1), _class='previous_page'))
                
            _pad_prev = 2
            _pad_next = 3 if self.page>3 else 7-self.page
            if self.page-_pad_prev > 1:
                self.append(_get_page_el(1))
                if self.page - _pad_prev > 2:
                    self.append(SPAN('... '))
                elif self.page - _pad_prev == 1:
                    self.append(_get_page_el(2))
            for page in range(max(self.page - _pad_prev, 1), 
                                   min(self.page + _pad_next, pages + 1)):
                self.append(_get_page_el(page))
            if self.page+_pad_next <= pages:
                if self.page+_pad_next <= pages - 2:
                    self.append(SPAN('... '))
                elif self.page+_pad_next == pages - 1:
                    self.append(_get_page_el(pages - 1))
                self.append(_get_page_el(pages))
            
            if pages > self.page:
                self.append(
                    A(current.T('Next') , _href=self._url(self.page + 1),
                         _title=(self.page + 1), _class='next_page'))
            
        return DIV.xml(self) 
      
class PagenateSelector(SPAN):
    
    def __init__(self, pagenates=(10, 25, 50, 100),
                 pagenate_var='pagenate', page_var='page', **attributes):
        SPAN.__init__(self, **attributes)
        self.attributes['_class'] = 'pagenate_selector'
        self.pagenates, self.pagenate_var, self.page_var  = (
            pagenates, pagenate_var, page_var
        )
        self.pagenate = int(current.request.get_vars.get(self.pagenate_var, pagenates[0]))
        
    def _url(self, pagenate):
        vars = current.request.get_vars.copy()
        vars[self.page_var] = 1
        vars[self.pagenate_var] = pagenate
        return URL(args=current.request.args, vars=vars)
  
    def xml(self): 
        def _get_pagenate_link(_pagenate):
            if _pagenate == self.pagenate:
                return str(_pagenate)
            else:
                return A(_pagenate, _href=self._url(_pagenate)).xml()
        inner = XML(current.T('Paginate: ') +
                 ', '.join([_get_pagenate_link(_pagenate) for _pagenate in self.pagenates])) 
        return SPAN(inner, **self.attributes).xml()
                    
class PaginateInfo(SPAN):
    def __init__(self, page, pagenate, records, **attributes):
        SPAN.__init__(self, **attributes)
        self.attributes['_class'] = 'pagenate_info'
        self.page, self.pagenate, self.records  = (
            page, pagenate, records
        )
        
    def xml(self): 
        inner = XML(current.T('Display: <b>%(start)s - %(end)s</b> of <b>%(total)s</b>') % 
              dict(start=(self.page - 1)*self.pagenate + 1, end=self.page*self.pagenate, 
                   total=self.records))
        return SPAN(inner, **self.attributes).xml()
