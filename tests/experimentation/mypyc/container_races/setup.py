from __future__ import annotations

from setuptools import setup
from mypyc.build import mypycify


setup(
    name="container_race_compiled",
    ext_modules=mypycify(["container_race_compiled.py"]),
)