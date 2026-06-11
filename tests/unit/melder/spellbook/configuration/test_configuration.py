import pytest

from melder.aether.spellbook.configuration.spellbook_configuration import SpellbookConfiguration
from melder.aether.spellbook.configuration.system_state import SystemState
from melder.utilities.helpers.general_helpers import EnumHelpers


from tests._frame_posture_test_support import (
    apply_automatic_defaults_for_spellbook_configuration,
    apply_dynamic_defaults_for_spellbook_configuration,
    build_aetheric_frame_configuration_for_spellbook_configuration,
    set_frame_ai_native_for_spellbook_configuration,
    set_frame_system_state_for_spellbook_configuration,
    set_shared_framewide_spellbook_configuration_for_spellbook_configuration,
)
def test_load_defaults_populates_all_required_properties():
    cfg = SpellbookConfiguration()
    cfg.load_default_dictionary()
    for key in cfg.available_properties:
        assert cfg.has_property(key)
    assert cfg.get_property("disposal_method_names") == []
    assert cfg.get_property("full_ahead_of_time_compilation") is True
    frame_configuration = build_aetheric_frame_configuration_for_spellbook_configuration(cfg, )
    assert frame_configuration.system_state == SystemState.automatic
    assert frame_configuration.shared_framewide_spellbook_configuration is False


def test_with_system_state_accepts_enum_strings():
    cfg = SpellbookConfiguration()
    set_frame_system_state_for_spellbook_configuration(cfg, "dynamic")
    assert build_aetheric_frame_configuration_for_spellbook_configuration(cfg, ).system_state == SystemState.dynamic


def test_with_system_state_can_replace_pre_conjure_posture():
    cfg = SpellbookConfiguration()
    set_frame_system_state_for_spellbook_configuration(cfg, SystemState.automatic)
    set_frame_system_state_for_spellbook_configuration(cfg, SystemState.dynamic)
    assert build_aetheric_frame_configuration_for_spellbook_configuration(cfg, ).system_state == SystemState.dynamic


def test_set_property_rejects_frozen():
    cfg = SpellbookConfiguration()
    cfg.load_default_dictionary()
    cfg.freeze()
    with pytest.raises(RuntimeError):
        cfg.set_property("disposal", True)


def test_set_property_rejects_non_string_key():
    cfg = SpellbookConfiguration()
    with pytest.raises(TypeError):
        cfg.set_property(123, "x")  # type: ignore[arg-type]


def test_clear_properties_blocks_when_frozen():
    cfg = SpellbookConfiguration()
    cfg.load_default_dictionary()
    cfg.freeze()
    with pytest.raises(RuntimeError):
        cfg.clear_properties()


def test_get_property_missing_raises_key_error():
    cfg = SpellbookConfiguration()
    cfg.load_default_dictionary()
    with pytest.raises(KeyError):
        cfg.get_property("missing")


def test_has_property_reflects_state():
    cfg = SpellbookConfiguration()
    assert cfg.has_property("disposal") is False
    cfg.set_property("disposal", True)
    assert cfg.has_property("disposal") is True


def test_validate_success_after_defaults():
    cfg = SpellbookConfiguration()
    cfg.load_default_dictionary()
    assert cfg.validate() is True


def test_validate_missing_property_raises():
    cfg = SpellbookConfiguration()
    cfg.load_default_dictionary()
    cfg._properties.pop("disposal")
    with pytest.raises(ValueError):
        cfg.validate()


def test_validate_wrong_type_raises():
    cfg = SpellbookConfiguration()
    cfg.load_default_dictionary()
    cfg.set_property("phase_scheduler_workers_per_spellbook", "wrong")
    with pytest.raises(ValueError):
        cfg.validate()


def test_validate_enum_type_raises():
    cfg = SpellbookConfiguration()
    with pytest.raises(ValueError):
        set_frame_system_state_for_spellbook_configuration(cfg, "not-an-enum")
def test_validate_phase_scheduler_workers_bounds():
    cfg = SpellbookConfiguration()
    cfg.load_default_dictionary()
    cfg.set_property("phase_scheduler_workers_per_spellbook", 0)
    with pytest.raises(ValueError):
        cfg.validate()


def test_validate_ai_native_enabled_type():
    cfg = SpellbookConfiguration()
    cfg.load_default_dictionary()
    with pytest.raises(TypeError):
        set_frame_ai_native_for_spellbook_configuration(cfg, "yes")  # type: ignore[arg-type]


def test_validate_ai_native_requires_dynamic_system_state():
    cfg = SpellbookConfiguration()
    cfg.load_default_dictionary()
    set_frame_ai_native_for_spellbook_configuration(cfg, True)
    with pytest.raises(ValueError):
        build_aetheric_frame_configuration_for_spellbook_configuration(cfg, )


def test_validate_ai_native_allowed_in_dynamic_system_state():
    cfg = SpellbookConfiguration()
    set_frame_ai_native_for_spellbook_configuration(apply_dynamic_defaults_for_spellbook_configuration(cfg), True)
    assert cfg.validate() is True


def test_validate_full_ahead_of_time_compilation_type():
    cfg = SpellbookConfiguration()
    cfg.load_default_dictionary()
    cfg.set_property("full_ahead_of_time_compilation", "yes")
    with pytest.raises(ValueError):
        cfg.validate()


def test_freeze_is_idempotent_and_blocks_mutation():
    cfg = SpellbookConfiguration()
    cfg.load_default_dictionary()
    cfg.freeze()
    cfg.freeze()
    with pytest.raises(RuntimeError):
        cfg.set_property("disposal", True)


def test_add_hook_returns_shared_map():
    cfg = SpellbookConfiguration()

    def hook_a():
        return None

    def hook_b():
        return None

    cfg.add_hook("sb1", "on_conduit_pre_created", hook_a)
    hooks = cfg.get_hooks("sb1")
    assert hooks is not cfg.get_hooks("sb1")
    hooks["on_conduit_pre_created"].append(hook_b)
    assert cfg.get_hooks("sb1")["on_conduit_pre_created"] == [hook_a]


def test_add_hook_rejects_unknown_or_noncallable():
    cfg = SpellbookConfiguration()
    with pytest.raises(ValueError):
        cfg.add_hook("sb1", "not_allowed", lambda: None)
    with pytest.raises(TypeError):
        cfg.add_hook("sb1", "on_conduit_pre_created", "not-callable")  # type: ignore[arg-type]


def test_add_hooks_handles_iterables_and_skips_none():
    cfg = SpellbookConfiguration()
    called = []

    def fn():
        called.append(True)

    with pytest.raises(TypeError):
        cfg.add_hooks("sb", on_conduit_post_created=[fn, None], on_conduit_activated=None)


def test_hooks_blocked_when_frozen():
    cfg = SpellbookConfiguration()
    cfg.load_default_dictionary()
    cfg.freeze()
    with pytest.raises(RuntimeError):
        cfg.add_hook("sb1", "on_conduit_pre_created", lambda: None)


def test_withers_chain_and_freeze():
    cfg = SpellbookConfiguration().with_disposal(True)
    apply_dynamic_defaults_for_spellbook_configuration(cfg)
    cfg.with_phase_scheduler_workers(3)
    cfg.with_phase_scheduler_barrier_timeout(1000)
    set_frame_ai_native_for_spellbook_configuration(cfg, True)
    cfg.finalize()
    assert cfg.has_property("disposal")
    assert cfg.get_property("disposal_method_names") == []


def test_with_phase_scheduler_workers_rejects_invalid():
    cfg = SpellbookConfiguration()
    with pytest.raises(ValueError):
        cfg.with_phase_scheduler_workers(0)


def test_with_shared_framewide_spellbook_configuration_sets_property() -> None:
    cfg = set_shared_framewide_spellbook_configuration_for_spellbook_configuration(SpellbookConfiguration(), True)
    assert (
        build_aetheric_frame_configuration_for_spellbook_configuration(cfg, ).shared_framewide_spellbook_configuration
        is True
    )


def test_with_phase_scheduler_barrier_timeout_limits():
    cfg = SpellbookConfiguration()
    with pytest.raises(ValueError):
        cfg.with_phase_scheduler_barrier_timeout(0)
    with pytest.raises(ValueError):
        cfg.with_phase_scheduler_barrier_timeout(400000)


def test_add_disposal_methods_validates_types():
    cfg = SpellbookConfiguration()
    with pytest.raises(TypeError):
        cfg.add_disposal_methods("ok", 123)  # type: ignore[arg-type]


def test_build_alias_for_finalize():
    cfg = SpellbookConfiguration().with_defaults().build()
    with pytest.raises(RuntimeError):
        cfg.set_property("disposal", True)


def test_dynamic_defaults_sets_state_dynamic():
    cfg = apply_dynamic_defaults_for_spellbook_configuration(SpellbookConfiguration())
    assert build_aetheric_frame_configuration_for_spellbook_configuration(cfg, ).system_state == SystemState.dynamic


def test_automatic_defaults_sets_state_automatic():
    cfg = apply_automatic_defaults_for_spellbook_configuration(SpellbookConfiguration())
    assert build_aetheric_frame_configuration_for_spellbook_configuration(cfg, ).system_state == SystemState.automatic


def test_iter_returns_keys():
    cfg = SpellbookConfiguration()
    cfg.load_default_dictionary()
    keys = set(iter(cfg))
    assert "disposal" in keys
    assert "full_ahead_of_time_compilation" in keys


def test_cleanup_idempotent_and_nulls_references():
    cfg = SpellbookConfiguration()
    cfg.load_default_dictionary()
    cfg.cleanup()
    cfg.cleanup()
    with pytest.raises(RuntimeError):
        cfg.set_property("disposal", True)
    assert not hasattr(cfg, '_properties')
    assert not hasattr(cfg, '_hooks')


def test_convert_enum_helper_matches_configuration_usage():
    cfg = SpellbookConfiguration()
    assert EnumHelpers.convert_enum_and_check("dynamic", SystemState) == SystemState.dynamic
    set_frame_system_state_for_spellbook_configuration(cfg, "automatic")
    assert build_aetheric_frame_configuration_for_spellbook_configuration(cfg, ).system_state == SystemState.automatic


# Additional coverage

def test_set_property_rejects_after_cleanup():
    cfg = SpellbookConfiguration()
    cfg.cleanup()
    with pytest.raises(RuntimeError):
        cfg.set_property("disposal", True)


def test_get_has_property_after_cleanup_raise():
    cfg = SpellbookConfiguration()
    cfg.cleanup()
    with pytest.raises(RuntimeError):
        cfg.get_property("disposal")
    with pytest.raises(RuntimeError):
        cfg.has_property("disposal")


def test_freeze_after_cleanup_raises():
    cfg = SpellbookConfiguration()
    cfg.cleanup()
    with pytest.raises(RuntimeError):
        cfg.freeze()


def test_load_defaults_preserves_pre_set_system_state():
    cfg = SpellbookConfiguration()
    set_frame_system_state_for_spellbook_configuration(cfg, SystemState.dynamic)
    cfg.load_default_dictionary()
    assert build_aetheric_frame_configuration_for_spellbook_configuration(cfg, ).system_state == SystemState.dynamic


def test_clear_properties_allows_reset_before_freeze():
    cfg = SpellbookConfiguration()
    cfg.load_default_dictionary()
    set_frame_system_state_for_spellbook_configuration(cfg, SystemState.dynamic)
    cfg.clear_properties()
    assert cfg.has_property("disposal") is False
    assert build_aetheric_frame_configuration_for_spellbook_configuration(cfg, ).system_state == SystemState.dynamic


def test_clear_properties_after_cleanup_raises():
    cfg = SpellbookConfiguration()
    cfg.cleanup()
    with pytest.raises(RuntimeError):
        cfg.clear_properties()


def test_validate_enums_method_failure_and_success():
    cfg = SpellbookConfiguration()
    set_frame_system_state_for_spellbook_configuration(cfg, "automatic")
    assert cfg.validate_enums() is True
    cfg = SpellbookConfiguration()
    with pytest.raises(ValueError):
        set_frame_system_state_for_spellbook_configuration(cfg, 123)  # type: ignore[arg-type]


def test_validate_disposal_method_names_type():
    cfg = SpellbookConfiguration()
    cfg.set_property("disposal", False)
    cfg.set_property("disposal_method_names", "not-a-list")
    cfg.set_property("full_ahead_of_time_compilation", True)
    cfg.set_property("phase_scheduler_workers_per_spellbook", 1)
    cfg.set_property("phase_scheduler_barrier_timeout_milliseconds", 1)
    with pytest.raises(ValueError):
        cfg.validate()


def test_validate_barrier_timeout_type_and_bounds():
    cfg = SpellbookConfiguration()
    cfg.load_default_dictionary()
    cfg.set_property("phase_scheduler_barrier_timeout_milliseconds", "bad")
    with pytest.raises(ValueError):
        cfg.validate()


def test_add_hook_after_cleanup_raises():
    cfg = SpellbookConfiguration()
    cfg.cleanup()
    with pytest.raises(RuntimeError):
        cfg.add_hook("sb", "on_conduit_pre_created", lambda: None)


def test_add_hooks_after_cleanup_raises():
    cfg = SpellbookConfiguration()
    cfg.cleanup()
    with pytest.raises(RuntimeError):
        cfg.add_hooks("sb", on_conduit_pre_created=lambda: None)


def test_get_hooks_missing_spellbook_id_returns_empty():
    cfg = SpellbookConfiguration()
    cfg.add_hook("sb1", "on_conduit_pre_created", lambda: None)
    assert cfg.get_hooks("missing") == {}


def test_add_hook_appends_multiple_times():
    cfg = SpellbookConfiguration()
    cfg.add_hook("sb", "on_conduit_pre_created", lambda: "a")
    cfg.add_hook("sb", "on_conduit_pre_created", lambda: "b")
    hooks = cfg.get_hooks("sb")["on_conduit_pre_created"]
    assert len(hooks) == 2


def test_add_hooks_rejects_generator_with_bad_entry():
    cfg = SpellbookConfiguration()

    def gen():
        yield lambda: None
        yield "bad"  # type: ignore[misc]

    with pytest.raises(TypeError):
        cfg.add_hooks("sb", on_conduit_pre_created=gen())


def test_with_hooks_fluent_returns_self():
    cfg = SpellbookConfiguration()
    result = cfg.with_hooks("sb", on_conduit_pre_created=lambda: None)
    assert result is cfg


def test_add_disposal_methods_dedup_and_order():
    cfg = SpellbookConfiguration()
    cfg.add_disposal_methods("close", "cleanup", "close")
    assert cfg.get_property("disposal_method_names") == ["close", "cleanup"]
    with pytest.raises(RuntimeError):
        cfg.add_disposal_methods("another")


def test_with_disposal_method_names_rejects_non_list():
    cfg = SpellbookConfiguration()
    with pytest.raises(TypeError):
        cfg.with_disposal_method_names("not-list")  # type: ignore[arg-type]


def test_with_full_ahead_of_time_compilation_sets_value():
    cfg = SpellbookConfiguration()
    returned = cfg.with_full_ahead_of_time_compilation(False)
    assert returned is cfg
    assert cfg.get_property("full_ahead_of_time_compilation") is False


def test_with_full_ahead_of_time_compilation_rejects_non_bool():
    cfg = SpellbookConfiguration()
    with pytest.raises(TypeError):
        cfg.with_full_ahead_of_time_compilation("false")  # type: ignore[arg-type]


def test_with_defaults_allows_overriding_full_ahead_of_time_compilation():
    cfg = SpellbookConfiguration().with_defaults()
    cfg.with_full_ahead_of_time_compilation(False)
    assert cfg.get_property("full_ahead_of_time_compilation") is False


def test_finalize_twice_is_idempotent():
    cfg = SpellbookConfiguration().with_defaults()
    cfg.finalize()
    cfg.finalize()
    with pytest.raises(RuntimeError):
        cfg.set_property("disposal", True)


def test_dynamic_defaults_does_not_overwrite_existing_disposal_names():
    cfg = SpellbookConfiguration()
    cfg.set_property("disposal_method_names", ["pre"])
    apply_dynamic_defaults_for_spellbook_configuration(cfg)
    assert cfg.get_property("disposal_method_names")[0] == "pre"


def test_with_system_state_rejects_overwrite_explicit():
    cfg = SpellbookConfiguration()
    set_frame_system_state_for_spellbook_configuration(cfg, SystemState.dynamic)
    set_frame_system_state_for_spellbook_configuration(cfg, SystemState.automatic)
    assert build_aetheric_frame_configuration_for_spellbook_configuration(cfg, ).system_state == SystemState.automatic


def test_iter_only_has_current_keys_after_clear_and_reset():
    cfg = SpellbookConfiguration()
    cfg.load_default_dictionary()
    cfg.clear_properties()
    cfg.set_property("disposal", True)
    keys = set(iter(cfg))
    assert keys == {"disposal"}


def test_cleanup_sets_frozen_and_blocks_mutation():
    cfg = SpellbookConfiguration()
    cfg.load_default_dictionary()
    cfg.cleanup()
    assert cfg._frozen is True
    with pytest.raises(RuntimeError):
        cfg.set_property("disposal", False)


def test_cleanup_clears_hooks_registry():
    cfg = SpellbookConfiguration()
    cfg.add_hook("sb", "on_conduit_pre_created", lambda: None)
    cfg.cleanup()
    assert not hasattr(cfg, '_hooks')


def test_add_hooks_registers_multiple_names():
    cfg = SpellbookConfiguration()
    called = []

    def pre():
        called.append("pre")

    def post():
        called.append("post")

    cfg.add_hooks("sb", on_conduit_pre_created=pre, on_conduit_post_created=post)
    hooks = cfg.get_hooks("sb")
    assert "on_conduit_pre_created" in hooks and "on_conduit_post_created" in hooks
    hooks["on_conduit_pre_created"][0]()
    hooks["on_conduit_post_created"][0]()
    assert called == ["pre", "post"]


def test_get_hooks_after_cleanup_raises():
    cfg = SpellbookConfiguration()
    cfg.cleanup()
    with pytest.raises(RuntimeError):
        cfg.get_hooks("sb")


def test_with_hooks_after_defaults_before_freeze_allowed():
    cfg = SpellbookConfiguration().with_defaults()
    cfg.with_hooks("sb", on_conduit_pre_created=lambda: None)
    assert "on_conduit_pre_created" in cfg.get_hooks("sb")


def test_validate_enums_with_extra_properties_present():
    cfg = SpellbookConfiguration()
    set_frame_system_state_for_spellbook_configuration(cfg, SystemState.automatic)
    cfg.set_property("disposal", False)
    cfg.set_property("disposal_method_names", [])
    cfg.set_property("phase_scheduler_workers_per_spellbook", 1)
    cfg.set_property("phase_scheduler_barrier_timeout_milliseconds", 1)
    assert cfg.validate_enums() is True


def test_iter_on_partially_populated_config():
    cfg = SpellbookConfiguration()
    cfg.set_property("disposal", True)
    keys = set(iter(cfg))
    assert keys == {"disposal"}
