# -*- coding: utf-8 -*-
# This plugins is licensed under the MIT license: http://www.opensource.org/licenses/mit-license.php
# Authors: Kenji Hosoda <hosoda@s-cubism.jp>
from gluon import *

def _get_length(require):
    if isinstance(require, IS_LENGTH):
        return require.maxsize
    elif isinstance(require, (IS_INT_IN_RANGE, IS_FLOAT_IN_RANGE, IS_DECIMAL_IN_RANGE)):
        import math
        if isinstance(require, IS_INT_IN_RANGE):
            maximum = require.maximum - 1
        else:
            maximum = require.maximum
        return int(math.log10(max(maximum, abs(require.minimum)))) + 1

def tight_input_widget(field, value, **attributes):
    _length = None
    
    if field.requires:
        if isinstance(field.requires, IS_EMPTY_OR):
            requires =  field.requires.other
        else:
            requires = field.requires
        if type(requires) in (list, tuple):
            for r in requires:
                _length = _get_length(r)
                if _length:
                    break
        else:
            _length = _get_length(requires)
            
    _type = field.type
    if _length and _length < 20 or field.type.startswith('decimal'):
        _style = 'text-align:right;'
        if field.type == 'integer':
            _type = 'integer'
        elif field.type == 'double':
            _length += 3
            _type = 'double'
        elif field.type.startswith('decimal'):
            left, right = field.type[8:-1].split(',')
            _length = (_length or int(left)) + int(right)
            _type = 'decimal'
        elif field.type in ('string', 'password'):
            _length *= 1.2
            _style = ''
            
        _style = _style + ('width:%sem;' % (0.5*(_length + 2)))
            
        if '_style' in attributes:
            attributes['_style'] = attributes['_style'] + ';' + _style
        else:
            attributes['_style'] = _style
            
    return SQLFORM.widgets[_type].widget(field, value, **attributes)
    
    