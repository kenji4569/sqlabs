# -*- coding: utf-8 -*-

info_plugin_metas = dict(
    plugin_horizontal_radio_widget=dict(
        label='Horizontal Radio Widget',
        short_description='A radio widget arranging its radio buttons horizontally.',
        long_description="""
In web2py, the default widget for a single select filed is a vertical radio widget,
which occupies a relatively large area. 
It's often the case that a horizontal radio widget is more appropriate.
So we implemented it, and further made it clickable on it's labels. 
""",
    ),
    plugin_multiselect_widget=dict(
        label='Multiselect Widget',
        short_description='A user-friendly multiselect widget.',
        long_description="""
In web2py, the default widget for a multiple select field is made by a select input tag,
which becomes difficult to handle when it had many option items.
So we built a custom multiple select widget which would be more user-friendly.
""",
    ),
    plugin_suggest_widget=dict(
        label='Suggest Widget',
        short_description=' ',
        long_description=""" """,
    ),
    plugin_lazy_options_widget=dict(
        label='Lazy Options Widget',
        short_description=' ',
        long_description=""" """,
    ),
)

if request.controller.startswith('plugin_'):
    import os
    from gluon.storage import Storage

    def _to_code(lines):
        return CODE(''.join(lines[1:]).strip(' ').strip('\n'))
        
    def _get_code(path):
        if not os.path.exists(path):
            raise HTTP(404)
        f = open(path, 'r')
        lines = f.readlines()
        f.close()
        return _to_code(lines)

    plugin_name = request.controller
    
    # reload the plugin module
    local_import(plugin_name, reload=True)
    
    # load the controll (usage) code
    controller_code = _get_code(os.path.join(request.folder, 'controllers', '%s.py' % plugin_name))
    
    # load the module (source) code
    module_code = _get_code(os.path.join(request.folder, 'modules', '%s.py' % plugin_name))
    
    info_plugin = info_plugin_metas[plugin_name]
    response.web2py_plugins = Storage(
        plugin_name=plugin_name,
        plugin_label=info_plugin['label'],
        plugin_description=info_plugin['long_description'],
        controller_code=controller_code,
        module_code=module_code,
    )
    response.view = 'web2py_plugins.html'