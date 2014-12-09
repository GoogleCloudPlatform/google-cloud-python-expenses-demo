import unittest

class ResourcePoolTests(unittest.TestCase):

    def _getTargetClass(self):
        from .pool import ResourcePool
        return ResourcePool

    def _makeOne(self, *args, **kw):
        return self._getTargetClass()(*args, **kw)

    def test_ctor_defaults(self):
        from threading import RLock
        from .pool import logger
        pool = self._makeOne()
        self.assertTrue(isinstance(pool._lock, type(RLock())))
        self.assertTrue(pool._logger is logger)
        self.assertEqual(pool.size, 4)
        self.assertEqual(pool.timeout, 1<<31)
        self.assertEqual(len(pool.available), 0)
        self.assertEqual(len(list(pool)), 0)

    def test_ctor_explicit(self):
        _logger = object()
        pool = self._makeOne(size=5, timeout=30, logger=_logger)
        self.assertTrue(pool._logger is _logger)
        self.assertEqual(pool.size, 5)
        self.assertEqual(pool.timeout, 30)

    def test_size_setter_reducing(self):
        pool = self._makeOne()
        resources = []
        for i in range(4):
            resource = _Resource()
            resources.append(resource)
            pool.add(resource)
        pool.size = 2
        self.assertEqual(pool.size, 2)
        available = pool.available
        self.assertEqual(len(available), 2)
        self.assertFalse(resources[0] in available)
        self.assertFalse(resources[1] in available)
        self.assertTrue(resources[2] in available)
        self.assertTrue(resources[3] in available)

    def test_timeout_setter_reducing(self):
        import time
        pool = self._makeOne()
        resources = []
        for i in range(4):
            resource = _Resource()
            resources.append(resource)
            pool.add(resource)
        time.sleep(.2)  # allow expiration when timeout is set.
        pool.timeout = .1
        self.assertEqual(pool.timeout, .1)
        available = pool.available
        self.assertEqual(len(available), 0)

    def test_add_already_in_pool(self):
        pool = self._makeOne()
        resource = _Resource()
        pool.add(resource)
        self.assertRaises(ValueError, pool.add, resource)

    def test_add_w_checked_out(self):
        pool = self._makeOne()
        resource = _Resource()
        pool.add(resource, checked_out=True)
        self.assertTrue(resource in list(pool))
        self.assertFalse(resource in pool.available)

    def test_add_wo_checked_out(self):
        pool = self._makeOne()
        resource = _Resource()
        pool.add(resource)
        self.assertTrue(resource in list(pool))
        self.assertTrue(resource in pool.available)

    def test_add_over_size(self):
        resources = []
        for i in range(4):
            resource = _Resource()
            resources.append(resource)
        logger = _Logger()
        pool = self._makeOne(size=1, logger=logger)
        pool.add(resources[0], checked_out=True)
        self.assertEqual(len(logger._warnings), 0)
        self.assertEqual(len(logger._critical), 0)
        pool.add(resources[1], checked_out=True)
        self.assertEqual(len(logger._critical), 0)
        self.assertEqual(len(logger._warnings), 1)
        self.assertEqual(logger._warnings[0][1], (2, 1))
        pool.add(resources[2], checked_out=True)
        self.assertEqual(len(logger._critical), 1)
        self.assertEqual(logger._critical[0][1], (3, 1))

    def test_check_in_not_already_in_pool(self):
        pool = self._makeOne()
        resource = _Resource()
        self.assertRaises(ValueError, pool.check_in, resource)

    def test_check_in_already_in_available(self):
        pool = self._makeOne()
        resource = _Resource()
        pool.add(resource)
        self.assertRaises(ValueError, pool.check_in, resource)

    def test_check_in_already_in_pool_but_checked_out(self):
        pool = self._makeOne()
        resource = _Resource()
        pool.add(resource, checked_out=True)
        pool.check_in(resource)
        self.assertTrue(resource in pool.available)
        self.assertTrue(resource in list(pool))

    def test_check_out_wo_available(self):
        pool = self._makeOne()
        self.assertTrue(pool.check_out() is None)

    def test_check_out_w_available(self):
        pool = self._makeOne()
        resources = []
        for i in range(4):
            resource = _Resource()
            resources.append(resource)
            pool.add(resource)
        resource = pool.check_out()
        self.assertTrue(resource is resources[-1])
        self.assertFalse(resource in pool.available)
        self.assertTrue(resource in list(pool))


class _Resource(object):
    pass


class _Logger(object):

    def __init__(self):
        self._warnings = []
        self._critical = []

    def warning(self, fmt, *args):
        self._warnings.append((fmt, args))

    def critical(self, fmt, *args):
        self._critical.append((fmt, args))
