#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import pytest

from strongtyping.strong_typing import FinalClass


def test_decorated_class_behaves_like_normal_class():
    @FinalClass
    class Some:
        """Some is a decorated class"""

        def __init__(self, name, value):
            self.name = name
            self.value = value

        def __repr__(self):
            return f"[FinalClass]({self.__class__.__name__}): {self.name}, {self.value}"

    assert Some.__doc__ == "Some is a decorated class"

    some = Some("Hello", "Class")
    assert "[FinalClass](Some): Hello, Class" == repr(some)

    some = Some(name="Hello", value="Class")
    assert "[FinalClass](Some): Hello, Class" == repr(some)


def test_raises_runtime_error():
    with pytest.raises(RuntimeError):

        @FinalClass
        class Some:
            pass

        class Child(Some):
            pass


if __name__ == "__main__":
    pytest.main(["-vv", "-s", __file__])
