# -*- coding: utf-8 -*-
from plugin_elrte_widget import ElrteWidget
from plugin_mmodal import PluginMModal
from plugin_uploadify_widget import (
    uploadify_widget, IS_UPLOADIFY_IMAGE, IS_UPLOADIFY_LENGTH, FILES as UPLOADIFY_FILES
)
import gluon.contrib.simplejson as json

# use disk_db for image storing
disk_db = db
    
# define a product table using memory db
db = DAL('sqlite:memory:')
db.define_table('product', Field('description', 'text'))

# define an image table using sqlite db
image_table = disk_db.define_table('plugin_elrte_widget_image', 
    Field('image', 'upload', autodelete=True, comment='<- upload an image file(max file size=10k)'),
    )
image_table.image.widget = uploadify_widget
image_table.image.requires = [IS_UPLOADIFY_IMAGE(), IS_UPLOADIFY_LENGTH(10240)]
if disk_db(image_table.id>0).count() > 3:
    last = disk_db(image_table.id>0).select(orderby=~image_table.id).first()
    disk_db(image_table.id<=last.id-3).delete()

def index():
    # set language
    try:
        lang = T.accepted_language.split('-')[0].replace('ja', 'jp')
    except:
        lang = 'en'

    # set image chooser window
    image_chooser = PluginMModal( # (this could be refactored more)
        title='Select',
        content=LOAD('plugin_elrte_widget', 'upload_or_choose', ajax=True).xml().replace('<!--', '').replace('//-->', ''),
        close="close")
    fm_open = """function(callback){
var el = jQuery("#%s");
if (el.length == 0) {el = jQuery(%s); jQuery(document.body).append(el);}
el.show();
jQuery.data(document.body, 'elrte_callback', callback)
}""" % (image_chooser.id, json.dumps(image_chooser.xml()))

    ################################ The core ######################################
    # Inject the elrte widget
    # You can specify the language for the editor, and include your image chooser.
    # In this demo, the image chooser uses the uploadify plugin.
    db.product.description.widget = ElrteWidget(lang=lang, fm_open=fm_open)
    ################################################################################

    form = SQLFORM(db.product)
    if form.accepts(request.vars, session):
        session.flash = 'submitted %s' % form.vars
        redirect(URL('index'))
        
    response.files += UPLOADIFY_FILES # the uploadify files need to be loaded before ajax (presumably). 
    return dict(form=form)
    
def upload_or_choose():
    form = SQLFORM(image_table, upload=URL('download'))
    info = ''
    if form.accepts(request.vars, session):
        info = 'submitted %s' % form.vars
    
    records = disk_db(image_table.id>0).select(orderby=~image_table.id)
    _get_src = lambda r: URL(request.controller, 'download', r.image)
    records = DIV([IMG(_src=_get_src(r), 
                       _onclick="jQuery.data(document.body, 'elrte_callback')('%s');jQuery('.plugin_mmodal').hide();" % _get_src(r),
                       _style='max-width:50px;max-height:50px;margin:5px;cursor:pointer;') 
                    for r in records])
    return BEAUTIFY(dict(form=form, info=info, records=records))
    
def download():
    return response.download(request,disk_db)
