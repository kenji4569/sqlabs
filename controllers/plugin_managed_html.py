# -*- coding: utf-8 -*-
#from plugin_bootstrap import Messaging
from plugin_managed_html import ManagedHTML
from gluon.storage import Storage

### setup core objects #########################################################
managed_html = ManagedHTML(db)
managed_html.settings.table_content_name = 'plugin_managed_html_content'
managed_html.settings.extra_fields = {
    'plugin_managed_html_content': [
        Field('created_on', 'datetime', default=request.now, 
              readable=False, writable=False)],
}

### define tables ##############################################################
managed_html.define_tables()
table_content = managed_html.settings.table_content

### populate records ###########################################################
import datetime
if db(table_content.created_on<request.now-datetime.timedelta(minutes=60)).count():
    table_content.truncate()
    session.flash = 'the database has been refreshed'
    redirect(URL('index'))

### demo functions #############################################################

def index():
    return dict(edit=A('page1', _href=URL('page1', vars=dict(_managed_html_view_mode='edit'))),
                live=A('page1', _href=URL('page1')),
                preview=A('page1', _href=URL('page1', vars=dict(_managed_html_view_mode='preview'))))
    
def page1():
    
    response.view = 'plugin_managed_html/page1.html'
    if request.get_vars._managed_html_view_mode == 'edit':
        managed_html.switch_to_edit_mode()
    elif request.get_vars._managed_html_view_mode == 'live':
        managed_html.switch_to_live_mode()
    elif request.get_vars._managed_html_view_mode == 'preview':
        managed_html.switch_to_preview_mode()
    
    product = Storage({'id': 1, 'name': 'Product 1'})
    
    return dict(back=A('back', _href=URL('index')),
                managed_html=managed_html)
    
    