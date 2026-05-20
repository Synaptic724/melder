import pytest

from melder.aether.spellbook.spell_compiler.system.spell_system_index import SpellSystemIndex
from melder.aether.spellbook.spell_compiler.system.spell_system_node import SpellSystemNode
from melder.aether.spellbook.spell_compiler.system.validation.identity_mixing_strategy import (
    IdentityMixingStrategy,
)


def test_identity_mixing_emits_error_for_lineage_dependency() -> None:
    """
    Purpose:
        Verify lineage ids used as dependencies emit errors.
    Contract:
        Emits identity_mixing_detected when a dependency matches a lineage id.
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
            dependencies={"lineage-dep"},
        )
    )
    index.upsert_node(
        SpellSystemNode(
            spell_id="dep",
            lineage_id="lineage-dep",
            dependencies=set(),
        )
    )
    diagnostics: list = []

    IdentityMixingStrategy().run(
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
    assert diagnostics[0].code == "identity_mixing_detected"
    assert diagnostics[0].details["dependency_id"] == "lineage-dep"


def test_identity_mixing_skips_version_dependencies() -> None:
    """
    Purpose:
        Verify version id dependencies do not emit diagnostics.
    Contract:
        Leaves diagnostics empty when dependencies reference version ids.
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
            dependencies={"dep"},
        )
    )
    index.upsert_node(
        SpellSystemNode(
            spell_id="dep",
            lineage_id="lineage-dep",
            dependencies=set(),
        )
    )
    diagnostics: list = []

    IdentityMixingStrategy().run(
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


def test_identity_mixing_skips_unknown_dependency_ids() -> None:
    index = SpellSystemIndex()
    index.upsert_node(
        SpellSystemNode(
            spell_id="root",
            lineage_id="lineage-root",
            dependencies={"unknown-id"},
        )
    )
    index.upsert_node(
        SpellSystemNode(
            spell_id="dep",
            lineage_id="lineage-dep",
            dependencies=set(),
        )
    )
    diagnostics: list = []

    IdentityMixingStrategy().run(
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


def test_identity_mixing_honors_cancellation() -> None:
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
            dependencies={"lineage-dep"},
        )
    )

    with pytest.raises(RuntimeError, match="cancelled"):
        IdentityMixingStrategy().run(
            index=index,
            blueprints={},
            phase4_results={},
            broken_spell_ids=set(),
            spell_system_states=object(),
            spell_lookup={},
            diagnostics=[],
            cancel_event=_Cancel(),
        )
