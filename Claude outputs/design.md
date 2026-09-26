# Override execution and caller inputs: one demand-driven design

Date: 2026-09-26. Author: melder_0. Task: tickets/tasks/2026-09-26_design_override_and_caller_input_execution_task.md.
Epic: EPIC-2026-09-24-override-execution-performance. Status: design proposal; production unchanged.
Alternative to: artifacts/override_structural_discovery_20260924/joint_alpha_proposal.md.

## Recommendation

Resolve an override payload once per key shape into a static plan over the physical construction
graph Melder already builds, then lower that plan top-down: a consumer asks for each dependency,
a shared dependency is looked up in its store first, and only a miss builds its subtree under the
slot guard shipped on 2026-09-25. The empty shape is the ordinary meld, so one lowering serves both.
Caller-supplied constructor inputs become a socket kind that needs no provider at conjure and is
checked per shape at meld.

Three properties follow, and they are the difference from joint alpha:
- No new lock protocol. Slot guards already give an acyclic, consumer-first lock order.
- Operand choice is a pure function of the key shape. Live store state decides only whether a
  constructor runs, never which value it receives, so results do not depend on thread timing.
- No path enumeration anywhere. Selectors resolve by walking named edges or counting paths.

## What current source does

| # | Behavior | Evidence |
| --- | --- | --- |
| 1 | The physical graph exists: shared spells expand once; instance keys are (id, None) for shared sites and per-path for many sites. | spell_occurrence_graph_analyzer_strategy.py:719-785; spell_occurrence_instance_processor_strategy.py:127-215 |
| 2 | Plans run bottom-up: Kahn order, providers first, one step per instance key. Reuse of a shared step is checked after its dependencies were built. | spell_occurrence_order_processor_strategy.py:103-171; spell_generalized_codegen_lane_plan.py:1500-1600 |
| 3 | Probe: meld Root(many) -> Middle(unique) -> Leaf(many) twice builds Leaf twice. No override involved. | current_behavior_results_314t.json |
| 4 | Probe: supplying a and b to Consumer(a, b, c) still builds A and B, then passes the supplied objects. | same |
| 5 | Phase-5 socket overlay walks every logical path; targeting then keys every socket ref. Runs at every conjure. | spell_system_root_blueprint_builder.py:435-500; spell_override_targeting_processor_strategy.py:51-110 |
| 6 | Probe: binary unique chain, 13 sites -> 8,190 root socket refs, 0.08 s conjure; 15 sites -> 32,766 refs, 0.31 s. | current_behavior_results_314t.json |
| 7 | An unbound required type fails conjure in Phase 3 ("no DI candidate"). OVERRIDE_REQUIRED is assigned only when a non-resolvable definition was selected. | compiler_phase_3.py:435-513, 693-768; probe case 3 |
| 8 | Slot guards: build locks nest consumer-first along the DAG; store locks are leaves. 12 lock-order cases pass. | creations.py:Creations.slot_guard; completed slot-guard task |

Contract items 1-8 as melder_1 verified them stay the reference for current override behavior:
tickets/tasks/completed/2026-09-25_verify_override_behavior_contract_task.md.

## Joint alpha: what to keep, what to drop

Keep: physical sites instead of logical paths; a supplied edge removes demand; reuse must precede
exclusive construction; one lowering for ordinary and override calls; value-only rows in the cache.

Drop, with reasons:
- **The claim protocol** (non-blocking claims, release-before-wait, retry, claim records). It exists to
  break the store/Spell inversion. Slot guards removed that inversion with an acyclic order, and the
  protocol's open items (claim lifetime, retirement, reentrancy, fairness) disappear with it.
- **Live-state operand selection.** Joint alpha lets a rule count only if its path is constructed now.
  A shared descendant then gets its value from whichever thread builds it first, depending on whether
  that thread saw an ancestor already stored. It is also what forces the claim prelude, guarded ranked
  candidates, fallback edges and a cache keyed by the complete selector layout.
- **The selector-state machine.** It avoids path explosion, but a PATH selector names one walk from the
  root and UNIQUE only needs a path count; neither needs enumeration or per-prefix state.
- It does not cover caller-supplied inputs, which is the consumer blocker since 09-24.

## The design

### 1. Physical graph rows

One row per site: spell id, existence, store operation, and per parameter: name, kind, position,
collection flag, default policy and socket kind (DI edge, PLAIN, CALLER_INPUT, CONTRACT). A DI edge
points at child sites. A many child belongs to its physical parent's parameter; shared sites merge.
These rows replace the Phase-5 path overlay and `targets_by_spec`, so conjure cost becomes
O(sites + edges) instead of O(logical paths), for every user, with or without overrides.

### 2. Shape plan, built once per key shape

The shape is the set of normalized override keys (plus positional arity). The first meld with a new
shape builds its plan; later melds with the same shape reuse it.

1. Parse keys with the existing TargetSpec parser and PATH > UNIQUE > BROADCAST precedence.
2. Validate against the declared graph, before any cut (contract item 3 unchanged):
   - PATH: walk named edges from the root; at least one match.
   - UNIQUE: exactly one declared logical path. Count paths by DP over sites (paths(child) +=
     paths(parent)), which gives today's count (a shared parameter reached twice counts twice).
   - BROADCAST: at least one site with that parameter name.
3. Cuts: a key that names a whole dependency replaces that edge with an operand. A PATH rule whose
   walk crosses a cut edge is inert (contract item 4, option (a), decided statically).
4. Demand: sites reachable from the root through uncut edges. Only these can run.
5. Operands: each live rule attaches to its physical (site, parameter). The highest rank wins. Two
   live PATH rules reaching one physical input through different aliases are a shape error; no
   values are compared (replaces the item-5 equality question).
6. Obligations per demanded site: a CALLER_INPUT with no operand, or an unresolved contract
   descriptor with no provider, lowers to a named error in that site's build branch.
7. Scope: `requires_spellspace_request` is computed over demanded sites, so a supplied Space-scoped
   dependency no longer makes a Conduit meld refuse.

### 3. Top-down lowering

Dependencies are built on demand, depth-first in parameter order, before their consumer. A shared site
has an inline hit path and an out-of-line miss function. Out-of-line is required: CPython rejects
deeply nested `with` blocks ("too many statically nested blocks"; 21 compile, 40 fail on 3.14.7).

```python
# Shape {"a"}: Consumer(a, b, c) with b many and c unique_per_conduit (store `s`).
def execute(ov, s):
    b = B()
    c = s._creations.get(ID_C, MISSING)
    if c is MISSING:
        c = _build_C(s)                  # C's subtree runs only on a miss
    return Consumer(a=ov["a"], b=b, c=c)

def _build_C(s):
    with (s._slot_guards.get(ID_C) or s.slot_guard(ID_C)):
        c = s._creations.get(ID_C, MISSING)
        if c is MISSING:
            c = C(d=D())                 # construct under the build lock
            s._creations[ID_C] = c       # existing publication path
    return c
```

- Reuse short-circuit falls out of the order: a stored shared site never builds its subtree. This
  also removes the ordinary-meld waste in row 3.
- A shared site that has operands from the shape and is found stored keeps today's refusal
  (MeldExecutionError), like an existing root with overrides (contract item 6).
- Many-only graphs are trees, so the lowering is straight-line code with no guards.
- The existing doors (admission, gate tickets, root reuse and its refusal) stay as they are; the
  lowering replaces only what runs inside them.
- Operands are literal-key reads from the call's override dict; nothing is interpreted per call.

### 4. Caller-supplied inputs

- Declare per binding, e.g. `bind(Task, existence="many", caller_inputs=("work",))`; the name is a
  decision. Validate names against the real signature. Part of binding identity, descriptions,
  crystallizer records and replay (workflows_0's list, findings.md:99-135).
- Phase 3 skips provider search for declared parameters and records a socket with no targets and no
  reference ids. Undeclared parameters keep today's "no DI candidate" failure.
- At meld, the shape plan either binds the input to an operand or lowers a named error into the
  site's build branch: "Task.work is supplied by the caller: meld(Task, override={'work': ...})".
  It fires only when that site is constructed, so a reused site never demands it, and a hit costs
  nothing. No per-call preflight is added.
- Option: parameters annotated with a type Melder refuses to bind (Conduit, Package) could be
  classified as caller inputs automatically, since no provider can ever exist for them.

### 5. Concurrency

No new mechanism. Miss functions take the site's slot guard (Spell lock for unique) and recheck
under it. Guards nest consumer-first along DAG edges, the order the 09-25 fix proved acyclic. Purge
already takes the same guard. No constructor is replayed and nothing retries. The decision a miss
makes is made under the guard that publishes its result, so no settled-claim concept is needed.

### 6. Caching

Shape plans and their executors live on the CreationContext, keyed by shape and bounded (e.g. 64,
least recently used), and are dropped when the context is replaced (revalidation, epoch change).
Purge keeps them: a plan holds no store state. A full-hit conjure skips phases 8-11, so the
persisted creation cache must carry the physical rows for shapes to be built. Needs generation 11.

## Failure and edge semantics

| Case | Result |
| --- | --- |
| Whole dependency supplied | Edge cut; the child runs only if another uncut edge demands it |
| Dependency parameter overridden | Child constructed with that operand (item 2; None/False by presence) |
| Rule below a supplied dependency | Inert, decided statically (item 4 (a)) |
| Rule below a shared parent that is reused at runtime | That subtree does not run; see D2 |
| Two live PATH rules on one physical input | Shape error at first meld of that shape (D3) |
| Invalid, unmatched or ambiguous selector | Shape error, checked against declarations (item 3) |
| Root or targeted shared site already stored | MeldExecutionError, unchanged (item 6) |
| Caller input missing on a constructed site | Named MeldExecutionError, raised in its build branch |
| Unresolved descriptor on a constructed site | Error; the descriptor object is never passed |
| Constructor raises | Current family error wrapping; no replay; published dependencies keep lifecycle (item 8) |

Hook ordering: shape resolution sits where targeting runs today, after root pre-hooks, so the
selector-error ordering structural_plan.md flagged is preserved.

## Decisions for the owner

- **D1 Caller-input declaration.** A per-binding keyword naming parameters (recommended), plus
  optional automatic classification of parameters typed with unbindable Melder kernel types.
- **D2 Reuse never changes operands.** A live rule configures the physical object it reaches. If a
  shared descendant is built for another consumer while the rule's own parent was reused, it still
  gets that value. Recommended, because the alternative makes a shared object's configuration depend
  on thread timing. This narrows the item-4 choice to supplied (static) cuts.
- **D3 Equal-rank aliases are an error.** Two PATH rules reaching one physical input fail regardless
  of values. Replaces item 5 (c) and removes the arbitrary-equality question.
- **D4 Construction order and count.** Constructors run depth-first in parameter order (dependencies
  still first), and stored shared sites no longer build throwaway subtrees in ordinary melds. Fewer
  constructors and disposals is observable; so is the changed sibling order.

## Implementation sequence

1. **Caller inputs (S1).** Declaration and the Phase-3 socket, executed by today's override
   executors; a missing input keeps today's missing-argument failure until S4 names it.
   Small, independent, and it unblocks CommandOps now.
2. **Physical rows and selector resolution (S2).** Replace the Phase-5 overlay and `targets_by_spec`;
   resolve PATH/UNIQUE/BROADCAST by walk, DP count and scan. Conjure becomes linear.
3. **Top-down lowering for the empty shape (S3).** Ordinary melds first, with out-of-line shared
   misses under slot guards. Gate: ordinary warm/cold parity measured on 3.14t and GIL.
4. **Shape plans (S4).** Cuts, operands, obligations and per-shape scope through the same lowering.
   Retire the separate override compilers and targeting artifacts. Cache generation 11.
5. **Qualification (S5).** melder_1's matrix updated for D2/D3, the 12 lock-order cases, contract
   regressions, constructor/disposal counts, then cold/warm/hydrated performance.

## Not verified

- No performance of this lowering is measured. Parity with ordinary melds is a gate, not a claim.
- many_only, solo and manifest families were not re-read in full; S3/S4 assume their tactics can
  lower from the same plan.
- PATH selectors into multi-provider collections, positional/variadic sockets, methods, lambdas and
  existing objects must keep today's semantics; not re-traced here.
- Nested child-hook behavior stays as it is today; not redesigned.
- Optional contract sockets (`Optional[...]` with a SpellContract default) may legitimately resolve
  to None; the unresolved-descriptor error must respect that. Not traced here.
- Shape count per context in real applications is unknown; the bound is a starting point.
