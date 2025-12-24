from __future__ import annotations

import pytest

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.spellbook.configuration.configuration import Configuration
from melder.spellbook.existence.existence import Existence
from melder.spellbook.spellbook import Spellbook
from tests.mocks.spellbook.core_classes import BasicConfig
from tests.mocks.spellbook.core_classes import BasicService
from tests.mocks.spellbook.protocols import IService


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


def test_spellbook_integration_config_shared_and_locked() -> None:
    """
    Purpose:
        Validate configuration sharing and locking across Spellbooks in a frame.
    Contract:
        - Conjuring a Spellbook freezes and binds the configuration.
        - A second Spellbook in the same frame adopts the same configuration.
        - Frozen configuration rejects mutation attempts.
    Returns:
        None.
    Raises:
        AssertionError: If configuration sharing or locking fails.
    """
    spellbook = Spellbook(aetheric_frame="shared-frame")
    config = spellbook.get_configuration()
    config.set_property("phase_scheduler_workers_per_spellbook", 1)
    spell_id = spellbook.bind(
        spell=BasicService,
        existence=Existence.unique,
        permissions="create",
    )

    conduit = spellbook.conjure(name="root")
    try:
        assert spellbook.is_configuration_locked() is True

        sibling = Spellbook(aetheric_frame="shared-frame")
        sibling_config = sibling.get_configuration()
        assert sibling_config is config
        assert sibling.is_configuration_locked() is True

        with pytest.raises(RuntimeError, match="frozen"):
            sibling_config.set_property("phase_scheduler_workers_per_spellbook", 2)

        instance = conduit.meld(spell=spell_id)
        assert isinstance(instance, BasicService)
    finally:
        conduit.cleanup()


def test_spellbook_integration_create_new_preset_spellbook_shares_config() -> None:
    """
    Purpose:
        Validate preset Spellbook creation preserves frame and configuration.
    Contract:
        - Preset Spellbook reuses the existing configuration object.
        - Preset Spellbook can bind and conjure distinct spells.
    Returns:
        None.
    Raises:
        AssertionError: If preset Spellbook integration fails.
    """
    spellbook = Spellbook(aetheric_frame="preset-frame")
    config = spellbook.get_configuration()
    config.set_property("phase_scheduler_workers_per_spellbook", 1)
    spellbook.bind(
        spell=BasicService,
        existence=Existence.unique,
        permissions="create",
    )

    preset = spellbook.create_new_preset_spellbook()
    assert preset.get_configuration() is config

    preset_spell_id = preset.bind(
        spell=BasicConfig,
        existence=Existence.unique,
        permissions="create",
    )

    conduit = preset.conjure(name="preset-root")
    try:
        instance = conduit.meld(spell=preset_spell_id)
        assert isinstance(instance, BasicConfig)
    finally:
        conduit.cleanup()


def test_spellbook_integration_named_frames_isolated() -> None:
    """
    Purpose:
        Validate named Aetheric frames isolate spell registries.
    Contract:
        - Spells registered in frame A are not visible in frame B.
        - Spells registered in frame B are not visible in frame A.
    Returns:
        None.
    Raises:
        AssertionError: If spells leak across frames.
    """
    frame_a = "frame-a"
    frame_b = "frame-b"

    spellbook_a = Spellbook(aetheric_frame=frame_a)
    config_a = spellbook_a.get_configuration()
    config_a.set_property("phase_scheduler_workers_per_spellbook", 1)
    spell_id_a = spellbook_a.bind(
        spell=BasicService,
        existence=Existence.unique,
        permissions="create",
    )

    spellbook_b = Spellbook(aetheric_frame=frame_b)
    config_b = spellbook_b.get_configuration()
    config_b.set_property("phase_scheduler_workers_per_spellbook", 1)
    spell_id_b = spellbook_b.bind(
        spell=BasicConfig,
        existence=Existence.unique,
        permissions="create",
    )

    conduit_a = spellbook_a.conjure(name="root-a")
    conduit_b = spellbook_b.conjure(name="root-b")
    try:
        assert spellbook_a.inspect_spell(BasicService, aetheric_frame=frame_a) == spell_id_a
        assert spellbook_a.inspect_spell(BasicService, aetheric_frame=frame_b) is None

        assert spellbook_b.inspect_spell(BasicConfig, aetheric_frame=frame_b) == spell_id_b
        assert spellbook_b.inspect_spell(BasicConfig, aetheric_frame=frame_a) is None
    finally:
        conduit_b.cleanup()
        conduit_a.cleanup()


def test_spellbook_integration_frame_config_mismatch_raises() -> None:
    """
    Purpose:
        Validate conflicting configuration objects are rejected for a shared frame.
    Contract:
        - After a Spellbook binds configuration to a frame, a different
          configuration object for the same frame raises at initialization.
    Returns:
        None.
    Raises:
        AssertionError: If mismatched configuration is accepted.
    """
    frame = "frame-mismatch"
    spellbook = Spellbook(aetheric_frame=frame)
    config = spellbook.get_configuration()
    config.set_property("phase_scheduler_workers_per_spellbook", 1)
    spellbook.bind(
        spell=BasicService,
        existence=Existence.unique,
        permissions="create",
    )

    conduit = spellbook.conjure(name="root")
    try:
        other_config = Configuration(aether_frame=frame)
        other_config.set_property("phase_scheduler_workers_per_spellbook", 1)
        with pytest.raises(RuntimeError, match="Aether configuration does not match"):
            Spellbook(aetheric_frame=frame, configuration=other_config)
    finally:
        conduit.cleanup()


def test_spellbook_integration_conjure_registers_spell_versions_and_cleanup_clears_registry() -> None:
    """
    Purpose:
        Validate conjure registers spell versions into the Aether registry and cleanup clears them.
    Contract:
        - Conduit registration inserts SpellIndex entries into the frame spell registry.
        - The frame version registry contains the bound spell version id.
        - Conduit cleanup removes the version id from the frame registry.
    Returns:
        None.
    Raises:
        AssertionError: If registries are not updated as expected.
    """
    frame = "frame-registry"
    spellbook = Spellbook(aetheric_frame=frame)
    config = spellbook.get_configuration()
    config.set_property("phase_scheduler_workers_per_spellbook", 1)
    spell_id = spellbook.bind(
        spell=BasicService,
        existence=Existence.unique,
        permissions="create",
    )

    conduit = spellbook.conjure(name="root")
    conduit_id = conduit.id
    spell_indices = set(spellbook.spells.keys())
    try:
        aether = Spellbook._aether
        frame_obj = aether._aetheric_frames[frame]
        registry = frame_obj._spell_registry
        assert conduit_id in registry
        assert registry[conduit_id] == spell_indices
        assert frame_obj.has_version(spell_id) is True
    finally:
        conduit.cleanup()

    frame_obj = Spellbook._aether._aetheric_frames[frame]
    registry = frame_obj._spell_registry
    assert conduit_id in registry
    assert registry[conduit_id] == set()
    assert frame_obj.has_version(spell_id) is False


def test_spellbook_integration_conjure_uses_locked_configuration_from_aether() -> None:
    """
    Purpose:
        Validate conjure uses the Aether-locked configuration without redefinition.
    Contract:
        - Spellbook adopts the Aether configuration and remains locked.
        - Conjure succeeds using the locked configuration.
        - Aether retains the original configuration instance.
    Returns:
        None.
    Raises:
        AssertionError: If configuration locking or conjure behavior is incorrect.
    """
    frame = "frame-locked-config"
    aether = Spellbook._aether
    aether._ensure_frame(frame)
    config = Configuration(aether_frame=frame)
    config.with_defaults()
    config.set_property("phase_scheduler_workers_per_spellbook", 1)
    config.set_property("phase_scheduler_barrier_timeout_milliseconds", 60000)
    aether._bind_configuration(config, frame)

    spellbook = Spellbook(aetheric_frame=frame)
    spell_id = spellbook.bind(
        spell=BasicService,
        existence=Existence.unique,
        permissions="create",
    )

    conduit = spellbook.conjure(name="root")
    try:
        assert spellbook.is_configuration_locked() is True
        assert spellbook.get_configuration() is config
        assert Spellbook._aether._get_configuration(frame) is config
        instance = conduit.meld(spell=spell_id)
        assert isinstance(instance, BasicService)
    finally:
        conduit.cleanup()


def test_spellbook_integration_configuration_frame_mismatch_raises() -> None:
    """
    Purpose:
        Validate configuration frame mismatch is rejected at initialization.
    Contract:
        - A Configuration with a different aether_frame raises when passed in.
    Returns:
        None.
    Raises:
        AssertionError: If mismatched configuration is accepted.
    """
    config = Configuration(aether_frame="frame-x")
    config.set_property("phase_scheduler_workers_per_spellbook", 1)
    with pytest.raises(RuntimeError, match="aetheric frame"):
        Spellbook(aetheric_frame="frame-y", configuration=config)


def test_spellbook_integration_same_frame_bind_collision_raises() -> None:
    """
    Purpose:
        Validate bind rejects spell_id collisions within a shared frame.
    Contract:
        - After a spell is registered in a frame, a second Spellbook binding
          the same spell raises a collision error.
    Returns:
        None.
    Raises:
        AssertionError: If collision detection does not raise.
    """
    frame = "collision-frame"
    spellbook = Spellbook(aetheric_frame=frame)
    config = spellbook.get_configuration()
    config.set_property("phase_scheduler_workers_per_spellbook", 1)
    spellbook.bind(
        spell=BasicService,
        existence=Existence.unique,
        permissions="create",
    )

    conduit = spellbook.conjure(name="root")
    try:
        sibling = Spellbook(aetheric_frame=frame)
        with pytest.raises(RuntimeError, match="Spell ID collision detected"):
            sibling.bind(
                spell=BasicService,
                existence=Existence.unique,
                permissions="create",
            )
    finally:
        conduit.cleanup()


def test_spellbook_integration_existing_object_bind_after_conjure_reuses_instance() -> None:
    """
    Purpose:
        Validate binding an existing object after conjure reuses the instance.
    Contract:
        - Meld returns the same existing instance for the bound spell.
    Returns:
        None.
    Raises:
        AssertionError: If meld does not reuse the existing instance.
    """
    spellbook = Spellbook()
    config = spellbook.get_configuration()
    config.set_property("phase_scheduler_workers_per_spellbook", 1)

    conduit = spellbook.conjure(name="root")
    try:
        existing = BasicConfig(label="existing")
        spell_id = spellbook.bind(
            spell=existing,
            existence=Existence.unique,
            permissions="create",
        )
        resolved = conduit.meld(spell=spell_id)
        assert resolved is existing
    finally:
        conduit.cleanup()


def test_spellbook_integration_fluent_binding_resolves_by_spellframe_and_name() -> None:
    """
    Purpose:
        Validate fluent binding resolves by spellframe and binding name.
    Contract:
        - SpellBinder registers a spell under a protocol + binding name.
        - Conduit can meld using spellframe + binding_name resolution.
        - Spellbook lookups return a valid SpellIndex and key.
    Returns:
        None.
    Raises:
        AssertionError: If resolution or lookup fails.
    """
    spellbook = Spellbook()
    config = spellbook.get_configuration()
    config.set_property("phase_scheduler_workers_per_spellbook", 1)

    binder = spellbook.create_binder()
    binder.bind(BasicService).under_spellframe(IService).named("primary").with_permissions("create")
    spell_id = binder.finalize()

    conduit = spellbook.conjure(name="root")
    try:
        instance = conduit.meld(spellframe=IService, binding_name="primary")
        assert isinstance(instance, BasicService)

        spell_index = spellbook.find_spell_index(IService, BasicService.__name__, "primary")
        assert spellbook.get_spell_permissions(spell_index) == "create"

        spell_key = spellbook.find_spell_key(IService, BasicService.__name__, "primary")
        assert isinstance(spell_key, tuple)
        assert conduit.meld(spell=spell_id) is instance
    finally:
        conduit.cleanup()


def test_spellbook_integration_fluent_binding_case_insensitive_keys() -> None:
    """
    Purpose:
        Validate fluent binding resolution with case-insensitive keys.
    Contract:
        - spellframe and binding_name are normalized for lookup.
        - Spellbook lookup APIs resolve with mixed-case inputs.
    Returns:
        None.
    Raises:
        AssertionError: If resolution fails with mixed-case keys.
    """
    spellbook = Spellbook()
    config = spellbook.get_configuration()
    config.set_property("phase_scheduler_workers_per_spellbook", 1)

    binder = spellbook.create_binder()
    binder.bind(BasicService).under_spellframe(IService).named("Primary").with_permissions("create")
    spell_id = binder.finalize()

    conduit = spellbook.conjure(name="root")
    try:
        instance = conduit.meld(spellframe="ISERVICE", binding_name="PRIMARY")
        assert isinstance(instance, BasicService)

        spell_index = spellbook.find_spell_index("ISERVICE", BasicService.__name__, "PRIMARY")
        assert spellbook.get_spell_permissions(spell_index) == "create"

        spell_key = spellbook.find_spell_key("ISERVICE", BasicService.__name__, "PRIMARY")
        assert isinstance(spell_key, tuple)
        assert conduit.meld(spell=spell_id) is instance
    finally:
        conduit.cleanup()


def test_spellbook_integration_fluent_binding_hooks_execute() -> None:
    """
    Purpose:
        Validate fluent hook wiring executes through meld.
    Contract:
        - pre/post hooks run on each meld.
        - activation hooks run once for unique spells.
    Returns:
        None.
    Raises:
        AssertionError: If hook counts are incorrect.
    """
    pre_calls: list[str] = []
    post_calls: list[str] = []
    activation_calls: list[object] = []

    def pre_hook() -> None:
        """
        Purpose:
            Track pre-hook execution.
        Contract:
            Appends a marker to pre_calls.
        Returns:
            None.
        """
        pre_calls.append("pre")

    def post_hook() -> None:
        """
        Purpose:
            Track post-hook execution.
        Contract:
            Appends a marker to post_calls.
        Returns:
            None.
        """
        post_calls.append("post")

    def activation_hook(instance: object) -> None:
        """
        Purpose:
            Track activation hook execution.
        Contract:
            Appends the instance to activation_calls.
        Args:
            instance: Newly created instance.
        Returns:
            None.
        """
        activation_calls.append(instance)

    spellbook = Spellbook()
    config = spellbook.get_configuration()
    config.set_property("phase_scheduler_workers_per_spellbook", 1)

    binder = spellbook.create_binder()
    binder.bind(BasicService).as_unique().with_pre_hook(pre_hook).with_post_hook(post_hook)
    binder.with_activation_hook(activation_hook)
    spell_id = binder.finalize()

    conduit = spellbook.conjure(name="root")
    try:
        first = conduit.meld(spell=spell_id)
        second = conduit.meld(spell=spell_id)
        assert first is second
        assert pre_calls == ["pre", "pre"]
        assert post_calls == ["post", "post"]
        assert activation_calls == [first]
    finally:
        conduit.cleanup()


def test_spellbook_integration_fluent_binding_hooks_execute_from_kwargs() -> None:
    """
    Purpose:
        Validate hook execution when provided via binder kwargs.
    Contract:
        - pre/post hooks run on every meld.
        - activation hooks run once for unique spells.
    Returns:
        None.
    Raises:
        AssertionError: If hook counts are incorrect.
    """
    pre_calls: list[str] = []
    post_calls: list[str] = []
    activation_calls: list[object] = []

    def pre_one() -> None:
        """
        Purpose:
            Track the first pre-hook execution.
        Contract:
            Appends a marker to pre_calls.
        Returns:
            None.
        """
        pre_calls.append("pre-1")

    def pre_two() -> None:
        """
        Purpose:
            Track the second pre-hook execution.
        Contract:
            Appends a marker to pre_calls.
        Returns:
            None.
        """
        pre_calls.append("pre-2")

    def post_hook() -> None:
        """
        Purpose:
            Track post-hook execution.
        Contract:
            Appends a marker to post_calls.
        Returns:
            None.
        """
        post_calls.append("post")

    def activation_hook(instance: object) -> None:
        """
        Purpose:
            Track activation hook execution.
        Contract:
            Appends the instance to activation_calls.
        Args:
            instance: Newly created instance.
        Returns:
            None.
        """
        activation_calls.append(instance)

    spellbook = Spellbook()
    config = spellbook.get_configuration()
    config.set_property("phase_scheduler_workers_per_spellbook", 1)

    binder = spellbook.create_binder()
    binder.bind(
        BasicService,
        pre_hooks=[pre_one, pre_two],
        activation_hooks=[activation_hook],
        post_hooks=[post_hook],
    )
    spell_id = binder.finalize()

    conduit = spellbook.conjure(name="root")
    try:
        first = conduit.meld(spell=spell_id)
        second = conduit.meld(spell=spell_id)
        assert first is second
        assert pre_calls == ["pre-1", "pre-2", "pre-1", "pre-2"]
        assert post_calls == ["post", "post"]
        assert activation_calls == [first]
    finally:
        conduit.cleanup()


def test_spellbook_integration_fluent_binding_reuse_registers_multiple_spells() -> None:
    """
    Purpose:
        Validate a SpellBinder can be reused across registrations.
    Contract:
        - Multiple finalize calls register distinct spells.
        - Both spell_ids resolve via meld.
    Returns:
        None.
    Raises:
        AssertionError: If reuse fails to register spells.
    """
    spellbook = Spellbook()
    config = spellbook.get_configuration()
    config.set_property("phase_scheduler_workers_per_spellbook", 1)

    binder = spellbook.create_binder()
    service_id = binder.bind(BasicService).as_unique().finalize()
    config_id = binder.bind(BasicConfig).as_unique().finalize()

    conduit = spellbook.conjure(name="root")
    try:
        assert isinstance(conduit.meld(spell=service_id), BasicService)
        assert isinstance(conduit.meld(spell=config_id), BasicConfig)
    finally:
        conduit.cleanup()


def test_spellbook_integration_fluent_defaults_apply_for_many() -> None:
    """
    Purpose:
        Validate SpellBinder default existence applies to registrations.
    Contract:
        - Binder default Existence.many yields new instances per meld.
    Returns:
        None.
    Raises:
        AssertionError: If instances are reused unexpectedly.
    """
    spellbook = Spellbook()
    config = spellbook.get_configuration()
    config.set_property("phase_scheduler_workers_per_spellbook", 1)

    binder = spellbook.create_binder(default_existence=Existence.many, default_permissions="create")
    spell_id = binder.bind(BasicService).finalize()

    conduit = spellbook.conjure(name="root")
    try:
        first = conduit.meld(spell=spell_id)
        second = conduit.meld(spell=spell_id)
        assert first is not second
    finally:
        conduit.cleanup()


def test_spellbook_integration_fluent_defaults_permissions_apply() -> None:
    """
    Purpose:
        Validate SpellBinder default permissions propagate to bindings.
    Contract:
        - Spellbook reports default permissions on the registered spell.
    Returns:
        None.
    Raises:
        AssertionError: If permissions do not match defaults.
    """
    spellbook = Spellbook()
    config = spellbook.get_configuration()
    config.set_property("phase_scheduler_workers_per_spellbook", 1)

    binder = spellbook.create_binder(default_existence=Existence.unique, default_permissions="read")
    binder.bind(BasicService)
    spell_id = binder.finalize()

    conduit = spellbook.conjure(name="root")
    try:
        assert isinstance(conduit.meld(spell=spell_id), BasicService)
        spell_index = spellbook.find_spell_index("BasicService", BasicService.__name__, "__default__")
        assert spellbook.get_spell_permissions(spell_index) == "read"
    finally:
        conduit.cleanup()


def test_spellbook_integration_fluent_binding_existing_object_reuses_instance() -> None:
    """
    Purpose:
        Validate binding an existing object through SpellBinder reuses it.
    Contract:
        - Meld returns the same existing instance for the bound spell.
    Returns:
        None.
    Raises:
        AssertionError: If the instance is not reused.
    """
    spellbook = Spellbook()
    config = spellbook.get_configuration()
    config.set_property("phase_scheduler_workers_per_spellbook", 1)

    conduit = spellbook.conjure(name="root")
    try:
        existing = BasicConfig(label="binder-existing")
        binder = spellbook.create_binder()
        spell_id = binder.bind(existing).as_unique().finalize()
        assert conduit.meld(spell=spell_id) is existing
    finally:
        conduit.cleanup()


def test_spellbook_integration_inspect_spell_class_registered_after_conjure() -> None:
    """
    Purpose:
        Validate inspect_spell returns a registered id for class spells.
    Contract:
        - After conjure, inspect_spell returns the bound spell_id for the class.
    Returns:
        None.
    Raises:
        AssertionError: If inspect_spell does not return the expected id.
    """
    spellbook = Spellbook()
    config = spellbook.get_configuration()
    config.set_property("phase_scheduler_workers_per_spellbook", 1)
    spell_id = spellbook.bind(
        spell=BasicService,
        existence=Existence.unique,
        permissions="create",
    )

    conduit = spellbook.conjure(name="root")
    try:
        inspected = spellbook.inspect_spell(BasicService)
        assert inspected == spell_id
    finally:
        conduit.cleanup()


def test_spellbook_integration_create_binder_fluent_bind_and_meld() -> None:
    """
    Purpose:
        Validate SpellBinder fluent binding through Spellbook integration.
    Contract:
        - Fluent binding returns a usable spell_id.
        - Conduit.meld resolves the bound spell.
    Returns:
        None.
    Raises:
        AssertionError: If fluent binding fails to resolve.
    """
    spellbook = Spellbook()
    config = spellbook.get_configuration()
    config.set_property("phase_scheduler_workers_per_spellbook", 1)

    binder = spellbook.create_binder()
    spell_id = binder.bind(BasicService).as_unique().finalize()

    conduit = spellbook.conjure(name="root")
    try:
        instance = conduit.meld(spell=spell_id)
        assert isinstance(instance, BasicService)
        assert instance.marker == "service"
    finally:
        conduit.cleanup()


def test_spellbook_integration_inspect_spell_returns_registered_id() -> None:
    """
    Purpose:
        Validate Spellbook.inspect_spell returns a registered spell id.
    Contract:
        - Inspecting a bound existing instance returns its spell_id.
        - Meld returns the same instance for existing-object spells.
    Returns:
        None.
    Raises:
        AssertionError: If inspect_spell fails to resolve the id.
    """
    spellbook = Spellbook()
    config = spellbook.get_configuration()
    config.set_property("phase_scheduler_workers_per_spellbook", 1)

    existing = BasicConfig()
    spell_id = spellbook.bind(
        spell=existing,
        existence=Existence.unique,
        permissions="create",
    )

    conduit = spellbook.conjure(name="root")
    try:
        inspected = spellbook.inspect_spell(existing)
        assert inspected == spell_id

        resolved = conduit.meld(spell=spell_id)
        assert resolved is existing
    finally:
        conduit.cleanup()


def test_spellbook_integration_contracted_spells_visible() -> None:
    """
    Purpose:
        Validate Spellbook contracted spell visibility after linking conduits.
    Contract:
        - Borrower Spellbook records contracted spell entries by conduit id.
        - Contracted spells can be melded via the borrower conduit.
    Returns:
        None.
    Raises:
        AssertionError: If contracted spells are not visible or resolvable.
    """
    configuration = Configuration()
    configuration.dynamic_defaults()
    configuration.set_property("phase_scheduler_workers_per_spellbook", 1)

    owner_book = Spellbook(configuration=configuration)
    spell_id = owner_book.bind(
        spell=BasicService,
        existence=Existence.unique,
        permissions="create",
    )
    borrower_book = Spellbook(configuration=configuration)

    owner = owner_book.conjure(automatic=False, name="owner")
    borrower = borrower_book.conjure(automatic=False, name="borrower")
    try:
        owner.link(borrower)
        borrower.add_spell_to_contract(
            spell_id=spell_id,
            conduit=owner,
            permissions="create",
        )

        contracted = borrower_book.contracted_spells.get(owner.id)
        assert contracted is not None
        assert any(
            spell_index.has_version(spell_id) for spell_index in contracted.keys()
        )

        instance = borrower.meld(spell=spell_id)
        assert isinstance(instance, BasicService)
    finally:
        borrower.cleanup()
        owner.cleanup()


def test_spellbook_integration_contract_removal_clears_access() -> None:
    """
    Purpose:
        Validate removing a contracted spell clears borrower access.
    Contract:
        - remove_spell_from_contract returns True on success.
        - The spell is no longer visible via get_spell_in_contracts.
    Returns:
        None.
    Raises:
        AssertionError: If the contract is not removed.
    """
    configuration = Configuration()
    configuration.dynamic_defaults()
    configuration.set_property("phase_scheduler_workers_per_spellbook", 1)

    owner_book = Spellbook(configuration=configuration)
    spell_id = owner_book.bind(
        spell=BasicService,
        existence=Existence.unique,
        permissions="create",
    )
    borrower_book = Spellbook(configuration=configuration)

    owner = owner_book.conjure(automatic=False, name="owner")
    borrower = borrower_book.conjure(automatic=False, name="borrower")
    try:
        owner.link(borrower)
        borrower.add_spell_to_contract(
            spell_id=spell_id,
            conduit=owner,
            permissions="create",
        )
        assert borrower.get_spell_in_contracts(spell_id) is not None

        removed = borrower.remove_spell_from_contract(
            spell_id=spell_id,
            conduit=owner,
        )
        assert removed is True
        assert borrower.get_spell_in_contracts(spell_id) is None
    finally:
        borrower.cleanup()
        owner.cleanup()


def test_spellbook_integration_sever_link_clears_contracts() -> None:
    """
    Purpose:
        Validate sever_link clears contracted spell access.
    Contract:
        - sever_link returns True when a link is removed.
        - Contracted spells are no longer visible after unlink.
    Returns:
        None.
    Raises:
        AssertionError: If unlink does not clear contracts.
    """
    configuration = Configuration()
    configuration.dynamic_defaults()
    configuration.set_property("phase_scheduler_workers_per_spellbook", 1)

    owner_book = Spellbook(configuration=configuration)
    spell_id = owner_book.bind(
        spell=BasicService,
        existence=Existence.unique,
        permissions="create",
    )
    borrower_book = Spellbook(configuration=configuration)

    owner = owner_book.conjure(automatic=False, name="owner")
    borrower = borrower_book.conjure(automatic=False, name="borrower")
    try:
        owner.link(borrower)
        borrower.add_spell_to_contract(
            spell_id=spell_id,
            conduit=owner,
            permissions="create",
        )
        assert borrower.get_spell_in_contracts(spell_id) is not None

        unlinked = owner.sever_link(borrower)
        assert unlinked is True
        assert borrower.get_spell_in_contracts(spell_id) is None
    finally:
        borrower.cleanup()
        owner.cleanup()


def test_spellbook_integration_find_spell_index_and_key_for_contracted_spell() -> None:
    """
    Purpose:
        Validate contracted spells resolve via Spellbook lookup APIs.
    Contract:
        - find_spell_index returns a SpellIndex for a contracted spell.
        - find_spell_key resolves the contracted lookup key.
        - Borrower meld resolves by spellframe + binding_name.
    Returns:
        None.
    Raises:
        AssertionError: If contracted lookups fail.
    """
    configuration = Configuration()
    configuration.dynamic_defaults()
    configuration.set_property("phase_scheduler_workers_per_spellbook", 1)

    owner_book = Spellbook(configuration=configuration)
    binder = owner_book.create_binder()
    binder.bind(BasicService).under_spellframe(IService).named("primary").as_unique()
    spell_id = binder.finalize()

    borrower_book = Spellbook(configuration=configuration)
    owner = owner_book.conjure(automatic=False, name="owner")
    borrower = borrower_book.conjure(automatic=False, name="borrower")
    try:
        owner.link(borrower)
        borrower.add_spell_to_contract(
            spell_id=spell_id,
            conduit=owner,
            permissions="create",
        )

        spell_index = borrower_book.find_spell_index(IService, BasicService.__name__, "primary")
        spell_key = borrower_book.find_spell_key(IService, BasicService.__name__, "primary")
        contracted = borrower_book.contracted_spells.get(owner.id)
        assert contracted is not None
        assert spell_index in contracted
        assert isinstance(spell_key, tuple)

        instance = borrower.meld(spellframe=IService, binding_name="primary")
        assert isinstance(instance, BasicService)
    finally:
        borrower.cleanup()
        owner.cleanup()
