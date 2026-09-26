# Joint alpha proposal: select construction work before executing it

Date: 2026-09-24. Lead: updater_0. Compiler partner: updater_1.
Epic: tickets/epics/2026-09-24_override_execution_performance_epic.md.
Status: concrete experimental proposal; production Melder is unchanged.

## Recommendation

Use one compact construction graph for ordinary and override execution. Prepare the input shape
before choosing constructors, then emit direct calls for the work still required. Shared lifetimes
need a native claim step that settles reuse before activating their constructor dependencies.

This addresses both costs established in the investigation: executing unnecessary constructors and
interpreting/rebuilding too much metadata on each call. The earlier emitter-only optimization remains
preserved as an instruction-cost baseline, not the selected architectural endpoint.

## Proposed responsibility split

| Layer | Owns |
| --- | --- |
| Bind / structural phases | Declaration, identity, default precedence, capability and provider facts |
| Compact base graph | Physical constructor sites, parameter edges, shared incoming provenance and readiness data |
| Prepared request program | Selector matching, precedence, supplied operands, conditional demand and fallback edges |
| Meld / CreationContext | Scope routing, admission, validity, current-context checks and execution orchestration |
| Native creation claims | Stable per-store/binding writer coordination and settled hit/miss decisions |
| Generated body | Direct constructor calls, selected operands and publication of actual created objects |
| Creations | Authoritative object/disposal registries and retirement; no scope-discovery policy |

Application references and constructors remain runtime bindings. Persist value-only graph/program
data through the existing cache family and invalidation lifecycle. Do not store caller values,
reuse snapshots or a winning alias chosen from one transient store state in the shape cache.

```text
declarations -> compact physical graph -> prepared selector/input shape
                                             |
                                admitted demand/claim prelude
                                             |
                           settled reuse + guarded constructor work
                                             |
                            direct calls -> native publication
```

## What the experiments now prove

- Compact interpretation, generated execution and both hydrated forms agree across forty-two
  scenario evaluations against the earlier expanded conditional oracle.
- Five dependencies with three supplied generate and execute three constructors including the
  consumer. Deep ordinary/left-supplied/both-supplied controls execute 511/256/1 constructors.
- A synthetic depth-64 shared graph represents 2^64 logical leaf paths with 65 physical sites and
  selector states. This is compact-representation evidence, not native conjure performance.
- The generated claim prelude requests only demanded shared sites, preserves falsey hits, waits
  for all incoming consumers and propagates contention without running constructors/comparisons.
- Native lock/admission experiments establish the actual writer and ticket boundaries. They also
  expose an existing store/unique-Spell lock-order inversion that the new protocol must eliminate.
- Experimental generated execution now publishes into real native Creations stores and supports
  reuse, purge/recreate, competing publication, failure release and dynamic Conduit/Space admission.
- The direct-publication variant retains those seven integration cases and adds a 511-site control:
  one constructor executes with base-catalog iteration forbidden. Earlier adapter files remain intact.

These are bounded semantic and mechanism proofs. They are not a production optimization, full-suite
qualification or native throughput result. Constructor reductions alone are not a speed measurement.

## Required behavior contract

1. A supplied whole dependency removes its construction demand, preserving any other live uses.
2. A constructor-parameter override keeps its owner constructor. Falsey and None values count by presence.
3. Validate selector syntax/matches against declarations, even when another rule cuts an ancestor.
4. Recommended: a valid rule below a supplied or reused constructor is inactive for that path and
   cannot influence a different active path. The prototypes implement this explicit policy.
5. Normalize surviving aliases onto physical inputs; preserve specificity and reject incompatible
   active equal-rank inputs. Arbitrary-object equality behavior still needs its precise native contract.
6. Keep root capability, lifecycle, scope authority and existing root override-on-reuse refusal.
7. An actually retained unresolved descriptor must fail honestly. Keep ordinary Python missing-argument
   errors; do not add a blanket argument validator or globally validate an incomplete baseline.
8. Retry claim selection only before user construction and value comparisons. Never replay constructors
   after a failure. Existing published dependencies retain their established lifecycle behavior.

Existing-object registration remains unique-only. This does not reopen its broader ownership redesign
or introduce a new public init={} API. Hook standardization and the separate Mojo/compiler-IR epic
remain outside scope.

## Native writer change is essential

Current normal-root per-conduit/lineage doors can hold the container store lock while requesting a
unique child's Spell lock. Purge takes the child's Spell lock then that store. The controlled native
probe demonstrates the wait cycle while preventing the final blocking acquisition from hanging.

The experiment instead claims a specific store/binding without holding the container lock while
waiting. If a claim is contested, all earlier claims are released before waiting and retrying the
prelude. Store mutexes cover observation/publication/removal only. User constructors and disposal
run outside those container mutexes; disposal also runs after the entry claim is released.

All writers must adopt one protocol: ordinary creation, overridden creation and purge. Updating only
the override lane would leave incompatible coordination and the original inversion in place.
Production must define claim-record lifetime, retirement, reentrancy and fairness explicitly.

## Implementation sequence

1. Lock the semantic regression matrix above and preserve the existing failure reproductions.
2. Define the native claim/publish/retire contract and implement it coherently across root wrappers,
   dependency emitters and Creations. Keep scope decisions in Meld/native routing.
3. Build complete compact graph rows upstream from declarations/resolved providers. Include signature
   position/kind, collections, existing objects and incoming contract/positional payload provenance.
   Remove upstream full-path inventory where it would otherwise retain the original scaling cost.
4. Prepare selector states and guarded operands/default edges under the existing base context identity.
   Share constructor argument lowering between ordinary and override plans.
5. Emit the demand/claim prelude and direct constructors. Bind constructors cold and pass call-local
   publication context; never rebuild wrappers over every base site on a pruned warm call.
6. Integrate native admission, retained-provider readiness, hooks/error timing and cache hydration.
   Preserve current invalidation ownership and qualify context replacement while calls are parked.
7. Run supported lifetime/signature/contract/purge/concurrency regressions, then measure public native
   cold/warm/hydrated paths and ordinary controls. Update release material and build assets only after
   the approved implementation and final source/document changes.

The first integration adapter intentionally omits full validation, all callable/signature forms,
many-disposal publication, transfer and general hook handling. The direct variant also duplicates
cold compilation while borrowing its predecessor's setup. Those are explicit production tasks,
not hidden claims of completed support.

## Reading and evidence

Start with these two task-owned reports, then their cited source ranges:
- artifacts/override_occurrence_discovery_20260924/compact_structure_proposal.md
- artifacts/override_structural_discovery_20260924/native_runtime_boundary.md

Compiler implementation and checks:
- artifacts/override_occurrence_discovery_20260924/compact_alias_plan.py
- artifacts/override_occurrence_discovery_20260924/compact_alias_emitter.py
- artifacts/override_occurrence_discovery_20260924/compact_alias_probe.py
- artifacts/override_occurrence_discovery_20260924/compact_alias_results.json
- artifacts/override_occurrence_discovery_20260924/compact_claim_prelude.py
- artifacts/override_occurrence_discovery_20260924/compact_claim_prelude_results.json

Native/store integration and checks:
- artifacts/override_structural_discovery_20260924/native_lock_probe.py
- artifacts/override_structural_discovery_20260924/native_lock_results.json
- artifacts/override_structural_discovery_20260924/entry_claim_probe.py
- artifacts/override_structural_discovery_20260924/entry_claim_results.json
- artifacts/override_structural_discovery_20260924/native_admission_probe.py
- artifacts/override_structural_discovery_20260924/native_admission_results.json
- artifacts/override_structural_discovery_20260924/native_compact_adapter.py
- artifacts/override_structural_discovery_20260924/native_compact_probe.py
- artifacts/override_structural_discovery_20260924/native_compact_results.json
- artifacts/override_structural_discovery_20260924/native_compact_direct_adapter.py
- artifacts/override_structural_discovery_20260924/native_compact_direct_probe.py
- artifacts/override_structural_discovery_20260924/native_compact_direct_results.json

The old emission-only prototype, static alias counterexamples and conditional proofs are preserved
under their original task artifact directories. No production source, version or build assets were
changed by this joint investigation.
