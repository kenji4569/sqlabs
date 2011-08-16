# -*- coding: utf-8 -*-
from gluon import *

class TableCheckbox(FORM):
    
    def __init__(self, id_getter=lambda row: row.id, 
                 tablecheckbox_var='tablecheckbox',
                 confirm_message='"Are you sure you want to submit?"',
                 submit_button='Submit checks',
                 **attributes):
        FORM.__init__(self, **attributes)
        self.attributes['_class'] = 'tablecheckbox'
        self.tablecheckbox_var, self.confirm_message, self.submit_button = (
            tablecheckbox_var, confirm_message, submit_button
        )
        self._checkall = '%s_checkall' % self.tablecheckbox_var
        self._selected = '%s_selected' % self.tablecheckbox_var
        self._button = '%s_button' % self.tablecheckbox_var
        
        self.append(SCRIPT("""
jQuery(document).ready(function(){
    var selected_el = jQuery("input[name=%(selected)s]");
    function set_activation(){setTimeout(function(){
        var button_el = jQuery('#%(button)s');
        selected_el.each(function(){
            if(jQuery(this).is(':checked')) { button_el.prop({disabled: false}); return false;
            } else { button_el.prop({disabled: true}); }}); }, 10); }
    selected_el.change(set_activation);
    jQuery("input[name=%(checkall)s]").change(set_activation);
});""" % dict(checkall=self._checkall, selected=self._selected, button=self._button)))
        self.append(INPUT(_type='hidden', _name=self.tablecheckbox_var))
        self.append(INPUT(_type='submit', _value=self.submit_button, 
              _onclick=self._get_submit_js(),
              _id=self._button, _disabled='disabled'))
      
    def column(self):
        return {'label':INPUT(_type='checkbox', _name=self._checkall, 
                                _onclick=self._get_toggle_all_js()),
                'content':lambda row, rc: DIV(INPUT(_type='checkbox', _name=self._selected, 
                                                    _value=row.id, _style='margin:3px;'),
                                              _style='text-align:center;'),
                'width': '', 'class': '', 'selected': False}
         
    def accepts(self, *args, **kwds):
        accepted = FORM.accepts(self, *args, **kwds)
        if accepted:
            self.vars[self.tablecheckbox_var] = current.request.vars[self.tablecheckbox_var].split(',')
        return accepted
        
    def xml(self): 
        return FORM.xml(self) 
                
    def _get_toggle_all_js(self):
        return """
jQuery('input[name=%(selected)s]').prop('checked', jQuery('input[name=%(checkall)s]').is(':checked'));
""" % dict(checkall=self._checkall, selected=self._selected)

    def _get_submit_js(self):
        return """
if(confirm(%(confirm_message)s)){
    var val = [];
    jQuery("input[name=%(selected)s]").each(function(){
        var el = jQuery(this);
        if(el.is(':checked')) { val.push(el.val()); }
    });
    jQuery("input[name=%(tablecheckbox)s]").val(val);
    return true;
;}; return false;""" % dict(confirm_message=self.confirm_message,
                            selected=self._selected,
                            tablecheckbox=self.tablecheckbox_var)
