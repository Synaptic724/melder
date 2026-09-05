"""Real binding-to-cleanup method order and reference ownership across compiler families."""

from typing import Iterator

import pytest

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spellbook import Spellbook
from melder.nexus.nexus import Nexus
from tests.component.melder.spellbook.test_ordered_disposal_binding import configured_book


class DisposalLeaf:
    """Record disposal in invocation order; accept a label to exercise real overrides."""

    def __init__(self, label: str = "base") -> None:
        """Start with an empty disposal log and retain the constructor label."""
        self.label = label
        self.calls: list[str] = []

    def close(self) -> None:
        """Record close without altering the other methods."""
        self.calls.append("close")

    def flush(self) -> None:
        """Record flush at its actual position in the chain."""
        self.calls.append("flush")

    def stop(self) -> None:
        """Record stop at its actual position in the chain."""
        self.calls.append("stop")


class DisposalRoot:
    """Hold a real injected dependency and verify it remains live during root disposal."""

    def __init__(self, leaf: DisposalLeaf, label: str = "base") -> None:
        """Borrow the injected leaf and initialize this instance's disposal observations."""
        self.leaf = leaf
        self.label = label
        self.calls: list[str] = []
        self.closed_before_leaf = False

    def close(self) -> None:
        """Record whether dependency teardown has started when root close runs."""
        self.closed_before_leaf = not self.leaf.calls
        self.calls.append("close")

    def flush(self) -> None:
        """Record flush at its actual position in the chain."""
        self.calls.append("flush")

    def stop(self) -> None:
        """Record stop at its actual position in the chain."""
        self.calls.append("stop")


@pytest.fixture(autouse=True)
def isolated_world() -> Iterator[None]:
    """Reset the real singleton world before and after each independent runtime graph."""
    Nexus._reset_singleton_for_tests()
    Aether._reset_singleton_for_tests()
    Spellbook._aether = Aether()
    Conduit._aether = Spellbook._aether
    try:
        yield
    finally:
        Nexus._reset_singleton_for_tests()
        Aether._reset_singleton_for_tests()
        Spellbook._aether = Aether()
        Conduit._aether = Spellbook._aether


@pytest.mark.parametrize("family", ["solo", "generalized", "many_only"])
@pytest.mark.parametrize("priority", [False, True])
@pytest.mark.parametrize("overrides", [False, True])
def test_real_compiled_disposal_uses_established_order(
        family: str, priority: bool, overrides: bool,
) -> None:
    """Cold and repeated melds carry bind policy into stored instances and actual ordered cleanup."""
    expected = ["flush", "close", "stop"] if priority else ["close", "stop", "flush"]
    with configured_book(["flush", "close"], priority) as book:
        leaf_id = book.bind(
            spell=DisposalLeaf,
            existence="unique" if family == "generalized" else "many",
            disposal_method_names=["close", "stop"],
        )
        target_id = leaf_id
        if family != "solo":
            target_id = book.bind(
                spell=DisposalRoot, existence="many", disposal_method_names=["close", "stop"],
            )
        conduit = book.conjure()
        target_spell = book.find_spell_by_id(target_id)
        assert target_spell is not None
        assert target_spell._compiler_artifact._spell_codegen_plan.no_overrides_plan.metadata["plan_family"] == family
        instance = conduit.meld(
            spell_id=target_id, override={"label": "custom"} if overrides else None,
        )
        repeated = conduit.meld(
            spell_id=target_id, override={"label": "custom"} if overrides else None,
        )
        assert repeated is not instance
        assert instance.label == ("custom" if overrides else "base")
        assert repeated.label == instance.label
        live = [(target_id, instance), (target_id, repeated)]
        if family != "solo":
            live.append((leaf_id, instance.leaf))
            if repeated.leaf is not instance.leaf:
                live.append((leaf_id, repeated.leaf))
        for spell_id, value in live:
            spell = book.find_spell_by_id(spell_id)
            assert spell is not None
            raw_entry = conduit._creations._disposable_creations[spell_id]
            entry = (
                next(row for row in raw_entry if row[0] is value)
                if spell.existence is Existence.many else raw_entry
            )
            assert entry[0] is value
            assert entry[1] == expected
            assert entry[1] is spell.disposal_method_names
        conduit.permanent_cleanup()
        for _spell_id, value in live:
            assert value.calls == expected
        if family != "solo":
            assert instance.closed_before_leaf is True
            assert repeated.closed_before_leaf is True
