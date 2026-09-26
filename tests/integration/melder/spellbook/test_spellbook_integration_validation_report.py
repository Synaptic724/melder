"""tests/integration/melder/spellbook/test_spellbook_integration_validation_report.py

What a user reads when a real conjure refuses spells (2026-09-26): each broken spell by name with
the reason and a fix, reasons from the conduit verdict included, no 64-character ids, warnings only
counted. Also pins the two misfires fixed with it: `*args: Any, **kwargs: Any` and plain data lists
and dicts no longer produce errors. A spell that only uses a cycle is named as its consumer, not as a
member of the cycle (2026-09-26).
"""
import re
from typing import Any, Iterator

import pytest

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.spellbook.configuration.spellbook_configuration import SpellbookConfiguration
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spellbook import Spellbook
from melder.nexus.nexus import Nexus
from melder.utilities.custom_exceptions.spellbook_validation_error import SpellbookValidationError
from tests._frame_posture_test_support import apply_dynamic_defaults_for_spellbook_configuration


@pytest.fixture(autouse=True)
def reset_singletons_for_report() -> Iterator[None]:
    """Reset Nexus + Aether around each test for singleton isolation."""
    def _reset() -> None:
        Nexus._reset_singleton_for_tests()
        Aether._reset_singleton_for_tests()
        aether = Aether()
        Spellbook._aether = aether
        Conduit._aether = aether

    _reset()
    yield
    _reset()


class Leaf:
    """Spellspace-scoped dependency."""

    def __init__(self) -> None:
        """Construct one leaf."""


class Holder:
    """Process-wide holder of a spellspace-scoped leaf (a captive dependency)."""

    def __init__(self, leaf: Leaf) -> None:
        """Keep the injected leaf."""
        self.leaf = leaf


class CycleA:
    """One half of a two-spell cycle, with one caller input."""

    def __init__(self, b: "CycleB", label: str) -> None:
        """Keep the other half and a label."""
        self.b = b
        self.label = label


class CycleB:
    """The other half of the cycle."""

    def __init__(self, a: CycleA) -> None:
        """Keep the first half."""
        self.a = a


class CycleUser:
    """Needs one half of the cycle without being part of it."""

    def __init__(self, a: CycleA) -> None:
        """Keep the half it needs."""
        self.a = a


class Flexible:
    """Accepts anything through *args/**kwargs annotated Any."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Keep the arguments."""
        self.args = args
        self.kwargs = kwargs


class Record:
    """Plain data holder: dicts and lists of data are caller inputs."""

    def __init__(self, payload: dict[str, Any], tags: list[str]) -> None:
        """Keep the data."""
        self.payload = payload
        self.tags = tags


def _book(tag: str) -> Spellbook:
    """Build one dynamic spellbook whose configuration frame matches its aetheric frame."""
    frame = f"intg-report-{tag}"
    configuration = SpellbookConfiguration(frame)
    apply_dynamic_defaults_for_spellbook_configuration(configuration)
    configuration.set_property("phase_scheduler_workers_per_spellbook", 1)
    return Spellbook(aetheric_frame=frame, configuration=configuration)


def _conjure_error(book: Spellbook) -> str:
    """Conjure and return the SpellbookValidationError text."""
    with pytest.raises(SpellbookValidationError) as caught:
        book.conjure(dynamic=True, name="root")
    return str(caught.value)


def test_scope_violation_report_states_reason_and_fix() -> None:
    """A conduit-verdict error reaches the message instead of "(none recorded)"."""
    book = _book("scope")
    book.bind(spell=Leaf, existence=Existence.unique_per_spell_space, permissions="create")
    book.bind(spell=Holder, existence=Existence.unique, permissions="create")
    try:
        message = _conjure_error(book)
    finally:
        book.cleanup()

    assert message.startswith("Spellbook validation failed. Broken spells: Holder.")
    assert "Spell 'Holder' (unique) depends on 'Leaf' (unique_per_spell_space)" in message
    assert "[scope_ordering_violation]" in message
    assert "none recorded" not in message


def test_cycle_report_uses_names_and_counts_warnings() -> None:
    """A cycle is named by class, with no 64-character ids, and the caller input is only counted."""
    book = _book("cycle")
    book.bind(spell=CycleA, existence=Existence.many, permissions="create")
    book.bind(spell=CycleB, existence=Existence.many, permissions="create")
    try:
        message = _conjure_error(book)
    finally:
        book.cleanup()

    assert "'CycleA' -> 'CycleB' -> 'CycleA'." in message
    assert re.search(r"[0-9a-f]{64}", message) is None
    assert "BINDING_RESOLUTION_CYCLE" not in message
    assert "1 warning not shown" in message
    assert "label" not in message


def test_cycle_consumer_is_reported_as_a_consumer() -> None:
    """A spell that only needs a cycle member is told which dependency leads there, not that it is in the cycle."""
    book = _book("consumer")
    book.bind(spell=CycleA, existence=Existence.many, permissions="create")
    book.bind(spell=CycleB, existence=Existence.many, permissions="create")
    book.bind(spell=CycleUser, existence=Existence.many, permissions="create")
    try:
        message = _conjure_error(book)
    finally:
        book.cleanup()

    assert (
        "Spell 'CycleUser' cannot be built: it needs 'CycleA', which is part of a dependency cycle: "
        "'CycleA' -> 'CycleB' -> 'CycleA'."
    ) in message
    assert "'CycleUser' itself is not part of that cycle." in message
    assert "Spell 'CycleUser' is part of a dependency cycle" not in message
    assert "Spell 'CycleA' is part of a dependency cycle: 'CycleA' -> 'CycleB' -> 'CycleA'." in message


def test_variadic_any_and_plain_data_containers_conjure() -> None:
    """*args: Any / **kwargs: Any and dict[str, Any] / list[str] parameters no longer break conjure."""
    book = _book("clean")
    book.bind(spell=Flexible, existence=Existence.many, permissions="create")
    book.bind(spell=Record, existence=Existence.many, permissions="create")
    try:
        conduit = book.conjure(dynamic=True, name="root")
        assert conduit is not None
    finally:
        book.cleanup()
