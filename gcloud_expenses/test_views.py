import unittest


class ViewTests(unittest.TestCase):
    def setUp(self):
        from pyramid import testing
        self.config = testing.setUp()

    def tearDown(self):
        from pyramid import testing
        testing.tearDown()

    def test_my_view(self):
        from pyramid import testing
        from .views import my_view
        request = testing.DummyRequest()
        info = my_view(request)
        self.assertEqual(info['project'], 'foo')
