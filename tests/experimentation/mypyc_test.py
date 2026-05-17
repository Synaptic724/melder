from pathlib import Path

from setuptools import find_packages, setup
from mypyc.build import mypycify


class MypycBuild:
    def __init__(self, source_root: str, package_root: str) -> None:
        self._source_root = Path(source_root)
        self._package_root = self._source_root / package_root

    def collect_python_modules(self) -> list[str]:
        modules: list[str] = []

        for path in self._package_root.rglob("*.py"):
            if "tests" in path.parts:
                continue

            if "__pycache__" in path.parts:
                continue

            modules.append(str(path))

        return modules


build = MypycBuild(source_root="src", package_root="melder")
source_files = build.collect_python_modules()

setup(
    name="melder",
    packages=find_packages("src"),
    package_dir={"": "src"},
    ext_modules=mypycify(
        [
            "--disallow-untyped-defs",
            *source_files,
        ]
    ),
)