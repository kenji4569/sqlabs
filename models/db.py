# -*- coding: utf-8 -*-

db = DAL('sqlite://storage.sqlite')  

response.generic_patterns = ['*'] if request.is_local else []

info_products = dict(
    web2py_plugins= dict(
        label='web2py-plugins',
        description=SPAN(A('Web2py', _href='http://www.web2py.com'), """ 
is a powerful opensource web framework based on python programming language.
We have developed many products using this framework, and love to share useful code parts from the development.
The code parts are organized in """,
A("a web2py's plugin system", _href='http://web2py.com/book/default/chapter/13#Plugins'),
"""."""),
    ),
    cloudmap=dict(
        label='cloudmap',
        description=SPAN("""Cloudmap is a visual search engine for any contents with user evaluations."""),
        status='under-construction',
    ),
    nanahoshi_cms=dict(
        label='nanahoshi-cms',
        description='CMS based on web2py',
        status='under-construction',
    ),
    nanahoshi_db=dict(
        label='nanahoshi-db',
        description='NoSQL package based on a distributed KVS',
        status='under-construction',
    ),
)