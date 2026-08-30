"""
Settle whether a lineage spell resolves correctly when it is a DEPENDENCY (not the
meld root), under a non-lineage root.

Model (runtime truth):
    lineage instances live in the meld's `root_creations` -- one instance per
    lineage; a lesser conduit borrows its lineage root's store. So any spell that
    depends on a lineage spell, melded across the root and its lessers, must see
    the SAME lineage instance.

The risk this probes:
    The generalized executor is handed only the ROOT's `caller_creations` (and an
    `owner_creations` the door derives from the root's route). The meld keeps
    `_root_creations` to itself. With a `many` root, `caller_creations` is the
    per-conduit store, so a lineage DEP routed CALLER would land in each conduit's
    own store -- and root vs lessers would get DIFFERENT lineage instances, which
    is broken lineage sharing.

Binary outcome:
    PASS -> the lineage dep is shared across the lineage; no hole.
    FAIL (assertion) -> root and lessers get different lineage deps; hole is real.
    ERROR at bind/conjure/meld -> the planner forbids lineage-as-dep here, so the
        shape can't be built and there is no hole to fix.

Run (3.14t):
    .venv_new\\Scripts\\python.exe -m pytest tests/experimentation/test_lineage_as_dependency.py -q
"""

import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple


def _ensure_src_on_path() -> None:
    """Put melder `src/` on sys.path (file is at <root>/tests/experimentation/)."""
    src_dir = Path(__file__).resolve().parents[2] / "src"
    if str(src_dir) not in sys.path:
        sys.path.insert(0, str(src_dir))


_ensure_src_on_path()

FRAME_NAME = "lineage-as-dep-test"
CONDUIT_NAME = "lineage-as-dep-test"


def _reset_runtime() -> None:
    """Reset the Aether/Nexus singleton runtime so each build starts clean."""
    from melder.aether.aether import Aether
    from melder.aether.conduit.conduit import Conduit
    from melder.aether.spellbook.spellbook import Spellbook
    from melder.nexus.nexus import Nexus

    Nexus._reset_singleton_for_tests()
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether


class _LineageLeaf:
    """A no-dependency lineage spell -> one instance per lineage."""

    def __init__(self) -> None:
        pass


class _ManyParentWithLineageDep:
    """
    A `many` (transient) spell that depends on the lineage spell, so the lineage
    spell appears as a DEPENDENCY step under a non-lineage (`many`) root. Being
    `many`, the parent is rebuilt on every meld, so its lineage dep is re-resolved
    each time -- which is exactly what surfaces a per-conduit vs per-lineage store.
    """

    def __init__(self, dep: _LineageLeaf) -> None:
        self.dep = dep


def _build_root() -> Tuple[Any, Any, Dict[type, str]]:
    """Bind the graph and conjure one root conduit (caching disabled, 1 worker)."""
    from melder.aether.spellbook.existence.existence import Existence
    from melder.aether.spellbook.spellbook import Spellbook

    _reset_runtime()
    spellbook = Spellbook(aetheric_frame=FRAME_NAME)
    spellbook.get_configuration().set_property(
        "phase_scheduler_workers_per_spellbook", 1
    )
    spellbook.configure_aether_frame(
        system_state=None,
        disposal=None,
        disposal_method_names=None,
        system_caching_enabled=False,
    )
    spell_ids: Dict[type, str] = {
        _LineageLeaf: spellbook.bind(
            spell=_LineageLeaf,
            existence=Existence.unique_per_conduit_lineage,
            permissions="create",
        ),
        _ManyParentWithLineageDep: spellbook.bind(
            spell=_ManyParentWithLineageDep,
            existence=Existence.many,
            permissions="create",
        ),
    }
    conduit = spellbook.conjure(name=CONDUIT_NAME, dynamic=False)
    return spellbook, conduit, spell_ids


def test_lineage_dependency_under_many_root_shares_across_lineage() -> None:
    """
    Meld a `many` parent (dep = lineage spell) on the root and two lesser conduits
    of the same lineage. The parent is transient, so its lineage dep is re-resolved
    each meld -- but lineage means ONE instance per lineage, so every parent must
    carry the SAME dep object.
    """
    spellbook, root, spell_ids = _build_root()
    try:
        parent_id = spell_ids[_ManyParentWithLineageDep]
        root_parent = root.meld(spell_id=parent_id)
        lesser_parents: List[Any] = []
        for _ in range(2):
            lesser = root.create_lesser_conduit()
            try:
                lesser_parents.append(lesser.meld(spell_id=parent_id))
            finally:
                lesser.cleanup()

        assert isinstance(root_parent.dep, _LineageLeaf)
        for lesser_parent in lesser_parents:
            assert lesser_parent.dep is root_parent.dep, (
                "lineage dep must be the SAME instance across the lineage (one per "
                "lineage). A different instance per conduit means the lineage dep "
                "resolved into the conduit's own caller_creations instead of the "
                "meld's root_creations -- the cross-scope-dependency hole."
            )
    finally:
        root.permanent_cleanup()
        spellbook.cleanup()


if __name__ == "__main__":
    test_lineage_dependency_under_many_root_shares_across_lineage()
    print("OK: lineage dependency is shared across the lineage (no hole).")
