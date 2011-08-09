# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

def multi_select_widget():
    form = SQLFORM(db.multiselect_demo)
    
    code = CODE(
"""def multiselect_widget(field, value, **attributes):
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
    
    script_el = SCRIPT('''
function multiselect_move_items(select, target) {
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
});''' % select_el_id)
    
    width = attributes.get('width', 320)
    size = attributes.get('size', 6)
    unselected_el = SELECT(_id=unselected_el_id, _size=size, _style="width:%spx" % width, _multiple=True,
                           *unselected_opts)
    select_el = SELECT(_id=select_el_id, _size=size, _style="width:%spx" % width, _multiple=True,
                       _name=field.name, requires=field.requires,
                       *selected_opts)
    
    return DIV(script_el,
               unselected_el,
               BR(),
               CENTER(
                    INPUT(_type='button', _value='↓  登録  ↓', 
                         _onclick=('multiselect_move_items("%s", "%s");' % 
                                   (unselected_el_id, select_el_id))),
                    ' ',
                    INPUT(_type='button', _value='↑  削除  ↑',
                          _onclick=('multiselect_move_items("%s", "%s");' %
                                    (select_el_id, unselected_el_id))),
                _style='padding:5px 0px;width:%spx;' % width),
               select_el,
               _id='%s_%s' % (field._tablename, field.name),
               _style='padding-bottom:10px;')
    """)
    return dict(form=form, code=code)

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
function multiselect_move_items(select, target) {
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
    
    return DIV(script_el,
               unselected_el,
               BR(),
               CENTER(
                    INPUT(_type='button', _value='↓  登録  ↓', 
                         _onclick=('multiselect_move_items("%s", "%s");' % 
                                   (unselected_el_id, select_el_id))),
                    ' ',
                    INPUT(_type='button', _value='↑  削除  ↑',
                          _onclick=('multiselect_move_items("%s", "%s");' %
                                    (select_el_id, unselected_el_id))),
                _style='padding:5px 0px;width:%spx;' % width),
               select_el,
               _id='%s_%s' % (field._tablename, field.name),
               _style='padding-bottom:10px;')
    
db.define_table('multiselect_demo',
   Field('bank_account_type', 'integer', label='口座区分', 
          requires=IS_EMPTY_OR(IS_IN_SET([(1, '普通'), (2, '当座')],  multiple=True)), 
          widget=multiselect_widget))

    
