# -*- coding: utf-8 -*-

def index():
    return dict(
        sections=[
            ('web2py_plugins', info_products['web2py_plugins'],
              [('Form Customize',
                    map(lambda k: (k, info_plugin_metas[k]), (
                        'plugin_solidform', 
                        'plugin_notemptymarker',
                        'plugin_hradio_widget', 
                        'plugin_multiselect_widget', 
                        'plugin_suggest_widget',
                        'plugin_lazy_options_widget',
                        'plugin_anytime_widget',
                        'plugin_color_widget',
                        'plugin_elrte_widget',
                        'plugin_uploadify_widget',
                    ))),
                ('Table Customize',
                     map(lambda k: (k, info_plugin_metas[k]), (
                        'plugin_solidtable', 
                        'plugin_paginator', 
                        'plugin_tablescope', 
                        'plugin_tablecheckbox', 
                        'plugin_tablepermuter', 
                    ))),
                ('Cateogry Tools',
                     map(lambda k: (k, info_plugin_metas[k]), (
                        'plugin_mptt', 
                    ))),
            ]),
        ],
    )