"""
Regression contract: address-bearing spells get the same id in a fresh process.

The in-process tests use content-identical twins; this one runs the real thing - two interpreters importing
the same module - for the shapes whose ids used to change on every run.
"""

import json
import os
import pathlib
import subprocess
import sys
import textwrap


def _shapes_module_source() -> str:
    """Return the source of the module whose objects both interpreters fingerprint."""
    return textwrap.dedent('''
    import functools


    class Engine:
        """Product type."""


    def make_engine(size: int = 3) -> Engine:
        return Engine()


    def make_with_marker(marker: object = object()) -> Engine:
        return Engine()


    class Workshop:
        def build(self) -> Engine:
            return Engine()


    class CallableFactory:
        def __call__(self) -> Engine:
            return Engine()


    class Settings:
        """Default repr."""


    class MarkerEngine:
        def __init__(self, marker: object = object()) -> None:
            self.marker = marker


    CANDIDATES = {
        "function": make_engine,
        "function_object_default": make_with_marker,
        "lambda": lambda: Engine(),
        "bound_method": Workshop().build,
        "partial": functools.partial(make_engine, size=4),
        "callable_instance": CallableFactory(),
        "instance_default_repr": Settings(),
        "class_object_default": MarkerEngine,
    }
''')


def _child_source() -> str:
    """Return the child script: print every candidate's spell id as JSON."""
    return textwrap.dedent('''
    import json
    from melder.aether.spellbook.bind.bind import Bind
    from melder.aether.spellbook.existence.existence import Existence
    import stability_shapes
    print(json.dumps({k: Bind.spell_id_inspector(v, existence=Existence.unique)
                      for k, v in stability_shapes.CANDIDATES.items()}))
''')


def _project_root() -> pathlib.Path:
    """Return the repository root (the directory holding `src/` and `tests/`)."""
    return pathlib.Path(__file__).resolve().parents[4]


def _ids_from_fresh_process(shapes_dir: pathlib.Path) -> dict[str, str]:
    """Run one fresh interpreter and return its spell ids by shape."""
    env = dict(os.environ)
    env["PYTHONPATH"] = os.pathsep.join([str(_project_root() / "src"), str(shapes_dir)])
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    completed = subprocess.run(
        [sys.executable, "-c", _child_source()],
        cwd=str(shapes_dir),
        env=env,
        capture_output=True,
        text=True,
        timeout=300,
    )
    assert completed.returncode == 0, completed.stderr
    return json.loads(completed.stdout.strip().splitlines()[-1])


def test_address_bearing_spell_ids_match_across_fresh_processes(tmp_path: pathlib.Path) -> None:
    """
    Purpose: Regression for function/method/lambda/partial/instance spell ids changing every process.
    Contract: Two fresh interpreters produce identical ids for every shape.
    """
    (tmp_path / "stability_shapes.py").write_text(_shapes_module_source(), encoding="utf-8")

    first = _ids_from_fresh_process(tmp_path)
    second = _ids_from_fresh_process(tmp_path)

    assert sorted(first) == sorted(second)
    assert {shape for shape in first if first[shape] != second[shape]} == set()
