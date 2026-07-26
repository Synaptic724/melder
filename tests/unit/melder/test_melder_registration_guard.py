"""
Unit tests for internal registration guard manifest membership and bind refusal.

Contract:
- Internal Melder classes exist in `INTERNAL_MANIFEST`.
- User classes are not in `INTERNAL_MANIFEST`.
- Attempting to bind a Melder internal class raises `InternalRegistrationError`.
"""

import pytest

from melder._build_assets._init_metadata.init_metadata import INTERNAL_MANIFEST
from melder.aether.aether import Aether
from melder.aether.spellbook.spellbook import Spellbook
from melder.utilities.custom_exceptions.internal_registration_error import InternalRegistrationError


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
