# -*- coding: utf-8 -*-

def index():
    def _make_widgets_list(*plugin_names):
        widgets_list = []
        for plugin_name in plugin_names:
            info_plugin_meta = info_plugin_metas[plugin_name]
            widgets_list.append(
               (info_plugin_meta['label'], 
                URL(plugin_name, 'index'),
                info_plugin_meta['short_description']) 
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
              [('Custom Widgets',
                    _make_widgets_list(
                        'plugin_hradio_widget', 
                        'plugin_multiselect_widget', 
                        'plugin_suggest_widget',
                        'plugin_lazy_options_widget',
                    )),
                 ('Grid Tools',
                     _make_widgets_list(
                        'plugin_solidtable', 
                    )),
                ('Custom Validators',
                     [('xxx Validator', 
                      URL('plugin_horizontal', 'index'),
                      """xxxxxxxxxxxxxxxxxxxxxx"""
                      ),
                      ('yyy Validator', 
                      URL('plugin_horizontal', 'index'),
                      """yyyyyyyyyyyyyyyyyyy"""
                      ),
                      ('zzz Validator', 
                      URL('plugin_horizontal', 'index'),
                      """zzzzzzzzzzzzzzzzzzzz"""
                      )
                     ]),
            ]),
        ],
    )