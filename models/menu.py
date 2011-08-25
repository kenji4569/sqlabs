# -*- coding: utf-8 -*-

if request.controller == 'default':
    response.title = request.application
else:
    response.title = '%s | %s' % (request.controller, request.application)

response.meta.author = 'S-cubism'
response.meta.description = 'Demos for developmental products by S-cubism, including web2py-plugins.'
response.meta.keywords = 'web2py, python, framework, web2py-plugin, cms'
