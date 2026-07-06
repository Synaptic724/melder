"""
Regression tests: cache rehydration exec of stored no-overrides code objects.

Purpose:
    Pin the fix for the split-namespace exec regression in
    `_build_inner_no_overrides_executor` (spell_codegen_creation_cache.py):
    hoist-form transient code objects (emitted by the closure-cell transient
    builder: `t{N} = ...` assignments before a bare `def (meld)`) place their
    hoists in the exec LOCALS under a split globals/locals exec while the def
    body's reads compile as GLOBALS - producing `NameError: t0` at meld time
    on every cache load of a freshly saved package. The loader must exec
    stored code objects with a SINGLE namespace.

Contract map:
    - Hoist-form transient code objects rehydrate into executors that
      construct correctly (the exact pre-fix failure).
    - Legacy defaults-form code objects (existing cache files saved before
      the closure port) still rehydrate and execute - backward compatibility
      of the single-namespace exec shape.
"""

import sys
from types import SimpleNamespace
from typing import Any, Dict


def _ensure_import_roots_on_path() -> None:
    """
    Purpose:
        Make `melder` imports resolve under plain CLI pytest runs.
    Contract:
        - Mirrors the efficacy probe's preamble; no-op under PyCharm/conftest.
    Returns:
        None.
    """
    if "." not in sys.path:
        sys.path.insert(0, ".")
    if "src" not in sys.path:
        sys.path.insert(0, "src")


_ensure_import_roots_on_path()

from melder.aether.spellbook.spell_compiler.codegen_creation_system.codegen_creation.spell_codegen_creation_cache import (
    _build_inner_no_overrides_executor,
)
from melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.generalized.compilers.generalized_no_overrides_codegen_creation_compiler import (
    _build_no_overrides_codegen_executor_source,
)

_TRANSIENT_DEP_FIELDS = (
    "dep1", "dep2a", "dep2b", "dep3a", "dep3b", "dep3c", "dep4a", "dep4b",
    "dep4c", "dep4d", "dep5a", "dep5b", "dep5c", "dep5d", "dep5e", "dep6a",
    "dep6b", "dep6c", "dep6d", "dep6e", "dep6f", "dep7a", "dep7b", "dep7c",
    "dep7d", "dep7e", "dep7f", "dep7g", "dep8a", "dep8b", "dep8c", "dep8d",
    "dep8e", "dep8f", "dep8g", "dep8h",
)


def _transient_schema(step_count: int, root_index: int, call_modes, **deps):
    """
    Build one normalized transient schema with zeroed dep arrays.
    """
    schema: Dict[str, Any] = {
        "step_count": step_count,
        "root_step_index": root_index,
        "call_modes": call_modes,
    }
    for field_name in _TRANSIENT_DEP_FIELDS:
        schema[field_name] = deps.get(
            field_name, tuple(0 for _ in range(step_count)),
        )
    return schema


def _row(spell_id: str, existence: str, deps=()):
    """
    Build one schema-only phase-11 step row (cache `steps_rows` shape).
    """
    return {
        "instance_key": (spell_id, None),
        "spell_id": spell_id,
        "existence": existence,
        "creations_target_kind": 0,
        "dependency_resolution_order": tuple(
            (name, tuple((dep, None) for dep in dep_ids))
            for name, dep_ids in deps
        ),
        "collection_param_names": (),
        "uses_positional_override": False,
        "contract_positional_override": None,
        "has_contract_payload": False,
        "contract_payload_items": (),
        "use_spell_lock_hint": False,
        "must_register": False,
        "shared_instance": False,
        "override_match_prefix": None,
        "override_match_prefix_len": 0,
        "override_keys": (),
        "expects_overrides": False,
        "contract_keys": (),
        "lock_hint": "creations_lock",
        "requires_spellspace": False,
        "owner_conduit_required": False,
        "disposal_method_names": (),
    }


def _pool_spell(target) -> SimpleNamespace:
    """
    Build one live-pool spell stub exposing the rehydration read surface.
    """
    return SimpleNamespace(
        is_class_spell=False,
        is_method_spell=False,
        is_lambda_spell=True,
        is_existing_creation=False,
        spell=target,
        user_created_object=None,
        has_disposal_methods=False,
        disposal_method_names=[],
    )


def _fake_live_spell(pool: Dict[str, Any]) -> SimpleNamespace:
    """
    Build the loader-facing spell whose Spellbook pool resolves step spells.
    """
    return SimpleNamespace(
        _spellbook=SimpleNamespace(_spell_id_pool=dict(pool)),
    )


def test_hoist_form_transient_code_object_rehydrates_and_executes() -> None:
    """The exact pre-fix failure: hoist-form cache load must not NameError."""
    def leaf() -> str:
        return "LEAF"

    def parent(x: Any) -> Any:
        return ("PARENT", x)

    schema = _transient_schema(2, 1, (0, 1), dep1=(0, 0))
    source = _build_no_overrides_codegen_executor_source(
        transient_schema=schema,
    )
    assert source is not None
    assert "t0 = transient_targets[0]" in source  # hoist form, not defaults
    code_object = compile(
        source,
        "<melder_no_overrides_codegen_creation_transient_executor>",
        "exec",
    )
    package = {
        "no_overrides": {
            "step_spell_ids": ("leaf_id", "parent_id"),
            "steps_rows": (
                _row("leaf_id", "many"),
                _row("parent_id", "many", deps=[("x", ["leaf_id"])]),
            ),
            "transient_schema": schema,
            "code_object": code_object,
            "root_spell_id": "parent_id",
        },
    }
    live_spell = _fake_live_spell({
        "leaf_id": _pool_spell(leaf),
        "parent_id": _pool_spell(parent),
    })
    executor = _build_inner_no_overrides_executor(live_spell, package)
    meld = SimpleNamespace()
    assert executor(meld) == ("PARENT", "LEAF")
    assert executor(meld) == ("PARENT", "LEAF")


def test_legacy_defaults_form_code_object_still_executes() -> None:
    """Existing cache files (defaults-form sources) stay loadable."""
    legacy_source = (
        "def _no_overrides_codegen_creation_executor(\n"
        "        meld,\n"
        "        transient_targets=transient_targets,\n"
        "        steps=steps,\n"
        "    ):\n"
        "    t0 = transient_targets[0]\n"
        "    t1 = transient_targets[1]\n"
        "    v0 = t0()\n"
        "    v1 = t1(v0)\n"
        "    return v1\n"
    )
    def leaf() -> str:
        return "L"

    def parent(x: Any) -> Any:
        return ("P", x)

    schema = _transient_schema(2, 1, (0, 1), dep1=(0, 0))
    code_object = compile(legacy_source, "<legacy_transient>", "exec")
    package = {
        "no_overrides": {
            "step_spell_ids": ("leaf_id", "parent_id"),
            "steps_rows": (
                _row("leaf_id", "many"),
                _row("parent_id", "many", deps=[("x", ["leaf_id"])]),
            ),
            "transient_schema": schema,
            "code_object": code_object,
            "root_spell_id": "parent_id",
        },
    }
    live_spell = _fake_live_spell({
        "leaf_id": _pool_spell(leaf),
        "parent_id": _pool_spell(parent),
    })
    executor = _build_inner_no_overrides_executor(live_spell, package)
    assert executor(SimpleNamespace()) == ("P", "L")
