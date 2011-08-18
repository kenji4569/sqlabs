# -*- coding: utf-8 -*-
from plugin_uploadify_widget import uploadify_widget

db.define_table('uploadify', 
    Field('image', 'upload'))
    
db.uploadify.image.widget = uploadify_widget
if db(db.uploadify.id>0).count() > 5:
    last = db(db.uploadify.id>0).select(orderby=~db.uploadify.id).first()
    db(db.uploadify.id<=last.id-5).delete()

def index():
    form = SQLFORM(db.uploadify)
    if form.accepts(request.vars, session):
        session.flash = 'submitted %s' % form.vars
        redirect(URL('index'))
    
    records = db(db.uploadify.id>0).select(orderby=~db.uploadify.id)
    print records
    return dict(form=form, records=SQLTABLE(records, upload=URL('download')))
    
def download():
    return response.download(request,db)