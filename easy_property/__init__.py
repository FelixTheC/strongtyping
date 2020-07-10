#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@created: 09.07.20
@author: felix
"""
from functools import partial
import strongtyping


def action(f, frefs):

    """
    This code is original from Ruud van der Ham https://github.com/salabim/easy_property
    """
    if f.__qualname__ == action.qualname:
        if any(action.f[fref] is not None for fref in frefs.split("_")):
            raise AttributeError(f"decorator defined twice")
    else:
        action.f.update({}.fromkeys(action.f, None))  # reset all values to None
        action.qualname = f.__qualname__
    action.f.update({}.fromkeys(frefs.split('_'), f))  # set all frefs values to f

    # this line was added by myself
    action.f['setter'] = strongtyping.strong_typing.match_typing(action.f['setter']) if action.f['setter'] is not None else None

    return property(*(action.f[ref] if (ref != "documenter" or action.f[ref] is None)
                      else action.f[ref](0) for ref in action.f))


action.qualname = None
action.f = dict.fromkeys(["getter", "setter", "deleter", "documenter"], None)

globals().update({fref: partial(action, frefs=fref) for fref in {**action.f, 'getter_setter': None}})
