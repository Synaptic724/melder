from __future__ import annotations

from melder import SpellBinder
import pytest

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spellbook import Spellbook
from tests.mocks.spellbook.core_classes import BasicConfig
from tests.mocks.spellbook.core_classes import BasicLogger
from tests.mocks.spellbook.core_classes import BasicService
from tests.mocks.spellbook.protocols import IService
from tests._frame_posture_test_support import (
    apply_dynamic_defaults_for_spellbook_configuration,
)


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
    apply_dynamic_defaults_for_spellbook_configuration(config)
    config.set_property("phase_scheduler_workers_per_spellbook", 1)
    spellbook.bind(
        spell=BasicService,
        existence=Existence.unique,
        permissions="create",
    )

    conduit = spellbook.conjure(name="root")
    try:
        binder = SpellBinder(conduit._spellbook, )
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
    apply_dynamic_defaults_for_spellbook_configuration(config)
    config.set_property("phase_scheduler_workers_per_spellbook", 1)
    spellbook.bind(
        spell=BasicService,
        existence=Existence.unique,
        permissions="create",
    )

    conduit = spellbook.conjure(name="root")
    try:
        binder = SpellBinder(conduit._spellbook, )
        with spellbook.transaction("bind"):
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
    apply_dynamic_defaults_for_spellbook_configuration(config)
    config.set_property("phase_scheduler_workers_per_spellbook", 1)
    spellbook.bind(
        spell=BasicService,
        existence=Existence.unique,
        permissions="create",
    )

    conduit = spellbook.conjure(name="root")
    try:
        binder = SpellBinder(conduit._spellbook, )
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
    apply_dynamic_defaults_for_spellbook_configuration(config)
    config.set_property("phase_scheduler_workers_per_spellbook", 1)
    spellbook.bind(
        spell=BasicService,
        existence=Existence.unique,
        permissions="create",
    )

    conduit = spellbook.conjure(name="root")
    try:
        binder = SpellBinder(conduit._spellbook, 
            default_existence=Existence.many,
            default_permissions="read",
        )
        with spellbook.transaction("bind"):
            spell_id = binder.bind(BasicConfig).finalize()

        first = conduit.meld(spell=spell_id)
        second = conduit.meld(spell=spell_id)
        assert first is not second
        assert conduit.get_spell_permissions(spell_id) == "read"
    finally:
        conduit.cleanup()


def test_conduit_binder_named_spellframe_resolution_and_lookup() -> None:
    """
    Purpose:
        Validate Conduit binder resolves by spellframe and binding name.
    Contract:
        - Fluent binder registers under a protocol + binding name.
        - Conduit.meld resolves using spellframe/binding_name.
        - Conduit.find_spell_id and inspect_spell return the registered id.
    Returns:
        None.
    Raises:
        AssertionError: If resolution or lookups fail.
    """
    spellbook = Spellbook()
    config = spellbook.get_configuration()
    apply_dynamic_defaults_for_spellbook_configuration(config)
    config.set_property("phase_scheduler_workers_per_spellbook", 1)
    spellbook.bind(
        spell=BasicLogger,
        existence=Existence.unique,
        permissions="create",
    )

    conduit = spellbook.conjure(name="root")
    try:
        binder = SpellBinder(conduit._spellbook, )
        with conduit.transaction("bind"):
            spell_id = (
                binder.bind(BasicService)
                .under_spellframe(IService)
                .named("primary")
                .with_permissions("create")
                .finalize()
            )

        resolved = conduit.meld(spellframe=IService, binding_name="primary")
        assert isinstance(resolved, BasicService)
        assert conduit.meld(spell=spell_id) is resolved

        resolved_id = conduit.find_spell_id(IService, BasicService.__name__, "primary")
        assert resolved_id == spell_id
        assert conduit.inspect_spell(BasicService) == spell_id
    finally:
        conduit.cleanup()


def test_conduit_binder_hooks_execute_in_order() -> None:
    """
    Purpose:
        Validate Conduit binder hook ordering executes through meld.
    Contract:
        - pre hooks run before activation and post hooks.
        - activation hooks run once for unique spells.
        - post hooks run after activation for initial creation.
    Returns:
        None.
    Raises:
        AssertionError: If hook ordering or counts are incorrect.
    """
    events: list[str] = []

    def pre_hook() -> None:
        """
        Purpose:
            Record pre-hook execution.
        Contract:
            Appends "pre" to events.
        Returns:
            None.
        """
        events.append("pre")

    def activation_hook(instance: object) -> None:
        """
        Purpose:
            Record activation hook execution.
        Contract:
            Appends "activation" to events.
        Args:
            instance: The created instance.
        Returns:
            None.
        """
        events.append("activation")

    def post_hook() -> None:
        """
        Purpose:
            Record post-hook execution.
        Contract:
            Appends "post" to events.
        Returns:
            None.
        """
        events.append("post")

    spellbook = Spellbook()
    config = spellbook.get_configuration()
    apply_dynamic_defaults_for_spellbook_configuration(config)
    config.set_property("phase_scheduler_workers_per_spellbook", 1)
    spellbook.bind(
        spell=BasicLogger,
        existence=Existence.unique,
        permissions="create",
    )

    conduit = spellbook.conjure(name="root")
    try:
        with spellbook.transaction("bind"):
            spell_id = (
                SpellBinder(conduit._spellbook, )
                .bind(BasicService)
                .as_unique()
                .with_pre_hook(pre_hook)
                .with_activation_hook(activation_hook)
                .with_post_hook(post_hook)
                .finalize()
            )

        first = conduit.meld(spell=spell_id)
        second = conduit.meld(spell=spell_id)
        assert first is second
        assert events == ["pre", "activation", "post", "pre", "post"]
    finally:
        conduit.cleanup()

