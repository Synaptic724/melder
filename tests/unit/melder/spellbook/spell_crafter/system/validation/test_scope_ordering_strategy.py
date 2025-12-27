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
