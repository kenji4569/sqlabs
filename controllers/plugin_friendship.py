# -*- coding: utf-8 -*-
from plugin_friendship import Friendship
from gluon.tools import Auth
import unittest

def run_test(TestCase):
    import cStringIO
    stream = cStringIO.StringIO()
    suite = unittest.TestLoader().loadTestsFromTestCase(TestCase)
    unittest.TextTestRunner(stream=stream, verbosity=2).run(suite)
    return stream.getvalue()

if request.function == 'test':
    db = DAL('sqlite:memory:')
    
auth = Auth(db)
friendship = Friendship(db)
friendship.settings.table_friend_name = 'plugin_friendship_friend'
friendship.settings.extra_fields = {
    'plugin_friendship_friend': 
        [Field('affinity', 'double', default=1), 
         Field('created_on', 'datetime', default=request.now)],
}

auth.define_tables()
friendship.define_tables(auth.settings.table_user_name)

num_users = 4
user_ids = {}
for i in range(1, num_users+1):   
    email = 'user%s@test.com' % i
    user = db(auth.settings.table_user.email==email).select().first()
    user_ids[i] = user and user.id or auth.settings.table_user.insert(email=email)

import datetime
deleted = db(db['plugin_friendship_friend'].created_on<
            request.now-datetime.timedelta(minutes=10)).delete()
if deleted:
    friendship.refresh_all_mutuals()

def index():
    user_no = int(request.args(0) or 1)
    user_id = user_ids[user_no]
    
    for action in ('add_friend', 'confirm_friend', 'ignore_friend', 'remove_friend'):
        if action in request.vars:
            getattr(friendship, action)(user_id, request.vars[action])
            session.flash = 'done: %s' % action
            redirect(URL('index', args=user_no))
            break
    
    user_chooser = []
    for i in range(1, num_users+1):
        if i == user_no:
            user_chooser.append('user%s' % user_no)
        else:
            user_chooser.append(A('user%s' % i, _href=URL('index', args=i)))
        
    table_user = auth.settings.table_user
    table_friend = friendship.settings.table_friend
    
    friends = []
    records = db(table_user.id.belongs(set(user_ids.values())-set([user_id]))).select(
                       table_user.ALL, table_friend.ALL, 
                       left=table_friend.on(
                                (table_friend.friend==table_user.id) & 
                                (table_friend.user==user_id)))
    for record in records:
        status = record[table_friend].status
        if status is None:
            option = A('Add friend', 
                       _href=URL('index', args=user_no, vars={'add_friend': record[table_user].id}))
        elif status == friendship.settings.status_requesting:
            option = 'requesting'
        elif status == friendship.settings.status_denied:
            option = 'denied'
        else:
            option = SPAN('mutual friends -> %s' % record[table_friend].mutual, ' ',
                          A('Remove friend',
                            _href=URL('index', args=user_no, vars={'remove_friend': record[table_user].id})))
        friends.append(DIV(record.auth_user.email[:5], ': ', option))
    
    friend_requests = []
    records = friendship.friend_requets(user_id).select(
                        table_user.ALL,
                        left=table_user.on(table_user.id==table_friend.user))
    for record in records:
        friend_requests.append(DIV(record.email[:5], ': ',
           A('Confirm', _href=URL('index', args=user_no, vars={'confirm_friend': record.id})), ' ',
           A('Not now', _href=URL('index', args=user_no, vars={'ignore_friend': record.id}))))
    
    return dict(choose_user=user_chooser,
                friends=friends,
                friend_requests=friend_requests,
                tests=A('unit test', _href=URL('test')),
                )
    
class TestFriendship(unittest.TestCase):

    def setUp(self):
        friendship.settings.table_friend.truncate()

    def test_add_friend(self):
        friendship.add_friend(user_ids[1], user_ids[2])
        self.assertEqual(friendship.friend_requets(user_ids[1]).count(), 0)
        self.assertEqual(friendship.friend_requets(user_ids[2]).count(), 1)
        self.assertEqual([r.user for r in friendship.friend_requets(user_ids[2]).select()], 
                         [user_ids[1]])
                         
    def test_confirm_friend(self):
        friendship.add_friend(user_ids[1], user_ids[2])
        friendship.confirm_friend(user_ids[2], user_ids[1])
        self.assertEqual(friendship.friend_requets(user_ids[1]).count(), 0)
        self.assertEqual(friendship.friend_requets(user_ids[2]).count(), 0)
        
        friends = friendship.friends(user_ids[1]).select()
        self.assertEqual([r.friend for r in friends], [user_ids[2]])
        self.assertEqual([r.mutual for r in friends], [0])
        
        friends = friendship.friends(user_ids[2]).select()
        self.assertEqual([r.friend for r in friends], [user_ids[1]])
        self.assertEqual([r.mutual for r in friends], [0])
        
    def test_remove_friend(self):
        friendship.add_friend(user_ids[1], user_ids[2])
        friendship.confirm_friend(user_ids[2], user_ids[1])
        friendship.remove_friend(user_ids[1], user_ids[2])
        
        friends = friendship.friends(user_ids[1]).select()
        self.assertEqual(len(friends), 0)
        friends = friendship.friends(user_ids[2]).select()
        self.assertEqual(len(friends), 0)
        
    
    def test_mutual(self):
        friendship.add_friend(user_ids[1], user_ids[2])
        friendship.confirm_friend(user_ids[2], user_ids[1])
        
        friendship.add_friend(user_ids[2], user_ids[3])
        friendship.confirm_friend(user_ids[3], user_ids[2])
        
        friendship.add_friend(user_ids[3], user_ids[1])
        friendship.confirm_friend(user_ids[1], user_ids[3])
        
        for i in range(1, 4):
            self.assertEqual([r.mutual for r in friendship.friends(user_ids[i]).select()], [1, 1])
        
        friendship.add_friend(user_ids[1], user_ids[4])
        friendship.confirm_friend(user_ids[4], user_ids[1])
        
        friendship.add_friend(user_ids[2], user_ids[4])
        friendship.confirm_friend(user_ids[4], user_ids[2])
        
        self.assertEqual([r.mutual for r in friendship.friends(user_ids[1]).select()], [2, 1, 1])
        self.assertEqual([r.mutual for r in friendship.friends(user_ids[2]).select()], [2, 1, 1])
        self.assertEqual([r.mutual for r in friendship.friends(user_ids[4]).select()], [1, 1])
        self.assertEqual([r.mutual for r in friendship.friends(user_ids[3]).select()], [1, 1])
        
        friendship.remove_friend(user_ids[1], user_ids[4])
        friendship.remove_friend(user_ids[2], user_ids[4])
        for i in range(1, 4):
            self.assertEqual([r.mutual for r in friendship.friends(user_ids[i]).select()], [1, 1])
        
    def test_ignore_friend(self):
        friendship.add_friend(user_ids[1], user_ids[2])
        friendship.ignore_friend(user_ids[2], user_ids[1])
        self.assertEqual(friendship.friend_requets(user_ids[1]).count(), 0)
        self.assertEqual(friendship.friend_requets(user_ids[2]).count(), 0)
        self.assertEqual(friendship.friends(user_ids[1]).count(), 0)
        self.assertEqual(friendship.friends(user_ids[2]).count(), 0)
        
    def test_extra_fields(self):
        friendship.add_friend(user_ids[1], user_ids[2])
        friendship.confirm_friend(user_ids[2], user_ids[1])
        friend = friendship.friend(user_ids[1], user_ids[2]).select().first()
        self.assertEqual(friend.affinity, 1.0)
        
def test():
    return dict(back=A('back', _href=URL('index')),
                output=CODE(run_test(TestFriendship)))
    