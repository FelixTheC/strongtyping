#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@created: 07.06.20
@author: felix
"""
import sys
from typing import Any, Union


class CachedSet(set):
    """
    Warning only use for caching when Memory limit is reached all items will be cleared
    """

    def __init__(self, memory_limit: Union[int, float] = 1, *args, **kwargs):
        """
        :param memory_limit: in MB
        """
        self.memory_limit = memory_limit * 1000000
        super(CachedSet, self).__init__(*args, **kwargs)

    def add(self, element: Any) -> None:
        if sys.getsizeof(self) > self.memory_limit:
            self.clear()
        super().add(element)
