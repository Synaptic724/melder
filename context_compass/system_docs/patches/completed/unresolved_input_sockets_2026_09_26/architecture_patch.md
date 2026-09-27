# architecture_patch

## Metadata
- Patch ID: unresolved_input_sockets_2026_09_26
- Status: draft for owner review (no source changed)
- Owner: user (implementation: melder_0)
- Story: STORY-2026-09-26-unresolved-input-sockets
- Task: TASK-2026-09-26-implement-missing-dependency-sockets
- Created: 2026-09-26

## Patch Scope and Non-Goals
- Objective: a typed constructor parameter that no registered spell can provide stops failing conjure.
  Resolution records it as an unresolved input; a meld fills it from its override payload, or raises
  `UnresolvedInputError` naming the consumer, parameter, expected type and override key when that
  object is actually constructed. Registering a matching provider later turns it into a normal edge.
- Non-goals: changing `resolvable=False` (a Nexus discoverability feature) or `OVERRIDE_REQUIRED`;
  changing collections, `SpellMap`, `SpellContract`, PLAIN parameters or the two-candidate error;
  a per-binding declaration; Nexus publication of unresolved inputs (follow-up); type-checking supplied
  values; a strict-mode setting; the demand-driven override rewrite (design steps S2-S5).

## Changed-Components Matrix
| component | change_type | rationale | depends_on |
|---|---|---|---|
| SpellCompiler Phase 3 (local frame) | modify | zero candidates yields an UNRESOLVED_INPUT socket, not an error | none |
| DAG socket vocabulary (SocketKind) | modify | new member UNRESOLVED_INPUT | none |
| Validation (Phase 4) | modify | report unresolved inputs; cycle strategy skips them | SocketKind |
| SpellSystemStates (change watcher) | modify | watch unresolved inputs so a later provider re-resolves | SocketKind |
| Artifact processor (Phase 9 injection) + row exporters | modify | carry an "unresolved_input" param source | SocketKind |
| Codegen creation executors (all families) | modify | failure path raises UnresolvedInputError | exception |
| Custom exceptions / package root | add | UnresolvedInputError(MeldExecutionError), exported | none |
| SpellbookCreationSystem (conjure prep) | modify | after structural phases, one INFO line lists unresolved inputs | Phase 3 |
| CachingSystem | modify | generation 11 retires executors emitted without the new failure path | executors |

## Interface and Boundary Deltas
- Public, additive: `melder.UnresolvedInputError`, a subclass of `MeldExecutionError`. Code catching
  `MeldExecutionError` keeps working.
- Public behavior change (deliberate): conjure no longer raises "no DI candidate found" for a single
  typed parameter with zero providers. Six existing tests assert the old contract and are rewritten.
- Internal: `SocketKind.UNRESOLVED_INPUT` appended (existing enum values unchanged); injection param
  source kind "unresolved_input"; row exporters append (position, parameter_kind) for that kind.

## Cross-Component Invariants
- Assignment point: only Phase 3 creates UNRESOLVED_INPUT, only for `SINGLE_BY_ANNOTATION` parameters of
  a resolvable spell whose candidate search returns nothing (no resolvable provider and no
  non-resolvable definition). Every other outcome is unchanged.
- The socket keeps its normalized `dependency_key`; that key is both the expected type in messages and
  the watch key that re-resolves the consumer when a provider with the same frame key is bound.
- An unresolved input never creates a DAG edge, a dependency id or a construction step.
- Execution: the parameter is omitted unless the call supplies it, exactly like today's
  OVERRIDE_REQUIRED inputs. Supplied values pass through by identity; None and False count by presence.
- The named error is raised only on the constructor-failure path of the object that owns the socket.
  A reused (stored) object never demands its unresolved inputs. Successful melds do no extra work.

## Migration / Rollout Order
1. SocketKind member, Phase 3 assignment, injection source, exporters, watcher, validation.
2. UnresolvedInputError and the failure-path helper; wire every executor family.
3. Conjure INFO report; cache generation 11.
4. Rewrite the six old-contract tests; add regressions; run unit/component/integration on 3.14t and GIL.
5. Promote to src_architecture / src_components, refresh graph descriptors, add the release note.
6. The new exception class joins the internal-registration manifest and the packaged system documents
   change, so build assets need a rebuild; that stays a separate owner-approved step.

## Rollback Constraints
- Revert is source-only: restoring the Phase 3 raise returns the old refusal. Generation 11 caches are
  rejected by a generation-10 reader and rebuild cold, so a downgrade needs no manual cache action.

## Ticket Coverage Matrix
| patch section | ticket | validation |
|---|---|---|
| Phase 3 assignment, SocketKind | TASK-2026-09-26-implement-missing-dependency-sockets | unit: Phase 3 zero/one/two candidates |
| Watcher | same | component: dynamic world, bind provider after conjure, meld injects it |
| Injection + exporters | same | unit: rows; component: cached (hydrated) executors |
| Error + wiring | same | component: every family, root/nested, supplied/missing, reused |
| Validation + report | same | unit: warning issued; cycle strategy skips |
| Cache generation | same | integration: generation history test |

## Evidence
- tickets/tasks/2026-09-26_implement_missing_dependency_sockets_task.md (notes, tranches A-E)
- tickets/tasks/2026-09-26_trace_caller_input_conjure_strictness_regression_task.md (cause timeline)
- artifacts/missing_dependency_sockets_20260926/probe_required_today_314t.json
