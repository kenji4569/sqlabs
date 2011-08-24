# -*- coding: utf-8 -*-

def index():
    return dict(
        products=[
            (k, info_products[k])
                for k in ['web2py_plugins', 'cloudmap', 
                          'nanahoshi_cms', 'nanahoshi_db']
        ],
    )
    