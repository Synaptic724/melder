"""
Cross-root differential for `unique_per_conduit_lineage` over the BORROW path.

This is the test the single-root smoke test could not be: it distinguishes
root_creations from owner_creations. Two independent roots (owner + borrower)
linked by a contract resolve the SAME bound service spell. The owner owns it;
the borrower borrows it across the link.

Expectation under resolver-root lineage semantics:
    - `unique` service: the borrowed provider is the owner's single instance, so
      owner.meld(service) IS borrower's borrowed service  (control: shows the
      borrow path normally collapses to one shared instance).
    - `unique_per_conduit_lineage` service: each root instantiates its OWN
      instance in its own lineage-root store, so owner's instance is NOT the
      borrower's borrowed instance  (the feature).

If the lineage case shows `is` (same object), the borrow path still collapses to
the owner store and needs the borrower's root_creations threaded into borrowed
resolution. If the `unique` control ALSO shows `is not`, the two books are in
separate frames and this differential is confounded (redesign needed).

Run (on the 3.14t target):
    .venv_new\\Scripts\\python.exe -m pytest tests/experimentation/test_lineage_borrow_isolation.py -q
"""

import sys
from pathlib import Path
from typing import Any, Tuple


def _ensure_src_on_path() -> None:
    src_dir = Path(__file__).resolve().parents[2] / "src"
    src_as_str = str(src_dir)
    if src_as_str not in sys.path:
        sys.path.insert(0, src_as_str)


_ensure_src_on_path()

import pytest  # noqa: E402

from melder.aether.aether import Aether  # noqa: E402
from melder.aether.conduit.conduit import Conduit  # noqa: E402
from melder.aether.spellbook.configuration.spellbook_configuration import (  # noqa: E402
    SpellbookConfiguration,
)
from melder.aether.spellbook.existence.existence import Existence  # noqa: E402
from melder.aether.spellbook.spellbook import Spellbook  # noqa: E402
from tests._frame_posture_test_support import (  # noqa: E402
    apply_dynamic_defaults_for_spellbook_configuration,
)
from tests.mocks.spellbook.contract_classes import (  # noqa: E402
    ContractConsumerExplicitSpellUpper,
    ContractConsumerOverrideList,
    ContractServicePrimary,
)
from tests.mocks.spellbook.protocols import IService  # noqa: E402


@pytest.fixture(autouse=True)
def _reset_aether_singleton() -> Any:
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether
    yield
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether


def _make_dynamic_configuration() -> SpellbookConfiguration:
    configuration = SpellbookConfiguration()
    apply_dynamic_defaults_for_spellbook_configuration(configuration)
    configuration.set_property("phase_scheduler_workers_per_spellbook", 1)
    return configuration


def _resolve_owner_and_borrower_service(existence: Existence) -> Tuple[Any, Any]:
    """
    Conjure an owner (which owns `service`) and a borrower (which borrows it via
    a link contract). Return (owner_service_instance, borrower_service_instance)
    where the borrower's instance is resolved through its consumer's socket.
    """
    configuration = _make_dynamic_configuration()
    owner_book = Spellbook(configuration=configuration)
    service_id = owner_book.bind(
        spell=ContractServicePrimary,
        existence=existence,
        permissions="create",
        binding_name="primary",
    )
    borrower_book = Spellbook(configuration=configuration)
    consumer_id = borrower_book.bind(
        spell=ContractConsumerExplicitSpellUpper,
        existence=Existence.unique,
        permissions="create",
    )

    owner = owner_book.conjure(dynamic=True, name="owner")
    borrower = borrower_book.conjure(dynamic=True, name="borrower")
    try:
        owner.link(borrower)
        with borrower.transaction("link", conduits=[borrower, owner]):
            assert borrower.add_spell_to_contract(
                spell_id=service_id,
                conduit=owner,
                permissions="create",
            )
        assert borrower.validate_contracts_and_define()

        owner_service = owner.meld(spell=service_id)
        borrower_instance = borrower.meld(spell=consumer_id)
        borrower_service = borrower_instance.service

        assert isinstance(owner_service, ContractServicePrimary)
        assert isinstance(borrower_service, ContractServicePrimary)
        return owner_service, borrower_service
    finally:
        borrower.cleanup()
        owner.cleanup()


def test_unique_service_is_shared_across_the_borrow_control() -> None:
    """
    Control: a `unique` borrowed provider collapses to one shared instance, so
    the owner's instance and the borrower's borrowed instance are the SAME object.
    (If this fails with `is not`, the two books are in separate frames and the
    lineage differential below is confounded.)
    """
    owner_service, borrower_service = _resolve_owner_and_borrower_service(
        Existence.unique
    )
    assert owner_service is borrower_service, (
        "unique borrowed provider should be one shared instance across the link"
    )


def test_lineage_service_is_isolated_per_root_over_the_borrow() -> None:
    """
    The feature: a `unique_per_conduit_lineage` borrowed provider is instantiated
    once PER LINEAGE ROOT, so the owner root and the borrower root hold DISTINCT
    instances.
    """
    owner_service, borrower_service = _resolve_owner_and_borrower_service(
        Existence.unique_per_conduit_lineage
    )
    assert owner_service is not borrower_service, (
        "lineage borrowed provider must be a distinct instance in each root's "
        "lineage-root store (resolver-root semantics), not the owner's single "
        "shared instance"
    )


def test_lineage_borrowed_service_with_override_isolates_and_applies() -> None:
    """
    Override-path probe: a borrowed `unique_per_conduit_lineage` service that the
    borrower constructs WITH a list override. Two claims:
      - the override is applied to the borrower's instance (marker), and
      - the borrower's instance is isolated from the owner's plain instance.
    If the override compilers still bake `_owner_creations` for lineage (the
    no-overrides OWNER fix was not mirrored into the override lane), this collapses
    to the owner store and one or both assertions fail.
    """
    configuration = _make_dynamic_configuration()
    owner_book = Spellbook(configuration=configuration)
    service_id = owner_book.bind(
        spell=ContractServicePrimary,
        existence=Existence.unique_per_conduit_lineage,
        permissions="create",
        spellframe=IService,
        binding_name="primary",
    )
    borrower_book = Spellbook(configuration=configuration)
    consumer_id = borrower_book.bind(
        spell=ContractConsumerOverrideList,
        existence=Existence.unique,
        permissions="create",
    )

    owner = owner_book.conjure(dynamic=True, name="owner")
    borrower = borrower_book.conjure(dynamic=True, name="borrower")
    try:
        owner.link(borrower)
        with borrower.transaction("link", conduits=[borrower, owner]):
            assert borrower.add_spell_to_contract(
                spell_id=service_id,
                conduit=owner,
                permissions="create",
            )
        assert borrower.validate_contracts_and_define()

        owner_service = owner.meld(spell=service_id)
        borrower_instance = borrower.meld(spell=consumer_id)
        borrower_service = borrower_instance.service

        assert isinstance(borrower_service, ContractServicePrimary)
        assert borrower_service.marker == "override-list", (
            "list override must apply to the borrower's constructed lineage service"
        )
        assert owner_service is not borrower_service, (
            "overridden borrowed lineage service must be a distinct per-root "
            "instance, not the owner's shared one"
        )
        assert getattr(owner_service, "marker", None) != "override-list", (
            "owner's plain instance must not carry the borrower's override"
        )
    finally:
        borrower.cleanup()
        owner.cleanup()


def test_lineage_meldtime_override_caches_in_borrower_root_not_owner() -> None:
    """
    Meld-time `spell_override` probe (the override EXECUTOR lane, not the contract
    override path). Borrower borrows a lineage service and melds it directly with a
    meld-time override. The constructed instance must live in the BORROWER's
    lineage-root store, so:
      - a subsequent PLAIN re-meld on the borrower reuses it (same object), and
      - the owner's store is NOT polluted (owner's plain meld keeps its own marker).
    Under the unfixed override emitter (bakes `_owner_creations`), the instance is
    stored in the OWNER store instead: the borrower's plain re-meld misses and
    rebuilds (b2 is not b1), and the owner sees the borrower's overridden instance.
    """
    configuration = _make_dynamic_configuration()
    owner_book = Spellbook(configuration=configuration)
    service_id = owner_book.bind(
        spell=ContractServicePrimary,
        existence=Existence.unique_per_conduit_lineage,
        permissions="create",
        binding_name="primary",
    )
    borrower_book = Spellbook(configuration=configuration)
    # Borrower needs at least one own binding to conjure a real root.
    borrower_book.bind(
        spell=ContractConsumerExplicitSpellUpper,
        existence=Existence.unique,
        permissions="create",
    )

    owner = owner_book.conjure(dynamic=True, name="owner")
    borrower = borrower_book.conjure(dynamic=True, name="borrower")
    try:
        owner.link(borrower)
        with borrower.transaction("link", conduits=[borrower, owner]):
            assert borrower.add_spell_to_contract(
                spell_id=service_id,
                conduit=owner,
                permissions="create",
            )
        assert borrower.validate_contracts_and_define()

        b1 = borrower.meld(spell=service_id, spell_override={"marker": "meld-override"})
        assert b1.marker == "meld-override"

        b2 = borrower.meld(spell=service_id)
        assert b2 is b1, (
            "meld-time override instance must be cached in the borrower's "
            "lineage-root store (so the plain re-meld reuses it)"
        )

        owner_service = owner.meld(spell=service_id)
        assert owner_service is not b1, "owner store must not hold the borrower's instance"
        assert owner_service.marker == "contract-primary", (
            "owner's lineage instance must not be polluted by the borrower's override"
        )
    finally:
        borrower.cleanup()
        owner.cleanup()


if __name__ == "__main__":
    # Minimal manual driver (pytest fixture not applied here; reset by hand).
    Aether._reset_singleton_for_tests()
    _a = Aether()
    Spellbook._aether = _a
    Conduit._aether = _a
    o1, b1 = _resolve_owner_and_borrower_service(Existence.unique)
    print("unique:  owner is borrower ->", o1 is b1, "(expect True)")
    Aether._reset_singleton_for_tests()
    _a = Aether()
    Spellbook._aether = _a
    Conduit._aether = _a
    o2, b2 = _resolve_owner_and_borrower_service(Existence.unique_per_conduit_lineage)
    print("lineage: owner is borrower ->", o2 is b2, "(expect False)")
