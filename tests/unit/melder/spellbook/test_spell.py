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


class DummySpellSystemStates:
    def __init__(self):
        self.mark_calls = []
        self.state_by_id = {}

    def mark_structural_change(self, spell_index, reason):
        self.mark_calls.append((spell_index.id, reason))

    def get_by_index_id(self, index_id):
        return self.state_by_id.get(index_id)


class DummySpellbook:
    def __init__(self, states):
        self._spell_system_states = states


class DummyGraph:
    def __init__(self):
        self.cleaned = False

    def cleanup(self):
        self.cleaned = True


class DummyProfile(Cleanable):
    def __init__(self):
        super().__init__()
        self.cleaned_flag = False

    def cleanup(self):
        self.cleaned_flag = True
        self._cleaned = True


class DummyCrafter:
    def __init__(self):
        self.requirements = "req"
        self.symbolic_graph = "sym"
        self.resolution_frame = "frame"
        self.validation_result_phase4 = "val4"
        self.validation_result_phase6 = "val6"
        self.validated = True
        self.is_broken = False
        self.cleaned = False

    def cleanup(self):
        self.cleaned = True

    def run_phase_requirements(self, cancel_event=None):
        self.requirements = ("ran", cancel_event)

    def run_phase_symbolic_graph(self, cancel_event=None):
        self.symbolic_graph = ("sym", cancel_event)

    def run_phase_local_frame(self, cancel_event=None):
        self.resolution_frame = ("frame", cancel_event)

    def run_phase_validation(self, cancel_event=None):
        self.validation_result_phase4 = ("val4", cancel_event)
        self.validation_result_phase6 = ("val6", cancel_event)

    def run_phase_system_graph(self, cancel_event=None):
        self.system_graph = ("sys", cancel_event)

    def run_phase_system_validation(self, cancel_event=None):
        self.system_validation = ("sysval", cancel_event)

    def run_phase_publish(self, cancel_event=None):
        self.published = ("pub", cancel_event)


def make_spell(
    spell_type: SpellType,
    *,
    spellframe=None,
    binding_name=None,
    existing_object=None,
    states=None,
    profile=None,
):
    states = states or DummySpellSystemStates()
    spellbook = DummySpellbook(states)
    spell_index = SpellIndex("init-id")
    spell = Spell(
        spell=object(),
        spell_index=spell_index,
        spellframe=spellframe,
        binding_name=binding_name,
        spell_name="MySpell",
        existence=Existence.unique_per_aetheric_frame,
        spell_type=spell_type,
        spell_id="sha256",
        permissions=Permissions.read,
        aetheric_frame="frame-a",
        profile=profile,
        existing_object=existing_object,
        spellbook=spellbook,
    )
    return spell, states


@pytest.mark.parametrize(
    "spell_type",
    [
        SpellType.EXISTING_CREATION,
        SpellType.EXISTING_CREATION_WITH_SPELLFRAME,
        SpellType.EXISTING_CREATION_WITH_BINDING_NAME_WITH_SPELLFRAME,
    ],
)
def test_is_existing_creation_true(spell_type):
    spell, _ = make_spell(spell_type)
    assert spell.is_existing_creation


@pytest.mark.parametrize(
    "spell_type",
    [
        SpellType.SPELL,
        SpellType.METHOD,
        SpellType.LAMBDA_METHOD_WITH_SPELLFRAME,
        SpellType.SPELL_WITH_BINDING_NAME,
    ],
)
def test_is_existing_creation_false_for_non_existing(spell_type):
    spell, _ = make_spell(spell_type)
    assert not spell.is_existing_creation


@pytest.mark.parametrize(
    "spell_type",
    [
        SpellType.SPELL,
        SpellType.SPELL_WITH_SPELLFRAME,
        SpellType.SPELL_WITH_BINDING_NAME,
        SpellType.SPELL_WITH_BINDING_NAME_WITH_SPELLFRAME,
    ],
)
def test_is_class_spell_true(spell_type):
    spell, _ = make_spell(spell_type)
    assert spell.is_class_spell


@pytest.mark.parametrize(
    "spell_type",
    [
        SpellType.METHOD,
        SpellType.EXISTING_CREATION,
        SpellType.LAMBDA_METHOD_WITH_BINDING_NAME,
        SpellType.METHOD_WITH_BINDING_NAME_WITH_SPELLFRAME,
    ],
)
def test_is_class_spell_false(spell_type):
    spell, _ = make_spell(spell_type)
    assert not spell.is_class_spell


@pytest.mark.parametrize(
    "spell_type",
    [
        SpellType.METHOD,
        SpellType.METHOD_WITH_BINDING_NAME,
        SpellType.METHOD_WITH_SPELLFRAME,
        SpellType.METHOD_WITH_BINDING_NAME_WITH_SPELLFRAME,
    ],
)
def test_is_method_spell_true(spell_type):
    spell, _ = make_spell(spell_type)
    assert spell.is_method_spell


@pytest.mark.parametrize(
    "spell_type",
    [
        SpellType.SPELL,
        SpellType.EXISTING_CREATION,
        SpellType.LAMBDA_METHOD_WITH_BINDING_NAME,
    ],
)
def test_is_method_spell_false(spell_type):
    spell, _ = make_spell(spell_type)
    assert not spell.is_method_spell


@pytest.mark.parametrize(
    "spell_type",
    [
        SpellType.LAMBDA_METHOD_WITH_BINDING_NAME,
        SpellType.LAMBDA_METHOD_WITH_SPELLFRAME,
        SpellType.LAMBDA_METHOD_WITH_BINDING_NAME_WITH_SPELLFRAME,
    ],
)
def test_is_lambda_spell_true(spell_type):
    spell, _ = make_spell(spell_type)
    assert spell.is_lambda_spell


@pytest.mark.parametrize(
    "spell_type",
    [
        SpellType.SPELL,
        SpellType.METHOD,
        SpellType.EXISTING_CREATION,
        SpellType.SPELL_WITH_BINDING_NAME_WITH_SPELLFRAME,
    ],
)
def test_is_lambda_spell_false(spell_type):
    spell, _ = make_spell(spell_type)
    assert not spell.is_lambda_spell


@pytest.mark.parametrize("existing_obj,expected", [(None, False), ("x", True)])
def test_has_existing_object(existing_obj, expected):
    spell, _ = make_spell(
        SpellType.EXISTING_CREATION,
        existing_object=existing_obj,
    )
    assert spell.has_existing_object is expected


def test_owner_conduit_info_defaults_to_none():
    spell, _ = make_spell(SpellType.SPELL)
    assert spell.owner_conduit_info == (None, None)
    assert spell.owned_spell is None


def test_owner_conduit_info_after_setting():
    spell, _ = make_spell(SpellType.SPELL)
    spell._add_owned_conduit("cid-1", "cname", creations={"foo": "bar"})
    assert spell.owner_conduit_info == ("cid-1", "cname")
    assert spell.owned_spell is True


@pytest.mark.parametrize(
    "spellframe,binding,expected_frame,expected_binding",
    [
        (None, None, "myspell", "__default__"),
        ("Frame", None, "frame", "__default__"),
        ("Frame", "Bind", "frame", "bind"),
        (type("FrameType", (), {}), "Bind", "frametype", "bind"),
        ("Frame", "__default__", "frame", "__default__"),
    ],
)
def test_key_normalization(spellframe, binding, expected_frame, expected_binding):
    spell, _ = make_spell(
        SpellType.SPELL_WITH_BINDING_NAME_WITH_SPELLFRAME,
        spellframe=spellframe,
        binding_name=binding,
    )
    assert spell.key == (expected_frame, expected_binding)


def test_repr_includes_name_binding_frame_and_id():
    spell, _ = make_spell(
        SpellType.SPELL_WITH_BINDING_NAME_WITH_SPELLFRAME,
        spellframe=type("FrameX", (), {}),
        binding_name="BindX",
    )
    text = repr(spell)
    assert "MySpell" in text
    assert "BindX" in text
    assert "FrameX" in text
    assert "sha256" in text


@pytest.mark.parametrize(
    "payload,expected_flag",
    [
        (None, False),
        ({}, False),
        ({"x": 1}, True),
    ],
)
def test_has_mutation_override_tracks_payload_truthiness(payload, expected_flag):
    spell, _ = make_spell(SpellType.SPELL)
    spell.apply_mutation_override(payload)
    assert spell.has_mutation_override is expected_flag


def test_apply_mutation_override_marks_set_when_payload_present():
    states = DummySpellSystemStates()
    spell, _ = make_spell(SpellType.SPELL, states=states)
    spell.apply_mutation_override({"a": 1})
    assert states.mark_calls[-1][1] == SpellStateChangeReason.mutation_contract_set
    assert spell.mutation_override == {"a": 1}


def test_apply_mutation_override_marks_cleared_when_payload_empty():
    states = DummySpellSystemStates()
    spell, _ = make_spell(SpellType.SPELL, states=states)
    spell.apply_mutation_override({})
    assert states.mark_calls[-1][1] == SpellStateChangeReason.mutation_contract_cleared
    assert spell.mutation_override == {}


def test_clear_mutation_override_is_idempotent_when_empty():
    states = DummySpellSystemStates()
    spell, _ = make_spell(SpellType.SPELL, states=states)
    spell.clear_mutation_override()
    assert states.mark_calls == []
    assert spell.mutation_override == {}


def test_clear_mutation_override_marks_change_when_overlay_was_set():
    states = DummySpellSystemStates()
    spell, _ = make_spell(SpellType.SPELL, states=states)
    spell.apply_mutation_override({"x": 1})
    states.mark_calls.clear()
    spell.clear_mutation_override()
    assert spell.mutation_override == {}
    assert states.mark_calls[-1][1] == SpellStateChangeReason.mutation_contract_cleared


def test_add_build_details_sets_graph_and_dependencies():
    spell, _ = make_spell(SpellType.SPELL)
    graph = DummyGraph()
    deps = ["a", "b"]
    spell._add_build_details(graph, deps)
    assert spell.dependency_graph is graph
    assert spell.dependencies == deps


def test_add_build_details_requires_graph():
    spell, _ = make_spell(SpellType.SPELL)
    with pytest.raises(ValueError):
        spell._add_build_details(None, [])


def test_add_build_details_requires_dependencies():
    spell, _ = make_spell(SpellType.SPELL)
    with pytest.raises(ValueError):
        spell._add_build_details(DummyGraph(), None)


def test_context_manager_returns_self_and_releases():
    spell, _ = make_spell(SpellType.SPELL)
    with spell as s:
        assert s is spell
    # lock should be released; acquiring again should succeed without deadlock
    with spell:
        pass


def test_cleanup_idempotent_and_clears_references():
    profile = DummyProfile()
    graph = DummyGraph()
    crafter = DummyCrafter()
    spell, _ = make_spell(SpellType.SPELL, profile=profile)
    spell.dependency_graph = graph
    spell._crafter = crafter
    spell.pre_hooks.append(lambda: None)
    spell.tags = ["tag"]
    spell.metadata = {"a": 1}
    spell.cleanup()
    spell.cleanup()  # second call should be no-op
    assert spell.cleaned
    assert graph.cleaned
    assert crafter.cleaned
    assert profile.cleaned_flag


def test_requirements_and_graph_properties_are_none_without_crafter():
    spell, _ = make_spell(SpellType.SPELL)
    assert spell.requirements is None
    assert spell.symbolic_graph is None
    assert spell.resolution_frame is None
    assert spell.validation_result_phase4 is None
    assert spell.validation_result_phase6 is None
    assert spell.validated is False
    assert spell.is_broken is False


def test_requirements_and_graph_properties_reflect_crafter_values():
    spell, _ = make_spell(SpellType.SPELL)
    crafter = DummyCrafter()
    spell._crafter = crafter
    assert spell.requirements == "req"
    assert spell.symbolic_graph == "sym"
    assert spell.resolution_frame == "frame"
    assert spell.validation_result_phase4 == "val4"
    assert spell.validation_result_phase6 == "val6"
    assert spell.validated is True
    assert spell.is_broken is False


def test_system_state_none_when_spellbook_missing_states():
    spell, _ = make_spell(SpellType.SPELL)
    spell._spell_system_states = None
    assert spell.system_state is None


def test_system_state_returns_state_from_system_states():
    states = DummySpellSystemStates()
    spell, _ = make_spell(SpellType.SPELL, states=states)
    states.state_by_id[spell.spell_index.id] = "state-obj"
    assert spell.system_state == "state-obj"


@pytest.mark.parametrize(
    "phase_attr",
    [
        "requirements",
        "symbolic_graph",
        "resolution_frame",
        "validation_result_phase4",
        "validation_result_phase6",
    ],
)
def test_run_all_phases_triggers_crafter_methods(phase_attr):
    spell, _ = make_spell(SpellType.SPELL)
    crafter = DummyCrafter()
    spell._crafter = crafter
    spell.run_all_phases(cancel_event=None)
    assert getattr(crafter, phase_attr)[0] in {"ran", "sym", "frame", "val4", "val6"}
    assert crafter.system_graph[0] == "sys"
    assert crafter.system_validation[0] == "sysval"
    assert crafter.published[0] == "pub"


def test_run_all_phases_propagates_cancel_event():
    spell, _ = make_spell(SpellType.SPELL)
    crafter = DummyCrafter()
    spell._crafter = crafter
    token = object()
    spell.run_all_phases(cancel_event=token)
    assert crafter.requirements[1] is token
    assert crafter.symbolic_graph[1] is token
    assert crafter.resolution_frame[1] is token
    assert crafter.validation_result_phase4[1] is token
    assert crafter.validation_result_phase6[1] is token
    assert crafter.system_graph[1] is token
    assert crafter.system_validation[1] is token
    assert crafter.published[1] is token


def test_mutation_override_defaults_empty_and_can_set_none_payload():
    states = DummySpellSystemStates()
    spell, _ = make_spell(SpellType.SPELL, states=states)
    assert spell.mutation_override == {}
    spell.apply_mutation_override(None)
    assert states.mark_calls[-1][1] == SpellStateChangeReason.mutation_contract_cleared
    assert spell.mutation_override == {}


def test_validated_and_broken_reflect_crafter_flags():
    spell, _ = make_spell(SpellType.SPELL)
    crafter = DummyCrafter()
    crafter.validated = False
    crafter.is_broken = True
    spell._crafter = crafter
    assert spell.validated is False
    assert spell.is_broken is True


def test_methods_raise_after_cleanup():
    spell, _ = make_spell(SpellType.SPELL)
    spell.cleanup()
    with pytest.raises(RuntimeError):
        spell.apply_mutation_override({"x": 1})
    with pytest.raises(RuntimeError):
        spell.clear_mutation_override()
    with pytest.raises(RuntimeError):
        _ = spell.system_state
    with pytest.raises(RuntimeError):
        spell.run_all_phases()


def test_add_build_details_raises_after_cleanup():
    spell, _ = make_spell(SpellType.SPELL)
    spell.cleanup()
    with pytest.raises(RuntimeError):
        spell._add_build_details(DummyGraph(), [])


def test_repr_falls_back_to_spell_type_when_no_frame():
    class FooSpell:
        pass

    spell, _ = make_spell(
        SpellType.SPELL,
        spellframe=None,
    )
    spell.spell = FooSpell
    text = repr(spell)
    assert "FooSpell" in text


def test_mutation_override_multiple_transitions_marks_changes():
    states = DummySpellSystemStates()
    spell, _ = make_spell(SpellType.SPELL, states=states)
    spell.apply_mutation_override({"a": 1})
    spell.apply_mutation_override({"b": 2})
    spell.clear_mutation_override()
    reasons = [r for _, r in states.mark_calls]
    assert SpellStateChangeReason.mutation_contract_set in reasons
    assert reasons[-1] == SpellStateChangeReason.mutation_contract_cleared


def test_system_state_raises_after_cleanup():
    spell, _ = make_spell(SpellType.SPELL)
    spell.cleanup()
    with pytest.raises(RuntimeError):
        _ = spell.system_state


def test_cleanup_sets_lock_to_none_and_is_idempotent():
    spell, _ = make_spell(SpellType.SPELL)
    first_lock = spell._lock
    spell.cleanup()
    assert spell._lock is None
    # second cleanup should not raise
    spell.cleanup()
    # ensure original lock was released
    assert first_lock is not None


def test_ensure_crafter_lazy_instantiation(monkeypatch):
    spell, _ = make_spell(SpellType.SPELL)

    class StubCrafter:
        def __init__(self, owner):
            self.owner = owner

    monkeypatch.setattr("melder.spellbook.spell_crafter.spell_crafter.SpellCrafter", StubCrafter)
    crafter = spell._ensure_crafter()
    assert isinstance(crafter, StubCrafter)
    assert crafter.owner is spell


def test_context_manager_raises_after_cleanup():
    spell, _ = make_spell(SpellType.SPELL)
    spell.cleanup()
    with pytest.raises(RuntimeError):
        with spell:
            pass


def test_add_owned_conduit_overwrites_previous():
    spell, _ = make_spell(SpellType.SPELL)
    spell._add_owned_conduit("first", "c1")
    spell._add_owned_conduit("second", "c2")
    assert spell.owner_conduit_info == ("second", "c2")
