# -*- coding: utf-8 -*-
from gluon import *
import copy

class SOLIDFORM(SQLFORM):

    def __init__(self, *args, **kwds):
        self.structured_fields = kwds.get('fields')
        
        _precedent_row_len = 1
        if self.structured_fields:
            flat_fields = []
            max_row_lines = 1
            for i, inner in enumerate(self.structured_fields):
                if type(inner) in (list, tuple):
                    for field in inner:
                        if field:
                            flat_fields.append(field)
                    max_row_lines = max(len(inner), max_row_lines)
                    _precedent_row_len = len(inner)
                elif inner:
                    flat_fields.append(inner)
                else:
                    self.structured_fields[i] = [inner for i in range(_precedent_row_len)]
            
            row_spans = dict((e, 1) for e in flat_fields)
            col_spans = dict((e, 1) for e in flat_fields)
                    
            row_lines = [[] for i in range(max_row_lines)]
            for row_no, inner in enumerate(self.structured_fields):
                if type(inner) in (list, tuple):
                    num_lines = len(inner)
                    colspan = max_row_lines / num_lines
                    extra_colspan = max_row_lines % num_lines
                    for i in range((max_row_lines-extra_colspan)/colspan):
                        field = inner[i]
                        if field:
                            col_spans[field] = colspan
                            row_lines[i*colspan].append(field)
                        else:
                            for _row_no in reversed(range(row_no)):
                                try:
                                    row_spans[self.structured_fields[_row_no][i]] += 1
                                    break
                                except KeyError:
                                    pass
                    if extra_colspan:
                        for line_no in range(max_row_lines-extra_colspan, max_row_lines):
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
        
        SQLFORM.__init__(self, *args, **kwds)
        
    def createform(self, xfields):
        if not self.structured_fields:
            return SQLFORM.createform(self, xfields)
        
        table = TABLE()
        
        n = len(self.flat_fields)
        xfield_dict = dict([(x, y) for x, y in zip(self.flat_fields, xfields[:n])])
        
        row_lines = copy.copy(self.row_lines)
        for i in range(len(row_lines[0])*self.max_row_lines):
            if i >= len(row_lines[0]):
                break
            tr_inner =[]
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
                                row_lines[j].insert(i+k, False)
                        col_span = self.col_spans[field]
                        if col_span > 1:
                            for k in range(1, col_span):
                                row_lines[j+k].insert(i, False)
                        tr_inner += self.create_td(xfield_dict[field], row_span, col_span)
            table.append(TR(*tr_inner))
            
        tr_inner =[]
        for id,a,b,c in xfields[n:]:
            td_b = self.field_parent[id] = TD(b,_class='w2p_fw')
            tr_inner.append(TD(a,_class='w2p_fl'))
            tr_inner.append(td_b)
            tr_inner.append(TD(c,_class='w2p_fc'))
        table.append(TR(*tr_inner))
        
        return table
        
    def create_td(self, xfield, row_span, col_span):
        id,a,b,c = xfield
        if self.formstyle == 'table3cols':
            td_b = self.field_parent[id] = TD(b, c and DIV(c) or '',
                                              _class='w2p_fw',
                                              _rowspan=row_span, 
                                              _colspan=2*col_span-1)
            return (TD(a,_class='w2p_fl',
                      _rowspan=row_span, 
                      _colspan=1), td_b)
        else:
            raise RuntimeError, 'formstyle not supported'
       
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
