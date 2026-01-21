"""Unit tests for ResearchSpell cleanup behavior."""

from __future__ import annotations

import pytest

from melder.spellbook.mutations.research.spell.spell_research import ResearchSpell


class _WeakRefTarget:
    """
    Purpose:
        Provide a weakref-friendly target for ResearchSpell.attach_spell.
    Contract:
        - Instances support weak references.
        - No behavior beyond identity is required.
    """


def test_research_spell_cleanup_cleans_nodes_and_refs() -> None:
    """
    Purpose:
        Validate ResearchSpell cleanup clears mutation nodes and weak references.
    Contract:
        - cleanup() marks the research line as cleaned.
        - cleanup() cleans committed nodes.
        - cleanup() nulls node registries, head id, metadata, and weak refs.
        - cleanup() is idempotent.
    Returns:
        None.
    Raises:
        AssertionError: If cleanup does not clear owned state.
    """
    research = ResearchSpell(spell_id="spell-id", name="spell-line")
    research.attach_spell(_WeakRefTarget())
    node = research.begin_mutation(message="seed")
    research.commit_mutation(node)

    research.cleanup()

    assert research.cleaned is True
    assert node.cleaned is True
    assert research._spell_ref is None
    assert research._nodes is None
    assert research._node_ids is None
    assert research._metadata is None
    assert research._head_id is None

    research.cleanup()

    with pytest.raises(RuntimeError, match="has already been cleaned"):
        research.begin_mutation()
