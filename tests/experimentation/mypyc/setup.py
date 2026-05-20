from __future__ import annotations

from setuptools import setup
from mypyc.build import mypycify


setup(
    name="list_race_target",
    ext_modules=mypycify(["list_race_target.py"]),
)