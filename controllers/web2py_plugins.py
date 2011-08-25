# -*- coding: utf-8 -*-

@cache(request.env.path_info, time_expire=10, cache_model=cache.ram)
def index():
    d = dict(
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
                ('Content Enhancement',
                     map(lambda k: (k, info_plugin_metas[k]), (
                        'plugin_mptt', 
                        'plugin_treeviewer',
                        'plugin_revision_crud',
                        'plugin_generic_menu',
                        'plugin_tagging',
                        'plugin_recommender',
                    ))),
                ('Others Tools',
                     map(lambda k: (k, info_plugin_metas[k]), (
                        'plugin_crontools', 
                        'plugin_deploytools',
                        'plugin_testtools',
                    ))),
            ]),
        ],
    )
    return response.render(d)