# -*- coding: utf-8 -*-
# This plugins is licensed under the MIT license: http://www.opensource.org/licenses/mit-license.php
# Authors: Kenji Hosoda <hosoda@s-cubism.jp>
from gluon import *
from gluon.storage import Storage, Messages


class Messaging(object):
    
    def __init__(self, db):
        self.db = db
        
        settings = self.settings = Storage()
        
        settings.onmessage = None
        
        settings.extra_fields = {}
        
        settings.select_fields = []
        settings.select_attributes = {}
        
        settings.table_message_name = 'messaging_message'
        settings.table_message = None
        
        settings.table_thread_name = 'messaging_thread'
        settings.table_thread = None
        
        settings.status_read = 'read'
        settings.status_unread = 'unread'
        
        messages = self.messages = Messages(current.T)
        messages.read = 'Already read'
        messages.unread = 'Unread'
        
        messages.label_status = 'Status'
        messages.label_body_text = 'Body text'
        messages.label_receiver = 'Receiver'
        
    def define_tables(self, table_user_name, migrate=True, fake_migrate=False):
        db, settings = self.db, self.settings
        
        if not settings.table_thread_name in db.tables:
            table = db.define_table(
                settings.table_thread_name,
                Field('user', 'reference %s' % table_user_name),
                Field('receiver', 'reference %s' % table_user_name,
                      label=self.messages.label_receiver),
                Field('status', length=16, default=settings.status_read,
                      label=self.messages.label_status),
                migrate=migrate, fake_migrate=fake_migrate,
                *settings.extra_fields.get(settings.table_thread_name, []))
            table.status.requires = IS_IN_SET(
                [(settings.status_read, self.messages.read),
                 (settings.status_unread, self.messages.unread)])
        settings.table_thread = db[settings.table_thread_name]
        
        if not settings.table_message_name in db.tables:
            settings.table_message = db.define_table(
                settings.table_message_name,
                Field('user', 'reference %s' % table_user_name),
                Field('thread', 'reference %s' % settings.table_thread_name),
                Field('body_text', 'text',
                      label=self.messages.label_body_text),
                Field('forward', 'text'),  # TODO
                migrate=migrate, fake_migrate=fake_migrate,
                *settings.extra_fields.get(settings.table_message_name, []))
        settings.table_message = db[settings.table_message_name]
        
    def threads_from_user(self, user_id):
        return self.db(self.settings.table_thread.user == user_id)
        
    def get_thread(self, user_id, receiver_id, *fields, **attributes):
        return self.threads_from_user(user_id)(self.settings.table_thread.receiver == receiver_id
                    ).select(*fields, **attributes).first()
        
    def messages_from_thread(self, thread_id):
        return self.db(self.settings.table_message.thread == thread_id)
        
    def add_message(self, user_id, receiver_id, body_text, forward_message_ids=None, **extra):
        db, settings = self.db, self.settings
        if str(user_id) == str(receiver_id):
            raise ValueError
        
        user_thread = self.get_thread(user_id, receiver_id)
        if not user_thread:
            user_thread_id = settings.table_thread.insert(user=user_id, receiver=receiver_id)
        else:
            user_thread_id = user_thread.id
            
        receiver_thread = self.get_thread(receiver_id, user_id)
        if not receiver_thread:
            receiver_thread_id = settings.table_thread.insert(user=receiver_id, receiver=user_id,
                                                                   status=settings.status_unread)
        else:
            if receiver_thread.status != settings.status_unread:
                receiver_thread.update_record(status=settings.status_unread)
            receiver_thread_id = receiver_thread.id
        
        forward = None
        if forward_message_ids:
            pass  # TODO
        settings.table_message.insert(user=user_id, thread=user_thread_id,
                                      body_text=body_text, forward=forward, **extra)
        settings.table_message.insert(user=user_id, thread=receiver_thread_id,
                                      body_text=body_text, forward=forward, **extra)
        
        if settings.onmessage:
            settings.onmessage(user_id, receiver_id)
           
    def remove_messages(self, user_id, receiver_id, message_ids=None):
        settings = self.settings
        if not message_ids:
            self.db(settings.table_thread.user == user_id)(settings.table_thread.receiver == receiver_id
                    ).delete()
        else:
            thread = self.get_thread(user_id, receiver_id)
            if not thread:
                raise ValueError
            self.messages_from_thread(thread.id)(settings.table_message.id.belongs(message_ids)
                                      ).delete()
