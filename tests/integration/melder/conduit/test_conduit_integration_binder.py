from __future__ import annotations

import pytest

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.spellbook.existence.existence import Existence
from melder.spellbook.spellbook import Spellbook
from tests.mocks.spellbook.core_classes import BasicConfig
from tests.mocks.spellbook.core_classes import BasicLogger
from tests.mocks.spellbook.core_classes import BasicService


@pytest.fixture(autouse=True)
def reset_aether_singleton_for_integration() -> None:
    """
    Purpose:
        Ensure integration tests start with a clean Aether singleton.
    Contract:
        - Resets the Aether singleton before the test runs.
        - Rebinds Spellbook._aether and Conduit._aether to the new instance.
        - Resets the singleton again after the test for isolation.
    Returns:
        None.
    """
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether
    yield
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether


def test_conduit_binder_finalize_requires_bind() -> None:
    """
    Purpose:
        Validate Conduit binder requires an active bind before finalize.
    Contract:
        - finalize without bind raises RuntimeError.
    Returns:
        None.
    Raises:
        AssertionError: If finalize succeeds without a bind.
    """
    spellbook = Spellbook()
    config = spellbook.get_configuration()
    config.set_property("phase_scheduler_workers_per_spellbook", 1)
    spellbook.bind(
        spell=BasicService,
        existence=Existence.unique,
        permissions="create",
    )

    conduit = spellbook.conjure(name="root")
    try:
        binder = conduit.create_binder()
        with pytest.raises(RuntimeError, match="no active spell"):
            binder.finalize()
    finally:
        conduit.cleanup()


def test_conduit_binder_reuse_and_named_binding() -> None:
    """
    Purpose:
        Validate Conduit binder reuse and named bindings.
    Contract:
        - The binder can register multiple spells sequentially.
        - named bindings resolve via find_spell_id.
        - inspect_spell returns the registered ids.
    Returns:
        None.
    Raises:
        AssertionError: If binder reuse or lookups fail.
    """
    spellbook = Spellbook()
    config = spellbook.get_configuration()
    config.set_property("phase_scheduler_workers_per_spellbook", 1)
    spellbook.bind(
        spell=BasicService,
        existence=Existence.unique,
        permissions="create",
    )

    conduit = spellbook.conjure(name="root")
    try:
        binder = conduit.create_binder()
        config_id = binder.bind(BasicConfig).named("primary").finalize()
        logger_id = binder.bind(BasicLogger).as_unique().finalize()

        resolved_id = conduit.find_spell_id("BasicConfig", BasicConfig.__name__, "primary")
        assert resolved_id == config_id
        assert conduit.inspect_spell(BasicConfig) == config_id
        assert conduit.inspect_spell(BasicLogger) == logger_id
    finally:
        conduit.cleanup()


def test_conduit_binder_cleanup_blocks_usage() -> None:
    """
    Purpose:
        Validate Conduit binder cleanup blocks further use.
    Contract:
        - bind after cleanup raises RuntimeError.
    Returns:
        None.
    Raises:
        AssertionError: If bind succeeds after cleanup.
    """
    spellbook = Spellbook()
    config = spellbook.get_configuration()
    config.set_property("phase_scheduler_workers_per_spellbook", 1)
    spellbook.bind(
        spell=BasicService,
        existence=Existence.unique,
        permissions="create",
    )

    conduit = spellbook.conjure(name="root")
    try:
        binder = conduit.create_binder()
        binder.cleanup()
        with pytest.raises(RuntimeError, match="cleaned"):
            binder.bind(BasicConfig)
    finally:
        conduit.cleanup()


def test_conduit_binder_defaults_apply_permissions_and_existence() -> None:
    """
    Purpose:
        Validate Conduit binder defaults apply to existence and permissions.
    Contract:
        - default_existence governs the binding when no overrides are set.
        - default_permissions persists to get_spell_permissions.
    Returns:
        None.
    Raises:
        AssertionError: If defaults are ignored.
    """
    spellbook = Spellbook()
    config = spellbook.get_configuration()
    config.set_property("phase_scheduler_workers_per_spellbook", 1)
    spellbook.bind(
        spell=BasicService,
        existence=Existence.unique,
        permissions="create",
    )

    conduit = spellbook.conjure(name="root")
    try:
        binder = conduit.create_binder(
            default_existence=Existence.many,
            default_permissions="read",
        )
        spell_id = binder.bind(BasicConfig).finalize()

        first = conduit.meld(spell=spell_id)
        second = conduit.meld(spell=spell_id)
        assert first is not second
        assert conduit.get_spell_permissions(spell_id) == "read"
    finally:
        conduit.cleanup()
