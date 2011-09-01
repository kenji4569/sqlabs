# -*- coding: utf-8 -*-
from plugin_elrte_widget import ElrteWidget
from plugin_uploadify_widget import (
    uploadify_widget, IS_UPLOADIFY_IMAGE, IS_UPLOADIFY_LENGTH
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
    import uuid
    mmodal_id = str(uuid.uuid4())
    def get_mmodal(content, title='Select', close="close", width=70, height=70):
        # original by web2py's welcome application
        return ("""<div id="%(id)s" class="plugin_mmodal" style="display:none"><div style="position:absolute;top:0%%;left:0%%;width:100%%;height:100%%;background-color:black;z-index:1001;-moz-opacity:0.8;opacity:.80;opacity:0.8;"></div>
                   <div class="dialog" style="position:absolute;top:%(top)s%%;left:%(left)s%%;width:%(width)s%%;height:%(height)s%%;padding:16px;border:2px solid black;background-color:white;opacity:1.0;z-index:1002;overflow:auto;">
                   <span style="font-weight:bold">%(title)s</span><span style="float:right">[<a href="#" onclick="jQuery(\'#%(id)s\').hide();return false;">%(close)s</a>]</span><hr/><div id="c%(id)s">%(content)s</div></div></div>""" % 
                dict(title=title,content=content,close=close,id=mmodal_id,left=(100-width)/2,top=(100-height)/2,width=width,height=height))
    
    fm_open = """function(callback){
var el = jQuery("#%s");
if (el.length == 0) {el = jQuery(%s); jQuery(document.body).append(el);}
var maxZ = Math.max.apply(null,jQuery.map(jQuery('body > *'), function(e,n){
           return parseInt(jQuery('.ui-dialog').css('zIndex'))||1 ;
           }));
el.children('.dialog').css('zIndex', maxZ + 10); 
el.show();
jQuery.data(document.body, 'elrte_callback', callback)
}""" % (mmodal_id, json.dumps(get_mmodal(
            content=LOAD('plugin_elrte_widget', 'upload_or_choose', ajax=True).xml().replace('<!--', '').replace('//-->', ''),
    )))

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
    
def upload_or_choose():
    form = SQLFORM(image_table, upload=URL('download'))
    info = ''
    if form.accepts(request.vars, session):
        info = 'submitted %s' % form.vars
    
    records = disk_db(image_table.id>0).select(orderby=~image_table.id, limitby=(0,3))
    _get_src = lambda r: URL(request.controller, 'download', r.image)
    records = DIV([IMG(_src=_get_src(r), 
                       _onclick="jQuery.data(document.body, 'elrte_callback')('%s');jQuery('.plugin_mmodal').hide();" % _get_src(r),
                       _style='max-width:50px;max-height:50px;margin:5px;cursor:pointer;') 
                    for r in records])
    return BEAUTIFY(dict(form=form, info=info, records=records))
    
def download():
    return response.download(request,disk_db)
