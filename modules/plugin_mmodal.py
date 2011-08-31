# -*- coding: utf-8 -*-
# taken from web2py's welcome application

from gluon import *

class PluginMModal:    
    """

    plugin minimalist modal
    
    This plugin generates a modal window (uses jquery base only)
    In the view create an instance of the plugin
    
        {{a=PluginMModal(title='Hello World',content='give this a try!',close="close",width=70,height=70)}}
    
    Then print the instance in somewhere in the page

        {{=a}}

    To generate a link that opens the model

        {{=a.link('click me to open it')}}

    If the content should be loaded via ajax just pass a callback='http:...' or callback=URL(...) to the plugin constructor

    """
    def __init__(self,title,content,callback=None,close="close",id=None,width=70,height=70):
        import uuid
        self.title=title        
        self.content=content
        self.close=close
        self.callback=callback
        self.id=id or str(uuid.uuid4())
        self.width=width
        self.height=height
    def xml(self):
        return '<div id="%(id)s" class="plugin_mmodal" style="display:none"><div style="position:absolute;top:0%%;left:0%%;width:100%%;height:100%%;background-color:black;z-index:1001;-moz-opacity:0.8;opacity:.80;opacity:0.8;"></div><div style="position:absolute;top:%(top)s%%;left:%(left)s%%;width:%(width)s%%;height:%(height)s%%;padding:16px;border:2px solid black;background-color:white;opacity:1.0;z-index:1002;overflow:auto;"><span style="font-weight:bold">%(title)s</span><span style="float:right">[<a href="#" onclick="jQuery(\'#%(id)s\').hide();return false;">%(close)s</a>]</span><hr/><div id="c%(id)s">%(content)s</div></div></div>' % dict(title=self.title,content=self.content,close=self.close,id=self.id,left=(100-self.width)/2,top=(100-self.height)/2,width=self.width,height=self.height)
    def link(self,message):
        script=''
        if self.callback:
            script="ajax('%s',[],'c%s');" % (self.callback,self.id)
        return A(message,_onclick="jQuery('#%(id)s').fadeIn();%(script)s return false" % dict(id=self.id,script=script))
