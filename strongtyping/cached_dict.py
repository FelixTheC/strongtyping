#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@created: 06.06.20
@author: felix
"""
import sys
from typing import Union


class CachedDict(dict):
    """
    Warning only use for caching when Memory limit is reached all items will be cleared
    """

    def __init__(self, memory_limit: Union[int, float] = 1, *args, **kwargs):
        """
        :param memory_limit: in MB
        """
        self.memory_limit = memory_limit * 1000000
        super().__init__(*args, **kwargs)

    def __setitem__(self, key, value):
        if sys.getsizeof(self) > self.memory_limit:
            self.clear()
        super().__setitem__(key, value)
