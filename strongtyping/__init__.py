#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@created: 04.06.20
@author: felix
"""

__all__ = ['_utils',
           'strong_typing_utils',
           'strong_typing',
           'docstring_typing',
           'cached_set',
           'cached_dict',
           'type_namedtuple']

import os

try:
    from strongtyping_modules.install import install
except ImportError:
    pass
else:
    if not bool(os.environ.get('ST_MODULES_INSTALLED', '0')):
        install()
        os.environ['ST_MODULES_INSTALLED'] = '1'
