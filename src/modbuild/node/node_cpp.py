import json
import subprocess

from node.node import Node


class NodeCpp(Node):
    def __init__(self, env, src):
        super(NodeCpp, self).__init__(env=env, src=src)
        base = src.rsplit('.', 1)[0]

        self._obj = env.build_dir / f'{base}.o'
        self._jsn = env.build_dir / f'{base}.json'
        self._gcm = env.cache_dir / f'{base}.gcm'
        self.dep_modules = []

        # Regardless of all else, if the object isn't built then the node is dirty.
        if not self._obj.exists():
            self.dirty = True
        # done.

    def clean(self):
        if self._obj.exists():
            self._obj.unlink()
        if self._jsn.exists():
            self._jsn.unlink()
        if self._gcm.exists():
            self._gcm.unlink()

    def obj(self):
        return str(self._obj)

    def jsn(self):
        return str(self._jsn)

    def gcm(self):
        return str(self._gcm)

    def build_json(self):
        if not self.dirty and self._jsn.exists():
            # The file hasn't changed and the appropriate json exists, don't bother with more.
            return

        # Make sure the subdirectoy for the build output exists.
        dirpath = self._jsn.parent
        if not dirpath.exists():
            dirpath.mkdir(parents=True)

        # Generate a builder command.
        builder = [
            '-M',
            '-MF', '/dev/null',
            '-fdeps-format=p1689r5',
            f'-fdeps-file={self._jsn}',
            f'-fdeps-target={self._obj.relative_to(self.env.build_dir)}',
            self.src()
        ]
        full = self.env.compile_commands + builder
        print(' '.join(full))
        subprocess.run(full, encoding='utf-8')

    def build_map(self):
        with open(self.jsn(), 'r') as jfile:
            dep = json.load(jfile)
            for rule in dep.get('rules', []):
                for prov in rule.get('provides', []):
                    if prov.get('is-interface', False):
                        logical = prov['logical-name']
                        self.env.mapper[logical] = self
                for req in rule.get('requires', []):
                    self.dep_modules.append(req['logical-name'])

    def build_deps(self):
        for dep in self.dep_modules:
            if dep in self.env.mapper:
                self.dep_nodes.append(self.env.mapper[dep])

    def build_obj(self):
        # First make sure any dependencies are built.
        for dep in self.dep_nodes:
            if dep.dirty:
                # If a dependency is dirty, then this node will need rebuilding too.
                self.dirty = True
                dep.build_obj()

        if self.dirty or not self._obj.exists():
            # Make sure the target path to the object exists.
            dirpath = self._obj.parent
            if not dirpath.exists():
                dirpath.mkdir(parents=True)

            builder = [
                f'-fmodule-mapper={self.env.mapfile}',
                '-o', self.obj(),
                '-c', self.src()
            ]
            full = self.env.compile_commands + builder
            print(' '.join(full))
            subprocess.run(full, encoding='utf-8')
            self.dirty = False
