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
        
        settings.onconfirm = None
        
        settings.table_friend_name = 'friend'
        settings.table_friend = None
        
        settings.status_requesting = 'requesting'
        settings.status_confirmed = 'confirmed'
        
    def define_tables(self, table_user_name, migrate=True, fake_migrate=False):
        db, settings = self.db, self.settings
        
        if not settings.table_friend_name in db.tables:
            settings.table_friend = db.define_table(
                settings.table_friend_name,
                Field('user', 'reference %s' % table_user_name),
                Field('friend', 'reference %s' % table_user_name),
                Field('status', length=16, default=settings.status_requesting),
                Field('mutual', 'integer', default=0),
                migrate=migrate, fake_migrate=fake_migrate,
                *settings.extra_fields.get(settings.table_friend_name, []))
 
    def add_friend(self, user_id, friend_id, **extra_vars):
        table_friend = self.settings.table_friend
        if user_id == friend_id:
            raise ValueError
        
        if self.db(table_friend.user==user_id)(table_friend.friend==friend_id).count():
            raise ValueError
        
        table_friend.insert(user=user_id, friend=friend_id, **extra_vars)
        
    def friend_requests(self, user_id):
        table_friend = self.settings.table_friend
        return self.db(table_friend.friend==user_id)(table_friend.status==self.settings.status_requesting)
    
    def confirm_friend(self, user_id, friend_id):
        db, settings, table_friend = self.db, self.settings, self.settings.table_friend
        
        if not db(table_friend.friend==user_id)(table_friend.user==friend_id)(
                  table_friend.status==settings.status_requesting).count():
            raise ValueError
            
        mutual_friends = (set([r.friend for r in self.friends_from_user(user_id).select(table_friend.friend)]) &
                          set([r.friend for r in self.friends_from_user(friend_id).select(table_friend.friend)]))
        for _user_id in (user_id, friend_id):
            db(table_friend.user==_user_id)(table_friend.status==settings.status_confirmed)(
               table_friend.friend.belongs(mutual_friends)).update(mutual=table_friend.mutual+1)
            db(table_friend.friend==_user_id)(table_friend.status==settings.status_confirmed)(
               table_friend.user.belongs(mutual_friends)).update(mutual=table_friend.mutual+1)
            
        updator = dict(status=settings.status_confirmed, 
                       mutual=len(mutual_friends))
            
        db(table_friend.friend==user_id)(table_friend.user==friend_id).update(**updator)
        
        if db(table_friend.user==user_id)(table_friend.friend==friend_id).count():
            db(table_friend.user==user_id)(table_friend.friend==friend_id).update(**updator)
        else:
            table_friend.insert(user=user_id, friend=friend_id, **updator)
           
        if settings.onconfirm:
            settings.onconfirm(user_id, friend_id)
        
    def friends_from_user(self, user_id):
        table_friend = self.settings.table_friend
        return self.db(table_friend.user==user_id)(table_friend.status==self.settings.status_confirmed)
        
    def get_friend(self, user_id, friend_id, *fields):
        return self.friends_from_user(user_id)(self.settings.table_friend.friend==friend_id
                                      ).select(*fields).first()
    
    def ignore_friend(self, user_id, friend_id):
        db, table_friend = self.db, self.settings.table_friend
        
        if not db(table_friend.friend==user_id)(table_friend.user==friend_id)(
                  table_friend.status==self.settings.status_requesting).count():
            raise ValueError
            
        db(table_friend.friend==user_id)(table_friend.user==friend_id).delete()
            
    def remove_friend(self, user_id, friend_id):
        db, settings, table_friend = self.db, self.settings, self.settings.table_friend
        
        if not db(table_friend.user==user_id)(table_friend.friend==friend_id)(
                  table_friend.status==settings.status_confirmed).count():
            raise ValueError
            
        mutual_friends = (set([r.friend for r in self.friends_from_user(user_id).select(table_friend.friend)]) &
                          set([r.friend for r in self.friends_from_user(friend_id).select(table_friend.friend)]))
        for _user_id in (user_id, friend_id):
            db(table_friend.user==_user_id)(table_friend.status==settings.status_confirmed)(
               table_friend.friend.belongs(mutual_friends)).update(mutual=table_friend.mutual-1)
            db(table_friend.friend==_user_id)(table_friend.status==settings.status_confirmed)(
               table_friend.user.belongs(mutual_friends)).update(mutual=table_friend.mutual-1)
               
        db(table_friend.user==user_id)(table_friend.friend==friend_id).delete()
        db(table_friend.friend==user_id)(table_friend.user==friend_id).delete()
        
    def refresh_all_mutuals(self):
        # ! Be careful when using the method, as it will require much time.
        db, table_friend = self.db, self.settings.table_friend
        records = db(table_friend.id>0).select()
        for record in records:
            user_id = record.user
            friend_id = record.friend
            mutual_friends = (set([r.friend for r in self.friends_from_user(user_id).select(table_friend.friend)]) &
                          set([r.friend for r in self.friends_from_user(friend_id).select(table_friend.friend)]))
            db(table_friend.user==user_id)(table_friend.friend==friend_id).update(mutual=len(mutual_friends))
        