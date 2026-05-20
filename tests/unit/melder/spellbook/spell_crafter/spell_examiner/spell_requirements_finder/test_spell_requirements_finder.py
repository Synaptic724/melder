import ast
import builtins
import inspect
import threading
import typing
from types import SimpleNamespace
from typing import List, Optional, Union, get_args, get_origin

import pytest

from melder.aether.conduit.conduit_ward.permissions.permissions import Permissions
from melder.aether.conduit.meld.contracts.mutation_contract import MutationContract
from melder.aether.conduit.meld.contracts.spell_contract import SpellContract
from melder.aether.conduit.meld.contracts.spell_map import SpellMap
from melder.aether.spellbook.bind.spell_index import SpellIndex
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spell import Spell
from melder.aether.spellbook.spell_compiler.spell_requirements_finder.parameter_di_shape import (
    ParameterDIShape,
)
from melder.aether.spellbook.spell_compiler.spell_requirements_finder.spell_parameter_requirements import (
    SpellParameterRequirement,
)
from melder.aether.spellbook.spell_compiler.spell_requirements_finder.spell_requirements import (
    SpellRequirements,
)
from melder.aether.spellbook.spell_compiler.spell_requirements_finder.spell_requirements_finder import (
    SpellRequirementsFinder,
)
from melder.aether.spellbook.spell_types.spell_types import SpellType
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


class _SupportsGetItem:
    @classmethod
    def __class_getitem__(cls, item):
        return ("ok", item)


class _BrokenGetItem:
    @classmethod
    def __class_getitem__(cls, item):
        raise RuntimeError("boom")


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


def test_finder_constructor_rejects_none_spell():
    with pytest.raises(ValueError, match="spell must not be None"):
        SpellRequirementsFinder(None)


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


def test_cleanup_swallows_requirement_cleanup_errors_and_rechecks_cleaned_inside_lock():
    class ExplodingRequirements:
        def cleanup(self):
            raise RuntimeError("boom")

    class _CoordinatedLock:
        def __init__(self) -> None:
            self._entered_first = threading.Event()
            self._second_attempted = threading.Event()
            self._lock = threading.RLock()

        def __enter__(self):
            if self._entered_first.is_set():
                self._second_attempted.set()
            self._lock.acquire()
            if not self._entered_first.is_set():
                self._entered_first.set()
                assert self._second_attempted.wait(timeout=1.0)
            return self

        def __exit__(self, exc_type, exc, tb):
            self._lock.release()

    finder = SpellRequirementsFinder(_make_spell(lambda: None))
    finder._requirements = ExplodingRequirements()
    finder.cleanup()
    assert finder.cleaned is True

    finder = SpellRequirementsFinder(_make_spell(lambda: None))
    coordinated_lock = _CoordinatedLock()
    finder._lock = coordinated_lock
    thread_results = []

    def _run_cleanup() -> None:
        finder.cleanup()
        thread_results.append(True)

    first = threading.Thread(target=_run_cleanup)
    second = threading.Thread(target=_run_cleanup)
    first.start()
    coordinated_lock._entered_first.wait(timeout=1.0)
    second.start()
    first.join(timeout=1.0)
    second.join(timeout=1.0)

    assert thread_results == [True, True]
    assert finder.cleaned is True
    assert not hasattr(finder, '_lock')


def test_resolve_call_target_returns_spell_callable():
    fn = lambda x: x  # noqa: E731
    spell = _make_spell(fn, spell_type=SpellType.METHOD)
    finder = SpellRequirementsFinder(spell)
    target = finder._resolve_call_target(spell)
    assert target is fn


def test_resolve_call_target_falls_back_to_raw_spell_object():
    spell = _make_spell(object(), spell_type=SpellType.EXISTING_CREATION)
    finder = SpellRequirementsFinder(spell)
    assert finder._resolve_call_target(spell) is spell.spell


def test_spell_property_and_annotation_resolution_fast_paths(monkeypatch):
    finder = SpellRequirementsFinder(_make_spell(lambda: None))
    signature = inspect.signature(lambda value: value)

    assert finder.spell is finder._spell
    assert finder._should_resolve_annotations(
        call_target=None,
        signature=signature,
    ) is False

    monkeypatch.delattr(inspect, "get_annotations")
    assert finder._should_resolve_annotations(
        call_target=lambda value: value,
        signature=signature,
    ) is True


@pytest.mark.parametrize(
    "text, expected",
    [
        ("", False),
        (" dep", False),
        ("None", False),
        ("pkg.", False),
        ("foo[bar]", False),
        ("foo bar", False),
        ("pkg.Dep", True),
    ],
)
def test_simple_name_resolution_and_invalid_name_forms(text, expected):
    finder = SpellRequirementsFinder(_make_spell(lambda: None))
    assert finder._is_simple_annotation_name(text) is expected


def test_name_and_expression_resolution_helper_edges():
    finder = SpellRequirementsFinder(_make_spell(lambda: None))
    sentinel = object()

    localns = {"Dep": Dep}
    globalns = {
        "__builtins__": {"int": int},
        "builtins": builtins,
        "pkg": Namespace,
    }

    assert finder._resolve_annotation_name("Dep", globalns, localns) is Dep
    assert finder._resolve_annotation_name("int", globalns, {}) is int
    assert finder._resolve_annotation_name("pkg.Dep", globalns, {}) is Dep
    assert finder._resolve_annotation_name("pkg.Missing", globalns, {}) is None

    parsed, value = finder._parse_annotation_expression("list[", globalns, localns)
    assert parsed is False
    assert value is None

    parsed, value = finder._parse_annotation_expression("call(Dep)", globalns, localns)
    assert parsed is False
    assert value is None

    node = ast.parse("pkg.Dep", mode="eval").body
    assert finder._resolve_annotation_node(
        node=node,
        globalns={},
        localns={},
        sentinel=sentinel,
    ) == "pkg.Dep"

    node = ast.parse("pkg.Missing", mode="eval").body
    assert finder._resolve_annotation_node(
        node=node,
        globalns={"pkg": SimpleNamespace()},
        localns={},
        sentinel=sentinel,
    ) is sentinel

    node = ast.parse("pkg.Missing | Dep", mode="eval").body
    assert finder._resolve_annotation_node(
        node=node,
        globalns={"pkg": SimpleNamespace(), "Dep": Dep},
        localns={},
        sentinel=sentinel,
    ) is sentinel

    node = ast.parse("pkg.Missing[Dep]", mode="eval").body
    assert finder._resolve_annotation_node(
        node=node,
        globalns={"pkg": SimpleNamespace(), "Dep": Dep},
        localns={},
        sentinel=sentinel,
    ) is sentinel

    node = ast.parse("list[pkg.Missing]", mode="eval").body
    assert finder._resolve_annotation_node(
        node=node,
        globalns={"pkg": SimpleNamespace()},
        localns={},
        sentinel=sentinel,
    ) is sentinel


def test_annotation_build_and_normalize_helper_edges():
    finder = SpellRequirementsFinder(_make_spell(lambda: None))
    sentinel = object()

    assert finder._build_subscripted_annotation(
        container=list,
        args=tuple(),
        sentinel=sentinel,
    ) is sentinel
    assert finder._build_subscripted_annotation(
        container=list,
        args=(int, str),
        sentinel=sentinel,
    ) is sentinel
    assert finder._build_subscripted_annotation(
        container=set,
        args=(int, str),
        sentinel=sentinel,
    ) is sentinel
    assert finder._build_subscripted_annotation(
        container=frozenset,
        args=(int, str),
        sentinel=sentinel,
    ) is sentinel
    assert finder._build_subscripted_annotation(
        container=dict,
        args=(int,),
        sentinel=sentinel,
    ) is sentinel
    assert finder._build_subscripted_annotation(
        container=Optional,
        args=(int, str),
        sentinel=sentinel,
    ) is sentinel

    class _SupportsGetItem:
        @classmethod
        def __class_getitem__(cls, item):
            return ("ok", item)

    class _BrokenGetItem:
        @classmethod
        def __class_getitem__(cls, item):
            raise RuntimeError("boom")

    assert finder._build_subscripted_annotation(
        container=_SupportsGetItem,
        args=(int,),
        sentinel=sentinel,
    ) == ("ok", int)
    assert finder._build_subscripted_annotation(
        container=_BrokenGetItem,
        args=(int,),
        sentinel=sentinel,
    ) is sentinel

    assert finder._normalize_annotation(
        annotation=None,
        globalns={},
        localns={},
    ) is None
    assert finder._normalize_annotation(
        annotation="pkg.Dep",
        globalns={},
        localns={},
    ) == "pkg.Dep"
    assert finder._normalize_annotation(
        annotation=typing.List,
        globalns={},
        localns={},
    ) is typing.List

    assert finder._rebuild_annotation(
        annotation=typing.List,
        origin=list,
        args=tuple(),
    ) is typing.List
    assert finder._rebuild_annotation(
        annotation=typing.List[int],
        origin=set,
        args=(int,),
    ) == set[int]
    assert finder._rebuild_annotation(
        annotation=typing.List[int],
        origin=frozenset,
        args=(int,),
    ) == frozenset[int]
    assert finder._rebuild_annotation(
        annotation=typing.Tuple[int, ...],
        origin=tuple,
        args=(int, Ellipsis),
    ) == tuple[int, Ellipsis]
    unchanged = typing.Iterable[int]
    assert finder._rebuild_annotation(
        annotation=unchanged,
        origin=get_origin(unchanged),
        args=get_args(unchanged),
    ) is unchanged


def test_resolve_parameter_annotations_handles_none_class_targets_and_fallbacks(monkeypatch):
    finder = SpellRequirementsFinder(_make_spell(lambda: None))

    assert finder._resolve_parameter_annotations(None) == {}

    def plain(value: int):
        return value

    assert finder._resolve_parameter_annotations(plain) == plain.__annotations__

    class Service:
        def __init__(self, dep: "Dep"):
            self.dep = dep

    resolved = finder._resolve_parameter_annotations(Service)
    assert resolved["dep"] is Dep

    class NoAnnotations:
        def __call__(self, value):
            return value

    assert finder._resolve_parameter_annotations(NoAnnotations()) == {}

    monkeypatch.delattr(inspect, "get_annotations")
    assert finder._resolve_parameter_annotations(plain) == {}


def test_resolve_parameter_annotations_falls_back_when_get_annotations_raises(monkeypatch):
    finder = SpellRequirementsFinder(_make_spell(lambda: None))

    def typed(value: "Dep"):
        return value

    def _raise(*args, **kwargs):
        raise RuntimeError("boom")

    monkeypatch.setattr(inspect, "get_annotations", _raise)

    resolved = finder._resolve_parameter_annotations(typed)

    assert resolved == {}


def test_name_resolution_and_annotation_normalization_remaining_edges():
    finder = SpellRequirementsFinder(_make_spell(lambda: None))

    assert finder._resolve_annotation_name(
        "len",
        {"__builtins__": builtins},
        {},
    ) is len

    assert finder._normalize_annotation(
        annotation="'pkg.Dep'",
        globalns={},
        localns={},
    ) == "pkg.Dep"
    assert finder._normalize_annotation(
        annotation="call(Dep)",
        globalns={"Dep": Dep},
        localns={},
    ) == "call(Dep)"


def test_remaining_subscript_optional_and_di_target_edges():
    finder = SpellRequirementsFinder(_make_spell(lambda: None))
    sentinel = object()

    assert finder._build_subscripted_annotation(
        container=set,
        args=(int,),
        sentinel=sentinel,
    ) == set[int]
    assert finder._build_subscripted_annotation(
        container=frozenset,
        args=(int,),
        sentinel=sentinel,
    ) == frozenset[int]
    assert finder._build_subscripted_annotation(
        container=dict,
        args=(str, int),
        sentinel=sentinel,
    ) == dict[str, int]
    assert finder._build_subscripted_annotation(
        container=tuple,
        args=(int, str),
        sentinel=sentinel,
    ) == tuple[int, str]
    assert finder._build_subscripted_annotation(
        container=_SupportsGetItem,
        args=(int, str),
        sentinel=sentinel,
    ) == ("ok", (int, str))

    annotation, is_optional, origin, args = finder._unwrap_optional(
        annotation=typing.Union[typing.ForwardRef("Dep"), None],
        origin=Union,
        args=get_args(typing.Union[typing.ForwardRef("Dep"), None]),
    )
    assert annotation == "Dep"
    assert is_optional is True

    annotation, is_optional, origin, args = finder._unwrap_optional(
        annotation=typing.Union[Dep, str, None],
        origin=Union,
        args=get_args(typing.Union[Dep, str, None]),
    )
    assert annotation == typing.Union[Dep, str, None]
    assert is_optional is True

    assert finder._looks_like_di_target(typing.Any) is False
    assert finder._looks_like_di_target(typing.ForwardRef("Dep")) is True
    assert finder._looks_like_di_target("Dep") is True
    assert finder._looks_like_di_target(int) is False
    assert finder._looks_like_di_target(Dep) is True
    assert finder._looks_like_di_target(typing.Callable) is False


def test_remaining_helper_edges_for_builtins_sentinels_and_tuple_paths(monkeypatch):
    finder = SpellRequirementsFinder(_make_spell(lambda: None))
    sentinel = object()

    class _GlobalsCarrier:
        __annotations__ = {"value": "int"}
        __globals__ = {}

    monkeypatch.setattr(
        inspect,
        "get_annotations",
        lambda *args, **kwargs: {"value": "int"},
    )
    assert finder._resolve_parameter_annotations(_GlobalsCarrier())["value"] is int

    node = ast.parse("call(Dep).attr", mode="eval").body
    assert finder._resolve_annotation_node(
        node=node,
        globalns={"Dep": Dep},
        localns={},
        sentinel=sentinel,
    ) is sentinel

    assert finder._build_subscripted_annotation(
        container=tuple,
        args=(int, Ellipsis),
        sentinel=sentinel,
    ) == tuple[int, Ellipsis]
    assert finder._build_subscripted_annotation(
        container=object(),
        args=(int,),
        sentinel=sentinel,
    ) is sentinel

    assert finder._rebuild_annotation(
        annotation=typing.Tuple[int, str],
        origin=tuple,
        args=(int, str),
    ) == tuple[int, str]

    assert finder._looks_like_di_target(list) is False


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
