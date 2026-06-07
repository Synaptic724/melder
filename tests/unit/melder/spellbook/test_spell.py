from melder.aether.aetheric_frame.dev_ops.spell_system_states.spell_state_change_reason import (
    SpellStateChangeReason,
)
from melder.aether.spellbook.spell_compiler.spell_examiner.profiles.general_profile import (
    SpellGeneralProfile,
)
from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.synchronization.creation_gate_controller import (
    CreationGateController,
)


class _SpellbookStub:
    """
    Minimal Spellbook stand-in that only exposes SpellSystemStates for Spell construction.
    """

    def __init__(self, states):
        self._spell_system_states = states

    def cleanup_and_remove_spell(self, spell):
        spell_index = spell.spell_index
        spell._spellbook_cleanup = True
        spell.cleanup()
        try:
            spell_index.cleanup()
        except Exception:
            pass


class _RecordingStates:
    """
    Records structural change requests from Spell mutation hooks.
    """

    def __init__(self):
        self.calls: list[tuple[SpellIndex, SpellStateChangeReason]] = []

    def mark_structural_change(self, spell_index, reason=SpellStateChangeReason.structure_changed):
        self.calls.append((spell_index, reason))

    def get_by_index_id(self, index_id):  # pragma: no cover - exposed for completeness
        return f"state:{index_id}"


class _CleanableProfile(Cleanable):
    """
    Cleanable stub used to verify Spell cleanup propagation.
    """

    def __init__(self):
        super().__init__()
        self.cleaned = False

    def cleanup(self):
        self.cleaned = True
        self._cleaned = True


class _Disposable:
    """
    Disposable stub that mirrors the cleanup contract used on attached artifacts.
    """

    def __init__(self):
        self.cleaned = False

    def cleanup(self):
        self.cleaned = True


def test_spell_key_and_type_flags():
    """
    Ensures Spell builds normalized lookup keys and class/type flags when a spellframe and binding are provided.
    """

    class Frame:
        pass

    states = _RecordingStates()
    spell = Spell(
        spell=Frame,
        spell_index=SpellIndex("version-1"),
        spellframe=Frame,
        binding_name="DB",
        spell_name="Frame",
        existence=Existence.unique,
        spell_type=SpellType.SPELL_WITH_BINDING_NAME_WITH_SPELLFRAME,
        spell_id="fingerprint",
        permissions=Permissions.read,
        aetheric_frame="default",
        spellbook=_SpellbookStub(states),
    )

    assert spell.key == ("frame", "db")
    assert spell.is_class_spell is True
    assert spell.is_method_spell is False
    assert spell.is_lambda_spell is False
    assert spell.is_existing_creation is False


def test_existing_creation_flags_and_existing_object_presence():
    """
    Verifies existing-creation spells set the expected flags and preserve provided instances.
    """

    existing = object()
    spell = Spell(
        spell=existing,
        spell_index=SpellIndex("existing-id"),
        spellframe=None,
        binding_name=None,
        spell_name="ExistingSpell",
        existence=Existence.unique,
        spell_type=SpellType.EXISTING_CREATION,
        spell_id="existing-fingerprint",
        permissions=Permissions.read,
        aetheric_frame="default",
        spellbook=_SpellbookStub(_RecordingStates()),
        existing_object=existing,
    )

    assert spell.key == ("existingspell", "__default__")
    assert spell.is_existing_creation is True
    assert spell.has_existing_object is True
    assert spell.is_class_spell is False
    assert spell.is_method_spell is False
    assert spell.is_lambda_spell is False


def test_mutation_override_updates_payload_without_structural_change_signal():
    """
    Applying and clearing mutation overlays should update payloads without
    signaling structural invalidation.
    """

    states = _RecordingStates()
    spell = Spell(
        spell=lambda: None,
        spell_index=SpellIndex("mutation-id"),
        spellframe=None,
        binding_name=None,
        spell_name="MutatingSpell",
        existence=Existence.unique,
        spell_type=SpellType.SPELL,
        spell_id="mutation-fingerprint",
        permissions=Permissions.read,
        aetheric_frame="default",
        spellbook=_SpellbookStub(states),
    )

    spell._dynamic_environment = True
    spell.apply_mutation_override({"mode": "overlay"})
    assert spell.mutation_override == {"mode": "overlay"}
    assert states.calls == []

    spell.apply_mutation_override(None)
    assert spell.mutation_override is None
    assert states.calls == []


def test_clear_mutation_override_is_noop_when_empty():
    """
    Clearing mutation overlays when none are set should avoid signaling DevOps state changes.
    """

    states = _RecordingStates()
    spell = Spell(
        spell=lambda: None,
        spell_index=SpellIndex("noop-id"),
        spellframe=None,
        binding_name=None,
        spell_name="NoOpSpell",
        existence=Existence.unique,
        spell_type=SpellType.SPELL,
        spell_id="noop-fingerprint",
        permissions=Permissions.read,
        aetheric_frame="default",
        spellbook=_SpellbookStub(states),
    )

    spell._dynamic_environment = True
    spell.clear_mutation_override()
    assert spell.mutation_override is None
    assert states.calls == []


def test_cleanup_disposes_artifacts_and_nulls_references():
    """
    Spell.cleanup should dispose attached artifacts, clean the lineage handle, and null internal references.
    """

    cleanup_calls = []

    class _TrackingSpellIndex(SpellIndex):
        __slots__ = ()

        def cleanup(self):
            cleanup_calls.append("spell_index")
            super().cleanup()

    dependency_graph = _Disposable()
    resolution_profile = _CleanableProfile()
    binding_profile = _CleanableProfile()

    spell = Spell(
        spell=lambda: None,
        spell_index=_TrackingSpellIndex("cleanup-id"),
        spellframe=None,
        binding_name=None,
        spell_name="CleanupSpell",
        existence=Existence.unique,
        spell_type=SpellType.SPELL,
        spell_id="cleanup-fingerprint",
        permissions=Permissions.create,
        aetheric_frame="default",
        spellbook=_SpellbookStub(_RecordingStates()),
    )

    # Attach disposable artifacts
    spell.dependency_graph = dependency_graph
    general_profile = SpellGeneralProfile(
        binding_profile=binding_profile,
        resolution_profile=resolution_profile,
    )
    spell.profile = general_profile
    spell._crafter = crafter  # internal attachment mimics SpellCrafter ownership

    spell.cleanup()

    assert dependency_graph.cleaned is True
    assert resolution_profile.cleaned is True
    assert binding_profile.cleaned is True
    assert not hasattr(spell, "profile")
    assert cleanup_calls == ["spell_index"]

    assert spell._cleaned is True
    assert spell._lock is not None
    assert not hasattr(spell, "spell")
    assert not hasattr(spell, "spell_index")
    assert not hasattr(spell, "_mutation_override")
    assert not hasattr(spell, "_pre_hooks")
    assert not hasattr(spell, "metadata")
    assert not hasattr(spell, "_spell_system_states")
import sys
import types

import pytest

from melder.aether.conduit.conduit_ward.permissions.permissions import Permissions
from melder.aether.aetheric_frame.dev_ops.spell_system_states.spell_state_change_reason import (
    SpellStateChangeReason,
)
from melder.aether.spellbook.bind.spell_index import SpellIndex
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spell import Spell
from melder.aether.spellbook.spell_types.spell_types import SpellType
from melder.utilities.general_base.cleanable import Cleanable


class _SpellbookStub:
    def __init__(self, states):
        self._spell_system_states = states

    def cleanup_and_remove_spell(self, spell):
        spell_index = spell.spell_index
        spell._spellbook_cleanup = True
        spell.cleanup()
        try:
            spell_index.cleanup()
        except Exception:
            pass


class _RecordingStates:
    def __init__(self):
        self.calls: list[tuple[SpellIndex, SpellStateChangeReason]] = []

    def mark_structural_change(self, spell_index, reason=SpellStateChangeReason.structure_changed):
        self.calls.append((spell_index, reason))

    def get_by_index_id(self, index_id):
        return f"state:{index_id}"


class _CleanableProfile(Cleanable):
    def __init__(self):
        super().__init__()
        self.was_cleaned = False

    def cleanup(self):
        self.was_cleaned = True
        self._cleaned = True


class _FailingCleanableProfile(Cleanable):
    def __init__(self):
        super().__init__()

    def cleanup(self):
        raise RuntimeError("profile cleanup boom")


class _Disposable:
    def __init__(self, fail_on_cleanup: bool = False):
        self.cleaned = False
        self.fail_on_cleanup = fail_on_cleanup

    def cleanup(self):
        self.cleaned = True
        if self.fail_on_cleanup:
            raise RuntimeError("cleanup boom")


class _DummyCrafter:
    """
    Purpose:
        Provide a SpellCrafter stub for phase sequencing tests.
    Contract:
        Records phase invocation order and captures cancel events.
    """
    def __init__(self):
        """
        Purpose:
            Initialize tracking state for phase calls.
        Contract:
            Sets phase output placeholders and call tracking fields.
        Returns:
            None.
        """
        self.calls: list[str] = []
        self.seen_cancel_events = []
        self.requirements = "req"
        self.symbolic_graph = "sym"
        self.resolution_frame = "frame"
        self.validation_result_phase4 = "p4"
        self.validation_result_phase6 = "p6"

        self.validated = True
        self.is_broken = False

    def run_phase_requirements(self, cancel_event=None):
        """
        Purpose:
            Record Phase 1 invocation.
        Contract:
            Appends the phase name and stores the cancel event.
        Args:
            cancel_event: Cancellation event passed by the caller.
        Returns:
            None.
        """
        self.calls.append("requirements")
        self.seen_cancel_events.append(cancel_event)

    def run_phase_symbolic_graph(self, cancel_event=None):
        """
        Purpose:
            Record Phase 2 invocation.
        Contract:
            Appends the phase name and stores the cancel event.
        Args:
            cancel_event: Cancellation event passed by the caller.
        Returns:
            None.
        """
        self.calls.append("symbolic_graph")
        self.seen_cancel_events.append(cancel_event)

    def run_phase_local_frame(self, cancel_event=None):
        """
        Purpose:
            Record Phase 3 invocation.
        Contract:
            Appends the phase name and stores the cancel event.
        Args:
            cancel_event: Cancellation event passed by the caller.
        Returns:
            None.
        """
        self.calls.append("local_frame")
        self.seen_cancel_events.append(cancel_event)

    def run_phase_validation(self, cancel_event=None):
        """
        Purpose:
            Record Phase 4 invocation.
        Contract:
            Appends the phase name and stores the cancel event.
        Args:
            cancel_event: Cancellation event passed by the caller.
        Returns:
            None.
        """
        self.calls.append("validation")
        self.seen_cancel_events.append(cancel_event)

    def run_phase_root_blueprints(self, conduit_id, cancel_event=None):
        """
        Purpose:
            Record Phase 5 invocation.
        Contract:
            Appends the phase name, stores conduit id, and stores the cancel event.
        Args:
            conduit_id: Conduit identifier passed by the caller.
            cancel_event: Cancellation event passed by the caller.
        Returns:
            None.
        """
        self.calls.append("root_blueprints")
        self.seen_cancel_events.append((conduit_id, cancel_event))

    def run_phase_root_blueprints_local(self, conduit_id, cancel_event=None):
        """
        Purpose:
            Record local Phase 5 invocation.
        Contract:
            Appends the phase name, stores conduit id, and stores the cancel event.
        Args:
            conduit_id: Conduit identifier passed by the caller.
            cancel_event: Cancellation event passed by the caller.
        Returns:
            None.
        """
        self.calls.append("root_blueprints_local")
        self.seen_cancel_events.append((conduit_id, cancel_event))

    def run_phase_occurrence_plan(self, conduit_id, cancel_event=None):
        """
        Purpose:
            Record Phase 8 invocation.
        Contract:
            Appends the phase name, stores conduit id, and stores the cancel event.
        Args:
            conduit_id: Conduit identifier passed by the caller.
            cancel_event: Cancellation event passed by the caller.
        Returns:
            None.
        """
        self.calls.append("occurrence_plan")
        self.seen_cancel_events.append((conduit_id, cancel_event))

    def run_phase_system_validation(self, conduit_id, cancel_event=None):
        """
        Purpose:
            Record Phase 6 invocation.
        Contract:
            Appends the phase name, stores conduit id, and stores the cancel event.
        Args:
            conduit_id: Conduit identifier passed by the caller.
            cancel_event: Cancellation event passed by the caller.
        Returns:
            None.
        """
        self.calls.append("system_validation")
        self.seen_cancel_events.append((conduit_id, cancel_event))

    def run_phase_system_validation_local(self, conduit_id, cancel_event=None):
        """
        Purpose:
            Record local Phase 6 invocation.
        Contract:
            Appends the phase name, stores conduit id, and stores the cancel event.
        Args:
            conduit_id: Conduit identifier passed by the caller.
            cancel_event: Cancellation event passed by the caller.
        Returns:
            None.
        """
        self.calls.append("system_validation_local")
        self.seen_cancel_events.append((conduit_id, cancel_event))

    def run_phase_change_control(self, conduit_id, cancel_event=None):
        """
        Purpose:
            Record Phase 7 invocation.
        Contract:
            Appends the phase name, stores conduit id, and stores the cancel event.
        Args:
            conduit_id: Conduit identifier passed by the caller.
            cancel_event: Cancellation event passed by the caller.
        Returns:
            None.
        """
        self.calls.append("change_control")
        self.seen_cancel_events.append((conduit_id, cancel_event))

    def run_phase_change_control_local(self, conduit_id, cancel_event=None):
        """
        Purpose:
            Record local Phase 7 invocation.
        Contract:
            Appends the phase name, stores conduit id, and stores the cancel event.
        Args:
            conduit_id: Conduit identifier passed by the caller.
            cancel_event: Cancellation event passed by the caller.
        Returns:
            None.
        """
        self.calls.append("change_control_local")
        self.seen_cancel_events.append((conduit_id, cancel_event))

    def run_phase_injection_plan(self, conduit_id, cancel_event=None):
        """
        Purpose:
            Record Phase 9 invocation.
        Contract:
            Appends the phase name, stores conduit id, and stores the cancel event.
        Args:
            conduit_id: Conduit identifier passed by the caller.
            cancel_event: Cancellation event passed by the caller.
        Returns:
            None.
        """
        self.calls.append("injection_plan")
        self.seen_cancel_events.append((conduit_id, cancel_event))

    def run_phase_patch_maps(self, conduit_id, cancel_event=None):
        """
        Purpose:
            Record Phase 10 invocation.
        Contract:
            Appends the phase name, stores conduit id, and stores the cancel event.
        Args:
            conduit_id: Conduit identifier passed by the caller.
            cancel_event: Cancellation event passed by the caller.
        Returns:
            None.
        """
        self.calls.append("patch_maps")
        self.seen_cancel_events.append((conduit_id, cancel_event))

    def run_phase_execution_plan(self, conduit_id, cancel_event=None):
        """
        Purpose:
            Record Phase 11 invocation.
        Contract:
            Appends the phase name, stores conduit id, and stores the cancel event.
        Args:
            conduit_id: Conduit identifier passed by the caller.
            cancel_event: Cancellation event passed by the caller.
        Returns:
            None.
        """
        self.calls.append("execution_plan")
        self.seen_cancel_events.append((conduit_id, cancel_event))

    def cleanup_phase_artifacts(self):
        """
        Purpose:
            Record phase artifact cleanup.
        Contract:
            Appends cleanup marker and clears phase artifacts.
        Returns:
            None.
        """
        self.calls.append("cleanup_phase_artifacts")
        self.requirements = None
        self.symbolic_graph = None
        self.resolution_frame = None
        self.validation_result_phase4 = None
        self.validation_result_phase6 = None

    def cleanup(self):
        """
        Purpose:
            Track cleanup invocation.
        Contract:
            Appends "cleanup" to the calls list.
        Returns:
            None.
        """
        self.calls.append("cleanup")


def _make_spell(
        *,
        spell=object,
        spellframe=None,
        binding_name=None,
        spell_name="SampleSpell",
        existence=Existence.unique,
        spell_type=SpellType.SPELL,
        spell_id="fingerprint",
        permissions=Permissions.read,
        states=None,
        profile=None,
        existing_object=None,
        dynamic_environment: bool = False,
):
    states = states or _RecordingStates()
    spell = Spell(
        spell=spell,
        spell_index=SpellIndex(spell_id),
        spellframe=spellframe,
        binding_name=binding_name,
        spell_name=spell_name,
        existence=existence,
        spell_type=spell_type,
        spell_id=spell_id,
        permissions=permissions,
        aetheric_frame="default",
        spellbook=_SpellbookStub(states),
        profile=profile,
        existing_object=existing_object,
    )
    spell._dynamic_environment = dynamic_environment
    return spell


def test_spell_hooks_default_state() -> None:
    """
    Verify Spell initializes with hooks disabled and empty hook lists.
    """
    spell = _make_spell()
    assert spell._hooks_enabled is False
    assert spell._pre_hooks == []
    assert spell._activation_hooks == []
    assert spell._post_hooks == []


def test_spell_set_hooks_updates_lists_and_enables() -> None:
    """
    Verify _set_hooks replaces hook lists and enables hook gating.
    """
    spell = _make_spell()
    pre_hook = lambda: None
    activation_hook = lambda _: None
    post_hook = lambda: None

    spell._set_hooks(
        pre_hooks=[pre_hook],
        activation_hooks=[activation_hook],
        post_hooks=[post_hook],
    )

    assert spell._pre_hooks == [pre_hook]
    assert spell._activation_hooks == [activation_hook]
    assert spell._post_hooks == [post_hook]
    assert spell._hooks_enabled is True


def test_spell_set_hooks_partial_update_preserves_existing() -> None:
    """
    Verify _set_hooks updates only provided lists and keeps others intact.
    """
    spell = _make_spell()
    pre_hook = lambda: None
    activation_hook = lambda _: None

    spell._set_hooks(pre_hooks=[pre_hook])
    spell._set_hooks(activation_hooks=[activation_hook])

    assert spell._pre_hooks == [pre_hook]
    assert spell._activation_hooks == [activation_hook]
    assert spell._hooks_enabled is True


def test_spell_set_hooks_none_does_not_clear_existing() -> None:
    """
    Verify _set_hooks leaves existing hooks unchanged when all inputs are None.
    """
    spell = _make_spell()
    pre_hook = lambda: None
    spell._set_hooks(pre_hooks=[pre_hook])
    original_pre = spell._pre_hooks

    spell._set_hooks(pre_hooks=None, activation_hooks=None, post_hooks=None)

    assert spell._pre_hooks is original_pre
    assert spell._hooks_enabled is True


def test_spell_set_hooks_empty_lists_disable_hooks() -> None:
    """
    Verify _set_hooks disables hook gating when all lists are empty.
    """
    spell = _make_spell()
    spell._set_hooks(pre_hooks=[lambda: None])

    spell._set_hooks(pre_hooks=[], activation_hooks=[], post_hooks=[])

    assert spell._pre_hooks == []
    assert spell._activation_hooks == []
    assert spell._post_hooks == []
    assert spell._hooks_enabled is False


def test_spell_set_hooks_copies_input_sequences() -> None:
    """
    Verify _set_hooks copies input hook sequences to avoid external mutation.
    """
    spell = _make_spell()
    hooks = [lambda: None]

    spell._set_hooks(pre_hooks=hooks)
    hooks.append(lambda: None)

    assert len(hooks) == 2
    assert spell._pre_hooks == [hooks[0]]


def test_spell_set_hooks_keeps_enabled_when_other_hooks_remain() -> None:
    """
    Verify clearing one hook list does not disable gating when others remain.
    """
    spell = _make_spell()
    activation_hook = lambda _: None
    spell._set_hooks(pre_hooks=[lambda: None], activation_hooks=[activation_hook])

    spell._set_hooks(pre_hooks=[])

    assert spell._pre_hooks == []
    assert spell._activation_hooks == [activation_hook]
    assert spell._hooks_enabled is True

@pytest.mark.parametrize(
    "spellframe,binding,spell_name,expected",
    [
        (type("Frame", (), {}), "DB", "Frame", ("frame", "db")),
        ("Proto", None, "Frame", ("proto", "__default__")),
        (None, "", "MySpell", ("myspell", "__default__")),
        (None, "Name", "Other", ("other", "name")),
        ("AlreadyLower", "MiXeD", "Name", ("alreadylower", "mixed")),
        (type("Thing", (), {}), None, "Thing", ("thing", "__default__")),
        ("Fancy-Frame", "bind-1", "Fancy", ("fancy-frame", "bind-1")),
    ],
)
def test_spell_key_normalization_variants(spellframe, binding, spell_name, expected):
    spell = _make_spell(spellframe=spellframe, binding_name=binding, spell_name=spell_name)
    assert spell.key == expected


@pytest.mark.parametrize(
    "spell_type,expected_class,expected_method,expected_lambda,expected_existing",
    [
        (SpellType.SPELL, True, False, False, False),
        (SpellType.SPELL_WITH_BINDING_NAME_WITH_SPELLFRAME, True, False, False, False),
        (SpellType.METHOD, False, True, False, False),
        (SpellType.METHOD_WITH_BINDING_NAME_WITH_SPELLFRAME, False, True, False, False),
        (SpellType.LAMBDA_METHOD_WITH_BINDING_NAME, False, False, True, False),
        (SpellType.EXISTING_CREATION_WITH_BINDING_NAME_WITH_SPELLFRAME, False, False, False, True),
    ],
)
def test_spell_type_flag_detection(spell_type, expected_class, expected_method, expected_lambda, expected_existing):
    spell = _make_spell(spell_type=spell_type)
    assert spell.is_class_spell is expected_class
    assert spell.is_method_spell is expected_method
    assert spell.is_lambda_spell is expected_lambda
    assert spell.is_existing_creation is expected_existing


@pytest.mark.parametrize(
    "existing_obj,expected",
    [
        (object(), True),
        (None, False),
    ],
)
def test_existing_creation_object_presence(existing_obj, expected):
    spell = _make_spell(spell_type=SpellType.EXISTING_CREATION, existing_object=existing_obj)
    assert spell.has_existing_object is expected


def test_owner_conduit_info_before_and_after_assignment():
    spell = _make_spell()
    assert spell.owner_conduit_info == (None, None)
    spell._add_owned_conduit(
        "conduit-1",
        "c1",
        creations="creations",
        dynamic_environment=False,
        creation_gate_controller=CreationGateController(),
        caching_enabled=False,
    )
    assert spell.owner_conduit_info == ("conduit-1", "c1")
    assert spell._owner_creations == "creations"


def test_emit_cache_delegates_to_spellbook_when_enabled():
    class _CachingSpellbookStub(_SpellbookStub):
        def __init__(self, states):
            super().__init__(states)
            self.calls = []

        def _emit_spell_cache(self, spell):
            self.calls.append(spell)
            return True

    spellbook = _CachingSpellbookStub(_RecordingStates())
    spell = Spell(
        spell=lambda: None,
        spell_index=SpellIndex("cache-id"),
        spellframe=None,
        binding_name=None,
        spell_name="CacheSpell",
        existence=Existence.unique,
        spell_type=SpellType.SPELL,
        spell_id="cache-fingerprint",
        permissions=Permissions.create,
        aetheric_frame="default",
        spellbook=spellbook,
    )
    spell._caching_enabled = True
    spell._creation_context = object()

    assert spell.emit_cache() is True
    assert spellbook.calls == [spell]


def test_emit_cache_returns_false_when_disabled():
    spell = _make_spell()
    spell._caching_enabled = False

    assert spell.emit_cache() is False


def test_emit_cache_returns_false_without_creation_context():
    spell = _make_spell()
    spell._caching_enabled = True
    spell._creation_context = None

    assert spell.emit_cache() is False


def test_emit_cache_file_delegates_to_spellbook_when_enabled():
    class _CachingSpellbookStub(_SpellbookStub):
        def __init__(self, states):
            super().__init__(states)
            self.calls = []

        def _emit_cache_file(self, spell):
            self.calls.append(spell)
            return True

    spellbook = _CachingSpellbookStub(_RecordingStates())
    spell = Spell(
        spell=lambda: None,
        spell_index=SpellIndex("cache-file-id"),
        spellframe=None,
        binding_name=None,
        spell_name="CacheFileSpell",
        existence=Existence.unique,
        spell_type=SpellType.SPELL,
        spell_id="cache-file-fingerprint",
        permissions=Permissions.create,
        aetheric_frame="default",
        spellbook=spellbook,
    )
    spell._caching_enabled = True

    assert spell.emit_cache_file() is True
    assert spellbook.calls == [spell]


def test_emit_cache_file_returns_false_when_disabled():
    spell = _make_spell()
    spell._caching_enabled = False

    assert spell.emit_cache_file() is False


def test_add_build_details_sets_dependencies_and_graph():
    spell = _make_spell()
    deps = ["a", "b", "c"]
    dag = object()
    spell._add_build_details(dag, deps)
    assert spell.dependency_graph is dag
    assert spell.dependencies == deps


@pytest.mark.parametrize(
    "dag,deps,error_msg",
    [
        (None, [], "Dependency graph cannot be None."),
        ("graph", None, "Dependencies cannot be None."),
    ],
)
def test_add_build_details_rejects_none_inputs(dag, deps, error_msg):
    spell = _make_spell()
    with pytest.raises(ValueError, match=error_msg):
        spell._add_build_details(dag, deps)


@pytest.mark.parametrize(
    "payload,expected_payload",
    [
        ({"mode": "overlay"}, {"mode": "overlay"}),
        ({}, None),
        (None, None),
        ([1, 2], {"__args__": [1, 2]}),
        ((1, 2), {"__args__": [1, 2]}),
    ],
)
def test_apply_mutation_override_normalizes_payload_without_devops_signal(
        payload,
        expected_payload,
):
    states = _RecordingStates()
    spell = _make_spell(states=states, dynamic_environment=True)
    spell.apply_mutation_override(payload)
    assert spell.mutation_override == expected_payload
    assert states.calls == []


def test_clear_mutation_override_noop_when_empty():
    states = _RecordingStates()
    spell = _make_spell(states=states, dynamic_environment=True)
    spell.clear_mutation_override()
    assert states.calls == []
    assert spell.mutation_override is None


def test_clear_mutation_override_clears_payload_without_devops_signal():
    states = _RecordingStates()
    spell = _make_spell(states=states, dynamic_environment=True)
    spell.apply_mutation_override({"v": 1})
    spell.clear_mutation_override()
    assert states.calls == []
    assert spell.mutation_override is None


def test_invalidate_spell_clears_context_and_marks_revalidation_state() -> None:
    states = _RecordingStates()
    spell = _make_spell(states=states, dynamic_environment=True)
    spell._creation_context = _Disposable()
    spell._creation_context_switch.advance(2)
    spell.resolution_required = False
    spell.resolution_complete = True

    spell.invalidate_spell()

    assert spell._creation_context is None
    assert spell._creation_context_switch.state == 0
    assert spell.resolution_required is True
    assert spell.resolution_complete is False
    assert states.calls[-1][1] is SpellStateChangeReason.structure_changed


def test_invalidate_spell_uses_explicit_change_reason() -> None:
    states = _RecordingStates()
    spell = _make_spell(states=states, dynamic_environment=True)

    spell.invalidate_spell(
        change_reason=SpellStateChangeReason.mutation_contract_set,
    )

    assert states.calls[-1][1] is SpellStateChangeReason.mutation_contract_set


def test_invalidate_spell_without_states_registry_still_invalidates_locally() -> None:
    spell = _make_spell(states=None, dynamic_environment=True)
    spell._spell_system_states = None
    spell._creation_context = _Disposable()
    spell._creation_context_switch.advance(2)
    spell.resolution_required = False
    spell.resolution_complete = True

    spell.invalidate_spell()

    assert spell._creation_context is None
    assert spell._creation_context_switch.state == 0
    assert spell.resolution_required is True
    assert spell.resolution_complete is False


def test_invalidate_spell_raises_outside_dynamic_mode() -> None:
    spell = _make_spell(dynamic_environment=False)

    with pytest.raises(
            RuntimeError,
            match="Spell invalidation for revalidation requires dynamic mode",
    ):
        spell.invalidate_spell()


def test_cleanup_disposes_artifacts_and_nulls_references():
    cleanup_calls = []

    class _TrackingSpellIndex(SpellIndex):
        __slots__ = ()

        def cleanup(self):
            cleanup_calls.append("spell_index")
            super().cleanup()

    dependency_graph = _Disposable()
    resolution_profile = _CleanableProfile()
    binding_profile = _CleanableProfile()
    crafter = _Disposable()

    spell = Spell(
        spell=lambda: None,
        spell_index=_TrackingSpellIndex("cleanup-id"),
        spellframe=None,
        binding_name=None,
        spell_name="CleanupSpell",
        existence=Existence.unique,
        spell_type=SpellType.SPELL,
        spell_id="cleanup-fingerprint",
        permissions=Permissions.create,
        aetheric_frame="default",
        spellbook=_SpellbookStub(_RecordingStates()),
    )

    spell.dependency_graph = dependency_graph
    compiler_artifact = spell._compiler_artifact
    general_profile = SpellGeneralProfile(
        binding_profile=binding_profile,
        resolution_profile=resolution_profile,
    )
    spell.profile = general_profile

    spell.cleanup()

    assert dependency_graph.cleaned is True
    assert compiler_artifact.cleaned is True
    assert resolution_profile.cleaned is True
    assert binding_profile.cleaned is True
    assert not hasattr(spell, "profile")
    assert cleanup_calls == ["spell_index"]

    assert spell._cleaned is True
    assert spell._lock is not None
    assert not hasattr(spell, "spell")
    assert not hasattr(spell, "spell_index")
    assert hasattr(spell, "_key")
    assert not hasattr(spell, "_pre_hooks")
    assert not hasattr(spell, "metadata")
    assert not hasattr(spell, "_spell_system_states")


def test_cleanup_idempotent():
    spell = _make_spell()
    spell.cleanup()
    spell.cleanup()  # second call should no-op
    assert spell._cleaned is True
    assert spell._lock is not None


def test_context_manager_releases_lock():
    spell = _make_spell()
    with spell as context_spell:
        assert context_spell is spell
        assert spell._lock.acquire() is True  # reentrant acquire succeeds on RLock
        spell._lock.release()
    assert spell._lock.acquire() is True
    spell._lock.release()


@pytest.mark.parametrize(
    "spellframe,binding_name,spell_name,expected_fragment",
    [
        (type("Frame", (), {}), "bind", "Frame", "frame"),
        (None, "bind", "Name", "Name"),
        ("FrameStr", None, "Name", "FrameStr"),
    ],
)
def test_repr_includes_core_identity(spellframe, binding_name, spell_name, expected_fragment):
    spell = _make_spell(spellframe=spellframe, binding_name=binding_name, spell_name=spell_name)
    text = repr(spell)
    assert expected_fragment in text
    assert spell.spell_id in text


def test_resolution_properties_return_none_without_crafter():
    spell = _make_spell()
    assert spell.requirements is None
    assert spell.symbolic_graph is None
    assert spell.resolution_frame is None
    assert spell.validation_result_phase4 is None
    assert spell.validation_result_phase6 is None
    assert spell.validated is False
    assert spell.is_broken is False


@pytest.mark.parametrize(
    "prop_name,expected",
    [
        ("requirements", "req"),
        ("symbolic_graph", "sym"),
        ("resolution_frame", "frame"),
        ("validation_result_phase4", "p4"),
        ("validation_result_phase6", "p6"),
        ("validated", True),
        ("is_broken", False),
    ],
)
def test_resolution_properties_delegate_to_crafter(prop_name, expected):
    spell = _make_spell()
    spell._compiler_artifact._requirements = "req"
    spell._compiler_artifact._symbolic_graph = "sym"
    spell._compiler_artifact._resolution_frame = "frame"
    spell._compiler_artifact._validation_result_phase4 = "p4"
    spell._compiler_artifact._validation_result_phase6 = "p6"
    spell._compiler_artifact._validated_phase4 = True
    spell._compiler_artifact._validated_phase6 = True
    spell._compiler_artifact._validated = True
    spell._compiler_artifact._is_broken = False
    assert getattr(spell, prop_name) == expected


def test_validated_property_reads_phase4_flag_only() -> None:
    """validated should reflect the phase-4 flag, not phase-6 or broken state."""
    spell = _make_spell()
    spell._compiler_artifact._validated_phase4 = False
    spell._compiler_artifact._validated_phase6 = True
    spell._compiler_artifact._is_broken = True

    assert spell.validated is False

    spell._compiler_artifact._validated_phase4 = True
    spell._compiler_artifact._validated_phase6 = False
    spell._compiler_artifact._is_broken = True

    assert spell.validated is True


@pytest.mark.parametrize(
    "prop_name",
    [
        "requirements",
        "symbolic_graph",
        "resolution_frame",
        "validation_result_phase4",
        "validation_result_phase6",
        "validated",
        "is_broken",
    ],
)
def test_resolution_properties_fail_after_cleanup(prop_name) -> None:
    """Resolution/introspection properties should stop working after cleanup."""
    spell = _make_spell()
    spell.cleanup()

    with pytest.raises(AttributeError):
        getattr(spell, prop_name)


def test_spell_does_not_expose_run_all_phases_facade():
    spell = _make_spell()
    assert not hasattr(spell, "run_all_phases")


def test_spell_does_not_expose_run_structural_phases_facade():
    spell = _make_spell()
    assert not hasattr(spell, "run_structural_phases")


@pytest.mark.parametrize(
    "payload,expected_flag",
    [
        ({}, False),
        ({"k": "v"}, True),
        (None, False),
    ],
)
def test_has_mutation_override_reflects_payload(payload, expected_flag):
    spell = _make_spell(dynamic_environment=True)
    spell.apply_mutation_override(payload)
    assert spell.has_mutation_override is expected_flag


def test_has_existing_object_after_cleanup_resets():
    existing = object()
    spell = _make_spell(spell_type=SpellType.EXISTING_CREATION, existing_object=existing)
    spell.cleanup()
    with pytest.raises(AttributeError):
        _ = spell.has_existing_object


def test_system_state_delegation_returns_state_from_spell_system_states():
    states = _RecordingStates()
    spell = _make_spell(states=states)
    state = spell.system_state
    assert state == f"state:{spell.spell_index.id}"


@pytest.mark.parametrize(
    "binding_name,expected",
    [
        ("MiXeD-Case", "mixed-case"),
        ("under_score", "under_score"),
        ("", "__default__"),
    ],
)
def test_binding_name_normalization_special_cases(binding_name, expected):
    spell = _make_spell(binding_name=binding_name or None)
    assert spell.key[1] == expected


def test_mutation_override_replaces_previous_payload():
    spell = _make_spell(dynamic_environment=True)
    spell.apply_mutation_override({"first": 1})
    spell.apply_mutation_override({"second": 2})
    assert spell.mutation_override == {"second": 2}


def test_add_build_details_overwrites_previous_values():
    spell = _make_spell()
    first = object()
    second = object()
    spell._add_build_details(first, ["a"])
    spell._add_build_details(second, ["b"])
    assert spell.dependency_graph is second
    assert spell.dependencies == ["b"]


def test_apply_mutation_override_no_states_does_not_raise():
    spell = _make_spell(states=None, dynamic_environment=True)
    spell._spell_system_states = None
    spell.apply_mutation_override({"k": "v"})
    assert spell.mutation_override == {"k": "v"}


def test_clear_mutation_override_no_states_safely_clears():
    spell = _make_spell(states=None, dynamic_environment=True)
    spell._spell_system_states = None
    spell.apply_mutation_override({"k": "v"})
    spell.clear_mutation_override()
    assert spell.mutation_override is None


def test_apply_mutation_override_raises_outside_dynamic_mode():
    spell = _make_spell(dynamic_environment=False)

    with pytest.raises(RuntimeError, match="Mutation overrides require dynamic mode"):
        spell.apply_mutation_override({"mode": "overlay"})


def test_clear_mutation_override_raises_outside_dynamic_mode():
    spell = _make_spell(dynamic_environment=False)

    with pytest.raises(RuntimeError, match="Mutation overrides require dynamic mode"):
        spell.clear_mutation_override()


def test_cleanup_swallows_child_cleanup_errors():
    spell = _make_spell()
    spell.dependency_graph = _Disposable(fail_on_cleanup=True)
    spell.profile = _CleanableProfile()
    spell.cleanup()
    assert spell._cleaned is True
    assert not hasattr(spell, "profile")


def test_cleanup_rechecks_cleaned_state_under_lock() -> None:
    class _FlipCleanedOnEnter:
        def __init__(self, owner):
            self._owner = owner

        def __enter__(self):
            self._owner._cleaned = True
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

    spell = _make_spell()
    original_lock = spell._lock
    spell._lock = _FlipCleanedOnEnter(spell)
    try:
        spell.cleanup()
    finally:
        spell._lock = original_lock

    assert spell._cleaned is True


def test_cleanup_swallows_profile_spellindex_switch_and_tags_clear_failures() -> None:
    cleanup_calls = []

    class _FailingSpellIndex(SpellIndex):
        __slots__ = ()

        def cleanup(self):
            cleanup_calls.append("spell_index")
            raise RuntimeError("spell_index cleanup boom")

    class _FailingSwitch:
        def __init__(self):
            self.state = 0

        def cleanup(self):
            raise RuntimeError("switch cleanup boom")

    spell = Spell(
        spell=lambda: None,
        spell_index=_FailingSpellIndex("cleanup-id"),
        spellframe=None,
        binding_name=None,
        spell_name="CleanupSpell",
        existence=Existence.unique,
        spell_type=SpellType.SPELL,
        spell_id="cleanup-fingerprint",
        permissions=Permissions.create,
        aetheric_frame="default",
        spellbook=_SpellbookStub(_RecordingStates()),
    )
    spell.profile = _FailingCleanableProfile()
    spell._creation_context_switch = _FailingSwitch()

    spell.cleanup()

    assert cleanup_calls == ["spell_index"]
    assert spell._cleaned is True
    assert not hasattr(spell, "profile")
    assert not hasattr(spell, "_creation_context_switch")


def test_owned_conduit_stamps_runtime_ownership_state():
    spell = _make_spell()
    spell._add_owned_conduit(
        "cid",
        "cname",
        creations="creations",
        dynamic_environment=False,
        creation_gate_controller=CreationGateController(),
        caching_enabled=False,
    )
    assert spell.owner_conduit_info == ("cid", "cname")
    assert spell._owner_creations == "creations"


def test_cleanup_clears_hooks_and_metadata_collections():
    spell = _make_spell()
    spell._pre_hooks = [lambda: None]
    spell._activation_hooks = [lambda: None]
    spell._post_hooks = [lambda: None]
    spell.tags = ["tag"]
    spell.metadata = {"k": "v"}
    spell.dependencies = ["dep"]
    spell.cleanup()
    assert not hasattr(spell, "_pre_hooks")
    assert not hasattr(spell, "_activation_hooks")
    assert not hasattr(spell, "_post_hooks")
    assert not hasattr(spell, "tags")
    assert not hasattr(spell, "metadata")
    assert not hasattr(spell, "dependencies")


def test_system_state_after_cleanup_raises():
    spell = _make_spell()
    spell.cleanup()
    with pytest.raises(RuntimeError):
        _ = spell.system_state


def test_removed_spell_phase_facades_stay_absent_after_cleanup():
    spell = _make_spell()
    spell.cleanup()
    assert not hasattr(spell, "run_all_phases")


def test_spell_does_not_expose_ensure_crafter() -> None:
    spell = _make_spell()
    assert not hasattr(spell, "_ensure_crafter")


def test_cleanup_creation_context_and_factory_swallow_child_cleanup_errors() -> None:
    spell = _make_spell()
    spell._creation_context = _Disposable(fail_on_cleanup=True)
    spell._creation_context_factory = _Disposable(fail_on_cleanup=True)
    spell._creation_context_switch.advance(2)

    spell._cleanup_creation_context()
    spell._cleanup_creation_context_factory()

    assert spell._creation_context is None
    assert spell._creation_context_factory is None
    assert spell._creation_context_switch.state == 0


def test_configure_creation_context_factory_requires_gate_and_builds_factory() -> None:
    spell = _make_spell()

    with pytest.raises(ValueError, match="creation_gate_controller cannot be None."):
        spell._configure_creation_context_factory(
            dynamic_environment=True,
            creation_gate_controller=None,
        )

    gate = CreationGateController()
    spell._configure_creation_context_factory(
        dynamic_environment=True,
        creation_gate_controller=gate,
    )

    assert spell._dynamic_environment is True
    assert spell._creation_context_factory is not None


def test_get_or_build_creation_context_uses_switch_fast_path_and_factory() -> None:
    spell = _make_spell()
    cached_context = object()
    spell._creation_context = cached_context
    spell._creation_context_switch.advance(2)

    assert spell._get_or_build_creation_context() is cached_context

    spell._creation_context_switch.advance(-2)

    class _Factory:
        def __init__(self):
            self.calls = []

        def get_or_build_for_spell(self, owner):
            self.calls.append(owner)
            return "built-context"

    factory = _Factory()
    spell._creation_context_factory = factory

    assert spell._get_or_build_creation_context() == "built-context"
    assert factory.calls == [spell]


def test_spell_does_not_expose_local_phase_facades() -> None:
    spell = _make_spell()
    assert not hasattr(spell, "run_phase_root_blueprints_local")
    assert not hasattr(spell, "run_phase_system_validation_local")
    assert not hasattr(spell, "run_phase_change_control_local")


def test_system_state_returns_none_when_states_registry_missing() -> None:
    spell = _make_spell(states=None)
    spell._spell_system_states = None

    assert spell.system_state is None
