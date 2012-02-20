# -*- coding: utf-8 -*-
from plugin_elrte_widget import ElrteWidget
from plugin_dialog import DIALOG
from plugin_uploadify_widget import (
    uploadify_widget, IS_UPLOADIFY_IMAGE, IS_UPLOADIFY_LENGTH
)
import uuid

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
    Field('name'),
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

    image_chooser = DIALOG(title=T('Select an image'), close=T('close'), renderstyle=True,
                           content=LOAD('plugin_elrte_widget', 'image_upload_or_choose', ajax=True))
    file_chooser = DIALOG(title=T('Select a file'), close=T('close'), renderstyle=True,
                          content=LOAD('plugin_elrte_widget', 'file_upload_or_choose', ajax=True))
    fm_open = """function(callback, kind){
if (kind == 'elfinder') {%s;} else {%s;}
jQuery.data(document.body, 'elrte_callback', callback)
}""" % (file_chooser.show(), image_chooser.show())

    cssfiles = [URL('static','css/base.css')]
    
    ################################ The core ######################################
    # Inject the elrte widget
    # You can specify the language for the editor, and include your image chooser.
    # In this demo, the image chooser uses the uploadify plugin.
    # If you want to edit contents with css applied, pass the css file urls for an argument.
    db.product.description.widget = ElrteWidget()
    db.product.description.widget.settings.lang = lang
    db.product.description.widget.settings.fm_open = fm_open
    db.product.description.widget.settings.cssfiles = cssfiles
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
    _get_src = lambda r: URL(request.controller, 'download', args=r.image)
    records = DIV([IMG(_src=_get_src(r), 
                       _onclick="""
jQuery.data(document.body, 'elrte_callback')('%s');jQuery('.dialog').hide(); return false;
""" % _get_src(r),
                       _style='max-width:50px;max-height:50px;margin:5px;cursor:pointer;') 
                    for r in records])
    return BEAUTIFY(dict(form=form, info=info, records=records))
    
def file_upload_or_choose():
    form = SQLFORM(file_table, upload=URL('download'))
    info = ''
    if form.accepts(request.vars, session):
        info = 'submitted %s' % form.vars
    
    def _get_icon(v):
        ext = v.split('.')[-1]
        if ext in ('pdf',): filename = 'icon_pdf.gif'
        elif ext in ('doc', 'docx', 'rst'): filename = 'icon_doc.gif'
        elif ext in ('xls', 'xlsx'): filename = 'icon_xls.gif'
        elif ext in ('ppt', 'pptx', 'pps'): filename = 'icon_pps.gif'
        elif ext in ('jpg', 'gif', 'png', 'bmp', 'svg', 'eps'): filename = 'icon_pic.gif'
        elif ext in ('swf', 'fla'): filename = 'icon_flash.gif'
        elif ext in ('mp3', 'wav', 'ogg', 'wma', 'm4a'): filename = 'icon_music.gif'
        elif ext in ('mov', 'wmv', 'mp4', 'api', 'mpg', 'flv'): filename = 'icon_film.gif'
        elif ext in ('zip', 'rar', 'gzip', 'bzip', 'ace', 'gz'): filename = 'icon_archive.gif'
        else: filename = 'icon_txt.gif'
        return IMG(_src=URL('static', 'plugin_elrte_widget/custom/icons/%s' % filename), 
                   _style='cursor:pointer;margin-right:5px;')
    
    records = disk_db(file_table.id>0).select(orderby=~file_table.id, limitby=(0,3))
    records = DIV([DIV(A(_get_icon(r.file), r.name, _href='#', _onclick="""
jQuery.data(document.body, 'elrte_callback')('%s');jQuery('.dialog').hide(); return false;
""" % A(_get_icon(r.file), r.name, _href=URL(request.controller, 'download', args=r.file)).xml()), 
                       _style='margin-bottom:5px;') for r in records])
    
    return BEAUTIFY(dict(form=form, info=info, records=records))
    
def download():
    return response.download(request,disk_db)
