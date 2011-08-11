# -*- coding: utf-8 -*-
from gluon import *
from gluon.sqlhtml import table_field, represent, Row
import urllib

class SOLIDTABLE(SQLTABLE):
    
    def __init__(self, sqlrows, linkto=None, upload=None, orderby=None,
            headers={}, truncate=16, columns=None, th_link='',
            extracolumns=None, selectid=None, renderstyle=False, **attributes):
        TABLE.__init__(self, **attributes)
        self.attributes['_class'] = 'solidtable'
        self.sqlrows, self.linkto, self.truncate, self.selectid, self.th_link, self.orderby = (
            sqlrows, linkto, truncate, selectid, th_link, orderby
        )
        self.components = []
        
        def _conver_column_key(c):
            if c is None:
                return None
            if type(c) == str:
                return c
            elif type(c) == dict:
                return str(c)
            else:
                return c
        _columns = []
        for cols_inner in columns or self.sqlrows.colnames:
            if type(cols_inner) in (list, tuple):
                _cols_inner = []
                for col in cols_inner:
                    _cols_inner.append(_conver_column_key(col))
                _columns.append(_cols_inner)
            else:
                _columns.append(_conver_column_key(cols_inner))
        columns = _columns
        
        show_header = headers is not None
        headers = self._convert_headers(show_header and headers or {}, columns)
        if extracolumns:#new implement dict
            _extracolumns = dict([(str(ec), ec) for ec in extracolumns])
            columns.extend([c for c in _extracolumns.keys() if c not in columns])
            headers.update(_extracolumns.items())
            
        columns, col_lines = self._make_multine_columns(columns, headers)
        
        if show_header:
            self.components.append(self._create_thead(headers, columns, col_lines))
            
        if renderstyle:
            _url = URL('static','plugin_solidtable/solidtable.css')
            if _url not in current.response.files:
                current.response.files.append(_url)
        
        self.components.append(self._create_tbody(headers, columns, col_lines))
            
    def _convert_headers(self, headers, columns):
        def _get_field_label(column):
            field = None
            if type(column) == str and column[0] != '(':
                parts = column.split('.')
                if len(parts) == 2:
                    (t,f) = parts
                    field = self.sqlrows.db[t][f]
            return (field and field.label) or column
            
        if headers=='fieldname:capitalize':
            headers = {}
            for c in columns:
                if c:
                    headers[c] = {'label': ' '.join([w.capitalize() 
                                    for w in c.split('.')[-1].split('_')])}
        elif headers=='labels':
            headers = {}
            for c in columns:
                if c:
                    headers[c] = {'label': _get_field_label(c)}
        else:
            def _set_label(c):
                if c:
                    if c not in headers:
                        headers[c] = {'label': _get_field_label(c)}
                    elif 'label' not in headers[c]:
                        headers[c]['label'] = _get_field_label(c)
            for cols_inner in columns or self.sqlrows.colnames:
                if type(cols_inner) in (list, tuple):
                    for col in cols_inner:
                        _set_label(col)
                else:
                    _set_label(cols_inner) 
                    
        return headers
        
    def _make_multine_columns(self, columns, headers):
        for header in headers.values():
            header['_colspan'] = 1
            header['_rowspan'] = 1
        
        flat_columns = []
        max_col_lines = 1 # max row span in the table header or each table "row"
        for cols_inner in columns:
            if type(cols_inner) in (list, tuple):
                for col in cols_inner:
                    if col:
                        flat_columns.append(col)
                max_col_lines = max(len(cols_inner), max_col_lines)
            elif cols_inner:
                flat_columns.append(cols_inner)
                
        col_lines = [[] for i in range(max_col_lines)]
        for col_no, cols_inner in enumerate(columns):
            if type(cols_inner) in (list, tuple):
                num_lines = len(cols_inner)
                rowspan = max_col_lines / num_lines
                extra_rowspan = max_col_lines % num_lines
                for i in range((max_col_lines-extra_rowspan)/rowspan):
                    col = cols_inner[i]
                    if col:
                        headers[col]['_rowspan'] = rowspan
                        col_lines[i*rowspan].append(col)
                    else:
                        for _col_no in reversed(range(col_no)):
                            try:
                                headers[columns[_col_no][i]]['_colspan'] += 1
                                break
                            except:
                                pass
                if extra_rowspan:
                    for line_no in range(max_col_lines-extra_rowspan, max_col_lines):
                        col_lines[line_no].append(None)
            else:
                col = cols_inner
                if col:
                    headers[col]['_rowspan'] = max_col_lines
                    col_lines[0].append(col)
                else:
                    for _col_no in reversed(range(col_no)):
                        try:
                            headers[columns[_col_no]]['_colspan'] += 1
                            break
                        except:
                            pass
                        
        return flat_columns, col_lines
             
    def _create_thead(self, headers, columns, col_lines):
        thead_inner = []
        for col_line in col_lines:
            tr_inner =[]
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
                label = A(label, _href=self.th_link+'?orderby=' + col) # from SQLTABLE
        return TH(label,**attrcol)
        
    def _apply_colclass(self, attrcol, header):
        attrcol.update(_rowspan=header['_rowspan'], _colspan=header['_colspan'])
        
        if header.get('selected'):
            colclass= str(header.get('class', '') + " colselected").strip()
        else:
            colclass = header.get('class')
        if colclass:
            attrcol.update(_class=colclass)
        
    def _create_tbody(self, headers, columns, col_lines):
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
                    elif hasattr(record, 'id') and record.id ==self.selectid:
                        _class += ' rowselected'
                tbody_inner.append(TR(_class=_class, *tr_inner))
        return TBODY(*tbody_inner)
        
    def _create_td(self, header, colname, record, rc):
        if 'content' in header:
            r = header['content'](record, rc)
        else:
            _colname = str(colname)
            if not table_field.match(str(_colname)):
                if "_extra" in record and _colname in record._extra:
                    r = record._extra[_colname]
                    if hasattr(colname, 'represent'):
                        r = colname.represent(r)
                    return TD(r)
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
                raise SyntaxError, 'something wrong in Rows object'
                
            r_old = r
            if not field:
                pass
            elif self.linkto and field.type == 'id':
                try:
                    href = self.linkto(r, 'table', tablename)
                except TypeError:
                    href = '%s/%s/%s' % (self.linkto, tablename, r_old)
                r = A(r, _href=href)
            elif field.type.startswith('reference'):
                if self.linkto:
                    ref = field.type[10:]
                    try:
                        href = self.linkto(r, 'reference', ref)
                    except TypeError:
                        href = '%s/%s/%s' % (self.linkto, ref, r_old)
                        if ref.find('.') >= 0:
                            tref,fref = ref.split('.')
                            if hasattr(self.sqlrows.db[tref],'_primarykey'):
                                href = '%s/%s?%s' % (self.linkto, tref, urllib.urlencode({fref:r}))
                    r = A(represent(field, r, record), _href=str(href))
                elif field.represent:
                    r = represent(field, r, record)
            elif self.linkto and hasattr(field._table,'_primarykey') and fieldname in field._table._primarykey:
                # have to test this with multi-key tables
                key = urllib.urlencode(dict( [ \
                            ((tablename in record \
                                  and isinstance(record, Row) \
                                  and isinstance(record[tablename], Row)) and
                             (k, record[tablename][k])) or (k, record[k]) \
                                for k in field._table._primarykey ] ))
                r = A(r, _href='%s/%s?%s' % (self.linkto, tablename, key))
            elif field.type.startswith('list:'):
                r = represent(field, r or [], record)
            elif field.represent:
                r = represent(field, r, record)
            elif field.type == 'blob' and r:
                r = 'DATA'
            elif field.type == 'upload':
                if upload and r:
                    r = A('file', _href='%s/%s' % (upload, r))
                elif r:
                    r = 'file'
                else:
                    r = ''
            elif field.type in ['string','text']:
                r = str(field.formatter(r))
                if isinstance(header, dict):
                    r = self._truncate_str(r, header.get('truncate') or self.truncate)
                else:
                    r = self._truncate_str(r, self.truncate)
                    
        attrcol = dict()
        if isinstance(header, dict):
            self._apply_colclass(attrcol, header)
                    
        return TD(r,**attrcol)
        
    def _truncate_str(self, r, truncate):
        if truncate:
            ur = unicode(r, 'utf8')
            if len(ur) > truncate:
                return ur[:truncate - 3].encode('utf8') + '...'
        return r
            
class OrderbySelector(object):
    def __init__(self, *orderbys):
        self.orderbys = orderbys
        
    def orderby(self):
        return None
        
    def __call__(self, column, label):
        if any(column is orderby for orderby in self.orderbys):
            return A(label, _href='#', _class='orderable')
        else:
            return label
        