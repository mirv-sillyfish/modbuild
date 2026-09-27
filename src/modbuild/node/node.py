import hashlib
from pathlib import Path

from db import db_con


class Node:
    """ Node is a basic build node.
    Basic build class that represents how to build a source file to a
    target file within a given dependency hierarchy.
    """

    def __init__(self, env, src: str):
        base = src.rsplit('.', 1)[0]

        self.env = env
        self._src = env.src_dir / src

        self.dep_nodes = []

        self._md5 = self.md5()
        self.dirty = True

        cur = db_con.cursor()
        md5 = cur.execute(''' SELECT hash FROM MD5 WHERE file=? ''', (self.src(),)).fetchone()
        if md5:
            if md5[0] == self._md5:
                self.dirty = False
            else:
                cur.execute(''' UPDATE MD5 SET hash=? WHERE file=? ''', (self._md5, self.src()))
                db_con.commit()
        else:
            cur.execute(''' INSERT INTO MD5 VALUES(?, ?) ''', (self.src(), self.md5()))
            db_con.commit()
        cur.close()

    def _hash(self, filename):
        md5 = None
        with open(filename, 'rb') as sfile:
            data = sfile.read()
            md5 = hashlib.md5(data).hexdigest()
        return md5

    def md5(self):
        return self._hash(self._src)

    def src(self):
        return str(self._src)

    def clean(self):
        pass
