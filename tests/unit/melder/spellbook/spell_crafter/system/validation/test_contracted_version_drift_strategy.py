from melder.spellbook.spell_crafter.system.spell_system_index import SpellSystemIndex
from melder.spellbook.spell_crafter.system.spell_system_node import SpellSystemNode
from melder.spellbook.spell_crafter.system.validation.contracted_version_drift_strategy import (
    ContractedVersionDriftStrategy,
)


class _SpellIndexStub:
    """
    Purpose:
        Provide a minimal spell index stub with lineage id access.
    Contract:
        Exposes id without validation.
    """

    def __init__(self, lineage_id: str) -> None:
        """
        Purpose:
            Initialize the index stub with a lineage id.
        Contract:
            Stores the provided lineage id as id.
        Args:
            lineage_id: Lineage id string.
        Returns:
            None.
        """
        self.id = lineage_id


class _SpellStub:
    """
    Purpose:
        Provide a minimal spell stub exposing spell_index.id.
    Contract:
        spell_index.id returns the lineage id.
    """

    def __init__(self, lineage_id: str) -> None:
        """
        Purpose:
            Initialize the spell stub with lineage metadata.
        Contract:
            Stores lineage id on spell_index.
        Args:
            lineage_id: Lineage id string.
        Returns:
            None.
        """
        self.spell_index = _SpellIndexStub(lineage_id)


def test_contracted_version_drift_emits_error() -> None:
    """
    Purpose:
        Verify stale index versions emit drift diagnostics.
    Contract:
        Emits contracted_version_drift when index spell id is not visible.
    Returns:
        None.
    Raises:
        AssertionError: If the diagnostic is missing.
    """
    index = SpellSystemIndex()
    index.upsert_node(
        SpellSystemNode(
            spell_id="old-version",
            lineage_id="lineage-1",
            dependencies=set(),
        )
    )
    spell_lookup = {
        "new-version": _SpellStub("lineage-1"),
    }
    diagnostics: list = []

    ContractedVersionDriftStrategy().run(
        index=index,
        blueprints={},
        phase4_results={},
        broken_spell_ids=set(),
        spell_system_states=object(),
        spell_lookup=spell_lookup,
        diagnostics=diagnostics,
        cancel_event=None,
    )

    assert len(diagnostics) == 1
    assert diagnostics[0].code == "contracted_version_drift"
    assert diagnostics[0].details["lineage_id"] == "lineage-1"


def test_contracted_version_drift_skips_visible_version() -> None:
    """
    Purpose:
        Verify visible versions do not emit drift diagnostics.
    Contract:
        Leaves diagnostics empty when index spell id is visible.
    Returns:
        None.
    Raises:
        AssertionError: If diagnostics are emitted unexpectedly.
    """
    index = SpellSystemIndex()
    index.upsert_node(
        SpellSystemNode(
            spell_id="current-version",
            lineage_id="lineage-1",
            dependencies=set(),
        )
    )
    spell_lookup = {
        "current-version": _SpellStub("lineage-1"),
    }
    diagnostics: list = []

    ContractedVersionDriftStrategy().run(
        index=index,
        blueprints={},
        phase4_results={},
        broken_spell_ids=set(),
        spell_system_states=object(),
        spell_lookup=spell_lookup,
        diagnostics=diagnostics,
        cancel_event=None,
    )

    assert diagnostics == []
