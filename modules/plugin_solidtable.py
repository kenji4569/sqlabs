# -*- coding: utf-8 -*-
from gluon import *
from gluon.sqlhtml import table_field

class SOLIDTABLE(TABLE):
    
    def __init__(self, sqlrows, linkto=None, upload=None, orderby=None,
            headers={}, truncate=16, columns=None, th_link='',
            extracolumns=None, selectid=None, renderstyle=False, **attributes):
        TABLE.__init__(self, **attributes)
        
        if '_id' not in attributes:
            attributes['_id'] = 'solidtable_%s' % id(sqlrows)
        
        self.components = []
        self.attributes = attributes
        self.sqlrows = sqlrows
        self.linkto = linkto
        self.truncate = truncate
        
        components = self.components
        if not sqlrows:
            return
        columns = columns or sqlrows.colnames
        columns = [c if type(c) is str else '%s' % id(c) for c in columns]
            
        self.show_header = headers is not None
        headers = self.show_header and headers or {}
        headers = self._convert_headers(headers, columns)
        if extracolumns:#new implement dict
            _extracolumns = dict([('%s' % id(ec), ec) for ec in extracolumns])
            columns.extend([c for c in _extracolumns.keys() if c not in columns])
            headers.update(_extracolumns.items())
        
        if self.show_header:
            components.append(self._create_thead(columns, headers))
            
        if renderstyle:
            components.append(STYLE(self.style()))
        
        components.append(self._create_tbody(columns, headers, 
                                             selectid, linkto, truncate))
        
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
                headers[c] = ' '.join([w.capitalize() for w in c.split('.')[-1].split('_')])
        elif headers=='labels':
            headers = {}
            for c in columns:
                headers[c] = _get_field_label(c)
        else:
            for c in columns:
                if c not in headers:
                    headers[c] = _get_field_label(c)
                elif 'label' not in headers[c]:
                    headers[c]['label'] = _get_field_label(c)
                    
        return headers
        
    def _create_thead(self, columns, headers):
        row = []
        for c in columns:#new implement dict
            if isinstance(headers.get(c), dict):
                th = self._create_th(headers[c])
            else:
                th = TH(headers.get(c, c))
            # if orderby:
                # pass # TODO
            row.append(th)
        return THEAD(TR(*row))
        
    def _create_th(self, coldict):
        attrcol = dict()
        if 'width' in coldict and coldict['width']:
            attrcol.update(_width=coldict['width'])
        self._apply_class(attrcol, coldict)
        return TH(coldict['label'],**attrcol)
        
    def _apply_class(self, attrcol, coldict):
        if coldict.get('selected'):
            colclass= str(coldict.get('class', '') + " colselected").strip()
        else:
            colclass = coldict.get('class')
        if colclass:
            attrcol.update(_class=colclass)
        
    def _create_tbody(self, columns, headers, 
                      selectid, linkto, truncate):
        tbody = []
        for (rc, record) in enumerate(self.sqlrows):
            row = []
            _class = 'even' if rc % 2 == 0 else 'odd'
            if selectid is not None and record.id == selectid:
                _class += ' rowselected'
            for colname in columns:
                row.append(self._create_td(colname, headers[colname], record, rc))
            tbody.append(TR(_class=_class, *row))
        return TBODY(*tbody)
        
    def _create_td(self, colname, header, record, rc):
        if '.' not in colname:
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
            if tablename in record \
                    and isinstance(record,Row) \
                    and isinstance(record[tablename],Row):
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
                    r = A(represent(field,r,record), _href=str(href))
                elif field.represent:
                    r = represent(field,r,record)
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
            self._apply_class(attrcol, header)
                    
        return TD(r,**attrcol)
        
    def _truncate_str(self, r, truncate):
        if truncate:
            return unicode(r, 'utf8')[:truncate - 3].encode('utf8') + '...'
        else:
            return r
            
    def style(self):
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
        ''' % dict(id=self.attributes['_id'])        
        return css
        