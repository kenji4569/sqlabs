# -*- coding: utf-8 -*-

def index():
    return dict(
        sections=[
            ('web2py-plugins', 
              SPAN(A('Web2py', _href="http://www.web2py.com"), """ 
is a powerful opensource web framework based on python programming language.
We have developed many products using the framework, and want to share some code parts of the products.
Thanks to a web2py's plugin system, the code parts should be quite portable. Have a look at the codes and try the demos."""),
              [('Custom Widgets',
                [('Horizontal Radio Widget', 
                  URL('plugin_horizontal_widget', 'index'),
                  """This widget ..."""
                  ),
                 ('Multiselect Widget', 
                  URL('plugin_multiselect_widget', 'index'),
                  """This widget ..."""
                  ),
                 ('Suggest Widget', 
                  URL('plugin_suggest_widget', 'index'),
                  """This widget ..."""
                  ),
                  ('Lazy Options Widget', 
                  URL('plugin_lazy_options_widget', 'index'),
                  """This widget ..."""
                  ),
                 ]),
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