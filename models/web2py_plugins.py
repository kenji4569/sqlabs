# -*- coding: utf-8 -*-

def get_info_plugin_metas(): 
    return dict(
    plugin_solidform=dict(
        label='Solid Form',
        short_description='A custom SQLFORM with denser layout',
        long_description=SPAN("""
A custom """, A('SQLFORM', _href='http://web2py.com/book/default/chapter/07#SQLFORM'),
""" with denser layout using multi-line columns. 
You can specify structured fields corresponding to the layout.
Other functionarities are same as SQLFORM, including facotry and readonly forms.
""")),
    plugin_notemptymarker=dict(
        label='Not-Empty Marker',
        short_description='Adding not-empty marker to a field label',
        long_description="""
This plugin automatically attaches not-empty markers to forms 
for each "not-empty" field, based on field validators.
Note that the current implemntation changes field labels.
        """,
    ),
    plugin_hradio_widget=dict(
        label='Horizontal Radio Widget',
        short_description='A radio widget arranging its radio buttons horizontally',
        long_description=SPAN(
A('A built-in radio widget in web2py', _href='http://web2py.com/examples/static/epydoc/web2py.gluon.sqlhtml.RadioWidget-class.html'), 
""" arranges its radio buttons vertically, which occupies a relatively large area. 
Here we implemented a horizontal radio widget, and further made it clickable for it's labels. 
"""),
    ),
    plugin_multiselect_widget=dict(
        label='Multiple Select Widget',
        short_description='A user-friendly multiple options widget',
        long_description=SPAN(
A('A built-in multiple options widget in web2py', _href='http://web2py.com/examples/static/epydoc/web2py.gluon.sqlhtml.MultipleOptionsWidget-class.html'),
""" is made by a single select input tag,
which would be difficult to handle when it had many options.
We built more user-friendly multiple select widget with two select input tags.
"""),
    ),
    plugin_suggest_widget=dict(
        label='Suggest Widget',
        short_description='A refined autocomplete widget',
        long_description=SPAN(""" 
The suggest widget is an alternative for """,
A("a built-in autocomplete widget in web2py", _href='http://web2py.com/book/default/chapter/07#Widgets'), """.
It uses """, A('a suggest.js', _href='http://www.vulgarisoip.com/2007/08/06/jquerysuggest-11/'), 
""" with some modifications to handle non-us charcters. 
Further, it visualize a selecting status at each typing step."""),
    ),
    plugin_lazy_options_widget=dict(
        label='Lazy Options Widget',
        short_description='A lazy loading options widget triggered by a js event',
        long_description=SPAN("""
The lazy options widget receives js events and sends ajax requests 
to fill its select options as in """, 
A('the normal options widget', _href='http://web2py.com/examples/static/epydoc/web2py.gluon.sqlhtml.OptionsWidget-class.html'), """.
"""),),
    plugin_anytime_widget=dict(
        label='Anytime Widget',
        short_description='A date-time picker widget using anytime.js',
        long_description=SPAN("""
This plugin provides picker widgets for time, date and datetime fileds, 
using """, A('anytime.js', _href='http://www.ama3.com/anytime/'), """.
"""),),
    plugin_color_widget=dict(
        label='Color Widget',
        short_description='A color picker widget using colorpicker.js',
        long_description=SPAN("""
This plugin provides a color picker widget, 
using """, A('colorpicker.js', _href='http://www.eyecon.ro/colorpicker/'), """.
Picked color is displayed in forms.
"""),),
    plugin_elrte_widget=dict(
        label='elRTE WYSIWYG Widget',
        short_description='A WYSIWYG editor widget using elRTE.js',
        long_description=SPAN("""
A WYSIWYG editor widget
using """, A('elRTE.js', _href='http://elrte.org/'), """.
You can specify the language for the editor via a contructor argument.
"""),),
    plugin_uploadify_widget=dict(
        label='Uploadify Widget',
        short_description='A file upload widget using uploadify.js',
        long_description=SPAN("""
A file upload widget 
using """, A('uploadify.js', _href='http://www.uploadify.com/'), """.
The uploadify turns a file input to a flash-based file uploader,
which displays a progress bar and enables ajax upload. 
"""),),
    plugin_solidtable=dict(
        label='Solid Table',
        short_description='A custom SQLTABLE with denser layout',
        long_description=SPAN("""
A custom """, A('SQLTABLE', _href='http://web2py.com/book/default/chapter/06#Serializing-Rows-in-Views'),
""" with denser layout using multi-line rows. 
You can specify structured fields corresponding to the layout.
The interface of the class is backward-compatible to the SQLTABLE,
and enables more flexible customization.
"""),),
    plugin_paginator=dict(
        label='Pagenator',
        short_description='A standard paginator',
        long_description=SPAN("""
A standard paginator used with SQLTABLE. The basic design is inspired by """, 
A('this discussion', _href='http://groups.google.com/group/web2py/browse_frm/thread/d1ec3ded48839071#'), 
""".
"""),
    ),
    plugin_tablescope=dict(
        label='Table Scope',
        short_description='A standard table scope selector',
        long_description="""
The table scope selects db records based on values of a field such as status,
and counts records for each value of the field.""",
    ),
    plugin_tablecheckbox=dict(
        label='Table Checkbox',
        short_description='Attaching checkboxes to a table',
        long_description=""" 
The table checkbox provides an extra column with checkboxes for records in a table.
This is a kind of form object and submits selected record ids.
""",
    ),
    plugin_tablepermuter=dict(
        label='Table Permuter',
        short_description='Making table rows permutable',
        long_description=SPAN(""" 
The table permuter makes table rows permutable using """,
A('jquery.tablednd.js', _href='http://www.isocra.com/2008/02/table-drag-and-drop-jquery-plugin/'), """.
This is a kind of form object and submits permuted row indices.
"""),
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
)

if request.controller.startswith('plugin_'):
    import os
    from gluon.admin import apath
    from gluon.fileutils import listdir
    from gluon.storage import Storage

    def _to_code(lines):
        return CODE(''.join(lines[1:]).strip(' ').strip('\n').replace('\r', ''))
        
    def _get_code(directory, filename):
        path = os.path.join(request.folder, directory, filename)
        def _get_code_core():
            if not os.path.exists(path):
                raise HTTP(404)
            f = open(path, 'r')
            lines = f.readlines()
            f.close()
            return _to_code(lines)
        return cache.ram('code:%s/%s' % (directory, filename), _get_code_core, time_expire=10)

    plugin_name = request.controller
    
    # reload the plugin module
    local_import(plugin_name, reload=MODULE_RELOAD)
    
    # load the controll (usage) code
    controller_code = _get_code('controllers', '%s.py' % plugin_name)
    
    # load the module (source) code
    module_code = _get_code('modules', '%s.py' % plugin_name)
    
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
        plugin_label=info_plugin['label'],
        plugin_short_description=info_plugin['short_description'],
        plugin_long_description=info_plugin['long_description'],
        controller_code=controller_code,
        module_code=module_code,
        statics=statics,
    )
    response.image = URL('static', 'images/%s.png' % plugin_name)
    response.view = 'web2py_plugins.html'