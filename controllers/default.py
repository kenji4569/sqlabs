# -*- coding: utf-8 -*-

def index():
    def _make_widgets_list(*plugin_names):
        widgets_list = []
        for plugin_name in plugin_names:
            info_plugin_meta = info_plugin_metas[plugin_name]
            widgets_list.append(
               (info_plugin_meta['label'], 
                URL('web2py_plugins', 'index', args=plugin_name),
                info_plugin_meta['short_description']) 
            )
        return widgets_list
        

    return dict(
        sections=[
            ('web2py-plugins', 
              SPAN(A('Web2py', _href="http://www.web2py.com"), """ 
is a powerful opensource web framework based on python programming language.
We have developed many products using the framework, and want to share some code parts of the products.
Thanks to a web2py's plugin system, the code parts should be quite portable. Have a look at the codes and try the demos."""),
              [('Custom Widgets',
                _make_widgets_list(
                    'plugin_horizontal_radio_widget', 
                    'plugin_multiselect_widget', 
                    'plugin_suggest_widget',
                    'plugin_lazy_options_widget',
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