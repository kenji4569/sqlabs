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
         Field('created_at', 'datetime', default=request.now)],
}

auth.define_tables()
friendship.define_tables(auth.settings.table_user_name)

num_users = 4
user_ids = {}
for i in range(1, num_users+1):   
    email = 'user%s@test.com' % i
    user = db(auth.settings.table_user.email==email).select().first()
    if not user:
        user_ids[i] = auth.settings.table_user.insert(email=email)
    else:
        user_ids[i] = user.id

import datetime
db(db['plugin_friendship_friend'].created_at<
    request.now-datetime.timedelta(minutes=10)).delete()

def index():
    user_no = int(request.args(0) or 1)
    user_id = user_ids[user_no]
    
    if 'request_friend' in request.vars:
        friendship.request_friend(user_id, request.vars.request_friend)
        session.flash = 'requesting friend'
        redirect(URL('index', args=user_no))
    
    user_chooser = []
    for i in range(1, num_users+1):
        if i == user_no:
            user_chooser.append('user%s' % user_no)
        else:
            user_chooser.append(A('user%s' % i, _href=URL('index', args=i)))
        user_chooser.append(SPAN(' '))
        
    # friendship.request_friend(user_ids[1], user_ids[2])
    # friendship.accept_friend(user_ids[2], user_ids[1])
    
    table_user = auth.settings.table_user
    table_friend = friendship.settings.table_friend
    table_friend_status = friendship.settings.table_friend_status
    
    users = db(table_user.id.belongs(set(user_ids.values())-set([user_id]))).select(
               table_user.ALL, table_friend_status.status,
               left=table_friend_status.on(
                        (table_friend_status.friend==table_user.id) & 
                        (table_friend_status.user==user_id))
               )
               
    friends = []
    for user in users:
        status = user[friendship.settings.table_friend_status_name].status
        if status == friendship.settings.status_requesting:
            option = 'requesting'
        elif status is None:
            option = 'add friend'
        else:
            option = ''
        friends.append(DIV(user.auth_user.email[:5], option))
    
    # friends = friendship.friends(user_id).select(
                    # table_user.ALL, left=table_user.on(table_user.id==table_friend.friend))
    
    return dict(choose_user=DIV(*user_chooser),
                friends=friends,
                # request_friends=[
                    # A('user%s' % no, _href=URL('index', args=user_no, vars={'request_friend': user_ids[no]})) 
                                # for no in not_yet_friend_nos],
                # users=users,
                )
    
class TestFriendship(unittest.TestCase):

    def setUp(self):
        friendship.settings.table_friend.truncate()

    def test_request_friend(self):
        friendship.request_friend(user_ids[1], user_ids[2])
        self.assertEqual(friendship.friend_requets(user_ids[1]).count(), 0)
        self.assertEqual(friendship.friend_requets(user_ids[2]).count(), 1)
        self.assertEqual([r.user for r in friendship.friend_requets(user_ids[2]).select()], 
                         [user_ids[1]])
                         
    def test_accept_friend(self):
        friendship.request_friend(user_ids[1], user_ids[2])
        friendship.accept_friend(user_ids[2], user_ids[1])
        self.assertEqual(friendship.friend_requets(user_ids[1]).count(), 0)
        self.assertEqual(friendship.friend_requets(user_ids[2]).count(), 0)
        
        friends = friendship.friends(user_ids[1]).select()
        self.assertEqual([r.friend for r in friends], [user_ids[2]])
        self.assertEqual([r.mutual for r in friends], [0])
        
        friends = friendship.friends(user_ids[2]).select()
        self.assertEqual([r.friend for r in friends], [user_ids[1]])
        self.assertEqual([r.mutual for r in friends], [0])
        
    def test_remove_friend(self):
        friendship.request_friend(user_ids[1], user_ids[2])
        friendship.accept_friend(user_ids[2], user_ids[1])
        friendship.remove_friend(user_ids[1], user_ids[2])
        
        friends = friendship.friends(user_ids[1]).select()
        self.assertEqual(len(friends), 0)
        friends = friendship.friends(user_ids[2]).select()
        self.assertEqual(len(friends), 0)
        
    
    def test_mutual(self):
        friendship.request_friend(user_ids[1], user_ids[2])
        friendship.accept_friend(user_ids[2], user_ids[1])
        
        friendship.request_friend(user_ids[2], user_ids[3])
        friendship.accept_friend(user_ids[3], user_ids[2])
        
        friendship.request_friend(user_ids[3], user_ids[1])
        friendship.accept_friend(user_ids[1], user_ids[3])
        
        for i in range(1, 4):
            self.assertEqual([r.mutual for r in friendship.friends(user_ids[i]).select()], [1, 1])
        
        friendship.request_friend(user_ids[1], user_ids[4])
        friendship.accept_friend(user_ids[4], user_ids[1])
        
        friendship.request_friend(user_ids[2], user_ids[4])
        friendship.accept_friend(user_ids[4], user_ids[2])
        
        self.assertEqual([r.mutual for r in friendship.friends(user_ids[1]).select()], [2, 1, 1])
        self.assertEqual([r.mutual for r in friendship.friends(user_ids[2]).select()], [2, 1, 1])
        self.assertEqual([r.mutual for r in friendship.friends(user_ids[4]).select()], [1, 1])
        self.assertEqual([r.mutual for r in friendship.friends(user_ids[3]).select()], [1, 1])
        
        friendship.remove_friend(user_ids[1], user_ids[4])
        friendship.remove_friend(user_ids[2], user_ids[4])
        for i in range(1, 4):
            self.assertEqual([r.mutual for r in friendship.friends(user_ids[i]).select()], [1, 1])
        
    def test_deny_friend(self):
        friendship.request_friend(user_ids[1], user_ids[2])
        friendship.deny_friend(user_ids[2], user_ids[1])
        self.assertEqual(friendship.friend_requets(user_ids[1]).count(), 0)
        self.assertEqual(friendship.friend_requets(user_ids[2]).count(), 0)
        self.assertEqual(friendship.friends(user_ids[1]).count(), 0)
        self.assertEqual(friendship.friends(user_ids[2]).count(), 0)
        self.assertRaises(ValueError, friendship.request_friend, user_ids[1], user_ids[2])
        
    def test_extra_fields(self):
        friendship.request_friend(user_ids[1], user_ids[2])
        friendship.accept_friend(user_ids[2], user_ids[1])
        friend = friendship.friend(user_ids[1], user_ids[2]).select().first()
        self.assertEqual(friend.affinity, 1.0)
        
def test():
    return dict(output=CODE(run_test(TestFriendship)))
    