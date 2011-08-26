# -*- coding: utf-8 -*-

if request.controller == 'default':
    response.title = request.application
else:
    response.title = '%s | %s' % (request.controller, request.application)

response.meta.author = 'S-cubism'
response.meta.description = response.meta.description or T("Introducing new products or services being developed by %s") % 'S-cubism'
response.meta.keywords = 'web2py, python, framework, web2py-plugin, cms'
