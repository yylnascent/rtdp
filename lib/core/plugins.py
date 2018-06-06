# Copyright (C) 2010-2013 Claudio Guarnieri.
# Copyright (C) 2014-2015 Cuckoo Foundation.
# This file is part of Cuckoo Sandbox - http://www.cuckoosandbox.org
# See the file 'docs/LICENSE' for copying permission.

import os
import pkgutil
import importlib
import inspect
import logging
from collections import defaultdict
from distutils.version import StrictVersion

from lib.common.exceptions import RTDPCriticalError

log = logging.getLogger(__name__)

_modules = defaultdict(list)

def import_plugin(name):
    try:
        module = __import__(name, globals(), locals(), ["dummy"], 0)
    except ImportError as e:
        raise RTDPCriticalError("Unable to import plugin "
                                "\"{0}\": {1}".format(name, e))
    else:
        load_plugins(module)

def import_package(package):
    prefix = package.__name__ + "."
    for loader, name, ispkg in pkgutil.iter_modules(package.__path__, prefix):
        log.debug("plugins name %s." % name)
        import_plugin(name)

def load_plugins(module):
    for name, value in inspect.getmembers(module):
        if inspect.isclass(value):
            register_plugin('intrusion')


def register_plugin(group, name):
    global _modules
    group = _modules.setdefault(group, [])
    group.append(name)

def list_plugins(group=None):
    if group:
        return _modules[group]
    else:
        return _modules
