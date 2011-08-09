# -*- coding: utf-8 -*-
import os

def error(): raise HTTP(404)

def to_code(lines):
    return CODE(''.join(lines[1:]).strip(' ').strip('\n'))
    
def get_code(path):
    if not os.path.exists(path):
        error()
    f = open(path, 'r')
    lines = f.readlines()
    f.close()
    return to_code(lines)

def index():
    plugin_name = request.args(0) or error()
    
    # reload the plugin module
    local_import(plugin_name, reload=True)
    
    # load the controll (usage) code
    controller_code = get_code(os.path.join(request.folder, 'controllers', '%s.py' % plugin_name))
    
    # load the module (source) code
    module_code = get_code(os.path.join(request.folder, 'modules', '%s.py' % plugin_name))
    
    info_plugin = info_plugin_metas[plugin_name]
    return dict(
        plugin_name=plugin_name,
        plugin_label=info_plugin['label'],
        plugin_description=info_plugin['description'],
        controller_code=controller_code,
        module_code=module_code,
    )
    
    