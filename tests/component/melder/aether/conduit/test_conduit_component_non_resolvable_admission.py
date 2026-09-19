"""Direct runtime admission preserves discovery while refusing non-resolvable registrations."""

from collections.abc import Iterator
from typing import ClassVar, Optional, Union

import pytest

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.conduit.spell_space.spell_space import SpellSpace
from melder.aether.spellbook.configuration.spellbook_configuration import (
    SpellbookConfiguration,
)
from melder.aether.spellbook.spellbook import Spellbook
from melder.utilities.custom_exceptions.meld_execution_error import MeldExecutionError
from tests._frame_posture_test_support import (
    configure_frame_posture_for_spellbook_configuration,
)


class RuntimeDefinition:
    """Application definition whose construction counter exposes accidental runtime invocation."""

    calls: ClassVar[int] = 0

    def __init__(self, value: int = 11) -> None:
        """Record a construction and preserve its argument for ordinary resolvable controls."""
        RuntimeDefinition.calls += 1
        self.value = value


class RuntimeProvider(RuntimeDefinition):
    """Separate executable provider must not replace an explicitly selected False definition."""


@pytest.fixture(autouse=True)
def reset_admission_world() -> Iterator[None]:
    """Isolate the Aether world and reset class diagnostics before and after every runtime scenario."""
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether
    RuntimeDefinition.calls = 0
    try:
        yield
    finally:
        Aether._reset_singleton_for_tests()
        aether = Aether()
        Spellbook._aether = aether
        Conduit._aether = aether


def _make_book(dynamic: bool = False) -> Spellbook:
    """Create a deterministic real book with explicit frame posture and disk caching disabled."""
    configuration = SpellbookConfiguration()
    configuration.load_default_dictionary()
    configuration.set_property("phase_scheduler_workers_per_spellbook", 1)
    frame = configure_frame_posture_for_spellbook_configuration(configuration, dynamic=dynamic)
    frame.with_system_caching_enabled(False)
    return Spellbook(configuration=configuration)


def _meld_selected(
    runtime: Union[Conduit, SpellSpace], selector: str, spell_id: str,
) -> object:
    """Use each supported public selector while keeping machine IDs separate from human names."""
    if selector == "id":
        return runtime.meld(spell_id=spell_id)
    if selector == "name":
        return runtime.meld("RuntimeDefinition")
    if selector == "frame":
        return runtime.meld(spellframe=RuntimeDefinition)
    if selector == "named":
        return runtime.meld(RuntimeDefinition, binding_name="definition")
    return runtime.meld(RuntimeDefinition)


@pytest.mark.parametrize("dynamic", [False, True])
@pytest.mark.parametrize("scoped", [False, True])
@pytest.mark.parametrize("validation_required", [False, True])
@pytest.mark.parametrize("selector", ["id", "name", "class", "frame", "named"])
def test_false_target_refuses_every_public_selector_before_optional_validation(
    dynamic: bool, scoped: bool, validation_required: bool, selector: str,
) -> None:
    """Repeated False resolution must retain its explicit diagnostic across modes, scopes and lookup caches."""
    book = _make_book(dynamic)
    spell_id = book.bind(
        spell=RuntimeDefinition, existence="unique", resolvable=False,
        binding_name="definition" if selector == "named" else None,
    )
    conduit = book.conjure(dynamic=dynamic)
    runtime = conduit.create_spellspace() if scoped else conduit
    # This is the optional validation gate under test, not a capability mutation.
    book._spellbook_validation_required = validation_required
    for _attempt in range(2):
        with pytest.raises(MeldExecutionError, match="resolvable=False") as raised:
            _meld_selected(runtime, selector, spell_id)
        assert raised.value.spell_id == spell_id
        assert raised.value.spell_name
        assert "override" in str(raised.value)
    assert RuntimeDefinition.calls == 0
    status = conduit.describe_live_creation_status(spell=spell_id)
    assert status["spell_id"] == spell_id
    assert status["is_live"] is False


@pytest.mark.parametrize("scoped", [False, True])
@pytest.mark.parametrize("existing_object", [False, True])
def test_false_target_refuses_reuse_even_when_user_object_is_already_present(
    scoped: bool, existing_object: bool,
) -> None:
    """Reuse-only resolution must enforce capability before either stored-object return or missing-live errors."""
    book = _make_book()
    supplied = RuntimeDefinition() if existing_object else None
    target = supplied if supplied is not None else RuntimeDefinition
    spell_id = book.bind(spell=target, existence="unique", resolvable=False)
    conduit = book.conjure()
    calls_before = RuntimeDefinition.calls
    if scoped:
        # SpellSpace exposes meld publicly; reuse-only belongs to its internal concrete door.
        door = conduit.create_spellspace()._meld
        with pytest.raises(MeldExecutionError, match="resolvable=False"):
            door.meld_existing_spell(spell=spell_id)
    else:
        with pytest.raises(MeldExecutionError, match="resolvable=False"):
            conduit.meld_existing_spell(spell=spell_id)
    assert RuntimeDefinition.calls == calls_before
    assert conduit.has_live_creation(spell=spell_id) is existing_object


@pytest.mark.parametrize("scoped", [False, True])
@pytest.mark.parametrize("override", [None, {}, {"value": 19}, [19], (19,)])
def test_false_target_override_cannot_enable_resolution_or_run_hooks(
    scoped: bool,
    override: Optional[Union[dict[str, object], list[object], tuple[object, ...]]],
) -> None:
    """An override payload does not grant capability, and refusal precedes pre-resolve hook effects."""
    events: list[str] = []

    def before_resolve(*_args: object) -> None:
        """Record an execution hook effect that must not occur for the False registration."""
        events.append("pre")

    book = _make_book()
    spell_id = book.bind(spell=RuntimeDefinition, existence="unique", resolvable=False)
    conduit = book.conjure()
    runtime = conduit.create_spellspace() if scoped else conduit
    runtime._meld.set_meld_hooks({"on_meld_pre_resolve": [before_resolve]})
    with pytest.raises(MeldExecutionError, match="resolvable=False"):
        runtime.meld(spell_id=spell_id, override=override)
    assert events == []
    assert RuntimeDefinition.calls == 0


@pytest.mark.parametrize("scoped", [False, True])
def test_explicit_false_selection_does_not_fall_back_to_a_resolvable_provider(scoped: bool) -> None:
    """A separately bound True provider stays resolvable while direct False selection remains a refusal."""
    book = _make_book()
    definition_id = book.bind(
        spell=RuntimeDefinition, binding_name="definition", existence="unique", resolvable=False,
    )
    provider_id = book.bind(
        spell=RuntimeProvider, spellframe=RuntimeDefinition, binding_name="runtime", existence="unique",
    )
    conduit = book.conjure()
    runtime = conduit.create_spellspace() if scoped else conduit
    with pytest.raises(MeldExecutionError, match="resolvable=False"):
        runtime.meld(spell_id=definition_id)
    first = runtime.meld(spell_id=provider_id)
    assert isinstance(first, RuntimeProvider)
    assert runtime.meld(spell_id=provider_id) is first
    assert RuntimeDefinition.calls == 1


@pytest.mark.parametrize("scoped", [False, True])
def test_notch_to_false_invalidates_cached_name_selection_without_mutating_capability(scoped: bool) -> None:
    """A legitimate version selection change must refuse the new False member after prior True use."""
    book = _make_book(dynamic=True)
    original_id = book.bind(spell=RuntimeDefinition, existence="unique")
    original = book._spells_by_id[original_id]
    conduit = book.conjure(dynamic=True)
    runtime = conduit.create_spellspace() if scoped else conduit
    first = runtime.meld(RuntimeDefinition)
    assert first.value == 11
    false_id = conduit.bind_inactive(
        spell=RuntimeDefinition, spell_index=original.spell_index, existence="unique", resolvable=False,
    )
    false_version = book._inactive_spells[false_id]
    conduit.notch_spell(spell_index=original.spell_index, spell=false_version)
    with pytest.raises(MeldExecutionError, match="resolvable=False") as raised:
        runtime.meld(RuntimeDefinition)
    assert raised.value.spell_id == false_id
    assert RuntimeDefinition.calls == 1
