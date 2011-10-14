# -*- coding: utf-8 -*-
# This plugins is licensed under the MIT license: http://www.opensource.org/licenses/mit-license.php
# Authors: Kenji Hosoda <hosoda@s-cubism.jp>
from gluon import *
from gluon.storage import Storage, Messages

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
        
        messages = self.messages = Messages(current.T)
        messages.requesting = 'Requesting'
        messages.confirmed = 'Confirmed'
        messages.label_status = 'Status'
        messages.label_mutual_friends = 'Confirmed'
        
        
    def define_tables(self, table_user_name, migrate=True, fake_migrate=False):
        db, settings = self.db, self.settings
        
        if not settings.table_friend_name in db.tables:
            table = db.define_table(
                settings.table_friend_name,
                Field('user', 'reference %s' % table_user_name),
                Field('friend', 'reference %s' % table_user_name),
                Field('status', length=16, default=settings.status_requesting,
                      label=self.messages.label_status),
                Field('mutual_friends', 'list:reference %s' % table_user_name,
                      label=self.messages.label_mutual_friends),
                migrate=migrate, fake_migrate=fake_migrate,
                *settings.extra_fields.get(settings.table_friend_name, []))
            table.status.requires = IS_IN_SET(
                [(settings.status_requesting, self.messages.requesting), 
                 (settings.status_confirmed, self.messages.confirmed)])
        settings.table_friend = db[settings.table_friend_name]
 
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
        user_id, friend_id = int(user_id), int(friend_id)
        db, settings, table_friend = self.db, self.settings, self.settings.table_friend
        
        if not db(table_friend.friend==user_id)(table_friend.user==friend_id)(
                  table_friend.status==settings.status_requesting).count():
            raise ValueError
            
        mutual_friends = (set([r.friend for r in self.friends_from_user(user_id).select(table_friend.friend)]) &
                          set([r.friend for r in self.friends_from_user(friend_id).select(table_friend.friend)]))

        for _user_id, _friend_id in ((user_id, friend_id), (friend_id, user_id)):
            for mutual_friend in mutual_friends:
                record = self.friends_from_user(_user_id)(
                            table_friend.friend == mutual_friend
                            ).select(table_friend.id, table_friend.mutual_friends).first()
                record.mutual_friends.append(_friend_id)
                record.update_record(mutual_friends=record.mutual_friends)
                
                self.friends_from_friend(_user_id)(
                    table_friend.user == mutual_friend
                    ).update(mutual_friends=record.mutual_friends)
            
        updator = dict(status=settings.status_confirmed, 
                       mutual_friends=list(mutual_friends))
        db(table_friend.friend==user_id)(table_friend.user==friend_id).update(**updator)
        
        if db(table_friend.user==user_id)(table_friend.friend==friend_id).count():
            db(table_friend.user==user_id)(table_friend.friend==friend_id).update(**updator)
        else:
            table_friend.insert(user=user_id, friend=friend_id, **updator)
           
        if settings.onconfirm:
            settings.onconfirm(user_id, friend_id)
        
    def friends_from_user(self, user_id):
        table_friend = self.settings.table_friend
        return self.db(table_friend.user==user_id)(
                       table_friend.status==self.settings.status_confirmed)
    
    def friends_from_friend(self, friend_id):
        table_friend = self.settings.table_friend
        return self.db(table_friend.friend==friend_id)(
                       table_friend.status==self.settings.status_confirmed)
      
    def get_friend(self, user_id, friend_id, *fields, **attributes):
        return self.friends_from_user(user_id)(self.settings.table_friend.friend==friend_id
                                      ).select(*fields, **attributes).first()
    
    def ignore_friend(self, user_id, friend_id):
        db, table_friend = self.db, self.settings.table_friend
        
        if not db(table_friend.friend==user_id)(table_friend.user==friend_id)(
                  table_friend.status==self.settings.status_requesting).count():
            raise ValueError
            
        db(table_friend.friend==user_id)(table_friend.user==friend_id).delete()
            
    def remove_friend(self, user_id, friend_id):
        user_id, friend_id = int(user_id), int(friend_id)
        db, settings, table_friend = self.db, self.settings, self.settings.table_friend
        
        if not db(table_friend.user==user_id)(table_friend.friend==friend_id)(
                  table_friend.status==settings.status_confirmed).count():
            raise ValueError
            
        mutual_friends = (set([r.friend for r in self.friends_from_user(user_id).select(table_friend.friend)]) &
                          set([r.friend for r in self.friends_from_user(friend_id).select(table_friend.friend)]))
        
        for _user_id, _friend_id in ((user_id, friend_id), (friend_id, user_id)):
            for mutual_friend in mutual_friends:
                record = self.friends_from_user(_user_id)(
                            table_friend.friend==mutual_friend
                            ).select(table_friend.id, table_friend.mutual_friends).first()
                record.mutual_friends.remove(_friend_id)
                record.update_record(mutual_friends=record.mutual_friends)
                
                self.friends_from_friend(_user_id)(
                    table_friend.user==mutual_friend
                    ).update(mutual_friends=record.mutual_friends)
               
        db(table_friend.user==user_id)(table_friend.friend==friend_id).delete()
        db(table_friend.friend==user_id)(table_friend.user==friend_id).delete()
        
    def refresh_all_mutual_friends(self):
        # ! Be careful when using the method, as it will require much time.
        db, table_friend = self.db, self.settings.table_friend
        records = db(table_friend.id>0).select()
        for record in records:
            user_id = record.user
            friend_id = record.friend
            mutual_friends = list(set([r.friend for r in self.friends_from_user(user_id).select(table_friend.friend)]) &
                                  set([r.friend for r in self.friends_from_user(friend_id).select(table_friend.friend)]))
            db(table_friend.user==user_id)(table_friend.friend==friend_id
               ).update(mutual_friends=mutual_friends)
        