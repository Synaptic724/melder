import inspect
from typing import List, Optional, Union, get_args, get_origin

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


class Namespace:
    Dep = Dep


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
    assert p.annotation is Dep


def test_string_annotation_dotted_name_resolves_to_attribute():
    def f(x: "Namespace.Dep"):
        return x

    reqs = _reqs_for(f, spell_type=SpellType.METHOD)
    p = _by_name(reqs)["x"]
    assert p.di_shape is ParameterDIShape.SINGLE_BY_ANNOTATION
    assert p.annotation is Dep


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


def test_forward_ref_list_annotation_resolves_collection_element() -> None:
    """
    Purpose:
        Validate forward-ref list annotations resolve to collection DI.
    Contract:
        - list["Dep"] is classified as collection DI.
        - The element annotation resolves to Dep.
    Returns:
        None.
    Raises:
        AssertionError: If classification or element resolution fails.
    """
    def f(x: list["Dep"]):
        """
        Purpose:
            Provide a target signature with a forward-ref list annotation.
        Contract:
            Returns the input for completeness.
        Args:
            x: Forward-ref annotated parameter.
        Returns:
            Any.
        """
        return x

    reqs = _reqs_for(f, spell_type=SpellType.METHOD)
    p = _by_name(reqs)["x"]
    assert p.di_shape is ParameterDIShape.COLLECTION_BY_ANNOTATION
    assert p.collection_element_annotation is Dep


def test_forward_ref_typing_list_annotation_resolves_collection_element() -> None:
    """
    Purpose:
        Validate typing.List forward-ref annotations resolve to collection DI.
    Contract:
        - List["Dep"] is classified as collection DI.
        - The element annotation resolves to Dep.
    Returns:
        None.
    Raises:
        AssertionError: If classification or element resolution fails.
    """
    def f(x: List["Dep"]):
        """
        Purpose:
            Provide a target signature with typing.List forward-ref annotations.
        Contract:
            Returns the input for completeness.
        Args:
            x: Forward-ref annotated parameter.
        Returns:
            Any.
        """
        return x

    reqs = _reqs_for(f, spell_type=SpellType.METHOD)
    p = _by_name(reqs)["x"]
    assert p.di_shape is ParameterDIShape.COLLECTION_BY_ANNOTATION
    assert p.collection_element_annotation is Dep


def test_forward_ref_optional_annotation_marks_optional() -> None:
    """
    Purpose:
        Validate Optional forward-ref annotations are treated as optional DI.
    Contract:
        - Optional["Dep"] is classified as single DI.
        - is_optional is True.
    Returns:
        None.
    Raises:
        AssertionError: If optional classification fails.
    """
    def f(x: Optional["Dep"]):
        """
        Purpose:
            Provide a target signature with an Optional forward-ref annotation.
        Contract:
            Returns the input for completeness.
        Args:
            x: Optional forward-ref parameter.
        Returns:
            Any.
        """
        return x

    reqs = _reqs_for(f, spell_type=SpellType.METHOD)
    p = _by_name(reqs)["x"]
    assert p.di_shape is ParameterDIShape.SINGLE_BY_ANNOTATION
    assert p.is_optional is True


def test_forward_ref_union_annotation_marks_optional() -> None:
    """
    Purpose:
        Validate Union forward-ref annotations are treated as optional DI.
    Contract:
        - Union["Dep", None] is classified as single DI.
        - is_optional is True.
    Returns:
        None.
    Raises:
        AssertionError: If optional classification fails.
    """
    def f(x: Union["Dep", None]):
        """
        Purpose:
            Provide a target signature with a Union forward-ref annotation.
        Contract:
            Returns the input for completeness.
        Args:
            x: Union forward-ref parameter.
        Returns:
            Any.
        """
        return x

    reqs = _reqs_for(f, spell_type=SpellType.METHOD)
    p = _by_name(reqs)["x"]
    assert p.di_shape is ParameterDIShape.SINGLE_BY_ANNOTATION
    assert p.is_optional is True


def test_string_expression_typing_optional_parses_and_marks_optional(monkeypatch) -> None:
    """
    Purpose:
        Validate typing.Optional string expressions are parsed into DI hints.
    Contract:
        - typing.Optional[Dep] becomes an optional single-annotation requirement.
        - The resolved annotation contains Dep and None.
    Returns:
        None.
    Raises:
        AssertionError: If parsing or classification fails.
    """
    def f(x: object) -> object:
        """
        Purpose:
            Provide a signature for Optional string-expression parsing.
        Contract:
            Returns the input for completeness.
        Args:
            x: Arbitrary input value.
        Returns:
            object: The input.
        """
        return x

    def fake_get_annotations(*args: object, **kwargs: object) -> dict[str, str]:
        """
        Purpose:
            Provide a deterministic string annotation payload.
        Contract:
            Returns a typing.Optional string expression for parameter "x".
        Args:
            *args: Unused positional arguments.
            **kwargs: Unused keyword arguments.
        Returns:
            dict[str, str]: The fake annotations mapping.
        """
        return {"x": "typing.Optional[Dep]"}

    monkeypatch.setattr(inspect, "get_annotations", fake_get_annotations)

    reqs = _reqs_for(f, spell_type=SpellType.METHOD)
    p = _by_name(reqs)["x"]
    assert p.di_shape is ParameterDIShape.SINGLE_BY_ANNOTATION
    assert p.is_optional is True
    assert Dep in get_args(p.annotation)
    assert type(None) in get_args(p.annotation)


def test_string_expression_typing_union_parses_and_marks_optional(monkeypatch) -> None:
    """
    Purpose:
        Validate typing.Union string expressions are parsed into DI hints.
    Contract:
        - typing.Union[Dep, None] becomes an optional single-annotation requirement.
        - The resolved annotation contains Dep and None.
    Returns:
        None.
    Raises:
        AssertionError: If parsing or classification fails.
    """
    def f(x: object) -> object:
        """
        Purpose:
            Provide a signature for Union string-expression parsing.
        Contract:
            Returns the input for completeness.
        Args:
            x: Arbitrary input value.
        Returns:
            object: The input.
        """
        return x

    def fake_get_annotations(*args: object, **kwargs: object) -> dict[str, str]:
        """
        Purpose:
            Provide a deterministic string annotation payload.
        Contract:
            Returns a typing.Union string expression for parameter "x".
        Args:
            *args: Unused positional arguments.
            **kwargs: Unused keyword arguments.
        Returns:
            dict[str, str]: The fake annotations mapping.
        """
        return {"x": "typing.Union[Dep, None]"}

    monkeypatch.setattr(inspect, "get_annotations", fake_get_annotations)

    reqs = _reqs_for(f, spell_type=SpellType.METHOD)
    p = _by_name(reqs)["x"]
    assert p.di_shape is ParameterDIShape.SINGLE_BY_ANNOTATION
    assert p.is_optional is True
    assert Dep in get_args(p.annotation)
    assert type(None) in get_args(p.annotation)


def test_string_expression_pep604_parses_and_marks_optional(monkeypatch) -> None:
    """
    Purpose:
        Validate PEP 604 string expressions are parsed into DI hints.
    Contract:
        - Dep | None becomes an optional single-annotation requirement.
        - The resolved annotation contains Dep and None.
    Returns:
        None.
    Raises:
        AssertionError: If parsing or classification fails.
    """
    def f(x: object) -> object:
        """
        Purpose:
            Provide a signature for PEP 604 string-expression parsing.
        Contract:
            Returns the input for completeness.
        Args:
            x: Arbitrary input value.
        Returns:
            object: The input.
        """
        return x

    def fake_get_annotations(*args: object, **kwargs: object) -> dict[str, str]:
        """
        Purpose:
            Provide a deterministic string annotation payload.
        Contract:
            Returns a PEP 604 string expression for parameter "x".
        Args:
            *args: Unused positional arguments.
            **kwargs: Unused keyword arguments.
        Returns:
            dict[str, str]: The fake annotations mapping.
        """
        return {"x": "Dep | None"}

    monkeypatch.setattr(inspect, "get_annotations", fake_get_annotations)

    reqs = _reqs_for(f, spell_type=SpellType.METHOD)
    p = _by_name(reqs)["x"]
    assert p.di_shape is ParameterDIShape.SINGLE_BY_ANNOTATION
    assert p.is_optional is True
    assert Dep in get_args(p.annotation)
    assert type(None) in get_args(p.annotation)


def test_string_expression_typing_list_parses_collection_element(monkeypatch) -> None:
    """
    Purpose:
        Validate typing.List string expressions are parsed into collection DI.
    Contract:
        - typing.List[Dep] becomes a collection annotation with Dep elements.
    Returns:
        None.
    Raises:
        AssertionError: If parsing or classification fails.
    """
    def f(x: object) -> object:
        """
        Purpose:
            Provide a signature for typing.List string-expression parsing.
        Contract:
            Returns the input for completeness.
        Args:
            x: Arbitrary input value.
        Returns:
            object: The input.
        """
        return x

    def fake_get_annotations(*args: object, **kwargs: object) -> dict[str, str]:
        """
        Purpose:
            Provide a deterministic string annotation payload.
        Contract:
            Returns a typing.List string expression for parameter "x".
        Args:
            *args: Unused positional arguments.
            **kwargs: Unused keyword arguments.
        Returns:
            dict[str, str]: The fake annotations mapping.
        """
        return {"x": "typing.List[Dep]"}

    monkeypatch.setattr(inspect, "get_annotations", fake_get_annotations)

    reqs = _reqs_for(f, spell_type=SpellType.METHOD)
    p = _by_name(reqs)["x"]
    assert p.di_shape is ParameterDIShape.COLLECTION_BY_ANNOTATION
    assert p.collection_element_annotation is Dep
    assert get_origin(p.annotation) is list


def test_forward_ref_local_class_annotation_remains_string() -> None:
    """
    Purpose:
        Validate local forward-ref annotations stay as strings when unresolved.
    Contract:
        - Local forward refs remain string annotations.
        - DI shape still classifies as single by annotation.
    Returns:
        None.
    Raises:
        AssertionError: If annotation normalization behaves unexpectedly.
    """
    class LocalDep:
        """
        Purpose:
            Provide a local dependency for forward-ref tests.
        Contract:
            Serves as a local-only annotation target.
        """

    def f(x: "LocalDep"):
        """
        Purpose:
            Provide a target signature with a local forward-ref annotation.
        Contract:
            Returns the input for completeness.
        Args:
            x: Local forward-ref parameter.
        Returns:
            Any.
        """
        return x

    reqs = _reqs_for(f, spell_type=SpellType.METHOD)
    p = _by_name(reqs)["x"]
    assert p.di_shape is ParameterDIShape.SINGLE_BY_ANNOTATION
    assert p.annotation == "LocalDep"


def test_forward_ref_nested_list_annotation_is_plain() -> None:
    """
    Purpose:
        Validate nested list annotations are not treated as DI collections.
    Contract:
        - list[list["Dep"]] is classified as plain.
    Returns:
        None.
    Raises:
        AssertionError: If nested list DI is misclassified.
    """
    def f(x: list[list["Dep"]]):
        """
        Purpose:
            Provide a target signature with a nested list annotation.
        Contract:
            Returns the input for completeness.
        Args:
            x: Nested list parameter.
        Returns:
            Any.
        """
        return x

    reqs = _reqs_for(f, spell_type=SpellType.METHOD)
    p = _by_name(reqs)["x"]
    assert p.di_shape is ParameterDIShape.PLAIN


def test_forward_ref_dict_annotation_is_plain() -> None:
    """
    Purpose:
        Validate dict annotations with forward refs are not treated as DI.
    Contract:
        - dict[str, "Dep"] is classified as plain.
    Returns:
        None.
    Raises:
        AssertionError: If dict annotations are misclassified.
    """
    def f(x: dict[str, "Dep"]):
        """
        Purpose:
            Provide a target signature with a dict forward-ref annotation.
        Contract:
            Returns the input for completeness.
        Args:
            x: Dict forward-ref parameter.
        Returns:
            Any.
        """
        return x

    reqs = _reqs_for(f, spell_type=SpellType.METHOD)
    p = _by_name(reqs)["x"]
    assert p.di_shape is ParameterDIShape.PLAIN


def test_forward_ref_builtin_list_annotation_is_plain() -> None:
    """
    Purpose:
        Validate builtin forward-ref annotations do not trigger DI.
    Contract:
        - list["int"] is classified as plain.
    Returns:
        None.
    Raises:
        AssertionError: If builtin annotations are misclassified.
    """
    def f(x: list["int"]):
        """
        Purpose:
            Provide a target signature with a builtin forward-ref list annotation.
        Contract:
            Returns the input for completeness.
        Args:
            x: Builtin forward-ref parameter.
        Returns:
            Any.
        """
        return x

    reqs = _reqs_for(f, spell_type=SpellType.METHOD)
    p = _by_name(reqs)["x"]
    assert p.di_shape is ParameterDIShape.PLAIN
