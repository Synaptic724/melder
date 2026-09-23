"""Configuration hook defaults are immutable seeds, with per-Book event precedence."""

from collections.abc import Iterator

import pytest

from melder.aether.spellbook.configuration.spellbook_configuration import (
    SpellbookConfiguration,
)


@pytest.fixture()
def configuration() -> Iterator[SpellbookConfiguration]:
    """Provide mutable defaults and always release configuration-owned references."""
    config = SpellbookConfiguration().with_defaults()
    try:
        yield config
    finally:
        config.cleanup()


@pytest.mark.parametrize("stage, position", [("pre", 0), ("activation", 1), ("post", 2)])
def test_bind_defaults_preserve_order_duplicates_and_captured_sets(
    configuration: SpellbookConfiguration, stage: str, position: int,
) -> None:
    """Appending or clearing replaces the seed set without mutating earlier captures."""
    first: list[object] = []
    second: list[object] = []
    assert configuration.get_bind_hooks() == ((), (), ())
    assert configuration.with_bind_hooks(**{stage: [first.append]}) is configuration
    captured = configuration.get_bind_hooks()
    configuration.add_bind_hooks(**{stage: [second.append, first.append]})
    for callback in configuration.get_bind_hooks()[position]:
        callback("value")
    assert first == ["value", "value"]
    assert second == ["value"]
    configuration.clear_bind_hooks()
    assert configuration.get_bind_hooks() == ((), (), ())
    captured[position][0]("retained")
    assert first == ["value", "value", "retained"]


@pytest.mark.parametrize("invalid_stage", ["pre", "activation", "post"])
def test_invalid_bind_batch_changes_no_stage(
    configuration: SpellbookConfiguration, invalid_stage: str,
) -> None:
    """A late invalid callback must not partially append earlier stages."""
    calls: list[object] = []
    configuration.add_bind_hooks(pre=[calls.append])
    before = configuration.get_bind_hooks()
    batch = {"pre": [calls.append], "activation": [calls.append], "post": [calls.append]}
    batch[invalid_stage] = [None]
    with pytest.raises(TypeError, match="callable"):
        configuration.add_bind_hooks(**batch)
    assert configuration.get_bind_hooks() is before


@pytest.mark.parametrize("operation", ["append", "clear", "fluent"])
def test_frozen_configuration_refuses_bind_default_changes(
    configuration: SpellbookConfiguration, operation: str,
) -> None:
    """Freezing seals seeds, including attempted empty changes."""
    calls: list[object] = []
    configuration.add_bind_hooks(pre=[calls.append])
    captured = configuration.get_bind_hooks()
    configuration.freeze()
    with pytest.raises(RuntimeError, match="frozen"):
        if operation == "append":
            configuration.add_bind_hooks()
        elif operation == "clear":
            configuration.clear_bind_hooks()
        else:
            configuration.with_bind_hooks(post=[calls.append])
    assert configuration.get_bind_hooks() is captured


def test_cleaned_configuration_releases_seeds_without_destroying_captured_callbacks(
    configuration: SpellbookConfiguration,
) -> None:
    """Retained immutable seeds remain callable; the cleaned config refuses all access."""
    calls: list[object] = []
    configuration.add_bind_hooks(pre=[calls.append])
    captured = configuration.get_bind_hooks()
    configuration.cleanup()
    with pytest.raises(RuntimeError):
        configuration.get_bind_hooks()
    with pytest.raises(RuntimeError):
        configuration.add_bind_hooks()
    with pytest.raises(RuntimeError):
        configuration.clear_bind_hooks()
    captured[0][0]("still-borrowed")
    assert calls == ["still-borrowed"]


@pytest.mark.parametrize("event", ["on_conduit_post_link", "on_meld_pre_resolve"])
def test_book_specific_event_replaces_only_its_default(
    configuration: SpellbookConfiguration, event: str,
) -> None:
    """Effective maps override one event while preserving defaults for other events."""
    defaults: list[object] = []
    local: list[object] = []
    configuration.with_hooks(**{event: defaults.append})
    configuration.add_hooks(on_conduit_post_unlink=defaults.append)
    configuration.with_hook("specific", event, local.append)
    assert configuration.get_hooks("other")[event] == [defaults.append]
    effective = configuration.get_hooks("specific")
    assert effective[event] == [local.append]
    assert effective["on_conduit_post_unlink"] == [defaults.append]
    effective[event].clear()
    assert configuration.get_hooks("specific")[event] == [local.append]


@pytest.mark.parametrize("event", ["on_conduit_activated", "on_meld_post_resolve"])
def test_explicit_none_single_hook_applies_to_future_books(
    configuration: SpellbookConfiguration, event: str,
) -> None:
    """The existing singular hook APIs accept None as the default Book key."""
    calls: list[object] = []
    configuration.add_hook(None, event, calls.append)
    configuration.with_hook(None, event, calls.append)
    assert configuration.get_hooks("future")[event] == [calls.append, calls.append]


@pytest.mark.parametrize("invalid", ["unknown", "value", "list"])
def test_invalid_runtime_hook_batch_preserves_all_existing_events(
    configuration: SpellbookConfiguration, invalid: str,
) -> None:
    """Default runtime hook registration validates the full batch before publication."""
    calls: list[object] = []
    configuration.add_hooks(on_conduit_post_link=calls.append)
    before = configuration.get_hooks("future")
    bad = {
        "unknown": {"not_a_hook": calls.append},
        "value": {"on_meld_pre_resolve": 7},
        "list": {"on_meld_pre_resolve": [calls.append, None]},
    }[invalid]
    with pytest.raises((ValueError, TypeError)):
        configuration.add_hooks(on_conduit_activated=calls.append, **bad)
    assert configuration.get_hooks("future") == before


def test_runtime_default_getters_keep_existing_live_map_contract(
    configuration: SpellbookConfiguration,
) -> None:
    """No merge preserves live map identity; a merged map still borrows event lists."""
    calls: list[object] = []
    configuration.add_hooks(on_meld_pre_resolve=calls.append)
    defaults = configuration.get_meld_hooks("one")
    assert configuration.get_meld_hooks("two") is defaults
    configuration.add_hooks("one", on_meld_post_resolve=calls.append)
    effective = configuration.get_meld_hooks("one")
    assert effective is not defaults
    assert effective["on_meld_pre_resolve"] is defaults["on_meld_pre_resolve"]
    assert set(effective) == {"on_meld_pre_resolve", "on_meld_post_resolve"}
