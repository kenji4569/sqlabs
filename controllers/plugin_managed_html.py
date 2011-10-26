# -*- coding: utf-8 -*-
#from plugin_bootstrap import Messaging
from plugin_managed_html import ManagedHTML
from gluon.storage import Storage

### setup core objects #########################################################
managed_html = ManagedHTML(db)
managed_html.settings.table_content_name = 'plugin_managed_html_content'
managed_html.settings.table_response_name = 'plugin_managed_html_response'
managed_html.settings.extra_fields = {
    'plugin_managed_html_content': [
        Field('created_on', 'datetime', default=request.now, 
              readable=False, writable=False)],
}

### define tables ##############################################################
managed_html.define_tables()
table_content = managed_html.settings.table_content
table_response = managed_html.settings.table_response

### populate records ###########################################################
import datetime
if db(table_content.created_on<request.now-datetime.timedelta(minutes=60)).count():
    for table in (table_content, table_response):
        table.truncate()
    session.flash = 'the database has been refreshed'
    redirect(URL('index'))

### demo functions #############################################################

def index():
    return dict(edit=A('page1', _href=URL('page1', vars=dict(managed_html_view_mode='edit'))),
                live=A('page1', _href=URL('page1')),
                preview=A('page1', _href=URL('page1', vars=dict(managed_html_view_mode='preview'))))
    
def page1():
    if request.get_vars.managed_html_view_mode == 'edit':
        managed_html.switch_to_edit_mode()
    elif request.get_vars.managed_html_view_mode == 'preview':
        managed_html.switch_to_preview_mode()
       
    product = Storage({'id': 1, 'name': 'Product 1'})
    
    view = DIV(
        managed_html.response('page1'), # execute before head rendering in view
        DIV(managed_html('header', default='header')),
        H1(response.title or ''),
        DIV(managed_html('product_%s' %  product.id, 
                         wrapper=lambda c: DIV(H4(product.name), c))), 
        HR(),
        DIV(managed_html('footer', default='footer')),
    )
    
    return dict(back=A('back', _href=URL('index')),
                view=view)
    
    