"""Override melds run one compiled plan per key set (override design v2, step S3a).

Supplied dependencies and everything only they need are never constructed (B1); root positional
payloads over injected parameters work (B5); a PATH through a collection reaches every member (B7);
an empty positional payload behaves like a normal meld (B8). Key errors, the P2 refusal and the
equal-rank conflict rule keep today's messages. Every case runs on fresh conjures and on the
marshalled manifest cache path, for the many_only and generalized families.
"""

import marshal
import threading
from collections import Counter
from collections.abc import Iterator
from typing import Any, List, Tuple

import pytest

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spell_compiler.codegen_creation_system.shared_assets.manifest_creation_cache import (
    build_package,
    load_creation_context_lazy,
)
from melder.aether.spellbook.spellbook import Spellbook
from melder.utilities.custom_exceptions.meld_execution_error import MeldExecutionError

BUILT: Counter = Counter()


class Leaf:
    """A many dependency below the supplied branches."""

    def __init__(self) -> None:
        """Count the build."""
        BUILT["Leaf"] += 1


class A:
    """A branch with its own dependency."""

    def __init__(self, leaf: Leaf) -> None:
        """Count the build and keep the leaf."""
        BUILT["A"] += 1
        self.leaf = leaf


class B:
    """A second branch with no dependencies."""

    def __init__(self) -> None:
        """Count the build."""
        BUILT["B"] += 1


class Config:
    """Shared in the generalized family, many otherwise."""

    def __init__(self) -> None:
        """Count the build."""
        BUILT["Config"] += 1


class Root:
    """Root(a: A, b: B, config: Config, limit=3)."""

    def __init__(self, a: A, b: B, config: Config, limit: int = 3) -> None:
        """Count the build and keep the operands."""
        BUILT["Root"] += 1
        self.a = a
        self.b = b
        self.config = config
        self.limit = limit


class Part:
    """One of five parts of a consumer."""

    def __init__(self, leaf: Leaf) -> None:
        """Count the build."""
        BUILT["Part"] += 1
        self.leaf = leaf


class P1(Part):
    """Part 1."""


class P2(Part):
    """Part 2."""


class P3(Part):
    """Part 3."""


class P4(Part):
    """Part 4."""


class P5(Part):
    """Part 5."""


class Consumer:
    """Consumer of five parts."""

    def __init__(self, p1: P1, p2: P2, p3: P3, p4: P4, p5: P5) -> None:
        """Count the build and keep the parts."""
        BUILT["Consumer"] += 1
        self.parts = (p1, p2, p3, p4, p5)


class IMember:
    """Frame type for collection members."""


class MemberA(IMember):
    """First member."""

    def __init__(self, leaf: Leaf) -> None:
        """Keep the leaf."""
        self.leaf = leaf


class MemberB(IMember):
    """Second member."""

    def __init__(self, leaf: Leaf) -> None:
        """Keep the leaf."""
        self.leaf = leaf


class Holder:
    """Owner of a collection."""

    def __init__(self, members: list[IMember]) -> None:
        """Keep the members."""
        self.members = members


class Store:
    """A shared site with its own parameter."""

    def __init__(self, leaf: Leaf) -> None:
        """Count the build and keep the leaf."""
        BUILT["Store"] += 1
        self.leaf = leaf


class Left:
    """Left consumer of the shared store."""

    def __init__(self, store: Store) -> None:
        """Keep the store."""
        self.store = store


class Right:
    """Right consumer of the shared store."""

    def __init__(self, store: Store) -> None:
        """Keep the store."""
        self.store = store


class Pair:
    """Root over two consumers of one shared store."""

    def __init__(self, left: Left, right: Right) -> None:
        """Keep both."""
        self.left = left
        self.right = right


class Keeper:
    """Root over one shared store and a plain parameter."""

    def __init__(self, store: Store, limit: int = 3) -> None:
        """Count the build and keep the operands."""
        BUILT["Keeper"] += 1
        self.store = store
        self.limit = limit


@pytest.fixture
def book() -> Iterator[Spellbook]:
    """Own one isolated world with disk caching disabled."""
    BUILT.clear()
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether
    spellbook = Spellbook(aetheric_frame="override-key-set-plans")
    spellbook.get_configuration().set_property("phase_scheduler_workers_per_spellbook", 1)
    spellbook._aetheric_frame_configuration.with_system_caching_enabled(False)
    try:
        yield spellbook
    finally:
        spellbook.cleanup()
        Aether._reset_singleton_for_tests()
        aether = Aether()
        Spellbook._aether = aether
        Conduit._aether = aether


def _conjure(spellbook: Spellbook, bindings: List[Tuple[Any, Existence]], root: Any, cached: bool) -> Conduit:
    """Bind, conjure and optionally reinstall the root from its marshalled manifest package."""
    ids = {
        spell: spellbook.bind(spell=spell, existence=existence, permissions="create", **extra)
        for spell, existence, extra in (
            binding if len(binding) == 3 else (binding[0], binding[1], {}) for binding in bindings
        )
    }
    conduit = spellbook.conjure()
    if cached:
        selected = spellbook.find_spell_by_id(ids[root])
        package = build_package(selected)
        selected._cleanup_creation_context()
        load_creation_context_lazy(selected, marshal.loads(marshal.dumps(package)), publish=True)
    return conduit


def _root_world(spellbook: Spellbook, family: str, cached: bool) -> Conduit:
    """Root over A(Leaf), B and Config; Config is shared only in the generalized family."""
    config = Existence.unique_per_conduit if family == "generalized" else Existence.many
    return _conjure(
        spellbook,
        [(Leaf, Existence.many), (A, Existence.many), (B, Existence.many), (Config, config),
         (Root, Existence.many)],
        Root,
        cached,
    )


FAMILIES = pytest.mark.parametrize("family", ["many_only", "generalized"])
CACHED = pytest.mark.parametrize("cached", [False, True])


@FAMILIES
@CACHED
def test_supplied_dependency_and_its_subtree_are_never_built(book: Spellbook, family: str, cached: bool) -> None:
    """Supplying `a` builds neither A nor its Leaf; repeated melds reuse one plan (B1)."""
    conduit = _root_world(book, family, cached)
    supplied = object()
    for _ in range(3):
        BUILT.clear()
        result = conduit.meld(Root, override={"a": supplied})
        assert result.a is supplied
        assert BUILT["A"] == 0 and BUILT["Leaf"] == 0
        assert BUILT["Root"] == 1 and BUILT["B"] == 1


@FAMILIES
@CACHED
def test_plain_parameter_override_builds_every_dependency(book: Spellbook, family: str, cached: bool) -> None:
    """A plain parameter key changes only that operand."""
    conduit = _root_world(book, family, cached)
    BUILT.clear()
    result = conduit.meld(Root, override={"limit": 9})
    assert result.limit == 9
    assert BUILT["A"] == 1 and BUILT["Leaf"] == 1 and BUILT["B"] == 1 and BUILT["Root"] == 1


@CACHED
def test_three_of_five_supplied_parts_build_only_the_other_two(book: Spellbook, cached: bool) -> None:
    """The epic example: three supplied parts leave two parts plus the consumer to build."""
    conduit = _conjure(
        book,
        [(Leaf, Existence.many), (P1, Existence.many), (P2, Existence.many), (P3, Existence.many),
         (P4, Existence.many), (P5, Existence.many), (Consumer, Existence.many)],
        Consumer,
        cached,
    )
    given = [object(), object(), object()]
    BUILT.clear()
    result = conduit.meld(Consumer, override={"p1": given[0], "p2": given[1], "p3": given[2]})
    assert list(result.parts[:3]) == given
    assert BUILT == Counter({"Part": 2, "Leaf": 2, "Consumer": 1})


@FAMILIES
def test_positional_payload_over_injected_parameters(book: Spellbook, family: str) -> None:
    """`__args__` fills the leading injected parameters and cuts them (B5); extra values fail in the constructor."""
    conduit = _root_world(book, family, False)
    first = object()
    BUILT.clear()
    result = conduit.meld(Root, override=(first,))
    assert result.a is first
    assert BUILT["A"] == 0 and BUILT["B"] == 1
    with pytest.raises(MeldExecutionError):
        conduit.meld(Root, override=(1, 2, 3, 4, 5))


def test_path_through_a_collection_reaches_every_member(book: Spellbook) -> None:
    """`members>leaf` supplies the leaf of both members (B7); no Leaf is built."""
    conduit = _conjure(
        book,
        [(Leaf, Existence.many), (MemberA, Existence.many, {"spellframe": IMember, "binding_name": "a"}),
         (MemberB, Existence.many, {"spellframe": IMember, "binding_name": "b"}), (Holder, Existence.many)],
        Holder,
        False,
    )
    leaf = object()
    BUILT.clear()
    result = conduit.meld(Holder, override={"members>leaf": leaf})
    assert [member.leaf for member in result.members] == [leaf, leaf]
    assert BUILT["Leaf"] == 0


@FAMILIES
def test_empty_positional_payload_is_a_normal_meld(book: Spellbook, family: str) -> None:
    """`override=()` builds exactly what a normal meld builds (B8)."""
    conduit = _root_world(book, family, False)
    BUILT.clear()
    conduit.meld(Root)
    normal = Counter(BUILT)
    BUILT.clear()
    conduit.meld(Root, override=())
    if family == "generalized":
        normal.pop("Config")
    assert BUILT == normal


def _pair_world(spellbook: Spellbook, cached: bool) -> Conduit:
    """Pair(left: Left(store), right: Right(store)) with Store(leaf) shared per conduit."""
    return _conjure(
        spellbook,
        [(Leaf, Existence.many), (Store, Existence.unique_per_conduit), (Left, Existence.many),
         (Right, Existence.many), (Pair, Existence.many)],
        Pair,
        cached,
    )


@CACHED
def test_rule_on_a_stored_shared_site_keeps_the_p2_error(book: Spellbook, cached: bool) -> None:
    """A key on a stored shared site's own parameter raises today's error (P2)."""
    conduit = _pair_world(book, cached)
    conduit.meld(Pair)
    with pytest.raises(MeldExecutionError, match="spell instance that already exists"):
        conduit.meld(Pair, override={"left>store>leaf": object()})


@CACHED
def test_rule_on_an_unstored_shared_site_builds_it_with_the_value(book: Spellbook, cached: bool) -> None:
    """Before the shared site is stored, the key supplies its parameter and the site is published."""
    conduit = _pair_world(book, cached)
    leaf = object()
    BUILT.clear()
    result = conduit.meld(Pair, override={"left>store>leaf": leaf})
    assert result.left.store.leaf is leaf and result.right.store is result.left.store
    assert BUILT["Leaf"] == 0 and BUILT["Store"] == 1
    assert conduit.meld(Pair).left.store is result.left.store


def test_supplied_shared_dependency_is_not_built_or_stored(book: Spellbook) -> None:
    """Supplying a shared dependency leaves its store empty; a later normal meld builds it once."""
    conduit = _pair_world(book, False)
    given = object()
    BUILT.clear()
    result = conduit.meld(Pair, override={"**store": given})
    assert result.left.store is given and result.right.store is given
    assert BUILT["Store"] == 0 and BUILT["Leaf"] == 0
    normal = conduit.meld(Pair)
    assert normal.left.store is normal.right.store
    assert BUILT["Store"] == 1


def test_equal_rank_keys_accept_one_object_and_refuse_different_ones(book: Spellbook) -> None:
    """Two PATH keys reaching one shared parameter: one object passes, two objects fail (E1)."""
    conduit = _pair_world(book, False)
    leaf = object()
    result = conduit.meld(Pair, override={"left>store>leaf": leaf, "right>store>leaf": leaf})
    assert result.left.store.leaf is leaf
    with pytest.raises(MeldExecutionError, match="Failed to apply overrides") as caught:
        conduit.meld(Pair, override={"left>store>leaf": object(), "right>store>leaf": object()})
    assert "Conflicting overrides" in str(caught.value.__cause__)


@CACHED
def test_warm_override_meld_skips_the_children_of_a_stored_shared_site(book: Spellbook, cached: bool) -> None:
    """With Store stored, an override meld builds only the root: Leaf, which only Store needs, is skipped (B2)."""
    conduit = _conjure(
        book, [(Leaf, Existence.many), (Store, Existence.unique_per_conduit), (Keeper, Existence.many)], Keeper, cached,
    )
    BUILT.clear()
    first = conduit.meld(Keeper, override={"limit": 1})
    second = conduit.meld(Keeper, override={"limit": 2})
    assert second.store is first.store and (first.limit, second.limit) == (1, 2)
    assert BUILT == Counter({"Leaf": 1, "Store": 1, "Keeper": 2})


@CACHED
def test_warm_normal_meld_skips_the_children_of_a_stored_shared_site(book: Spellbook, cached: bool) -> None:
    """With Store stored, a normal meld builds only the root: Leaf, which only Store needs, is skipped (S2b-2)."""
    conduit = _conjure(
        book, [(Leaf, Existence.many), (Store, Existence.unique_per_conduit), (Keeper, Existence.many)], Keeper, cached,
    )
    BUILT.clear()
    first = conduit.meld(Keeper)
    second = conduit.meld(Keeper)
    assert second is not first and second.store is first.store
    assert BUILT == Counter({"Leaf": 1, "Store": 1, "Keeper": 2})


@FAMILIES
def test_bad_key_keeps_todays_text_and_is_retried(book: Spellbook, family: str) -> None:
    """A key that names nothing fails the same way on every call; a valid key still works after."""
    conduit = _root_world(book, family, False)
    for _ in range(2):
        with pytest.raises(MeldExecutionError, match="Failed to apply overrides") as caught:
            conduit.meld(Root, override={"a>nosuch": 1})
        assert "No sockets found for override path 'a>nosuch'" in str(caught.value.__cause__)
    assert conduit.meld(Root, override={"limit": 1}).limit == 1


@FAMILIES
def test_concurrent_override_melds_are_correct(book: Spellbook, family: str) -> None:
    """Threads melding with several key sets at once each get their own supplied values."""
    conduit = _root_world(book, family, False)
    errors: List[BaseException] = []
    barrier = threading.Barrier(8)

    def worker(index: int) -> None:
        try:
            barrier.wait()
            for round_index in range(50):
                supplied = object()
                key = ("a", "b", "limit")[(index + round_index) % 3]
                result = conduit.meld(Root, override={key: supplied})
                assert getattr(result, key) is supplied
        except BaseException as exc:
            errors.append(exc)

    threads = [threading.Thread(target=worker, args=(index,)) for index in range(8)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    assert errors == []


class NameReadingBase:
    """A base whose `__new__` records whether it received names or positions."""

    def __new__(cls, *args: Any, **kwargs: Any) -> Any:
        """Record (positional count, keyword names), then allocate."""
        instance = super().__new__(cls)
        instance.shape = (len(args), tuple(sorted(kwargs)))
        return instance


class NamedRoot(NameReadingBase):
    """Its signature is its own `__init__`'s; every call passes through the base `__new__`."""

    def __init__(self, leaf: Leaf, b: B, limit: int = 3) -> None:
        """Keep the operands."""
        self.leaf = leaf
        self.b = b
        self.limit = limit


@FAMILIES
@CACHED
def test_a_constructor_that_observes_names_receives_names(book: Spellbook, family: str, cached: bool) -> None:
    """Normal and override melds pass values by name when the call passes through a custom `__new__` (P5)."""
    shared_b = Existence.unique_per_conduit if family == "generalized" else Existence.many
    conduit = _conjure(
        book, [(Leaf, Existence.many), (B, shared_b), (NamedRoot, Existence.many)], NamedRoot, cached,
    )
    assert conduit.meld(NamedRoot).shape == (0, ("b", "leaf"))
    assert conduit.meld(NamedRoot, override={"limit": 9}).shape == (0, ("b", "leaf", "limit"))
    supplied = Leaf()
    result = conduit.meld(NamedRoot, override={"leaf": supplied})
    assert result.shape == (0, ("b", "leaf")) and result.leaf is supplied
