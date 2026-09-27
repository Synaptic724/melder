"""S6: promote the override site-plan lane (patch override_site_plan_2026_09_26) into the canonical system docs.

Usage: python apply_s6_docs_edits.py <repo_root> [--check]

Anchored prose edits (each anchor must match exactly once), measured C1 ranges (every C1 `- path:` entry whose
file length changed is re-measured; entries for deleted files are removed), and a declared partial update of the
full package inventory (the lane's deleted modules out, its new modules in, purposes read from source by the
inventory's own rule). Nothing is written unless every edit applies. Indexes are regenerated separately.
"""

import ast
import datetime
import pathlib
import re
import sys

SC = "context_compass/system_docs/src_components.md"
SA = "context_compass/system_docs/src_architecture.md"
TC = "context_compass/system_docs/tests_components.md"
CCS = "src/melder/aether/spellbook/spell_compiler/codegen_creation_system/"
LOW = CCS + "shared_assets/site_plan_lowering.py"
RUN = CCS + "shared_assets/site_plan_override_runtime.py"
RES = CCS + "shared_assets/override_key_resolver.py"
NOW = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

SC_SITE_PLAN_BLOCK = """Site-plan runtime for normal and override melds (2026-09-26, override design v2):
- One `SitePlanOverrideRuntime` per hydrated root of the many_only and generalized families, built by the family
  hydrator at the first meld from the manifest's no-overrides step rows (hydrated by the family's
  `_hydrate_steps_from_rows`, which resolves contract payload refs to live values) and the live Phase-3
  topologies. Solo roots keep their own lanes.
- Site graph: `SitePlanLowering.build_site_graph` builds one `SpellSite` per step (instance key, the parameter
  table from the topology, dependency sites per parameter, logical path counts) through
  `SpellSiteGraphProcessorStrategy.build_site_graph`. That strategy is library code: Phase 9 does not register it,
  and `SpellCodegenModel.site_graph_shape` is filled only by callers that run it.
- Normal plan: at construction the runtime resolves the empty key set and emits `def _site_plan_executor(meld)`
  (`execute_normal`); both hydrators install it as the inner no-overrides executor under the unchanged
  route-keyed doors. The opt-in singleton specializer keeps its own body and deopts to this plan.
- Override plans: `execute_with_overrides(meld, ov)` reads `plans.get(tuple(ov))`; a miss compiles the key set
  under the runtime's compile lock (no user code runs there) and stores it, oldest first out at 256 key sets.
  `OverrideKeyResolver.resolve` gives the winner per (site, parameter) by rank (`__args__` > PATH > UNIQUE >
  BROADCAST), P1 cuts (a PATH rule under a parameter another key supplies is inactive, yet still validated),
  UNIQUE counts over logical paths and equal-rank conflicts. Demand follows only parameters without a winner,
  so a supplied dependency and everything only it needs is never built (B1). `__args__` of length N supplies the
  root's first N positional parameters, DI-injected ones included (one plan per arity; B5). A key set with no
  winner runs the normal plan. Key errors keep their texts, wrapped in
  `MeldExecutionError("Failed to apply overrides.")`, and are not cached.
- Emission (`SitePlanEmission`): kept steps are placed consumers before providers. A shared site is a lock-free
  hit read where it is placed plus an out-of-line `_miss{i}` that builds the sites placed inside it, then takes
  the slot guard (the Spell lock for `unique` with the lock hint), rechecks, constructs and publishes. A stored
  shared site's children are therefore not built (B2), and a plan holds one build lock at a time, never across
  another site's constructor. A shared site with a winning key is pinned to the top level, so a key that targets
  a stored instance keeps today's "already exists" refusal (P2). Disposal-bearing many sites register in the
  innermost scope store, and every registration passes the Spell's live `disposal_method_names` list.
- Call shape (P5): operands go positionally only while the receiving code binds that position to that name
  (`SitePlanLowering.positional_run`: a class keeping `type.__call__`, `object.__new__` and a plain `__init__`, a
  plain function, or a bound method of one) or while they are a caller's root `__args__` values; the rest go by
  keyword. Steps that are not plain calls (existing creations, contract payloads, a positional-only operand the
  rule cannot place) construct through the family's generic helper.
- Unresolved inputs are decided before construction: a context raises `UnresolvedInputError.for_unsupplied` for
  the first site it would build whose UNRESOLVED_INPUT parameters have no winning key, before constructing
  anything in it; solo roots check their call target the same way. OVERRIDE_REQUIRED sockets are unchanged.
- Retired with it: the Phase-9 override-targeting processor, both override compilers and runtimes, the legacy
  non-manifest codec and the fallback no-overrides family (S3b), the Phase-5 per-path socket overlay (S5a), the
  override-targeting surface (R1: `SpellOverrider`, `DagIndex`, `SocketRef`, `SocketRefSanityStrategy`, the
  blueprint socket API) and the old normal step and transient emitters (R2). Manifests are version 4 (no
  overrides section). Cache generations 13 (`collection_member_paths`) and 14 (`override_site_plan_lanes`).
- EVIDENCE:
  - `src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/site_plan_override_runtime.py:SitePlanOverrideRuntime`
  - `src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/site_plan_lowering.py:SitePlanLowering`
  - `src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/site_plan_lowering.py:SitePlanEmission`
  - `src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/override_key_resolver.py:OverrideKeyResolver.resolve`
  - `src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/hydration/generalized_hydrator.py:_build_site_plan_runtime`
  - `src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/many_only/hydration/many_only_hydrator.py:_build_site_plan_runtime`

Compiler paths after the overlay retirement (2026-09-26):
- Phase 5 records no socket references and mints no path (S5a): each `RootResolutionBlueprint` owns a fresh
  `PathRegistry` (`path_registry`) that Phase 8 mints into. The per-path overlay walk followed logical paths
  (a 15-site binary chain spent most of its 117 ms conjure there; 7 ms after). `dag_index.py` holds `PathRegistry`
  only (R1). The Phase-8 fast reuse key is (root id, ordered node ids, registry identity, pool digest).
- Collection members get their own paths: `PathRegistry.extend_path(parent, name, *, member=None)` interns by
  (parent, name, member) and keeps `name` as the stored segment, so formatted paths are unchanged. Phase 8 mints
  each collection member's subtree with `member=target_id`, so every member gets its own `Existence.many`
  dependencies, transitively; shared existences stay one per scope. Cache generation 13 cold-resets older bundles.
- EVIDENCE:
  - `src/melder/aether/spellbook/spell_compiler/dag/dag_index.py:PathRegistry.extend_path`
  - `src/melder/aether/spellbook/spell_compiler/system/spell_system_root_blueprint_builder.py:SpellSystemRootBlueprintBuilder`
  - `src/melder/aether/spellbook/spell_compiler/spell_analyzer/strategies/spell_occurrence_graph_analyzer_strategy.py:SpellOccurrenceGraphAnalyzerStrategy`

"""

SC_FAST_DOOR_BLOCK = """Fast meld door for override payloads and existing objects (2026-09-26):
- An id-string meld whose payload is a non-empty `dict` reads the same fast-door entry and guard ladder as a
  plain meld (no meld hooks, door epoch, context identity, no spellbook-wide validation) and calls the live
  `captured_context._overrides_executor(meld, payload)[0]`; a miss, a list or tuple payload, or an empty dict
  takes the full lane. The full lane's non-dynamic, no-hook override branch writes the entry after success, so
  override-only callers reach the fast lane from their second call.
- Three readers share that ladder: `ConduitMeld.meld`, `SpellSpaceMeld.meld` and `Conduit.meld`, which for an
  automatic conduit and a string `spell_id` reads the entry itself and otherwise calls the door positionally.
- Entries are `(spell, captured_context, captured_epoch, existing_object_entry)`. The bool is set by the four
  entry builders to `target_spell.user_created_object is not None`; a flagged plain hit returns
  `door_spell.user_created_object` without calling the existing-creation door (whose whole body is that read).
  The entry stores a bool, not the object: spell removal does not clear entries, and a stale entry must not keep
  a removed object alive. Override arms ignore the flag, so an existing object with a payload still reaches its
  refusal.
- No new lock, state or registry. Dynamic spells never get an entry (their creation gate routes them through
  admission), so mutation overrides are never skipped.
- EVIDENCE: `src/melder/aether/conduit/meld/conduit_meld.py:ConduitMeld.meld`,
  `src/melder/aether/conduit/meld/spellspace_meld.py:SpellSpaceMeld.meld`,
  `src/melder/aether/conduit/conduit.py:Conduit.meld` and the entry registry in
  `src/melder/aether/conduit/meld/meld.py:Meld`.

"""

SC_OVERRIDE_FLOW = """### Flow: Override Meld -> Key-Set Plan
1. `Conduit.meld(spell_id=..., override={...})` (or a front door) serves a warm automatic spell from the fast-door
   entry, calling the context's `_overrides_executor(meld, payload)`; otherwise the full lane normalizes the
   payload and reaches the same slot.
2. The override door calls `SitePlanOverrideRuntime.execute_with_overrides(meld, ov)`: one key tuple, one dict
   read, one call.
3. On the first use of a key set, `SitePlanOverrideRuntime._compile_plan` runs `OverrideKeyResolver.resolve`
   over the site graph, then `SitePlanLowering.emit`, compiles through the executor code cache and stores the
   plan; a key error raises `MeldExecutionError("Failed to apply overrides.")` and nothing is stored.
4. The plan raises for unsupplied unresolved inputs and equal-rank conflicts before any construction, builds only
   the demanded sites (shared sites through their misses), passes supplied values where their keys win, and
   returns the root.

"""

SC_OVERRIDE_DIAGRAM = """### Override Key-Set Plan Flow
```text
meld(override={...}) -> key tuple -> plan cache hit -> plan(meld, ov)
                                  -> miss -> resolver (winners, P1 cuts, conflicts) -> demand -> emit -> store
plan: unresolved/conflict checks -> demanded sites only -> shared: hit read | _miss{i} (children, guard, build)
empty key set -> normal plan (execute_normal), also the family's inner no-overrides executor
```

```mermaid
flowchart LR
  M[Override meld] --> K[Key tuple]
  K --> H{Plan stored?}
  H -->|Yes| P[Run plan]
  H -->|No| R[OverrideKeyResolver: winners, cuts, conflicts]
  R --> D[Demand: skip supplied subtrees]
  D --> E[SitePlanLowering.emit and compile]
  E --> P
  P --> S[Shared sites: hit read or miss builds children, then guard and publish]
  N[Normal meld] --> Q[Normal plan: empty key set]
```

"""

SC_EDITS = [
    ("insert_before", "Responsibilities:\n- Build requirements, symbolic graph, and local frames.\n", SC_SITE_PLAN_BLOCK),
    ("insert_before", "Responsibilities:\n- Provide a shared abstract `Meld` core for lookup, validation, lazy\n", SC_FAST_DOOR_BLOCK),
    ("replace",
     "- Ordinary required inputs use existing override execution and Python constructor errors. No additional\n"
     "  argument preflight is introduced; existing eager whole-child construction remains unchanged.\n",
     "- Ordinary required inputs use existing override execution and Python constructor errors. No additional\n"
     "  argument preflight is introduced. UPDATED 2026-09-26: override melds of the many_only and generalized\n"
     "  families no longer build a supplied child (key-set plans, B1); OVERRIDE_REQUIRED inputs keep Python's error.\n"),
    ("replace",
     "- When it is not supplied, Python raises TypeError at argument binding. Each construction failure site then\n"
     "  consults `UnresolvedInputError.from_failed_construction(spell, exc, supplied_names,\n"
     "  supplied_positional_count)`. It requires a TypeError, reads the consumer's durable Phase-3 topology and\n"
     "  returns an error only for UNRESOLVED_INPUT sockets that were neither named nor covered by the positional\n"
     "  count; that error is raised from the TypeError. Any other failure keeps its existing error:\n"
     "  MeldExecutionError, or the raw exception at a solo root.\n"
     "- Sites: `_raise_meld_construction_error` and `_construct_spell_instance` in the generalized and many_only\n"
     "  no-override compilers, the transient unrolled and manifest no-override emitted blocks, and the three\n"
     "  emitted override blocks plus `_invoke_spell_with_kwargs` in both override compilers. The hydrated\n"
     "  manifest override runtime receives the helper through its static namespace. Solo executors bind a\n"
     "  guarded `call_target` only for a spell whose topology has an UNRESOLVED_INPUT socket; their emitted\n"
     "  source is unchanged.\n"
     "- The error fires only when that object is constructed. A stored consumer is returned without calling its\n",
     "- When it is not supplied, nothing is constructed for it (UPDATED 2026-09-26, key-set plans S4a/S4b): a site\n"
     "  plan raises `UnresolvedInputError.for_unsupplied(spell, names)` for the first site it would build whose\n"
     "  UNRESOLVED_INPUT parameters have no winning key, before any construction in that context; a solo root's\n"
     "  decided call target checks the call's keyword names and positional count against those sockets and raises\n"
     "  without calling the constructor. The error has no `__cause__`. Any other constructor failure keeps its\n"
     "  existing error: MeldExecutionError chained from it, or the raw exception at a solo root.\n"
     "- Decision points: `SitePlanEmission._unresolved_check_lines` (the emitted `_raise_unresolved_input`) and the\n"
     "  solo compilers' `_call_target_for`. Until 2026-09-26 every construction failure site asked\n"
     "  `UnresolvedInputError.from_failed_construction` after the TypeError; that hook, the families' failure-path\n"
     "  branch and the override compilers that called it are gone.\n"
     "- The error is decided only where that object would be constructed. A stored consumer is returned without calling its\n"),
    ("replace",
     "- The expected type is read on the failure path from the constructor signature with FORWARDREF\n",
     "- The expected type is read when the error is built, from the constructor signature with FORWARDREF\n"),
    ("replace",
     "- INTERIM: the demand-driven build plan (override design S3/S4) is meant to decide this error before the\n"
     "  call and retire these failure-path hooks. OVERRIDE_REQUIRED inputs keep their existing errors when omitted.\n",
     "- DONE 2026-09-26: the key-set plans (override design S3/S4) decide this error before the call, and the\n"
     "  failure-path hook is retired. OVERRIDE_REQUIRED inputs keep their existing errors when omitted.\n"),
    ("replace",
     "- EVIDENCE: `src/melder/utilities/custom_exceptions/unresolved_input_error.py:UnresolvedInputError.from_failed_construction`,\n"
     "  `src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/compilers/generalized_no_overrides_codegen_creation_compiler.py:_raise_meld_construction_error`,\n",
     "- EVIDENCE: `src/melder/utilities/custom_exceptions/unresolved_input_error.py:UnresolvedInputError.for_unsupplied`,\n"
     "  `src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/site_plan_lowering.py:SitePlanEmission._unresolved_check_lines`,\n"),
    ("replace",
     "- UnresolvedInputError (a MeldExecutionError subclass, exported at the package root) when a constructed\n"
     "  spell's unresolved input was not supplied. `param_name` is the first missing parameter,\n",
     "- UnresolvedInputError (a MeldExecutionError subclass, exported at the package root) when a spell that would\n"
     "  be constructed lacks an unresolved input; raised before construction, with no `__cause__` (2026-09-26).\n"
     "  `param_name` is the first missing parameter,\n"),
    ("replace",
     "- HookExecutionError for hook failures.\n\nObservability:\n- Exceptions carrying the stage that failed",
     "- HookExecutionError for hook failures.\n"
     "- MeldExecutionError(\"Failed to apply overrides.\") chained from the key error when an override key names no\n"
     "  socket, a UNIQUE key matches more than one, or equal-rank keys disagree; \"already exists\" when a key targets\n"
     "  a stored shared instance (texts unchanged by the 2026-09-26 key-set plans).\n\n"
     "Observability:\n- Exceptions carrying the stage that failed"),
    ("replace",
     "  - override specialization executor for override/mutation paths\n",
     "  - override specialization executor for override/mutation paths\n"
     "  - UPDATED 2026-09-26: for many_only and generalized roots both come from one `SitePlanOverrideRuntime`\n"
     "    (its normal plan, and one plan per override key set).\n"),
    ("replace",
     "  `INTERNAL_CODES` (index, blueprint, socket-reference, bind-metadata and Phase-1-consistency checks) render as\n",
     "  `INTERNAL_CODES` (index, blueprint, bind-metadata and Phase-1-consistency checks; the socket-reference codes\n"
     "  left with their strategy on 2026-09-26) render as\n"),
    ("replace",
     "  ordered node ids, socket rows `(node_id, param_name, param_path_id, socket_kind)`, DAG edge rows\n",
     "  ordered node ids, DAG edge rows\n"),
    ("replace",
     "  `(parent, child, param_name, socket_kind)`, index spell ids) and signs them with SHA256. It is\n",
     "  `(parent, child, param_name, socket_kind)`, index spell ids; the phase-5 socket rows left with R1 on\n"
     "  2026-09-26) and signs them with SHA256. It is\n"),
    ("replace",
     "  id(path_registry), blueprint_socket_rows, pool_digest)` and the input signature hashes the same parts;\n",
     "  id(path_registry), pool_digest)` (blueprint socket rows left the key with R1, 2026-09-26) and the input\n"
     "  signature hashes the same parts;\n"),
    ("replace",
     "  from `inspect.signature(..., FORWARDREF)`, memoized per hydration; `.override[key]`): the generalized\n"
     "  manifest compiler resolves the ROWS once at `hydrate_no_overrides_executor` and\n"
     "  `build_specialized_no_overrides_executor` (`resolve_contract_payload_rows`), and the generalized legacy\n"
     "  and many_only `_hydrate_steps_from_rows` resolve per row (adapters gain `contract_payload_refs`). The\n",
     "  from `inspect.signature(..., FORWARDREF)`, memoized per hydration; `.override[key]`): the opt-in specializer\n"
     "  resolves its ROWS once (`build_specialized_no_overrides_executor`, `resolve_contract_payload_rows`), and\n"
     "  both families' `_hydrate_steps_from_rows`, which feed the site-plan runtime, resolve per row (adapters gain\n"
     "  `contract_payload_refs`). The\n"),
    ("replace",
     "  RuntimeError at hydration (a plan/row contract violation, not a user error). The override lanes' row\n"
     "  copies and `build_runtime_rows` are unchanged until the override site-plan lowering (S3).\n",
     "  RuntimeError at hydration (a plan/row contract violation, not a user error). The override lanes' row\n"
     "  copies went with the override lane (S3b, 2026-09-26); override plans read the same resolved rows.\n"),
    ("replace",
     "- `src/melder/utilities/custom_exceptions/spellbook_validation_error.py`\n\n\n"
     "#### Architecture narrative (folded in from `src_architecture.md`, 2026-08-01)\n\n"
     "Carried across when `src_architecture.md` was recomposed to its Required Section\n"
     "Contract, which names component-level deep dives an anti-pattern in that document.\n"
     "Text is preserved as authored; only its location changed.\n\n"
     "*From `## SpellCompiler and Validation Pipeline`:*\n",
     "- `src/melder/utilities/custom_exceptions/spellbook_validation_error.py`\n"
     "- `" + LOW + "`\n- `" + RUN + "`\n- `" + RES + "`\n\n\n"
     "#### Architecture narrative (folded in from `src_architecture.md`, 2026-08-01)\n\n"
     "Carried across when `src_architecture.md` was recomposed to its Required Section\n"
     "Contract, which names component-level deep dives an anti-pattern in that document.\n"
     "Text is preserved as authored; only its location changed.\n\n"
     "*From `## SpellCompiler and Validation Pipeline`:*\n"),
    ("replace",
     "  the no-overrides hydration of the generalized (manifest and legacy) and many_only families reads the\n",
     "  the row hydration of the generalized and many_only families (which feeds the site-plan runtime) reads the\n"),
    ("replace",
     "- Precedence is unchanged: meld override > descriptor payload value > dependency. The override lanes keep\n"
     "  the earlier literalized rows until the override site-plan lowering (S3) replaces them.\n",
     "- Precedence is unchanged: meld override > descriptor payload value > dependency. Since 2026-09-26 override\n"
     "  melds run key-set plans over the same resolved rows, so a meld that passes its own override also delivers\n"
     "  descriptor payload objects by identity.\n"),
    ("replace",
     "- RootResolutionBlueprint uses a PathRegistry (PathId interning) and DagIndex\n"
     "  (SocketRef stores param_path_id) for Phase 5/8 path handling.\n",
     "- RootResolutionBlueprint owns a PathRegistry (PathId interning) that Phase 8 mints into; since 2026-09-26\n"
     "  Phase 5 records no socket references and DagIndex/SocketRef are retired.\n"),
    ("replace",
     "4. `SpellInjectionProcessorStrategy` emits an \"unresolved_input\" param source; the Phase-10 planners treat\n"
     "   it as an override target that is omitted unless supplied.\n"
     "5. At meld a supplied value reaches the constructor by identity. A missing one fails argument binding with\n"
     "   TypeError; the family's failure site calls `UnresolvedInputError.from_failed_construction(...)` and\n"
     "   raises the result from that TypeError.\n",
     "4. `SpellInjectionProcessorStrategy` emits an \"unresolved_input\" param source; the key-set plans treat it as\n"
     "   an override target that is omitted unless supplied.\n"
     "5. At meld a supplied value reaches the constructor by identity. For a missing one the plan (or the solo\n"
     "   call target) raises `UnresolvedInputError.for_unsupplied(...)` before constructing anything under the\n"
     "   consumer (2026-09-26; until then a TypeError at argument binding was converted afterwards).\n"),
    ("insert_before", "### Flow: Conduit.has_live_creation -> Meld Probe\n", SC_OVERRIDE_FLOW),
    ("replace",
     "meld: value supplied -> constructor receives it      missing -> TypeError -> UnresolvedInputError\n",
     "meld: value supplied -> constructor receives it      missing -> UnresolvedInputError before construction\n"),
    ("replace",
     "  M -->|No| E[UnresolvedInputError raised from TypeError]\n",
     "  M -->|No| E[UnresolvedInputError before any construction]\n"),
    ("insert_before", "### Mermaid: Conduit Upgrade\n", SC_OVERRIDE_DIAGRAM),
    ("replace",
     "## Information Sources\n- `src/melder/utilities/caching_system/caching_system.py`\n",
     "## Information Sources\n- `src/melder/utilities/caching_system/caching_system.py`\n"
     "- `" + LOW + "`\n- `" + RUN + "`\n- `" + RES + "`\n"
     "- `src/melder/aether/spellbook/spell_compiler/artifact_processor/strategies/spell_site_graph_processor_strategy.py`\n"
     "- `src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/hydration/generalized_hydrator.py`\n"
     "- `src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/many_only/hydration/many_only_hydrator.py`\n"
     "- `src/melder/aether/conduit/meld/conduit_meld.py`\n"),
]

SC_HANDOFF = """2026-09-26 override site-plan lane (override design v2, S1-S6): override melds of the many_only and generalized
families run one plan per override key set that builds only what the payload does not supply (B1), accepts
`__args__` over DI-injected root parameters (B5) and keeps every key error text; normal melds of those families
run the same runtime's normal plan, where a stored shared object's dependencies are no longer rebuilt (B2).
Unresolved inputs are decided before construction in every family; constructors that observe argument names
receive names. Warm override melds and existing objects use the fast meld door. The Phase-5 per-path overlay, the
override-targeting surface, both override compilers, the legacy codec, the fallback family and the old normal
emitters are retired; collection members get their own many dependencies (cache generations 13 and 14).
Promoted into the SpellCompiler entry ("Site-plan runtime ...", "Compiler paths ..."), the Meld Resolution
Runtime entry (fast door; unresolved inputs), the DI descriptors entry, the Phase Artifacts subcomponent, the
flows and diagrams (override key-set plan; unresolved input), the code map (new files; stale ranges re-measured)
and the package inventory (declared partial update). Open, outside the lane: Phase 5 iterates the live spell pool
without a snapshot, so a concurrent bind can rarely fail a conjure-time revalidation.

"""

SA_INVARIANT = """- Override key-set plans and the site-plan runtime (2026-09-26): each hydrated root of the many_only and
  generalized families owns one `SitePlanOverrideRuntime`. Its normal plan (the empty key set) is the family's
  inner no-overrides executor; an override meld runs the plan compiled for its payload's key tuple, which
  builds only the sites the unsupplied parameters demand, so a supplied dependency and everything only it needs
  is never constructed. Plans are compiled once per key set under the runtime's compile lock and read lock-free
  after. A shared site is read lock-free where it is placed and built in an out-of-line miss that builds its
  children first and then takes its slot guard, so a plan never holds one build lock across another site's
  constructor and a stored shared site's children are not rebuilt. Operands depend on the key set only; supplied
  values are never inspected beyond the equal-rank conflict guard. Operands go positionally only where the
  receiving code binds that position to that name. Key errors keep their texts and are not cached.
  EVIDENCE: `src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/site_plan_override_runtime.py:SitePlanOverrideRuntime`
  and `src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/site_plan_lowering.py:SitePlanEmission`.
"""

SA_DIAGRAM = """### Override Key-Set Plans
```text
meld(override) -> key tuple -> stored plan? -> plan(meld, ov)
                               no -> resolver -> demand (skip supplied subtrees) -> emit, compile, store
normal meld   -> normal plan (empty key set) of the same runtime
```

```mermaid
flowchart LR
  O[Override meld] --> K[Key tuple]
  K --> C{Plan stored?}
  C -->|No| R[Resolve keys, demand, emit, compile]
  R --> P[Plan]
  C -->|Yes| P
  P --> B[Build only unsupplied sites]
  N[Normal meld] --> Q[Normal plan of the same runtime]
```

"""

SA_HANDOFF = """2026-09-26 override site-plan lane: override melds of the many_only and generalized families run one compiled
plan per override key set that never builds a supplied dependency; normal melds of those families run the same
runtime's normal plan, and unresolved inputs are decided before construction in every family. The Phase-5
per-path overlay, the override-targeting surface and the old emitters are retired, so conjure no longer grows
with logical paths. The meld sequence, the operational invariants, the failure modes, the diagrams and the code
map carry it; the component map carries the mechanics.

"""

SA_EDITS = [
    ("replace",
     "  names it when a construction goes without it (2026-09-26).\n",
     "  names it when a construction would go without it (2026-09-26).\n"
     "- Key-set plan: the code one override key set compiles to in a `SitePlanOverrideRuntime`; it builds only what\n"
     "  the payload does not supply. The empty key set is the normal plan of the many_only and generalized\n"
     "  families (2026-09-26).\n"),
    ("replace",
     "   - Execute codegen-creation-backed runtime lanes and return the resolved instance.\n",
     "   - Execute codegen-creation-backed runtime lanes and return the resolved instance.\n"
     "   - many_only and generalized roots run one site-plan runtime: normal melds its normal plan, override melds\n"
     "     the plan compiled for their key set, which builds only what the payload does not supply (2026-09-26).\n"
     "     Warm automatic id melds, override payloads and existing objects included, use the fast meld door.\n"),
    ("replace",
     "5. A constructor call that lacks an unresolved input fails argument binding; the failure path raises\n"
     "   `UnresolvedInputError` naming the consumer, parameter, expected type and override keys (2026-09-26).\n",
     "5. A meld that would construct a spell without one of its unresolved inputs raises `UnresolvedInputError`\n"
     "   naming the consumer, parameter, expected type and override keys, before anything under it is built\n"
     "   (2026-09-26).\n"),
    ("insert_before",
     "- Shared context rebuild windows (2026-09-26): a dynamic spell's CreationContext and phase-11 plan are shared\n",
     SA_INVARIANT),
    ("replace",
     "  hashes the pool-invariant rows once per pass. The override lanes keep their earlier rows until the\n"
     "  override site-plan lowering replaces them.\n",
     "  hashes the pool-invariant rows once per pass. Override melds read the same resolved rows through the\n"
     "  key-set plans (2026-09-26).\n"),
    ("replace",
     "  counting as supplied. A later matching bind re-resolves it into a NORMAL edge. The named error comes only\n"
     "  from the constructor-failure path of the object that owns the socket; a stored object never demands the\n",
     "  counting as supplied. A later matching bind re-resolves it into a NORMAL edge. The named error is decided\n"
     "  before constructing the object that owns the socket (key-set plans and the solo call target, 2026-09-26);\n"
     "  a stored object never demands the\n"),
    ("replace",
     "  and `src/melder/utilities/custom_exceptions/unresolved_input_error.py:UnresolvedInputError.from_failed_construction`.\n",
     "  and `src/melder/utilities/custom_exceptions/unresolved_input_error.py:UnresolvedInputError.for_unsupplied`.\n"),
    ("replace",
     "- A meld that constructs a spell without one of its unresolved inputs raises `UnresolvedInputError`, a\n"
     "  `MeldExecutionError` exported at the package root, chained from the binding TypeError. It names the\n"
     "  consumer, parameter, expected type and override keys, and lists every missing input. A TypeError with\n"
     "  every unresolved input supplied keeps the existing error. Since 2026-09-26 conjure no longer raises for a\n",
     "- A meld that would construct a spell without one of its unresolved inputs raises `UnresolvedInputError`, a\n"
     "  `MeldExecutionError` exported at the package root, before anything under that spell is built and with no\n"
     "  `__cause__` (2026-09-26; until then it was raised from the binding TypeError). It names the consumer,\n"
     "  parameter, expected type and override keys, and lists every missing input. A TypeError from a constructor\n"
     "  body with every unresolved input supplied keeps the existing error. Since 2026-09-26 conjure no longer raises for a\n"),
    ("replace",
     "  EVIDENCE: `src/melder/utilities/custom_exceptions/unresolved_input_error.py:UnresolvedInputError`.\n"
     "- Duplicate binding keys or spell id collisions raise RuntimeError.\n",
     "  EVIDENCE: `src/melder/utilities/custom_exceptions/unresolved_input_error.py:UnresolvedInputError`.\n"
     "- An override key that names no socket, a UNIQUE key that matches more than one, or equal-rank keys with\n"
     "  different values raise `MeldExecutionError(\"Failed to apply overrides.\")` chained from the key error; a key\n"
     "  that targets a stored shared instance raises \"already exists\". Texts are unchanged by the 2026-09-26\n"
     "  key-set plans; a failed key set is not cached.\n"
     "- Duplicate binding keys or spell id collisions raise RuntimeError.\n"),
    ("replace",
     "         value missing  -> TypeError at binding -> UnresolvedInputError (a MeldExecutionError)\n",
     "         value missing  -> UnresolvedInputError (a MeldExecutionError) before construction\n"),
    ("replace", "  M -->|No| E[UnresolvedInputError]\n", "  M -->|No| E[UnresolvedInputError before construction]\n"),
    ("insert_before", "### ASCII Context Diagram (C4)\n", SA_DIAGRAM),
    ("replace",
     "## Information Sources\n- `src/melder/utilities/caching_system/caching_system.py`\n",
     "## Information Sources\n- `src/melder/utilities/caching_system/caching_system.py`\n"
     "- `" + LOW + "`\n- `" + RUN + "`\n- `" + RES + "`\n"),
    ("replace", "## Context / Handoff Summary\n\n", "## Context / Handoff Summary\n\n" + SA_HANDOFF),
]
SC_EDITS.append(("replace", "## Context / Handoff Summary\n\n", "## Context / Handoff Summary\n\n" + SC_HANDOFF))

NEW_CORE = (
    (LOW, "key-set plan lowering: site graph from steps, placement, emission, call shape."),
    (RUN, "per-root site-plan runtime: normal plan and one plan per override key set."),
    (RES, "override key grammar, ranks, P1 cuts and conflicts over a site graph."),
)
NEW_INVENTORY = (
    "src/melder/aether/spellbook/spell_compiler/artifact_processor/data/spell_site_graph_analysis.py",
    "src/melder/aether/spellbook/spell_compiler/artifact_processor/strategies/spell_site_graph_processor_strategy.py",
    RES, LOW, RUN,
)
INVENTORY_NOTE = """PARTIAL UPDATE, 2026-09-26, DECLARED. The override site-plan lane removed the entries of the {removed}
modules it deleted and added its {added} new modules under the same rule. Modules other lanes created or deleted
since 2026-08-01 are not reflected here; group counts below are counts of the listed entries. A full re-walk is
still owed.

"""


def _line_count(root: pathlib.Path, rel: str) -> int:
    """Measure a file the way the C1 contract does (splitlines, no phantom last line)."""
    return len((root / rel).read_bytes().decode("utf-8", "replace").splitlines())


def _c1_entry(root: pathlib.Path, rel: str, note: str) -> str:
    """Render one measured C1 entry."""
    count = _line_count(root, rel)
    text = f"- path: `{rel}`\n  start_line: 1\n  end_line: {count}\n  loc: {count}\n  verified_at: {NOW}\n"
    return text + (f"  note: {note}\n" if note else "")


def _remeasure(root: pathlib.Path, data: str, rel: str) -> str:
    """Re-measure every C1 entry whose file length changed; refuse on an entry for a missing file."""
    lines = data.split("\n")
    changed = 0
    for index, line in enumerate(lines):
        match = re.match(r"^- path: `([^`]+)`$", line)
        if not match:
            continue
        path = root / match.group(1)
        if not path.exists():
            raise SystemExit(f"{rel}:{index + 1}: C1 entry for a missing file: {match.group(1)}")
        count = _line_count(root, match.group(1))
        fields = {}
        for offset in range(1, 5):
            field = re.match(r"^  (start_line|end_line|loc|verified_at): (.*)$", lines[index + offset])
            if not field:
                raise SystemExit(f"{rel}:{index + 1}: malformed C1 entry")
            fields[field.group(1)] = index + offset
        if lines[fields["end_line"]] == f"  end_line: {count}":
            continue
        lines[fields["end_line"]] = f"  end_line: {count}"
        lines[fields["loc"]] = f"  loc: {count}"
        lines[fields["verified_at"]] = f"  verified_at: {NOW}"
        changed += 1
    print(f"{rel}: re-measured {changed} C1 entries")
    return "\n".join(lines)


def _purpose(root: pathlib.Path, rel: str) -> str:
    """Inventory rule: module docstring, then `__agent_purpose__`, then first class docstring; first line."""
    tree = ast.parse((root / rel).read_text(encoding="utf-8"))
    text = ast.get_docstring(tree)
    if not text:
        for node in tree.body:
            if isinstance(node, ast.Assign) and any(
                    isinstance(t, ast.Name) and t.id == "__agent_purpose__" for t in node.targets):
                text = ast.literal_eval(node.value)
                break
    if not text:
        text = next((ast.get_docstring(n) for n in tree.body if isinstance(n, ast.ClassDef)), None)
    first = next((line.strip() for line in (text or "").splitlines() if line.strip()), None)
    return first.rstrip(".") if first else "UNKNOWN - no module docstring, `__agent_purpose__`, or class docstring"


def _inventory(root: pathlib.Path, data: str, rel: str) -> str:
    """Drop entries of deleted modules, add the lane's new modules, recount groups, declare the partial update."""
    start = data.index("### Full Package Inventory (exhaustive, retained)\n")
    end = data.index("\n## Promoted Patch Detail (re-absorbed 2026-08-02)\n")
    lines = data[start:end].split("\n")
    out, removed, index = [], 0, 0
    while index < len(lines):
        line = lines[index]
        match = re.match(r"^- `(src/[^`]+\.py)`", line)
        block = [line]
        while match and index + 1 < len(lines) and lines[index + 1].startswith("  "):
            index += 1
            block.append(lines[index])
        if match and not (root / match.group(1)).exists():
            removed += 1
        else:
            out.extend(block)
        index += 1
    for new_rel in NEW_INVENTORY:
        if any(line.startswith(f"- `{new_rel}`") for line in out):
            raise SystemExit(f"{rel}: inventory already lists {new_rel}")
        purpose = _purpose(root, new_rel)
        entry = [f"- `{new_rel}` - {purpose}"] if len(f"- `{new_rel}` - {purpose}") <= 120 else [
            f"- `{new_rel}`", f"  {purpose}"]
        group_end = next(i for i, line in enumerate(out) if line.startswith("**aether/aetheric_mediator/"))
        group_start = next(i for i, line in enumerate(out) if line.startswith("**aether/ - "))
        position = group_end
        for i in range(group_start, group_end):
            match = re.match(r"^- `(src/[^`]+\.py)`", out[i])
            if match and match.group(1) > new_rel:
                position = i
                break
        else:
            while out[position - 1] == "":
                position -= 1
        out[position:position] = entry
    for i, line in enumerate(out):
        header = re.match(r"^(\*\*.*\*\* - )(\d+) modules$", line)
        if header:
            count = 0
            for later in out[i + 1:]:
                if later.startswith("**"):
                    break
                count += bool(re.match(r"^- `src/", later))
            out[i] = f"{header.group(1)}{count} modules"
    body = "\n".join(out)
    anchor = "Module count: 574 (excluding `__init__.py`), measured 2026-08-01.\n\n"
    if body.count(anchor) != 1:
        raise SystemExit(f"{rel}: inventory module-count anchor not found once")
    body = body.replace(anchor, anchor + INVENTORY_NOTE.format(removed=removed, added=len(NEW_INVENTORY)))
    print(f"{rel}: inventory removed {removed}, added {len(NEW_INVENTORY)}")
    return data[:start] + body + data[end:]


def _edit(data: str, edit: tuple, rel: str) -> str:
    """Apply one anchored edit: `replace` or `insert_before`, each anchor exactly once."""
    kind, anchor, text = edit
    if data.count(anchor) != 1:
        raise SystemExit(f"{rel}: anchor found {data.count(anchor)} times: {anchor[:70]!r}")
    if kind == "replace":
        return data.replace(anchor, text)
    return data.replace(anchor, text + anchor)


TC_LOW = "tests/unit/melder/spellbook/spell_compiler/shared_assets/test_site_plan_lowering.py"
TC_COMP = "tests/component/melder/spellbook/test_spellbook_component_override_key_set_plans.py"
TC_HANDOFF = """2026-09-26 override site-plan lane: `test_site_plan_lowering.py` (key-set plan lowering and runtime
contracts: demand, placement and misses, guard order, call shape, unresolved inputs, disposal lists, lock-free
hits) joined the Spellbook Compiler Unit Cluster and `test_spellbook_component_override_key_set_plans.py`
(override and normal melds through real conjures, fresh and cached, both plan families) the Spellbook Compiler
Component Cluster. `test_dag_index.py` now covers `PathRegistry` only. Tests of retired code (SpellOverrider,
DagIndex targeting, the socket-reference sanity strategy, the old override and normal emitters) are gone. Stale
C1 ranges across this map were re-measured.

"""
TC_EDITS = [
    ("replace",
     "- `tests/unit/melder/spellbook/spell_crafter/dag/test_dag_index.py`\n"
     "- `tests/unit/melder/spellbook/spell_crafter/system/test_spell_system_validation_system.py`\n",
     "- `tests/unit/melder/spellbook/spell_crafter/dag/test_dag_index.py` (PathRegistry only since 2026-09-26)\n"
     "- `tests/unit/melder/spellbook/spell_crafter/system/test_spell_system_validation_system.py`\n"
     "- `" + TC_LOW + "` (key-set plans, 2026-09-26)\n"),
    ("replace",
     "- `tests/component/melder/spellbook/spell_crafter/validation/test_spellbook_component_validation_system.py`\n"
     "\n### Subcomponent: Aether Integration Cluster\n",
     "- `tests/component/melder/spellbook/spell_crafter/validation/test_spellbook_component_validation_system.py`\n"
     "- `" + TC_COMP + "` (key-set plans, 2026-09-26)\n"
     "\n### Subcomponent: Aether Integration Cluster\n"),
    ("replace", "## Context / Handoff Summary\n\n", "## Context / Handoff Summary\n\n" + TC_HANDOFF),
]


def _tests_components(root: pathlib.Path) -> str:
    """Key files, measured C1 entries for the two new test files, re-measured ranges, handoff."""
    tc = (root / TC).read_text(encoding="utf-8")
    for edit in TC_EDITS:
        tc = _edit(tc, edit, TC)
    entries = "".join(_c1_entry(root, rel, "") for rel in (TC_LOW, TC_COMP))
    tc = _edit(tc, ("insert_before", "\n## Diagrams\n### ASCII Component Diagram (C3/C2)\n", "\n" + entries.rstrip("\n")), TC)
    return _remeasure(root, tc, TC)


def main() -> None:
    """Check everything, then write the selected documents (unless --check).

    `--only tc` limits the run to tests_components (the source maps were applied first, 2026-09-26T20:1xZ; their
    anchors no longer match once applied, so a re-run must not touch them).
    """
    root = pathlib.Path(sys.argv[1])
    check = "--check" in sys.argv[2:]
    only_tc = "--only" in sys.argv[2:] and sys.argv[sys.argv.index("--only") + 1] == "tc"
    pending = {}
    if not only_tc:
        sc = (root / SC).read_text(encoding="utf-8")
        for edit in SC_EDITS:
            sc = _edit(sc, edit, SC)
        sc = _inventory(root, sc, SC)
        sc = _edit(sc, ("insert_before", "### Full Package Inventory (exhaustive, retained)\n",
                        "".join(_c1_entry(root, rel, "") for rel, _note in NEW_CORE)), SC)
        pending[SC] = _remeasure(root, sc, SC)
        sa = (root / SA).read_text(encoding="utf-8")
        for edit in SA_EDITS:
            sa = _edit(sa, edit, SA)
        anchor = "  note: DI shape classification.\n"
        sa = _edit(sa, ("replace", anchor, anchor + "".join(_c1_entry(root, rel, note) for rel, note in NEW_CORE)), SA)
        pending[SA] = _remeasure(root, sa, SA)
    pending[TC] = _tests_components(root)
    for rel, data in pending.items():
        long_lines = [i + 1 for i, line in enumerate(data.split("\n"))
                      if len(line) > 120 and "`" not in line and not line.startswith("|")]
        if long_lines:
            print(f"{rel}: prose lines over 120 chars: {long_lines[:10]}")
        if not check:
            (root / rel).write_text(data, encoding="utf-8")
        print(("checked " if check else "edited ") + rel)

if __name__ == "__main__":
    main()
