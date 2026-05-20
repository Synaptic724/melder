from __future__ import annotations

from setuptools import setup
from mypyc.build import mypycify


setup(
    name="lock_contention_compiled",
    ext_modules=mypycify(["lock_contention_compiled.py"]),
)