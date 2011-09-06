# -*- coding: utf-8 -*-
from plugin_elrte_widget import ElrteWidget, Dialog
from plugin_uploadify_widget import (
    uploadify_widget, IS_UPLOADIFY_IMAGE, IS_UPLOADIFY_LENGTH
)

# use disk_db for image storing
disk_db = db
    
# define a product table using memory db
db = DAL('sqlite:memory:')
db.define_table('product', Field('description', 'text'))

# define an image table using disk db
image_table = disk_db.define_table('plugin_elrte_widget_image', 
    Field('image', 'upload', autodelete=True, comment='<- upload an image (max file size=10k)'),
    )
image_table.image.widget = uploadify_widget
image_table.image.requires = [IS_UPLOADIFY_LENGTH(10240, 1), IS_UPLOADIFY_IMAGE()]

# define a file table using disk db
file_table = disk_db.define_table('plugin_elrte_widget_file', 
    Field('file', 'upload', autodelete=True, comment='<- upload a file(max file size=100k)'),
    )
file_table.file.widget = uploadify_widget
file_table.file.requires = IS_UPLOADIFY_LENGTH(102400, 1)

# restrict records for demo
for table in (image_table, file_table):
    if disk_db(table.id>0).count() > 3:
        last = disk_db(table.id>0).select(orderby=~table.id).first()
        disk_db(table.id<=last.id-3).delete()

def index():
    # set language
    try:
        lang = T.accepted_language.split('-')[0].replace('ja', 'jp')
    except:
        lang = 'en'

    image_chooser = Dialog(title='Select', 
                           content=LOAD('plugin_elrte_widget', 'image_upload_or_choose', ajax=True))
    file_chooser = Dialog(title='Select', 
                          content=LOAD('plugin_elrte_widget', 'file_upload_or_choose', ajax=True))
    fm_open = """function(callback, kind){
if (kind == 'elfinder') {%s();} else {%s();}
jQuery.data(document.body, 'elrte_callback', callback)
}""" % (file_chooser.get_show_js(), image_chooser.get_show_js())

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
        
    return dict(form=form)
    
def image_upload_or_choose():
    form = SQLFORM(image_table, upload=URL('download'))
    info = ''
    if form.accepts(request.vars, session):
        info = 'submitted %s' % form.vars
    
    records = disk_db(image_table.id>0).select(orderby=~image_table.id, limitby=(0,3))
    _get_src = lambda r: URL(request.controller, 'download', r.image)
    records = DIV([IMG(_src=_get_src(r), 
                       _onclick="jQuery.data(document.body, 'elrte_callback')('%s');jQuery('.dialog').hide();" % _get_src(r),
                       _style='max-width:50px;max-height:50px;margin:5px;cursor:pointer;') 
                    for r in records])
    return BEAUTIFY(dict(form=form, info=info, records=records))
    
def file_upload_or_choose():
    form = SQLFORM(file_table, upload=URL('download'))
    info = ''
    if form.accepts(request.vars, session):
        info = 'submitted %s' % form.vars
    
    records = disk_db(file_table.id>0).select(orderby=~file_table.id, limitby=(0,3))
    _get_src = lambda r: URL(request.controller, 'download', r.file)
    records = DIV([IMG(_src=_get_src(r), 
                       _onclick="jQuery.data(document.body, 'elrte_callback')('%s');jQuery('.dialog').hide();" % _get_src(r),
                       _style='max-width:50px;max-height:50px;margin:5px;cursor:pointer;') 
                    for r in records])
    return BEAUTIFY(dict(form=form, info=info, records=records))
    
def download():
    return response.download(request,disk_db)
