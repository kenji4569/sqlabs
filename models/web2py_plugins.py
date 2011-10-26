# -*- coding: utf-8 -*-

def get_info_plugin_metas(): 
    return dict(
    plugin_hradio_widget=dict(
        label='Horizontal Radio Widget',
        short_description=T('A radio widget arranging its buttons horizontally'),
        long_description=XML(T("""
%s arranges its radio buttons vertically, which occupies a relatively large area. 
Here we implemented a horizontal radio widget, and further made it clickable for it's labels. 
""") % A(T('A built-in radio widget'), _href='http://web2py.com/examples/static/epydoc/web2py.gluon.sqlhtml.RadioWidget-class.html').xml())
    ),
    plugin_multiselect_widget=dict(
        label='Multiple Select Widget',
        short_description=T('A user-friendly multiple options widget'),
        long_description=XML(T("""
%s is made by a single select tag,
which would be difficult to handle when it had many options.
We built more user-friendly multiple select widget with two select tags.
You can choice between horizontal or vertical layout.
""") % A(T('A built-in multiple options widget'), _href='http://web2py.com/examples/static/epydoc/web2py.gluon.sqlhtml.MultipleOptionsWidget-class.html').xml())   
    ),
    plugin_suggest_widget=dict(
        label='Suggest Widget',
        short_description=T('A refined autocomplete widget'),
        long_description=XML(T("""
The suggest widget is an alternative for %s.
It uses %s with some modifications to handle non-us charcters. 
Further, it visualize a selecting status at each typing step.
""") % (A(T("a built-in autocomplete widget"), _href='http://web2py.com/book/default/chapter/07#Widgets').xml(),
        A('suggest.js', _href='http://www.vulgarisoip.com/2007/08/06/jquerysuggest-11/').xml()))
    ),
    plugin_lazy_options_widget=dict(
        label='Lazy Options Widget',
        short_description=T('A lazy loading options widget triggered by a js event'),
        long_description=XML(T("""
The lazy options widget receives js events and sends ajax requests to populate its select options as in %s.
""") % A(T('a built-in options widget'), _href='http://web2py.com/examples/static/epydoc/web2py.gluon.sqlhtml.OptionsWidget-class.html').xml())
    ),
    plugin_anytime_widget=dict(
        label='Anytime Widget',
        adopted=True,
        short_description=T('A date-time picker widget using anytime.js'),
        long_description=XML(T("""
This plugin provides time, date and datetime picker widgets using %s.
""") % A('anytime.js', _href='http://www.ama3.com/anytime/').xml())
    ),
    plugin_color_widget=dict(
        label='Color Widget',
        short_description=T('A color picker widget using colorpicker.js'),
        long_description=XML(T("""
This plugin provides a color picker widget, using %s. Picked color is displayed in forms. 
""") % A('colorpicker.js', _href='http://www.eyecon.ro/colorpicker/').xml())
    ),
    plugin_elrte_widget=dict(
        label='elRTE WYSIWYG Widget',
        short_description=T('A WYSIWYG editor widget using elRTE.js'),
        long_description=XML(T("""
A WYSIWYG editor widget using %s. You can specify your language by a contructor argument, and include your image chooser.
""") % A('elRTE.js', _href='http://elrte.org/').xml())
    ),
    plugin_uploadify_widget=dict(
        label='Uploadify Widget',
        short_description=T('A file upload widget using uploadify.js'),
        long_description=XML(T("""
A file upload widget using %s.
The uploadify turns a file input tag into a flash-based file uploader,
which displays a progress bar and enables ajax upload. 
""") % A('uploadify.js', _href='http://www.uploadify.com/').xml())
    ),
    
    plugin_tight_input_widget=dict(
        label='Tight Input Widget',
        short_description=T('A size-adjusted input widget'),
        long_description=T("""
An input widget whose size is automatically adjusted to maximum length of its field value
 defined by validators such as IS_LENGTH and IS_INT_IN_RANGE.
The widget works with string, integer, double, and, decimal fields.
"""),
    ),
    
    plugin_solidform=dict(
        label='Solid Form',
        short_description=T('A custom SQLFORM for denser layout'),
        long_description=XML(T("""
A custom %s for denser layout using multi-line columns. 
You can specify structured fields corresponding to the layout.
Other functionarities are same as SQLFORM, including facotry and readonly forms.
""") % A('SQLFORM', _href='http://web2py.com/book/default/chapter/07#SQLFORM').xml())
    ),
    plugin_notemptymarker=dict(
        label='Not-Empty Marker',
        short_description=T('Add not-empty markers to field labels'),
        long_description=XML(T("""
This plugin automatically attaches not-empty markers to labels of "not-empty" fields of a form, 
based on field validators.
"""))
    ),
    plugin_solidtable=dict(
        label='Solid Table',
        short_description=T('A custom SQLTABLE for denser layout'),
        long_description=XML(T("""
A custom %s for denser layout using multi-line rows. 
You can specify structured fields corresponding to the layout.
The interface of the class keeps backward-compatible to the SQLTABLE,
and enables more flexible customization.
""") % A('SQLTABLE', _href='http://web2py.com/book/default/chapter/06#Serializing-Rows-in-Views').xml())
    ),
    plugin_paginator=dict(
        label='Paginator',
        short_description=T('A standard paginator'),
        long_description=XML(T("""
A standard paginator which can be used with SQLTABLE. The basic design is inspired by %s.
""") % A(T('this discussion'), _href='http://groups.google.com/group/web2py/browse_frm/thread/d1ec3ded48839071#').xml())
    ),
    plugin_tablescope=dict(
        label='Table Scope',
        short_description=T('A scope selector for table records'),
        long_description=T("""
This plugin provides buttons to select table records by a value of a field,
showing the record count for each value of the field.
"""),
    ),
    plugin_tablecheckbox=dict(
        label='Table Checkbox',
        short_description=T('A table column composed of checkboxes'),
        long_description=T("""
The plugin provides a form object which is an extra table column composed of checkboxes to select multiple records,
and submits selected record ids.
"""),
    ),
    plugin_tablepermuter=dict(
        label='Table Permuter',
        short_description=T('Make table rows permutable'),
        long_description=XML(T("""
This plugin a form object which makes table rows permutable using %s, and submits permuted row indices.
""") % A('jquery.tablednd.js', _href='http://www.isocra.com/2008/02/table-drag-and-drop-jquery-plugin/').xml())
    ),
    
    plugin_comment_cascade=dict(
        label='Comment Cascade',
        short_description=T('Make facebook-like comment boxes'),
        long_description=T("""A manager to make ajax-intensive comment boxes for a sort of news feed as in Facebook."""),
    ),
    plugin_friendship=dict(
        label='Friendship',
        short_description=T('A friendship manager'),
        long_description=T("""A manager to make friendship relations among users as in Facebook."""),
    ),
    plugin_messaging=dict(
        label='Messaging',
        short_description=T('A direct messaging manager'),
        long_description=T("""A manager for direct messaging between users as in Facebook."""),
    ),
    
    plugin_mptt=dict(
        label='Modified Preorder Tree Traversal',
        show_image=False,
        short_description='',
        long_description='',
        status='under-construction',
    ),
    plugin_treeviewer=dict(
        label='Tree Viewer',
        show_image=False,
        short_description='',
        long_description='',
        status='under-construction',
    ),
    plugin_revision_crud=dict(
        label='Revision CRUD',
        show_image=False,
        short_description='',
        long_description='',
        status='under-construction',
    ),
    plugin_generic_menu=dict(
        label='Generic Menu',
        show_image=False,
        short_description='',
        long_description='',
        status='under-construction',
    ),
    plugin_tagging=dict(
        label='Tagging',
        show_image=False,
        short_description='',
        long_description='',
        status='under-construction',
    ),
    plugin_recommender=dict(
        label='Recommender',
        show_image=False,
        short_description='',
        long_description='',
        status='under-construction',
    ),
    plugin_crontools=dict(
        label='Cron Tools',
        show_image=False,
        short_description='',
        long_description='',
        status='under-construction',
    ),
    plugin_deploytools=dict(
        label='Deploy Tools',
        show_image=False,
        short_description='',
        long_description='',
        status='under-construction',
    ),
    plugin_testtools=dict(
        label='Test Tools',
        show_image=False,
        short_description='',
        long_description='',
        status='under-construction',
    ),
    
    plugin_catalog=dict(
        label='Catalog',
        short_description='A minimum set of catalog models for shopping',
        long_description="""A minimum set of catalog models for shopping (Now Developping)""",
    ),
    plugin_checkout=dict(
        label='Checkout',
        show_image=False,
        short_description='A minimum set of checkout models for shopping',
        long_description="""A minimum set of checkout models for shopping (Now Developping)""",
        status='under-construction',
    ),
    
    plugin_managed_html=dict(
        label='Managed HTML',
        show_image=False,
        short_description='TODO',
        long_description="""TODO""",
        status='under-construction',
    ),
)

if request.controller.startswith('plugin_'):
    if request.controller == 'plugin_comment_box':
        session.flash = 'changed from plugin_comment_box to plugin_comment_cascade'
        redirect(URL('plugin_comment_cascade', 'index'))
        
    import os
    from gluon.admin import apath
    from gluon.fileutils import listdir
    from gluon.storage import Storage

    def _to_code(lines, linestart):
        return CODE(''.join(lines[linestart:]).strip(' ').strip('\n').replace('\r', ''))
        
    def _get_code(directory, filename, linestart):
        path = os.path.join(request.folder, directory, filename)
        def _get_code_core():
            if not os.path.exists(path):
                raise HTTP(404)
            f = open(path, 'r')
            lines = f.readlines()
            f.close()
            return _to_code(lines, linestart)
        return cache.ram('code:%s/%s' % (directory, filename), _get_code_core, time_expire=10)

    plugin_name = request.controller
    
    # reload the plugin module
    local_import(plugin_name, reload=MODULE_RELOAD)
    
    # load the controll (usage) code
    controller_code = _get_code('controllers', '%s.py' % plugin_name, linestart=1)
    
    # load the module (source) code
    module_code = _get_code('modules', '%s.py' % plugin_name, linestart=3)
    
    # Get static files
    def _get_statics():
        statics = listdir(apath('sqlabs/static/%s/' % plugin_name, r=request), '[^\.#].*')
        statics = [x.replace('\\','/') for x in statics]
        statics.sort()
        return statics
    statics = cache.ram('statics:%s' % plugin_name, _get_statics, time_expire=10)
    
    info_plugin = get_info_plugin_metas()[plugin_name]
    response.web2py_plugins = Storage(
        plugin_name=plugin_name,
        plugin_adopted=info_plugin.get('adopted', False),
        plugin_label=info_plugin['label'],
        plugin_short_description=info_plugin['short_description'],
        plugin_long_description=info_plugin['long_description'],
        controller_code=controller_code,
        module_code=module_code,
        statics=statics,
    )
    response.meta.description = info_plugin['short_description']
    response.image = URL('static', 'images/%s.png' % plugin_name)
    response.view = 'web2py_plugins.html'