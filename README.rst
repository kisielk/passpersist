passpersist: A library for writing Net-SNMP pass_persist commands
=================================================================

Installation
------------

Run `python setup.py install`

Example Usage
-------------

Create an executable python script that does something like the following::

    #!/usr/bin/env python
    import passpersist
    import random


    class MySubtree(passpersist.DictSubtree):
        def update_dict(self):
            self.oid_dict['.5'] = ('INTEGER', random.randint())


    if __name__ == "__main__":
        subtree = MySubTree()
        persist = passpersist.PassPersist(base_oid='.1.2.3.4', subtree=subtree)
        persist.listen()


Then in `/etc/snmp/snmpd.conf` add::

    pass_persist .1.2.3.4 /path/to/script.py
