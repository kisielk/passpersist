import sys
import re
from time import time

def oid_compare(x, y):
    """Comparison function for OID strings."""
    a = [int(v) for v in x.split('.')[1:]]
    b = [int(v) for v in y.split('.')[1:]]
    return cmp(a, b)

def oid_bisect_right(a, x):
    """bisect_right for an array of OID strings"""
    lo = 0
    hi = len(a)
    while lo < hi:
        mid = (lo + hi)//2
        if oid_compare(x, a[mid]) == -1:
            hi = mid
        else:
            lo = mid + 1
    return lo

class PassPersist(object):
    """Implements a Net-SNMP pass-persist module for a given subtree.

    The base_oid parameter is the root OID at which to place the subtree and
    should be in the format ".1.2.3.4"

    The subtree paramater is a dict-like object that responds to the keys(),
    items() and get() method. The keys of the dictionary should be the OIDs of
    the subtree, eg: ".5.6". The values should be tuples of (type, value), eg:
    "('Counter64', 1232314)". The get() method should return None if the key is
    not found, just as a dict does.

    This class makes the assumption that the dictionary keys never change, so
    it's not suitable for implementing any kind of indexed trees where the
    number of values in a branch varies during runtime.
    """

    def __init__(self, base_oid, subtree):
        self.base_oid = base_oid
        self.subtree = subtree

    def _get_base_oid(self):
        return self._base_oid

    def _set_base_oid(self, base_oid):
        self._base_oid = base_oid
        self._oid_re = re.compile("^(%s)(.*)" % base_oid)

    base_oid = property(_get_base_oid, _set_base_oid)

    def _get_subtree(self):
        return self._subtree

    def _update_oids(self):
        self._oids = self._subtree.keys()
        self._oids.sort(oid_compare)

    def _set_subtree(self, subtree):
        self._subtree = subtree
        self._update_oids()

    subtree = property(_get_subtree, _set_subtree)

    def get(self, request):
        """An SNMP get request.

        The request should be a string in the format ".root_oid.sub_oid"

        Returns a tuple: (oid, result_type, result) if a value exists at the
        requested OID, otherwise None.
        """
        request_match = self._oid_re.match(request)

        if request_match:
            result = self._subtree.get(request_match.group(2))
            if result:
                return request, result[0], result[1]
            else:
                return None
        else:
            return None

    def getnext(self, request):
        """An SNMP getnext request.

        Returns a tuple: (oid, result_type, result) from the next OID in the tree.
        Returns None only if there are no other OIDs in the current tree.
        """
        request_match = self._oid_re.match(request)

        if request_match:
            try:
                idx = oid_bisect_right(self._oids, request_match.group(2))
                oid = self._oids[idx]
                result = self._subtree[oid]
                return "%s%s" % (self._base_oid, oid), result[0], result[1]
            except (ValueError, IndexError):
                return None
        else:
            return None

    def _handle_request(self, request, request_func):
        result = request_func(request)
        if result:
            print result[0]
            print result[1]
            print result[2]
        else:
            print "NONE"

    def listen(self):
        """Begins listening for SNMP requests."""
        try:
            while True:
                line = raw_input()
                if line == "get":
                    request = raw_input()
                    self._handle_request(request, self.get)
                elif line == "getnext":
                    request = raw_input()
                    self._handle_request(request, self.getnext)
                elif line == "PING":
                    print "PONG"
                else:
                    print "NONE"
        except EOFError:
            # It's ok to get EOF, it just breaks us out of the loop
            pass

class CachedPassPersist(PassPersist):
    """A cached version of PassPersist.
    
    Functions much like the PassPersist class except that it keeps a cache of
    the dictionary values for the number of seconds specified by the cache
    parameter. This is suitable for plugins where the data is expensive to
    retrieve and freshness is not critical.

    Unlike the PassPersist class, this one can handle changing indicies.
    """
    def __init__(self, base_oid, subtree, cache=60):
        super(CachedPassPersist, self).__init__(base_oid, subtree)
        self.cache_time = cache

    def _update_cache(self):
        self._subtree = dict(self._real_subtree.items())
        self._update_oids()
        self.last_updated = time()

    def _check_and_update_cache(self):
        if time() - self.last_updated >= self.cache_time:
            self._update_cache()

    def _set_subtree(self, subtree):
        super(CachedPassPersist, self)._set_subtree(subtree)
        self._real_subtree = self._subtree
        self._update_cache()

    subtree = property(PassPersist._get_subtree, _set_subtree)

    def get(self, request):
        self._check_and_update_cache()
        return super(CachedPassPersist, self).get(request)

    def getnext(self, request):
        self._check_and_update_cache()
        return super(CachedPassPersist, self).getnext(request)

class DictSubtree(object):
    """A dictionary-based subtree base class.

    Child classes should redefine the update_dict() method and place data in to
    the oid_dict dictionary.
    """
    def __init__(self):
        self.update_dict()

    def update_dict(self):
        self.oid_dict = {}

    def get(self, oid):
        self.update_dict()
        return self.oid_dict.get(oid)

    def items(self):
        self.update_dict()
        return self.oid_dict.items()

    def keys(self):
        self.update_dict()
        return self.oid_dict.keys()

if __name__ == "__main__":
    subtree = { '.1.1' : ('STRING', 'Foo'), '.1.2' : ('STRING', 'Bar') }
    persist = CachedPassPersist(".0.0", subtree)
    persist.listen()
