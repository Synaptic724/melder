"""
Validate the new `unique_per_conduit_lineage` runtime lane.

Context:
    `unique_per_conduit_lineage` was moved off the shared owner-creations route
    onto its own `"lineage"` route that reads/writes the RESOLVING door's
    lineage-root creations (`root_creations`). This test conjures real lineage
    spells and proves the lane executes correctly and shares one instance across
    a lineage (root + lesser), for both the solo lane (no deps) and the
    generalized lane (a lineage root with a `unique` dep -> exercises the
    per-step OWNER routing change).

Scope:
    - Proves intra-lineage SHARING (root + lesser resolve the same instance) and
      that the instance physically lives in the lineage-root store.
    - Does NOT prove cross-root ISOLATION (two roots -> two instances); that
      rides the borrow path (epic Story E) and is a separate test.

Run (on the 3.14t target):
    .venv_new\\Scripts\\python.exe -m pytest tests/experimentation/test_lineage_root_scoped_instance.py -q
"""

import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple


def _ensure_src_on_path() -> None:
    """
    Put the melder `src/` directory on `sys.path` (this file is at
    <root>/tests/experimentation/, so the import root is <root>/src).
    """
    src_dir = Path(__file__).resolve().parents[2] / "src"
    src_as_str = str(src_dir)
    if src_as_str not in sys.path:
        sys.path.insert(0, src_as_str)


_ensure_src_on_path()

FRAME_NAME = "lineage-root-scoped-test"
CONDUIT_NAME = "lineage-root-scoped-test"


def _reset_runtime() -> None:
    """
    Reset the Aether/Nexus singleton runtime so each build starts clean.
    """
    from melder.aether.aether import Aether
    from melder.aether.conduit.conduit import Conduit
    from melder.aether.spellbook.spellbook import Spellbook
    from melder.nexus.nexus import Nexus

    Nexus._reset_singleton_for_tests()
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether


class _UniqueDep:
    """Plain unique (frame-singleton) dependency used by the generalized case."""

    def __init__(self) -> None:
        pass


class _LineageSolo:
    """No-dependency lineage spell -> solo lane."""

    def __init__(self) -> None:
        pass


class _LineageWithDep:
    """Lineage spell with a unique dep -> generalized lane (root step is lineage)."""

    def __init__(self, dep: _UniqueDep) -> None:
        self.dep = dep


def _build_root() -> Tuple[Any, Any, Dict[type, str]]:
    """
    Bind the lineage graph and conjure one root conduit (caching disabled,
    single phase-scheduler worker), mirroring the benchmark harness setup.
    """
    from melder.aether.spellbook.existence.existence import Existence
    from melder.aether.spellbook.spellbook import Spellbook

    _reset_runtime()
    spellbook = Spellbook(aetheric_frame=FRAME_NAME)
    configuration = spellbook.get_configuration()
    configuration.set_property("phase_scheduler_workers_per_spellbook", 1)
    spellbook.configure_aether_frame(
        system_state=None,
        disposal=None,
        disposal_method_names=None,
        system_caching_enabled=False,
    )
    spell_ids: Dict[type, str] = {
        _UniqueDep: spellbook.bind(
            spell=_UniqueDep, existence=Existence.unique, permissions="create"
        ),
        _LineageSolo: spellbook.bind(
            spell=_LineageSolo,
            existence=Existence.unique_per_conduit_lineage,
            permissions="create",
        ),
        _LineageWithDep: spellbook.bind(
            spell=_LineageWithDep,
            existence=Existence.unique_per_conduit_lineage,
            permissions="create",
        ),
    }
    conduit = spellbook.conjure(name=CONDUIT_NAME, dynamic=False)
    return spellbook, conduit, spell_ids


def _meld_in_lineage(spell_id: str) -> Tuple[Any, Any, List[Any]]:
    """
    Meld `spell_id` on the root and on two pooled lesser conduits.

    Returns:
        (root_instance, root_conduit, [lesser_instances...]).
    """
    spellbook, root, spell_ids = _build_root()
    try:
        root_instance = root.meld(spell_id=spell_id)
        lesser_instances: List[Any] = []
        for _ in range(2):
            lesser = root.create_lesser_conduit()
            try:
                lesser_instances.append(lesser.meld(spell_id=spell_id))
            finally:
                lesser.cleanup()
        # Capture root presence before teardown.
        in_root_store = root._creations.get_creation(spell_id)
        return root_instance, in_root_store, lesser_instances
    finally:
        root.permanent_cleanup()
        spellbook.cleanup()


def test_solo_lineage_shares_one_instance_across_the_lineage() -> None:
    """
    A no-dep lineage spell: root + lessers all resolve the SAME instance, and it
    lives in the lineage-root store.
    """
    _, _, spell_ids = _build_root()
    root_instance, in_root_store, lesser_instances = _meld_in_lineage(
        spell_ids[_LineageSolo]
    )
    assert root_instance is not None
    assert in_root_store is root_instance, (
        "lineage instance must live in the lineage-root creations store"
    )
    for lesser_instance in lesser_instances:
        assert lesser_instance is root_instance, (
            "every lesser in the lineage must resolve the root's single instance"
        )


def test_generalized_lineage_root_with_unique_dep_shares_one_instance() -> None:
    """
    A lineage spell WITH a unique dep (generalized lane): root + lessers share the
    one lineage instance (and the unique dep is itself a single frame instance).
    """
    _, _, spell_ids = _build_root()
    root_instance, in_root_store, lesser_instances = _meld_in_lineage(
        spell_ids[_LineageWithDep]
    )
    assert root_instance is not None
    assert isinstance(root_instance.dep, _UniqueDep)
    assert in_root_store is root_instance
    for lesser_instance in lesser_instances:
        assert lesser_instance is root_instance
        # The shared lineage instance carries the same (unique) dep object.
        assert lesser_instance.dep is root_instance.dep


if __name__ == "__main__":
    test_solo_lineage_shares_one_instance_across_the_lineage()
    test_generalized_lineage_root_with_unique_dep_shares_one_instance()
    print("OK: lineage root-scoped instance sharing holds for solo + generalized.")
