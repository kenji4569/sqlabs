# -*- coding: utf-8 -*-
from gluon import *

def mark_not_empty(table, marker='*', marker_style='color:#d00;'):
    for field in table:
        is_not_empty = False
        if field.requires:
            if type(field.requires) in (list, tuple):
                for r in field.requires:
                    if isinstance(r, IS_NOT_EMPTY):
                        is_not_empty = True
                        break
            else:
                if isinstance(field.requires, 
                        (IS_ALPHANUMERIC, IS_DATE, IS_DATE_IN_RANGE, IS_DATETIME, 
                         IS_DATETIME_IN_RANGE, IS_DECIMAL_IN_RANGE,
                         IS_EMAIL, IS_EQUAL_TO, IS_EXPR, IS_FLOAT_IN_RANGE,
                         IS_INT_IN_RANGE, IS_IN_SET, IS_LIST_OF, IS_MATCH,
                         IS_NOT_EMPTY, 
                         IS_TIME, IS_URL, IS_SLUG, IS_STRONG,
                         IS_IMAGE, IS_UPLOAD_FILENAME, IS_IPV4, 
                         IS_NOT_IN_DB, IS_IN_DB)):
                    is_not_empty = True
                    
        if is_not_empty:    
            field.label = SPAN(field.label, ' ', SPAN(marker, _style=marker_style), ' ')
    