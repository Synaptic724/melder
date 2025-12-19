import inspect
from typing import Optional, Union

import pytest

from melder.aether.conduit.conduit_ward.permissions.permissions import Permissions
from melder.aether.conduit.meld.contracts.mutation_contract import MutationContract
from melder.aether.conduit.meld.contracts.spell_contract import SpellContract
from melder.aether.conduit.meld.contracts.spell_map import SpellMap
from melder.spellbook.bind.spell_index import SpellIndex
from melder.spellbook.existence.existence import Existence
from melder.spellbook.spell import Spell
from melder.spellbook.spell_crafter.spell_examiner.spell_requirements_finder.parameter_di_shape import (
    ParameterDIShape,
)
from melder.spellbook.spell_crafter.spell_examiner.spell_requirements_finder.spell_parameter_requirements import (
    SpellParameterRequirement,
)
from melder.spellbook.spell_crafter.spell_examiner.spell_requirements_finder.spell_requirements import (
    SpellRequirements,
)
from melder.spellbook.spell_crafter.spell_examiner.spell_requirements_finder.spell_requirements_finder import (
    SpellRequirementsFinder,
)
from melder.spellbook.spell_types.spell_types import SpellType
from melder.utilities.custom_exceptions.operation_cancelled_error import (
    OperationCancelledError,
)
from melder.utilities.synchronization.cancellation_event_signal import (
    CancellationEventSignal,
)


class _StubSpellbook:
    def __init__(self):
        self._spell_system_states = object()


def _make_spell(
    call_target,
    *,
    spell_type: SpellType = SpellType.SPELL,
    spellframe=None,
    binding_name=None,
    version: str = "v1",
) -> Spell:
    return Spell(
        call_target,
        SpellIndex(version),
        spellframe,
        binding_name,
        getattr(call_target, "__name__", "name"),
        Existence.unique,
        spell_type,
        "id",
        Permissions.read,
        "frame",
        spellbook=_StubSpellbook(),
    )


def _reqs_for(func, *, spell_type=SpellType.METHOD):
    spell = _make_spell(func, spell_type=spell_type)
    return SpellRequirementsFinder(spell).build_requirements()


def _by_name(reqs: SpellRequirements):
    return {p.name: p for p in reqs.parameters}


class Dep:
    ...


def test_existing_creation_spells_have_no_parameters():
    for st in (
        SpellType.EXISTING_CREATION,
        SpellType.EXISTING_CREATION_WITH_SPELLFRAME,
        SpellType.EXISTING_CREATION_WITH_BINDING_NAME_WITH_SPELLFRAME,
    ):
        spell = _make_spell(object(), spell_type=st, version="v123")
        reqs = SpellRequirementsFinder(spell).build_requirements()
        assert reqs.spell_id == "v123"
        assert reqs.parameters == ()


def test_build_requirements_is_cached_until_cleanup():
    spell = _make_spell(lambda: None)
    finder = SpellRequirementsFinder(spell)
    r1 = finder.build_requirements()
    r2 = finder.build_requirements()
    assert r1 is r2

    finder.cleanup()
    with pytest.raises(RuntimeError):
        _ = r1.parameters  # cleaned requirements should block access

    # after cleanup, building again yields a fresh instance
    finder2 = SpellRequirementsFinder(spell)
    r3 = finder2.build_requirements()
    assert r3 is not r1


def test_resolve_call_target_returns_spell_callable():
    fn = lambda x: x  # noqa: E731
    spell = _make_spell(fn, spell_type=SpellType.METHOD)
    finder = SpellRequirementsFinder(spell)
    target = finder._resolve_call_target(spell)
    assert target is fn


def test_parameter_classification_shapes_and_optional_logic():
    spellmap_default = SpellMap(spellframe="frame-key")
    mutation_default = MutationContract(spellframe="frame-key")
    contract_default = SpellContract(spellframe="frame-key")

    def target(
        self,
        dep: Dep,
        opt_dep: Optional[Dep],
        dep_list: list[Dep],
        plain,
        opt_plain="x",
        builtin_list: list[str] = None,
        spellmap=spellmap_default,
        mutation: MutationContract = mutation_default,
        contract: SpellContract = contract_default,
        opt_union: Optional[Dep] = None,
        union_multi: Union[Dep, str, None] = None,
        *args,
        **kwargs,
    ):
        return (
            dep,
            opt_dep,
            dep_list,
            plain,
            opt_plain,
            builtin_list,
            spellmap,
            mutation,
            contract,
            opt_union,
            union_multi,
            args,
            kwargs,
        )

    reqs = _reqs_for(target)
    by_name = _by_name(reqs)

    def shape(name):
        return by_name[name].di_shape

    def optional(name):
        return by_name[name].is_optional

    # self/args/kwargs ignored
    assert shape("self") is ParameterDIShape.IGNORE and optional("self") is True
    assert by_name["args"].is_var_positional and by_name["args"].di_shape is ParameterDIShape.IGNORE
    assert by_name["kwargs"].is_var_keyword and by_name["kwargs"].di_shape is ParameterDIShape.IGNORE

    assert shape("dep") is ParameterDIShape.SINGLE_BY_ANNOTATION
    assert optional("dep") is False

    assert shape("opt_dep") is ParameterDIShape.SINGLE_BY_ANNOTATION
    assert optional("opt_dep") is True

    assert shape("dep_list") is ParameterDIShape.COLLECTION_BY_ANNOTATION
    assert by_name["dep_list"].collection_element_annotation is Dep

    assert shape("plain") is ParameterDIShape.PLAIN and optional("plain") is False
    assert optional("opt_plain") is True

    # builtin collection stays plain
    assert shape("builtin_list") is ParameterDIShape.PLAIN

    assert shape("spellmap") is ParameterDIShape.SPELLMAP_DEFAULT
    assert by_name["spellmap"].spellmap_default is spellmap_default

    assert shape("mutation") is ParameterDIShape.MUTATION_CONTRACT
    assert shape("contract") is ParameterDIShape.SPELL_CONTRACT

    assert shape("opt_union") is ParameterDIShape.SINGLE_BY_ANNOTATION
    assert optional("opt_union") is True

    # union containing builtin keeps plain
    assert shape("union_multi") is ParameterDIShape.PLAIN
    assert optional("union_multi") is True


def test_string_annotation_counts_as_di_target():
    def f(x: "Dep"):
        return x

    reqs = _reqs_for(f, spell_type=SpellType.METHOD)
    p = _by_name(reqs)["x"]
    assert p.di_shape is ParameterDIShape.SINGLE_BY_ANNOTATION
    assert p.annotation == "Dep"


def test_builtin_annotation_stays_plain():
    def f(x: int):
        return x

    p = _by_name(_reqs_for(f))["x"]
    assert p.di_shape is ParameterDIShape.PLAIN
    assert p.annotation is int


def test_signature_failure_returns_empty_parameters(monkeypatch):
    monkeypatch.setattr(inspect, "signature", lambda _: (_ for _ in ()).throw(TypeError("boom")))

    def f(x):
        return x

    reqs = _reqs_for(f)
    assert reqs.parameters == ()


def test_cancellation_raises_operation_cancelled():
    spell = _make_spell(lambda: None)
    finder = SpellRequirementsFinder(spell)
    signal = CancellationEventSignal()
    signal.cancel()
    with pytest.raises(OperationCancelledError):
        finder.build_requirements(signal.event)


def test_cleanup_idempotent_and_nuls_references():
    spell = _make_spell(lambda: None)
    finder = SpellRequirementsFinder(spell)
    reqs = finder.build_requirements()
    finder.cleanup()
    finder.cleanup()  # idempotent

    assert reqs._cleaned is True
    with pytest.raises(RuntimeError):
        _ = finder.spell


def test_spell_requirements_cleanup_swallows_child_errors_and_blocks_access():
    class Child(SpellParameterRequirement):
        def __init__(self):
            super().__init__(
                name="a",
                position=0,
                kind=inspect.Parameter.POSITIONAL_OR_KEYWORD,
                annotation=None,
                default_value=None,
                has_default=False,
                is_var_positional=False,
                is_var_keyword=False,
                is_keyword_only=False,
                is_optional=False,
                di_shape=ParameterDIShape.PLAIN,
            )

        def cleanup(self):
            super().cleanup()
            raise RuntimeError("boom")

    reqs = SpellRequirements(
        spell_id="s",
        spell_type=SpellType.SPELL,
        existence=Existence.unique,
        spellframe=None,
        binding_name=None,
        parameters=[Child()],
    )

    reqs.cleanup()
    assert reqs._cleaned is True
    with pytest.raises(RuntimeError):
        _ = reqs.parameters
