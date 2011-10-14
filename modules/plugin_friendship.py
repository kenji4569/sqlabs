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
        
        settings.table_edge_name = 'friendship_edge'
        settings.table_edge = None
        
        settings.status_requesting = 'requesting'
        settings.status_confirmed = 'confirmed'
        
        messages = self.messages = Messages(current.T)
        messages.requesting = 'Requesting'
        messages.confirmed = 'Confirmed'
        messages.label_status = 'Status'
        messages.label_mutual_friends = 'Confirmed'
        
    def define_tables(self, table_user_name, migrate=True, fake_migrate=False):
        db, settings = self.db, self.settings
        
        if not settings.table_edge_name in db.tables:
            table = db.define_table(
                settings.table_edge_name,
                Field('user', 'reference %s' % table_user_name),
                Field('friend', 'reference %s' % table_user_name),
                Field('status', length=16, default=settings.status_requesting,
                      label=self.messages.label_status),
                Field('mutual_friends', 'list:reference %s' % table_user_name,
                      label=self.messages.label_mutual_friends),
                migrate=migrate, fake_migrate=fake_migrate,
                *settings.extra_fields.get(settings.table_edge_name, []))
            table.status.requires = IS_IN_SET(
                [(settings.status_requesting, self.messages.requesting), 
                 (settings.status_confirmed, self.messages.confirmed)])
        settings.table_edge = db[settings.table_edge_name]
 
    def add_friend(self, user_id, friend_id, **extra_vars):
        table_edge = self.settings.table_edge
        if user_id == friend_id:
            raise ValueError
        
        if self.db(table_edge.user==user_id)(table_edge.friend==friend_id).count():
            raise ValueError
        
        table_edge.insert(user=user_id, friend=friend_id, **extra_vars)
        
    def confirm_friend(self, user_id, friend_id):
        user_id, friend_id = int(user_id), int(friend_id)
        db, settings, table_edge = self.db, self.settings, self.settings.table_edge
        
        if not db(table_edge.friend==user_id)(table_edge.user==friend_id)(
                  table_edge.status==settings.status_requesting).count():
            raise ValueError
            
        mutual_friends = (set([r.friend for r in self.friend_edges_from_user(user_id).select(table_edge.friend)]) &
                          set([r.friend for r in self.friend_edges_from_user(friend_id).select(table_edge.friend)]))

        for _user_id, _friend_id in ((user_id, friend_id), (friend_id, user_id)):
            for mutual_friend in mutual_friends:
                edge = self.friend_edges_from_user(_user_id)(
                            table_edge.friend == mutual_friend
                            ).select(table_edge.id, table_edge.mutual_friends).first()
                edge.mutual_friends.append(_friend_id)
                edge.update_record(mutual_friends=edge.mutual_friends)
                
                self.friend_edges_from_friend(_user_id)(
                    table_edge.user == mutual_friend
                    ).update(mutual_friends=edge.mutual_friends)
            
        updator = dict(status=settings.status_confirmed, 
                       mutual_friends=list(mutual_friends))
        db(table_edge.friend==user_id)(table_edge.user==friend_id).update(**updator)
        
        if db(table_edge.user==user_id)(table_edge.friend==friend_id).count():
            db(table_edge.user==user_id)(table_edge.friend==friend_id).update(**updator)
        else:
            table_edge.insert(user=user_id, friend=friend_id, **updator)
           
        if settings.onconfirm:
            settings.onconfirm(user_id, friend_id)
        
    def requesting_edges_from_user(self, user_id):
        table_edge = self.settings.table_edge
        return self.db(table_edge.friend==user_id)(table_edge.status==self.settings.status_requesting)
    
    def friend_edges_from_user(self, user_id):
        table_edge = self.settings.table_edge
        return self.db(table_edge.user==user_id)(
                       table_edge.status==self.settings.status_confirmed)
    
    def friend_edges_from_friend(self, friend_id):
        table_edge = self.settings.table_edge
        return self.db(table_edge.friend==friend_id)(
                       table_edge.status==self.settings.status_confirmed)
      
    def get_friend_edge(self, user_id, friend_id, *fields, **attributes):
        return self.friend_edges_from_user(user_id)(self.settings.table_edge.friend==friend_id
                                      ).select(*fields, **attributes).first()
    
    def ignore_friend(self, user_id, friend_id):
        db, table_edge = self.db, self.settings.table_edge
        
        if not db(table_edge.friend==user_id)(table_edge.user==friend_id)(
                  table_edge.status==self.settings.status_requesting).count():
            raise ValueError
            
        db(table_edge.friend==user_id)(table_edge.user==friend_id).delete()
            
    def remove_friend(self, user_id, friend_id):
        user_id, friend_id = int(user_id), int(friend_id)
        db, settings, table_edge = self.db, self.settings, self.settings.table_edge
        
        if not db(table_edge.user==user_id)(table_edge.friend==friend_id)(
                  table_edge.status==settings.status_confirmed).count():
            raise ValueError
            
        mutual_friends = (set([r.friend for r in self.friend_edges_from_user(user_id).select(table_edge.friend)]) &
                          set([r.friend for r in self.friend_edges_from_user(friend_id).select(table_edge.friend)]))
        
        for _user_id, _friend_id in ((user_id, friend_id), (friend_id, user_id)):
            for mutual_friend in mutual_friends:
                edge = self.friend_edges_from_user(_user_id)(
                            table_edge.friend==mutual_friend
                            ).select(table_edge.id, table_edge.mutual_friends).first()
                edge.mutual_friends.remove(_friend_id)
                edge.update_record(mutual_friends=edge.mutual_friends)
                
                self.friend_edges_from_friend(_user_id)(
                    table_edge.user==mutual_friend
                    ).update(mutual_friends=edge.mutual_friends)
               
        db(table_edge.user==user_id)(table_edge.friend==friend_id).delete()
        db(table_edge.friend==user_id)(table_edge.user==friend_id).delete()
        
    def refresh_all_mutual_friends(self):
        # ! Be careful when using the method. It will require much time.
        db, table_edge = self.db, self.settings.table_edge
        edges = db(table_edge.id>0).select()
        for edge in edges:
            user_id = edge.user
            friend_id = edge.friend
            mutual_friends = list(set([r.friend for r in self.friend_edges_from_user(user_id).select(table_edge.friend)]) &
                                  set([r.friend for r in self.friend_edges_from_user(friend_id).select(table_edge.friend)]))
            db(table_edge.user==user_id)(table_edge.friend==friend_id
               ).update(mutual_friends=mutual_friends)
        