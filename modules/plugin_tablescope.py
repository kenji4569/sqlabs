# -*- coding: utf-8 -*-
from gluon import *

class TableScope(DIV): 

    def __init__(self, dataset, field, all=True, default=None,
                  left=None, groupby=None, scope_var='scope', page_var='page', 
                  renderstyle=False, **attributes):
        DIV.__init__(self, **attributes)
        self.attributes['_class'] = 'tablescope'
        self.dataset, self.scope_var, self.page_var = (
            dataset, scope_var, page_var
        )
        
        self.scopes = []
        self.scope_details = {}
        for k, v in field.requires.options():
            if str(v):
                self.scopes.append(k)
                _dataset = self.dataset(field==k)
                if groupby:
                    count = len(_dataset.select(field, left=left, groupby=groupby))
                elif left:
                    counter = field.count()
                    count = _dataset.select(counter, left=left).first()[counter]
                else:
                    count = _dataset.count()
                self.scope_details[k] = dict(label=v, count=count)
            
        if all == True:
            count = sum([e['count'] for e in self.scope_details.values()])
            self.scope_details['__all__'] = dict(label=current.T('All'), count=count) 
            self.scopes.insert(0, '__all__')
            
        self.scope = str(current.request.get_vars.get(self.scope_var) or (default or self.scopes[0]))
        if self.scope == '__all__':
            self.scoped_dataset = dataset
        else:
            self.scoped_dataset = dataset(field==self.scope)
        
        if renderstyle:
            _url = URL('static','plugin_tablescope/tablescope.css')
            if _url not in current.response.files:
                current.response.files.append(_url)
                
    def _url(self, scope):
        vars = current.request.get_vars.copy()
        vars[self.page_var] = 1
        vars[self.scope_var] = scope
        return URL(args=current.request.args, vars=vars)
        
    def xml(self): 
        for scope in self.scopes:
            scope_detail = self.scope_details[scope]
            count = scope_detail['count']
            label = scope_detail['label']
            if scope == self.scope:
                self.append(
                    SPAN(EM(label), ' ', SPAN('(%s)' % count, _class='count'),
                        _class='scope selected'))
            else:
                self.append(
                    SPAN(A(label, _href=self._url(scope=scope)), 
                         ' ', SPAN('(%s)' % count, _class='count'),
                    _class='scope'))
    
        return DIV.xml(self) 
        