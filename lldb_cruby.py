#!/usr/bin/env python
#coding: utf-8
#
# Usage: run `command script import -r misc/lldb_cruby.py` on LLDB
#
# Test: misc/test_lldb_cruby.rb
#

from __future__ import print_function
import lldb
import os
import inspect
import sys
import shlex
import platform
import glob
import importlib
import operator

from constants import *

load_dir, _ = os.path.split(os.path.realpath(__file__))

for fname in glob.glob(f"{load_dir}/commands/*_command.py"):
    _, basename = os.path.split(fname)
    mname, _ = os.path.splitext(basename)

    print(f"importing {mname} from {fname}")
    exec(f"import commands.{mname}")

def custom_command_p(memname, mem):
    return inspect.isclass(mem) and \
        memname.endswith("Command") and \
        not memname.startswith("RbBase") and \
        callable(getattr(mem, "register_lldb_command", None))

def __lldb_init_module(debugger, dict):
    # Register all classes that have a register_lldb_command method
    for modname in sys.modules:
        if "command" in modname and not modname == "rb_base_command":
            for memname, mem in inspect.getmembers(sys.modules[modname]):
                if custom_command_p(memname, mem):
                    mem.register_lldb_command(debugger, f"{__name__}.{mem.__module__}")
