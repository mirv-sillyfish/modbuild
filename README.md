# modbuild

C++ module builder, heavily inspired by SCons (a much better build system that otherwise lacks module support).

The term "builder" here is misleading. This is not a normal build system: it's not described, it's programmed.

Simply call the modbuild.py file from the directory of the build.py file of the target project. See the example.

## Requirements

This is experimental and built around gcc-16.2 (though 16.1 might work) and requires some of the nice dependency file generation avilable there. It's probably relatively easy to setup something similar for clang one day.
