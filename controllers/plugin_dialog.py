# -*- coding: utf-8 -*-
from plugin_dialog import DIALOG

def index():
    dialog = DIALOG(LOAD(f='inner', ajax=True), title='Test', 
                    close_button='close', renderstyle=True)
    return dict(dialog=A('show dialog', _href='#',
                         _onclick='%s;return false' % dialog.show()))
                         
def inner():
    return DIV('OK!')