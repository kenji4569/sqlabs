# -*- coding: utf-8 -*-
from plugin_uploadify_widget import (
    uploadify_widget, IS_UPLOADIFY_IMAGE, IS_UPLOADIFY_FILENAME, IS_UPLOADIFY_LENGTH
)

db.define_table('uploadify', 
    Field('image', 'upload', autodelete=True),
    Field('text', 'upload', autodelete=True))
    
db.uploadify.image.widget = uploadify_widget
db.uploadify.image.requires = [IS_UPLOADIFY_IMAGE(), IS_UPLOADIFY_LENGTH(10240)]

db.uploadify.text.widget = uploadify_widget
db.uploadify.text.requires = IS_EMPTY_OR([IS_UPLOADIFY_FILENAME(extension='txt'), 
                                          IS_UPLOADIFY_LENGTH(1024)])
    
if db(db.uploadify.id>0).count() > 5:
    last = db(db.uploadify.id>0).select(orderby=~db.uploadify.id).first()
    db(db.uploadify.id<=last.id-5).delete()

def index():
    form = SQLFORM(db.uploadify, upload=URL('download'))
    if form.accepts(request.vars, session):
        session.flash = 'submitted %s' % form.vars
        redirect(URL('index'))
    
    records = db(db.uploadify.id>0).select(orderby=~db.uploadify.id)
    records = SQLTABLE(records, upload=URL('download'), linkto=lambda f, t, r: URL('edit', args=f))
    return dict(form=form, records=records)
    
def edit():
    record = db(db.uploadify.id==request.args(0)).select().first() or redirect('index')
    form = SQLFORM(db.uploadify, record, upload=URL('download'))
    if form.accepts(request.vars, session):
        session.flash = 'edit %s' % form.vars
        redirect(URL('edit', args=request.args))
    
    return dict(back=A('back', _href=URL('index')), form=form)
    
def download():
    return response.download(request,db)