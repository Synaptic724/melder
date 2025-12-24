"""Unit tests for SpellMutationNode cleanup behavior."""

from __future__ import annotations

from melder.spellbook.mutations.research.spell.node.spell_mutation_node import SpellMutationNode


def test_spell_mutation_node_cleanup_clears_payloads() -> None:
    """
    Purpose:
        Validate SpellMutationNode cleanup clears metadata and structure payloads.
    Contract:
        - cleanup() marks the node as cleaned.
        - cleanup() clears parent_id and payload references.
        - cleanup() is idempotent.
    Returns:
        None.
    Raises:
        AssertionError: If cleanup does not clear node payloads.
    """
    node = SpellMutationNode(
        spell_id="spell-id",
        parent_id="parent-id",
        metadata={"message": "seed"},
        structure={"field": "value"},
    )

    node.cleanup()

    assert node.cleaned is True
    assert node._metadata is None
    assert node._structure is None
    assert node._parent_id is None

    node.cleanup()
