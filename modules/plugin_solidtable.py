# -*- coding: utf-8 -*-
from gluon import *
from gluon.sqlhtml import table_field

class SOLIDTABLE(TABLE):
    
    def __init__(self, sqlrows, linkto=None, upload=None, orderby=None,
            headers={}, truncate=16, columns=None, th_link='',
            extracolumns=None, selectid=None, renderstyle=False, **attributes):
        if not sqlrows:
            return
        TABLE.__init__(self, **attributes)
        if '_id' not in attributes:
            attributes['_id'] = 'solidtable_%s' % id(sqlrows)
        self.attributes, self.sqlrows, self.linkto, self.truncate, self.selectid = (
            attributes, sqlrows, linkto, truncate, selectid
        )
        self.components = []
        
        def _conver_column_key(c):
            if c is None:
                return None
            return c if type(c) is str else '%s' % id(c)
        _columns = []
        for columns_inner in columns or self.sqlrows.colnames:
            if type(columns_inner) in (list, tuple):
                _columns_inner = []
                for column in columns_inner:
                    _columns_inner.append(_conver_column_key(column))
                _columns.append(_columns_inner)
            else:
                _columns.append(_conver_column_key(columns_inner))
        columns = _columns
            
        show_header = headers is not None
        headers = self._convert_headers(show_header and headers or {}, columns)
        if extracolumns:#new implement dict
            _extracolumns = dict([('%s' % id(ec), ec) for ec in extracolumns])
            columns.extend([c for c in _extracolumns.keys() if c not in columns])
            headers.update(_extracolumns.items())
            
        columns, col_lines = self._make_multine_columns(columns, headers)
        
        if show_header:
            self.components.append(self._create_thead(headers, columns, col_lines))
            
        if renderstyle:
            self._set_render_style()
        
        self.components.append(self._create_tbody(headers, columns, col_lines))
            
    def _convert_headers(self, headers, columns):
        
        def _get_field_label(column):
            parts = column.split('.')
            field = None
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
                if c not in headers:
                    headers[c] = {'label': _get_field_label(c)}
                elif 'label' not in headers[c]:
                    headers[c]['label'] = _get_field_label(c)
            for columns_inner in columns or self.sqlrows.colnames:
                if type(columns_inner) in (list, tuple):
                    for column in columns_inner:
                        if column:
                            _set_label(column)
                else:
                    if columns_inner:
                        _set_label(columns_inner) 
                    
        return headers
        
    def _make_multine_columns(self, columns, headers):
        for header in headers.values():
            header['_colspan'] = 1
            header['_rowspan'] = 1
        
        flat_columns = []
        max_col_lines = 1 # max row span in the table header or each table "row"
        for columns_inner in columns:
            if type(columns_inner) in (list, tuple):
                for column in columns_inner:
                    if column:
                        flat_columns.append(column)
                max_col_lines = max(len(columns_inner), max_col_lines)
            elif columns_inner:
                flat_columns.append(columns_inner)
                
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
                    tr_inner.append(self._create_th(headers[col]))
            thead_inner.append(tr_inner)
        return THEAD(*thead_inner)
        
    def _create_th(self, header):
        attrcol = dict()
        self._apply_colclass(attrcol, header)
        if header.get('width'):
            attrcol.update(_width=header['width'])
        
        return TH(header['label'],**attrcol)
        
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
                if self.selectid is not None and record.id == self.selectid:
                    _class += ' rowselected'
                tbody_inner.append(TR(_class=_class, *tr_inner))
        return TBODY(*tbody_inner)
        
    def _create_td(self, header, colname, record, rc):
        if 'content' in header:
            r = header['content'](record, rc)
        else:
            if not table_field.match(colname):
                if "_extra" in record and colname in record._extra:
                    r = record._extra[colname]
                    return TD(r)
                else:
                    raise KeyError("Column %s not found (SQLTABLE)" % colname)
            (tablename, fieldname) = colname.split('.')
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
                r = represent(field,r or [],record)
            elif field.represent:
                r = represent(field,r,record)
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
            return unicode(r, 'utf8')[:truncate - 3].encode('utf8') + '...'
        else:
            return r
            
    def _set_render_style(self):
        # original by: http://activeadmin.info/
        css = '''
#%(id)s { width: 100%%; margin-bottom: 10px; border: 0; border-spacing: 0; }
  #%(id)s th {
    background: #efefef;
    background: -webkit-gradient(linear, left top, left bottom, from(#efefef), to(#dfe1e2));
    background: -moz-linear-gradient(-90deg, #efefef, #dfe1e2);
    filter: progid:DXImageTransform.Microsoft.gradient(startColorstr=#efefef, endColorstr=#dfe1e2);
    -ms-filter: progid:DXImageTransform.Microsoft.gradient(startColorstr=#efefef, endColorstr=#dfe1e2);
    box-shadow: 0 1px 2px #aaaaaa;
    -moz-box-shadow: 0 1px 2px #aaaaaa;
    -webkit-box-shadow: 0 1px 2px #aaaaaa;
    text-shadow: white 0 1px 0;
    border-bottom: 1px solid #ededed;
    font-size: 1.0em; font-weight: bold; line-height: 140%%; color: #5e6469;
    word-break: break-all;
    padding: 5px 12px 3px 12px;
    margin-bottom: 0.5em;
    //text-align: left;}
  #%(id)s th.colselected {
    background: #E2E2E2;
    background: -webkit-gradient(linear, left top, left bottom, from(#E2E2E2), to(#D2D4D6));
    background: -moz-linear-gradient(-90deg, #E2E2E2, #D2D4D6);
    filter: progid:DXImageTransform.Microsoft.gradient(startColorstr=#e2e2e2, endColorstr=#d2d4d6);
    -ms-filter: progid:DXImageTransform.Microsoft.gradient(startColorstr=#e2e2e2, endColorstr=#d2d4d6);
    border-bottom: 1px solid #DFE1E2;}
    
    #%(id)s th span.icon svg path, #%(id)s th span.icon svg polygon, #%(id)s th span.icon svg rect, #%(id)s th span.icon svg circle {
      fill: #5e6469 !important; }
    #%(id)s th span.icon {
      width: 1em;
      height: 1em; }
    #%(id)s th span.icon svg {
      width: 1em;
      height: 1em; }
    #%(id)s th span.icon {
      margin-right: 5px; }
    #%(id)s th a, #%(id)s th a:link, #%(id)s th a:visited {
      color: #5e6469;
      text-decoration: none;
      display: block; 
      max-height: 34px;
      overflow:hidden;}
    #%(id)s th a:hover { color: black; }
    #%(id)s th.sortable a {
      background: url("../images/orderable.png") no-repeat 0 4px;
      padding-left: 13px; }
    #%(id)s th.sorted-asc a {
      background-position: 0 -27px; }
    #%(id)s th.sorted-desc a {
      background-position: 0 -56px; }
    #%(id)s th.sorted-asc, #%(id)s th.sorted-desc {
      background: #e2e2e2;
      background: -webkit-gradient(linear, left top, left bottom, from(#e2e2e2), to(#d2d4d6));
      background: -moz-linear-gradient(-90deg, #e2e2e2, #d2d4d6);
      filter: progid:DXImageTransform.Microsoft.gradient(startColorstr=#e2e2e2, endColorstr=#d2d4d6);
      -ms-filter: progid:DXImageTransform.Microsoft.gradient(startColorstr=#e2e2e2, endColorstr=#d2d4d6);
      border-bottom: 1px solid #dfe1e2; }
  #%(id)s tr.even td { background: #f4f5f5; }
  #%(id)s td {
    padding: 2px 5px 0px 5px;
    border-bottom: 1px solid #e8e8e8;
    vertical-align: top; 
    word-break: break-all;}
  #%(id)s tr.rowselected td { background: #fff0f0;  }
        ''' % dict(id=self.attributes['_id']) 
        
        self.components.append(STYLE(css))
        