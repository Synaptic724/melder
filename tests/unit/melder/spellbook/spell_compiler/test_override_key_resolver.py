"""Unit contracts for override key resolution over a site graph (override design S1)."""

from typing import Dict, Optional, Tuple

import pytest

from melder.aether.spellbook.spell_compiler.artifact_processor.data.spell_site_graph_analysis import (
    SpellSite,
    SpellSiteGraphAnalysis,
    SpellSiteParam,
)
from melder.aether.spellbook.spell_compiler.codegen_creation_system.shared_assets.override_key_resolver import (
    OverrideKeyResolver,
)

Row = Tuple[str, str, Tuple[int, ...]]


def _graph(
        sites: Tuple[Tuple[str, bool, Tuple[Tuple[str, str, Tuple[int, ...]], ...]], ...],
        path_counts: Tuple[int, ...],
) -> SpellSiteGraphAnalysis:
    """Build a section from (spell id, shared, ((name, kind, dependency sites), ...)) rows."""
    built = []
    for index, (spell_id, shared, params) in enumerate(sites):
        rows = tuple(
            SpellSiteParam(
                name=name,
                position=position,
                parameter_kind=kind,
                socket_kind_value=1,
                is_collection=len(dependencies) > 1,
                is_optional=not dependencies,
                source_kind="dependency" if dependencies else "plain",
                contract_key=None,
                dependency_sites=dependencies,
            )
            for position, (name, kind, dependencies) in enumerate(params)
        )
        instance_key: Tuple[str, Optional[int]] = (spell_id, None if shared else index)
        built.append(SpellSite(index=index, instance_key=instance_key, spell_id=spell_id, shared=shared, params=rows))
    return SpellSiteGraphAnalysis(sites=tuple(built), path_counts=path_counts)


def _shallow() -> SpellSiteGraphAnalysis:
    """Root(a: A, /, b: B, n=3, *, k=1); A(x: X); X(); B()."""
    return _graph(
        (
            ("root", False, (
                ("a", "POSITIONAL_ONLY", (1,)),
                ("b", "POSITIONAL_OR_KEYWORD", (3,)),
                ("n", "POSITIONAL_OR_KEYWORD", ()),
                ("k", "KEYWORD_ONLY", ()),
            )),
            ("A", False, (("x", "POSITIONAL_OR_KEYWORD", (2,)),)),
            ("X", False, ()),
            ("B", False, ()),
        ),
        (1, 1, 1, 1),
    )


def _shared_diamond() -> SpellSiteGraphAnalysis:
    """Root(l: L, r: R); L(s: S); R(s: S); S shared (x: X); X many under S."""
    return _graph(
        (
            ("root", False, (("l", "POSITIONAL_OR_KEYWORD", (1,)), ("r", "POSITIONAL_OR_KEYWORD", (2,)))),
            ("L", False, (("s", "POSITIONAL_OR_KEYWORD", (3,)),)),
            ("R", False, (("s", "POSITIONAL_OR_KEYWORD", (3,)),)),
            ("S", True, (("x", "POSITIONAL_OR_KEYWORD", (4,)),)),
            ("X", False, ()),
        ),
        (1, 1, 1, 2, 2),
    )


def _winners(graph: SpellSiteGraphAnalysis, *keys: str, arity: int = 0) -> Dict[Tuple[str, str], str]:
    """Resolve and name winners by (spell id, parameter) for readable assertions."""
    resolution = OverrideKeyResolver.resolve(graph, keys, arity)
    return {(graph.sites[site].spell_id, name): key for (site, name), key in resolution.winners.items()}


def test_root_key_supplies_the_root_parameter() -> None:
    """A bare key is a PATH of one segment: the root's own parameter."""
    assert _winners(_shallow(), "a") == {("root", "a"): "a"}


def test_nested_path_walks_named_edges() -> None:
    """`a>x` is parameter x of the site that supplies root parameter a."""
    assert _winners(_shallow(), "a>x") == {("A", "x"): "a>x"}


@pytest.mark.parametrize("key", ["nosuch", "a>nosuch", "n>z"])
def test_unknown_or_non_dependency_path_raises_todays_error(key: str) -> None:
    """An unknown segment, or a walk through a plain parameter, matches nothing."""
    with pytest.raises(RuntimeError, match=f"No sockets found for override path '{key}'."):
        OverrideKeyResolver.resolve(_shallow(), (key,))


def test_unique_key_counts_logical_paths() -> None:
    """UNIQUE succeeds for one socket and reports today's count for a shared site."""
    assert _winners(_shallow(), "*x") == {("A", "x"): "*x"}
    with pytest.raises(RuntimeError, match=r"Unique override '\*x' matched 2 sockets; expected exactly one."):
        OverrideKeyResolver.resolve(_shared_diamond(), ("*x",))
    with pytest.raises(RuntimeError, match=r"Unique override '\*s' matched 2 sockets; expected exactly one."):
        OverrideKeyResolver.resolve(_shared_diamond(), ("*s",))
    with pytest.raises(RuntimeError, match=r"No sockets found for unique override '\*nosuch'."):
        OverrideKeyResolver.resolve(_shallow(), ("*nosuch",))


def test_broadcast_key_targets_every_parameter_with_that_name() -> None:
    """BROADCAST reaches every site that has the parameter, once per site."""
    assert _winners(_shared_diamond(), "**s") == {("L", "s"): "**s", ("R", "s"): "**s"}
    with pytest.raises(RuntimeError, match=r"No sockets found for broadcast override '\*\*nosuch'."):
        OverrideKeyResolver.resolve(_shallow(), ("**nosuch",))


def test_malformed_key_raises_value_error() -> None:
    """Parsing errors keep TargetSpec's ValueError."""
    with pytest.raises(ValueError):
        OverrideKeyResolver.resolve(_shallow(), ("**",))


def test_rank_order_is_path_then_unique_then_broadcast() -> None:
    """The most specific key wins on a shared target."""
    assert _winners(_shallow(), "**x", "a>x") == {("A", "x"): "a>x"}
    assert _winners(_shallow(), "**x", "*x") == {("A", "x"): "*x"}


def test_rule_below_a_supplied_parameter_is_inactive() -> None:
    """P1: supplying l makes l>s>x inactive, so the shared S built for r keeps its default x."""
    graph = _shared_diamond()
    resolution = OverrideKeyResolver.resolve(graph, ("l", "l>s>x"))

    assert {(graph.sites[site].spell_id, name) for site, name in resolution.winners} == {("root", "l")}
    assert resolution.inactive_keys == ("l>s>x",)
    assert resolution.targets_by_key["l>s>x"] == ((3, "x"),)


def test_rule_through_an_alias_applies_to_the_shared_site() -> None:
    """P3: with nothing cut, a rule through either alias targets the one shared site."""
    assert _winners(_shared_diamond(), "l>s>x") == {("S", "x"): "l>s>x"}
    assert _winners(_shared_diamond(), "r>s>x") == {("S", "x"): "r>s>x"}


def test_keys_under_a_cut_are_still_validated() -> None:
    """An inactive key with a bad segment still raises (contract item 3)."""
    with pytest.raises(RuntimeError, match="No sockets found for override path 'a>nosuch'."):
        OverrideKeyResolver.resolve(_shallow(), ("a", "a>nosuch"))


def test_equal_rank_keys_on_one_parameter_are_reported_as_conflicts() -> None:
    """Two spellings of one path collide at equal rank; the first key wins."""
    resolution = OverrideKeyResolver.resolve(_shallow(), ("a", " a"))

    assert resolution.winners == {(0, "a"): "a"}
    assert resolution.conflicts == ((0, "a", "a", " a"),)


def test_positional_values_fill_positional_parameters_first() -> None:
    """`__args__` of length N supplies the first N positional parameters and outranks PATH keys."""
    resolution = OverrideKeyResolver.resolve(_shallow(), ("__args__", "a"), 2)

    assert resolution.positional == {"a": 0, "b": 1}
    assert resolution.winners == {(0, "a"): "__args__", (0, "b"): "__args__"}
    wide = OverrideKeyResolver.resolve(_shallow(), ("__args__",), 9)
    assert wide.positional == {"a": 0, "b": 1, "n": 2}
    assert (0, "k") not in wide.winners


def test_collection_path_reaches_every_member() -> None:
    """A PATH through a collection parameter fans out to each member site."""
    graph = _graph(
        (
            ("root", False, (("items", "POSITIONAL_OR_KEYWORD", (1, 2)),)),
            ("M1", False, (("v", "POSITIONAL_OR_KEYWORD", ()),)),
            ("M2", False, (("v", "POSITIONAL_OR_KEYWORD", ()),)),
        ),
        (1, 1, 1),
    )

    assert _winners(graph, "items>v") == {("M1", "v"): "items>v", ("M2", "v"): "items>v"}


def test_resolution_is_pure() -> None:
    """The same inputs resolve to equal results."""
    graph = _shared_diamond()
    first = OverrideKeyResolver.resolve(graph, ("l", "**x", "r>s"))
    second = OverrideKeyResolver.resolve(graph, ("l", "**x", "r>s"))

    assert first.winners == second.winners
    assert first.targets_by_key == second.targets_by_key
    assert first.inactive_keys == second.inactive_keys
