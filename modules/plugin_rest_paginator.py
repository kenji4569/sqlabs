# -*- coding: utf-8 -*-
from gluon.storage import Storage
from gluon import *


def paginate_load(load_url,
                  preinput='',
                  limit=10,
                  page_request_func='''function(vars, page_index){vars['offset'] = page_index * vars['limit_'+'default'];}''',
                  get_total_count_func='''function($results){ return $(".total_count", this.$results).text();}''',
                  name='default',
                  vars={},
                  renderstyle=False,
                  direct_import=False):
    '''example
    {{
    from plugin_rest_paginator import paginate_load
    vars = { '_template':URL('static', 'page', args=response.page.tenant + '/template/' + 'news_detail.handlebars'),
             'limit':request.vars['limit_'+name] if request.vars.has_key('limit_'+name) else 4
             }
    if request.vars['category_'+name]:
        vars['category'] = request.vars['category_'+name]
    }}

    {{=
    paginate_load(load_url=URL(c,f,args=args,extension='load'),
                  preinput=LOAD(c, f, extension='load',
                                args=args,
                                vars=vars,
                                ajax=current.request.ajax)
                  limit=vars['limit'],
                  name='blog',
                  vars=vars,
                  page_request_func="function(vars, page_index){vars['offset'] = page_index * vars['limit_'+'blog'];}",
                  get_total_count_func="function($results){ this.num_entries = $(".total_count", $results).text();}",
                  direct_import=True,
                  )
    }}
    '''

    import gluon.contrib.simplejson
    script = '''
      (function(){
        _pagination_%(name)s = new Pagination("%(name)s", "%(url)s", %(limit)s, %(vars)s);
        _pagination_%(name)s['page_request_func'] = %(page_request_func)s;
        _pagination_%(name)s['get_total_count_func'] = %(get_total_count_func)s;
      })();

      $(function(){
        _pagination_%(name)s.run();
      });
    ''' % dict(name=name,
               url=load_url,
               limit=limit,
               vars=XML(gluon.contrib.simplejson.dumps(vars)),
               page_request_func=page_request_func,
               get_total_count_func=get_total_count_func,
               )

    pagination = DIV(_id='Pagination_'+name, _class='pagination')
    results = DIV(_id='results_'+name)
    results.append(preinput)

    ret = DIV()

    urls = [ URL('static','plugin_rest_paginator/jquery.pagination.js'),
             URL('static','plugin_rest_paginator/paginate.js') ]
    for _url in urls:
        if _url not in current.response.files:
            current.response.files.append(_url)
            if direct_import:
                ret.append(TAG.script(_type='text/javascript', _src=_url))
    if renderstyle:
        urls.append(URL('static','plugin_restful_paginate/paginate.css'))
        if direct_import:
            ret.append(TAG.link(_type='text/css', _rel='stylesheet', _href=URL('static','plugin_rest_paginator/paginate.css')))

    ret.append(TAG.script(XML(script), _type='text/javascript'))
    ret.append(results)
    ret.append(pagination)

    return ret



