# -*- coding: utf-8 -*-
# This plugins is licensed under the MIT license: http://www.opensource.org/licenses/mit-license.php
# Authors: Kenji Hosoda <hosoda@s-cubism.jp>
from gluon import *
from gluon.storage import Storage


class Notifier(object):

    def __init__(self, db):
        self.db = db
        
        settings = self.settings = Storage()
        
        settings.extra_fields = {}
        
        settings.table_notification_name = 'notification'
        settings.table_notification = None
        
        settings.keyword = 'notifier'
        
    def define_tables(self, migrate=True, fake_migrate=False):
        db, settings = self.db, self.settings
        
        if not settings.table_notification_name in db.tables:
            db.define_table(
                settings.table_notification_name,
                Field('name', unique=True),
                Field('content', 'text'),
                Field('last_event_time', 'datetime',
                      default=current.request.now, update=current.request.now),
                migrate=migrate, fake_migrate=fake_migrate,
                *settings.extra_fields.get(settings.table_notification_name, []))
        settings.table_notification = db[settings.table_notification_name]
        
    def add_notification(self, name, content):
        db, table_notification = self.db, self.settings.table_notification
        if not db(table_notification.name == name).count():
            table_notification.insert(name=name, content=content)
        else:
            db(table_notification.name == name).update(content=content)
            
    def get_notifications(self):
        db, table_notification = self.db, self.settings.table_notification
        return db(table_notification.id > 0).select(orderby=table_notification.last_event_time)
         
    def process(self):
        request = current.request
        db = self.db
        
        keyword = self.settings.keyword
        if keyword in request.vars:
            db(table_notification.id == request.vars[keyword]).delete()
            redirect(URL(args=request.args))
    
    # TODO
    # http://t.wits.sg/misc/jQueryProgressBar/demo.php
    # http://www.west-wind.com/weblog/posts/2008/Jun/13/A-jQuery-Client-Status-Bar
