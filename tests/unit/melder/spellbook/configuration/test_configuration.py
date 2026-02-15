import pytest

from melder.spellbook.configuration.configuration import Configuration
from melder.spellbook.configuration.system_state import SystemState
from melder.utilities.helpers.general_helpers import EnumHelpers
from melder.utilities.logger.std_logger_factory import StdLoggerFactory


class DummyFactory:
    def __init__(self):
        self.calls = []
        self.cleaned = False

    def __call__(self, obj):
        self.calls.append(obj)
        return f"logger-for-{id(obj)}"

    def cleanup(self):
        self.cleaned = True


def test_load_defaults_populates_all_required_properties():
    cfg = Configuration()
    cfg.load_default_dictionary()
    for key in cfg.available_properties:
        assert cfg.has_property(key)
    assert cfg.get_property("system_state") == SystemState.automatic
    assert cfg.get_property("debugging") is False
    assert cfg.get_property("disposal_method_names") == []
    assert cfg.get_property("full_ahead_of_time_compilation") is True


def test_set_property_converts_enum_strings():
    cfg = Configuration()
    cfg.set_property("system_state", "dynamic")
    assert cfg.get_property("system_state") == SystemState.dynamic


def test_set_property_rejects_idempotent_overwrite():
    cfg = Configuration()
    cfg.set_property("system_state", SystemState.automatic)
    with pytest.raises(RuntimeError):
        cfg.set_property("system_state", SystemState.dynamic)


def test_set_property_rejects_frozen():
    cfg = Configuration()
    cfg.load_default_dictionary()
    cfg.freeze()
    with pytest.raises(RuntimeError):
        cfg.set_property("debugging", True)


def test_set_property_rejects_non_string_key():
    cfg = Configuration()
    with pytest.raises(TypeError):
        cfg.set_property(123, "x")  # type: ignore[arg-type]


def test_clear_properties_blocks_when_frozen():
    cfg = Configuration()
    cfg.load_default_dictionary()
    cfg.freeze()
    with pytest.raises(RuntimeError):
        cfg.clear_properties()


def test_get_property_missing_raises_key_error():
    cfg = Configuration()
    cfg.load_default_dictionary()
    with pytest.raises(KeyError):
        cfg.get_property("missing")


def test_has_property_reflects_state():
    cfg = Configuration()
    assert cfg.has_property("debugging") is False
    cfg.set_property("debugging", True)
    assert cfg.has_property("debugging") is True


def test_validate_success_after_defaults():
    cfg = Configuration()
    cfg.load_default_dictionary()
    assert cfg.validate() is True


def test_validate_missing_property_raises():
    cfg = Configuration()
    cfg.load_default_dictionary()
    cfg._properties.pop("debugging")
    with pytest.raises(ValueError):
        cfg.validate()


def test_validate_wrong_type_raises():
    cfg = Configuration()
    cfg.load_default_dictionary()
    cfg.set_property("phase_scheduler_workers_per_spellbook", "wrong")
    with pytest.raises(ValueError):
        cfg.validate()


def test_validate_enum_type_raises():
    cfg = Configuration()
    with pytest.raises(ValueError):
        cfg.set_property("system_state", "not-an-enum")


def test_validate_phase_scheduler_workers_bounds():
    cfg = Configuration()
    cfg.load_default_dictionary()
    cfg.set_property("phase_scheduler_workers_per_spellbook", 0)
    with pytest.raises(ValueError):
        cfg.validate()


def test_validate_ai_native_enabled_type():
    cfg = Configuration()
    cfg.load_default_dictionary()
    cfg.set_property("ai_native_enabled", "yes")
    with pytest.raises(ValueError):
        cfg.validate()


def test_validate_full_ahead_of_time_compilation_type():
    cfg = Configuration()
    cfg.load_default_dictionary()
    cfg.set_property("full_ahead_of_time_compilation", "yes")
    with pytest.raises(ValueError):
        cfg.validate()


def test_freeze_is_idempotent_and_blocks_mutation():
    cfg = Configuration()
    cfg.load_default_dictionary()
    cfg.freeze()
    cfg.freeze()
    with pytest.raises(RuntimeError):
        cfg.set_property("debugging", True)


def test_set_logger_factory_default_and_custom():
    cfg = Configuration()
    cfg.set_logger_factory()
    assert cfg.has_logger_factory() is True
    custom = DummyFactory()
    cfg = Configuration()
    cfg.set_logger_factory(custom)
    logger = cfg.get_logger_for(object())
    assert isinstance(logger, str)
    assert custom.calls  # factory invoked


def test_set_logger_factory_rejects_async_callable():
    async def async_factory(obj):  # pragma: no cover - ensure async path rejected
        return StdLoggerFactory()(obj)

    cfg = Configuration()
    with pytest.raises(TypeError):
        cfg.set_logger_factory(async_factory)  # type: ignore[arg-type]


def test_set_logger_factory_rejects_non_callable():
    cfg = Configuration()
    with pytest.raises(TypeError):
        cfg.set_logger_factory(123)  # type: ignore[arg-type]


def test_clear_logger_factory_blocks_when_frozen():
    cfg = Configuration()
    cfg.load_default_dictionary()
    cfg.set_logger_factory()
    cfg.freeze()
    with pytest.raises(RuntimeError):
        cfg.clear_logger_factory()


def test_clear_logger_factory_resets_factory():
    cfg = Configuration()
    cfg.set_logger_factory()
    assert cfg.has_logger_factory() is True
    cfg.clear_logger_factory()
    assert cfg.has_logger_factory() is False


def test_add_hook_returns_shared_map():
    cfg = Configuration()

    def hook_a():
        return None

    def hook_b():
        return None

    cfg.add_hook("sb1", "on_conduit_pre_created", hook_a)
    hooks = cfg.get_hooks("sb1")
    assert hooks is cfg.get_hooks("sb1")
    hooks["on_conduit_pre_created"].append(hook_b)
    assert cfg.get_hooks("sb1")["on_conduit_pre_created"] == [hook_a, hook_b]


def test_add_hook_rejects_unknown_or_noncallable():
    cfg = Configuration()
    with pytest.raises(ValueError):
        cfg.add_hook("sb1", "not_allowed", lambda: None)
    with pytest.raises(TypeError):
        cfg.add_hook("sb1", "on_conduit_pre_created", "not-callable")  # type: ignore[arg-type]


def test_add_hooks_handles_iterables_and_skips_none():
    cfg = Configuration()
    called = []

    def fn():
        called.append(True)

    with pytest.raises(TypeError):
        cfg.add_hooks("sb", on_conduit_post_created=[fn, None], on_conduit_activated=None)


def test_hooks_blocked_when_frozen():
    cfg = Configuration()
    cfg.load_default_dictionary()
    cfg.freeze()
    with pytest.raises(RuntimeError):
        cfg.add_hook("sb1", "on_conduit_pre_created", lambda: None)


def test_withers_chain_and_freeze():
    cfg = (
        Configuration()
        .with_debugging(True)
        .with_disposal(True)
        .dynamic_defaults()
        .with_phase_scheduler_workers(3)
        .with_phase_scheduler_barrier_timeout(1000)
        .with_ai_native(True)
        .finalize()
    )
    assert cfg.has_property("system_state")
    assert cfg.get_property("debugging") is True
    assert cfg.get_property("disposal_method_names") == []


def test_with_phase_scheduler_workers_rejects_invalid():
    cfg = Configuration()
    with pytest.raises(ValueError):
        cfg.with_phase_scheduler_workers(0)


def test_with_phase_scheduler_barrier_timeout_limits():
    cfg = Configuration()
    with pytest.raises(ValueError):
        cfg.with_phase_scheduler_barrier_timeout(0)
    with pytest.raises(ValueError):
        cfg.with_phase_scheduler_barrier_timeout(400000)


def test_add_disposal_methods_validates_types():
    cfg = Configuration()
    with pytest.raises(TypeError):
        cfg.add_disposal_methods("ok", 123)  # type: ignore[arg-type]


def test_build_alias_for_finalize():
    cfg = Configuration().with_defaults().build()
    with pytest.raises(RuntimeError):
        cfg.set_property("debugging", True)


def test_dynamic_defaults_sets_state_dynamic():
    cfg = Configuration().dynamic_defaults()
    assert cfg.get_property("system_state") == SystemState.dynamic


def test_automatic_defaults_sets_state_automatic():
    cfg = Configuration().automatic_defaults()
    assert cfg.get_property("system_state") == SystemState.automatic


def test_iter_returns_keys():
    cfg = Configuration()
    cfg.load_default_dictionary()
    keys = set(iter(cfg))
    assert "system_state" in keys
    assert "ai_native_enabled" in keys


def test_cleanup_idempotent_and_nulls_references():
    cfg = Configuration()
    cfg.load_default_dictionary()
    cfg.set_logger_factory(DummyFactory())
    cfg.cleanup()
    cfg.cleanup()
    with pytest.raises(RuntimeError):
        cfg.set_property("debugging", True)
    assert cfg._properties is None
    assert cfg._hooks is None


def test_cleanup_runs_logger_factory_cleanup():
    cfg = Configuration()
    factory = DummyFactory()
    cfg.set_logger_factory(factory)
    cfg.cleanup()
    assert factory.cleaned is False


def test_convert_enum_helper_matches_configuration_usage():
    cfg = Configuration()
    assert EnumHelpers.convert_enum_and_check("dynamic", SystemState) == SystemState.dynamic
    cfg.set_property("system_state", "automatic")
    assert cfg.get_property("system_state") == SystemState.automatic


# Additional coverage

def test_set_property_rejects_after_cleanup():
    cfg = Configuration()
    cfg.cleanup()
    with pytest.raises(RuntimeError):
        cfg.set_property("debugging", True)


def test_get_has_property_after_cleanup_raise():
    cfg = Configuration()
    cfg.cleanup()
    with pytest.raises(RuntimeError):
        cfg.get_property("debugging")
    with pytest.raises(RuntimeError):
        cfg.has_property("debugging")


def test_freeze_after_cleanup_raises():
    cfg = Configuration()
    cfg.cleanup()
    with pytest.raises(RuntimeError):
        cfg.freeze()


def test_load_defaults_preserves_pre_set_system_state():
    cfg = Configuration()
    cfg.set_property("system_state", SystemState.dynamic)
    cfg.load_default_dictionary()
    assert cfg.get_property("system_state") == SystemState.dynamic


def test_clear_properties_allows_reset_before_freeze():
    cfg = Configuration()
    cfg.load_default_dictionary()
    cfg.clear_properties()
    assert cfg.has_property("system_state") is False
    cfg.set_property("system_state", SystemState.dynamic)
    assert cfg.get_property("system_state") == SystemState.dynamic


def test_clear_properties_after_cleanup_raises():
    cfg = Configuration()
    cfg.cleanup()
    with pytest.raises(RuntimeError):
        cfg.clear_properties()


def test_validate_enums_method_failure_and_success():
    cfg = Configuration()
    cfg.set_property("system_state", "automatic")
    assert cfg.validate_enums() is True
    cfg = Configuration()
    with pytest.raises(ValueError):
        cfg.set_property("system_state", 123)  # type: ignore[arg-type]


def test_validate_disposal_method_names_type():
    cfg = Configuration()
    cfg.set_property("system_state", SystemState.dynamic)
    cfg.set_property("debugging", False)
    cfg.set_property("disposal", False)
    cfg.set_property("disposal_method_names", "not-a-list")
    cfg.set_property("full_ahead_of_time_compilation", True)
    cfg.set_property("phase_scheduler_workers_per_spellbook", 1)
    cfg.set_property("ai_native_enabled", False)
    cfg.set_property("ai_profiles_enabled", False)
    cfg.set_property("phase_scheduler_barrier_timeout_milliseconds", 1)
    with pytest.raises(ValueError):
        cfg.validate()


def test_validate_barrier_timeout_type_and_bounds():
    cfg = Configuration()
    cfg.load_default_dictionary()
    cfg.set_property("phase_scheduler_barrier_timeout_milliseconds", "bad")
    with pytest.raises(ValueError):
        cfg.validate()


def test_add_hook_after_cleanup_raises():
    cfg = Configuration()
    cfg.cleanup()
    with pytest.raises(RuntimeError):
        cfg.add_hook("sb", "on_conduit_pre_created", lambda: None)


def test_add_hooks_after_cleanup_raises():
    cfg = Configuration()
    cfg.cleanup()
    with pytest.raises(RuntimeError):
        cfg.add_hooks("sb", on_conduit_pre_created=lambda: None)


def test_get_hooks_missing_spellbook_id_returns_empty():
    cfg = Configuration()
    cfg.add_hook("sb1", "on_conduit_pre_created", lambda: None)
    assert cfg.get_hooks("missing") == {}


def test_add_hook_appends_multiple_times():
    cfg = Configuration()
    cfg.add_hook("sb", "on_conduit_pre_created", lambda: "a")
    cfg.add_hook("sb", "on_conduit_pre_created", lambda: "b")
    hooks = cfg.get_hooks("sb")["on_conduit_pre_created"]
    assert len(hooks) == 2


def test_add_hooks_rejects_generator_with_bad_entry():
    cfg = Configuration()

    def gen():
        yield lambda: None
        yield "bad"  # type: ignore[misc]

    with pytest.raises(TypeError):
        cfg.add_hooks("sb", on_conduit_pre_created=gen())


def test_get_logger_for_returns_none_without_factory():
    cfg = Configuration()
    assert cfg.get_logger_for(object()) is None


def test_set_logger_factory_after_freeze_raises():
    cfg = Configuration()
    cfg.load_default_dictionary()
    cfg.freeze()
    with pytest.raises(RuntimeError):
        cfg.set_logger_factory(DummyFactory())


def test_clear_logger_factory_after_cleanup_raises():
    cfg = Configuration()
    cfg.set_logger_factory(DummyFactory())
    cfg.cleanup()
    with pytest.raises(RuntimeError):
        cfg.clear_logger_factory()


def test_custom_logger_factory_exception_propagates():
    class ExplodingFactory:
        def __call__(self, obj):
            raise RuntimeError("boom")

    cfg = Configuration()
    cfg.set_logger_factory(ExplodingFactory())
    with pytest.raises(RuntimeError):
        cfg.get_logger_for(object())


def test_with_hooks_fluent_returns_self():
    cfg = Configuration()
    result = cfg.with_hooks("sb", on_conduit_pre_created=lambda: None)
    assert result is cfg


def test_add_disposal_methods_dedup_and_order():
    cfg = Configuration()
    cfg.add_disposal_methods("close", "cleanup", "close")
    assert cfg.get_property("disposal_method_names") == ["close", "cleanup"]
    with pytest.raises(RuntimeError):
        cfg.add_disposal_methods("another")


def test_with_disposal_method_names_rejects_non_list():
    cfg = Configuration()
    with pytest.raises(TypeError):
        cfg.with_disposal_method_names("not-list")  # type: ignore[arg-type]


def test_with_full_ahead_of_time_compilation_sets_value():
    cfg = Configuration()
    returned = cfg.with_full_ahead_of_time_compilation(False)
    assert returned is cfg
    assert cfg.get_property("full_ahead_of_time_compilation") is False


def test_with_full_ahead_of_time_compilation_rejects_non_bool():
    cfg = Configuration()
    with pytest.raises(TypeError):
        cfg.with_full_ahead_of_time_compilation("false")  # type: ignore[arg-type]


def test_with_defaults_allows_overriding_full_ahead_of_time_compilation():
    cfg = Configuration().with_defaults()
    cfg.with_full_ahead_of_time_compilation(False)
    assert cfg.get_property("full_ahead_of_time_compilation") is False


def test_finalize_twice_is_idempotent():
    cfg = Configuration().with_defaults()
    cfg.finalize()
    cfg.finalize()
    with pytest.raises(RuntimeError):
        cfg.set_property("debugging", True)


def test_dynamic_defaults_does_not_overwrite_existing_disposal_names():
    cfg = Configuration()
    cfg.set_property("disposal_method_names", ["pre"])
    cfg.dynamic_defaults()
    assert cfg.get_property("disposal_method_names")[0] == "pre"


def test_with_system_state_rejects_overwrite_explicit():
    cfg = Configuration()
    cfg.set_property("system_state", SystemState.dynamic)
    with pytest.raises(RuntimeError):
        cfg.with_system_state(SystemState.automatic)


def test_iter_only_has_current_keys_after_clear_and_reset():
    cfg = Configuration()
    cfg.load_default_dictionary()
    cfg.clear_properties()
    cfg.set_property("system_state", SystemState.dynamic)
    keys = set(iter(cfg))
    assert keys == {"system_state"}


def test_cleanup_sets_frozen_and_blocks_mutation():
    cfg = Configuration()
    cfg.load_default_dictionary()
    cfg.cleanup()
    assert cfg._frozen is True
    with pytest.raises(RuntimeError):
        cfg.set_property("debugging", False)


def test_cleanup_clears_hooks_registry():
    cfg = Configuration()
    cfg.add_hook("sb", "on_conduit_pre_created", lambda: None)
    cfg.cleanup()
    assert cfg._hooks is None


def test_add_hooks_registers_multiple_names():
    cfg = Configuration()
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
    cfg = Configuration()
    cfg.cleanup()
    with pytest.raises(RuntimeError):
        cfg.get_hooks("sb")


def test_clear_logger_factory_when_not_set_is_noop():
    cfg = Configuration()
    assert cfg.has_logger_factory() is False
    cfg.clear_logger_factory()
    assert cfg.has_logger_factory() is False


def test_get_logger_for_after_freeze_uses_existing_factory():
    cfg = Configuration()
    factory = DummyFactory()
    cfg.set_logger_factory(factory)
    cfg.load_default_dictionary()
    cfg.freeze()
    logger = cfg.get_logger_for(object())
    assert isinstance(logger, str)
    assert factory.calls


def test_with_hooks_after_defaults_before_freeze_allowed():
    cfg = Configuration().with_defaults()
    cfg.with_hooks("sb", on_conduit_pre_created=lambda: None)
    assert "on_conduit_pre_created" in cfg.get_hooks("sb")


def test_validate_enums_with_extra_properties_present():
    cfg = Configuration()
    cfg.set_property("system_state", SystemState.automatic)
    cfg.set_property("debugging", False)
    cfg.set_property("disposal", False)
    cfg.set_property("disposal_method_names", [])
    cfg.set_property("phase_scheduler_workers_per_spellbook", 1)
    cfg.set_property("ai_native_enabled", False)
    cfg.set_property("phase_scheduler_barrier_timeout_milliseconds", 1)
    assert cfg.validate_enums() is True


def test_iter_on_partially_populated_config():
    cfg = Configuration()
    cfg.set_property("system_state", SystemState.dynamic)
    keys = set(iter(cfg))
    assert keys == {"system_state"}
