import pytest

from melder.spellbook.existence.existence import Existence
from melder.spellbook.spell_crafter.system.spell_system_index import SpellSystemIndex
from melder.spellbook.spell_crafter.system.spell_system_node import SpellSystemNode
from melder.spellbook.spell_crafter.system.validation.scope_ordering_strategy import (
    ScopeOrderingStrategy,
)


def test_scope_ordering_violation_emits_error() -> None:
    """
    Purpose:
        Verify broad-to-narrow dependencies emit scope ordering errors.
    Contract:
        Emits scope_ordering_violation when scope ordering is violated.
    Returns:
        None.
    Raises:
        AssertionError: If the diagnostic is missing.
    """
    index = SpellSystemIndex()
    index.upsert_node(
        SpellSystemNode(
            spell_id="root",
            lineage_id="lineage-root",
            dependencies={"child"},
            existence=Existence.unique,
        )
    )
    index.upsert_node(
        SpellSystemNode(
            spell_id="child",
            lineage_id="lineage-child",
            dependencies=set(),
            existence=Existence.unique_per_spell_space,
        )
    )
    diagnostics: list = []

    ScopeOrderingStrategy().run(
        index=index,
        blueprints={},
        phase4_results={},
        broken_spell_ids=set(),
        spell_system_states=object(),
        spell_lookup={},
        diagnostics=diagnostics,
        cancel_event=None,
    )

    assert len(diagnostics) == 1
    assert diagnostics[0].code == "scope_ordering_violation"
    assert diagnostics[0].details["dependency_id"] == "child"


def test_scope_ordering_allows_narrow_to_broad() -> None:
    """
    Purpose:
        Verify narrow-to-broad dependencies do not emit diagnostics.
    Contract:
        Leaves diagnostics empty when ordering is respected.
    Returns:
        None.
    Raises:
        AssertionError: If diagnostics are emitted unexpectedly.
    """
    index = SpellSystemIndex()
    index.upsert_node(
        SpellSystemNode(
            spell_id="root",
            lineage_id="lineage-root",
            dependencies={"child"},
            existence=Existence.unique_per_spell_space,
        )
    )
    index.upsert_node(
        SpellSystemNode(
            spell_id="child",
            lineage_id="lineage-child",
            dependencies=set(),
            existence=Existence.unique,
        )
    )
    diagnostics: list = []

    ScopeOrderingStrategy().run(
        index=index,
        blueprints={},
        phase4_results={},
        broken_spell_ids=set(),
        spell_system_states=object(),
        spell_lookup={},
        diagnostics=diagnostics,
        cancel_event=None,
    )

    assert diagnostics == []


def test_scope_ordering_honors_cancellation() -> None:
    class _Cancel:
        @property
        def is_set(self):
            return True

        def throw_if_set(self):
            raise RuntimeError("cancelled")

    index = SpellSystemIndex()
    index.upsert_node(
        SpellSystemNode(
            spell_id="root",
            lineage_id="lineage-root",
            dependencies=set(),
            existence=Existence.unique,
        )
    )

    with pytest.raises(RuntimeError, match="cancelled"):
        ScopeOrderingStrategy().run(
            index=index,
            blueprints={},
            phase4_results={},
            broken_spell_ids=set(),
            spell_system_states=object(),
            spell_lookup={},
            diagnostics=[],
            cancel_event=_Cancel(),
        )


def test_scope_ordering_skips_node_with_unknown_or_missing_existence() -> None:
    index = SpellSystemIndex()
    missing_existence = SpellSystemNode(
        spell_id="missing",
        lineage_id="lineage-missing",
        dependencies={"dep"},
        existence=None,
    )
    unknown_existence = SpellSystemNode(
        spell_id="unknown",
        lineage_id="lineage-unknown",
        dependencies={"dep"},
        existence=Existence.unique,
    )
    unknown_existence.existence = object()
    many_existence = SpellSystemNode(
        spell_id="many",
        lineage_id="lineage-many",
        dependencies={"dep"},
        existence=Existence.many,
    )
    dep = SpellSystemNode(
        spell_id="dep",
        lineage_id="lineage-dep",
        dependencies=set(),
        existence=Existence.unique_per_spell_space,
    )
    for node in (missing_existence, unknown_existence, many_existence, dep):
        index.upsert_node(node)

    diagnostics: list = []

    ScopeOrderingStrategy().run(
        index=index,
        blueprints={},
        phase4_results={},
        broken_spell_ids=set(),
        spell_system_states=object(),
        spell_lookup={},
        diagnostics=diagnostics,
        cancel_event=None,
    )

    assert diagnostics == []


def test_scope_ordering_skips_missing_and_unknown_dependency_existence() -> None:
    index = SpellSystemIndex()
    root = SpellSystemNode(
        spell_id="root",
        lineage_id="lineage-root",
        dependencies={"missing", "none-dep", "many-dep", "unknown-dep"},
        existence=Existence.unique,
    )
    none_dep = SpellSystemNode(
        spell_id="none-dep",
        lineage_id="lineage-none",
        dependencies=set(),
        existence=None,
    )
    many_dep = SpellSystemNode(
        spell_id="many-dep",
        lineage_id="lineage-many",
        dependencies=set(),
        existence=Existence.many,
    )
    unknown_dep = SpellSystemNode(
        spell_id="unknown-dep",
        lineage_id="lineage-unknown",
        dependencies=set(),
        existence=Existence.unique,
    )
    unknown_dep.existence = object()
    for node in (root, none_dep, many_dep, unknown_dep):
        index.upsert_node(node)

    diagnostics: list = []

    ScopeOrderingStrategy().run(
        index=index,
        blueprints={},
        phase4_results={},
        broken_spell_ids=set(),
        spell_system_states=object(),
        spell_lookup={},
        diagnostics=diagnostics,
        cancel_event=None,
    )

    assert diagnostics == []
