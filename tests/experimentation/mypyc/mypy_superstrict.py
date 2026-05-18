from pathlib import Path

from mypyc.build import mypycify
from setuptools import find_packages, setup


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

    def collect_mypyc_args(self) -> list[str]:
        args: list[str] = [
            "--strict",
            "--warn-unreachable",
            "--strict-equality",
            "--strict-equality-for-none",

            # Any blockers
            "--disallow-any-unimported",
            "--disallow-any-expr",
            "--disallow-any-decorated",
            "--disallow-any-explicit",
            "--disallow-any-generics",

            # Untyped blockers
            "--disallow-untyped-calls",
            "--disallow-untyped-defs",
            "--disallow-incomplete-defs",
            "--disallow-untyped-decorators",
            "--check-untyped-defs",

            # Import / re-export strictness
            "--no-implicit-reexport",

            # Warnings that should be treated as defects
            "--warn-redundant-casts",
            "--warn-unused-ignores",
            "--warn-return-any",
            "--warn-no-return",

            # Extra error codes
            "--enable-error-code=redundant-self",
            "--enable-error-code=redundant-expr",
            "--enable-error-code=possibly-undefined",
            "--enable-error-code=truthy-bool",
            "--enable-error-code=truthy-iterable",
            "--enable-error-code=ignore-without-code",
            "--enable-error-code=unused-awaitable",
            "--enable-error-code=explicit-override",
            "--enable-error-code=mutable-override",
            "--enable-error-code=unimported-reveal",
            "--enable-error-code=exhaustive-match",
            "--enable-error-code=deprecated",

            # Output
            "--show-error-codes",
            "--show-error-code-links",
            "--show-column-numbers",
        ]

        args.extend(self.collect_python_modules())

        return args


setup(
    name="melder",
    packages=find_packages("src"),
    package_dir={"": "src"},
    package_data={"melder": ["py.typed", "**/*.pyi"]},
    ext_modules=mypycify(
        MypycBuild(
            source_root="src",
            package_root="melder",
        ).collect_mypyc_args(),
        opt_level="3",
        debug_level="0",
        strip_asserts=True,
        multi_file=False,
        separate=False,
    ),
)