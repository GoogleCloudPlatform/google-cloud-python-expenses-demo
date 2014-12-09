import logging
import threading
import time
import weakref


logger = logging.getLogger(__name__)


class ResourcePool(object):
    """Manage a pool of resourcess.

    There's no limit on the number of resourcess a pool can keep track of,
    but a warning is logged if there are more than ``pool.size`` active
    resources, and a critical problem if more than twice ``pool.size``.

    New resourcess are registered via add().  This will log a message if
    "too many" resourcess are active.

    When a resource is explicitly closed, return it via ``pool.check_in()``.
    That adds the resource to a stack of resources available for
    reuse, and throws away the oldest stack entries if the stack is too
    large.  ``pool.check_out()`` pops this stack.

    When a resource is obtained via ``pool.check_out()``, the pool holds only a
    weak reference to it thereafter.  It's not necessary to inform the pool
    if the resource goes away.  A resource handed out by ``pool.check_out()``
    counts against ``pool.size`` only so long as it exists, and provided it
    isn't returned via ``pool.check_in()``.
    
    We retain weak references to "checked out" resources  to allow debugging
    / monitoring.
    """

    def __init__(self, size=4, timeout=1<<31, logger=logger):

        self._lock = threading.RLock()
        self._logger = logger
        self._size = size
        self._timeout = timeout  # seconds

        # A weak mapping, id(resource) -> resource.
        self._all = weakref.WeakValueDictionary()

        # A stack of resources available to check out.
        self._available = []

    def __enter__(self):  # pragma: no cover
        return self._lock.__enter__()

    def __exit__(self, etype, err, tb):  # pragma: no cover
        return self._lock.__exit__(etype, err, tb)

    def __iter__(self):
        with self._lock:
            return iter(list(self._all.values()))

    @property
    def size(self):
        """Expected maximum # of live resources.
        """
        return self._size

    @size.setter
    def size(self, size):
        """Change the expected maximum # of live resources.

        If the new size is smaller than the current value, this may discard
        the oldest available resources.
        """
        with self._lock:
            self._size = size
            self._shrink(size)

    @property
    def timeout(self):
        """Max # of seconds to keep a resource in the pool.
        """
        return self._timeout

    @timeout.setter
    def timeout(self, timeout):
        """Change the max # of seconds to keep a resource in the pool.

        If the new timeout is smaller than the old value, this may discard
        the oldest available resources.
        """
        with self._lock:
            old, self._timeout = self._timeout, timeout
            if timeout < old:
                self._shrink(self.size)

    @property
    def available(self):
        """Return a set of the available connections.
        """
        with self._lock:
            return set([resource for timestamp, resource in self._available])

    def add(self, resource, checked_out=False):
        """Add a new resource to the pool.

        Raise ValueError if ``resource`` is already in the pool.

        If ``checked_out`` is False, push ``resource`` onto the available
        stack even if we're over the pool size limit (but shrink the pool
        if needed, potentially discarding older resources).

        If ``checked_out`` is True, do *not* push the resource onto
        the available stack:  the caller will presumably release it later
        via a call to ``check_in``.
        """
        with self._lock:
            if id(resource) in self._all:
                raise ValueError("Resource already in the pool")
            self._all[id(resource)] = resource
            if not checked_out:
                self._shrink(self.size - 1)
                self._append(resource)
            n = len(self._all)
            if n > self.size:
                reporter = self._logger.warning
                if n > 2 * self.size:
                    reporter = self._logger.critical
                reporter("Pool has %s resources with a size of %s",
                        n, self.size)

    def check_in(self, resource):
        """Release a checked-out resource back to the pool.

        Push ``resource`` onto the stack of available resources.
        
        May discard older available resources.
        """
        with self._lock:
            if id(resource) not in self._all:
                raise ValueError("Unknown resource:  use 'add()'")
            if resource in self.available:
                raise ValueError("Resource already checked in")
            self._shrink(self.size - 1)
            self._append(resource)

    def check_out(self):
        """Pop an available resource and return it.

        Return None if none are available.  In that case, the caller might
        create a new resource and register it via ``add()``, passing the
        ``checked_out`` flag to retain use of the resource..
        """
        with self._lock:
            if self._available:
                return self._available.pop()[1]

    def _append(self, resource):
        """Push a timestamped resource onto the stack available for checkout.

        Assumes ``self._lock`` is already acquired.
        """
        self._available.append((time.time(), resource))

    def _shrink(self, target):
        """Discard oldest available resources to meet the given target size.

        Assumes ``self._lock`` is already acquired.
        """
        threshhold = time.time() - self.timeout

        available = self._available
        while (len(available) > target or
              available and available[0][0] < threshhold):
            resource = available.pop(0)[1]
            del self._all[id(resource)]
