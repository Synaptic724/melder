from melder.spellbook.spell_crafter.system.spell_system_index import SpellSystemIndex
from melder.spellbook.spell_crafter.system.spell_system_node import SpellSystemNode
from melder.spellbook.spell_crafter.system.validation.visibility_gap_strategy import (
    VisibilityGapStrategy,
)


class _StateStub:
    """
    Purpose:
        Provide a minimal spell system state stub with dependencies.
    Contract:
        Exposes direct_dependencies without validation.
    """

    def __init__(self, direct_dependencies: set[str]) -> None:
        """
        Purpose:
            Initialize the state stub with direct dependencies.
        Contract:
            Stores the provided dependency set.
        Args:
            direct_dependencies: Direct dependency ids.
        Returns:
            None.
        """
        self.direct_dependencies = direct_dependencies


class _StatesStub:
    """
    Purpose:
        Provide a spell system states stub for lookup.
    Contract:
        Returns stored state objects by spell id.
    """

    def __init__(self, mapping: dict[str, _StateStub]) -> None:
        """
        Purpose:
            Initialize the state lookup mapping.
        Contract:
            Stores the provided mapping.
        Args:
            mapping: Spell id to state mapping.
        Returns:
            None.
        """
        self._mapping = dict(mapping)

    def get_by_spell_id(self, spell_id: str) -> _StateStub | None:
        """
        Purpose:
            Return the state for the requested spell id.
        Contract:
            Returns None when the spell id is not present.
        Args:
            spell_id: Spell id lookup key.
        Returns:
            _StateStub | None: Stored state or None.
        """
        return self._mapping.get(spell_id)


def test_visibility_gap_emits_missing_dependency_error() -> None:
    """
    Purpose:
        Verify missing dependencies filtered from the index emit errors.
    Contract:
        Emits visibility_gap_dependency_filtered when state deps are missing.
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
            dependencies={"visible"},
        )
    )
    states = _StatesStub({"root": _StateStub({"visible", "missing"})})
    diagnostics: list = []

    VisibilityGapStrategy().run(
        index=index,
        blueprints={},
        phase4_results={},
        broken_spell_ids=set(),
        spell_system_states=states,
        spell_lookup={},
        diagnostics=diagnostics,
        cancel_event=None,
    )

    assert len(diagnostics) == 1
    assert diagnostics[0].code == "visibility_gap_dependency_filtered"
    assert diagnostics[0].details["missing_dependency_ids"] == ["missing"]


def test_visibility_gap_skips_when_dependencies_match() -> None:
    """
    Purpose:
        Verify no diagnostics are emitted when dependencies match.
    Contract:
        Leaves diagnostics empty when state and index deps align.
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
            dependencies={"visible"},
        )
    )
    states = _StatesStub({"root": _StateStub({"visible"})})
    diagnostics: list = []

    VisibilityGapStrategy().run(
        index=index,
        blueprints={},
        phase4_results={},
        broken_spell_ids=set(),
        spell_system_states=states,
        spell_lookup={},
        diagnostics=diagnostics,
        cancel_event=None,
    )

    assert diagnostics == []
