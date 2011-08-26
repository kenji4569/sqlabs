# -*- coding: utf-8 -*-

@cache('%s-%s' % (request.env.path_info, T.accepted_language), time_expire=10, cache_model=cache.ram)
def index():
    d = dict(
        products=[
            (k, info_products[k])
                for k in ['web2py_plugins', 'cloudmap', 
                          'nanahoshi_cms', 'nanahoshi_db']
        ],
    )
    return response.render(d)
    