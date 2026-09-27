import json
import subprocess

from node.node_cpp import NodeCpp

class NodeStd(NodeCpp):
    def __init__(self, env):
        super(NodeStd, self).__init__(env=env, src='bits/std.cc')
        # 'bits/std.cc'

    def md5(self):
        return 'deadbeef'

    def build_json(self):
        # Don't do anything, std is already known about.
        pass

    def build_map(self):
        self.env.mapper['std'] = self

    def build_deps(self):
        # std won't have dependencies on this project.
        pass

    def build_obj(self):
        if not self.dirty and self._obj.exists():
            return

        dirpath = self._obj.parent
        if not dirpath.exists():
            dirpath.mkdir(parents=True)
        # g++ -fmodules -std=c++26 -fsearch-include-path -c bits/std.cc
        builder = [
            f'-fmodule-mapper={self.env.mapfile}',
            '-fsearch-include-path',
            '-c', 'bits/std.cc',
            '-o', self.obj()
        ]
        full = self.env.compile_commands + builder
        print(' '.join(full))
        subprocess.run(full, encoding='utf-8')
        self.dirty = False
