# -*- coding: utf-8 -*-
# This plugins is licensed under the MIT license: http://www.opensource.org/licenses/mit-license.php
# Authors: Kenji Hosoda <hosoda@s-cubism.jp>
from gluon import *

# For referencing static and views from other application
import os
APP = os.path.basename(os.path.dirname(os.path.dirname(__file__)))


class TableScope(DIV):

    def __init__(self, dataset, field=None, 
                 all=True, default=None,
                 queries=None,
                 left=None, groupby=None, scope_var='scope', page_var='page',
                 renderstyle=False, **attributes):
        DIV.__init__(self, **attributes)
        self.attributes['_class'] = 'tablescope'
        self.dataset, self.scope_var, self.page_var = (
            dataset, scope_var, page_var
        )
        
        self.scopes = []
        self.scope_details = {}

        def _get_count(_dataset):
            if groupby:
                return len(_dataset.select(field, left=left, groupby=groupby))
            elif left:
                counter = field.count()
                return _dataset.select(counter, left=left).first()[counter]
            else:
                return _dataset.count()

        if queries:
            for k, v, query in queries:
                self.scopes.append(k)
                _dataset = self.dataset(query)
                self.scope_details[k] = dict(label=v, count=_get_count(_dataset))

        if field:
            for k, v in field.requires.options():
                if str(v):
                    self.scopes.append(k)
                    _dataset = self.dataset(field == k)
                    self.scope_details[k] = dict(label=v, count=_get_count(_dataset))
            
        if all == True:
            count = sum([e['count'] for e in self.scope_details.values()])
            self.scope_details['__all__'] = dict(label=current.T('All'), count=count)
            self.scopes.insert(0, '__all__')
            
        self.scope = str(current.request.get_vars.get(self.scope_var) or (default or self.scopes[0]))
        if self.scope == '__all__':
            self.scoped_dataset = dataset
        else:
            if queries:
                self.scoped_dataset = dataset(dict([(k, query) for k, v, query in queries])[self.scope])
            if field:
                self.scoped_dataset = dataset(field == self.scope)
        
        if renderstyle:
            _url = URL(APP, 'static', 'plugin_tablescope/tablescope.css')
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
                    SPAN(A(label, _class='w2p_trap', _href=self._url(scope=scope)),
                         ' ', SPAN('(%s)' % count, _class='count'),
                    _class='scope'))
    
        return DIV.xml(self)
