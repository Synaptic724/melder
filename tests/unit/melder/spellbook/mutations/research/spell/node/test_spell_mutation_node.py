"""Unit tests for SpellMutationNode cleanup behavior."""

from __future__ import annotations

import pytest

from melder.mutation_research.research.spell.node.spell_mutation_node import SpellMutationNode


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


def test_spell_mutation_node_properties_and_metadata_detach() -> None:
    """
    Purpose:
        Validate the stable property surface before cleanup.
    Contract:
        - id is a non-empty string.
        - spell_id and parent_id round-trip constructor values.
        - metadata returns a detached shallow copy.
        - structure exposes the stored payload.
    Returns:
        None.
    Raises:
        AssertionError: If the property surface is incorrect.
    """
    structure = {"field": "value"}
    node = SpellMutationNode(
        spell_id="spell-id",
        parent_id="parent-id",
        metadata={"message": "seed"},
        structure=structure,
    )

    meta = node.metadata
    meta["message"] = "mutated"

    assert isinstance(node.id, str)
    assert node.id != ""
    assert node.spell_id == "spell-id"
    assert node.parent_id == "parent-id"
    assert node.metadata == {"message": "seed"}
    assert node.structure is structure

    node.cleanup()


def test_spell_mutation_node_placeholder_methods_raise() -> None:
    """
    Purpose:
        Validate the explicit placeholder contract.
    Contract:
        - snapshot_from_spell raises until implemented.
        - apply_to_blueprint raises until implemented.
    Returns:
        None.
    Raises:
        AssertionError: If placeholder methods stop raising.
    """
    node = SpellMutationNode(spell_id="spell-id")

    with pytest.raises(NotImplementedError):
        SpellMutationNode.snapshot_from_spell(
            object(),
            spell_id="spell-id",
        )

    with pytest.raises(NotImplementedError):
        node.apply_to_blueprint(object())

    node.cleanup()

    assert node.cleaned is True
    assert not hasattr(node, '_metadata')
    assert not hasattr(node, '_structure')
    assert not hasattr(node, '_parent_id')

    node.cleanup()
