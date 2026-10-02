import argparse

from db import db_clean
from environment import Environment
from builder_cpp import BuilderCpp
from node.node_cpp import NodeVersion

parser = argparse.ArgumentParser(
    prog='hello')
parser.add_argument('--clean', help='clean build directory of generated files', action='store_true')
args = parser.parse_args()

sources = [
    'hello.cpp'
]

# Normally src_dir might be 'src' but for this example it's just '.'
env = Environment(src_dir='.', build_dir='build/debug')
builder = BuilderCpp(env=env, sources=sources, target='xarchitect')
# There's a default to generate version.cpp if that's wanted too.
# builder.nodes.append(NodeVersion(env))
# NodeStd is included in the builder by default, not need to specify it here.

def build(sources):
    # env.parse_cflags(['pkg-config', '--cflags', 'sdl3'])
    # env.parse_ldflags(['pkg-config', '--libs', 'fmt'])

    builder.build()
    print('build complete')


def clean(sources):
    builder.clean()
    # Also clean the main database to force a full rebuild next time.
    db_clean()


if args.clean:
    clean(sources=sources)
else:
    build(sources=sources)
