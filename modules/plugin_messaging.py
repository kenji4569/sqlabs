# -*- coding: utf-8 -*-
# This plugins is licensed under the MIT license: http://www.opensource.org/licenses/mit-license.php
# Authors: Kenji Hosoda <hosoda@s-cubism.jp>
from gluon import *
from gluon.storage import Storage

class Messaging(object):
    
    def __init__(self, db):
        self.db = db
        
        settings = self.settings = Storage()
        
        settings.onmessage = None
        
        settings.extra_fields = {}
        
        settings.select_fields = []
        settings.select_attributes = {}
        
        settings.table_message_name = 'message'
        settings.table_message = None
        
        settings.table_thread_name = 'message_thread'
        settings.table_thread = None
        
        settings.status_unread = 'unread'
        settings.status_read = 'read'
        
    def define_tables(self, table_user_name, migrate=True, fake_migrate=False):
        db, settings = self.db, self.settings
        
        if not settings.table_thread_name in db.tables:
            settings.table_thread = db.define_table(
                settings.table_thread_name,
                Field('user', 'reference %s' % table_user_name),
                Field('other', 'reference %s' % table_user_name),
                Field('status', length=16, default=settings.status_read),
                migrate=migrate, fake_migrate=fake_migrate,
                *settings.extra_fields.get(settings.table_thread_name, []))
                
        if not settings.table_message_name in db.tables:
            settings.table_message = db.define_table(
                settings.table_message_name,
                Field('user', 'reference %s' % table_user_name),
                Field('thread', 'reference %s' % settings.table_thread_name),
                Field('body', 'text'),
                Field('forward', 'text'),
                migrate=migrate, fake_migrate=fake_migrate,
                *settings.extra_fields.get(settings.table_message_name, []))
  
    def threads_from_user(self, user_id):
        return self.db(self.settings.table_thread.user==user_id)
        
    def get_thread(self, user_id, other_id, *fields, **attributes):
        return self.threads_from_user(user_id)(self.settings.table_thread.other==other_id
                    ).select(*fields, **attributes).first()
        
    def messages_from_thread(self, thread_id):
        return self.db(self.settings.table_message.thread==thread_id)
        
    def add_message(self, user_id, other_id, body, forward_message_ids=None, **extra):
        db, settings = self.db, self.settings
        if str(user_id) == str(other_id):
            raise ValueError
        
        user_thread = self.get_thread(user_id, other_id)
        if not user_thread:
            user_thread_id = settings.table_thread.insert(user=user_id, other=other_id)
        else:
            user_thread_id = user_thread.id
            
        other_thread = self.get_thread(other_id, user_id)
        if not other_thread:
            other_thread_id = settings.table_thread.insert(user=other_id, other=user_id,
                                                                   status=settings.status_unread)
        else:
            if other_thread.status != settings.status_unread:
                other_thread.update_record(status=settings.status_unread)
            other_thread_id = other_thread.id
        
        forward = None
        if forward_message_ids:
            pass # TODO
        settings.table_message.insert(user=user_id, thread=user_thread_id,
                                      body=body, forward=forward, **extra)
        settings.table_message.insert(user=user_id, thread=other_thread_id,
                                      body=body, forward=forward, **extra)
        
        if settings.onmessage:
            settings.onmessage(user_id, other_id)
           
    def remove_messages(self, user_id, other_id, message_ids=None):
        settings = self.settings
        if not message_ids:
            self.db(settings.table_thread.user==user_id)(settings.table_thread.other==other_id
                    ).delete()
        else:
            thread = self.get_thread(user_id, other_id)
            if not thread:
                raise ValueError
            self.messages_from_thread(thread.id)(settings.table_message.id.belongs(message_ids)
                                      ).delete()