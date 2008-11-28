import passpersist

class oid_compare_Tests(object):
    def oid_compare_test_smaller(self):
        oid1 = ".0.0"
        oid2 = ".0.0.1"
        assert passpersist.oid_compare(oid1, oid2) == -1

    def oid_compare_test_equal(self):
        oid1 = ".0.1"
        oid2 = ".0.1"
        assert passpersist.oid_compare(oid1, oid2) == 0

    def oid_compare_test_greater(self):
        oid1 = ".0.2"
        oid2 = ".0.1.1"
        assert passpersist.oid_compare(oid1, oid2) == 1

class PassPersist_Tests(object):
    def setUp(self):
        self.root = '.0.0'
        self.oid1 = '.1.1'
        self.oid2 = '.1.2'
        self.subtree = { self.oid1 : ('STRING', 'Foo'), self.oid2 : ('STRING', 'Bar') }
        self.result1 = (self.root + self.oid1, 'STRING', 'Foo')
        self.result2 = (self.root + self.oid2, 'STRING', 'Bar')
        self.pp = passpersist.PassPersist(self.root, self.subtree)

    def base_oid_test(self):
        assert self.pp.base_oid == self.root

    def get_none_at_root_test(self):
        assert self.pp.get(self.root) == None

    def get_non_root_test(self):
        assert self.pp.get('.1') == None

    def get_valid_test(self):
        assert self.pp.get(self.root + self.oid1) == self.result1
        assert self.pp.get(self.root + self.oid2) == self.result2

    def getnext_from_root_test(self):
        assert self.pp.getnext(self.root) == self.result1

    def getnext_from_oid1_test(self):
        assert self.pp.getnext(self.root + self.oid1) == self.result2

    def getnext_from_oid2_test(self):
        assert self.pp.getnext(self.root + self.oid2) == None

    def dict_update_test(self):
        new_value = "Skadoo"
        self.subtree[self.oid1] = ('STRING', new_value)
        new_result = (self.result1[0], self.result1[1], new_value)
        result = self.pp.get(self.root + self.oid1)
        assert result == new_result

class CachedPassPersist_Tests(PassPersist_Tests):
    def setUp(self):
        super(CachedPassPersist_Tests, self).setUp()
        self.pp = passpersist.CachedPassPersist(self.root, self.subtree)

    def dict_update_test(self):
        """Change the subtree without waiting for the cache to update."""
        new_value = "Skadoo"
        self.subtree[self.oid1] = ('STRING', new_value)
        result = self.pp.get(self.root + self.oid1)
        assert result == self.result1

    def dict_update_with_cache_update_test(self):
        """Set a low cache time and wait for the cache to update."""
        from time import sleep,time
        self.pp.cache_time = 1
        new_value = "Skadoo"
        self.subtree[self.oid1] = ('STRING', new_value)
        new_result = (self.result1[0], self.result1[1], new_value)
        sleep(2)
        result = self.pp.get(self.root + self.oid1)
        time = time()
        assert result == new_result

