# -*- coding: utf-8 -*-

def index():
    def _make_widgets_list(*plugin_names):
        widgets_list = []
        for plugin_name in plugin_names:
            info_plugin_meta = info_plugin_metas[plugin_name]
            widgets_list.append(
               (info_plugin_meta['label'], 
                URL(plugin_name, 'index'),
                info_plugin_meta['short_description'],
                info_plugin_meta.get('show_image') and URL('static', 'images/%s.png' % plugin_name) or None ) 
            )
        return widgets_list
        
    return dict(
        sections=[
            ('web2py-plugins', 
              SPAN(A('Web2py', _href='http://www.web2py.com'), """ 
is a powerful opensource web framework based on python programming language.
We have developed many products using this framework, and love to share useful code parts from the development.
The code parts are organized in """,
A("a web2py's plugin system", _href='http://web2py.com/book/default/chapter/13#Plugins'),
""". Try the demos and codes below."""),
              [('Form Customize',
                    _make_widgets_list(
                        'plugin_solidform', 
                        'plugin_hradio_widget', 
                        'plugin_multiselect_widget', 
                        'plugin_suggest_widget',
                        'plugin_lazy_options_widget',
                        'plugin_anytime_widget',
                        'plugin_color_widget',
                        'plugin_elrte_widget',
                    )),
                 ('Table Customize',
                     _make_widgets_list(
                        'plugin_solidtable', 
                        'plugin_paginator', 
                        'plugin_tablescope', 
                        'plugin_tablecheckbox', 
                        'plugin_tablepermuter', 
                    )),
                ('Cateogry Tools',
                     _make_widgets_list(
                        'plugin_mptt', 
                    )),
            ]),
        ],
    )