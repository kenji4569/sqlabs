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

db = DAL('sqlite:memory:')
auth = Auth(db)
friendship = Friendship(db)

auth.define_tables()
friendship.define_tables(auth.settings.table_user)

user_ids = {}
for i in range(1, 4):
    user_ids[i] = auth.settings.table_user.insert(email='user%s@test.com' % i)

class TestFriendship(unittest.TestCase):

    def setUp(self):
        friendship.settings.table_friendship.truncate()
        friendship.settings.table_friend_request.truncate()
        friendship.settings.table_friend_denial.truncate()

    def test_request_friend(self):
        friendship.request_friend(user_ids[1], user_ids[2])
        self.assertEqual(friendship.count_friend_requets(user_ids[1]), 0)
        self.assertEqual(friendship.count_friend_requets(user_ids[2]), 1)
        self.assertEqual(friendship.get_friend_requets(user_ids[2]), 
                         [user_ids[1]])
                         
    def test_approve_friend(self):
        friendship.request_friend(user_ids[1], user_ids[2])
        friendship.approve_friend(user_ids[2], user_ids[1])
        self.assertEqual(friendship.count_friend_requets(user_ids[1]), 0)
        self.assertEqual(friendship.count_friend_requets(user_ids[2]), 0)
        self.assertEqual(friendship.get_friends(user_ids[1]), 
                         [user_ids[2]])
        self.assertEqual(friendship.get_friends(user_ids[2]), 
                         [user_ids[1]])
                         
    def test_deny_friend(self):
        friendship.request_friend(user_ids[1], user_ids[2])
        friendship.deny_friend(user_ids[2], user_ids[1])
        self.assertEqual(friendship.count_friend_requets(user_ids[1]), 0)
        self.assertEqual(friendship.count_friend_requets(user_ids[2]), 0)
        self.assertEqual(friendship.get_friends(user_ids[1]), [])
        self.assertEqual(friendship.get_friends(user_ids[2]), [])
        self.assertRaises(ValueError, friendship.request_friend, user_ids[1], user_ids[2])
        

def index():
    return dict(output=CODE(run_test(TestFriendship)))
    