# -*- coding: utf-8 -*-
# This plugins is licensed under the MIT license: http://www.opensource.org/licenses/mit-license.php
# Authors: Kenji Hosoda <hosoda@s-cubism.jp>
from gluon import *


def _is_not_empty(requires):
    if isinstance(requires, IS_LENGTH):
        return bool(requires.minsize)
        
    return isinstance(requires,
                (IS_ALPHANUMERIC, IS_DATE, IS_DATE_IN_RANGE, IS_DATETIME,
                 IS_DATETIME_IN_RANGE, IS_DECIMAL_IN_RANGE,
                 IS_EMAIL, IS_EQUAL_TO, IS_EXPR, IS_FLOAT_IN_RANGE,
                 IS_INT_IN_RANGE, IS_IN_SET, IS_LIST_OF, IS_MATCH,
                 IS_NOT_EMPTY,
                 IS_TIME, IS_URL, IS_SLUG, IS_STRONG,
                 IS_IMAGE, IS_UPLOAD_FILENAME, IS_IPV4,
                 IS_NOT_IN_DB, IS_IN_DB))

default_not_empty_marker = SPAN('*', _class='not_empty')


def mark_not_empty(table, marker=default_not_empty_marker):
    for field in table:
        is_not_empty = False
        if field.requires:
            if type(field.requires) in (list, tuple):
                for r in field.requires:
                    if _is_not_empty(r):
                        is_not_empty = True
                        break
            elif _is_not_empty(field.requires):
                is_not_empty = True
                    
        if is_not_empty:
            field._label = field.label
            field.label = SPAN(SPAN(field.label), ' ', marker, ' ')


def unmark_not_empty(table):
    for field in table:
        if hasattr(field, '_label'):
            field.label = field._label
