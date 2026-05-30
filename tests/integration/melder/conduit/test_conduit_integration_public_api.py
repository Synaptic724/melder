from __future__ import annotations

from melder import SpellBinder
import pytest

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.spellbook.configuration.spellbook_configuration import SpellbookConfiguration
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spellbook import Spellbook
from tests.mocks.spellbook.core_classes import BasicConfig
from tests.mocks.spellbook.core_classes import BasicLogger
from tests.mocks.spellbook.core_classes import BasicService
from tests.mocks.spellbook.factories import BuiltArtifact


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


def test_conduit_public_api_id_name_and_repr() -> None:
    """
    Purpose:
        Validate Conduit id, name, and repr formatting.
    Contract:
        - id is a non-empty string.
        - name matches the conjure name.
        - repr includes the name and id.
    Returns:
        None.
    Raises:
        AssertionError: If identity or representation fields are missing.
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
        assert isinstance(conduit.id, str)
        assert conduit.id != ""
        assert conduit.name == "root"
        rep = repr(conduit)
        assert "Conduit name=root" in rep
        assert conduit.id in rep
    finally:
        conduit.cleanup()


def test_conduit_public_api_name_setter_blocks_rename() -> None:
    """
    Purpose:
        Validate a root conduit cannot be renamed once its final name is set.
    Contract:
        - root conduit receives the default name when none is provided.
        - reassigning raises RuntimeError.
    Returns:
        None.
    Raises:
        AssertionError: If rename is allowed.
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

    conduit = spellbook.conjure()
    try:
        assert conduit.name == "default"
        with pytest.raises(RuntimeError, match="Conduit name is set"):
            conduit.name = "rename"
    finally:
        conduit.cleanup()


def test_conduit_public_api_context_manager_allows_meld() -> None:
    """
    Purpose:
        Validate the Conduit context manager does not block meld.
    Contract:
        - Meld works inside the context manager.
        - Meld works after the context exits.
    Returns:
        None.
    Raises:
        AssertionError: If meld fails inside or outside the context.
    """
    spellbook = Spellbook()
    config = spellbook.get_configuration()
    apply_dynamic_defaults_for_spellbook_configuration(config)
    config.set_property("phase_scheduler_workers_per_spellbook", 1)
    spell_id = spellbook.bind(
        spell=BasicService,
        existence=Existence.unique,
        permissions="create",
    )

    conduit = spellbook.conjure(name="root")
    try:
        with conduit as ctx:
            instance = ctx.meld(spell=spell_id)
            assert isinstance(instance, BasicService)
        assert isinstance(conduit.meld(spell=spell_id), BasicService)
    finally:
        conduit.cleanup()


def test_conduit_meld_with_spell_override_round_trip() -> None:
    """
    Purpose:
        Validate meld applies spell_override payloads for root parameters.
    Contract:
        - spell_override overrides the root constructor parameter.
        - Returned instance reflects the override marker.
    Returns:
        None.
    Raises:
        AssertionError: If overrides are not applied.
    """
    spellbook = Spellbook()
    config = spellbook.get_configuration()
    apply_dynamic_defaults_for_spellbook_configuration(config)
    config.set_property("phase_scheduler_workers_per_spellbook", 1)
    spell_id = spellbook.bind(
        spell=BuiltArtifact,
        existence=Existence.many,
        permissions="create",
    )

    conduit = spellbook.conjure(name="root")
    try:
        instance = conduit.meld(
            spell=spell_id,
            spell_override={"marker": "override"},
        )
        assert isinstance(instance, BuiltArtifact)
        assert instance.marker == "override"
    finally:
        conduit.cleanup()


def test_conduit_public_api_spellspace_lifecycle() -> None:
    """
    Purpose:
        Validate spellspace lifecycle and active scope behavior.
    Contract:
        - get_active_spellspace returns None when inactive.
        - create_spellspace produces a direct spellspace handle that can meld
          through its own front door.
        - enter_spellspace still marks the active spellspace for conduit
          inspection helpers.
    Returns:
        None.
    Raises:
        AssertionError: If spellspace lifecycle behavior is incorrect.
    """
    spellbook = Spellbook()
    config = spellbook.get_configuration()
    apply_dynamic_defaults_for_spellbook_configuration(config)
    config.set_property("phase_scheduler_workers_per_spellbook", 1)
    spell_id = spellbook.bind(
        spell=BasicService,
        existence=Existence.unique_per_spell_space,
        permissions="create",
    )

    conduit = spellbook.conjure(name="root")
    try:
        assert conduit.get_active_spellspace() is None

        inactive = conduit.create_spellspace()
        instance = inactive.meld(spell=spell_id)
        assert isinstance(instance, BasicService)

        with conduit.enter_spellspace() as active:
            assert conduit.get_active_spellspace() is active
            instance = active.meld(spell=spell_id)
            assert isinstance(instance, BasicService)

        assert conduit.get_active_spellspace() is None
    finally:
        conduit.cleanup()


def test_conduit_public_api_spell_lookup_helpers() -> None:
    """
    Purpose:
        Validate Conduit spell lookup helpers resolve local spell metadata.
    Contract:
        - get_spell_by_id returns the local spell wrapper.
        - find_spell_id and find_spell_key resolve known spells.
        - inspect_spell returns the registered spell id.
        - check_spell_id returns True for known spell ids.
        - get_spell_permissions resolves the bound permissions.
    Returns:
        None.
    Raises:
        AssertionError: If lookup helpers fail to resolve.
    """
    spellbook = Spellbook()
    config = spellbook.get_configuration()
    apply_dynamic_defaults_for_spellbook_configuration(config)
    config.set_property("phase_scheduler_workers_per_spellbook", 1)
    spell_id = spellbook.bind(
        spell=BasicService,
        existence=Existence.unique,
        permissions="create",
    )

    conduit = spellbook.conjure(name="root")
    try:
        spell = conduit.get_spell_by_id(spell_id)
        assert spell is not None
        assert spell.spell_id == spell_id

        resolved_id = conduit.find_spell_id("BasicService", BasicService.__name__, "__default__")
        assert resolved_id == spell_id

        spell_key = conduit.find_spell_key("BasicService", BasicService.__name__, "__default__")
        assert spell_key is not None

        assert conduit.inspect_spell(BasicService) == spell_id
        assert conduit.check_spell_id(spell_id) is True
        assert conduit.get_spell_permissions(spell_id) == "create"
    finally:
        conduit.cleanup()


def test_conduit_public_api_bind_and_binder_register_spells() -> None:
    """
    Purpose:
        Validate Conduit bind and create_binder delegate to the Spellbook.
    Contract:
        - Conduit.bind registers spells after conjure.
        - Conduit.create_binder binds spells via fluent API.
    Returns:
        None.
    Raises:
        AssertionError: If binding via Conduit fails.
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
        config_id = conduit.bind(
            spell=BasicConfig,
            existence=Existence.unique,
            permissions="create",
        )
        with spellbook.transaction("bind"):
            logger_id = SpellBinder(conduit._spellbook, ).bind(BasicLogger).as_unique().finalize()

        config_spell = conduit.get_spell_by_id(config_id)
        logger_spell = conduit.get_spell_by_id(logger_id)
        assert config_spell is not None
        assert logger_spell is not None
        assert config_spell.spell_id == config_id
        assert logger_spell.spell_id == logger_id
        assert conduit.inspect_spell(BasicConfig) == config_id
        assert conduit.inspect_spell(BasicLogger) == logger_id
    finally:
        conduit.cleanup()


def test_conduit_public_api_begin_transaction_bind_allows_post_conjure_bind() -> None:
    """
    Purpose:
        Validate begin_transaction("bind") opens the bind window for Conduit.
    Contract:
        - Conduit.bind succeeds inside a begin/end transaction window.
        - Conduit.meld resolves the new spell by id.
    Returns:
        None.
    Raises:
        AssertionError: If binding or meld resolution fails.
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
        conduit.begin_transaction("bind")
        config_id = conduit.bind(
            spell=BasicConfig,
            existence=Existence.unique,
            permissions="create",
        )
        conduit.end_transaction("bind")

        resolved = conduit.meld(spell=config_id)
        assert isinstance(resolved, BasicConfig)
    finally:
        conduit.cleanup()


def test_conduit_begin_transaction_sets_conduit_scope_key() -> None:
    """
    Purpose:
        Validate Conduit transactions advertise conduit scope keys for conflicts.
    Contract:
        - Conduit begin_transaction emits a scope key that conflicts with other requests.
        - Overlapping scope keys are rejected by change-control admission.
    Returns:
        None.
    Raises:
        AssertionError: If conflict admission is not enforced.
    """
    frame_name = "shared-conduit-scope"
    configuration = SpellbookConfiguration(frame_name)
    apply_dynamic_defaults_for_spellbook_configuration(configuration)
    configuration.finalize()
    spellbook_a = Spellbook(aetheric_frame=frame_name, configuration=configuration)
    spellbook_b = Spellbook(aetheric_frame=frame_name, configuration=configuration)
    conduit_a = spellbook_a.conjure(automatic=False, name="conduit-a")
    conduit_peer = spellbook_b.conjure(automatic=False, name="conduit-peer")
    change_control = spellbook_a._aether._get_change_control_manager(frame_name)
    scope_key = change_control.transaction_manager().make_scope_key_conduit(conduit_a.id)
    try:
        conduit_a.begin_transaction("link", conduits=[conduit_a, conduit_peer])
        with pytest.raises(RuntimeError, match="Change-control admission denied"):
            conduit_peer.begin_transaction(
                "link",
                conduits=[conduit_peer, conduit_a],
                scope_keys=[scope_key],
            )
    finally:
        conduit_a.end_transaction("link")
        conduit_peer.cleanup()
        conduit_a.cleanup()


def test_conduit_public_api_cleanup_lesser_conduits() -> None:
    """
    Purpose:
        Validate cleanup_lesser_conduits clears child conduits.
    Contract:
        - Lesser conduits become unusable after cleanup.
    Returns:
        None.
    Raises:
        AssertionError: If lesser conduits remain usable after cleanup.
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
    lesser = conduit.create_lesser_conduit()
    lesser_id = lesser.id
    try:
        conduit.cleanup_lesser_conduits()
        with pytest.raises(RuntimeError, match="cleaned"):
            lesser.meld(spell=spell_id)
        assert conduit.get_lesser_conduit(lesser_id) is None
    finally:
        conduit.cleanup()


def test_conduit_public_api_bind_rejects_lesser_conduit() -> None:
    """
    Purpose:
        Validate lesser conduits cannot bind spells.
    Contract:
        - bind on a lesser conduit raises RuntimeError.
    Returns:
        None.
    Raises:
        AssertionError: If lesser bind is allowed.
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
    lesser = conduit.create_lesser_conduit()
    try:
        with pytest.raises(RuntimeError, match="Only normal conduits"):
            lesser.bind(
                spell=BasicConfig,
                existence=Existence.unique,
                permissions="create",
            )
    finally:
        conduit.cleanup()


def test_conduit_public_api_get_conduit_by_id_name_and_spell_id() -> None:
    """
    Purpose:
        Validate Aether lookup helpers resolve conduits by id, name, and spell ownership.
    Contract:
        - get_conduit_by_id returns the target conduit.
        - get_conduit_by_name returns the target conduit.
        - get_conduit_by_spell_id returns the spell owner conduit.
    Returns:
        None.
    Raises:
        AssertionError: If Aether lookup helpers fail.
    """
    configuration = SpellbookConfiguration()
    configuration.load_default_dictionary()
    configuration.set_property("phase_scheduler_workers_per_spellbook", 1)

    spellbook_a = Spellbook(configuration=configuration)
    spell_id_a = spellbook_a.bind(
        spell=BasicService,
        existence=Existence.unique,
        permissions="create",
    )

    spellbook_b = Spellbook(configuration=configuration)
    spell_id_b = spellbook_b.bind(
        spell=BasicConfig,
        existence=Existence.unique,
        permissions="create",
    )

    conduit_a = spellbook_a.conjure(name="root-a")
    conduit_b = spellbook_b.conjure(name="root-b")
    try:
        cloud = conduit_a._spellbook._aether.get_conduit_cloud(conduit_a._aetheric_frame_name)
        assert cloud.get_conduit_by_id(conduit_b.id) is conduit_b
        assert cloud.get_conduit_by_name("root-b") is conduit_b
        assert conduit_a.get_conduit_by_spell_id(spell_id_b) is conduit_b
        assert conduit_b.get_conduit_by_spell_id(spell_id_a) is conduit_a
    finally:
        conduit_b.cleanup()
        conduit_a.cleanup()

