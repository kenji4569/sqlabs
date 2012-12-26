# -*- coding: utf-8 -*-
# This plugins is licensed under the MIT license: http://www.opensource.org/licenses/mit-license.php
# Authors: Kenji Hosoda <hosoda@s-cubism.jp>
from gluon import *
from gluon.sqlhtml import table_field, represent, Row
import urllib

# For referencing static and views from other application
import os
APP = os.path.basename(os.path.dirname(os.path.dirname(__file__)))


class SOLIDTABLE(SQLTABLE):
    
    def __init__(self, sqlrows, linkto=None, upload=None, orderby=None,
            headers={}, truncate=16, columns=None, th_link='',
            extracolumns=None, selectid=None, renderstyle=False, **attributes):
        TABLE.__init__(self, **attributes)
        self.attributes['_class'] = 'solidtable'
        self.sqlrows, self.linkto, self.upload, self.truncate, self.selectid, self.th_link, self.orderby = (
            sqlrows, linkto, upload, truncate, selectid, th_link, orderby
        )
        self.components = []
        
        def _convert_column_key(c):
            if c is None:
                return None
            if type(c) == str:
                return c
            elif type(c) == dict or isinstance(c, Field):
                return str(c)
            else:
                return c
        
        max_col_lines = 1  # max row span in table header or each table "row"
        flat_columns = []
        _converted_columns = []
        _precedent_col_len = 1
        for inner in columns or self.sqlrows.colnames:
            if type(inner) in (list, tuple):
                _inner = []
                for col in inner:
                    _col = _convert_column_key(col)
                    if _col:
                        flat_columns.append(str(_col))
                    _inner.append(_col)
                _converted_columns.append(_inner)
                max_col_lines = max(len(inner), max_col_lines)
                _precedent_col_len = len(inner)
            else:
                _col = _convert_column_key(_convert_column_key(inner))
                if _col:
                    flat_columns.append(str(_col))
                    _converted_columns.append(_col)
                    _precedent_col_len = 1
                else:
                    _converted_columns.append([_col for i in range(_precedent_col_len)])
                    
        columns = _converted_columns
        
        show_header = headers is not None
        headers = self._convert_headers(show_header and headers or {}, columns)
        if extracolumns:  # new implement dict
            _extracolumns = dict([(str(ec), ec) for ec in extracolumns])
            columns.extend([c for c in [str(ec) for ec in extracolumns] if c not in flat_columns])
            headers.update(_extracolumns.items())
            
        col_lines = self._make_multine_columns(columns, headers, max_col_lines)
        
        if show_header:
            self.components.append(self._create_thead(headers, col_lines))
            
        self.components.append(self._create_tbody(headers, col_lines))
            
        if renderstyle:
            _url = URL(APP, 'static', 'plugin_solidtable/solidtable.css')
            if _url not in current.response.files:
                current.response.files.append(_url)
        
    def _convert_headers(self, headers, columns):
        def _get_field(column):
            field = None
            if type(column) == str and column[0] != '(':
                parts = column.split('.')
                if len(parts) == 2:
                    (t, f) = parts
                    field = self.sqlrows.db[t][f]
            return field
    
        if headers == 'fieldname:capitalize':
            headers = {}

            def _set_header_capitalize(c):
                if type(c) == str:
                    headers[c] = {'label': ' '.join([w.capitalize()
                                    for w in c.split('.')[-1].split('_')])}
                elif c:
                    field = _get_field(c)
                    headers[c] = {'label': (field and field.label) or c,
                                  'class': field and field.type or ''}
            _set_header = _set_header_capitalize

        elif headers == 'labels':
            headers = {}

            def _set_header_labels(c):
                if c:
                    field = _get_field(c)
                    headers[c] = {'label': (field and field.label) or c,
                                  'class': field and field.type or ''}
            _set_header = _set_header_labels
             
        else:
            def _set_header_default(c):
                if c:
                    field = _get_field(c)
                    label = (field and field.label) or c
                    class_ = field and field.type or ''
                    if c not in headers:
                        headers[c] = {'label': label, 'class': class_}
                    else:
                        if 'label' not in headers[c]:
                            headers[c]['label'] = label
                        if 'class' not in headers[c]:
                            headers[c]['class'] = class_
            _set_header = _set_header_default
                    
        for inner in columns or self.sqlrows.colnames:
            if type(inner) in (list, tuple):
                for col in inner:
                    _set_header(col)
            else:
                _set_header(inner)
                    
        return headers
        
    def _make_multine_columns(self, columns, headers, max_col_lines):
        for header in headers.values():
            header['_colspan'] = 1
            header['_rowspan'] = 1
        
        col_lines = [[] for i in range(max_col_lines)]
        for col_no, inner in enumerate(columns):
            if type(inner) in (list, tuple):
                num_lines = len(inner)
                rowspan = max_col_lines / num_lines
                extra_rowspan = max_col_lines % num_lines
                for i in range((max_col_lines - extra_rowspan) / rowspan):
                    col = inner[i]
                    if col:
                        headers[col]['_rowspan'] = rowspan
                        col_lines[i * rowspan].append(col)
                    else:
                        for _col_no in reversed(range(col_no)):
                            try:
                                headers[columns[_col_no][i]]['_colspan'] += 1
                                break
                            except KeyError:
                                pass
                if extra_rowspan:
                    for line_no in range(max_col_lines - extra_rowspan, max_col_lines):
                        col_lines[line_no].append(None)
            else:
                col = inner
                headers[col]['_rowspan'] = max_col_lines
                col_lines[0].append(col)
                    
        return col_lines
             
    def _create_thead(self, headers, col_lines):
        thead_inner = []
        for col_line in col_lines:
            tr_inner = []
            for col in col_line:
                if not col:
                    tr_inner.append(TH())
                else:
                    tr_inner.append(self._create_th(headers, col))
            thead_inner.append(TR(*tr_inner))
        return THEAD(*thead_inner)
        
    def _create_th(self, headers, col):
        header = headers[col]
        attrcol = dict()
        self._apply_colclass(attrcol, header)
        if header.get('width'):
            attrcol.update(_width=header['width'])
        
        label = header['label']
        if self.orderby and not isinstance(label, A):
            if callable(self.orderby):
                label = self.orderby(col, label)
            else:
                label = A(label, _href=self.th_link + '?orderby=' + col, _class='w2p_trap')  # from SQLTABLE
        return TH(label, **attrcol)
        
    def _apply_colclass(self, attrcol, header):
        attrcol.update(_rowspan=header['_rowspan'], _colspan=header['_colspan'])
        
        if header.get('selected'):
            colclass = str(header.get('class', '') + " colselected").strip()
        else:
            colclass = header.get('class')
        if colclass:
            attrcol.update(_class=colclass)
        
    def _create_tbody(self, headers, col_lines):
        tbody_inner = []
        for (rc, record) in enumerate(self.sqlrows):
            for col_line in col_lines:
                tr_inner = []
                for col in col_line:
                    if not col:
                        tr_inner.append(TD())
                    else:
                        tr_inner.append(self._create_td(headers[col], col, record, rc))
                _class = 'even' if rc % 2 == 0 else 'odd'
                if self.selectid is not None:
                    if callable(self.selectid):
                        if self.selectid(record):
                            _class += ' rowselected'
                    elif hasattr(record, 'id') and record.id == self.selectid:
                        _class += ' rowselected'
                tbody_inner.append(TR(_class=_class, *tr_inner))
        return TBODY(*tbody_inner)
        
    def _create_td(self, header, colname, record, rc):
        attrcol = dict()
        self._apply_colclass(attrcol, header)
             
        if 'content' in header:
            r = header['content'](record, rc)
        else:
            _colname = str(colname)
            if not table_field.match(str(_colname)):
                if "_extra" in record and _colname in record._extra:
                    r = record._extra[_colname]
                    if hasattr(colname, 'represent'):
                        r = colname.represent(r)
                    return TD(r, **attrcol)
                else:
                    raise KeyError("Column %s not found (SQLTABLE)" % _colname)
            
            (tablename, fieldname) = _colname.split('.')
            try:
                field = self.sqlrows.db[tablename][fieldname]
            except KeyError:
                field = None
                
            if tablename in record and isinstance(record, Row) and isinstance(record[tablename], Row):
                r = record[tablename][fieldname]
            elif fieldname in record:
                r = record[fieldname]
            else:
                raise SyntaxError('something wrong in Rows object')
                
            r_old = r
            if not field:
                pass
            elif self.linkto and field.type == 'id':
                try:
                    href = self.linkto(r, 'table', tablename)
                except TypeError:
                    href = '%s/%s/%s' % (self.linkto, tablename, r_old)
                r = A(r, _href=href, _class='w2p_trap')
            elif field.type.startswith('reference'):
                if self.linkto:
                    ref = field.type[10:]
                    try:
                        href = self.linkto(r, 'reference', ref)
                    except TypeError:
                        href = '%s/%s/%s' % (self.linkto, ref, r_old)
                        if ref.find('.') >= 0:
                            tref, fref = ref.split('.')
                            if hasattr(self.sqlrows.db[tref], '_primarykey'):
                                href = '%s/%s?%s' % (self.linkto, tref, urllib.urlencode({fref: r}))
                    r = A(represent(field, r, record), _href=str(href), _class='w2p_trap')
                elif field.represent:
                    r = represent(field, r, record)
            elif self.linkto and hasattr(field._table, '_primarykey') and fieldname in field._table._primarykey:
                # have to test this with multi-key tables
                key = urllib.urlencode(dict([ \
                            ((tablename in record \
                                  and isinstance(record, Row) \
                                  and isinstance(record[tablename], Row)) and
                             (k, record[tablename][k])) or (k, record[k]) \
                                for k in field._table._primarykey]))
                r = A(r, _href='%s/%s?%s' % (self.linkto, tablename, key), _class='w2p_trap')
            elif field.type.startswith('list:'):
                r = represent(field, r or [], record)
            elif field.represent:
                r = represent(field, r, record)
            elif field.type == 'blob' and r:
                r = 'DATA'
            elif field.type == 'upload':
                if callable(self.upload) and r:
                    r = A('file', _href='%s' % self.upload(r), _class='w2p_trap')
                elif self.upload and r:
                    r = A('file', _href='%s/%s' % (self.upload, r), _class='w2p_trap')
                elif r:
                    r = 'file'
                else:
                    r = ''
            elif field.type in ['string', 'text']:
                r = str(field.formatter(r))
                if isinstance(header, dict):
                    r = self._truncate_str(r, header.get('truncate') or self.truncate)
                else:
                    r = self._truncate_str(r, self.truncate)
                    
        return TD(r, **attrcol)
        
    def _truncate_str(self, r, truncate):
        if truncate:
            ur = unicode(r, 'utf8')
            if len(ur) > truncate:
                return ur[:truncate - 3].encode('utf8') + '...'
        return r

        
class OrderbySelector(object):
    def __init__(self, orderbys, orderby_var='orderby'):
        self.orderbys = orderbys
        self.orderby_var = orderby_var
        
        _ivnert_orderbys = []
        for orderby in self.orderbys:
            if orderby.op == orderby.db._adapter.INVERT:
                _ivnert_orderbys.append(orderby.first)
            else:
                _ivnert_orderbys.append(~orderby)
        self.orderbys_dict = dict([(self._get_key(o), o) for o in orderbys + _ivnert_orderbys])
        
        if self.orderby_var in current.request.get_vars:
            orderby_key = current.request.get_vars[self.orderby_var]
            for _orderby_key, _orderby in self.orderbys_dict.items():
                if orderby_key == _orderby_key:
                    current_orderby = _orderby
                    break
            else:
                current_orderby = None
        else:
            current_orderby = self.orderbys and self.orderbys[0] or None
        self.current_orderby = current_orderby
        
        if current_orderby:
            if current_orderby.op == current_orderby.db._adapter.INVERT:
                self.current_field = current_orderby.first
                self.next_orderby = self.current_field
                self.current_class = 'orderby-desc'
            else:
                self.current_field = current_orderby
                self.next_orderby = ~self.current_field
                self.current_class = 'orderby-asc'
        else:
            self.current_field = current_orderby
        
    def _get_key(self, orderby):
        import hashlib
        m = hashlib.md5()
        m.update(str(orderby))
        return m.hexdigest()
        
    def _url(self, orderby):
        vars = current.request.get_vars.copy()
        vars[self.orderby_var] = self._get_key(orderby)
        return URL(args=current.request.args, vars=vars)
        
    def orderby(self):
        return self.current_orderby
        
    def __call__(self, column, label):
        if str(column) == str(self.current_field):
            return A(label, _href=self._url(self.next_orderby), _class='w2p_trap orderby ' + self.current_class)
        
        for orderby in self.orderbys:
            if orderby.op == orderby.db._adapter.INVERT:
                _column = orderby.first
            else:
                _column = orderby
            if str(column) == str(_column):
                return A(label, _href=self._url(orderby), _class='w2p_trap orderby')
                
        return label
