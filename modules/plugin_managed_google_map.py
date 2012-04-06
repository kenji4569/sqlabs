# -*- coding: utf-8 -*-
# This plugins is licensed under the MIT license: http://www.opensource.org/licenses/mit-license.php
# Authors: Yusuke Kishita <yuusuuke.kishiita@gmail.com>, Kenji Hosoda <hosoda@s-cubism.jp>
from gluon import *

# For referencing static and views from other application
import os
APP = os.path.basename(os.path.dirname(os.path.dirname(__file__)))

def managed_google_map(managed_html):
    
    _urls = [URL(APP, 'static', 'plugin_managed_google_map/handlebars-1.0.0.beta.6.js')]
    for _url in _urls:
        if _url not in current.response.files:
            current.response.files.append(_url)

    context = dict(managed_html=managed_html)
    current.response.render('plugin_managed_google_map/block.html', context)
    return current.response._view_environment['MANAGED_GOOGLE_MAP']
