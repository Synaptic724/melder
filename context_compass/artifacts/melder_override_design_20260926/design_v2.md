# Override execution: structural design v2

Date: 2026-09-26. Author: melder_0. Status: for owner review; production unchanged.
Task: tickets/tasks/2026-09-26_design_override_and_caller_input_execution_task.md.
Epic: EPIC-2026-09-24-override-execution-performance.
Replaces: design.md sections "The design" onward. design.md D1 is settled by the shipped UNRESOLVED_INPUT
socket; its D2 is P3 below; its D3 is withdrawn (item 5 (c) stays); its D4 is B2 below.
Evidence: ticket notes 2026-09-26T10:27Z to 11:02Z, capture_v2_0254_314t/, perf_0254_314t/, and the
Codex artifacts under override_structural_discovery_20260924/ and override_occurrence_discovery_20260924/.

## 1. The answer

Today an override meld runs one fixed step list that builds every instance in the root's graph, then
swaps the supplied values in at run time. The compiler reduces the targets to per-step counts before it
emits code, so the generated executor cannot know which parameter is supplied and cannot skip its
dependency. The override executor is also an interpreted twin of a lowering that normal melds already
do well: with no keys at all (`override=()`) it runs at about 20% of normal speed.

Design v2 changes that structurally, in four parts:

1. **One site graph per root.** Built at conjure from rows Phase 9 already produces: one site per
   instance key (a shared spell is one site), with every constructor parameter and its operand source.
   No logical-path enumeration.
2. **One plan per override key set.** Compiled on first use and cached on the root's context. Key
   parsing, key validation, static cuts and operand placement happen once, at compile time. Supplied
   values are never inspected (owner: trust the user, fail hard).
3. **One lowering for normal and override melds.** A normal meld is the plan for the empty key set.
   Only demanded sites are emitted. Supplied values are read by literal key (`ov["a"]`). A shared site is
   an inline store read plus an out-of-line miss function, and its children are built only inside that
   miss.
4. **No new concurrency protocol.** Shared misses use the slot guards shipped on 2026-09-25, with the
   existing recheck. Warm hits stay one lock-free dict read.

Per call, an override meld becomes `plans.get(tuple(ov))` plus one call. Supplied branches are never
built, and ordinary melds stop building children of shared objects that are already stored.

## 2. What is wrong today

Every row below is source- or probe-verified on 0.2.54 plus today's source (3.14.7t, VM copy).

| # | Symptom | Cause | Ticket note |
| --- | --- | --- | --- |
| 1 | Supplied dependencies are still constructed (A for {"a"}, X and the S lookup for {"s"}, L for {"l"}). | Phase 10 has one step list per root shared by every key set; the emitter writes one block per row; the finalizer passes target counts, not sockets. | 10:43:37Z, 10:58:17Z |
| 2 | An override meld with no keys runs at 19.7-23.2% of normal. | The override body is interpreted: `param_name != 'a'` compares, kwargs dicts, an `instance_results` dict, KeyError guards. | 09:09:11Z, 10:58:17Z |
| 3 | Per-key cost on top: wide graph with 8 root keys runs at 8.1% of normal. | Targeting re-derives the key set's meaning from the values on every call and keys executors by a rebuilt socket shape. | 09:00:20Z |
| 4 | A warm ordinary meld builds the children of a stored shared object (X under S, Leaf under Middle). | Providers-first Kahn order: a shared step's reuse check runs after its dependencies were built. | 00:19:24Z, 10:58:17Z |
| 5 | Semantic defects: a rule on a secondary alias is ignored (91 -> 13); a rule under a supplied primary path leaks into the surviving alias; a nested missing contract passes the descriptor; a supplied Space-scoped dependency is refused on the Conduit door. | Logical-path targeting over a physical graph. | 10:32:04Z |
| 6 | Root positional overrides fail on DI-injected parameters ("got multiple values for argument 'a'"). | The executor passes `*args` plus the dependency kwargs for the same parameters. | 11:00:39Z |
| 7 | Conjure cost grows with logical paths (binary shared chain of 15 sites: 32,766 socket refs, 0.31 s). | The Phase-5 overlay and the targeting section enumerate every path. | 00:17:13Z |
| 8 | A PATH through a collection keeps only the last member (UNKNOWN whether any test covers it). | Collection members share a path id and targeting stores one ref per path string. | 11:02:24Z |

## 3. Decisions this design rests on

| Id | Decision | Source |
| --- | --- | --- |
| O1 | Structural fix: supplied dependencies are not constructed. The common override is a plain reference passed to the root constructor, so the design centers on it; nested paths, `*`/`**` selectors and aliased shared descendants are outliers that must be correct but are not tuned first. | Owner, 10:40:10Z |
| O2 | No validation of supplied values (type, shape, readiness). A wrong object fails wherever the user's code fails. | Owner, 10:47:11Z |
| P1 | A rule below a supplied dependency is inactive. | Contract item 4 (a); both designs |
| P2 | A rule that targets a shared site which is already stored raises today's error. The shared-root refusal stays. | melder_0 reading, 10:40:10Z; to confirm (Q1) |
| P3 | Operands depend only on the key set. A rule below a reused parent stays active for a shared descendant that another live path builds. | melder_0 reading, 10:40:10Z; to confirm (Q1) |
| E1 | Equal-rank conflicts: identity first, `==` only for plain scalars. | Contract item 5 (c) |
| K1 | Key names are validated once per key set, when its plan is compiled (as today, where targeting validates keys before execution). | Proposed 10:47:11Z; to confirm (Q2) |

## 4. The model

### 4.1 Site graph (per root, built at conjure)

The graph is a view over data Phase 9 already fits:

- **Sites.** One per instance key: many spells get one site per occurrence path, shared spells one site
  keyed `(spell_id, None)`. Source: the instance processor.
- **Parameter table per site.** Every constructor parameter from the Phase-3 local topology, in signature
  order: name, position, parameter kind, socket kind (NORMAL, SPELL_CONTRACT, OVERRIDE_REQUIRED,
  UNRESOLVED_INPUT), collection flag. PLAIN parameters with defaults are included because they are
  targetable today (`{"timeout": 9}` works).
- **Operand source per parameter.** Dependency sites (more than one for a collection), contract payload
  value, unresolved input, override-required input, or plain default. Source: the injection processor's
  `SpellInjectionParamSource` rows.
- **Store routing per site.** Existence, creations target kind and lock hint, exactly as the generalized
  plan steps carry them today.
- **Two small indexes.** Parameter name -> list of (site, param) for `*` and `**` keys; and a logical
  path count per site (how many root paths reach it), computed once by dynamic programming over the DAG.
  The count preserves today's UNIQUE rule ("matched 2 sockets; expected exactly one") without listing
  paths.

Size is O(sites + edges). It replaces the targeting section, whose size is O(logical paths).

### 4.2 Plan for one key set (compiled once, on first use)

Input: the payload's key tuple, `tuple(ov)`. Steps:

1. **Parse** each key with today's grammar (`TargetSpec.parse`): `a` or `a>b>c` is a PATH of parameter
   names from the root, `*n` is UNIQUE, `**n` is BROADCAST. `__args__` is the positional payload.
2. **Resolve targets** without enumerating paths:
   - PATH: walk from the root site one parameter at a time, following that parameter's dependency sites
     (all members for a collection). A missing parameter raises today's "No sockets found for override
     path" error. Validation walks through cut ancestors too (contract item 3).
   - UNIQUE: look up the name index; the sum of path counts must be exactly 1, otherwise today's errors.
   - BROADCAST: look up the name index; no match raises today's error.
3. **Rank** each (site, param): PATH 3 > UNIQUE 2 > BROADCAST 1. Two different keys of equal rank on one
   operand emit a conflict guard (E1). That guard is the only per-call check in the design.
4. **Cut (P1).** Apply winners top-down from the root. A PATH key whose walk passes through a parameter
   that already has a winning override is inactive.
5. **Demand.** From the root: a parameter with an override or a contract payload value needs nothing
   below it; a dependency parameter demands its site(s). Undemanded sites are not emitted.
6. **Unresolved inputs.** An unresolved or override-required input with no key on a demanded site is known
   now. The plan raises `UnresolvedInputError` at the earliest point that site is certain to be built:
   the top of the plan when it is unconditionally demanded, otherwise inside the shared miss that builds
   it. This replaces the interim failure-path hook `UnresolvedInputError.from_failed_construction`.
7. **P2 marks.** A demanded shared site with any winning override raises today's "spell instance that
   already exists" error in its hit branch. A shared root raises "root spell that already exists" in its
   hit branch whenever a payload is present.
8. **Emit** (section 5) and compile through the existing executor code and factory caches.

A key set that fails validation raises today's `MeldExecutionError("Failed to apply overrides.")`,
chained from the `RuntimeError`. It is not cached.

### 4.3 Operand precedence

Override > contract payload value > dependency, as today. `__args__` of length N supplies the root's
first N positional parameters in signature order and cuts their dependencies. Extra positional values
are passed through and fail in the constructor, as today.

## 5. Lowering: one emitter for normal and override melds

Rules:

- **L1. Each demanded site is evaluated once per call**, at the shallowest point that covers all its
  demands: top level if any demand is unconditional, otherwise inside the shared miss that demands it.
  Values reach miss functions as arguments. A site demanded only from misses of two different shared
  parents gets a per-call cell so the second demand sees this call's value (emitted only in such graphs).
- **L2. Many sites are inline**, emitted after their operands, called positionally where the signature
  allows, as today's normal many-only lowering does.
- **L3. Shared sites are an inline hit plus an out-of-line miss function.** The miss holds the existing
  slot guard (or the Spell lock for `unique`) across recheck, children, construction and publication.
  Out-of-line misses keep block nesting bounded: CPython 3.14.7 compiled 21 nested `with` blocks and
  rejected 40 in the 2026-09-26T00:19Z probe.
- **L4. Supplied operands are literal reads**: `ov["a"]`, `args[0]`. No store read and no registration
  of a supplied object, which today's substitution does not register either.
- **L5. Errors**: constructor failures keep `_raise_meld_construction_error`; unresolved inputs per 4.2.6;
  P2 in hit branches.
- **L6. Normal lane**: the plan for the empty key set fills today's `_no_overrides_executor`,
  `_no_overrides_instance_executor` and fast-door slots.

The examples omit the per-call `try/except` wrappers after example A; the emitted code keeps them.

### A. Root key, all-many graph (the common case)

`Root(a: A, b: B)`, all `many`, `meld(Root, override={"a": obj})`.

Today (`002_many_shallow_override_a.py`, 95 lines, abridged):

```python
instance_0 = plan_step_0.spell.spell()              # A: built, then discarded
instance_1 = plan_step_1.spell.spell()              # B
single_override_socket_2 = override_targets_2[0]
single_override_value_2 = override_map[single_override_socket_2]
kwargs_2 = {}
if single_override_socket_2.param_name != 'a':
    kwargs_2['a'] = instance_results[(A_ID, 1)]
if single_override_socket_2.param_name != 'b':
    kwargs_2['b'] = instance_results[(B_ID, 2)]
kwargs_2[single_override_socket_2.param_name] = single_override_value_2
instance_2 = plan_step_2.spell.spell(**kwargs_2)
```

v2, key set `("a",)`:

```python
def _plan(meld, ov):
    try:
        v1 = t1()                                   # B
    except Exception as exc:
        _raise_meld_construction_error(spell_1, exc, (), 0)
    try:
        v2 = t2(ov["a"], v1)                        # Root; A is never constructed
    except Exception as exc:
        _raise_meld_construction_error(spell_2, exc, (), 2)
    return v2
```

This is the normal lowering today (`000_many_shallow_normal.py`) minus one site, plus one dict read.

### B. Ordinary meld with a shared dependency (empty key set)

`Root(a: A, s: S)`, `S(x: X)`; S is `unique_per_conduit`, the rest `many`.

Today (`003_gen_mixed_normal_cold.py`) builds X first, then checks S's store, so a warm meld builds X
and drops it. v2:

```python
def _plan(meld):
    v_a = t_a()
    c_s = meld._conduit_creations
    v_s = c_s._creations.get(sid_s)                 # warm: one lock-free read
    if v_s is None:
        v_s = _miss_s(meld, c_s)
    return t_root(a=v_a, s=v_s)

def _miss_s(meld, c_s):
    with (c_s._slot_guards.get(sid_s) or c_s.slot_guard(sid_s)):
        v_s = c_s._creations.get(sid_s)
        if v_s is None:
            v_x = t_x()                             # X exists only when S is built
            v_s = t_s(x=v_x)
            c_s._creations[sid_s] = v_s             # plus disposal registration, as today
    return v_s
```

### C. Supplied shared dependency at the root

Same graph, `override={"s": obj}`. Today S's store is read and X is built, then `s` is substituted.

```python
def _plan(meld, ov):
    v_a = t_a()
    return t_root(a=v_a, s=ov["s"])                 # S and X are never visited
```

### D. Rule on a shared site's own parameter (outlier; P2)

Same graph, `override={"s>x": obj}`.

```python
def _plan(meld, ov):
    v_a = t_a()
    c_s = meld._conduit_creations
    if c_s._creations.get(sid_s) is not None:
        _raise_override_on_existing_instance(...)  # today's message
    return t_root(a=v_a, s=_miss_s_x(meld, c_s, ov))

def _miss_s_x(meld, c_s, ov):
    with (c_s._slot_guards.get(sid_s) or c_s.slot_guard(sid_s)):
        if c_s._creations.get(sid_s) is not None:
            _raise_override_on_existing_instance(...)
        v_s = t_s(x=ov["s>x"])                      # X is cut
        c_s._creations[sid_s] = v_s
    return v_s
```

### E. Rule below a reused parent (outlier; P3)

`Root(p: P, q: Q)`, `P(d: D)`, `Q(d: D)`, `D(x: X)`; P and D shared, Q and X many.
`override={"p>d>x": obj}`. D is demanded unconditionally (through Q), so L1 evaluates it at top level.

```python
def _plan(meld, ov):
    v_d = c_d._creations.get(sid_d)
    if v_d is not None:
        _raise_override_on_existing_instance(...)  # P2: D carries a winning override
    v_d = _miss_d(meld, c_d, ov)                    # x = ov["p>d>x"], whether or not P is stored
    v_p = c_p._creations.get(sid_p)
    if v_p is None:
        v_p = _miss_p(meld, c_p, v_d)               # a new P gets this call's D
    return t_root(p=v_p, q=t_q(d=v_d))
```

Under joint alpha the rule would be inactive whenever P is already stored, so D's value would depend on
this call's reuse outcome; that dependency is what requires its claim prelude. Here D's operands are fixed
when the plan is compiled.

### F. Broadcast (outlier)

`override={"**logger": lg}` resolves once to every (site, "logger") pair. Many sites read `ov["**logger"]`.
A shared site among them gets a P2 hit branch, which is today's behavior (a broadcast is a targeted
override on that site).

### G. Unresolved input

`Root(a: A, t: Task)`, `Task(work: Package)` with Package unregistered. Today A is built, Task's
constructor raises `TypeError`, and the failure path converts it to `UnresolvedInputError`.

```python
def _plan(meld):                                    # empty key set
    _raise_unresolved_input(spell_task, ("work",))  # decided at compile; nothing is constructed

def _plan(meld, ov):                                # key set ("t>work",)
    return t_root(a=t_a(), t=t_task(work=ov["t>work"]))
```

### H. Root positional payload

`Root(a: A, b: B)`, `meld(Root, override=(obj,))`, normalized to `{"__args__": [obj]}`. Today this raises
"got multiple values for argument 'a'".

```python
def _plan(meld, ov):                                # key set ("__args__",)
    args = ov["__args__"]
    if len(args) != 1:
        return _plan_for_arity(meld, ov, args)      # other arities compile on first use
    return t_root(args[0], t_b())
```

## 6. Runtime dispatch and per-call cost

The context's override slot becomes:

```python
def execute_with_overrides(meld, ov):
    keys = tuple(ov)
    plan = plans.get(keys)
    if plan is None:
        plan = compile_plan(keys)                   # validates keys; failures are not cached
    return plan(meld, ov)
```

- Per call: one tuple of k interned strings, one dict read, one call. Gone: payload splitting,
  targeting, socket maps, value-identity caches, the socket-shape executor cache.
- Different insertion orders of the same keys are separate entries with identical plans. They share the
  compiled code object through the existing process-wide caches.
- `plans` is owned by the root's override runtime and is cleaned with its `CreationContext`, per the
  module-scope rule (no module-level caches). A FIFO cap bounds key sets generated at run time.
- A stored mutation override (`spell._mutation_override`) takes the same dispatcher.
- The per-call overhead is UNKNOWN until measured; section 14 sets the targets.

## 7. Concurrency

- No new locks. A shared miss holds that site's slot guard (an RLock), or the Spell lock for `unique`,
  across recheck, children, construction and publication. The store lock stays a leaf.
- Nested holds go consumer before provider along DAG edges. That is one global partial order, so two
  plan executions cannot wait on each other in a cycle; a same-thread re-entrant meld re-acquires an
  RLock it holds. This realizes the documented invariant "build locks follow the acyclic dependency graph
  consumer-first".
- Warm hits are one lock-free dict read, unchanged.
- Why no claim protocol: joint alpha must settle every reuse outcome before choosing operands, because
  its operands depend on reuse. Under P3 operands depend only on the key set, so the recheck under the
  guard is enough.
- Cost: a cold shared build now holds its guard while its children are built. Warm paths are unaffected.
  Listed as R2.

## 8. Caching and invalidation

- **Disk (.melc).** Each family manifest's override section drops the path-expanded `targets_by_spec`
  and `specificity_by_spec` and gains the site graph's parameter tables, name index and path counts. The
  site rows themselves are today's step rows. Cache generation 12 ("site_plan_override_lowering");
  older bundles cold-reset through the existing admission check. fable_0's replayability gate
  (`build_package` returning None) is unchanged.
- **In process.** Plans are compiled lazily per key set, as executors are per shape today. Emitted source
  is shared across spells through `executor_code_cache` and `executor_factory_cache`.
- **Invalidation.** Plans live on the context's override runtime. Anything that replaces the context
  (recompile, notch, a later bind that resolves an unresolved input) discards them through the existing
  context-identity and door-epoch machinery. No new invalidation surface.

## 9. Error order, hooks and modes

Failure order for one call: (1) payload shape (`TypeError` from meld normalization); (2) key validation on
the first compile of the key set; (3) the equal-rank conflict guard, if emitted; (4) unresolved inputs
known unconditionally (plan top); (5) at each site: P2 in hit branches, unresolved inputs in misses,
constructor errors.

- Hooks: unchanged. Only the root's hooks run in meld; the hooks lane keeps the `(instance, created)`
  door.
- Dynamic mode: the CreationGate ticket in `CreationContext` is unchanged.
- SpellSpace door: uses the same executors. The Space-scoped supplied-dependency refusal (row 5) should
  disappear because a supplied site is never visited; to be verified in S3.

## 10. What changes, phase by phase

| Phase / area | Change | Files |
| --- | --- | --- |
| 5 | None in S1-S4. S5 retires the per-path socket overlay once its three other readers are resolved (Phase-6 socket_ref_sanity_strategy, the Phase-8 occurrence analyzer, shared_compiler_executions). | spell_system_root_blueprint_builder.py and those readers |
| 8 | None. | - |
| 9 | Replace the override-targeting processor with a site-graph processor (parameter tables, name index, path counts). | spell_override_targeting_processor_strategy.py, spell_override_targeting_analysis.py -> new site-graph strategy and analysis |
| 10 | Step rows stay. The separate overrides plan variant becomes unnecessary: one step table per root. Decided in S2. | many_only_codegen_plan.py, spell_generalized_codegen_lane_plan.py |
| 11 | One shared site-plan lowering for normal and override melds, used by solo, many_only and generalized. Retire the override emitters and the targeting runtime (about 8.1k lines today). S2 decides whether the shared lowering replaces or extends the three normal emitters. | new shared_assets module; retire many_only_overrides (2817), generalized_overrides (3075), generalized_manifest_overrides_runtime (659), solo_overrides (328), both targeting artifacts (2 x 427), both overrides steps (210, 199); rework both finalize steps' override runtimes |
| Runtime | `CreationContext` slots and the meld doors unchanged. `UnresolvedInputError.from_failed_construction` retired; the three families' `_raise_meld_construction_error` lose that branch. | creation_context.py (none), unresolved_input_error.py, family compilers |
| Cache | Generation 12; three family manifests. | caching_system.py, *_manifest.py, *_creation_cache.py |

## 11. Owner-visible behavior changes

- **B1.** Supplied dependencies, and everything only they needed, are not constructed. (The goal.) This
  includes a supplied shared dependency that today is built and stored as a side effect of the call.
- **B2.** Ordinary melds do not build children of a stored shared object, and cold builds construct
  consumer-first, so constructor call order changes. (design.md D4.)
- **B3.** A rule on a secondary alias applies; a rule under a supplied path no longer leaks into another
  alias. (Fixes the Codex defects.)
- **B4.** P3: a rule below a reused parent still applies to the shared descendant built through another
  path.
- **B5.** A root positional payload over DI-injected parameters works instead of raising.
- **B6.** `UnresolvedInputError` is raised before anything under that consumer is constructed. Same
  message.
- **B7.** A PATH through a collection parameter applies to every member (today: the last member only).
- **B8.** `override=()` and other empty payloads run at normal speed. The shared-root refusal is unchanged.

Unchanged: the key grammar, the bad-key errors and messages, the P2 messages, supplied objects never
registered, no value checks.

## 12. Joint alpha comparison

| Aspect | Joint alpha | v2 |
| --- | --- | --- |
| Graph | Compact physical sites plus selector states | Same sites; selectors resolved by walks, a name index and path counts |
| Operand choice | Conditional on this call's reuse outcomes | Fixed per key set (P3) |
| Concurrency | Consumer-first claim prelude: per-entry claims held for the whole call, release-all and retry up to 32 | Existing slot guards and recheck; warm hits lock-free |
| Emission | Straight-line direct calls, literal raw-key reads | Same, plus consumer-first miss functions |
| Ordinary melds | Shares the graph | Same lowering; also removes the ordinary child waste |
| Rule on a stored shared site | Silently inactive | Today's error (P2) |
| Evidence | 42 scenario evaluations and adapters; no throughput measured | Captures and probes on current source; measurement plan in section 14 |

Both keep: physical sites, PATH > UNIQUE > BROADCAST, static cuts (P1), validation under cut ancestors,
item 5 (c), the root refusal, no constructor replay, and no value checks.

## 13. Build order

Each step is system-impacting, so each opens a patch lane (architecture, component and code-description
patches for the lowering and its concurrency) before code.

1. **S1 Site graph and key resolver** (Phase 9). No runtime change. Gate: a differential oracle against
   today's targeting over every key form, UNIQUE counts included, on the regression corpus.
2. **S2 Shared lowering for the normal lane** (empty key set). Gate: identical results; constructor counts
   differ only as B2 predicts; full suites on 3.14t and GIL; normal throughput at or above today; cache
   generation 12.
3. **S3 Key-set plans and the dispatcher** for all three families; retire the override emitters and the
   targeting runtime. Gate: melder_1's regression matrix, the Codex scenario corpus (B3 cases flip
   deliberately), and the section 14 targets.
4. **S4 Unresolved inputs decided in the plan**; retire the failure-path hook.
5. **S5 Retire the Phase-5 path overlay** after reading its three other readers; conjure becomes linear.
6. **S6 Qualification**: canonical docs, graph descriptors, assets, release note.

## 14. Measurement and verification

Prototype results for E1-E4 (2026-09-26, 3.14t and GIL): prototype_results.md. They cover the root-key
center and `unique_per_conduit` shared sites; the list of uncovered shapes is in that file.

- Throughput: the existing experiment `test_melder_creation_overrides_performance.py` (shallow, wide,
  diamond, deep; normal, root keys, 8 wide keys, empty tuple) on 3.14t and GIL. Targets to agree with the
  owner: root-key overrides at 90% or more of normal for the same demanded work; `override=()` equal to
  normal within noise; 8 wide keys at 80% or more.
- Construction: the epic's examples (5 dependencies with 3 supplied -> 2 plus the consumer; deep graph
  with both branches supplied -> 1 of 511) and the capture graphs in this directory.
- Conjure: the binary shared chain at 13 and 15 sites, before and after S5.
- Locks: the 2026-09-25 slot-guard regression cases plus a new nested-miss contention case.
- Semantics: melder_1's regression matrix and the re-run Codex probes, with B3 flips recorded.

## 15. Unknowns and risks

- **U1.** How today's normal lowering orders a contract payload against a dependency on the same
  parameter. Read before S2.
- **U2.** Whether any test covers a PATH through a collection (B7).
- **U3.** Whether the three other readers of the Phase-5 overlay need logical paths (S5).
- **U4.** Carried from the contract story: nested unresolved contract, item-7 per-family error wording,
  the R5d probe, R7c.
- **R1.** Shared miss functions call nested misses, so Python recursion depth equals the depth of the
  longest shared chain. Pathological chains near the recursion limit (about 1000) would need an iterative
  form.
- **R2.** A cold shared build holds its guard while its children are built.
- **R3.** Key sets generated at run time: bounded by the FIFO cap on `plans`.
- **R4.** B2 changes constructor order; code that depends on construction order sees it.
- **R5.** The prototype's deep normal meld is 2-5% slower than today's (cause UNKNOWN; S2 parity gate).

## 16. Decisions requested

- **Q1.** Confirm P2 (keep today's error for a rule on a stored shared site) and P3 (operands fixed per
  key set; no claim protocol).
- **Q2.** Confirm K1: key names validated once per key set, no value checks.
- **Q3.** Accept B2: ordinary melds stop building children of stored shared objects, and cold-build
  constructor order changes.
- **Q4.** Accept B5 (root positional payloads) and B7 (collection fan-out).
- **Q5.** Approve the build order and open the S1 patch lane.
