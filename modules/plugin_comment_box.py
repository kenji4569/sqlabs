# -*- coding: utf-8 -*-
# This plugins is licensed under the MIT license: http://www.opensource.org/licenses/mit-license.php
# Authors: Kenji Hosoda <hosoda@s-cubism.jp>
from gluon import *
from gluon.storage import Storage

class CommentBox(object):
    
    def __init__(self, db):
        self.db = db
        
        settings = self.settings = Storage()
        
        settings.extra_fields = {}
        
        settings.table_comment_name = 'comment'
        settings.table_comment = None
        
    def define_tables(self, table_target_name, table_user_name, 
                      migrate=True, fake_migrate=False):
        db, settings = self.db, self.settings
        
        if not settings.table_comment_name in db.tables:
            settings.table_comment = db.define_table(
                settings.table_comment_name,
                Field('target', 'reference %s' % table_target_name),
                Field('body'),
                Field('created_by', 'reference %s' % table_user_name),
                Field('created_on', 'datetime', default=request.now),
                migrate=migrate, fake_migrate=fake_migrate,
                *settings.extra_fields.get(settings.table_comment_name, []))
            
        
