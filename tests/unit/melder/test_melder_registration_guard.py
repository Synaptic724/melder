"""
Unit tests for internal registration guard manifest membership and bind refusal.

Contract:
- Internal Melder classes exist in `INTERNAL_MANIFEST`.
- User classes are not in `INTERNAL_MANIFEST`.
- Attempting to bind a Melder internal class raises `InternalRegistrationError`.
"""

from typing import Iterator

import pytest

from melder._build_assets._bind_guard.bind_guard import INTERNAL_MANIFEST
from melder.aether.aether import Aether
from melder.aether.aether_utility_system import AetherUtilitySystem
from melder.aether.spellbook.spellbook import Spellbook
from melder.nexus.nexus import Nexus
from melder.utilities.custom_exceptions.internal_registration_error import InternalRegistrationError


def _boot_fresh_aether() -> None:
    """Reset the runtime singletons, boot a new Aether and bind it to `Spellbook._aether`."""
    AetherUtilitySystem._reset_singleton_for_tests()
    Nexus._reset_singleton_for_tests()
    Aether._reset_singleton_for_tests()
    Spellbook._aether = Aether()


@pytest.fixture(autouse=True)
def live_aether() -> Iterator[None]:
    """
    Run each test against a freshly booted Aether, and leave one behind.

    Purpose:
        `test_bind_rejects_internal_class` builds a Spellbook, which needs the Nexus an Aether boot
        constructs. Without its own setup the test passed only when the test before it left a live
        Aether, and failed after tests whose teardown reset the singletons without booting a new one.

    Yields:
        None.
    """
    _boot_fresh_aether()
    yield
    _boot_fresh_aether()


def test_internal_manifest_contains_aether() -> None:
    target_cls = Aether
    key = (target_cls.__module__, target_cls.__qualname__)
    assert key in INTERNAL_MANIFEST


def test_internal_manifest_does_not_contain_user_class() -> None:
    class UserClass:
        pass

    key = (UserClass.__module__, UserClass.__qualname__)
    assert key not in INTERNAL_MANIFEST


def test_bind_rejects_internal_class() -> None:
    spellbook = Spellbook()
    with pytest.raises(InternalRegistrationError) as excinfo:
        spellbook.bind(spell=Aether, existence="unique")

    msg = str(excinfo.value)
    assert "Registration blocked" in msg
    assert "type=Aether" in msg
