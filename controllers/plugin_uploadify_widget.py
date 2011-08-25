# -*- coding: utf-8 -*-
from plugin_uploadify_widget import (
    uploadify_widget, IS_UPLOADIFY_IMAGE, IS_UPLOADIFY_FILENAME, IS_UPLOADIFY_LENGTH
)
import random

table = db.define_table('plugin_uploadify_widget', 
    Field('name', default=''.join([random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890') 
                                        for i in range(10)])),
    Field('image', 'upload', autodelete=True),
    Field('text', 'upload', autodelete=True),
    )
    
################################ The core ######################################
# Inject the uploadify widget
# The "requires" needs custom validators.
table.image.widget = uploadify_widget
table.image.requires = [IS_UPLOADIFY_IMAGE(), IS_UPLOADIFY_LENGTH(10240)]
# Inject the another uploadify widget with different requires
table.text.widget = uploadify_widget
table.text.requires = IS_EMPTY_OR([IS_UPLOADIFY_FILENAME(extension='txt'), 
                                          IS_UPLOADIFY_LENGTH(1024)])
################################################################################
    
if db(table.id>0).count() > 5:
    last = db(table.id>0).select(orderby=~table.id).first()
    db(table.id<=last.id-5).delete()

def index():
    form = SQLFORM(table, upload=URL('download'))
    if form.accepts(request.vars, session):
        session.flash = 'submitted %s' % form.vars
        redirect(URL('index'))
    
    records = db(table.id>0).select(orderby=~table.id)
    records = SQLTABLE(records, headers="labels",
                       upload=URL('download'), linkto=lambda f, t, r: URL('edit', args=f))
    return dict(form=form, records=records)
    
def edit():
    record = db(table.id==request.args(0)).select().first() or redirect('index')
    form = SQLFORM(table, record, upload=URL('download'))
    if form.accepts(request.vars, session):
        session.flash = 'edit %s' % form.vars
        redirect(URL('edit', args=request.args))
    
    return dict(back=A('back', _href=URL('index')), form=form)
    
def download():
    return response.download(request,db)