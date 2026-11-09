"""Real transaction regressions for exact-name DevOps enum values."""

from collections.abc import Generator
from enum import StrEnum
from typing import Union

import pytest

from melder.aether.aether import Aether
from melder.aether.aetheric_frame.dev_ops.change_control_manager.transaction_request.transaction_request import (
    ChangeTransactionType,
)
from melder.aether.conduit.conduit import Conduit
from melder.aether.spellbook.configuration.spellbook_configuration import SpellbookConfiguration
from melder.aether.spellbook.spellbook import Spellbook
from tests._frame_posture_test_support import (
    apply_automatic_defaults_for_spellbook_configuration,
    apply_dynamic_defaults_for_spellbook_configuration,
)
from tests.mocks.spellbook.core_classes import BasicService


@pytest.fixture(autouse=True)
def isolated_world() -> Generator[None, None, None]:
    """Give each test its own in-process Aether and retire it afterward."""
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether
    yield
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether


def make_book(*, dynamic: bool) -> Spellbook:
    """Build a book with the requested frame posture and filesystem caching off."""
    configuration = SpellbookConfiguration()
    if dynamic:
        apply_dynamic_defaults_for_spellbook_configuration(configuration)
    else:
        apply_automatic_defaults_for_spellbook_configuration(configuration)
    configuration.set_property("phase_scheduler_workers_per_spellbook", 1)
    book = Spellbook(configuration=configuration)
    book._aetheric_frame_configuration.with_system_caching_enabled(False)
    return book


def test_legacy_bind_commits_and_closes_its_window() -> None:
    """A normal bind must not fail after registering its spell on transaction close."""
    book = make_book(dynamic=True)
    try:
        spell_id = book.bind(spell=BasicService, existence="unique")
        assert book.find_spell_by_spell_id(spell_id) is not None
        assert book._get_required_transaction_mediator().get_active_request() is None
    finally:
        book.cleanup()


@pytest.mark.parametrize(
    ("begin_type", "end_type"),
    (
        ("bind", "bind"),
        ("bind", "BIND"),
        ("BIND", "bind"),
        (ChangeTransactionType.BIND, "bind"),
        ("bind", ChangeTransactionType.BIND),
        (ChangeTransactionType.BIND, ChangeTransactionType.BIND),
    ),
)
def test_spellbook_binding_window_accepts_equivalent_forms(
        begin_type: Union[str, ChangeTransactionType],
        end_type: Union[str, ChangeTransactionType],
) -> None:
    """A nested bind closes cleanly when entry and exit name the same kind."""
    book = make_book(dynamic=True)
    mediator = book._get_required_transaction_mediator()
    try:
        book.begin_transaction(begin_type)
        spell_id = book.bind(spell=BasicService, existence="unique")
        assert book.find_spell_by_spell_id(spell_id) is not None
        book.end_transaction(end_type)
        assert mediator.get_active_request() is None
    finally:
        if mediator.get_active_request() is not None:
            mediator.end_transaction(success=False)
        book.cleanup()


def test_spellbook_rejects_a_different_close_kind_without_releasing_bind() -> None:
    """A mismatched close leaves the actual bind window available to its owner."""
    book = make_book(dynamic=True)
    mediator = book._get_required_transaction_mediator()
    try:
        book.begin_transaction("bind")
        with pytest.raises(RuntimeError, match="does not match"):
            book.end_transaction("LINK")
        assert mediator.get_active_request() is not None
        book.end_transaction("BIND")
        assert mediator.get_active_request() is None
    finally:
        if mediator.get_active_request() is not None:
            mediator.end_transaction(success=False)
        book.cleanup()


@pytest.mark.parametrize("kind", ("link", "LINK", ChangeTransactionType.LINK))
def test_link_window_accepts_contract_mutation_for_each_form(
        kind: Union[str, ChangeTransactionType],
) -> None:
    """A link window admits an actual contract grant and keeps its peer scope."""
    owner_book = make_book(dynamic=True)
    borrower_book = make_book(dynamic=True)
    spell_id = owner_book.bind(spell=BasicService, existence="unique")
    owner = owner_book.conjure(dynamic=True, name="owner")
    borrower = borrower_book.conjure(dynamic=True, name="borrower")
    try:
        assert owner.link(borrower)
        with borrower.transaction(kind, conduits=[borrower, owner]):
            assert borrower.add_spell_to_contract(spell_id=spell_id, conduit=owner) is True
        inbound = borrower.get_spells_in_contract_by_conduit(owner.id)["inbound"]
        assert spell_id in [contracted_id for contracted_id, _ in inbound]
    finally:
        borrower.cleanup()
        owner.cleanup()


@pytest.mark.parametrize(
    ("flag_name", "member"),
    (
        ("disable_bind", ChangeTransactionType.BIND),
        ("disable_linking", ChangeTransactionType.LINK),
        ("disable_transfer_of_ownership", ChangeTransactionType.TRANSFER_OWNERSHIP),
        ("disable_conduit_cluster", ChangeTransactionType.CLUSTER_LINK),
        ("disable_mutations", ChangeTransactionType.MUTATION),
    ),
)
@pytest.mark.parametrize("form", ("legacy", "canonical", "member"))
def test_disabled_transaction_is_refused_for_every_named_form(
        flag_name: str,
        member: ChangeTransactionType,
        form: str,
) -> None:
    """Frame disable flags cannot be bypassed by choosing another string form."""
    book = make_book(dynamic=True)
    getattr(book._aetheric_frame_configuration, f"with_{flag_name}")(True)
    conduit = book.conjure(dynamic=True, name="root")
    mediator = book._get_required_transaction_mediator()
    kind = member.wire_value if form == "legacy" else member.name if form == "canonical" else member
    try:
        with pytest.raises(RuntimeError, match="disabled"):
            conduit.begin_transaction(kind)
        assert mediator.get_active_request() is None
    finally:
        if mediator.get_active_request() is not None:
            mediator.end_transaction(success=False)
        conduit.cleanup()


@pytest.mark.parametrize("kind", ("link", "LINK", ChangeTransactionType.LINK))
def test_automatic_frame_rejects_all_link_forms(
        kind: Union[str, ChangeTransactionType],
) -> None:
    """A named link request cannot bypass automatic-frame admission."""
    book = make_book(dynamic=False)
    conduit = book.conjure(name="root")
    mediator = book._get_required_transaction_mediator()
    try:
        with pytest.raises(RuntimeError, match="dynamic mode"):
            conduit.begin_transaction(kind)
        assert mediator.get_active_request() is None
    finally:
        if mediator.get_active_request() is not None:
            mediator.end_transaction(success=False)
        conduit.cleanup()


class ForeignTransaction(StrEnum):
    """Foreign values used to verify the comparison boundary keeps their identity."""

    CANONICAL = "BIND"
    LEGACY = "bind"


@pytest.mark.parametrize("member", tuple(ChangeTransactionType))
def test_comparison_projection_keeps_exact_enum_equality_and_hash(member: ChangeTransactionType) -> None:
    """Every member keeps its exact value while known forms compare by the old token."""
    assert member.value == member.name
    assert member == member.name
    assert hash(member) == hash(member.name)
    assert ChangeTransactionType._comparison_token(member) == member.name.lower()
    assert ChangeTransactionType._comparison_token(member.name) == member.name.lower()
    assert ChangeTransactionType._comparison_token(member.name.lower()) == member.name.lower()


@pytest.mark.parametrize("value", ("Bind", " bind ", "unknown", "", None))
def test_comparison_projection_leaves_unrecognized_inputs_unchanged(value: object) -> None:
    """Other spellings are not silently normalized by the compatibility boundary."""
    assert ChangeTransactionType._comparison_token(value) is value


def test_comparison_projection_does_not_coerce_foreign_enum_members() -> None:
    """Foreign members remain themselves, including their old string equality."""
    assert ChangeTransactionType._comparison_token(ForeignTransaction.CANONICAL) is ForeignTransaction.CANONICAL
    assert ChangeTransactionType._comparison_token(ForeignTransaction.LEGACY) is ForeignTransaction.LEGACY
    assert ForeignTransaction.LEGACY == "bind"
