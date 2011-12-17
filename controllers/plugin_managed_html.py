# -*- coding: utf-8 -*-
#from plugin_bootstrap import Messaging
from plugin_managed_html import ManagedHTML
from gluon.storage import Storage

from plugin_uploadify_widget import (
    uploadify_widget, IS_UPLOADIFY_IMAGE, IS_UPLOADIFY_LENGTH
)
### setup core objects #########################################################
managed_html = ManagedHTML(db)
managed_html.settings.table_content_name = 'plugin_managed_html_content'
managed_html.settings.table_file_name = 'plugin_managed_html_file'
managed_html.settings.extra_fields = {
    'plugin_managed_html_content': [
        Field('created_on', 'datetime', default=request.now, 
              readable=False, writable=False)],
    'plugin_managed_html_file': [
        Field('created_on', 'datetime', default=request.now, 
              readable=False, writable=False)],
}

managed_html.settings.home_url = URL('web2py_plugins', 'index')
managed_html.settings.home_label = 'Web2py plugins'

managed_html.settings.page_crud = DIV('TODO')

image_crud_keyword = 'managed_html_image_crud'
managed_html.settings.image_crud =LOAD(
    url=URL(args=request.args, vars={image_crud_keyword:True}), ajax=True)

managed_html.switch_mode()
    
### define tables ##############################################################
managed_html.define_tables()
table_content = managed_html.settings.table_content
table_image = managed_html.settings.table_image
table_image.name.widget = uploadify_widget
table_image.name.uploadfolder = managed_html.settings.uploadfolder
table_image.name.comment = '<- upload an image (max file size=10k)'
# table_image.name.requires = [IS_UPLOADIFY_LENGTH(10240, 1), IS_UPLOADIFY_IMAGE()]

### populate records ###########################################################
import datetime
if db(table_content.created_on<request.now-datetime.timedelta(minutes=60)).count():
    table_content.truncate()
    table_image.truncate()
    session.flash = 'the database has been refreshed'
    redirect(managed_html.edit_url('page1'))

### demo functions #############################################################

# for ajax
if image_crud_keyword in request.vars or request.args(2) == image_crud_keyword:
    form = SQLFORM(table_image, upload=managed_html.settings.upload)
    info = ''
    if form.accepts(request.vars, session):
        managed_html.oncreate_image(form)
        info = 'submitted' 
    
    records = db(table_image.id>0).select(orderby=~table_image.id, limitby=(0,3))
    _get_src = lambda r: URL(request.controller, 'download', args=r.name)
    records = DIV([IMG(_src=_get_src(r), 
                       _onclick="""
jQuery(document.body).trigger('managed_html_image_selected', '%s');return false;
""" % _get_src(r),
                       _style='max-width:50px;max-height:50px;margin:5px;cursor:pointer;') 
                    for r in records])
    el = BEAUTIFY(dict(form=form, info=info, records=records))
    raise HTTP(200, el)
    
def index():
    return dict(page1=A('page1', _href=managed_html.edit_url('page1')),
                page2=A('page2', _href=managed_html.edit_url('page2')))
    
def page1():
    response.view = 'plugin_managed_html/page1.html'
    return dict(managed_html=managed_html, URL=managed_html.url, ORIGINAL_URL=URL)
                
def page2():
    response.view = 'plugin_managed_html/page2.html'
    return dict(managed_html=managed_html, URL=managed_html.url, ORIGINAL_URL=URL)
    
    
def download():
    return response.download(request, db)

    