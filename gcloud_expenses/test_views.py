import unittest


class ViewTests(unittest.TestCase):
    def setUp(self):
        from pyramid import testing
        self.config = testing.setUp()

    def tearDown(self):
        from pyramid import testing
        testing.tearDown()

    def test_home_page(self):
        from pyramid import testing
        from .views import home_page
        request = testing.DummyRequest()
        info = home_page(request)
        self.assertEqual(info, {})
