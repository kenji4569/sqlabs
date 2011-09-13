# -*- coding: utf-8 -*-
# This plugins is licensed under the MIT license: http://www.opensource.org/licenses/mit-license.php
# Authors: Kenji Hosoda <hosoda@s-cubism.jp>
from gluon import *
from gluon.storage import Storage

class Friendship(object):
    
    def __init__(self, db):
        self.db = db
        
        settings = self.settings = Storage()
        settings.table_friendship_name = 'friendship'
        settings.table_friend_request_name = 'friend_request'
        settings.table_friend_denial_name = 'friend_denial'
        settings.table_friendship = None
        settings.table_friend_request = None
        settings.table_friend_denial = None
        
        settings.onapprove = None
        
    def define_tables(self, table_user, migrate=True, fake_migrate=False):
        db, settings = self.db, self.settings
        
        for name in ('friendship', 'friend_request', 'friend_denial'):
            if not settings['table_%s_name' % name] in db.tables:
                settings['table_%s' % name] = db.define_table(
                    settings['table_%s_name' % name],
                    Field('user', table_user),
                    Field('friend', table_user),
                    migrate=migrate, fake_migrate=fake_migrate)
                
    def request_friend(self, user_id, friend_id):
        db, settings = self.db, self.settings
        if user_id == friend_id:
            raise ValueError
        for name in ('friendship', 'friend_request', 'friend_denial'):
            table = settings['table_%s' % name]
            if db(table.user==user_id)(table.friend==friend_id).count():
                raise ValueError
        
        settings.table_friend_request.insert(user=user_id, friend=friend_id)
        
    def count_friend_requets(self, user_id):
        db, settings = self.db, self.settings
        return db(settings.table_friend_request.friend==user_id).count()
    
    def get_friend_requets(self, user_id, limitby=(0, 5)):
        db, settings = self.db, self.settings
        return [r.user for r in 
                db(settings.table_friend_request.friend==user_id
                   ).select(settings.table_friend_request.user, limitby=limitby)]
            
    def approve_friend(self, user_id, friend_id):
        db, settings = self.db, self.settings
        
        if not db(settings.table_friend_request.friend==user_id)(
                  settings.table_friend_request.user==friend_id).count():
            raise ValueError
            
        db(settings.table_friend_request.friend==user_id)(
           settings.table_friend_request.user==friend_id).delete()
        db(settings.table_friend_request.user==user_id)(
           settings.table_friend_request.friend==friend_id).delete()
           
        settings.table_friendship.insert(user=user_id, friend=friend_id)
        settings.table_friendship.insert(friend=user_id, user=friend_id)
        
        if settings.onapprove:
            settings.onapprove(user_id, friend_id)
        
    def get_friends(self, user_id, limitby=(0, 20)):
        db, settings = self.db, self.settings
        return [r.friend for r in 
                db(settings.table_friendship.user==user_id
                   ).select(settings.table_friendship.friend, limitby=limitby)]
    
    def deny_friend(self, user_id, friend_id):
        db, settings = self.db, self.settings
        
        if not db(settings.table_friend_request.friend==user_id)(
                  settings.table_friend_request.user==friend_id).count():
            raise ValueError
            
        db(settings.table_friend_request.friend==user_id)(
           settings.table_friend_request.user==friend_id).delete()
           
        settings.table_friend_denial.insert(friend=user_id, user=friend_id)
        