# -*- coding: utf-8 -*-

"""
"""

from gluon import *
from gluon.storage import Storage


class PersistentStorage(object):

    def __init__(self, db):
        self.db = db
        settings = self.settings = Storage()

        settings.extra_fields = {}
        
        settings.table_storage_name = 'persistent_storage'
        settings.table_storage = None
        
    def define_tables(self, migrate=True, fake_migrate=False):
        settings = self.settings
        db = self.db
        
        if not settings.table_storage_name in db.tables:
            db.define_table(
                settings.table_storage_name,
                Field('name', unique=True),
                Field('content', 'text'),
                migrate=migrate, fake_migrate=fake_migrate,
                *settings.extra_fields.get(settings.table_storage_name, []))
        settings.table_storage = db[settings.table_storage_name]
    
    def __getitem__(self, name):
        from gluon.contrib import simplejson as json
        from gluon.storage import Storage
        record = self.db(self.settings.table_storage.name == name).select().first()
        return Storage(json.loads(record.content)) if record and record.content else Storage()

    def __setitem__(self, name, content):
        from gluon.contrib import simplejson as json
        if not self.db(self.settings.table_storage.name == name).count():
            self.settings.table_storage.insert(
                name=name, content=json.dumps(content)
            )
        else:
            self.db(self.settings.table_storage.name == name).update(
                content=json.dumps(content)
            )
        
    def __delitem__(self, name):
        self.db(self.settings.table_storage.name == name).delete()
