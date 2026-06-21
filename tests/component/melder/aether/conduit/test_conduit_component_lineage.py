"""tests/component/melder/aether/conduit/test_conduit_component_lineage.py

Validation: Not run.

Component tests for `unique_per_conduit_lineage` at the conduit-subsystem level:
ONE lineage (a root and its lessers) sharing a single creation store. Covers the
structural store wiring (`_meld._root_creations`, `_cluster_creations`) and the
behavioral sharing, plus the differential against `unique_per_conduit`.

Cross-root ISOLATION and the dependency-routing path are integration concerns and
live in tests/integration/melder/conduit/test_conduit_integration_lineage_isolation.py.
"""

from __future__ import annotations

import pytest

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spellbook import Spellbook
from melder.nexus.nexus import Nexus

_LINEAGE = Existence.unique_per_conduit_lineage
_UPC = Existence.unique_per_conduit


@pytest.fixture(autouse=True)
def reset_singletons_for_component_lineage() -> None:
    """Reset Nexus + Aether around each component lineage test for isolation."""

    def _reset() -> None:
        Nexus._reset_singleton_for_tests()
        Aether._reset_singleton_for_tests()
        aether = Aether()
        Spellbook._aether = aether
        Conduit._aether = aether

    _reset()
    yield
    _reset()


class _LineageThing:
    def __init__(self) -> None:
        pass


class _LineageAlt:
    def __init__(self) -> None:
        pass


class _UpcThing:
    def __init__(self) -> None:
        pass


def _lineage_book(tag: str) -> Spellbook:
    """Mirror of the lineage-root build: caching off, one phase-scheduler worker."""
    book = Spellbook(aetheric_frame=f"comp-lin-{tag}")
    book.get_configuration().set_property("phase_scheduler_workers_per_spellbook", 1)
    book.configure_aether_frame(
        system_state=None,
        disposal=None,
        disposal_method_names=None,
        system_caching_enabled=False,
    )
    return book


# --- structural wiring ------------------------------------------------------
def test_root_meld_root_creations_points_at_own_store() -> None:
    book = _lineage_book("struct-root")
    root = book.conjure(name="root", dynamic=False)
    try:
        assert root._meld._root_creations is root._creations
    finally:
        root.permanent_cleanup()
        book.cleanup()


def test_lesser_and_deep_share_root_creations_pointer() -> None:
    book = _lineage_book("struct-lesser")
    root = book.conjure(name="root", dynamic=False)
    lesser = root.create_lesser_conduit()
    deep = lesser.create_lesser_conduit()
    try:
        assert lesser._meld._root_creations is root._creations
        assert deep._meld._root_creations is root._creations
    finally:
        deep.cleanup()
        lesser.cleanup()
        root.permanent_cleanup()
        book.cleanup()


def test_cluster_facade_shared_down_lineage() -> None:
    book = _lineage_book("struct-facade")
    root = book.conjure(name="root", dynamic=False)
    lesser = root.create_lesser_conduit()
    try:
        assert lesser._cluster_creations is root._cluster_creations
    finally:
        lesser.cleanup()
        root.permanent_cleanup()
        book.cleanup()


# --- behavioral sharing -----------------------------------------------------
def test_root_and_lessers_share_one_instance_in_root_store() -> None:
    book = _lineage_book("share")
    spell_id = book.bind(spell=_LineageThing, existence=_LINEAGE, permissions="create")
    root = book.conjure(name="root", dynamic=False)
    try:
        root_instance = root.meld(spell=spell_id)
        assert root._creations.get_creation(spell_id) is root_instance
        for _ in range(3):
            lesser = root.create_lesser_conduit()
            try:
                assert lesser.meld(spell=spell_id) is root_instance
            finally:
                lesser.cleanup()
    finally:
        root.permanent_cleanup()
        book.cleanup()


def test_deep_lesser_shares_root_instance() -> None:
    book = _lineage_book("deep")
    spell_id = book.bind(spell=_LineageThing, existence=_LINEAGE, permissions="create")
    root = book.conjure(name="root", dynamic=False)
    try:
        root_instance = root.meld(spell=spell_id)
        lesser = root.create_lesser_conduit()
        deep = lesser.create_lesser_conduit()
        try:
            assert lesser.meld(spell=spell_id) is root_instance
            assert deep.meld(spell=spell_id) is root_instance
        finally:
            deep.cleanup()
            lesser.cleanup()
    finally:
        root.permanent_cleanup()
        book.cleanup()


def test_two_distinct_lineage_spells_isolated() -> None:
    book = _lineage_book("two")
    id_a = book.bind(spell=_LineageThing, existence=_LINEAGE, permissions="create")
    id_b = book.bind(spell=_LineageAlt, existence=_LINEAGE, permissions="create")
    root = book.conjure(name="root", dynamic=False)
    try:
        a = root.meld(spell=id_a)
        b = root.meld(spell=id_b)
        assert a is not b
        lesser = root.create_lesser_conduit()
        try:
            assert lesser.meld(spell=id_a) is a
            assert lesser.meld(spell=id_b) is b
        finally:
            lesser.cleanup()
    finally:
        root.permanent_cleanup()
        book.cleanup()


def test_lineage_shared_but_unique_per_conduit_is_not() -> None:
    """Differential: lineage shares across lessers; unique_per_conduit does not."""
    book = _lineage_book("diff")
    lin_id = book.bind(spell=_LineageThing, existence=_LINEAGE, permissions="create")
    upc_id = book.bind(spell=_UpcThing, existence=_UPC, permissions="create")
    root = book.conjure(name="root", dynamic=False)
    try:
        root_lin = root.meld(spell=lin_id)
        root_upc = root.meld(spell=upc_id)
        lesser = root.create_lesser_conduit()
        try:
            assert lesser.meld(spell=lin_id) is root_lin
            assert lesser.meld(spell=upc_id) is not root_upc
        finally:
            lesser.cleanup()
    finally:
        root.permanent_cleanup()
        book.cleanup()


def test_remeld_is_idempotent() -> None:
    book = _lineage_book("idem")
    spell_id = book.bind(spell=_LineageThing, existence=_LINEAGE, permissions="create")
    root = book.conjure(name="root", dynamic=False)
    try:
        assert root.meld(spell=spell_id) is root.meld(spell=spell_id)
    finally:
        root.permanent_cleanup()
        book.cleanup()
