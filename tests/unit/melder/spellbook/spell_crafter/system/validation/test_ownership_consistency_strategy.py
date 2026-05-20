import pytest

from melder.aether.spellbook.spell_compiler.system.spell_system_index import SpellSystemIndex
from melder.aether.spellbook.spell_compiler.system.spell_system_node import SpellSystemNode
from melder.aether.spellbook.spell_compiler.system.validation.ownership_consistency_strategy import (
    OwnershipConsistencyStrategy,
)


def _make_node(spell_id: str, lineage_id: str | None, conduit_id: str | None):
    if lineage_id is None:
        class _NodeStub:
            def __init__(self) -> None:
                self.spell_id = spell_id
                self.lineage_id = None
                self.conduit_id = conduit_id

        return _NodeStub()

    node = SpellSystemNode(
        spell_id=spell_id,
        lineage_id=lineage_id,
        dependencies=set(),
        conduit_id=conduit_id,
    )
    return node


def test_ownership_consistency_skips_lineageless_nodes() -> None:
    index = SpellSystemIndex()
    index._nodes["lineageless"] = _make_node("lineageless", None, "conduit-a")  # noqa: SLF001

    diagnostics: list = []

    OwnershipConsistencyStrategy().run(
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


def test_ownership_consistency_honors_cancellation() -> None:
    class _Cancel:
        @property
        def is_set(self):
            return True

        def throw_if_set(self):
            raise RuntimeError("cancelled")

    index = SpellSystemIndex()
    index.upsert_node(_make_node("v1", "lineage-a", "conduit-a"))

    with pytest.raises(RuntimeError, match="cancelled"):
        OwnershipConsistencyStrategy().run(
            index=index,
            blueprints={},
            phase4_results={},
            broken_spell_ids=set(),
            spell_system_states=object(),
            spell_lookup={},
            diagnostics=[],
            cancel_event=_Cancel(),
        )
