
from melder.aether.conduit.conduit_ward.permissions.permissions import Permissions
from melder.aether.dev_ops.spell_system_states.spell_state_change_reason import (
    SpellStateChangeReason,
)
from melder.spellbook.bind.spell_index import SpellIndex
from melder.spellbook.existence.existence import Existence
from melder.spellbook.spell_crafter.spell_examiner.profiles.general_profile import (
    SpellGeneralProfile,
)
from melder.spellbook.spell import Spell
from melder.spellbook.spell_types.spell_types import SpellType
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


def test_mutation_override_signals_structural_change():
    """
    Applying and clearing mutation overlays should update payloads and signal structural changes to DevOps state.
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

    spell.apply_mutation_override({"mode": "overlay"})
    assert spell.mutation_override == {"mode": "overlay"}
    assert states.calls[-1][1] is SpellStateChangeReason.mutation_contract_set

    spell.apply_mutation_override(None)
    assert spell.mutation_override == {}
    assert states.calls[-1][1] is SpellStateChangeReason.mutation_contract_cleared
    assert len(states.calls) == 2


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

    spell.clear_mutation_override()
    assert spell.mutation_override == {}
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
    assert spell.profile is None
    assert cleanup_calls == ["spell_index"]

    assert spell._cleaned is True
    assert spell._lock is None
    assert spell.spell is None
    assert spell.spell_index is None
    assert spell._key is None
    assert spell._pre_hooks is None
    assert spell.metadata is None
    assert spell._spell_system_states is None
import sys
import types

import pytest

from melder.aether.conduit.conduit_ward.permissions.permissions import Permissions
from melder.aether.dev_ops.spell_system_states.spell_state_change_reason import (
    SpellStateChangeReason,
)
from melder.spellbook.bind.spell_index import SpellIndex
from melder.spellbook.existence.existence import Existence
from melder.spellbook.spell import Spell
from melder.spellbook.spell_types.spell_types import SpellType
from melder.utilities.general_base.cleanable import Cleanable


class _SpellbookStub:
    def __init__(self, states):
        self._spell_system_states = states


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
):
    states = states or _RecordingStates()
    return Spell(
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


def test_spell_set_hooks_raises_when_cleaned() -> None:
    """
    Verify _set_hooks rejects calls after cleanup.
    """
    spell = _make_spell()
    spell.cleanup()

    with pytest.raises(RuntimeError, match="already been cleaned"):
        spell._set_hooks(pre_hooks=[])


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
    )
    assert spell.owner_conduit_info == ("conduit-1", "c1")
    assert spell.owned_spell is True


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
    "payload,expected_reason,expected_payload",
    [
        ({"mode": "overlay"}, SpellStateChangeReason.mutation_contract_set, {"mode": "overlay"}),
        ({}, SpellStateChangeReason.mutation_contract_cleared, {}),
    ],
)
def test_apply_mutation_override_signals_devops(payload, expected_reason, expected_payload):
    states = _RecordingStates()
    spell = _make_spell(states=states)
    spell.apply_mutation_override(payload)
    assert spell.mutation_override == expected_payload
    assert states.calls[-1][1] is expected_reason


def test_clear_mutation_override_noop_when_empty():
    states = _RecordingStates()
    spell = _make_spell(states=states)
    spell.clear_mutation_override()
    assert states.calls == []
    assert spell.mutation_override == {}


def test_clear_mutation_override_signals_when_overlay_present():
    states = _RecordingStates()
    spell = _make_spell(states=states)
    spell.apply_mutation_override({"v": 1})
    spell.clear_mutation_override()
    assert states.calls[-1][1] is SpellStateChangeReason.mutation_contract_cleared
    assert spell.mutation_override == {}


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
    general_profile = SpellGeneralProfile(
        binding_profile=binding_profile,
        resolution_profile=resolution_profile,
    )
    spell.profile = general_profile
    spell._crafter = crafter

    spell.cleanup()

    assert dependency_graph.cleaned is True
    assert resolution_profile.cleaned is True
    assert binding_profile.cleaned is True
    assert spell.profile is None
    assert cleanup_calls == ["spell_index"]

    assert spell._cleaned is True
    assert spell._lock is None
    assert spell.spell is None
    assert spell.spell_index is None
    assert spell._key is None
    assert spell._pre_hooks is None
    assert spell.metadata is None
    assert spell._spell_system_states is None


def test_cleanup_idempotent():
    spell = _make_spell()
    spell.cleanup()
    spell.cleanup()  # second call should no-op
    assert spell._cleaned is True
    assert spell._lock is None


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
    crafter = _DummyCrafter()
    spell._crafter = crafter
    assert getattr(spell, prop_name) == expected


def test_run_all_phases_invokes_crafter_in_order():
    spell = _make_spell()
    crafter = _DummyCrafter()
    spell._ensure_crafter = types.MethodType(lambda self: crafter, spell)
    cancel_event = object()

    spell.run_all_phases("cid", cancel_event=cancel_event)

    assert crafter.calls == [
        "requirements",
        "symbolic_graph",
        "local_frame",
        "validation",
        "root_blueprints",
        "system_validation",
        "change_control",
        "occurrence_plan",
        "injection_plan",
        "patch_maps",
        "execution_plan",
        "cleanup_phase_artifacts",
    ]
    observed = [
        ev[1] if isinstance(ev, tuple) else ev for ev in crafter.seen_cancel_events
    ]
    assert all(ev is cancel_event for ev in observed)


def test_run_structural_phases_invokes_crafter_in_order():
    spell = _make_spell()
    crafter = _DummyCrafter()
    spell._ensure_crafter = types.MethodType(lambda self: crafter, spell)
    cancel_event = object()

    spell.run_structural_phases(cancel_event=cancel_event)

    assert crafter.calls == [
        "requirements",
        "symbolic_graph",
        "local_frame",
        "validation",
    ]
    assert all(ev is cancel_event for ev in crafter.seen_cancel_events)


@pytest.mark.parametrize(
    "payload,expected_flag",
    [
        ({}, False),
        ({"k": "v"}, True),
        (None, False),
    ],
)
def test_has_mutation_override_reflects_payload(payload, expected_flag):
    spell = _make_spell()
    spell.apply_mutation_override(payload)
    assert spell.has_mutation_override is expected_flag


def test_has_existing_object_after_cleanup_resets():
    existing = object()
    spell = _make_spell(spell_type=SpellType.EXISTING_CREATION, existing_object=existing)
    spell.cleanup()
    assert spell.has_existing_object is False


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
    spell = _make_spell()
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
    spell = _make_spell(states=None)
    spell._spell_system_states = None
    spell.apply_mutation_override({"k": "v"})
    assert spell.mutation_override == {"k": "v"}


def test_clear_mutation_override_no_states_safely_clears():
    spell = _make_spell(states=None)
    spell._spell_system_states = None
    spell.apply_mutation_override({"k": "v"})
    spell.clear_mutation_override()
    assert spell.mutation_override == {}


def test_cleanup_swallows_child_cleanup_errors():
    spell = _make_spell()
    spell.dependency_graph = _Disposable(fail_on_cleanup=True)
    spell.profile = _CleanableProfile()
    spell.cleanup()
    assert spell._cleaned is True
    assert spell.profile is None


def test_owned_conduit_marks_owned_spell_true():
    spell = _make_spell()
    spell._add_owned_conduit(
        "cid",
        "cname",
        creations="creations",
        dynamic_environment=False,
        creation_gate_controller=CreationGateController(),
    )
    assert spell.owned_spell is True
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
    assert spell._pre_hooks is None
    assert spell._activation_hooks is None
    assert spell._post_hooks is None
    assert spell.tags is None
    assert spell.metadata is None
    assert spell.dependencies is None


def test_system_state_after_cleanup_raises():
    spell = _make_spell()
    spell.cleanup()
    with pytest.raises(RuntimeError):
        _ = spell.system_state


def test_run_all_phases_rejects_after_cleanup():
    spell = _make_spell()
    spell.cleanup()
    with pytest.raises(RuntimeError):
        spell.run_all_phases("cid")


def test_ensure_crafter_lazy_creation_uses_imported_class(monkeypatch):
    created = {}

    class DummySpellCrafter:
        def __init__(self, owner, *, resolution_profile=None):
            created["owner"] = owner
            created["resolution_profile"] = resolution_profile

    dummy_module = types.SimpleNamespace(SpellCrafter=DummySpellCrafter)
    module_name = "melder.spellbook.spell_crafter.spell_crafter"
    original = sys.modules.get(module_name)
    sys.modules[module_name] = dummy_module
    try:
        spell = _make_spell()
        crafter = spell._ensure_crafter()
        assert created["owner"] is spell
        assert isinstance(crafter, DummySpellCrafter)
        # second call returns cached instance
        assert spell._ensure_crafter() is crafter
    finally:
        if original is not None:
            sys.modules[module_name] = original
        else:
            sys.modules.pop(module_name, None)
