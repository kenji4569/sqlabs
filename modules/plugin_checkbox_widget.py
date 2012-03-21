from gluon import *

# For referencing static and views from other application
import os
APP = os.path.basename(os.path.dirname(os.path.dirname(__file__)))


def checkbox_widget(field, value, **attributes):
    url = URL(APP, 'static', 'plugin_checkbox_widget/checkbox.css')
    if url not in current.response.files:
        current.response.files.append(url)
            
    attributes['_class'] = 'plugin_checkbox_widget_wrapper'

    input_el = SQLFORM.widgets.boolean.widget(field, value)
    input_el.attributes['_class'] += ' plugin_checkbox_widget'

    classes = 'plugin_checkbox_widget_label'
    
    if value:
        classes += " plugin_checkbox_widget_selected"
    label = LABEL('', _class=classes,
                  _for=field.tablename + '_' + field.name)

    script = SCRIPT("""
jQuery("#%(id)s").change(function(){
    var el = jQuery(this);
    if(el.is(":checked")){
        el.parent().children('label').addClass("plugin_checkbox_widget_selected");
    }else{
        el.parent().children('label').removeClass("plugin_checkbox_widget_selected");
    }
});
    """ % dict(id=input_el.attributes['_id']))
    return DIV(input_el, label, script, **attributes)
