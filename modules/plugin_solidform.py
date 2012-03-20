# -*- coding: utf-8 -*-
# This plugins is licensed under the MIT license: http://www.opensource.org/licenses/mit-license.php
# Authors: Kenji Hosoda <hosoda@s-cubism.jp>
from gluon import *
import copy


class SOLIDFORM(SQLFORM):

    def __init__(self, *args, **kwds):
        self.structured_fields = kwds.get('fields')
        self.showid = kwds.get('showid', True)

        table = args and args[0] or kwds['table']
        if not self.structured_fields:
            self.structured_fields = [f.name for f in table if self._is_show(f)]
        else:
            self.structured_fields = copy.copy(self.structured_fields)
        _precedent_row_len = 1

        include_id = False
        flat_fields = []
        max_row_lines = 1
        for i, inner in enumerate(self.structured_fields):
            if type(inner) in (list, tuple):
                _inner = []
                for field in inner:
                    if field == 'id':
                        include_id = True
                        self.showid = True
                    if field and self._is_show(table[field]):
                        flat_fields.append(field)
                        _inner.append(field)
                self.structured_fields[i] = _inner
                max_row_lines = max(len(_inner), max_row_lines)
                _precedent_row_len = len(_inner)
            elif inner:
                if inner == 'id':
                    include_id = True
                    self.showid = True
                if self._is_show(table[inner]):
                    flat_fields.append(inner)
                else:
                    self.structured_fields[i] = None
            else:
                self.structured_fields[i] = [inner for i in range(_precedent_row_len)]
                
        self.structured_fields = [e for e in self.structured_fields if e or e is None]
        
        row_spans = dict((e, 1) for e in flat_fields)
        col_spans = dict((e, 1) for e in flat_fields)
                
        row_lines = [[] for i in range(max_row_lines)]
        for row_no, inner in enumerate(self.structured_fields):
            if type(inner) in (list, tuple):
                num_lines = len(inner)
                colspan = max_row_lines / num_lines
                extra_colspan = max_row_lines % num_lines
                for i in range((max_row_lines - extra_colspan) / colspan):
                    field = inner[i]
                    if field:
                        col_spans[field] = colspan
                        row_lines[i * colspan].append(field)
                    else:
                        for _row_no in reversed(range(row_no)):
                            try:
                                row_spans[self.structured_fields[_row_no][i]] += 1
                                break
                            except KeyError:
                                pass
                if extra_colspan:
                    for line_no in range(max_row_lines - extra_colspan, max_row_lines):
                        row_lines[line_no].append(None)
            else:
                field = inner
                col_spans[field] = max_row_lines
                row_lines[0].append(field)
        
        self.row_spans = row_spans
        self.col_spans = col_spans
        self.max_row_lines = max_row_lines
        self.flat_fields = flat_fields
        self.row_lines = row_lines
        kwds['fields'] = copy.copy(flat_fields)
            
        if not self.structured_fields or flat_fields[0] == 'id':
            self.ignore_first = False
        else:
            self.ignore_first = include_id
        
        self.readonly = kwds.get('readonly', False)
            
        kwds['showid'] = self.showid
        SQLFORM.__init__(self, *args, **kwds)
        
    def _is_show(self, fieldobj):
        return (fieldobj.writable or fieldobj.readable) and (fieldobj.type != 'id' or
                                                             (self.showid and fieldobj.readable))
        
    def createform(self, xfields):
        table_inner = []
        if self.showid and self.record and (not self.readonly or self.ignore_first):
            if not self.ignore_first:
                id, a, b, c = xfields[0]
                tr_inner = []
                tr_inner.append(TD(a, _class='w2p_fl'))
                tr_inner.append(TD(b, _class='w2p_fw', _colspan=(2 * self.max_row_lines) - 1))
                table_inner.append(TR(*tr_inner))
            xfields = xfields[1:]
         
        n = len(self.flat_fields)
        xfield_dict = dict([(x, y) for x, y in zip(self.flat_fields, xfields[:n])])
        
        row_lines = copy.copy(self.row_lines)
        for i in range(max(len(line) for line in row_lines) * self.max_row_lines):
            if i >= len(row_lines[0]):
                break
            tr_inner = []
            for j, row_line in enumerate(row_lines):
                if i < len(row_line):
                    field = row_line[i]
                    if field is None:
                        tr_inner.append(TD())
                    elif field is False:
                        pass
                    else:
                        row_span = self.row_spans[field]
                        if row_span > 1:
                            for k in range(1, row_span):
                                row_lines[j].insert(i + k, False)
                        col_span = self.col_spans[field]
                        if col_span > 1:
                            for k in range(1, col_span):
                                row_lines[j + k].insert(i, False)
                        tr_inner += self.create_td(xfield_dict[field], row_span, col_span)
            table_inner.append(TR(*tr_inner))
            
        for id, a, b, c in xfields[n:]:
            td_b = self.field_parent[id] = TD(b, _class='w2p_fw',
                                              _colspan=(2 * self.max_row_lines) - 1)
            tr_inner = []
            tr_inner.append(TD(a, _class='w2p_fl'))
            tr_inner.append(td_b)
            table_inner.append(TR(*tr_inner))
        
        return TABLE(*table_inner)
        
    def create_td(self, xfield, row_span, col_span):
        id, a, b, c = xfield
        if self.formstyle == 'table3cols':
            td_b = self.field_parent[id] = TD(
                b,
                c and not self.readonly and DIV(c, _class='notation') or '',  # do not show when readonly
                _class='w2p_fw',
                _rowspan=row_span,
                _colspan=2 * col_span - 1)
            return (TD(a, _class='w2p_fl',
                      _rowspan=row_span,
                      _colspan=1), td_b)
        else:
            raise RuntimeError('formstyle not supported')

    @staticmethod
    def factory(*fields, **attributes):
        table_name = attributes.get('table_name', 'no_table')
        if 'table_name' in attributes:
            del attributes['table_name']
        
        flat_fields = []
        structured_fields = []
        for inner in fields:
            if type(inner) in (list, tuple):
                _inner = []
                for field in inner:
                    _inner.append(field.name)
                    if field:
                        flat_fields.append(field)
                structured_fields.append(_inner)
            elif inner:
                flat_fields.append(inner)
                structured_fields.append(inner.name)
                
        return SOLIDFORM(DAL(None).define_table(table_name, *flat_fields),
                         fields=structured_fields, **attributes)
    
    @staticmethod
    def formstyle(id, a, td_b, c):
        if c:
            td_b.components = td_b.components + [DIV(c, _class='notation')]
        return TR(TD(a, _class='w2p_fl'), td_b, _id=id)
