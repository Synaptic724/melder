"""
Diagnostic: which compiled executors does each binding shape actually produce?

Goal: stop guessing about lane routing. For several bindings of the SAME deep
graph we capture EVERY emitted executor source via `builtins.compile` (robust --
catches compiles regardless of which module triggers them, unlike wrapping one
module's `get_or_compile_executor_code` reference) and print each `source_name`.

The `source_name` reveals the lane/shape, e.g.:
  <melder_no_overrides_codegen_creation_step_executor...>      generalized step-plan
  <melder_no_overrides_codegen_creation_transient_executor>    transient unrolled
  <solo_no_overrides_codegen_creation:...>                     solo family
  <creation_context_no_overrides_only_template:...>            door template

We also flag whether each source contains `instance_results` (dict path) and run
each shape twice -- once with the real `_all_steps_inlinable` and once forcing it
False -- to see whether forcing the dict path changes anything (if it doesn't, the
generalized unroll never applies to that shape).

Run (fresh process so nothing is pre-cached):
  pytest -s -k test_lane_routing_diagnostic benchmarks/testing_other_di/test_unroll_path_diagnostic.py
"""

import sys
from pathlib import Path

# benchmarks/ has no conftest and pyproject does not add src/ to the path, so a
# plain-terminal pytest cannot import `melder` (PyCharm adds source roots, a bare
# shell does not). Put repo-root/src + repo-root on sys.path so this runs anywhere.
_PROJECT_ROOT = Path(__file__).resolve().parents[2]
for _candidate in (str(_PROJECT_ROOT / "src"), str(_PROJECT_ROOT)):
    if _candidate not in sys.path:
        sys.path.insert(0, _candidate)

import builtins
from typing import Dict, List, Tuple, Type

import pytest

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spellbook import Spellbook
from tests.mocks.spellbook.deep_layers import get_depth_5_classes
from melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.generalized.compilers import (
    generalized_no_overrides_codegen_creation_compiler as GEN,
)


def _reset_aether() -> None:
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether


def _capture_compiles(
    classes: Tuple[Type, ...],
    root_cls: Type,
    *,
    existence_of,
    force_dict: bool,
) -> List[Tuple[str, str]]:
    """Build the graph once; capture every emitted executor source."""
    captured: List[Tuple[str, str]] = []
    original_compile = builtins.compile
    original_inlinable = GEN._all_steps_inlinable

    def _cap(source, filename, mode, *args, **kwargs):
        if (
            isinstance(filename, str)
            and isinstance(source, str)
            and filename.startswith("<")
            and ("executor" in filename or "creation" in filename or "melder" in filename)
        ):
            captured.append((filename, source))
        return original_compile(source, filename, mode, *args, **kwargs)

    builtins.compile = _cap
    if force_dict:
        GEN._all_steps_inlinable = lambda steps: False
    try:
        _reset_aether()
        spellbook = Spellbook(aetheric_frame=f"lane-diag-{int(force_dict)}")
        spellbook.get_configuration().set_property(
            "phase_scheduler_workers_per_spellbook", 1
        )
        spell_ids: Dict[Type, str] = {}
        for cls in classes:
            spell_ids[cls] = spellbook.bind(
                spell=cls, existence=existence_of(cls), permissions="create"
            )
        conduit = spellbook.conjure(name="lane-diag")
        try:
            conduit.meld(spell=spell_ids[root_cls])
        finally:
            conduit.cleanup()
    finally:
        builtins.compile = original_compile
        GEN._all_steps_inlinable = original_inlinable
    return captured


def _print_capture(tag: str, captured: List[Tuple[str, str]]) -> None:
    # de-dup by source text
    seen = set()
    rows = []
    for name, src in captured:
        if src in seen:
            continue
        seen.add(src)
        rows.append((name, src))
    print(f"\n--- {tag}: {len(rows)} distinct executor source(s) ---")
    for name, src in rows:
        marker = "DICT(instance_results)" if "instance_results" in src else "no-dict"
        print(
            f"  {marker:24s} lines={src.count(chr(10)) + 1:4d}  {name}"
        )


@pytest.mark.parametrize(
    "shape",
    [
        "all_unique",
        "all_many",
        "many_root_unique_deps",
        "all_many_one_singleton",     # mostly many + ONE singleton leaf (your steer)
        "singleton_root_many_deps",   # one singleton root over many deps
    ],
)
def test_lane_routing_diagnostic(shape: str) -> None:
    classes = get_depth_5_classes()
    root_cls = classes[-1]
    first_leaf = classes[0]  # a leaf node

    if shape == "all_unique":
        existence_of = lambda cls: Existence.unique
    elif shape == "all_many":
        existence_of = lambda cls: Existence.many
    elif shape == "many_root_unique_deps":
        existence_of = lambda cls: (
            Existence.many if cls is root_cls else Existence.unique
        )
    elif shape == "all_many_one_singleton":
        existence_of = lambda cls: (
            Existence.unique if cls is first_leaf else Existence.many
        )
    else:  # singleton_root_many_deps
        existence_of = lambda cls: (
            Existence.unique if cls is root_cls else Existence.many
        )

    print(f"\n========== shape = {shape} (depth 5, root={root_cls.__name__}) ==========")
    real = _capture_compiles(classes, root_cls, existence_of=existence_of, force_dict=False)
    forced = _capture_compiles(classes, root_cls, existence_of=existence_of, force_dict=True)
    _print_capture("real _all_steps_inlinable", real)
    _print_capture("forced _all_steps_inlinable=False", forced)
