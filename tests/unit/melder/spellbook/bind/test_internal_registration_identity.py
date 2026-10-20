"""
Characterization tests for the internal-registration guard's identity rule (core-protection review,
2026-10-10).

Purpose:
    The guard refuses to register Melder's own classes as spells. A protected core or a fork of it
    depends on what that guard actually keys on, so these tests pin it: the identity is the exact
    `(module, qualname)` string pair of the class (an instance answers through its type), with no
    inheritance and no object identity, and every entry the build asset records is rooted at the
    `melder` package. A fork published under another top-level package name is therefore outside the
    guard, and a user class that claims a Melder identity is refused. These describe today's rule;
    they do not decide the review's fork questions.

Runs only on 3.14t (melder package root import chain).
"""
from typing import Iterator

import pytest

from melder._build_assets._bind_guard.bind_guard import INTERNAL_MANIFEST
from melder.aether.aether import Aether
from melder.aether.aether_utility_system import AetherUtilitySystem
from melder.aether.spellbook.bind.bind import assert_allowed
from melder.aether.spellbook.spellbook import Spellbook
from melder.nexus.nexus import Nexus
from melder.utilities.custom_exceptions.internal_registration_error import InternalRegistrationError


def _boot_fresh_aether() -> None:
    """
    Reset the runtime singletons and bind a freshly booted Aether to `Spellbook._aether`.

    Returns:
        None.
    """
    AetherUtilitySystem._reset_singleton_for_tests()
    Nexus._reset_singleton_for_tests()
    Aether._reset_singleton_for_tests()
    Spellbook._aether = Aether()


@pytest.fixture(autouse=True)
def live_aether() -> Iterator[None]:
    """
    Run each test against a freshly booted Aether, and leave one behind.

    Yields:
        None.
    """
    _boot_fresh_aether()
    yield
    _boot_fresh_aether()


@pytest.fixture()
def spellbook() -> Iterator[Spellbook]:
    """
    Provide one default Spellbook and clean it after the test.

    Yields:
        Spellbook: A fresh book on the default frame.
    """
    book = Spellbook()
    try:
        yield book
    finally:
        book.cleanup()


def test_a_user_subclass_of_an_internal_class_registers_normally(spellbook: Spellbook) -> None:
    """
    Contract: the guard does not walk the MRO - a user subclass of a guarded Melder class carries
    its own module and qualname and registers like any user class.
    """
    base_identity = (InternalRegistrationError.__module__, InternalRegistrationError.__qualname__)
    assert base_identity in INTERNAL_MANIFEST

    class UserRefusal(InternalRegistrationError):
        """A user-owned subclass of a guarded Melder exception."""

    spell_id = spellbook.bind(spell=UserRefusal, existence="unique")

    assert spellbook.find_spell_by_spell_id(spell_id).spell is UserRefusal


def test_an_instance_of_an_internal_class_is_refused_like_the_class(spellbook: Spellbook) -> None:
    """
    Contract: an instance answers through its type, so registering an existing object of a guarded
    class is refused with the same error as the class - while the object itself stays usable
    (the guard restricts registration, never use).
    """
    guarded_instance = InternalRegistrationError("constructed and usable")

    with pytest.raises(InternalRegistrationError, match="type=InternalRegistrationError"):
        spellbook.bind(spell=guarded_instance, existence="unique")

    assert str(guarded_instance) == "constructed and usable"
    assert len(spellbook.spells) == 0


def test_a_forked_identity_outside_the_melder_package_is_not_guarded(spellbook: Spellbook) -> None:
    """
    Contract: the guard compares strings, not objects. A class named like `Aether` but defined in
    another top-level package (how a renamed fork would publish it) is absent from the manifest,
    passes the guard and registers.
    """
    forked_aether = type("Aether", (), {"__module__": "melder_fork.aether.aether"})
    assert (forked_aether.__module__, forked_aether.__qualname__) not in INTERNAL_MANIFEST

    assert_allowed(forked_aether, context="bind")
    spell_id = spellbook.bind(spell=forked_aether, existence="unique")

    assert spellbook.find_spell_by_spell_id(spell_id).spell is forked_aether


def test_a_user_class_claiming_a_melder_identity_is_refused(spellbook: Spellbook) -> None:
    """
    Contract: the converse of the forked identity - a user class whose module and qualname match a
    manifest entry is refused although it is not Melder's class.
    """
    impostor = type("Aether", (), {"__module__": Aether.__module__})
    assert impostor is not Aether

    with pytest.raises(InternalRegistrationError, match="type=Aether"):
        spellbook.bind(spell=impostor, existence="unique")

    assert len(spellbook.spells) == 0


def test_every_manifest_entry_is_rooted_at_the_melder_package() -> None:
    """
    Contract: the build asset names every guarded class under the `melder` package, so the guard
    covers exactly the classes importable as `melder.*` when the manifest was last rebuilt.
    """
    modules = {module_name for module_name, _qualname in INTERNAL_MANIFEST}

    assert modules
    assert all(
        module_name == "melder" or module_name.startswith("melder.")
        for module_name in modules
    )
