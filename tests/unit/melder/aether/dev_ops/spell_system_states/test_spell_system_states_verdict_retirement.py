"""Unit coverage for per-conduit verdict retirement in `SpellSystemStates` (rebind-after-first-meld repair).

`unregister_index` retires the removed spell id's resolution verdicts in every registered conduit state and
`register_index` retires any verdict already held for the version id it publishes, so a definition bound
again under the same content-stable id is resolved again by each conduit before it is built there.
"""

from typing import List, Optional, Tuple
from unittest.mock import MagicMock

import pytest

from melder.aether.aetheric_frame.dev_ops.devops_information_registry import DevopsInformationRegistry
from melder.aether.aetheric_frame.dev_ops.spell_system_states.spell_state_change_reason import (
    SpellStateChangeReason,
)
from melder.aether.aetheric_frame.dev_ops.spell_system_states.spell_system_states import SpellSystemStates
from melder.aether.aetheric_frame.dev_ops.spell_system_states.spell_validity import SpellValidity
from melder.aether.spellbook.bind.spell_index import SpellIndex


class _RecordingRiskManager:
    """Risk-manager double recording structural and resolution callbacks separately."""

    def __init__(self) -> None:
        """Start with no recorded callbacks."""
        self.structural: List[Tuple[str, Optional[SpellValidity]]] = []
        self.resolution: List[Tuple[str, str, Optional[SpellValidity]]] = []

    def on_structural_validity_change(self, lineage_id: str, validity: Optional[SpellValidity]) -> None:
        """Record a structural callback."""
        self.structural.append((lineage_id, validity))

    def on_resolution_validity_change(
            self,
            conduit_id: str,
            spell_id: str,
            validity: Optional[SpellValidity],
    ) -> None:
        """Record a resolution callback."""
        self.resolution.append((conduit_id, spell_id, validity))


@pytest.fixture
def registry() -> DevopsInformationRegistry:
    """A live DevOps information registry, cleaned after the test."""
    registry = DevopsInformationRegistry("retirement-frame")
    yield registry
    registry.cleanup()


@pytest.fixture
def states(registry: DevopsInformationRegistry) -> SpellSystemStates:
    """A SpellSystemStates registry over a mocked frame, cleaned after the test."""
    frame = MagicMock()
    frame.name = "retirement-frame"
    states = SpellSystemStates(frame, registry)
    yield states
    if not states._cleaned:
        states.cleanup()


def _index(spell_id: str) -> SpellIndex:
    """Build a real SpellIndex whose selected spell id is `spell_id`."""
    return SpellIndex(spell_id)


def _seed_verdicts(states: SpellSystemStates, spell_id: str, conduit_ids: Tuple[str, ...]) -> None:
    """Publish a valid spell and root verdict for `spell_id` in each named conduit."""
    for conduit_id in conduit_ids:
        states.set_conduit_spell_validity(conduit_id, spell_id, SpellValidity.valid)
        states.set_conduit_root_validity(conduit_id, spell_id, SpellValidity.valid)


def _verdicts(states: SpellSystemStates, conduit_id: str, spell_id: str) -> Tuple[SpellValidity, SpellValidity]:
    """Return (spell validity, root validity) for one conduit and id."""
    state = states.get_conduit_resolution_state(conduit_id)
    assert state is not None
    return state.get_spell_validity(spell_id), state.get_root_validity(spell_id)


def test_forget_spell_resolution_verdicts_counts_only_the_conduits_that_held_one(
        states: SpellSystemStates,
) -> None:
    """The public verb visits every conduit and reports how many held a verdict for the id."""
    _seed_verdicts(states, "spell-a", ("c1", "c2"))
    _seed_verdicts(states, "spell-b", ("c3",))

    forgotten = states.forget_spell_resolution_verdicts(
        "spell-a", change_reason=SpellStateChangeReason.cleaned_up_spell,
    )

    assert forgotten == 2
    assert _verdicts(states, "c1", "spell-a") == (SpellValidity.unknown, SpellValidity.unknown)
    assert _verdicts(states, "c2", "spell-a") == (SpellValidity.unknown, SpellValidity.unknown)
    assert _verdicts(states, "c3", "spell-b") == (SpellValidity.valid, SpellValidity.valid)


def test_forget_spell_resolution_verdicts_empty_id_is_zero(states: SpellSystemStates) -> None:
    """An empty id forgets nothing."""
    _seed_verdicts(states, "spell-a", ("c1",))

    assert states.forget_spell_resolution_verdicts("") == 0
    assert _verdicts(states, "c1", "spell-a") == (SpellValidity.valid, SpellValidity.valid)


def test_forget_spell_resolution_verdicts_miss_is_zero(states: SpellSystemStates) -> None:
    """An id no conduit resolved is a miss everywhere."""
    _seed_verdicts(states, "spell-a", ("c1",))

    assert states.forget_spell_resolution_verdicts("never-resolved") == 0


def test_forget_spell_resolution_verdicts_refuses_a_cleaned_registry(states: SpellSystemStates) -> None:
    """The public verb fails fast once the registry is cleaned."""
    states.cleanup()

    with pytest.raises(RuntimeError):
        states.forget_spell_resolution_verdicts("spell-a")


def test_unregister_index_retires_the_removed_ids_verdicts_in_every_conduit(
        states: SpellSystemStates,
) -> None:
    """Removing a lineage leaves no verdict for its current spell id in any conduit."""
    index = _index("spell-a")
    states.register_index(index)
    _seed_verdicts(states, "spell-a", ("root", "peer"))
    _seed_verdicts(states, "spell-b", ("root",))

    states.unregister_index(index)

    assert _verdicts(states, "root", "spell-a") == (SpellValidity.unknown, SpellValidity.unknown)
    assert _verdicts(states, "peer", "spell-a") == (SpellValidity.unknown, SpellValidity.unknown)
    assert _verdicts(states, "root", "spell-b") == (SpellValidity.valid, SpellValidity.valid)


def test_unregister_index_marks_each_affected_conduit_dirty_with_cleaned_up_spell(
        states: SpellSystemStates,
) -> None:
    """The conduit states that held a verdict are dirty with the removal reason; others are not."""
    index = _index("spell-a")
    states.register_index(index)
    _seed_verdicts(states, "spell-a", ("root",))
    _seed_verdicts(states, "spell-b", ("peer",))
    states.clear_conduit_dirty("root", 1.0)
    states.clear_conduit_dirty("peer", 1.0)

    states.unregister_index(index)

    root_state = states.get_conduit_resolution_state("root")
    peer_state = states.get_conduit_resolution_state("peer")
    assert root_state is not None and peer_state is not None
    assert root_state.is_dirty() is True
    assert root_state._last_change_reason is SpellStateChangeReason.cleaned_up_spell
    assert peer_state.is_dirty() is False


def test_unregister_index_missing_lineage_still_retires_the_selected_ids_verdicts(
        states: SpellSystemStates,
) -> None:
    """The 'state missing' branch retires verdicts for `selected_spell_id` as well."""
    _seed_verdicts(states, "spell-orphan", ("root",))

    assert states.unregister_index(_index("spell-orphan")) is None

    assert _verdicts(states, "root", "spell-orphan") == (SpellValidity.unknown, SpellValidity.unknown)


def test_register_index_retires_a_verdict_already_held_for_the_version_id(
        states: SpellSystemStates,
) -> None:
    """A version id that re-enters the frame starts with no verdict in any conduit (the rebind case)."""
    _seed_verdicts(states, "spell-a", ("root", "peer"))
    _seed_verdicts(states, "spell-b", ("root",))

    states.register_index(_index("spell-a"))

    assert _verdicts(states, "root", "spell-a") == (SpellValidity.unknown, SpellValidity.unknown)
    assert _verdicts(states, "peer", "spell-a") == (SpellValidity.unknown, SpellValidity.unknown)
    assert _verdicts(states, "root", "spell-b") == (SpellValidity.valid, SpellValidity.valid)
    root_state = states.get_conduit_resolution_state("root")
    assert root_state is not None
    assert root_state._last_change_reason is SpellStateChangeReason.register_or_rebind


def test_register_index_first_time_id_touches_no_verdict(states: SpellSystemStates) -> None:
    """Registering an id no conduit resolved leaves every other verdict and dirty flag alone."""
    _seed_verdicts(states, "spell-b", ("root",))
    states.clear_conduit_dirty("root", 1.0)

    states.register_index(_index("spell-new"))

    assert _verdicts(states, "root", "spell-b") == (SpellValidity.valid, SpellValidity.valid)
    root_state = states.get_conduit_resolution_state("root")
    assert root_state is not None
    assert root_state.is_dirty() is False


def test_unregister_then_register_same_id_leaves_no_verdict_for_the_replacement(
        states: SpellSystemStates,
) -> None:
    """The rebind-after-first-meld sequence at the registry level: valid -> removed -> rebound -> unknown."""
    first = _index("spell-same")
    states.register_index(first)
    _seed_verdicts(states, "spell-same", ("root",))
    assert _verdicts(states, "root", "spell-same") == (SpellValidity.valid, SpellValidity.valid)

    states.unregister_index(first)
    second = _index("spell-same")
    state = states.register_index(second)

    assert state.current_spell_id == "spell-same"
    assert _verdicts(states, "root", "spell-same") == (SpellValidity.unknown, SpellValidity.unknown)


def test_retirement_fires_no_resolution_callback_and_keeps_the_structural_pattern(
        states: SpellSystemStates,
) -> None:
    """Forgetting notifies no RiskManager; the structural gated/cleaned pattern of the lineage is unchanged."""
    risk_manager = _RecordingRiskManager()
    states.set_risk_manager(risk_manager)
    index = _index("spell-a")
    states.register_index(index)
    _seed_verdicts(states, "spell-a", ("root",))
    resolution_calls_after_seed = len(risk_manager.resolution)
    assert resolution_calls_after_seed == 2

    states.unregister_index(index)
    states.register_index(_index("spell-a"))

    assert len(risk_manager.resolution) == resolution_calls_after_seed
    assert [validity for _, validity in risk_manager.structural] == [
        SpellValidity.gated,
        SpellValidity.cleaned,
        SpellValidity.gated,
    ]


def test_retirement_never_creates_a_conduit_state(states: SpellSystemStates) -> None:
    """Forgetting reads the registry; it does not mint conduit buckets."""
    index = _index("spell-a")
    states.register_index(index)

    states.unregister_index(index)
    states.forget_spell_resolution_verdicts("spell-a")

    assert list(states.iter_conduit_resolution_states()) == []
