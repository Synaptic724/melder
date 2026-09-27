"""Differential oracle: the site-graph key resolver against today's override targeting (override design S1).

Every key today's targeting accepts (all exact paths it indexes plus `*name` and `**name` for every parameter
name) and a set of invalid keys are resolved by both implementations on real conjured graphs. They must
agree on the targeted (spell id, parameter) pairs, on how many logical sockets each key reaches, and on
the error raised. The one recorded difference: today's targeting keeps only the last member for a PATH
through a collection; the resolver keeps every member.
"""

from collections import Counter
from collections.abc import Iterator
from typing import Any, Dict, List, Optional, Tuple, Union

import pytest

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spell import Spell
from melder.aether.spellbook.spell_compiler.codegen_creation_system.shared_assets.override_key_resolver import (
    OverrideKeyResolver,
)
from melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.many_only.artifacts.spell_override_targeting_codegen_creation import (
    SpellOverrideTargetingCodegenCreation,
)
from melder.aether.spellbook.spell_compiler.dag.target_spec import TargetSpec, TargetSpecKind
from melder.aether.spellbook.spellbook import Spellbook

Outcome = Union[Tuple[str, Counter], Tuple[str, str, str]]


class Leaf:
    """A dependency with no parameters."""


class Other:
    """A second leaf type."""


class Node:
    """A many node over one leaf and one plain default."""

    def __init__(self, leaf: Leaf, limit: int = 3) -> None:
        """Store the leaf and the limit."""
        self.leaf = leaf
        self.limit = limit


class Shared:
    """Shared across two consumers; owns one leaf."""

    def __init__(self, leaf: Leaf) -> None:
        """Store the leaf."""
        self.leaf = leaf


class Left:
    """First consumer of the shared object."""

    def __init__(self, shared: Shared) -> None:
        """Store the shared object."""
        self.shared = shared


class Right:
    """Second consumer of the shared object."""

    def __init__(self, shared: Shared, other: Other) -> None:
        """Store the shared object and another leaf."""
        self.shared = shared
        self.other = other


class DiamondRoot:
    """Root over two consumers of one shared object, plus a keyword-only plain parameter."""

    def __init__(self, left: Left, right: Right, *, label: str = "root") -> None:
        """Store both consumers and the label."""
        self.left = left
        self.right = right
        self.label = label


class TreeRoot:
    """Root over two many nodes (a tree of many sites)."""

    def __init__(self, first: Node, second: Node) -> None:
        """Store both nodes."""
        self.first = first
        self.second = second


class Missing:
    """A type nothing provides, so consumers get an UNRESOLVED_INPUT socket."""


class UnresolvedRoot:
    """Root with one unresolved input beside a normal dependency."""

    def __init__(self, leaf: Leaf, work: Missing) -> None:
        """Store both inputs."""
        self.leaf = leaf
        self.work = work


class IMember:
    """Frame type for collection members."""


class MemberA(IMember):
    """First collection member."""

    def __init__(self, leaf: Leaf) -> None:
        """Store the leaf."""
        self.leaf = leaf


class MemberB(IMember):
    """Second collection member."""

    def __init__(self, leaf: Leaf) -> None:
        """Store the leaf."""
        self.leaf = leaf


class CollectionRoot:
    """Root over a collection of members."""

    def __init__(self, members: list[IMember]) -> None:
        """Store the members."""
        self.members = members


@pytest.fixture
def book() -> Iterator[Spellbook]:
    """Own one isolated world with disk caching disabled."""
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether
    spellbook = Spellbook(aetheric_frame="override-key-oracle")
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


def _conjured_root(
        spellbook: Spellbook,
        bindings: List[Tuple[Any, Existence, Dict[str, Any]]],
        root: Any,
        override: Optional[Dict[str, Any]] = None,
) -> Spell:
    """Bind, conjure, meld the root once (with `override` when it has unresolved inputs) and return it."""
    ids = {
        spell: spellbook.bind(spell=spell, existence=existence, permissions="create", **extra)
        for spell, existence, extra in bindings
    }
    conduit = spellbook.conjure()
    conduit.meld(root, override=override)
    selected = spellbook.find_spell_by_id(ids[root])
    assert selected is not None
    return selected


def _today(targeting: SpellOverrideTargetingCodegenCreation, key: str) -> Outcome:
    """Resolve one key with today's targeting artifact."""
    try:
        matches, _, _ = targeting._resolve_targets_for_raw_key(key)
    except (RuntimeError, ValueError) as error:
        return ("error", type(error).__name__, str(error))
    return ("ok", Counter((match.node_id, match.param_name) for match in matches))


def _resolver(spell: Spell, key: str) -> Outcome:
    """Resolve one key with the site-graph resolver, weighting UNIQUE/BROADCAST by logical path counts."""
    graph = spell._compiler_artifact._spell_codegen_model.site_graph_shape
    try:
        resolution = OverrideKeyResolver.resolve(graph, (key,))
    except (RuntimeError, ValueError) as error:
        return ("error", type(error).__name__, str(error))
    is_path = TargetSpec.parse(key).kind is TargetSpecKind.PATH
    counted: Counter = Counter()
    for site, name in resolution.targets_by_key[key]:
        counted[(graph.sites[site].spell_id, name)] += 1 if is_path else graph.path_counts[site]
    return ("ok", counted)


def _compare(spell: Spell, extra_keys: Tuple[str, ...] = ()) -> Dict[str, Tuple[Outcome, Outcome]]:
    """Run both implementations over today's indexed keys plus extra keys; return disagreements."""
    model = spell._compiler_artifact._spell_codegen_model
    analysis = model.override_targeting_shape
    targeting = SpellOverrideTargetingCodegenCreation.from_analysis(
        root_spell_id=spell.spell_id,
        targets_by_spec=analysis.targets_by_spec,
        specificity_by_spec=analysis.specificity_by_spec,
    )
    try:
        keys = sorted(set(analysis.targets_by_spec) | set(extra_keys))
        assert keys, "today's targeting indexed no keys"
        disagreements: Dict[str, Tuple[Outcome, Outcome]] = {}
        for key in keys:
            today, resolver = _today(targeting, key), _resolver(spell, key)
            if today != resolver:
                disagreements[key] = (today, resolver)
        return disagreements
    finally:
        targeting.cleanup()


def _invalid_keys(*extra: str) -> Tuple[str, ...]:
    """Keys both implementations must reject the same way, plus test-specific extras."""
    return ("nosuch", "*nosuch", "**nosuch", "**", "leaf>nosuch") + extra


def test_oracle_many_tree_with_plain_defaults(book: Spellbook) -> None:
    """A tree of many sites with plain defaults: every indexed key agrees."""
    spell = _conjured_root(
        book,
        [(Leaf, Existence.many, {}), (Node, Existence.many, {}), (TreeRoot, Existence.many, {})],
        TreeRoot,
    )

    assert _compare(spell, _invalid_keys("first>limit>x", "first>nosuch")) == {}


def test_oracle_shared_diamond_counts_logical_sockets(book: Spellbook) -> None:
    """A shared site reached by two paths: UNIQUE counts and exact aliases agree."""
    spell = _conjured_root(
        book,
        [
            (Leaf, Existence.many, {}),
            (Other, Existence.many, {}),
            (Shared, Existence.unique_per_conduit, {}),
            (Left, Existence.many, {}),
            (Right, Existence.many, {}),
            (DiamondRoot, Existence.many, {}),
        ],
        DiamondRoot,
    )

    assert _compare(spell, _invalid_keys("*leaf", "*shared", "*other", "*label")) == {}


def test_oracle_unresolved_input_is_a_target(book: Spellbook) -> None:
    """An UNRESOLVED_INPUT parameter is indexed and resolved the same way."""
    spell = _conjured_root(
        book,
        [(Leaf, Existence.many, {}), (UnresolvedRoot, Existence.many, {})],
        UnresolvedRoot,
        override={"work": Missing()},
    )

    assert _compare(spell, _invalid_keys("*work", "**work")) == {}


def test_oracle_collection_records_the_last_member_difference(book: Spellbook) -> None:
    """Through a collection, today keeps one member per path and the resolver keeps every member."""
    spell = _conjured_root(
        book,
        [
            (Leaf, Existence.many, {}),
            (MemberA, Existence.many, {"spellframe": IMember, "binding_name": "a"}),
            (MemberB, Existence.many, {"spellframe": IMember, "binding_name": "b"}),
            (CollectionRoot, Existence.many, {}),
        ],
        CollectionRoot,
    )

    disagreements = _compare(spell, _invalid_keys("*leaf", "**leaf"))

    assert set(disagreements) == {"members>leaf"}
    today, resolver = disagreements["members>leaf"]
    assert today[0] == "ok" and sum(today[1].values()) == 1
    assert resolver[0] == "ok" and sum(resolver[1].values()) == 2
