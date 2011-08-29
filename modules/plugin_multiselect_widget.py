# -*- coding: utf-8 -*-
# This plugins is licensed under the MIT license: http://www.opensource.org/licenses/mit-license.php
# Authors: Kenji Hosoda <hosoda@s-cubism.jp>
from gluon import *

def multiselect_widget(field, value, **attributes):
    requires = field.requires
    if not isinstance(requires, (list, tuple)):
        requires = [requires]
    if requires:
        if hasattr(requires[0], 'options'):
            options = requires[0].options()
        else:
            raise SyntaxError, 'widget cannot determine options of %s'  % field
    
    selected_opts = []
    unselected_opts = []
    
    _value = map(str, value) if value else []
    for (k, v) in options:
        opt = OPTION(v, _value=k)
        if _value and k in _value:
            selected_opts.append(opt)
        else:
            unselected_opts.append(opt)
    
    unselected_el_id = "unselected_%s" % field.name
    select_el_id = field.name
    
    script_el = SCRIPT("""
function plugin_multiselect_widget_move(select, target) {
    jQuery('#' + select).children().each(function() {
        if (this.selected) {
            jQuery('#' + target).append(this);
            jQuery(this).attr({selected: false});
        }
    });
}
jQuery(document).ready(function() {
    jQuery("form input[type=submit]").click(function() {
        jQuery('#' +'%s').children().attr({selected: true});
    });
});""" % select_el_id)
    
    width = attributes.get('width', 320)
    size = attributes.get('size', 6)
    unselected_el = SELECT(_id=unselected_el_id, _size=size, _style="width:%spx" % width, _multiple=True,
                           *unselected_opts)
    select_el = SELECT(_id=select_el_id, _size=size, _style="width:%spx" % width, _multiple=True,
                       _name=field.name, requires=field.requires,
                       *selected_opts)
    attributes['_style'] = attributes.get('_style', 'padding-bottom:10px;')
    
    arrangement = attributes.get('arrangement', 'vertical')
    if arrangement == 'vertical':
        return DIV(script_el, unselected_el, BR(),
                   CENTER(
                        INPUT(_type='button', _value='↓  %s  ↓' % current.T('register'), 
                             _onclick=('plugin_multiselect_widget_move("%s", "%s");' % 
                                       (unselected_el_id, select_el_id))), ' ',
                        INPUT(_type='button', _value='↑  %s  ↑' % current.T('delete'),
                              _onclick=('plugin_multiselect_widget_move("%s", "%s");' %
                                        (select_el_id, unselected_el_id))),
                    _style='padding:5px 0px;width:%spx;' % width),
                   select_el,
                   _id='%s_%s' % (field._tablename, field.name),
                   **attributes)
    elif arrangement == 'horizontal':
        return DIV(script_el, TABLE(TR(
                       TD(unselected_el),
                       TD(
                            INPUT(_type='button', _value='%s  →' % current.T('register'), 
                                 _onclick=('plugin_multiselect_widget_move("%s", "%s");' % 
                                           (unselected_el_id, select_el_id))), BR(),BR(),
                            INPUT(_type='button', _value='←  %s' % current.T('delete'),
                                  _onclick=('plugin_multiselect_widget_move("%s", "%s");' %
                                            (select_el_id, unselected_el_id))),
                            _style='vertical-align:middle;padding-right: 10px;text-align:center;'
                       ),
                       TD(select_el),
                   )),
                   _id='%s_%s' % (field._tablename, field.name),
                   **attributes)
    
def vmultiselect_widget(field, value, **attributes):
    attributes['arrangement'] = 'vertical'
    return multiselect_widget(field, value, **attributes)
    
def hmultiselect_widget(field, value, **attributes):
    attributes['arrangement'] = 'horizontal'
    attributes['width'] = 150
    return multiselect_widget(field, value, **attributes)
