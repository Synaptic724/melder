"""Design v2 prototype: site graph, per-key-set plans and one lowering (artifact-only, E1).

Purpose:
    Measure design_v2.md before any production change. Builds a site graph from a live, conjured root
    spell's Phase-9 model and Phase-10 steps, compiles one plan per override key set, and installs the
    plans into that spell's CreationContext slots at run time. No Melder source file is edited.

Contract:
    - Supported sites: `many` and `unique_per_conduit`; the root must be `many`. Unsupported shapes
      (collections, contract payloads, other shared existences, *args/**kwargs constructors, a shared
      site demanded from two different miss contexts) raise NotImplementedError at graph/plan build.
    - Keys: PATH (`a`, `a>b`), UNIQUE (`*n`), BROADCAST (`**n`) and root `__args__`, with today's error
      texts for unknown keys and UNIQUE counts. Rank ARGS > PATH > UNIQUE > BROADCAST.
    - Semantics: P1 static cuts, P2 error on a stored shared site with a winning override, P3 operands
      fixed per key set, E1 conflict guard (identity, then == for plain scalars).
    - Supplied values are never inspected.

Threading:
    Plans take the existing slot guard (an RLock) of a shared site across recheck, children,
    construction and publication; hits are lock-free dict reads. The plan dict is written on first use
    of a key set only; concurrent first compiles of one key set converge on equivalent plans.
"""
import annotationlib
import inspect
from collections import defaultdict
from typing import Any, Callable, Dict, List, Optional, Set, Tuple

from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.generalized.compilers.generalized_no_overrides_codegen_creation_compiler import (
    _raise_meld_construction_error,
)
from melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.generalized.compilers.generalized_overrides_codegen_creation_compiler import (
    _raise_override_on_existing_instance,
)
from melder.aether.spellbook.spell_compiler.dag.target_spec import TargetSpec, TargetSpecKind
from melder.utilities.custom_exceptions.meld_execution_error import MeldExecutionError
from melder.utilities.custom_exceptions.unresolved_input_error import UnresolvedInputError

SiteKey = Tuple[str, Optional[int]]
Target = Tuple[SiteKey, str]

POSITIONAL_KINDS = (inspect.Parameter.POSITIONAL_ONLY, inspect.Parameter.POSITIONAL_OR_KEYWORD)
RANK_BROADCAST, RANK_UNIQUE, RANK_PATH, RANK_ARGS = 1, 2, 3, 4
TOP = "T"


class Param:
    """One constructor parameter of a site and its default operand source."""

    __slots__ = ("name", "position", "kind", "deps", "has_default", "required_input")

    def __init__(self, name: str, position: int, kind: Any, deps: Tuple[SiteKey, ...],
                 has_default: bool, required_input: bool) -> None:
        self.name = name
        self.position = position
        self.kind = kind
        self.deps = deps
        self.has_default = has_default
        self.required_input = required_input


class Site:
    """One physical construction site: an instance key, its spell and its parameter table."""

    __slots__ = ("key", "index", "spell", "store_key", "shared", "params", "by_name")

    def __init__(self, key: SiteKey, index: int, spell: Any, shared: bool, params: List[Param]) -> None:
        self.key = key
        self.index = index
        self.spell = spell
        self.store_key = spell.spell_index.selected_spell_id
        self.shared = shared
        self.params = params
        self.by_name = {param.name: param for param in params}


class SiteGraph:
    """Compact site graph for one root: sites, a parameter-name index and DP path counts."""

    def __init__(self, root_spell: Any) -> None:
        artifact = root_spell._compiler_artifact
        model = artifact._spell_codegen_model
        steps = artifact._spell_codegen_plan.no_overrides_plan.steps
        injection = model.injection_shape
        self.root_spell = root_spell
        self.root_key: SiteKey = tuple(model.instance_shape.root_instance_key)
        self.sites: Dict[SiteKey, Site] = {}
        for index, step in enumerate(steps):
            key: SiteKey = tuple(step.instance_key)
            spell = step.spell
            shared = key[1] is None
            if shared and spell.existence is not Existence.unique_per_conduit:
                raise NotImplementedError(f"shared existence {spell.existence} not in the prototype")
            if not shared and spell.existence is not Existence.many:
                raise NotImplementedError(f"existence {spell.existence} not in the prototype")
            spec = injection.instance_specs_by_instance_key[key]
            if spec.contract_payload:
                raise NotImplementedError("contract payloads are not in the prototype")
            self.sites[key] = Site(key, index, spell, shared, self._params(spell, spec))
        if self.sites[self.root_key].shared:
            raise NotImplementedError("the prototype requires a many root")
        self.order = self._topological()
        self.path_count = self._path_counts()
        self.name_index: Dict[str, List[Target]] = defaultdict(list)
        for key in self.order:
            for param in self.sites[key].params:
                self.name_index[param.name].append((key, param.name))

    @staticmethod
    def _params(spell: Any, spec: Any) -> List[Param]:
        signature = inspect.signature(spell.spell, annotation_format=annotationlib.Format.FORWARDREF)
        params: List[Param] = []
        for position, (name, parameter) in enumerate(signature.parameters.items()):
            if parameter.kind in (inspect.Parameter.VAR_POSITIONAL, inspect.Parameter.VAR_KEYWORD):
                raise NotImplementedError("*args/**kwargs constructors are not in the prototype")
            source = spec.param_sources.get(name)
            deps: Tuple[SiteKey, ...] = ()
            required_input = False
            if source is not None:
                if source.kind == "dependency":
                    if source.is_collection or len(source.dependency_keys) != 1:
                        raise NotImplementedError("collection parameters are not in the prototype")
                    deps = tuple(tuple(dep) for dep in source.dependency_keys)
                elif source.kind in ("unresolved_input", "override_required"):
                    required_input = True
                else:
                    raise NotImplementedError(f"param source {source.kind} not in the prototype")
            has_default = parameter.default is not inspect.Parameter.empty
            if not deps and not required_input and not has_default:
                raise NotImplementedError(f"parameter {name} has no operand source")
            params.append(Param(name, position, parameter.kind, deps, has_default, required_input))
        return params

    def _topological(self) -> List[SiteKey]:
        """Return reachable sites parents-first (reverse DFS post-order from the root)."""
        order: List[SiteKey] = []
        seen: Set[SiteKey] = set()

        def visit(key: SiteKey) -> None:
            if key in seen:
                return
            seen.add(key)
            for param in self.sites[key].params:
                for dep in param.deps:
                    visit(dep)
            order.append(key)

        visit(self.root_key)
        order.reverse()
        return order

    def _path_counts(self) -> Dict[SiteKey, int]:
        """Count logical root paths to every site in one pass (what UNIQUE counts today)."""
        counts: Dict[SiteKey, int] = {key: 0 for key in self.order}
        counts[self.root_key] = 1
        for key in self.order:
            for param in self.sites[key].params:
                for dep in param.deps:
                    counts[dep] += counts[key]
        return counts


class Resolution:
    """Winning operand per (site, param) for one key set, plus equal-rank conflicts."""

    __slots__ = ("winners", "conflicts", "positional")

    def __init__(self) -> None:
        self.winners: Dict[Target, str] = {}
        self.conflicts: List[Tuple[Target, str, str]] = []
        self.positional: Dict[str, int] = {}


class PlanCompiler:
    """Compile key-set plans over one SiteGraph and emit them as straight-line Python."""

    def __init__(self, graph: SiteGraph) -> None:
        self.graph = graph
        self.sources: Dict[Tuple[Tuple[str, ...], int], str] = {}

    # ---- key resolution -------------------------------------------------------------------------
    def _walk(self, segments: Tuple[str, ...], raw: str) -> List[Tuple[Target, Tuple[Target, ...]]]:
        """Resolve one PATH by walking named edges from the root; no path enumeration."""
        finals: List[Tuple[Target, Tuple[Target, ...]]] = []

        def step(key: SiteKey, index: int, prefixes: Tuple[Target, ...]) -> None:
            site = self.graph.sites[key]
            param = site.by_name.get(segments[index])
            if param is None:
                raise RuntimeError(f"No sockets found for override path '{'>'.join(segments)}'.")
            target = (key, param.name)
            if index == len(segments) - 1:
                finals.append((target, prefixes))
                return
            if not param.deps:
                raise RuntimeError(f"No sockets found for override path '{'>'.join(segments)}'.")
            for dep in param.deps:
                step(dep, index + 1, prefixes + (target,))

        step(self.graph.root_key, 0, ())
        return finals

    def resolve(self, keys: Tuple[str, ...], arity: int) -> Resolution:
        candidates: List[Tuple[int, str, Target, Tuple[Target, ...]]] = []
        for raw in keys:
            if raw == "__args__":
                continue
            spec = TargetSpec.parse(raw)
            if spec.kind is TargetSpecKind.PATH:
                for target, prefixes in self._walk(spec.path, raw):
                    candidates.append((RANK_PATH, raw, target, prefixes))
                continue
            matches = self.graph.name_index.get(spec.param_name, [])
            if spec.kind is TargetSpecKind.UNIQUE:
                count = sum(self.graph.path_count[key] for key, _ in matches)
                if count == 0:
                    raise RuntimeError(f"No sockets found for unique override '*{spec.param_name}'.")
                if count > 1:
                    raise RuntimeError(
                        f"Unique override '*{spec.param_name}' matched {count} sockets; expected exactly one."
                    )
                rank = RANK_UNIQUE
            else:
                if not matches:
                    raise RuntimeError(f"No sockets found for broadcast override '**{spec.param_name}'.")
                rank = RANK_BROADCAST
            for target in matches:
                candidates.append((rank, raw, target, ()))
        resolution = Resolution()
        if arity:
            root = self.graph.sites[self.graph.root_key]
            positional = [param for param in root.params if param.kind in POSITIONAL_KINDS]
            for index, param in enumerate(positional[:arity]):
                candidates.append((RANK_ARGS, "__args__", (root.key, param.name), ()))
                resolution.positional[param.name] = index
        # P1: a PATH rule whose walk crosses a targeted parameter is inactive. Fixpoint, top-down.
        active = candidates
        for _ in range(len(candidates) + 1):
            targeted = {target for _, _, target, _ in active}
            narrowed = [c for c in candidates if not any(prefix in targeted for prefix in c[3])]
            if len(narrowed) == len(active):
                break
            active = narrowed
        best: Dict[Target, Tuple[int, List[str]]] = {}
        for rank, raw, target, _ in active:
            current = best.get(target)
            if current is None or rank > current[0]:
                best[target] = (rank, [raw])
            elif rank == current[0] and raw not in current[1]:
                current[1].append(raw)
        for target, (_, raws) in best.items():
            resolution.winners[target] = raws[0]
            for other in raws[1:]:
                resolution.conflicts.append((target, raws[0], other))
        return resolution

    # ---- demand and contexts --------------------------------------------------------------------
    def _contexts(self, resolution: Resolution) -> Tuple[Dict[SiteKey, Any], Dict[SiteKey, Set[Any]]]:
        demand: Dict[SiteKey, Set[Any]] = defaultdict(set)
        expanded: Set[SiteKey] = set()

        def visit(key: SiteKey, context: Any) -> None:
            demand[key].add(context)
            if key in expanded:
                return
            expanded.add(key)
            site = self.graph.sites[key]
            child_context = key if site.shared else context
            for param in site.params:
                if (key, param.name) in resolution.winners:
                    continue
                for dep in param.deps:
                    visit(dep, child_context)

        visit(self.graph.root_key, TOP)
        evaluation: Dict[SiteKey, Any] = {}
        for key, contexts in demand.items():
            if TOP in contexts:
                evaluation[key] = TOP
            elif len(contexts) == 1:
                evaluation[key] = next(iter(contexts))
            else:
                raise NotImplementedError("a site demanded from two miss contexts needs a per-call cell")
        return evaluation, demand

    # ---- emission -------------------------------------------------------------------------------
    def compile(self, keys: Tuple[str, ...], arity: int) -> Callable[..., Any]:
        """Return `plan(meld)` for the empty key set, else `plan(meld, ov)`."""
        resolution = self.resolve(keys, arity)
        source = self._emit(keys, arity, resolution)
        self.sources[(keys, arity)] = source
        namespace = self._namespace()
        exec(compile(source, "<melder_v2_prototype_plan>", "exec"), namespace)
        return namespace["_plan"]

    def _namespace(self) -> Dict[str, Any]:
        namespace: Dict[str, Any] = {
            "_raise_meld_construction_error": _raise_meld_construction_error,
            "_raise_override_on_existing_instance": _raise_override_on_existing_instance,
            "_unresolved": _unresolved_error,
            "_conflict": _conflict_guard,
            "root_spell_id": self.graph.root_spell.spell_index.selected_spell_id,
        }
        for site in self.graph.sites.values():
            namespace[f"t{site.index}"] = site.spell.spell
            namespace[f"spell{site.index}"] = site.spell
            namespace[f"sid{site.index}"] = site.store_key
        return namespace

    def _emit(self, keys: Tuple[str, ...], arity: int, resolution: Resolution) -> str:
        evaluation, demand = self._contexts(resolution)
        sites = self.graph.sites
        needs_cache: Dict[Any, Set[SiteKey]] = {}

        def needs(context: Any) -> Set[SiteKey]:
            """Sites a miss context (or one nested in it) uses but does not evaluate itself."""
            if context in needs_cache:
                return needs_cache[context]
            result: Set[SiteKey] = set()
            for key, contexts in demand.items():
                if context in contexts and evaluation[key] != context:
                    result.add(key)
            for key, where in evaluation.items():
                if where == context and sites[key].shared:
                    result |= {k for k in needs(key) if evaluation[k] != context}
            needs_cache[context] = result
            return result

        functions: List[List[str]] = []
        has_ov = bool(keys)

        def operand(site: Site, param: Param) -> Optional[str]:
            winner = resolution.winners.get((site.key, param.name))
            if winner == "__args__":
                return f"args[{resolution.positional[param.name]}]"
            if winner is not None:
                return f"ov[{winner!r}]"
            if param.deps:
                return f"v{sites[param.deps[0]].index}"
            return None

        def call_line(site: Site, indent: str) -> List[str]:
            positional: List[str] = []
            keyword: List[str] = []
            switched = False
            for param in site.params:
                expression = operand(site, param)
                if expression is None:
                    switched = True
                    continue
                if not switched and param.kind in POSITIONAL_KINDS:
                    positional.append(expression)
                elif param.kind is inspect.Parameter.POSITIONAL_ONLY:
                    raise NotImplementedError("positional-only parameter after an omitted one")
                else:
                    keyword.append(f"{param.name}={expression}")
            arguments = ", ".join(positional + keyword)
            i = site.index
            return [
                f"{indent}try:",
                f"{indent}    v{i} = t{i}({arguments})",
                f"{indent}except Exception as exc:",
                f"{indent}    _raise_meld_construction_error(spell{i}, exc)",
            ]

        def missing_inputs(site: Site) -> List[str]:
            return [
                param.name for param in site.params
                if param.required_input and (site.key, param.name) not in resolution.winners
            ]

        def raise_line(site: Site, indent: str) -> str:
            supplied = tuple(
                param.name for param in site.params
                if (site.key, param.name) in resolution.winners or param.deps
            )
            return f"{indent}raise _unresolved(spell{site.index}, {supplied!r})"

        def p2(site: Site) -> bool:
            return any((site.key, param.name) in resolution.winners for param in site.params)

        def body(context: Any, indent: str, available: Set[SiteKey], lines: List[str]) -> Callable[[SiteKey], None]:
            def ensure(key: SiteKey) -> None:
                if key in available:
                    return
                site = sites[key]
                if evaluation[key] != context:
                    raise AssertionError(f"site {key} should arrive as an argument")
                if site.shared:
                    for free in sorted(needs(key), key=lambda k: sites[k].index):
                        if evaluation[free] == context:
                            ensure(free)
                    emit_miss(site)
                    i = site.index
                    free_args = "".join(f", v{sites[k].index}" for k in sorted(needs(key), key=lambda k: sites[k].index))
                    lines.append(f"{indent}v{i} = cs._creations.get(sid{i})")
                    if p2(site):
                        lines.append(f"{indent}if v{i} is not None:")
                        lines.append(f"{indent}    _raise_override_on_existing_instance(spell=spell{i}, "
                                     f"has_targeted_overrides=True, any_overrides_present=True, "
                                     f"root_spell_id=root_spell_id)")
                    lines.append(f"{indent}if v{i} is None:")
                    lines.append(f"{indent}    v{i} = _miss{i}(meld, cs, ov{', args' if arity else ''}{free_args})")
                else:
                    if missing_inputs(site):
                        lines.append(raise_line(site, indent))
                    for param in site.params:
                        if (site.key, param.name) not in resolution.winners and param.deps:
                            ensure(param.deps[0])
                    lines.extend(call_line(site, indent))
                available.add(key)
            return ensure

        emitted_misses: Set[SiteKey] = set()

        def emit_miss(site: Site) -> None:
            if site.key in emitted_misses:
                return
            emitted_misses.add(site.key)
            i = site.index
            free = sorted(needs(site.key), key=lambda k: sites[k].index)
            params = "".join(f", v{sites[k].index}" for k in free)
            lines = [f"def _miss{i}(meld, cs, ov{', args' if arity else ''}{params}):",
                     f"    with (cs._slot_guards.get(sid{i}) or cs.slot_guard(sid{i})):",
                     f"        v{i} = cs._creations.get(sid{i})",
                     f"        if v{i} is None:"]
            inner: List[str] = []
            if missing_inputs(site):
                inner.append(raise_line(site, "            "))
            ensure = body(site.key, "            ", set(free), inner)
            for param in site.params:
                if (site.key, param.name) not in resolution.winners and param.deps:
                    ensure(param.deps[0])
            inner.extend(call_line(site, "            "))
            inner.append(f"            cs._creations[sid{i}] = v{i}")
            lines.extend(inner)
            if p2(site):
                lines.append("        else:")
                lines.append(f"            _raise_override_on_existing_instance(spell=spell{i}, "
                             f"has_targeted_overrides=True, any_overrides_present=True, "
                             f"root_spell_id=root_spell_id)")
            lines.append(f"    return v{i}")
            functions.append(lines)

        top: List[str] = []
        head = "def _plan(meld, ov):" if has_ov else "def _plan(meld):"
        prologue: List[str] = [] if has_ov else ["    ov = None"]
        if arity:
            prologue.append('    args = ov["__args__"]')
        for target, first, other in resolution.conflicts:
            prologue.append(f"    _conflict(ov[{first!r}], ov[{other!r}], {repr(target[1])})")
        # Statically known unresolved inputs on unconditionally demanded sites: raise before building.
        for key in self.graph.order:
            if evaluation.get(key) == TOP and not sites[key].shared and missing_inputs(sites[key]):
                prologue.append(raise_line(sites[key], "    "))
        if any(sites[key].shared for key, where in evaluation.items() if where == TOP):
            prologue.append("    cs = meld._conduit_creations")
        ensure_top = body(TOP, "    ", set(), top)
        ensure_top(self.graph.root_key)
        root_index = sites[self.graph.root_key].index
        lines_all: List[str] = []
        for function in functions:
            lines_all.extend(function)
            lines_all.append("")
        lines_all.append(head)
        lines_all.extend(prologue)
        lines_all.extend(top)
        lines_all.append(f"    return v{root_index}")
        return "\n".join(lines_all) + "\n"


def _unresolved_error(spell: Any, supplied: Tuple[str, ...]) -> BaseException:
    """Build today's UnresolvedInputError text before any construction (no TypeError parsing)."""
    error = UnresolvedInputError.from_failed_construction(
        spell, TypeError("unresolved input not supplied"), supplied_names=supplied,
    )
    if error is not None:
        return error
    return MeldExecutionError(spell_id=spell.spell_id, spell_name=spell.spell_name,
                              message="A required input was not supplied.")


_PLAIN_SCALARS = (int, float, str, bool, bytes, type(None))


def _conflict_guard(first: Any, second: Any, where: str) -> None:
    """E1: identity first; `==` only for plain scalars of one type; otherwise refuse."""
    if first is second:
        return
    if type(first) is type(second) and type(first) in _PLAIN_SCALARS and first == second:
        return
    raise MeldExecutionError(spell_id=where, spell_name=where,
                             message=f"Conflicting overrides for '{where}' with the same specificity.")


class V2Runtime:
    """Per-root v2 runtime: the normal plan plus the key-set dispatcher for one root spell."""

    def __init__(self, root_spell: Any) -> None:
        self.graph = SiteGraph(root_spell)
        self.compiler = PlanCompiler(self.graph)
        self.normal = self.compiler.compile((), 0)
        self.plans: Dict[Tuple[str, ...], Callable[..., Any]] = {}
        self.dispatcher = self._build_dispatcher()

    def _compile_keys(self, keys: Tuple[str, ...]) -> Callable[..., Any]:
        try:
            if "__args__" not in keys:
                return self.compiler.compile(keys, 0)
            return self._arity_dispatch(keys)
        except NotImplementedError:
            raise
        except MeldExecutionError:
            raise
        except Exception as exc:
            spell = self.graph.root_spell
            raise MeldExecutionError(spell_id=spell.spell_index.selected_spell_id, spell_name=spell.spell_name,
                                     message="Failed to apply overrides.", inner=exc) from exc

    def _arity_dispatch(self, keys: Tuple[str, ...]) -> Callable[..., Any]:
        by_arity: Dict[int, Callable[..., Any]] = {}
        compiler = self.compiler

        def plan(meld: Any, ov: Dict[str, Any]) -> Any:
            arity = len(ov["__args__"])
            inner = by_arity.get(arity)
            if inner is None:
                inner = compiler.compile(keys, arity)
                by_arity[arity] = inner
            return inner(meld, ov)

        return plan

    def _build_dispatcher(self) -> Callable[..., Any]:
        plans = self.plans
        plans_get = plans.get
        compile_keys = self._compile_keys

        def execute_with_overrides(meld: Any, ov: Dict[str, Any]) -> Tuple[Any, bool]:
            keys = tuple(ov)
            plan = plans_get(keys)
            if plan is None:
                plan = compile_keys(keys)
                plans[keys] = plan
            return plan(meld, ov), True

        return execute_with_overrides


class SlotSwitch:
    """Swap one spell's CreationContext executor slots between today's executors and v2 (no source edits)."""

    def __init__(self, spell: Any, runtime: V2Runtime) -> None:
        context = spell._creation_context
        self.context = context
        normal = runtime.normal
        self.current = (context._no_overrides_executor, context._no_overrides_instance_executor,
                        context._overrides_executor)
        self.v2 = ((lambda meld: (normal(meld), True)), normal, runtime.dispatcher)

    def use(self, variant: str) -> None:
        slots = self.v2 if variant == "v2" else self.current
        context = self.context
        context._no_overrides_executor, context._no_overrides_instance_executor, context._overrides_executor = slots
