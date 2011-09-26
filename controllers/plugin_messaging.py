# -*- coding: utf-8 -*-
from plugin_messaging import Messaging
from gluon.tools import Auth
import unittest

if request.function == 'test':
    db = DAL('sqlite:memory:')

### setup core objects #########################################################    
auth = Auth(db)
messaging = Messaging(db)
messaging.settings.table_message_thread_name = 'plugin_messaging_message_thread'
messaging.settings.table_message_name = 'plugin_messaging_message'
messaging.settings.extra_fields = {
    'plugin_messaging_message_thread': 
        [Field('created_on', 'datetime', default=request.now)],
}

### define tables ##############################################################
auth.define_tables()
table_user = auth.settings.table_user

messaging.define_tables(auth.settings.table_user_name)
table_message_thread = messaging.settings.table_message_thread
table_message = messaging.settings.table_message

### populate records ###########################################################
num_users = 3
user_ids = {}
for i in range(1, num_users+1):   
    email = 'user%s@test.com' % i
    user = db(auth.settings.table_user.email==email).select().first()
    user_ids[i] = user and user.id or auth.settings.table_user.insert(email=email)
    
import datetime
deleted = db(db['plugin_messaging_message_thread'].created_on<
            request.now-datetime.timedelta(minutes=30)).delete()
if deleted:
    session.flash = 'the database has been refreshed'
    redirect(URL('index'))
    
### demo functions #############################################################
def index():
    user_no = int(request.args(0) or 1)
    user_id = user_ids[user_no]
    
    user_chooser = []
    for i in range(1, num_users+1):
        if i == user_no:
            user_chooser.append(SPAN('user%s' % user_no))
        else:
            user_chooser.append(A('user%s' % i, _href=URL('index', args=i)))
    user_chooser = DIV(XML(' '.join([r.xml() for r in user_chooser])), _style='font-weight:bold')
    
    if not request.args(1):
        records = messaging.message_threads(user_id).select(
                    table_user.ALL, table_message_thread.ALL,
                    left=(table_user.on(table_user.id==table_message_thread.other)))
        message_threads = []
        for record in records:
            el = A(record[table_user].email[:5], 
                                     _href=URL('index', args=[user_no, record[table_user].email[4]]))
            if record[table_message_thread].status == messaging.settings.status_unread:
                el =  SPAN(el, ' unread', _style='background:silver')
            
            message_threads.append(el)
            
        others = [(i, 'user%s' % i) for i in range(1, num_users+1) if i != user_no]
        form = SQLFORM.factory(Field('other', label='To', requires=IS_IN_SET(others)),
                               Field('body'))
        if form.accepts(request.vars, session):
            messaging.add_message(user_id, user_ids[int(form.vars.other)], form.vars.body)
            redirect(URL('index', args=[user_no, form.vars.other]))
        
        return dict(current_user=user_chooser,
                    message=form,
                    message_threads=message_threads,
                    tests=[A('unit test', _href=URL('test'))],
                    )
    else:
        other_no = request.args(1)
        other_id = user_ids[int(other_no)]
        message_thread = messaging.message_thread(user_id, other_id).select().first()
        if message_thread.status == messaging.settings.status_unread:
            message_thread.update_record(status=messaging.settings.status_read)
        
        records = messaging.messages(message_thread.id).select(
                    table_user.ALL, table_message.ALL,
                    orderby=~table_message.id,
                    left=(table_user.on(table_user.id==table_message.user)))
        messages = []
        for record in reversed(records):
            messages.append(LI(EM(record[table_user].email[:5], _href='#'), ' ', SPAN(record[table_message].body)))
        messages = UL(*messages)
        
        form = SQLFORM.factory(Field('body'))
        if form.accepts(request.vars, session):
            messaging.add_message(user_id, other_id, form.vars.body)
            redirect(URL('index', args=request.args))
        
        return dict(back=A('back', _href=URL('index', args=user_no)),
                    current__user=user_chooser,
                    message_to='user%s' % other_no,
                    messages=messages,
                    reply=form,
                    tests=[A('unit test', _href=URL('test'))],
                    )
      
### unit tests #################################################################
class TestMessaging(unittest.TestCase):

    def setUp(self):
        messaging.settings.table_message_thread.truncate()
        messaging.settings.table_message.truncate()
        
    def test_add_message(self):
        user_id = 1
        other_id = 2
        
        self.assertEqual(messaging.message_threads(user_id).count(), 0)
        
        body = 'test'
        messaging.add_message(user_id, other_id, body)
        
        user_thread = messaging.message_thread(user_id, other_id).select().first()
        self.assertEqual(user_thread.status, messaging.settings.status_read)
                         
        message = messaging.messages(user_thread.id).select().first()
        self.assertEqual(message.user, user_id)
        self.assertEqual(message.body, body)
        
        other_thread = messaging.message_thread(other_id, user_id).select().first()
        self.assertEqual(other_thread.status, messaging.settings.status_unread)
        
        message = messaging.messages(other_thread.id).select().first()
        self.assertEqual(message.user, user_id)
        self.assertEqual(message.body, body)
        
        body = 'test2'
        messaging.add_message(user_id, other_id, body)
        self.assertEqual(messaging.messages(user_thread.id).count(), 2)
        self.assertEqual(messaging.messages(other_thread.id).count(), 2)
        
    def test_delete(self):
        user_id = 1
        other_id = 2
        for i in range(3):
            messaging.add_message(user_id, other_id, 'test')
        messaging.delete_messages(user_id, other_id)
        self.assertEqual(messaging.message_threads(user_id).count(), 0)
        
        for i in range(3):
            messaging.add_message(user_id, other_id, 'test')
        user_thread = messaging.message_thread(user_id, other_id).select().first()
        message_ids = [r.id for r in messaging.messages(user_thread.id).select()]
        messaging.delete_messages(user_id, other_id, message_ids[1:])
        self.assertEqual(messaging.messages(user_thread.id).count(), 1)
        
def test():
    def run_test(TestCase):
        import cStringIO
        stream = cStringIO.StringIO()
        suite = unittest.TestLoader().loadTestsFromTestCase(TestCase)
        unittest.TextTestRunner(stream=stream, verbosity=2).run(suite)
        return stream.getvalue()
    return dict(back=A('back', _href=URL('index')),
                output=CODE(run_test(TestMessaging)))