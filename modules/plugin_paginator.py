# -*- coding: utf-8 -*-
# original by http://groups.google.com/group/web2py/browse_frm/thread/d1ec3ded48839071#
from gluon import *

class Paginator(DIV): 

    def __init__(self, perpage=10, records=100, 
                 renderstyle=False, page_var='page', **attributes):
        DIV.__init__(self, **attributes)
        if '_id' not in self.attributes:
            self.attributes['_id'] = 'paginator_%s' % id(self)
        self.perpage, self.records, self.renderstyle, self.page_var = (
            perpage, records, renderstyle, page_var
        )
        self.page = int(current.request.vars.get(self.page_var) or 1) 
    
    def _url(self, page):
        vars = current.request.get_vars.copy()
        vars[self.page_var] = page
        return URL(args=current.request.args, vars=vars)

    def limitby(self): 
        return (self.perpage*(self.page-1), self.perpage*self.page)
      
    def xml(self): 
        ### compute the number of pages ###
        pages = (self.records - 1) / self.perpage + 1
        if (self.records > self.perpage and
            pages == 1 and pages * self.perpage != self.records):
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
                              
            ### add prev link ###
            if self.page != 1:
                self.append(
                    A(current.T('Prev') , _href=self._url(self.page - 1),
                         _title=(self.page - 1), _class='previous_page'))
                
            ### add paging numbers ###
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
            
            ### add next link ###
            if pages > self.page:
                self.append(
                    A(current.T('Next') , _href=self._url(self.page + 1),
                         _title=(self.page + 1), _class='next_page'))
            
            # ### concat them
            # pager_el = DIV(_class='pagination', *inner)
        
        if self.renderstyle:
            self.append(STYLE(self.style()))
            
        return DIV.xml(self) 
        
    def style(self):
        # original by: http://activeadmin.info/
        return '''
#%(id)s {
  display: inline; margin-left: 10px; 
  font-size: 0.8em; font-weight: bold; font-family: Helvetica, Arial, sans-serif;
  }
  #%(id)s a {
    box-shadow: 0 1px 2px #aaaaaa;
    -moz-box-shadow: 0 1px 2px #aaaaaa;
    -webkit-box-shadow: 0 1px 2px #aaaaaa;
    text-decoration: none;
    margin-right: 3px;
    cursor: pointer;
    background: #f9f9f9;
    background: -webkit-gradient(linear, left top, left bottom, from(#f9f9f9), to(#dddbdb));
    background: -moz-linear-gradient(-90deg, #f9f9f9, #dddbdb);
    filter: progid:DXImageTransform.Microsoft.gradient(startColorstr=#f9f9f9, endColorstr=#dddbdb);
    -ms-filter: progid:DXImageTransform.Microsoft.gradient(startColorstr=#f9f9f9, endColorstr=#dddbdb);
    text-shadow: white 0 1px 0;
    color: #777; 
    }
    #%(id)s a:hover {
      color: #444;
      box-shadow: 0 1px 3px #888888;
      -moz-box-shadow: 0 1px 3px #888888;
      -webkit-box-shadow: 0 1px 3px #888888; }
    #%(id)s a:active {
      box-shadow: inset 0 1px 2px #aaaaaa;
      -moz-box-shadow: inset 0 1px 2px #aaaaaa;
      -webkit-box-shadow: inset 0 1px 2px #aaaaaa; }
  #%(id)s em {
    box-shadow: 0 1px 2px #aaaaaa;
    -moz-box-shadow: 0 1px 2px #aaaaaa;
    -webkit-box-shadow: 0 1px 2px #aaaaaa;
    background: #838a90;
    background: -webkit-gradient(linear, left top, left bottom, from(#838a90), to(#414549));
    background: -moz-linear-gradient(-90deg, #838a90, #414549);
    filter: progid:DXImageTransform.Microsoft.gradient(startColorstr=#838a90, endColorstr=#414549);
    -ms-filter: progid:DXImageTransform.Microsoft.gradient(startColorstr=#838a90, endColorstr=#414549);
    text-shadow: black 0 1px 0;
    text-decoration: none;
    font-weight: bold;
    font-size: 1.0em;
    color: #efefef; }
    #%(id)s em:hover {
      color: #fff;
      box-shadow: 0 1px 3px #888888;
      -moz-box-shadow: 0 1px 3px #888888;
      -webkit-box-shadow: 0 1px 3px #888888; }
    #%(id)s em:active {
      box-shadow: inset 0 1px 2px black;
      -moz-box-shadow: inset 0 1px 2px black;
      -webkit-box-shadow: inset 0 1px 2px black; }
  #%(id)s a, #%(id)s em {
    margin-right: 4px;
    padding: 2px 5px;
    border: none;}
          ''' %  dict(id=self.attributes['_id']) 
      
class PerpageSelector(SPAN):
    
    def __init__(self, perpages=(10, 25, 50, 100),
                 perpage_var='perpage', page_var='page', **attributes):
        SPAN.__init__(self, **attributes)
        if '_id' not in self.attributes:
            self.attributes['_id'] = 'perpageselector_%s' % id(self)
        self.perpages, self.perpage_var, self.page_var  = (
            perpages, perpage_var, page_var
        )
        self.perpage = int(current.request.get_vars.get(self.perpage_var, perpages[0]))
        
    def _url(self, perpage):
        vars = current.request.get_vars.copy()
        vars[self.page_var] = 1
        vars[self.perpage_var] = perpage
        return URL(args=current.request.args, vars=vars)
  
    def xml(self): 
        def _get_perpage_link(_perpage):
            if _perpage == self.perpage:
                return str(_perpage)
            else:
                return A(_perpage, _href=self._url(_perpage)).xml()
        inner = XML(current.T('Per page: ') +
                 ', '.join([_get_perpage_link(_perpage) for _perpage in self.perpages])) 
        return SPAN(inner, _style='font-size: 0.85em; color: #B3BCC1;'
                    ).xml()
                    
class PagingInfo(SPAN):
    def __init__(self, page, perpage, records, **attributes):
        SPAN.__init__(self, **attributes)
        if '_id' not in self.attributes:
            self.attributes['_id'] = 'paginginfo_%s' % id(self)
        self.page, self.perpage, self.records  = (
            page, perpage, records
        )
        
    def xml(self): 
        inner = XML(current.T('Display: <b>%(start)s - %(end)s</b> of <b>%(total)s</b>') % 
              dict(start=(self.page - 1)*self.perpage + 1, end=self.page*self.perpage, 
                   total=self.records))
        return SPAN(inner, _style='font-size: 0.85em; color: #B3BCC1;').xml()
