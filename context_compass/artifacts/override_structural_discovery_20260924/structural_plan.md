# Structural override investigation and proposed implementation sequence

Date: 2026-09-24. Lead: updater_0. Graph/compiler partner: updater_1.
Status: compact graph/codegen and native-store integration prototypes available; production remains unmodified.
Epic: tickets/epics/2026-09-24_override_execution_performance_epic.md.

## Current continuation

The owner directed both agents to continue experimenting with better alpha structures. The peer's
compact_structure_proposal.md replaces full path enumeration with physical sites and selector progress.
The lead's native_runtime_boundary.md now records actual lock/admission behavior and an integrated
compact/native-store prototype. Read those two together for the latest implementation boundary.

The current native paths exhibit a store/unique-Spell lock-order inversion. The experimental writer
protocol avoids holding container locks while waiting or constructing, and the compact claim prelude
asks only for demanded shared sites. Seven integrated cases verify native publication, reuse/purge,
contention, failure and dynamic Conduit/Space admission. Fourteen native lock controls, four protocol
controls and five admission/disposal controls qualify the underlying observations. This is an
experimental replacement seam, not a production patch or throughput result.

## What is established

The current path chooses the original construction work first and substitutes argument values later.
The retained emitter prototype makes that original work cheaper but does not remove any constructors.
Its public original-workload throughput is 41.8% shallow, 53.3% wide, 41.6% diamond and 95.3% deep
relative to normal creation. The 1.64x-4.68x ratios compare with the old override path only.

That prototype remains frozen as the instruction-cost baseline. Its code, raw samples, preparation
costs and independent ten-test review are linked through the earlier investigation tasks. The owner
has selected structural planning as the main fix.

## Evidence from the deeper investigation

| Case | Current native behavior | Required work shown by structural diagnostic |
| --- | --- | --- |
| Five many dependencies, three supplied | Six constructors including consumer | Three: the two remaining dependencies and consumer |
| Shared provider still used by unsupplied slots | Two constructors | Two: keep the shared provider and consumer |
| Collection replaced by an empty list | Constructs its member and consumer | Consumer only |
| Child constructor parameter overridden | Constructs child and consumer | Both remain |
| Whole child supplied | Constructs child and consumer | Consumer only |
| Deep left branch supplied | 511 constructors | 256 |
| Both deep root branches supplied | 511 constructors | One root |

The structural diagnostic is a direct-constructor simulation over real plan rows, not a native Meld
implementation. Eleven scenes preserve canonical manifests, reproduce closure through marshal roundtrip
and record stable source/script hashes. They also demonstrate why flat-row filtering is insufficient.

The lead ran nine separate native admission/lifecycle scenarios and three independent native alias
confirmations without invoking the graph slicer. These establish additional correctness problems:

- A nested override through the secondary path of a shared parent is accepted but ignored.
- A nested rule below an externally replaced primary path can still modify the surviving secondary path.
- Expanding all aliases and merely deduplicating the shared parent invents an extra many child.
- A reused shared provider still causes unnecessary transient descendants to be constructed and disposed.
- Full-graph Space requirements reject a Conduit request even when its only Space dependency is supplied.
- A direct missing contract rejects resolution, but the nested path can pass the SpellContract descriptor
  itself into an application constructor. Both call orders were checked.

This confirms an orchestration/representation issue, not only generated-code overhead.

The alias-aware interpreter now passes nine additional bounded cases. It fixes the static left/right
counterexamples in simulation, converges unequal-depth aliases and preserves changing values in one
prepared plan. An independent lead review adds three passing controls with distinct many parents:
five constructor sites remain distinct, separate inputs stay separate, and replacing one parent cuts
its two constructor sites. These are algorithmic checks, not measured native improvements.

The independent review also exposes two limits of the first static-alias prototype. When a parent is reused,
its descendant rules still participate in the static shared-input selection: they can cause an
equal-priority conflict or win over the input from a different path that actually needs construction.
Conditional constructor execution alone therefore does not finish the alias problem. See the
runtime-demand section below; both examples are retained in alias_review_results.json. A separate
conditional prototype now passes twenty peer cases and two independent lead reviews against these
defects. Earlier prototypes and their failing evidence remain preserved.

Evidence:
- artifacts/override_occurrence_discovery_20260924/structural_findings.md
- artifacts/override_occurrence_discovery_20260924/results.json
- artifacts/override_structural_discovery_20260924/semantics_findings.md
- artifacts/override_structural_discovery_20260924/semantics_observations.json
- artifacts/override_structural_discovery_20260924/native_alias_confirmation.json
- artifacts/override_occurrence_discovery_20260924/alias_results.json
- artifacts/override_structural_discovery_20260924/alias_review_results.json
- artifacts/override_occurrence_discovery_20260924/conditional_alias_results.json
- artifacts/override_structural_discovery_20260924/conditional_alias_review_results.json

## Recommended structure

Keep the declared graph and the ordinary plan intact. Derive an effective construction program for
the requested input shape. The required distinction is between logical paths, used to address an
argument, and construction sites, used to identify the one object construction actually needed.

```text
declared parameters + logical paths + lifetime facts
                         |
             supplied socket selection
                         |
           active aliases and input sources
                         |
       physical construction sites and reuse branches
                         |
        readiness/scope obligations for retained work
                         |
            cached generated creation program
```

For a shared Branch reached through left and right, its constructor has one Token input even when
Token is many. That Token's construction site follows the physical Branch constructor and its input
slot; it must not multiply simply because Branch has two logical aliases. Two distinct many Branch
constructors still require separate Tokens. This is construction-plan identity, not a new lifetime or
ownership mode. Existence and Creations retain their current storage/disposal responsibilities.

Collect all surviving shared incoming requests before choosing children, including aliases reached
at different depths. Choosing the first visited alias would reproduce the existing canonical-path bias.
Map logical sockets to physical constructor inputs only with that provenance preserved.

## Proposed behavior contract

1. Supplying a whole dependency terminates that edge's construction demand. Keep other surviving uses.
2. Modifying a dependency's constructor input keeps its constructor. None, False and empty collections
   are supplied values, determined by presence rather than truthiness.
3. Validate selector syntax, existence, uniqueness and precedence against declared paths. A valid
   descendant rule below a supplied ancestor becomes inactive for that path; it does not mutate the
   supplied object or contaminate a different retained alias. Invalid selectors still fail.
4. Normalize surviving alias requests to shared physical inputs. Preserve existing specificity rules;
   incompatible surviving requests for one shared constructor must fail rather than silently pick an alias
   or create multiple supposedly shared instances. Exact equality/tie diagnostics need specification.
5. Preserve hard root identity, lifecycle, capability, transaction and ownership guards. Derive demand
   requirements from the effective request; never mark the unresolved baseline globally valid merely
   because one supplied call can run.
6. A retained unresolved descriptor/provider must not silently become a Python default object. Preserve
   ordinary Python missing-argument errors for retained constructors; add no blanket argument preflight.
7. Reuse checks must precede construction needed exclusively by the reusable object. Cache the conditional
   program, not live store contents. Rules below a reused constructor need an explicit applicability
   policy before their values or priorities can contribute to another active alias. Purge and later
   recreation must keep working with the same context.
8. Keep supplied values externally owned. A graph cut does not register, purge, dispose or transfer them.

The nested-rule and shared-conflict items are recommendations for the structural contract, not claims
that current behavior already follows them. Existing root override-on-reuse refusal remains the default.
Do not silently extend this work into a general hook or existing-object redesign.

## Concrete change areas

| Area | Responsibility in the structural design |
| --- | --- |
| Phase 3 topology / Phase 5 blueprint | Preserve declaration, signature, socket and provider-readiness facts separately from execution demand. |
| Phase 8 occurrence analysis | Retain shared alias provenance instead of discarding alternate descendant context. Avoid blindly expanding all shared paths. |
| Phase 9 instance/injection/targeting | Assign construction-context identities, normalize active aliases, and combine surviving parameter sources before expanding children. |
| Phase 10 planning | Build root-demanded effective programs and explicit reusable-node construction branches; preserve the ordinary fast plan. |
| Phase 11 emitters | Generate only demanded constructors with existing error/lifetime operations. Reuse the proven normal-style call lowering. |
| Family manifests / hydration | Persist sufficient value-only alias/site/readiness data under the existing family cache lifecycle, with compatible schema rejection. |
| Meld / CreationContext | Order effective readiness and scope checks with existing admission/locks; preserve root and caller authority on both Conduit and Space doors. |

The peer report names the exact classes and methods under each area. Current phase8_11 Codegen IR
contains summaries, not a complete reusable adjacency graph; do not assume it already solves storage.
Basic slices round-trip existing manifest rows, but full alias-aware planning needs additional facts.

## Performance and cache boundaries

Perform graph selection/grouping when preparing a structural shape, not by traversing the graph on
every Meld. Reuse existing root context invalidation, base signatures and door epochs. Values remain
per call. New source specialization must include exact physical operand/cut placement; target counts
alone are insufficient, particularly in the generalized source cache.

Keep ordinary no-override many execution on its existing direct-call route. Shared reuse is a live
condition and retains its existing store/Spell locking. No new global cache owner, supplied-object
identity cache or Creations scope-policy layer is proposed.

The alias proof also establishes that the resolved logical socket set alone is not enough for
specialization. Broadcast plus exact input and two exact inputs can address the same sockets but
produce different shared winners/conflicts. Preserve specificity or the equivalent complete guarded
source-selection layout in the cached program's identity.

Constructor reductions are established only in the diagnostic. No native structural speedup is
measured yet, and avoiding constructors does not guarantee a win for every tiny graph after dispatch
cost. Qualification must report both latency and percentage of normal throughput, plus constructor counts.

## Runtime demand is also alias demand

The independent counterexample has a reusable CachedParent and a separate FreshParent, both declared
to request SharedService. CachedParent may have been created earlier with an external service;
reusing it does not prove SharedService is present in the runtime store.

This state is now confirmed through native public APIs: meld CachedParent with an external service,
purge SharedService, then observe CachedParent still live and returned by reference while the shared
service store is empty. The existing eager path creates an unused tracked service before substitution;
purge removes that entry. The subsequent alias evaluations remain interpreter observations.

```text
root.cached -> reused CachedParent -> old externally supplied service
root.fresh  -> new FreshParent     -> new shared service needed now
```

With cached>service>value=21 and fresh>service>value=91, the first static prototype raises before checking
CachedParent reuse. With **value=91 plus cached>service>value=21, it skips CachedParent construction
but constructs FreshParent's service with 21. These are prototype limitations against the proposed
path-inactivity rule; they are not new assertions about native Melder behavior.

Recommendation: retain a conditional demand program per input shape. A reusable constructor's
descendant aliases contribute only on its construction branch. Cache all necessary rule provenance
and potential input choices; evaluate active priority/conflicts from current demand before invoking
the affected constructor. Do not cache the chosen live-store outcome or rebuild the graph for every
call. Simple many-only graphs do not need these reuse conditions.

The remaining production question is how these conditions interact with the existing store and Spell
locks. A read taken before execution cannot promise that purge or another constructor will not change
the store before consumption. Qualification must use native admission/locking, not pass an arbitrary
dictionary of reuse outcomes as the diagnostic does. Root override-on-reuse refusal remains separate.

An alternative contract would explicitly reject descendant overrides below reused parents. That is
a user-visible policy choice; silently allowing an inactive path to customize another one is not the
recommended behavior. The owner has not selected that alternative or a new nested-reuse policy yet.

The conditional proof now implements the recommended behavior in a separate interpreter. It preserves
all potentially active ranked inputs and default dependency edges, guarded by constructor demand.
For the equal-rank example, one prepared program produces 91 with the parent reused, conflicts when
both parents are fresh, then produces 91 when reuse returns. Mixed specificity similarly alternates
91/21/91. The lead verifies both transitions using a native-produced retained parent.

Fallback edges matter as much as ranked inputs. If the only rule supplying Token lies below a reused
parent, the other active path needs a normally constructed Token again. The twenty-case peer suite
checks this for an object, None and False, alongside static cuts, unequal depths and distinct many
parents. Prepared metadata and the canonical native manifests remain unchanged. No new family-cache
hydration, native lock protocol or generated-code performance has been qualified by this interpreter.

## Next implementation preparation, in order

1. Fix the semantic regression matrix: supplied edges, active shared aliases, equal-rank conflicts,
   collections, ordinary missing arguments, descriptor readiness, root scopes and cached-parent reuse.
2. Bounded alias-demand proof is now available: static aliases, ghost Token, unequal depths, distinct
   many parents, conditional ranking and restored default edges. Retain the earlier 6-to-3/511-to-1
   construction evidence; use these artifacts as tests of the production data contract.
3. Define the production data contract and admission/readiness boundary. Validate it on both doors,
   with baseline validity preserved independently from call-specific readiness.
4. Implement the compiler/data/hydration changes through those contracts, retaining existing stores,
   invalidation and the no-override fast path. Then integrate the earlier emitter improvement.
5. Qualify cold/warm/cache-loaded behavior, every supported Existence, concurrency/revalidation/purge,
   selector semantics, construction/disposal counts and ordinary-path performance before release.

Before step 3 is considered settled, resolve the observed hook-order boundary: current root pre-hooks
run before invalid-selector rejection, while activation/post do not. Moving preparation can change
that failure ordering. Direct versus nested child-hook behavior is also catalogued separately.
Positional input binding must distinguish caller-provided arguments from synthesized DI keywords;
the known duplicate-argument issue must not be hidden as a performance improvement.

No production override code, public API, version or build assets have changed in this investigation.
The epic stays active for the structural work. Earlier prototype code/results remain preserved.
