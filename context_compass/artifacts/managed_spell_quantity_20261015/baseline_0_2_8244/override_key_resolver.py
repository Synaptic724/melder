from typing import TYPE_CHECKING, ClassVar, Dict, List, Set, Tuple

from melder.aether.spellbook.spell_compiler.artifact_processor.data.spell_site_graph_analysis import (
    SiteTarget,
)
from melder.aether.spellbook.spell_compiler.dag.target_spec import TargetSpec, TargetSpecKind

if TYPE_CHECKING:
    from melder.aether.spellbook.spell_compiler.artifact_processor.data.spell_site_graph_analysis import (
        SpellSiteGraphAnalysis,
    )

ResolverCandidate = Tuple[int, str, SiteTarget, Tuple[SiteTarget, ...]]


class OverrideKeyResolution:
    """
    Result of resolving one override key tuple over one site graph.

    Purpose:
        Carry what a key set means for construction, decided once per key set:
        which key supplies each (site, parameter), which root parameters take
        positional values, which equal-rank keys collide and which keys are
        inactive because an ancestor parameter is supplied.

    Contract:
        - `targets_by_key[key]` lists every raw target of the key before cuts
          (a PATH key has one target per walk, several through collections).
        - `winners[(site, name)]` is the winning key; `"__args__"` marks a root
          positional value whose index is `positional[name]`.
        - `conflicts` holds (site, name, winning key, other key) for distinct
          keys that reach one parameter at the winning rank.
        - `inactive_keys` lists keys all of whose targets were cut (P1). They
          were still validated.
        - Value-typed containers only; no spell, store or supplied value is read.

    Registration:
        MELDER KERNEL - internal compiler value object.

    Subsystem Context:
        Output of `OverrideKeyResolver.resolve`.

    System Context:
        Override site-plan lowering (design step S1); consumed by key-set plan
        compilation from step S3.

    AGENT_ACCESS: internal

    AGENT_PURPOSE:
        access: internal. Winners, positional placements, conflicts, raw targets and
        inactive keys for one override key set.
    """

    __slots__ = [
        "targets_by_key",
        "winners",
        "positional",
        "conflicts",
        "inactive_keys",
    ]

    def __init__(
            self,
            *,
            targets_by_key: Dict[str, Tuple[SiteTarget, ...]],
            winners: Dict[SiteTarget, str],
            positional: Dict[str, int],
            conflicts: Tuple[Tuple[int, str, str, str], ...],
            inactive_keys: Tuple[str, ...],
    ) -> None:
        """
        Build one resolution.

        Args:
            targets_by_key:
                Raw targets per key, before cuts.
            winners:
                Winning key per (site index, parameter name).
            positional:
                Root parameter name -> index into the `__args__` payload.
            conflicts:
                (site index, parameter name, winning key, other key) rows.
            inactive_keys:
                Keys whose every target was cut.

        Returns:
            None.
        """
        self.targets_by_key = targets_by_key
        self.winners = winners
        self.positional = positional
        self.conflicts = conflicts
        self.inactive_keys = inactive_keys


class OverrideKeyResolver:
    """
    Resolve override keys over a site graph without enumerating logical paths.

    Purpose:
        Decide, once per key set, what an override payload's keys mean: today's
        key grammar (`a`, `a>b>c`, `*n`, `**n`) and error texts, the rank order
        PATH > UNIQUE > BROADCAST (root positional values rank above all), static
        cuts (a PATH rule below a supplied parameter is inactive) and equal-rank
        conflicts.

    Contract:
        - Pure: the result depends only on the site graph, the key tuple and the
          positional arity. No store, spell or supplied value is read.
        - PATH keys walk named parameters from the root, following every
          dependency site of each parameter (a collection fans out).
        - UNIQUE counts logical root paths through `path_counts`, so its error
          reports today's socket count.
        - Raises `RuntimeError` with today's messages for keys that match
          nothing; `TargetSpec.parse` raises `ValueError` for malformed keys.
          Errors are raised at the first invalid key in payload order.

    Registration:
        MELDER KERNEL - stateless helper; never user-instantiated or bound.

    Subsystem Context:
        Shared codegen-creation asset beside the family compilers; reads the
        Phase-9 `SpellSiteGraphAnalysis`.

    System Context:
        Override site-plan lowering (design step S1). Step S3 compiles one plan
        per key set from its result.

    AGENT_ACCESS: internal

    AGENT_PURPOSE:
        access: internal. Maps an override key tuple to winning (site, parameter)
        operands with P1 cuts and equal-rank conflicts, using today's grammar and errors.
    """

    __slots__ = ()

    RANK_BROADCAST: ClassVar[int] = 1
    RANK_UNIQUE: ClassVar[int] = 2
    RANK_PATH: ClassVar[int] = 3
    RANK_ARGS: ClassVar[int] = 4
    ARGS_KEY: ClassVar[str] = "__args__"
    POSITIONAL_KINDS: ClassVar[Tuple[str, ...]] = ("POSITIONAL_ONLY", "POSITIONAL_OR_KEYWORD")

    @classmethod
    def resolve(
            cls,
            site_graph: SpellSiteGraphAnalysis,
            keys: Tuple[str, ...],
            positional_arity: int = 0,
    ) -> OverrideKeyResolution:
        """
        Resolve one override key tuple.

        Contract:
            Follows code_description_patch_override_key_resolver steps 1-8:
            parse, resolve raw targets, add root positional targets, cut to a
            fixpoint, then pick winners by rank and record equal-rank conflicts.

        Args:
            site_graph:
                Phase-9 site-graph section of the root spell.
            keys:
                Payload keys in payload order; `"__args__"` is skipped (its
                length arrives as `positional_arity`).
            positional_arity:
                Number of root positional values supplied through `__args__`.

        Raises:
            RuntimeError:
                When a PATH, UNIQUE or BROADCAST key matches nothing, or a UNIQUE
                key matches more than one logical socket.
            ValueError:
                When `TargetSpec.parse` rejects a malformed key.

        Returns:
            OverrideKeyResolution:
                The resolution for this key set.
        """
        candidates: List[ResolverCandidate] = []
        targets_by_key: Dict[str, Tuple[SiteTarget, ...]] = {}
        for raw in keys:
            if raw == cls.ARGS_KEY:
                continue
            found = cls._candidates_for_key(site_graph, raw)
            targets_by_key[raw] = tuple(candidate[2] for candidate in found)
            candidates.extend(found)
        positional: Dict[str, int] = {}
        if positional_arity > 0:
            candidates.extend(cls._positional_candidates(site_graph, positional_arity, positional))
        active = cls._cut(candidates)
        winners, conflicts = cls._winners(active)
        active_keys = {candidate[1] for candidate in active}
        inactive_keys = tuple(
            raw for raw in targets_by_key
            if raw not in active_keys
        )
        return OverrideKeyResolution(
            targets_by_key=targets_by_key,
            winners=winners,
            positional=positional,
            conflicts=conflicts,
            inactive_keys=inactive_keys,
        )

    @classmethod
    def _candidates_for_key(
            cls,
            site_graph: SpellSiteGraphAnalysis,
            raw: str,
    ) -> List[ResolverCandidate]:
        """
        Parse one key and return its ranked raw targets (with walk prefixes for PATH).
        """
        spec = TargetSpec.parse(raw)
        if spec.kind is TargetSpecKind.PATH:
            return [
                (cls.RANK_PATH, raw, target, prefixes)
                for target, prefixes in cls._walk(site_graph, spec.path or ())
            ]
        name = spec.param_name or ""
        matches = site_graph.param_index.get(name, ())
        if spec.kind is TargetSpecKind.UNIQUE:
            count = sum(site_graph.path_counts[site] for site, _ in matches)
            if count == 0:
                raise RuntimeError(f"No sockets found for unique override '*{name}'.")
            if count > 1:
                raise RuntimeError(
                    f"Unique override '*{name}' matched {count} sockets; expected exactly one."
                )
            return [(cls.RANK_UNIQUE, raw, target, ()) for target in matches]
        if spec.kind is TargetSpecKind.BROADCAST:
            if not matches:
                raise RuntimeError(f"No sockets found for broadcast override '**{name}'.")
            return [(cls.RANK_BROADCAST, raw, target, ()) for target in matches]
        raise RuntimeError(f"Unsupported TargetSpecKind: {spec.kind!r}")

    @staticmethod
    def _walk(
            site_graph: SpellSiteGraphAnalysis,
            segments: Tuple[str, ...],
    ) -> List[Tuple[SiteTarget, Tuple[SiteTarget, ...]]]:
        """
        Walk one PATH from the root; return each final target with its prefixes.

        Raises:
            RuntimeError:
                When a segment names no parameter of the site reached, or a
                non-final segment names a parameter with no dependency site.
        """
        message = f"No sockets found for override path '{'>'.join(segments)}'."
        finals: List[Tuple[SiteTarget, Tuple[SiteTarget, ...]]] = []
        frontier: List[Tuple[int, Tuple[SiteTarget, ...]]] = [(site_graph.root_site_index, ())]
        last = len(segments) - 1
        for depth, segment in enumerate(segments):
            next_frontier: List[Tuple[int, Tuple[SiteTarget, ...]]] = []
            for site, prefixes in frontier:
                param = site_graph.param(site, segment)
                if param is None:
                    raise RuntimeError(message)
                target = (site, segment)
                if depth == last:
                    finals.append((target, prefixes))
                    continue
                if not param.dependency_sites:
                    raise RuntimeError(message)
                for dependency in param.dependency_sites:
                    next_frontier.append((dependency, prefixes + (target,)))
            frontier = next_frontier
        return finals

    @classmethod
    def _positional_candidates(
            cls,
            site_graph: SpellSiteGraphAnalysis,
            arity: int,
            positional: Dict[str, int],
    ) -> List[ResolverCandidate]:
        """
        Return ARGS-rank targets for the root's first `arity` positional parameters.

        Contract:
            Fills `positional` with parameter name -> payload index. Parameters
            beyond the root's positional-capable ones are left to the constructor.
        """
        root = site_graph.sites[site_graph.root_site_index]
        ordered = [
            param for param in root.params
            if param.parameter_kind in cls.POSITIONAL_KINDS
        ]
        found: List[ResolverCandidate] = []
        for index, param in enumerate(ordered[:arity]):
            positional[param.name] = index
            found.append((cls.RANK_ARGS, cls.ARGS_KEY, (root.index, param.name), ()))
        return found

    @staticmethod
    def _cut(candidates: List[ResolverCandidate]) -> List[ResolverCandidate]:
        """
        Drop every candidate whose walk crosses a targeted parameter (P1), to a fixpoint.
        """
        active = candidates
        for _ in range(len(candidates) + 1):
            targeted: Set[SiteTarget] = {candidate[2] for candidate in active}
            narrowed = [
                candidate for candidate in candidates
                if not any(prefix in targeted for prefix in candidate[3])
            ]
            if len(narrowed) == len(active):
                return narrowed
            active = narrowed
        return active

    @staticmethod
    def _winners(
            active: List[ResolverCandidate],
    ) -> Tuple[Dict[SiteTarget, str], Tuple[Tuple[int, str, str, str], ...]]:
        """
        Pick the highest-rank key per target; record distinct equal-rank keys as conflicts.
        """
        best: Dict[SiteTarget, Tuple[int, List[str]]] = {}
        for rank, raw, target, _ in active:
            current = best.get(target)
            if current is None or rank > current[0]:
                best[target] = (rank, [raw])
            elif rank == current[0] and raw not in current[1]:
                current[1].append(raw)
        winners: Dict[SiteTarget, str] = {}
        conflicts: List[Tuple[int, str, str, str]] = []
        for target, (_, raws) in best.items():
            winners[target] = raws[0]
            for other in raws[1:]:
                conflicts.append((target[0], target[1], raws[0], other))
        return winners, tuple(conflicts)
