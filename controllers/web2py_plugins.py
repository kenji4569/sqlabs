# -*- coding: utf-8 -*-
    
response.image = URL('static', 'images/products/web2py_plugins.jpg')

@cache('%s-%s' % (request.env.path_info, T.accepted_language), time_expire=10, cache_model=cache.ram)
def index():
    response.meta.description = T("""A collection of plugins of %s, an opensource Python web framework.
Here we love to share useful code parts produced by our development with the framework.
The code parts are organized in %s, and easily available.""") % ('Web2py', T("a web2py's plugin system"))
    info_plugin_metas = get_info_plugin_metas()
    d = dict(
        sections=[
            ('web2py_plugins', info_products['web2py_plugins'],
              [('Form Widgets',
                    map(lambda k: (k, info_plugin_metas[k]), (
                        'plugin_hradio_widget', 
                        'plugin_multiselect_widget', 
                        'plugin_suggest_widget',
                        'plugin_lazy_options_widget',
                        'plugin_uploadify_widget',
                        'plugin_elrte_widget',
                        'plugin_tight_input_widget',
                        'plugin_color_widget',
                        'plugin_rating_widget',
                        'plugin_anytime_widget',
                    ))),
                ('Form Customize',
                    map(lambda k: (k, info_plugin_metas[k]), (
                        'plugin_solidform', 
                        'plugin_notemptymarker',
                    ))),
                ('Table Customize',
                     map(lambda k: (k, info_plugin_metas[k]), (
                        'plugin_solidtable', 
                        'plugin_paginator', 
                        'plugin_tablescope', 
                        'plugin_tablecheckbox', 
                        'plugin_tablepermuter', 
                    ))),
                ('Content Management',
                     map(lambda k: (k, info_plugin_metas[k]), (
                        'plugin_solidgrid',
                        'plugin_dialog',
                        'plugin_mptt', 
                        'plugin_jstree', 
                    ))),
            ]),
        ],
    )
    return response.render(d)
    
def pack_plugin():
    from gluon.admin import plugin_pack
    app = request.application
    filename = ''
    if len(request.args) == 1:
        fname = 'web2py.plugin.%s.w2p' % request.args[0]
        filename = plugin_pack(app, request.args[0], request)
    if filename:
        response.headers['Content-Type'] = 'application/w2p'
        disposition = 'attachment; filename=%s' % fname
        response.headers['Content-Disposition'] = disposition
        f = open(filename, 'rb')
        try:
            return f.read()
        finally:
            f.close()
    else:
        session.flash = T('internal error')
        redirect(URL('index'))