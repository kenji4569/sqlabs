from gluon.storage import Storage
from gluon import *

#example
##  {{
## from plugin_rest_paginator import paginate_load
## vars = { '_template':URL('static', 'page', args=response.page.tenant + '/template/' + 'news_detail.handlebars'),
##          'limit':request.vars['limit'] if request.vars.has_key('limit') else 4
##          }
## if request.vars['category']:
##     vars['category'] = request.vars['category']
## }}

## {{=
## paginate_load('api_articles',
##               'articles',
##               limit=vars['limit'],
##               name='blog',
##               args=[response.tenant.name],
##               vars=vars,
##               page_request_func="function(vars, page_index){vars['offset'] = page_index * vars['limit'];}",
##               get_total_count_func="function(){ this.$results = $("#results_"+this.name); this.num_entries = $(".total_count", this.$results).text();}",
##               )
## }}


# i.e. {{=load_akamon_api_articles(args=[response.tenant.name])}}
def load_akamon_api_articles( c='api_articles',
                              f='articles',
                              template=None,
                              args=[],
                              limit=10,
                              name='blog',
                              template_name='default.handlebars',
                              renderstyle=True):
    if template is None:
        template = URL('static', 'page', args=current.response.tenant.name + '/template/' + template_name)
    if current.request.vars.has_key('limit'):
        limit = current.request.vars['limit']

    vars = { '_template':template,
             'limit':limit
             }

    if current.request.vars['category']:
        vars['category'] = current.request.vars['category']
    if current.request.vars['offset']:
        vars['offset'] = current.request.vars['offset']
    
    return paginate_load(c,
                         f,
                         limit=vars['limit'],
                         name=name,
                         args=args,
                         vars=vars,
                         page_request_func='''function(vars, page_index){vars['offset'] = page_index * vars['limit'];}''',
                         get_total_count_func='''function(){ this.$results = $("#results_"+this.name); this.num_entries = $(".total_count", this.$results).text();}''',
                         renderstyle=renderstyle,
                         )

def paginate_load( c,
                   f,
                   limit=10,
                   page_request_func='''function(vars, page_index){vars['offset'] = page_index * vars['limit'];}''',
                   get_total_count_func='''function(){ this.$results = $("#results_"+this.name); this.num_entries = $(".total_count", this.$results).text();}''',
                   name='default',
                   args=[],
                   vars={},
                   renderstyle=False ):
    if args:
        load_url = URL(c, f, args=args, extension='load')
    else:
        load_url = URL(c, f, extension='load')
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
    results.append(LOAD(c, f, extension='load',
                        args=args,
                        vars=vars,
                        ajax=current.request.ajax))

    ret = DIV()

    urls = [ URL('static','plugin_rest_paginator/jquery.pagination.js'),
             URL('static','plugin_rest_paginator/paginate.js') ]
    for _url in urls:
        if _url not in current.response.files:
            current.response.files.append(_url)
            ret.append(TAG.script(_type='text/javascript', _src=_url))
    if renderstyle:
        urls.append(URL('static','plugin_restful_paginate/paginate.css'))
        ret.append(TAG.link(_type='text/css', _rel='stylesheet', _href=URL('static','plugin_rest_paginator/paginate.css')))

    ret.append(TAG.script(XML(script), _type='text/javascript'))
    ret.append(results)
    ret.append(pagination)

    return ret



