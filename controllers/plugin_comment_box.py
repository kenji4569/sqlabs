# -*- coding: utf-8 -*-
from plugin_comment_list import CommentBox()
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
comment_box = CommentBox(db)
comment_box.settings.table_comment_name = 'plugin_comment_box_comment'

def index():
    pass
    
def test():
    pass


