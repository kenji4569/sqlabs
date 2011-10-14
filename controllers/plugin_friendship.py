# -*- coding: utf-8 -*-
from plugin_friendship import Friendship
from gluon.tools import Auth
import unittest
import datetime

if request.function == 'test':
    db = DAL('sqlite:memory:')
    
### setup core objects #########################################################
auth = Auth(db)
friendship = Friendship(db)
friendship.settings.table_edge_name = 'plugin_friendship_edge'
friendship.settings.extra_fields = {
    'plugin_friendship_edge': 
        [Field('affinity', 'double', default=1), 
         Field('created_on', 'datetime', default=request.now)],
}

### define tables ##############################################################
auth.define_tables()
table_user = auth.settings.table_user

friendship.define_tables(str(table_user))
table_edge = friendship.settings.table_edge

### populate records ###########################################################
num_users = 5
user_ids = {}
for user_no in range(1, num_users+1):   
    email = 'user%s@test.com' % user_no
    user = db(table_user.email==email).select().first()
    user_ids[user_no] = user and user.id or table_user.insert(email=email)

if db(table_edge.created_on<request.now-datetime.timedelta(minutes=30)).count():
    table_edge.truncate()
    session.flash = 'the database has been refreshed'
    redirect(URL('index'))

### demo functions #############################################################
def index():
    user_no = int(request.args(0) or 1)
    user_id = user_ids[user_no]
    
    for action in ('add_friend', 'confirm_friend', 'ignore_friend', 'remove_friend'):
        if action in request.vars:
            getattr(friendship, action)(user_id, request.vars[action])
            session.flash = action
            redirect(URL('index', args=user_no))
    
    user_chooser = []
    for i in range(1, num_users+1):
        if i == user_no:
            user_chooser.append(SPAN('user%s' % user_no))
        else:
            user_chooser.append(A('user%s' % i, _href=URL('index', args=i)))
    user_chooser = DIV(XML(' '.join([r.xml() for r in user_chooser])), _style='font-weight:bold')
    
    friends = []
    records = db(table_user.id.belongs(set(user_ids.values())-set([user_id]))).select(
                       table_user.ALL, table_edge.ALL, 
                       left=table_edge.on(
                                (table_edge.friend==table_user.id) & 
                                (table_edge.user==user_id)))
                                
    status_options = dict(table_edge.status.requires.options())
    for record in records:
        status = record[table_edge].status
        if status is None:
            option = A(T('Add friend'), 
                       _href=URL('index', args=user_no, vars={'add_friend': record[table_user].id}))
        elif status == friendship.settings.status_requesting:
            option = SPAN(status_options[status], _style='color:blue;')
        else:
            option = SPAN(T('%s mutual friends') % len(record[table_edge].mutual_friends), ' ',
                          A(T('Remove friend'),
                            _href=URL('index', args=user_no, vars={'remove_friend': record[table_user].id})),
                          _style='color:green;')
        friends.append(DIV(record.auth_user.email[:5], ': ', option))
    
    friend_requests = []
    records = friendship.requesting_edges_from_user(user_id).select(
                        table_user.ALL,
                        left=table_user.on(table_user.id==table_edge.user))
    for record in records:
        friend_requests.append(DIV(record.email[:5], ': ',
           A(T('Confirm'), _href=URL('index', args=user_no, vars={'confirm_friend': record.id})), ' ',
           A(T('Not now'), _href=URL('index', args=user_no, vars={'ignore_friend': record.id})),
           _style='color:red;font-size:1.2em;'))
    
    return dict(current_user=user_chooser,
                friends=friends,
                friend_requests=friend_requests,
                unit_tests=[A('basic test', _href=URL('test'))],
                )
    
### unit tests #################################################################
class TestFriendship(unittest.TestCase):

    def setUp(self):
        table_edge.truncate()

    def test_add_friend(self):
        friendship.add_friend(user_ids[1], user_ids[2])
        self.assertEqual(friendship.requesting_edges_from_user(user_ids[1]).count(), 0)
        self.assertEqual(friendship.requesting_edges_from_user(user_ids[2]).count(), 1)
        self.assertEqual([r.user for r in friendship.requesting_edges_from_user(user_ids[2]).select()], 
                         [user_ids[1]])
                         
    def test_confirm_friend(self):
        friendship.add_friend(user_ids[1], user_ids[2])
        friendship.confirm_friend(user_ids[2], user_ids[1])
        self.assertEqual(friendship.requesting_edges_from_user(user_ids[1]).count(), 0)
        self.assertEqual(friendship.requesting_edges_from_user(user_ids[2]).count(), 0)
        
        friends = friendship.friend_edges_from_user(user_ids[1]).select()
        self.assertEqual([r.friend for r in friends], [user_ids[2]])
        self.assertEqual([len(r.mutual_friends) for r in friends], [0])
        
        friends = friendship.friend_edges_from_user(user_ids[2]).select()
        self.assertEqual([r.friend for r in friends], [user_ids[1]])
        self.assertEqual([len(r.mutual_friends) for r in friends], [0])
        
    def test_remove_friend(self):
        friendship.add_friend(user_ids[1], user_ids[2])
        friendship.confirm_friend(user_ids[2], user_ids[1])
        friendship.remove_friend(user_ids[1], user_ids[2])
        
        friends = friendship.friend_edges_from_user(user_ids[1]).select()
        self.assertEqual(len(friends), 0)
        friends = friendship.friend_edges_from_user(user_ids[2]).select()
        self.assertEqual(len(friends), 0)
        
    
    def test_mutual_friends(self):
        friendship.add_friend(user_ids[1], user_ids[2])
        friendship.confirm_friend(user_ids[2], user_ids[1])
        
        friendship.add_friend(user_ids[2], user_ids[3])
        friendship.confirm_friend(user_ids[3], user_ids[2])
        
        friendship.add_friend(user_ids[3], user_ids[1])
        friendship.confirm_friend(user_ids[1], user_ids[3])
        
        for i in range(1, 4):
            self.assertEqual([len(r.mutual_friends) for r in friendship.friend_edges_from_user(user_ids[i]).select()],
                              [1, 1])
        
        friendship.add_friend(user_ids[1], user_ids[4])
        friendship.confirm_friend(user_ids[4], user_ids[1])
        
        friendship.add_friend(user_ids[2], user_ids[4])
        friendship.confirm_friend(user_ids[4], user_ids[2])
        
        self.assertEqual([len(r.mutual_friends) for r in friendship.friend_edges_from_user(user_ids[1]).select()], 
                         [2, 1, 1])
        self.assertEqual([len(r.mutual_friends) for r in friendship.friend_edges_from_user(user_ids[2]).select()], 
                         [2, 1, 1])
        self.assertEqual([len(r.mutual_friends) for r in friendship.friend_edges_from_user(user_ids[4]).select()], 
                         [1, 1])
        self.assertEqual([len(r.mutual_friends) for r in friendship.friend_edges_from_user(user_ids[3]).select()], 
                         [1, 1])
        
        friendship.remove_friend(user_ids[1], user_ids[4])
        friendship.remove_friend(user_ids[2], user_ids[4])
        
        for i in range(1, 4):
            self.assertEqual([len(r.mutual_friends) for r in friendship.friend_edges_from_user(user_ids[i]).select()], 
                             [1, 1])
                        
        friendship.add_friend(user_ids[1], user_ids[4])
        friendship.confirm_friend(user_ids[4], user_ids[1])
        friendship.add_friend(user_ids[2], user_ids[4])
        friendship.confirm_friend(user_ids[4], user_ids[2])
        friendship.add_friend(user_ids[3], user_ids[4])
        friendship.confirm_friend(user_ids[4], user_ids[3])
        
        for i in range(1, 5):
            self.assertEqual([len(r.mutual_friends) for r 
                                in friendship.friend_edges_from_user(user_ids[i]).select()], 
                             [2, 2, 2])
        
        friendship.add_friend(user_ids[1], user_ids[5])
        friendship.confirm_friend(user_ids[5], user_ids[1])
        friendship.add_friend(user_ids[2], user_ids[5])
        friendship.confirm_friend(user_ids[5], user_ids[2])
        friendship.add_friend(user_ids[3], user_ids[5])
        friendship.confirm_friend(user_ids[5], user_ids[3])
        friendship.add_friend(user_ids[4], user_ids[5])
        friendship.confirm_friend(user_ids[5], user_ids[4])
        
        for i in range(1, 6):
            self.assertEqual([len(r.mutual_friends) for r 
                                in friendship.friend_edges_from_user(user_ids[i]).select()], 
                             [3, 3, 3, 3])
        
        friendship.remove_friend(user_ids[1], user_ids[5])
        friendship.remove_friend(user_ids[2], user_ids[5])
        friendship.remove_friend(user_ids[3], user_ids[5])
        friendship.remove_friend(user_ids[4], user_ids[5])
        
        for i in range(1, 5):
            self.assertEqual([len(r.mutual_friends) for r 
                                in friendship.friend_edges_from_user(user_ids[i]).select()], 
                             [2, 2, 2])
        
    def test_ignore_friend(self):
        friendship.add_friend(user_ids[1], user_ids[2])
        friendship.ignore_friend(user_ids[2], user_ids[1])
        self.assertEqual(friendship.requesting_edges_from_user(user_ids[1]).count(), 0)
        self.assertEqual(friendship.requesting_edges_from_user(user_ids[2]).count(), 0)
        self.assertEqual(friendship.friend_edges_from_user(user_ids[1]).count(), 0)
        self.assertEqual(friendship.friend_edges_from_user(user_ids[2]).count(), 0)
        
    def test_extra_fields(self):
        friendship.add_friend(user_ids[1], user_ids[2])
        friendship.confirm_friend(user_ids[2], user_ids[1])
        friend_edge = friendship.get_friend_edge(user_ids[1], user_ids[2])
        self.assertEqual(friend_edge.affinity, 1.0)
        
def run_test(TestCase):
    import cStringIO
    stream = cStringIO.StringIO()
    suite = unittest.TestLoader().loadTestsFromTestCase(TestCase)
    unittest.TextTestRunner(stream=stream, verbosity=2).run(suite)
    return stream.getvalue()
    
def test():
    return dict(back=A('back', _href=URL('index')),
                output=CODE(run_test(TestFriendship)))
    