# -*- coding: utf-8 -*-
# This plugins is licensed under the MIT license: http://www.opensource.org/licenses/mit-license.php
# Authors: Kenji Hosoda <hosoda@s-cubism.jp>
from gluon import *
from gluon.storage import Storage

class Friendship(object):
    
    def __init__(self, db):
        self.db = db
        
        settings = self.settings = Storage()
        
        settings.extra_fields = {}
        
        settings.onaccept = None
        
        settings.table_friend_name = 'friend'
        settings.table_friend = None
        
        settings.status_requesting = 'r'
        settings.status_accepted = 'a'
        settings.status_denied = 'd'
        
    def define_tables(self, table_user_name, migrate=True, fake_migrate=False):
        db, settings = self.db, self.settings
        
        if not settings.table_friend_name in db.tables:
            settings.table_friend = db.define_table(
                settings.table_friend_name,
                Field('user', 'reference %s' % table_user_name),
                Field('friend', 'reference %s' % table_user_name),
                Field('status', length=1, default=settings.status_requesting,
                      requires=[settings.status_requesting, settings.status_accepted, settings.status_denied]),
                Field('mutual', 'integer', default=0),
                migrate=migrate, fake_migrate=fake_migrate,
                *settings.extra_fields.get(settings.table_friend_name, []))
 
    def request_friend(self, user_id, friend_id):
        db, settings, table = self.db, self.settings, self.settings.table_friend
        if user_id == friend_id:
            raise ValueError
        
        if db(table.user==user_id)(table.friend==friend_id).count():
            raise ValueError
        
        table.insert(user=user_id, friend=friend_id)
        
    def friend_requets(self, user_id):
        db, settings, table = self.db, self.settings, self.settings.table_friend
        
        return db(table.friend==user_id)(table.status==settings.status_requesting)
    
    def accept_friend(self, user_id, friend_id):
        db, settings, table = self.db, self.settings, self.settings.table_friend
        
        if not db(table.friend==user_id)(table.user==friend_id)(
                  table.status==settings.status_requesting).count():
            raise ValueError
            
        mutual_friends = (set([r.friend for r in self.friends(user_id).select(table.friend)]) &
                          set([r.friend for r in self.friends(friend_id).select(table.friend)]))
        for _user_id in (user_id, friend_id):
            db(table.user==_user_id)(table.status==settings.status_accepted)(
               table.friend.belongs(mutual_friends)).update(mutual=table.mutual+1)
            db(table.friend==_user_id)(table.status==settings.status_accepted)(
               table.user.belongs(mutual_friends)).update(mutual=table.mutual+1)
            
        updator = dict(status=settings.status_accepted, 
                       mutual=len(mutual_friends))
            
        db(table.friend==user_id)(table.user==friend_id).update(**updator)
        
        if db(table.user==user_id)(table.friend==friend_id).count():
            db(table.user==user_id)(table.friend==friend_id).update(**updator)
        else:
            table.insert(user=user_id, friend=friend_id, **updator)
           
        if settings.onaccept:
            settings.onaccept(user_id, friend_id)
        
    def friends(self, user_id):
        db, settings, table = self.db, self.settings, self.settings.table_friend
        return db(table.user==user_id)(table.status==settings.status_accepted)
        
    def friend(self, user_id, friend_id):
        db, settings, table = self.db, self.settings, self.settings.table_friend
        return self.friends(user_id)(table.friend==friend_id)
    
    def deny_friend(self, user_id, friend_id):
        db, settings, table = self.db, self.settings, self.settings.table_friend
        
        if not db(table.friend==user_id)(table.user==friend_id)(
                  table.status==settings.status_requesting).count():
            raise ValueError
            
        db(table.friend==user_id)(table.user==friend_id).update(
            status=settings.status_denied)
            
    def remove_friend(self, user_id, friend_id):
        db, settings, table = self.db, self.settings, self.settings.table_friend
        
        if not db(table.user==user_id)(table.friend==friend_id)(
                  table.status==settings.status_accepted).count():
            raise ValueError
            
        mutual_friends = (set([r.friend for r in self.friends(user_id).select(table.friend)]) &
                          set([r.friend for r in self.friends(friend_id).select(table.friend)]))
        for _user_id in (user_id, friend_id):
            db(table.user==_user_id)(table.status==settings.status_accepted)(
               table.friend.belongs(mutual_friends)).update(mutual=table.mutual-1)
            db(table.friend==_user_id)(table.status==settings.status_accepted)(
               table.user.belongs(mutual_friends)).update(mutual=table.mutual-1)
               
        db(table.user==user_id)(table.friend==friend_id).delete()
        db(table.friend==user_id)(table.user==friend_id).delete()
        