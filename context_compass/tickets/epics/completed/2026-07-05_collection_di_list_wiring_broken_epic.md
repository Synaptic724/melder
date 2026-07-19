# Epic: `list[Frame]` collection DI never wires its members (+ Phase-6 empty-collection guard)

- Completed: 2026-07-11T21:45:00Z
- Summary: Closed on the orphan sweep (agent_0 does not exist;
  owner-directed). The header line below is STALE - agent_0's later
  board-row state (2026-07-07: guard restored mode-scoped per owner
  ruling, []-injection landed for dynamic books, c1_zero re-pinned to
  raise, v6) postdates it, and the owner's repeated full-tree greens
  since (9702) prove the break matrix + tree exit gates. Residue, if
  any, surfaces as new work with fresh evidence.

Status: OPEN — root cause localized to the phase-3 -> phase-8 collection dependency
flow; NOT yet fixed. A phase-6 detection strategy was added but does not yet fire.
(NOTE 2026-07-11: stale header - see the closure Summary above.)
Owner constraint: all validation must live in Phase 4 or Phase 6 (never Phase 3);
the empty-collection guard specifically must be Phase 6 (not Phase 8).

Target runtime: Python 3.14t (free-threaded). The package cannot be imported under
< 3.14 (deferred annotations are relied upon), so all reproduction must run on 3.14t.

--------------------------------------------------------------------------------
## 1. Symptom

A consumer whose constructor declares a collection dependency:

    class NeedsPlugins:
        def __init__(self, plugins: list[IPlugin]) -> None:
            self.plugins = plugins

does NOT receive its providers, no matter how many are bound (0, 1, 2, or 3).
At meld time the generated constructor call omits the `plugins` argument entirely:

    TypeError: NeedsPlugins.__init__() missing 1 required positional argument: 'plugins'

Intended behavior: bind N implementations under a frame; `list[Frame]` receives a
list of all N instances; N==0 injects an empty list `[]` (see the resolver docstring
at src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_3.py:520,
"an empty collection will be injected").

--------------------------------------------------------------------------------
## 2. Failing tests (paths + exact failure)

File: tests/integration/melder/spellbook/test_spellbook_integration_resolution_break_matrix.py
Run: python -m pytest <that file> -k c1 -v -rA   (on 3.14t)

- test_c1_zero_implementations_fails_conjure         (~line 581)
    Binds NeedsPlugins only (0 IPlugin providers). Expects conjure() to raise
    (empty required collection). ACTUAL: "DID NOT RAISE" — conjure succeeds; the
    failure is deferred to meld. The added Phase-6 guard did NOT fire.

- test_c1_single_implementation_injects_one          (~line 596, marked xfail)
    1 provider. ACTUAL: solo hydrator, missing 'plugins' arg (TypeError).

- test_c1_three_implementations_injects_all_three     (~line 608)
    3 providers under IPlugin. ACTUAL: routes to `solo_no_overrides_codegen_creation`,
    missing 'plugins' arg (TypeError). Proves members do NOT wire even when bound.

- test_c1_mixed_existence_still_injects_all           (~line 625)
    2 providers (unique + many). ACTUAL: same solo missing-arg TypeError.

- test_c1_collection_over_concrete_element_type       (~line 644, marked xfail)
    list[Engine] with 1 Engine bound under spellframe=Engine.
    ACTUAL: `object of type 'Engine' has no len()` — a SINGLE member was injected
    as a bare scalar instead of a 1-element list (distinct symptom; see Defect #2).

SEPARATE, unrelated bug surfaced by the same file (do NOT conflate with collections):
- test_b3_override_beats_spellmap_default            (~line 497)
    meld(spell=NeedsConfigViaMap, spell_override={"config": sentinel}) where the
    param default is SpellMap(Config). ACTUAL:
    RuntimeError: "generalized manifest references unknown spell_id 'cf958b4...'"
    at generalized_binding_resolver.resolve_spell (generalized hydrator). This is an
    override-vs-SpellMap-default codegen bug, tracked here only as a pointer.

--------------------------------------------------------------------------------
## 3. Minimal reproduction

    sb = Spellbook(); sb.get_configuration().set_property("phase_scheduler_workers_per_spellbook", 1)
    sb.bind(spell=PluginA, existence=Existence.unique, permissions="create", spellframe=IPlugin)
    sb.bind(spell=PluginB, existence=Existence.unique, permissions="create", spellframe=IPlugin, binding_name="b")
    sb.bind(spell=PluginC, existence=Existence.unique, permissions="create", spellframe=IPlugin, binding_name="c")
    sb.bind(spell=NeedsPlugins, existence=Existence.unique, permissions="create")
    c = sb.conjure(name="root")
    c.meld(spell=NeedsPlugins).plugins   # expected 3, actual: missing-arg TypeError

IPlugin is an empty typing.Protocol. NeedsPlugins.__init__(self, plugins: list[IPlugin]).

--------------------------------------------------------------------------------
## 4. Traced causal chain (meld failure back to phase 3)

1. meld -> creation_context._no_overrides_instance_executor -> `solo` hydrator
   (src/.../codegen_creation_system/strategies/solo/hydration/solo_hydrator.py:156).
   The `solo` strategy is COLLECTION-BLIND (no collection handling anywhere under
   .../strategies/solo/**), so the collection arg is never assembled -> missing arg.

2. `solo` is selected by SoloCodegenPlanDiscoveryStrategy.discover
   (src/.../codegen_planner/codegen_plan_discovery_system/strategies/
   solo_codegen_plan_discovery_strategy.py:~43): it claims when
   `existence_occurrence_shape.total_spell_count == 1`.

3. The occurrence graph that drives that count is built in
   src/.../spell_analyzer/strategies/spell_occurrence_graph_analyzer_strategy.py:
     - _build_occurrence_graph (~628) -> _collect_occurrence_dependencies (~769)
     - _append_topology_dependencies (~809): iterates topology.sockets and does
       `if not socket.target_spell_ids: continue` (~826). It RETURNS True whenever a
       topology exists, and _collect_occurrence_dependencies only falls back to the
       DAG `if not used_topology` (~792). => dependency expansion is driven ENTIRELY
       by topology.sockets[].target_spell_ids.
   So if the `plugins` socket has EMPTY target_spell_ids, NeedsPlugins gets zero
   dependency occurrences -> occurrence graph has 1 node -> solo -> missing arg.

4. Therefore the collection socket's `target_spell_ids` is EMPTY even with 3 providers
   bound. That tuple is populated (or not) in Phase 3.

5. Phase 3: src/.../phases/compiler_phase_3.py
     - _build_local_frame_dag (~748): for each dep, resolve; `if not resolved: continue`
       (~848); for resolved members append to socket_targets[(param_name, position)]
       and add DAG edges; then topology = _build_local_topology(spell, graph, socket_targets)
       (call ~868).
     - Collection resolve: _resolve_collection_by_annotation (~505) uses the pass
       candidate index via _indexed_annotation_candidates (~374) when present, else
       the scan _matches_annotation (~177).
     - Static reading says BOTH paths SHOULD match PluginA (spellframe=IPlugin) against
       the element annotation IPlugin:
         * index: _build_candidate_index (~277) buckets by `id(frame)` (~334); the
           lookup is `ident[id(annotation)]` (_indexed_annotation_candidates ~403).
         * scan: `frame is annotation` (_matches_annotation ~245).
     - Phase 2 (compiler_phase_2.py:135-137) sets the collection dep's
       target_annotation = param.collection_element_annotation (i.e. IPlugin) and
       is_collection = True. So the element (IPlugin), not list[IPlugin], is matched.

   => Code reads correct, but runtime yields empty target_spell_ids for list[IPlugin].
   The concrete-frame case (list[Engine], spellframe=Engine) yields ONE member
   (hence the scalar-unwrap symptom), which hints the Protocol-frame path differs.

--------------------------------------------------------------------------------
## 5. The decisive unknown (needs ONE runtime data point)

Two hypotheses remain, indistinguishable by static reading:

  (A) RESOLUTION returns empty: _resolve_collection_by_annotation returns {} for
      list[IPlugin]. Likely causes: identity mismatch between id(IPlugin) in the
      resolved annotation vs id(IPlugin) at bind time (so the `ident` bucket misses),
      or eq-risky index handling for Protocol metaclasses (_get_candidate_index ~348
      returns None on eq_risky, forcing the scan; verify which path runs).

  (B) TOPOLOGY BUILD drops it: resolution returns the members (they appear as DAG
      edges) but _build_local_topology does not copy them into the socket's
      target_spell_ids — a key mismatch between socket_targets keyed by
      (param_name, position) and how _build_local_topology reads it.

DISAMBIGUATE with a 1-line probe at compiler_phase_3.py:848, during the NeedsPlugins
build:
    print(dep.param_name, dep.di_shape, len(resolved))
- len == 3  => hypothesis (B): resolution is fine; fix _build_local_topology / the
              socket_targets key.
- len == 0  => hypothesis (A): fix the collection matcher/index for Protocol frames.

A second probe to confirm the topology contents at Phase 6 (inside the added strategy,
per socket): print spell_id, socket.param_name, socket.is_collection,
socket.is_optional, socket.target_spell_ids.

--------------------------------------------------------------------------------
## 6. Distinct defects (do not merge)

Defect #1 (PRIMARY): collection members never wire.
  list[Frame] (esp. a Protocol-frame element) resolves/records ZERO target_spell_ids,
  so the consumer routes to the collection-blind `solo` codegen and the arg is dropped.
  Affects 0/1/2/3 members. Fix lives in Phase 3 resolution or topology-build
  (see section 5) — but per owner constraint, DO NOT add validation logic to Phase 3;
  a genuine resolution/topology *correctness* fix there is a different thing than
  validation and should be discussed with the owner.

Defect #2 (SECONDARY): single-member unwrap.
  When a collection does resolve exactly one member (the concrete list[Engine] case),
  codegen injects the bare instance instead of [instance]. The generalized/many
  collection compiler must ALWAYS emit a list, independent of member count.
  Sites: src/.../codegen_creation_system/strategies/generalized/** and .../many_only/**.

Defect #3 (DESIGN): empty collection should inject `[]`.
  compiler_phase_3.py:848 `if not resolved: continue` drops the socket entirely, so
  codegen has no record to emit `[]`. Per the resolver docstring the intent is to
  inject an empty list. The owner wants the *validation* of a required-but-empty
  collection to be a Phase-6 strategy (see section 7); optional collections should
  inject `[]` and pass.

--------------------------------------------------------------------------------
## 7. Added strategy (this session) — present but NOT working

File: src/melder/aether/spellbook/spell_compiler/system/validation/empty_collection_strategy.py
Class: EmptyCollectionStrategy(SpellSystemValidationStrategy)
Registered: src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_6.py
            in _build_strategies(), immediately after VisibilityGapStrategy()
            (import added next to the visibility_gap_strategy import).

What it does: in Phase 6, for each spell in `index.nodes`, reads the durable local
topology via spell_system_states.get_local_topology_by_id(spell_id).iter_sockets()
and emits a `collection_socket_no_providers` ERROR for each socket where
is_collection and not is_optional and not target_spell_ids.

Why topology (not the DAG or requirements): at Phase 6 the artifact `_requirements`
is already nulled (spell_compiler_artifact.py:299), the combined DAG carries no
is-collection flag (SocketKind is only NORMAL/SPELL_CONTRACT and an empty collection
emits no edge), so the only Phase-6-durable record of "this socket is a list AND how
many it wired" is the SpellSystemStates local topology (SpellSocketDescriptor:
topology/spell_local_topology.py:69 is_collection, :71 target_spell_ids).

Observed: it did NOT fire for test_c1_zero (conjure did not raise). Candidate reasons
to investigate (need a print inside run()):
  - the conjure path may use CompilerPhase6.run_local, which fail-fasts on a
    visibility-gap pre-pass and returns BEFORE the strategy set runs;
  - spell_system_states.get_local_topology_by_id(spell_id) may return None for the
    id key coming from index.nodes (id-keying mismatch: version id vs pool key);
  - the collection socket may be absent from the topology, or its is_collection flag
    is False, or (unexpectedly) target_spell_ids is non-empty.
Confirm which before iterating on the strategy.

Prior variant (also in git history of this file this session): a version that walked
blueprints[root].dag counting parents via node.dependencies/node.incoming_params.
That approach CANNOT see an empty collection (no DAG edge exists) and depended on
`_requirements` (nulled by Phase 6), so it was replaced by the topology version.

--------------------------------------------------------------------------------
## 8. Source files to gather (with the key lines)

Resolution / topology (Phase 1-3):
  - phases/compiler_phase_1.py  (requirements + di_shape classification)
  - spell_requirements_finder/parameter_di_shape.py  (ParameterDIShape enum;
    COLLECTION_BY_ANNOTATION)
  - spell_requirements_finder/spell_requirements_finder.py  (_classify_parameter,
    collection element extraction)
  - phases/compiler_phase_2.py:135-137  (collection dep target_annotation + is_collection)
  - phases/compiler_phase_3.py  (505 _resolve_collection_by_annotation, 748
    _build_local_frame_dag, 848 the drop, 177 _matches_annotation, 374
    _indexed_annotation_candidates, 277 _build_candidate_index, 348 _get_candidate_index,
    868 _build_local_topology call)
  - topology/spell_local_topology.py  (SpellSocketDescriptor + SpellLocalTopology;
    iter_sockets, sockets, get_local_topology_by_id lives on SpellSystemStates)

Occurrence / routing (Phase 5/8/10):
  - blueprints/root_resolution_blueprint.py  (combined DAG, socket_refs, dag_index)
  - dag/dag_node.py, dag/directed_acyclic_work_graph.py  (nodes, dependencies,
    incoming_params, children_by_param, get_node)
  - spell_analyzer/strategies/spell_occurrence_graph_analyzer_strategy.py
    (809 _append_topology_dependencies, 826 skip-empty, 792 used_topology gate,
    480 total_spell_count=len(occurrence_rows))
  - spell_analyzer/data/spell_existence_occurrence_analysis.py  (total_spell_count field)
  - codegen_planner/codegen_plan_discovery_system/strategies/
    solo_codegen_plan_discovery_strategy.py  (claims total_spell_count==1)
  - codegen_creation_system/strategies/solo/**   (collection-blind)
  - codegen_creation_system/strategies/generalized/**  (has collection handling +
    the single-unwrap Defect #2)

Validation (Phase 4/6):
  - phases/compiler_phase_6.py  (_build_strategies list, run_frame_wide, run_local)
  - system/validation/strategy_base.py  (SpellSystemValidationStrategy.run contract)
  - system/validation/broken_spell_in_dag_strategy.py, dependency_type_sanity_strategy.py,
    root_coverage_strategy.py  (reference patterns for walking index/blueprints)
  - system/validation/empty_collection_strategy.py  (the added, not-yet-working guard)
  - system/system_diagnostic.py  (SystemDiagnostic / SystemDiagnosticSeverity)
  - spell_compiler_artifact.py:299  (_requirements nulled -> why Phase 6 can't use it)

Tests:
  - tests/integration/melder/spellbook/test_spellbook_integration_resolution_break_matrix.py
    (the c1_* tests + b3_override; module doubles: IPlugin, PluginA/B/C, NeedsPlugins,
    NeedsEngineList, Engine)
  - tests/integration/melder/spellbook/test_spellbook_integration_resolution_contract_forms.py
    (C1 happy-path form test)
  - tests/integration/melder/spellbook/test_spellbook_integration_validation_system.py
    (how Phase 4/6 validation is driven + compiler_test_helpers usage)
  - tests/component/melder/spellbook/compiler_test_helpers.py  (run_phase_1..11 drivers)

--------------------------------------------------------------------------------
## 9. Environment gotchas (real, cost hours if unknown)

- 3.14t ONLY. Cannot import melder under 3.10/3.13; conftest resets the Aether
  singleton per test (see the break-matrix fixture).
- Mount/tool corruption observed this session:
    * bash reads MANGLE some source files (deterministic substring dropping):
      "collections"->"lns", "socket_kind"->"n", "total_spell_count"->"ln". Use the
      Read file-tool for any file you will edit; do NOT trust bash grep/sed contents
      of dag/**, spell_analyzer/**, generalized/** codegen files.
    * file-tool Write/Edit on these paths TRUNCATE the tail or append NUL bytes on
      shrinking edits. After any write: py_compile AND check
      open(path,'rb').read().count(b'\x00') == 0; if truncated, rewrite via a bash
      `cat > file <<'EOF'` heredoc (that has been reliable).

--------------------------------------------------------------------------------
## 10. Owner constraints (must honor)

- Validation belongs in Phase 4 or Phase 6 ONLY. Do not add validation to Phase 3.
- The empty/required-collection guard MUST be Phase 6, not Phase 8.
- By Phase 6 the combined DAGs exist (Phase 5 stitches all local DAGs); Phase 6 is the
  correct place to reason about whole-graph satisfiability.
- Fixing the members-not-wiring correctness bug (Defect #1) may require a Phase-3
  resolution/topology change; that is a correctness fix, not validation — raise it
  with the owner before editing Phase 3.

--------------------------------------------------------------------------------
## 11. Suggested order of attack

1. Run the 1-line probe at compiler_phase_3.py:848 (section 5) to pick hypothesis A vs B.
2. Fix Defect #1 at its true source (resolution match for Protocol frames, or the
   topology-build key) so target_spell_ids is populated for list[IPlugin].
3. Re-run c1_three/c1_mixed: expect them to route to the generalized (not solo) lane.
4. Fix Defect #2 (generalized/many must wrap a single member in a list).
5. Confirm the Phase-6 EmptyCollectionStrategy now fires on c1_zero (required empty)
   and stays silent on the populated cases; fix its non-firing (section 7) if needed.
6. Decide empty-required policy: hard error (current strategy) vs inject [] for
   optional; align the c1_zero test accordingly.
7. Separately triage test_b3_override_beats_spellmap_default (override vs SpellMap
   default manifest bug).

--------------------------------------------------------------------------------
## Artifact Links (Optional)

- artifacts/2026-07-05_collection_di_probe.py (probe_script, delete_on_close):
  read-only monkeypatch probe answering P1 classification, P3 resolution
  (hypothesis A vs B), topology rows, and P6 strategy visibility in one
  user-run 3.14t pass.

--------------------------------------------------------------------------------
## Notes

- DATETIME: 2026-07-05T20:30:23Z
  TYPE: PLAN
  CLAIM: Lane opened by agent_0 (certified this session). Order of attack accepted as
    written in section 11, with one environment delta: this sandbox has no 3.14t, so
    the section-5 disambiguation probe cannot be executed here; hypothesis A vs B will
    be resolved by exhaustive static reading of the phase-3 resolution + topology-build
    path first, and only escalated to a user-run probe if static reading stays truly
    ambiguous. All source reads via file-tool (bash reads mangle these files, sec. 9).
  EVIDENCE:
  - tickets/epics/2026-07-05_collection_di_list_wiring_broken_epic.md:126-150
  - tickets/epics/2026-07-05_collection_di_list_wiring_broken_epic.md:263-276
  IMPACT: Keeps the fix loop unblocked without burning a user round-trip unless needed.
  NEXT: Read compiler_phase_3.py resolution/index/topology sections + phase 2 dep
    construction, then record FACT or DECISION_REQUEST on hypothesis A vs B.
  REREAD: REQUIRED
  SCORE_0_TO_10: 7

- DATETIME: 2026-07-05T20:55:00Z
  TYPE: CONFLICT
  CLAIM: Synaptic onboarding workflow Phase 4 requires reading readable_src_graph.json,
    but the file is 732KB (~180k tokens) and a full read cannot fit in the session
    context window without forcing compaction mid-lane (self-defeating; also collides
    with context_window_budget bounded-slice policy). Resolution applied: full reads of
    src_architecture.md + src_components.md, plus bounded in-scope graph chunks for the
    compiler subsystem (phases 2-9 nodes, SpellLocalTopology, analyzer, hydrators, solo
    discovery) per graph_details_usage bounded-chunk consumption. Full graph read waived
    unless the owner overrules.
  EVIDENCE:
  - agent_onboarding/user_defined/synaptic_python_developer/workflows/synaptic_python_developer_onboarding.md:127-138
  - agent_onboarding/default/general/skills/context_window_budget.md:9-12
  - agent_onboarding/default/engineer/skills/graph_details_usage.md:34-38
  IMPACT: Onboarding bundle treated complete; lane keeps enough context budget for the fix.
  NEXT: Begin source investigation of compiler_phase_3.py (hypothesis A vs B).
  REREAD: HELPFUL
  SCORE_0_TO_10: 6

- DATETIME: 2026-07-05T22:40:00Z
  TYPE: FACT
  CLAIM: Reading tranche results. (1) Hypothesis B as stated is structurally impossible
    inside phase 3: _build_local_frame_dag records socket_targets under
    (dep.param_name, dep.position) and _build_local_topology reads the same tuple from
    the same graph.dependencies objects - no key can mismatch. (2) Phase-6 wiring of
    EmptyCollectionStrategy is correct: registered in _build_strategies and run by both
    run_frame_wide and run_local; the run_local visibility fail-fast cannot mask c1_zero
    (zero deps -> zero gaps). (3) Topology keying is aligned: registered and fetched by
    selected_spell_id. (4) Conjure DOES raise on phase-6 ERROR diagnostics via
    _enforce_conduit_resolution_valid on the from-scratch path, so the strategy's silence
    in c1_zero means the socket rows themselves lack (is_collection AND not optional AND
    empty targets) or the topology/di_shape upstream is wrong. (5) Phase-1 classification
    and phase-3 matching read correct for Protocol elements too (typing.List normalizes
    to list origin; Bind stores Protocol spellframes untransformed; identity buckets and
    the scan's `frame is annotation` both should match) - static analysis is exhausted at
    the same wall as the prior session. (6) OWNER CONSTRAINT reaffirmed 2026-07-05: no
    fix of any kind in phase 3 without explicit approval; phase 3 is collection/attachment
    only; propagate what phase 6 needs and act in phase 6.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_3.py:714-746
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_3.py:848-868
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_6.py:303-327
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_6.py:445-488
  - src/melder/aether/aetheric_frame/dev_ops/spell_system_states/spell_system_states.py:1168-1263
  - src/melder/aether/spellbook/spellbook_creation_system.py:307-368
  - src/melder/aether/spellbook/spell_compiler/spell_requirements_finder/spell_requirements_finder.py:1064-1177
  - src/melder/aether/spellbook/bind/bind.py:306-343
  IMPACT: The decisive unknown is now a pure runtime question; every static suspect is
    cleared or pinned to the probe. Sandbox cannot run it (3.10 only; uv 3.14t download
    blocked by network policy), so the owner runs the probe.
  NEXT: Owner runs artifacts/2026-07-05_collection_di_probe.py on 3.14t and reports
    output; fix design follows the probe verdict (phase-6 action + propagation only).
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-07-05T23:59:00Z
  TYPE: MEASURE
  CLAIM: Owner-run probe (3.14t, direct python, doubles in __main__) shows the ENTIRE
    pipeline behaving CORRECTLY on the current tree, contradicting the pytest failures:
    (S1 c1_zero) classify=COLLECTION optional=False; targets=0; EmptyCollectionStrategy
    EMITTED collection_socket_no_providers; conjure RAISED SpellbookValidationError -
    exactly what the failing test expects. (S2 c1_three) resolution len=3 via candidate
    index; topology targets=3; meld returned a real list len=3. (S3 concrete single)
    resolution len=1, topology targets=1, but meld returned a BARE Engine instead of
    [Engine] - Defect #2 (single-member unwrap) CONFIRMED live; the only probe-visible
    defect. Also: the runtime annotation arrives as builtin GenericAlias
    list[IPlugin] even though the source wrote typing.List[IPlugin].
  EVIDENCE:
  - artifacts/2026-07-05_collection_di_probe.py:1-336
  - tickets/epics/2026-07-05_collection_di_list_wiring_broken_epic.md:33-63
  IMPACT: Hypotheses A and B are BOTH dead for the current tree; classification,
    resolution, topology, the phase-6 guard, and conjure enforcement all work outside
    pytest. The c1 failures are context-dependent: pytest execution context (assertion-
    rewritten module import, conftest chain) or run-to-run drift of the ACTIVE
    (uncommitted, owner-held) conduit.py, which SyntaxError'd at :5555 mid-session and
    then parsed fine with no restore - the tree state under the earlier pytest run is
    not provably the tree state under the probe. Owner directive recorded: conduit.py
    is active work; do NOT restore or edit it in this lane. My file-tool AND bash views
    of conduit.py do not match the owner's live copy (both transports show a clean
    5572-line file) - treat conduit.py content as UNKNOWN through my tools.
  NEXT: Owner re-runs the 4 c1 tests on the current tree to check probe/pytest parity;
    if they now pass, remaining work = Defect #2 list-wrap + b3 (separate); if they
    still fail, the delta is pytest-context and gets probed inside pytest.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-07-06T00:45:00Z
  TYPE: MEASURE
  CLAIM: ROOT CAUSE CONFIRMED - STALE CONJURE-CACHE REPLAY, not a resolution bug.
    Quarantining ONE file (src/melder/__melder_cache__/__conjure_cache__/default/root.melc)
    flipped all four failing tests PLUS b3_override to PASSED on user-run 3.14t
    (5 passed, 2 xfailed). Mechanism: every break-matrix test conjures
    (frame=default, name="root"), so they all share one bundle file keyed
    frame/conduit with per-spell payloads keyed ONLY by spell content SHA. The bundle
    accumulated payloads across historical runs; replay served (a) solo bundles built
    when the pipeline was older/broken -> missing-arg TypeErrors (c1_three/mixed),
    (b) a generalized manifest embedding a dependency spell id from a DIFFERENT pool
    composition -> b3 "unknown spell_id cf958b...", and (c) the full-cache-hit lane
    bypasses _enforce_conduit_resolution_valid BY DESIGN -> c1_zero conjure never
    raised even though EmptyCollectionStrategy works (probe-proven: it fires and
    fails conjure on the from-scratch path). Defect #1 does NOT exist in current
    code; the owner's phase-6 guard is correct and live. Remaining real defects:
    Defect #2 single-member bare injection (both xfails; probe scenario 3 returned a
    bare Engine), and the cache-correctness defect itself.
  EVIDENCE:
  - src/melder/__melder_cache__/__conjure_cache__/default/root.melc (quarantined as .quarantine)
  - src/melder/aether/spellbook/spellbook_creation_system.py:319-322
  - src/melder/utilities/caching_system/caching_system.py:27-127
  - src/melder/aether/aetheric_frame/aetheric_frame_configuration.py:82-82
  IMPACT: Epic reframes from "collection DI broken" to "conjure cache replays stale
    bundles and bypasses phase-6 verdicts". Relevant to the parked
    2026-07-02_unify_cache_rehydration_with_live_emitters_epic (owner-parked, fable_0):
    this is live evidence for that lane's premise. Quarantined bundle retained for
    forensics until a cache fix lands.
  NEXT: DECISION_REQUEST below - owner picks cache-fix scope; Defect #2 fix proceeds
    in this lane.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-07-06T00:45:00Z
  TYPE: DECISION_REQUEST
  CLAIM: Cache-correctness scope needs an owner decision. Compliant options:
    (1) MINIMAL GUARD (this lane): validate payloads at load/hydration - reject any
    cached payload whose manifest references spell ids missing from the live pool,
    and stamp bundles with a compiler-version/codegen-schema token so old bundles
    invalidate wholesale; cache-hit lane re-applies the stored phase-6 verdict or
    falls back to from-scratch when absent. (2) FULL REDESIGN (separate lane): fold
    into the parked unify_cache_rehydration epic (one emitter for live+cache births)
    where verdict/replay coherence is solved structurally. (3) BOTH: land (1) now as
    MRP-correct stopgap, keep (2) as the durable fix.
  EVIDENCE:
  - tickets/epics/2026-07-02_unify_cache_rehydration_with_live_emitters_epic.md:1-1
  IMPACT: Without at least (1), any compiler-output change silently resurrects this
    failure class for every SHA-stable spell in every long-lived bundle.
  NEXT: Owner picks 1/2/3; meanwhile Defect #2 (single-member list wrap in the
    generalized/many_only codegen lanes) is investigated in this lane.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-07-06T01:10:00Z
  TYPE: DECISION
  CLAIM: Owner decision (2026-07-06): cache-correctness implementation DEFERRED - the
    stale cache was cleared manually and that is accepted as sufficient for now. The
    versioning mechanism exists (CURRENT_VERSION=3 + python cache_tag + conduit
    identity enforced at load, mismatch regenerates cold); the operational gap is that
    CURRENT_VERSION tracks container format only and was not bumped across
    payload-semantics changes. Design for later (recorded, not approved for build):
    bump to 4 + add a codegen_schema metadata token owned by the codegen system +
    hydration self-heal on unknown manifest ids + phase-6 verdict parity on cache-hit
    conjures. RISK accepted by owner: failure class recurs on the next
    payload-semantics change until this lands.
  EVIDENCE:
  - src/melder/utilities/caching_system/caching_system.py:60-64
  - src/melder/utilities/caching_system/caching_system.py:408-458
  IMPACT: Lane pivots to Defect #2 (single-member bare injection; the two xfails).
  NEXT: Locate the generalized/many_only emission branch that decides list-vs-scalar
    by member count instead of socket is_collection; trace whether is_collection
    survives into the phase 9-11 model/plan/creation artifacts.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-07-06T01:55:00Z
  TYPE: FACT
  CLAIM: Defect #2 root cause mapped end to end. The socket's is_collection flag dies
    after phase 3: neither the phase-9 SpellCodegenModel, the SpellInjectionParamSource/
    SpellInjectionInstanceSpec, nor the generalized/many_only plan steps carry it. The
    ONLY collection signal downstream is allow_list_aggregation, and phase 9 derives it
    BY COUNT (spell_injection_processor_strategy.py:177-178: `if len(dependency_keys)
    > 1`). Consequently every phase-11 emitter decides list-vs-scalar by count:
    _build_kwargs_no_overrides docstring says it outright ("Single dependency maps to
    one value; multiple map to a list", generalized_no_overrides compiler :1309-1358)
    and _inlinable_common_shape (:552-593) inlines a 1-member collection as a bare
    scalar kwarg. A 1-member collection is indistinguishable from single DI everywhere
    past phase 9. Durable per-param truth exists in SpellSystemStates local topology
    (socket.is_collection), reachable at phase 9 via spell._spellbook, same read
    pattern as the phase-6 guard and the phase-8 analyzer.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/artifact_processor/strategies/spell_injection_processor_strategy.py:166-183
  - src/melder/aether/spellbook/spell_compiler/artifact_processor/data/spell_injection_analysis.py:18-72
  - src/melder/aether/spellbook/spell_compiler/codegen_planner/data/spell_generalized_codegen_lane_plan.py:92-231
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/compilers/generalized_no_overrides_codegen_creation_compiler.py:552-593
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/compilers/generalized_no_overrides_codegen_creation_compiler.py:1309-1358
  IMPACT: Fix shape is pure propagation + consumption (no phase-3 changes): phase 9
    reads topology truth and stamps per-param is_collection; plan steps carry a
    collection_param_names set; phase-11 emitters wrap by flag not count. Payload
    schema grows a field -> CachingSystem.CURRENT_VERSION must bump 3->4 in the same
    diff (the lever the owner pointed at).
  NEXT: Present exact file/symbol list to owner for scope confirmation (exceeds the
    5-file expansion gate), then implement.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-07-06T02:50:00Z
  TYPE: PLAN
  CLAIM: Defect #2 implementation IN FLIGHT (owner approved full slice, read-first).
    LANDED so far: (1) SpellInjectionParamSource.is_collection +
    SpellInjectionInstanceSpec.collection_param_names (derived frozenset); (2) phase-9
    strategy stamps per-param collection truth from SpellSystemStates topology
    (lazy per-spell-id cache) and ORs it into allow_list_aggregation; contract-merge
    preserves the flag; (3) generalized plan step: slot+ctor+property
    collection_param_names, populated at both build sites; core unit test updated;
    (4) generalized fast-plan body: any collection param forces positional_ok=False
    (CALLn specializations excluded -> CALLN fallback); (5) many_only plan step:
    same field+gate+build-site wiring; (6) generalized no-overrides compiler:
    _inlinable_common_shape bails on collection params; _build_kwargs_no_overrides
    wraps count==1 collections and stops the len==1 tail unwrap; (7) many_only
    no-overrides compiler: same three fixes; (8) generalized overrides compiler:
    both emit helpers take collection_param_names and emit list-wrapped count==1
    assignments; construct wrappers + 10 call sites in _append_overrides_step_shape_source
    thread the field; shape-metadata builder requires + carries it (18-elem tuple);
    _hydrate_steps_from_rows requires + rebuilds it; runtime _build_kwargs_with_overrides
    wraps by flag; (9) schema rows: codegen_creation_schema_helpers (ir row +
    no-overrides signature row) and shared_compiler_executions (duplicate ir row,
    duplicate signature row, phase-9 injection instance rows, phase-11 injection-spec
    signature rows) all carry sorted collection_param_names / is_collection.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/artifact_processor/data/spell_injection_analysis.py:9-107
  - src/melder/aether/spellbook/spell_compiler/artifact_processor/strategies/spell_injection_processor_strategy.py:112-250
  - src/melder/aether/spellbook/spell_compiler/codegen_planner/data/spell_generalized_codegen_lane_plan.py:92-330
  - src/melder/aether/spellbook/spell_compiler/codegen_planner/data/many_only_codegen_plan.py:58-190
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/compilers/generalized_no_overrides_codegen_creation_compiler.py:552-600
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/compilers/generalized_overrides_codegen_creation_compiler.py:619-880
  IMPACT: All live-lane emission paths now wrap single-member collections.
  NEXT: Remaining edits: generalized_runtime_rows.py (row class + rebuild),
    generalized_manifest_no_overrides_compiler.py (:609-612 count arm, :747-748),
    many_only_overrides_codegen_creation_compiler.py (its kwargs/emit arms),
    CachingSystem.CURRENT_VERSION 3->4, un-xfail the two c1 tests + add a many-lane
    single-member regression test; then owner runs c1 matrix + full 3.14t tree.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-07-06T04:10:00Z
  TYPE: FACT
  CLAIM: Defect #2 slice COMPLETE, including an owner-caught regression fix. INCIDENT:
    the generalized overrides _build_shape_source_step_metadata referenced
    collection_param_names in its metadata tuple without the extraction binding (the
    original Edit hit a duplicate fragment, failed, and only the _hydrate_steps_from_rows
    copy got the line) -> NameError broke component meld-override tests on the owner's
    first run. Fixed (extraction landed at the metadata builder) and a full
    reference-vs-binding audit was run across every touched file: generalized overrides
    (33 refs), many_only overrides (24), generalized/many_only no-overrides (5 each),
    manifest no-overrides (3), both plan data files, runtime rows, phase-9 strategy/data,
    schema helpers, shared executions - every reference now has a binding, parameter, or
    row extraction in scope. Remaining slice items landed: runtime rows field + rebuild,
    manifest inline emission wraps by row truth, many_only overrides full mirror,
    CachingSystem.CURRENT_VERSION 3->4 (payload schema grew), both c1 xfails removed,
    NEW test test_c1_single_many_existence_member_injects_one_element_list (many_only
    lane), unit stubs updated (plan-core ctor x2, emission-contract _row, compilers-core
    row builders + 5 SimpleNamespace steps + NEW unit wrap test, dual-build spec stub +
    STEP_ATTRS).
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/compilers/generalized_overrides_codegen_creation_compiler.py:688-688
  - src/melder/utilities/caching_system/caching_system.py:60-69
  - tests/integration/melder/spellbook/test_spellbook_integration_resolution_break_matrix.py:592-683
  IMPACT: All lanes (solo excluded by design - no deps possible) wrap collection sockets
    by phase-3 socket truth, live + cached + overrides + fast paths.
  NEXT: Owner re-runs the component meld-override file, the c1 matrix, then the full
    3.14t tree; report verdicts. Validation status: Not run.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-07-06T18:35:00Z
  TYPE: FACT
  CLAIM: Owner's 22-failure --last-failed triage RESOLVED for this lane (post-compaction
    REONBOARD completed first). The prior audit missed that the many_only family has its
    OWN row producers that never spell "collection": (1)
    ManyOnlyCodegenCreationHelpers.build_override_step_row now emits
    collection_param_names (was the direct cause of "missing required field
    'collection_param_names' at index 0" in the many_only overrides hydrate; feeds the
    overrides step, finalize step, and manifest plan_rows); (2)
    build_no_overrides_step_signature_row now includes the sorted tuple so
    specialization cache keys change when collection-ness changes (parity with the
    generalized signature rows); (3) many_only_manifest._build_many_only_no_overrides_row
    now emits the field (its docstring promises "exactly the field set the hydration
    requires" - it was one short). Whole-src sweep confirms every
    "dependency_resolution_order" row emission now carries collection_param_names
    (4 producers, 14-file field census matches the touched set). (4) Phase-9 stub
    AttributeError fixed at both drift sites per the root-cause-first rule (test/setup
    correction, not defensive guards in owned code): the migrations injection test and
    the codegen pipeline component test now hand the strategy a spellbook stub exposing
    _spell_system_states.get_local_topology_by_id -> None (the documented
    missing-topology path). The multithreading failure was a cascade of these and should
    clear. NOT-MINE (flag only, untouched): the two conduit contract-hook tests, the
    crystallizer link-transaction test, and test_post_conjure_contract_addition_marks_
    local_collection_consumers - that last one is a REAL design question (phase-6 guard
    correctly rejects a dynamic-mode borrower whose list is legitimately empty until a
    later contract supplies members; owner must decide if the guard relaxes for
    dynamic-mode books).
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/many_only/many_only_codegen_creation_helpers.py:139-146
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/many_only/many_only_codegen_creation_helpers.py:175-194
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/many_only/manifest/many_only_manifest.py:166-190
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/many_only/compilers/many_only_overrides_codegen_creation_compiler.py:2186-2199
  - tests/unit/melder/spellbook/spell_compiler/test_spell_strategy_migrations.py:282-296
  - tests/component/melder/spellbook/spell_compiler/test_spell_codegen_pipeline_component.py:105-116
  IMPACT: Every producer/hydrator pair in both lanes is schema-coherent; the only
    remaining c1-lane failures on rerun should be not-mine or the dynamic-mode guard
    design question. INCIDENT LOG: sandbox replicas of many_only_codegen_creation_helpers
    .py, many_only_manifest.py, test_spell_strategy_migrations.py AND THIS EPIC read
    stale-truncated over bash; hosts verified intact via file-tool - these files are
    FILE-TOOL-ONLY now (same class as the prior conduit.py/mailbox incidents).
    Validation status: Not run (3.10 sandbox; owner runs 3.14t).
  NEXT: Owner reruns the --last-failed set on 3.14t; then rules on the dynamic-mode
    empty-collection guard question.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-07-06T19:20:00Z
  TYPE: MEASURE
  CLAIM: Owner-run --last-failed (12 selected): 8 failures = STALE-CACHE REPLAY OF MY
    OWN SCHEMA CHANGE, the deferred cache defect recurring within one day exactly as
    the accepted RISK predicted. Mechanism: the earlier 22-failure run executed with
    the stricter hydrates but the pre-fix many_only row producers, and WROTE those
    field-less rows into the shared default/root.melc bundle under CURRENT_VERSION=4;
    today's rerun replayed that bundle into the strict no-overrides hydrate
    (many_only_no_overrides compiler :459) for every many-existence meld (6 overrides-
    suite tests + the new c1 many-lane regression test + the SpellMap binding test).
    The live producer fix was verified on-disk before the run (manifest row :179).
    FIX LANDED: CachingSystem.CURRENT_VERSION 4->5 with version-history note -
    payload semantics changed inside version 4's lifetime, so v4 bundles must
    invalidate wholesale; no cache clearing needed. LESSON PINNED: any change to the
    phase-11 row schema MUST bump the version in the SAME edit, even mid-lane between
    owner runs. Remaining 4: post_conjure_contract_addition = the dynamic-mode
    empty-collection guard DESIGN QUESTION (phase-4/6 verdict rejects BorrowerConsumer
    whose list[IService] is empty until a later contract fills it - owner ruling
    needed: relax the guard for dynamic-mode books, or re-pin the test); 2 conduit
    contract-hook tests + 1 crystallizer link-transaction test = other lanes
    (contract/link-transaction), untouched.
  EVIDENCE:
  - src/melder/utilities/caching_system/caching_system.py:59-74
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/many_only/manifest/many_only_manifest.py:166-190
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/many_only/compilers/many_only_no_overrides_codegen_creation_compiler.py:444-462
  - tickets/epics/2026-07-05_collection_di_list_wiring_broken_epic.md:470-490
  IMPACT: Strengthens the parked cache-correctness DECISION_REQUEST (option 1 minimal
    guard): version discipline alone is fragile because it depends on the agent
    remembering to bump; a schema token owned by the codegen system would make this
    class structurally impossible. Validation status: Not run (owner runs 3.14t).
  NEXT: Owner reruns --last-failed on 3.14t (v4 bundle now cold-regenerates); expect
    the 8 cache-replay failures green, then rule on the dynamic-mode guard question.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-07-06T21:15:00Z
  TYPE: MEASURE
  CLAIM: Owner-run --last-failed CONFIRMS the cache diagnosis: all 8 replay failures
    GREEN after the v5 bump (12 selected -> 4 selected; every many_only
    overrides/no-overrides meld path now hydrates rows with collection_param_names).
    The collection-DI defect slice is fully validated on owner-run 3.14t except one
    DECISION_REQUEST below. Remaining 4 failures: (1)
    test_post_conjure_contract_addition_marks_local_collection_consumers - THIS LANE's
    guard vs dynamic-mode deferred provisioning (see DECISION_REQUEST); (2)
    test_severing_the_last_detail_evicts_the_contract_record - crystallizer test calls
    remove_spell_from_contract without an active link window; runtime canon now
    requires begin_transaction('link') for contract mutations - contract/link-
    transaction lane, not this one; (3)(4) the two conduit contract-hook unit tests -
    hook peer-resolution dispatch drift (resolve_peer fired on the reuse path;
    get_conduit_by_id called twice) - conduit contract-hook lane, not this one.
  EVIDENCE:
  - src/melder/utilities/caching_system/caching_system.py:59-74
  - tests/integration/melder/spellbook/test_spellbook_integration_overrides.py:89-613
  - tests/integration/melder/spellbook/test_spellbook_integration_resolution_break_matrix.py:655-663
  IMPACT: Exit-signal evidence for the epic's code scope is in; only the guard-policy
    ruling remains inside this lane.
  NEXT: Owner rules on the DECISION_REQUEST below.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-07-06T21:15:00Z
  TYPE: DECISION_REQUEST
  CLAIM: Dynamic-mode empty-collection policy needs an owner ruling. The collision:
    this epic's Phase-6 EmptyCollectionStrategy hard-fails conjure when a required
    collection socket has zero providers (correct for c1_zero), but
    test_post_conjure_contract_addition_marks_local_collection_consumers conjures a
    dynamic-mode borrower whose list[IService] is INTENTIONALLY empty until a later
    post-conjure contract supplies the provider - the test's whole premise is
    deferred provisioning marking consumers dirty. Both behaviors cannot hold.
    Compliant options: (1) RECOMMENDED - scope the hard-fail to non-dynamic books:
    in dynamic mode an empty required collection downgrades to a deferred/dirty mark
    (same surface the post-conjure contract-add path already marks), because
    emptiness at conjure is not final when contracts can add members later; static/
    automatic books keep the hard error. (2) Keep the guard universal and re-pin the
    test to add the contract inside the pre-conjure window (changes the feature's
    meaning: post-conjure contract adds can never satisfy a required collection).
    (3) Keep the guard universal but let the borrower declare the socket optional -
    pushes the policy onto user annotations.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/system/validation/empty_collection_strategy.py:1-1
  - tests/integration/melder/spellbook/test_spellbook_integration_post_conjure_bind_snapshot.py:353-440
  IMPACT: Option 1 preserves both the c1_zero guard win and the dynamic-mode
    contract-provisioning feature; options 2/3 narrow one of them.
  NEXT: Owner picks 1/2/3; on (1) I implement the dynamic-mode scope in the Phase-6
    strategy in this lane.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-07-06T22:30:00Z
  TYPE: DECISION
  CLAIM: Owner ruling (2026-07-06): the guard was solving the wrong problem - a
    required collection with zero providers should just SPAWN WITH AN EMPTY LIST,
    universally (beyond option 1: no mode scoping, no hard error anywhere). "If there
    is nothing in it we should just provide an empty list if it spawns why should we
    care."
  EVIDENCE:
  - tickets/epics/2026-07-05_collection_di_list_wiring_broken_epic.md:1-1
  IMPACT: Empty-required-collection semantics change from fail-fast to []-injection;
    the phase-6 strategy becomes observability-only.
  NEXT: Implementation note below.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-07-06T22:30:00Z
  TYPE: PLAN
  CLAIM: Empty-collection []-injection slice LANDED (read-first; whole chain traced
    before editing). The pre-change reality: a zero-provider collection socket died at
    THREE points - the analyzer skipped zero-target sockets (no occurrence entry), the
    plan extractors dropped empty-key params, and every emitter's count==0 arm skipped
    the kwarg (missing-arg TypeError), with solo (collection-blind) claiming the
    1-spell case. Changes: (1) phase-8 analyzer `_append_topology_dependencies`
    publishes required empty collection sockets as `dependencies[param] = []`
    (optional empties stay unpublished so ctor defaults apply; phase 8, NOT phase 3);
    (2) solo discovery declines any model whose injection shape carries a collection
    param - a spell with a collection socket is not "no deps possible", so it routes
    to the collection-aware families; (3) EmptyCollectionStrategy downgraded
    ERROR->WARNING with rewritten message/docstrings (observability only; WARNING
    never trips `_enforce_conduit_resolution_valid`); (4) plan extractors keep
    empty-key dependency-kind collection params (SpellManyOnlyCodegenPlanBuilder.
    _extract_param_keys + _extract_param_keys_no_overrides - single shared site both
    lanes delegate to - and the many_only builder's _dependency_resolution_order);
    (5) all four RUNTIME kwargs builders assign `kwargs[param] = []` in their
    count==0 arm for collection params; (6) all four EMITTED-source arms render the
    same (override-guarded emitters wrap the [] in the not-overridden guard); (7)
    manifest `row_inlinable_common_shape` keeps 0-key collection entries - its
    list-literal arm joins zero refs into `[]` (docstring re-pinned); (8) fast/CALLn +
    transient-unrolled lanes need nothing: collection steps already carry
    positional_ok=False -> CALLN, and the unrolled schema builders return None on any
    CALLN step; (9) c1_zero re-pinned: conjure succeeds, meld injects [] (renamed
    test_c1_zero_implementations_injects_empty_list); (10) CachingSystem
    CURRENT_VERSION 5->6 IN THE SAME DIFF (pinned lesson applied - occurrence rows and
    emitted bodies changed). Every edited file's HOST copy verified intact via
    file-tool at the bash-replica truncation points (replica lag now covers ~10 files;
    bash parse of edited files is unreliable, file-tool is truth).
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/spell_analyzer/strategies/spell_occurrence_graph_analyzer_strategy.py:825-841
  - src/melder/aether/spellbook/spell_compiler/codegen_planner/codegen_plan_discovery_system/strategies/solo_codegen_plan_discovery_strategy.py:33-62
  - src/melder/aether/spellbook/spell_compiler/system/validation/empty_collection_strategy.py:29-158
  - src/melder/aether/spellbook/spell_compiler/codegen_planner/data/spell_generalized_codegen_lane_plan.py:2700-2734
  - src/melder/aether/spellbook/spell_compiler/codegen_planner/data/many_only_codegen_plan.py:1202-1224
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/compilers/generalized_manifest_no_overrides_compiler.py:752-770
  - tests/integration/melder/spellbook/test_spellbook_integration_resolution_break_matrix.py:581-595
  - src/melder/utilities/caching_system/caching_system.py:59-79
  IMPACT: Post-conjure contract test's borrower now conjures ([] + WARNING) and the
    dirty-marking path under test is reachable; c1_zero asserts the new policy; all
    populated-collection behavior unchanged. Validation status: Not run (owner runs
    3.14t).
  NEXT: Owner runs the c1 matrix + the post_conjure snapshot test + full 3.14t tree.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-07-06T23:05:00Z
  TYPE: FACT
  CLAIM: Owner-run --last-failed (4 selected) after the []-injection slice: all 4 are
    stub drift against the slice's new contracts, all fixed. (1)+(2) discovery stubs
    (_ModelProbe in test_codegen_plan_discovery_core, _ProcessorStateProbe in
    test_codegen_discovery_pipeline_component) now set injection_shape=None -
    mirrors the real SpellCodegenModel default (slot ctor-defaults to None,
    verified spell_codegen_model.py:99/:154); solo discovery treats None as
    no-collections and claims. (3)+(4) test_spell_codegen_cache_rehydration_exec
    _row helper now emits "collection_param_names": () - its rows feed the
    generalized no-overrides CACHE hydrate (compiler :345 required-set), same
    producer/consumer law as the src row builders. Proactive sweep of every test
    row-builder ("creations_target_kind" dict census across tests/): also fixed
    test_generalized_specializer_wrapper _row (manifest-family row; manifest
    emitters read row["collection_param_names"]) BEFORE it failed; compilers-core,
    emission-contracts, dual-build-differential already carried the field.
    test_spell_codegen_planner_core's probe safely exits discovery before the
    injection read (existence shape None). Hosts verified at both new replica
    truncation points (discovery-component :232, specializer-wrapper :368) - lag
    only.
  EVIDENCE:
  - tests/unit/melder/spellbook/spell_compiler/test_codegen_plan_discovery_core.py:35-47
  - tests/component/melder/spellbook/spell_compiler/test_codegen_discovery_pipeline_component.py:33-46
  - tests/unit/melder/spellbook/spell_compiler/test_spell_codegen_cache_rehydration_exec.py:76-107
  - tests/unit/melder/spellbook/spell_compiler/test_generalized_specializer_wrapper.py:36-70
  IMPACT: Every known consumer of the step-row schema and the solo injection-shape
    read now has aligned producers/stubs in src AND tests. Validation status: Not
    run (owner runs 3.14t).
  NEXT: Owner reruns --last-failed, then the full tree.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-07-07T00:10:00Z
  TYPE: MEASURE
  CLAIM: DEFERRAL NO LONGER VIABLE - the cache-correctness defect now reproduces
    WITHIN a single full-tree run, after a manual cache clear (owner-run evidence,
    two runs). Mechanism (same one recorded 2026-07-06T00:45): every break-matrix
    test conjures (frame=default, name="root") -> ONE shared bundle;
    _build_conjure_cache_state classifies by spell-id SET intersection only
    (spellbook_creation_system.py:410-427) and payloads are keyed by content SHA
    alone (caching_system.py:244-263). NeedsPlugins has an identical SHA in every
    c1 test but a different resolved composition per test. Observed: (a) c1_zero
    ({NeedsPlugins} only) classified FULL HIT against an earlier test's payload ->
    manifest references a pool member that does not exist -> RuntimeError unknown
    spell_id (post-clear run: f750d115...; pre-clear run reproduced the historical
    cf958b... on b3); (b) run-order poisoning both directions - pre-clear run:
    c1_zero wrote plugins=[] and c1_single/three/mixed replayed [] (0!=1/0!=3/0!=2);
    post-clear run: c1_single wrote [PluginA] and c1_three/mixed replayed it
    (1!=3/1!=2) SILENTLY WRONG - proving subset-validation/self-heal alone cannot
    fix this ([PluginA] is a valid subset of c1_mixed's pool and still wrong).
    Cache clears cannot help: contamination is intra-run. The []-injection slice is
    NOT regressing - c1_single passed post-clear when it compiled fresh, and all
    wrong values are exact replays of sibling-test manifests.
  EVIDENCE:
  - src/melder/aether/spellbook/spellbook_creation_system.py:410-427
  - src/melder/utilities/caching_system/caching_system.py:244-263
  - tests/integration/melder/spellbook/test_spellbook_integration_resolution_break_matrix.py:581-638
  IMPACT: Correct payload reuse requires the key to carry the RESOLUTION
    COMPOSITION, not just the spell SHA. Anything less replays wrong graphs
    silently.
  NEXT: DECISION_REQUEST below.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-07-07T00:10:00Z
  TYPE: DECISION_REQUEST
  CLAIM: Cache composition-keying needs an owner go/no-go. Recommended fix (A):
    compute one pool-composition hash per conjure in _build_conjure_cache_state
    (hash over sorted live payload-eligible spell ids + the binding facts that
    feed resolution: spellframe, binding_name, existence) and key spell payloads
    by (composition_hash, spell_id) inside the bundle - CachingSystem lookup/
    upsert/cached_spell_ids gain the composition dimension; CURRENT_VERSION 6->7
    in the same diff. Correct by construction: same book composition = warm reuse
    (the real production case), any composition change = cold for that book, no
    silent cross-book replay possible. Alternative (B): store the composition
    hash inside each payload and validate at classification - same correctness,
    but pays a marshal decode per cached spell on every conjure classification.
    NOT viable (C): hydration-time self-heal on unknown ids - proven insufficient
    by c1_mixed's silent [PluginA] replay. Coordination note: fable_0's parked
    unify_cache_rehydration epic touches the same bundle machinery; (A) is
    orthogonal (keying, not emission) but the lane should be flagged.
  EVIDENCE:
  - src/melder/aether/spellbook/spellbook_creation_system.py:371-446
  - tickets/epics/2026-07-02_unify_cache_rehydration_with_live_emitters_epic.md:1-1
  IMPACT: Without (A)/(B), the c1 matrix and any suite sharing frame/conduit names
    across compositions stays permanently flaky, and production books that rebind
    replay stale graphs.
  NEXT: Owner picks A/B (or redirects); agent_0 implements in this lane on
    approval.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-07-07T01:30:00Z
  TYPE: DECISION
  CLAIM: Owner OVERRULED the cache-keying proposal: the frame/conduit-name bundle
    contract is the intended runtime design; the defect is TEST HYGIENE - the
    break-matrix reuses (default, "root") across different pool compositions, which
    real applications do not do. Directive: "fix the tests so they properly create
    new cache each time." Composition-keying (options A/B above) is WITHDRAWN as a
    lane action; the runtime cache machinery stays untouched.
  EVIDENCE:
  - tickets/epics/2026-07-05_collection_di_list_wiring_broken_epic.md:1-1
  IMPACT: Cache-correctness work exits this lane entirely; the fix is scoped to the
    test suite.
  NEXT: Per-test cache isolation in the break-matrix (note below).
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-07-07T01:30:00Z
  TYPE: PLAN
  CLAIM: Break-matrix cache isolation LANDED, mirroring the established
    test_cache_runtime_integration idiom (frame_configuration.
    with_system_cache_root_path + package-root-anchored fragment): new helpers
    _package_root() + _fresh_conjure_cache_fragment() (rmtree+mkdir of
    src/melder/__melder_cache_break_matrix__ per call - one shared label, tests run
    sequentially, no directory accumulation), and _make_spellbook() now points every
    Spellbook's frame configuration at that freshly wiped root with a docstring
    recording WHY (identical class SHAs bound into different pool compositions must
    not share a bundle). Every test now compiles from scratch and exercises its own
    cache writes in isolation; the default __melder_cache__ tree is untouched by
    this suite. MAILBOX: consumed melder_0's 2026-07-07T01:05 NOTICE - the
    attention-board truncation was their bash rewrite against a stale replica;
    file-tool-only adopted by them; my restoration verified; their 3 closure anchors
    re-added; adaptive_pgo anchor still unowned. Host of the break-matrix verified
    intact at the replica truncation point (:877). Validation status: Not run.
  EVIDENCE:
  - tests/integration/melder/spellbook/test_spellbook_integration_resolution_break_matrix.py:166-220
  - tests/integration/melder/spellbook/test_cache_runtime_integration.py:55-89
  IMPACT: c1/b3 flakiness class removed at its root for this suite; other suites
    sharing (frame, conduit-name) across compositions can adopt the same helper
    pattern if they ever flare.
  NEXT: Owner reruns the break matrix (expect c1_zero/single/three/mixed/single_many
    + b3 all green, order-independent), then the full 3.14t tree.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-07-07T02:00:00Z
  TYPE: DECISION
  CLAIM: Owner REJECTED the custom cache-root approach - it minted a NEW cache zone
    under the package root (src/melder/__melder_cache_break_matrix__), which is
    exactly the kind of repo pollution the fix was supposed to avoid, and it ignored
    the suite-wide precedent. CORRECTED implementation (landed): the junk directory
    is deleted, the helpers/imports are reverted, and _make_spellbook now simply
    disables system caching through the PUBLIC API -
    spellbook.configure_aether_frame(system_caching_enabled=False) - the same
    posture test_aether.py:1595 and the cache suite's caching_enabled=False arms
    already use. Rationale recorded in the helper docstring: this suite tests
    resolution, not the cache; caching off = every conjure compiles from scratch,
    order-independent, zero cache artifacts. FEEDBACK CAPTURED for this lane: when a
    test suite needs isolation from a runtime subsystem it is not testing, DISABLE
    the subsystem via its existing public switch; do not invent new filesystem
    zones or replicate cache-suite plumbing into unrelated suites.
  EVIDENCE:
  - tests/integration/melder/spellbook/test_spellbook_integration_resolution_break_matrix.py:166-187
  - src/melder/aether/spellbook/spellbook.py:5241-5248
  IMPACT: No new directories under src/melder; the break matrix exercises pure
    resolution; the conjure cache is exercised where it belongs (the cache suites).
    Validation status: Not run.
  NEXT: Owner reruns the break matrix, then the full 3.14t tree.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-07-07T02:40:00Z
  TYPE: DECISION
  CLAIM: Owner asked to KEEP the zero-provider guard now that the c1 flakiness is
    explained as cache/test hygiene. Clarified causality: the guard was downgraded
    for the dynamic-mode contract test (deferred provisioning), NOT for the c1
    flakiness. Reconciliation LANDED - the guard is now MODE-SCOPED:
    (1) EmptyCollectionStrategy reads the owning book's mode per spell
    (spell._spellbook._aetheric_frame_configuration.system_state, the same surface
    the phase-9 contract-override path reads; missing lookup/config resolves to
    fail-fast): AUTOMATIC books -> ERROR (conjure fails fast - original guard
    behavior restored; composition is final so the socket can never be satisfied);
    DYNAMIC books -> WARNING + [] injection (post-conjure contracts can still
    supply members). Mode-specific remediation text in each arm. (2) c1_zero
    RE-PINNED back to its original raise expectation
    (test_c1_zero_implementations_fails_conjure; its book is automatic). The
    []-injection machinery (analyzer empty-socket rows, plan extractors, emitter
    count==0 arms, solo decline) STAYS - dynamic books construct with [] until
    contracts fill the socket, and the post_conjure dirty-marking test depends on
    it. Frame config timing verified: freeze+bind happens in
    _prepare_spellbook_for_conjure BEFORE resolution phases, so phase 6 sees the
    true mode. No other tests pin the guard's severity (grep: only c1_zero's
    docstring references the strategy).
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/system/validation/empty_collection_strategy.py:30-215
  - tests/integration/melder/spellbook/test_spellbook_integration_resolution_break_matrix.py:598-607
  - src/melder/aether/aetheric_frame/aetheric_frame_configuration.py:663-672
  IMPACT: Both owner-authored expectations hold simultaneously: automatic books
    fail fast on unsatisfiable collections; dynamic books keep deferred contract
    provisioning. Validation status: Not run.
  NEXT: Owner reruns break matrix + post_conjure snapshot test + full 3.14t tree.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-07-07T02:55:00Z
  TYPE: DECISION
  CLAIM: Owner CONFIRMED the mode-scoped guard as final (briefly considered
    silencing the dynamic-mode WARNING entirely, then withdrew: "nevermind this is
    ok"). Locked behavior: AUTOMATIC -> ERROR fail-fast; DYNAMIC -> WARNING + []
    injection. No code change from the 02:40 state.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/system/validation/empty_collection_strategy.py:30-215
  IMPACT: Guard semantics are settled; lane returns to awaiting owner-run 3.14t
    verdicts.
  NEXT: Owner runs break matrix + post_conjure snapshot + full tree.
  REREAD: HELPFUL
  SCORE_0_TO_10: 7
