from mypyc.build import mypycify
from setuptools import setup

setup(
    ext_modules=mypycify(
        [
            "src/strongtyping/strong_typing_utils.py",
        ]
    ),
)
