import concurrent.futures
import os
import subprocess
import sqlite3

from node.node_cpp import NodeCpp
from node.node_std import NodeStd


class BuilderCpp:
    """ Default builder for C++ module projects. """

    def __init__(self, env, sources, target):
        self.nodes = [NodeCpp(env, src) for src in sources]
        self.nodes.append(NodeStd(env))
        self.env = env
        self.target = env.build_dir / target

    def build(self):
        if not self.env.build_dir.exists():
            self.env.build_dir.mkdir(parents=True)

        # Run a scan on all nodes to assess md5 state.
        for node in self.nodes:
            node.pre_scan()

        # Check for any dirty nodes to save on rebuilds.
        actioned = any(node.dirty for node in self.nodes)
        if not actioned and self.target.exists():
            return

        cpu_count = os.cpu_count()
        workers = cpu_count if cpu_count else 1

        # Build the json descriptions of the modules and their dependencies.
        with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
            for node in self.nodes:
                # node.build_json()
                executor.submit(node.build_json)

        # Build the memory map, and write it out to file.
        for node in self.nodes:
            node.build_map()
        self.env.write_mapper()

        # Now build the in-memory dependency tree so object build order
        # can be properly determined.
        for node in self.nodes:
            node.build_deps()

        # Build any object not already built.
        # Build all nodes with dependencies immediately.
        '''
        for node in self.nodes:
            node.build_obj()
        '''

        # Iteratively build nodes with satisfied dependencies until all nodes are built.
        # Builds nodes in parallel where possible. Not terribly efficient as it recreates
        # the executor each iteration, but gets the jobs done.
        dirty_nodes = [node for node in self.nodes]
        while len(dirty_nodes) > 0:
            with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
                for node in dirty_nodes:
                    node.build_obj_submit(executor)
            # Reduce the nodes to those which are considered dirty.
            dirty_nodes = [node for node in dirty_nodes if node.dirty]

        # Finally build the executable.
        object_files = [node.obj() for node in self.nodes]
        linker = [
            '-o', str(self.target)
        ]
        full = self.env.link_commands + linker + object_files
        print(' '.join(full))
        subprocess.run(full, encoding='utf-8')

    def clean(self):
        for node in self.nodes:
            node.clean()
        if self.target.exists():
            self.target.unlink()
        self.env.clean()
