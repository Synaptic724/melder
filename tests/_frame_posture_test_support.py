import typing

from melder.aether.aether import Aether
from melder.aether.aetheric_frame.aetheric_frame_configuration import AethericFrameConfiguration
from melder.aether.spellbook.configuration.spellbook_configuration import SpellbookConfiguration
from melder.aether.spellbook.configuration.system_state import SystemState


_TEST_FRAME_POSTURES: dict[str, AethericFrameConfiguration] = {}


def _get_or_create_detached_frame_posture(
        configuration: SpellbookConfiguration,
) -> AethericFrameConfiguration:
    """
    Return one detached frame-posture copy for the given SpellbookConfiguration.
    """
    configuration_id = configuration._id
    frame_configuration = _TEST_FRAME_POSTURES.get(configuration_id)
    if frame_configuration is None:
        frame_configuration = AethericFrameConfiguration(
            origin_spellbook_id=None,
            system_state=SystemState.automatic,
            ai_native_enabled=False,
            rift_enabled=False,
            shared_framewide_spellbook_configuration=False,
        )
        _TEST_FRAME_POSTURES[configuration_id] = frame_configuration
    return frame_configuration


def _sync_detached_frame_posture_to_aether(
        configuration: SpellbookConfiguration,
) -> AethericFrameConfiguration:
    """
    Apply the detached test posture onto the live frame-owned posture object.
    """
    detached_configuration = _get_or_create_detached_frame_posture(configuration)
    aether = Aether()
    frame_name = configuration._aether_frame
    aether._ensure_frame(frame_name)
    frame_configuration = aether._get_aetheric_frame_configuration(frame_name)
    if frame_configuration is None:
        raise RuntimeError("Frame posture is unavailable for the requested test frame.")
    if frame_configuration._frozen:
        if frame_configuration.matches_posture(detached_configuration):
            return typing.cast(AethericFrameConfiguration, frame_configuration)
        raise RuntimeError(
            "Cannot reconfigure a frozen frame posture to a different value in tests."
        )
    frame_configuration.with_system_state(detached_configuration.system_state)
    frame_configuration.with_ai_native(detached_configuration.ai_native_enabled)
    frame_configuration.with_rift_enabled(detached_configuration.rift_enabled)
    frame_configuration.with_shared_framewide_spellbook_configuration(
        detached_configuration.shared_framewide_spellbook_configuration
    )
    frame_configuration.with_disable_all_transactions_after_conjure(
        detached_configuration.disable_all_transactions_after_conjure
    )
    frame_configuration.with_disable_mutations(
        detached_configuration.disable_mutations
    )
    frame_configuration.with_disable_linking(
        detached_configuration.disable_linking
    )
    frame_configuration.with_disable_bind(
        detached_configuration.disable_bind
    )
    frame_configuration.with_disable_conduit_cluster(
        detached_configuration.disable_conduit_cluster
    )
    frame_configuration.with_disable_transfer_of_ownership(
        detached_configuration.disable_transfer_of_ownership
    )
    frame_configuration.with_disable_contract_mutation(
        detached_configuration.disable_contract_mutation
    )
    frame_configuration.with_queue_competing_root_transactions(
        detached_configuration.queue_competing_root_transactions
    )
    frame_configuration.with_max_transaction_wait_time_in_seconds(
        detached_configuration.max_transaction_wait_time_in_seconds
    )
    return typing.cast(AethericFrameConfiguration, frame_configuration)


def configure_frame_posture_for_spellbook_configuration(
        configuration: SpellbookConfiguration,
        *,
        dynamic: bool = False,
        rift_enabled: bool = False,
        ai_native_enabled: bool = False,
        shared_framewide_spellbook_configuration: bool = False,
) -> AethericFrameConfiguration:
    """
    Configure the frame-owned posture associated with one SpellbookConfiguration.

    Purpose:
        Tests that previously authored frame posture through the rich local
        Spellbook configuration now need a direct path onto the frame-owned
        `AethericFrameConfiguration`.

    Args:
        configuration:
            Local Spellbook configuration whose frame name identifies the target
            frame posture object.
        dynamic:
            When True, apply dynamic defaults; otherwise apply automatic
            defaults.
        rift_enabled:
            Whether Rift visibility should be enabled.
        ai_native_enabled:
            Whether AI-native posture should be enabled.
        shared_framewide_spellbook_configuration:
            Whether frame-wide shared rich-config mode should be enabled.

    Returns:
        AethericFrameConfiguration: The mutable frame-owned posture object used
        by the target frame.
    """
    detached_configuration = _get_or_create_detached_frame_posture(configuration)
    if dynamic:
        detached_configuration.dynamic_defaults()
    else:
        detached_configuration.automatic_defaults()
    detached_configuration.with_rift_enabled(rift_enabled)
    detached_configuration.with_ai_native(ai_native_enabled)
    detached_configuration.with_shared_framewide_spellbook_configuration(
        shared_framewide_spellbook_configuration
    )
    return _sync_detached_frame_posture_to_aether(configuration)


def get_frame_posture_for_spellbook_configuration(
        configuration: SpellbookConfiguration,
) -> AethericFrameConfiguration:
    """
    Return the frame-owned posture object for one SpellbookConfiguration.

    Args:
        configuration:
            Rich Spellbook configuration whose frame posture should be resolved.

    Returns:
        AethericFrameConfiguration: The frame-owned posture for the
        configuration's frame.
    """
    return _sync_detached_frame_posture_to_aether(configuration)


def set_frame_system_state_for_spellbook_configuration(
        configuration: SpellbookConfiguration,
        system_state: typing.Union[SystemState, str],
) -> SpellbookConfiguration:
    """
    Apply one system_state value to the frame-owned posture for tests.
    """
    detached_configuration = _get_or_create_detached_frame_posture(configuration)
    detached_configuration.with_system_state(system_state)
    _sync_detached_frame_posture_to_aether(configuration)
    return configuration


def set_frame_ai_native_for_spellbook_configuration(
        configuration: SpellbookConfiguration,
        enabled: bool = True,
) -> SpellbookConfiguration:
    """
    Apply one AI-native flag to the frame-owned posture for tests.
    """
    detached_configuration = _get_or_create_detached_frame_posture(configuration)
    detached_configuration.with_ai_native(enabled)
    _sync_detached_frame_posture_to_aether(configuration)
    return configuration


def set_frame_rift_enabled_for_spellbook_configuration(
        configuration: SpellbookConfiguration,
        enabled: bool = True,
) -> SpellbookConfiguration:
    """
    Apply one Rift-enabled flag to the frame-owned posture for tests.
    """
    detached_configuration = _get_or_create_detached_frame_posture(configuration)
    detached_configuration.with_rift_enabled(enabled)
    _sync_detached_frame_posture_to_aether(configuration)
    return configuration


def set_shared_framewide_spellbook_configuration_for_spellbook_configuration(
        configuration: SpellbookConfiguration,
        enabled: bool = True,
) -> SpellbookConfiguration:
    """
    Apply one shared-rich-config flag to the frame-owned posture for tests.
    """
    detached_configuration = _get_or_create_detached_frame_posture(configuration)
    detached_configuration.with_shared_framewide_spellbook_configuration(enabled)
    _sync_detached_frame_posture_to_aether(configuration)
    return configuration


def apply_dynamic_defaults_for_spellbook_configuration(
        configuration: SpellbookConfiguration,
) -> SpellbookConfiguration:
    """
    Apply rich-config defaults plus dynamic frame posture defaults for tests.
    """
    configuration.with_defaults()
    detached_configuration = _get_or_create_detached_frame_posture(configuration)
    detached_configuration.dynamic_defaults()
    _sync_detached_frame_posture_to_aether(configuration)
    return configuration


def apply_automatic_defaults_for_spellbook_configuration(
        configuration: SpellbookConfiguration,
) -> SpellbookConfiguration:
    """
    Apply rich-config defaults plus automatic frame posture defaults for tests.
    """
    configuration.with_defaults()
    detached_configuration = _get_or_create_detached_frame_posture(configuration)
    detached_configuration.automatic_defaults()
    _sync_detached_frame_posture_to_aether(configuration)
    return configuration


def build_aetheric_frame_configuration_for_spellbook_configuration(
        configuration: SpellbookConfiguration,
        origin_spellbook_id: typing.Optional[str] = None,
) -> AethericFrameConfiguration:
    """
    Build a detached frame configuration copy from one SpellbookConfiguration.

    Purpose:
        Some tests need a standalone `AethericFrameConfiguration` object for
        bind/equality assertions. The runtime owner is still the frame, so this
        helper copies the current frame-owned posture into a detached object.
    """
    frame_configuration = _get_or_create_detached_frame_posture(configuration)
    return AethericFrameConfiguration(
        origin_spellbook_id=origin_spellbook_id,
        system_state=frame_configuration.system_state,
        ai_native_enabled=frame_configuration.ai_native_enabled,
        rift_enabled=frame_configuration.rift_enabled,
        shared_framewide_spellbook_configuration=(
            frame_configuration.shared_framewide_spellbook_configuration
        ),
        disable_all_transactions_after_conjure=(
            frame_configuration.disable_all_transactions_after_conjure
        ),
        disable_mutations=frame_configuration.disable_mutations,
        disable_linking=frame_configuration.disable_linking,
        disable_bind=frame_configuration.disable_bind,
        disable_conduit_cluster=frame_configuration.disable_conduit_cluster,
        disable_transfer_of_ownership=(
            frame_configuration.disable_transfer_of_ownership
        ),
        disable_contract_mutation=(
            frame_configuration.disable_contract_mutation
        ),
        queue_competing_root_transactions=(
            frame_configuration.queue_competing_root_transactions
        ),
        max_transaction_wait_time_in_seconds=(
            frame_configuration.max_transaction_wait_time_in_seconds
        ),
    )
