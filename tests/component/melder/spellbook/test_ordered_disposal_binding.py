"""Producer contracts for ordered book/per-spell disposal metadata and bind identity."""

import json
import os
import subprocess
import sys
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator, Optional

import pytest

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.spellbook.bind.bind import Bind
from melder.aether.spellbook.configuration.spellbook_configuration import SpellbookConfiguration
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spellbinder import SpellBinder
from melder.aether.spellbook.spellbook import Spellbook
from melder.nexus.nexus import Nexus


class OrderedDisposalService:
    """Record actual disposal calls; definition order deliberately differs from requested order."""

    def __init__(self) -> None:
        """Initialize the per-instance invocation log."""
        self.calls: list[str] = []

    def close(self) -> None:
        """Record close without changing the other disposal methods."""
        self.calls.append("close")

    def flush(self) -> None:
        """Record flush in the order the runtime invokes it."""
        self.calls.append("flush")

    def stop(self) -> None:
        """Record stop in the order the runtime invokes it."""
        self.calls.append("stop")


class InheritedOnlyDisposal(OrderedDisposalService):
    """An empty own namespace keeps inherited-only methods outside current profile matching."""


def service_factory() -> OrderedDisposalService:
    """Return a service through the existing non-class binding family."""
    return OrderedDisposalService()


@pytest.fixture(autouse=True)
def fresh_runtime() -> Iterator[None]:
    """Isolate the real runtime using the suite's existing singleton reset pattern."""
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


@contextmanager
def configured_book(
        names: Optional[list[str]],
        priority: bool = False,
        *,
        frame: str = "ordered-disposal",
        dynamic: bool = False,
) -> Iterator[Spellbook]:
    """Own a configured book for one test, with caching disabled and no recorder activation."""
    configuration = SpellbookConfiguration(frame)
    if names is not None:
        configuration.with_disposal_method_names(names)
    if priority:
        configuration.with_enforce_priority_disposal_methods()
    configuration.with_defaults().with_phase_scheduler_workers(1).finalize()
    book = Spellbook(aetheric_frame=frame, configuration=configuration)
    try:
        book.configure_aether_frame(
            system_state="dynamic" if dynamic else None,
            disposal=None,
            disposal_method_names=None,
            system_caching_enabled=False,
        )
        yield book
    finally:
        book.cleanup()


@pytest.mark.parametrize("priority,expected", [
    (False, ["close", "stop", "flush"]),
    (True, ["flush", "close", "stop"]),
])
def test_binding_combines_groups_in_priority_order(priority: bool, expected: list[str]) -> None:
    """Resolve both groups once, preserving order while dropping duplicates and missing names."""
    with configured_book(["flush", "missing", "close", "flush"], priority) as book:
        spell_id = book.bind(
            spell=OrderedDisposalService,
            existence="many",
            disposal_method_names=["close", "stop", "absent", "close"],
        )
        spell = book.find_spell_by_id(spell_id)
        assert spell is not None
        assert spell.disposal_method_names == expected
        assert spell.has_disposal_methods is True
        assert Bind.spell_id_inspector(
            OrderedDisposalService,
            spell_name=spell.spell_name,
            existence=spell.existence,
            disposal_method_names=spell.disposal_method_names,
        ) == spell_id


@pytest.mark.parametrize("book_names,spell_names,expected", [
    (None, None, []),
    ([], [], []),
    (["flush", "close"], None, ["flush", "close"]),
    (["flush", "close"], [], ["flush", "close"]),
    ([], ["stop", "close"], ["stop", "close"]),
    (["missing"], ["absent"], []),
])
def test_empty_and_missing_groups_preserve_matching_contract(
        book_names: Optional[list[str]],
        spell_names: Optional[list[str]],
        expected: list[str],
) -> None:
    """An empty per-spell group leaves book names applicable; no matches means no disposal."""
    with configured_book(book_names) as book:
        spell_id = book.bind(
            spell=OrderedDisposalService, existence="many", disposal_method_names=spell_names,
        )
        spell = book.find_spell_by_id(spell_id)
        assert spell is not None
        assert spell.disposal_method_names == expected
        assert spell.has_disposal_methods is bool(expected)


@pytest.mark.parametrize("priority", [False, True])
def test_each_binding_uses_its_own_explicit_names(priority: bool) -> None:
    """The first binding must not supply another binding's explicit policy or shared list."""
    with configured_book(["flush"], priority) as book:
        first_id = book.bind(
            spell=OrderedDisposalService, existence="many", binding_name="first",
            disposal_method_names=["close"],
        )
        second_id = book.bind(
            spell=OrderedDisposalService, existence="many", binding_name="second",
            disposal_method_names=["stop"],
        )
        first = book.find_spell_by_id(first_id)
        second = book.find_spell_by_id(second_id)
        assert first is not None and second is not None
        assert first.disposal_method_names == (["flush", "close"] if priority else ["close", "flush"])
        assert second.disposal_method_names == (["flush", "stop"] if priority else ["stop", "flush"])
        assert first.disposal_method_names is not second.disposal_method_names


@pytest.mark.parametrize("priority", [False, True])
@pytest.mark.parametrize("after_conjure", [False, True])
def test_staged_binding_preserves_its_own_order_and_index_selection(
        priority: bool,
        after_conjure: bool,
) -> None:
    """Staging applies the same policy before/after conjure without replacing the active member."""
    with configured_book(["flush"], priority, dynamic=True) as book:
        active_id = book.bind(
            spell=OrderedDisposalService, existence="many", disposal_method_names=["close"],
        )
        active = book.find_spell_by_id(active_id)
        assert active is not None
        if after_conjure:
            book.conjure(dynamic=True)
        staged_id = book.bind_inactive(
            spell=OrderedDisposalService, spell_index=active.spell_index, existence="many",
            disposal_method_names=["stop"],
        )
        staged = book._get_owned_spell(staged_id)
        assert staged is not None
        try:
            assert staged.spell_index is active.spell_index
            assert active.spell_index.selected_spell_id == active_id
            assert staged_id != active_id
            assert staged.disposal_method_names == (["flush", "stop"] if priority else ["stop", "flush"])
        finally:
            book.cleanup_spell(spell=staged)


@pytest.mark.parametrize("priority", [False, True])
def test_fluent_binder_forwards_explicit_disposal_names(priority: bool) -> None:
    """The existing fluent kwargs path reaches the same ordered producer contract."""
    with configured_book(["flush"], priority) as book:
        binder = SpellBinder(book)
        try:
            spell_id = binder.bind(OrderedDisposalService).with_kwargs(
                disposal_method_names=["stop", "close"],
            ).finalize()
        finally:
            binder.cleanup()
        spell = book.find_spell_by_id(spell_id)
        assert spell is not None
        assert spell.disposal_method_names == (["flush", "stop", "close"] if priority else ["stop", "close", "flush"])


@pytest.mark.parametrize("target", [InheritedOnlyDisposal, service_factory, OrderedDisposalService()])
def test_disposal_matching_stays_with_existing_class_profile(target: object) -> None:
    """Inherited-only, factory, and prebuilt-instance methods remain outside class-profile matching."""
    with configured_book(["flush", "close"], True) as book:
        spell_id = book.bind(spell=target, existence="unique", disposal_method_names=["stop"])
        spell = book.find_spell_by_id(spell_id)
        assert spell is not None
        assert spell.disposal_method_names == []
        assert spell.has_disposal_methods is False


def test_raw_configuration_can_bind_without_disposal_name_property() -> None:
    """The raw configuration's early priority default permits ordinary pre-validation binding."""
    configuration = SpellbookConfiguration("raw-disposal-config")
    book = Spellbook(aetheric_frame="raw-disposal-config", configuration=configuration)
    try:
        spell_id = book.bind(spell=OrderedDisposalService, existence="many", disposal_method_names=["close"])
        spell = book.find_spell_by_id(spell_id)
        assert spell is not None
        assert spell.disposal_method_names == ["close"]
    finally:
        book.cleanup()


def test_resolved_order_changes_sha_but_unmatched_names_do_not() -> None:
    """Only retained order contributes to the disposal portion of the bind fingerprint."""
    identities: list[str] = []
    for number, names in enumerate((["flush", "close"], ["close", "flush"], ["flush", "missing", "close"])):
        with configured_book(names, frame=f"disposal-hash-{number}") as book:
            identities.append(book.bind(spell=OrderedDisposalService, existence="many"))
    assert identities[0] != identities[1]
    assert identities[0] == identities[2]


@pytest.mark.parametrize("priority,expected", [
    (False, ["close", "stop", "flush"]),
    (True, ["flush", "close", "stop"]),
])
def test_bound_order_reaches_real_cleanup(priority: bool, expected: list[str]) -> None:
    """A real conjure/meld/cleanup smoke check preserves the producer sequence."""
    with configured_book(["flush", "close"], priority) as book:
        spell_id = book.bind(
            spell=OrderedDisposalService, existence="many", disposal_method_names=["close", "stop"],
        )
        conduit = book.conjure()
        instance = conduit.meld(spell_id=spell_id)
        conduit.permanent_cleanup()
        assert instance.calls == expected


def test_real_bind_fingerprint_is_stable_across_hash_seeds() -> None:
    """Fresh supported processes bind the same source-defined class to the same ordered identity."""
    repository = Path(__file__).resolve().parents[4]
    probe = """
import json
from tests.component.melder.spellbook.test_ordered_disposal_binding import OrderedDisposalService, configured_book
with configured_book(["flush", "close"]) as book:
    spell_id = book.bind(spell=OrderedDisposalService, existence="many", disposal_method_names=["stop"])
    spell = book.find_spell_by_id(spell_id)
    print(json.dumps([spell_id, list(spell.disposal_method_names)]))
"""
    records = []
    for seed in ("1", "2", "3"):
        environment = os.environ.copy()
        environment["PYTHONHASHSEED"] = seed
        environment["PYTHONPATH"] = os.pathsep.join((str(repository / "src"), str(repository)))
        result = subprocess.run(
            [sys.executable, "-c", probe], cwd=repository, env=environment,
            text=True, capture_output=True, check=True, timeout=30,
        )
        records.append(json.loads(result.stdout))
    assert records[0] == records[1] == records[2]
    assert records[0][1] == ["stop", "flush", "close"]
