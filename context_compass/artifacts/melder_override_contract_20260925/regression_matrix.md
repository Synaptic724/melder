# Regression matrix: joint alpha behavior contract items 1-8

Date: 2026-09-25. Author: melder_1. Lead: melder_0.
Task: tickets/tasks/2026-09-25_verify_override_behavior_contract_task.md.
Status: draft test plan for owner review. No test code; no src/tests changes.

## How to read this matrix

- **Current** is behavior verified from source in this task. Every source range is in the task
  `## Notes`; this file does not restate evidence it cannot cite.
- **Proposed** is `joint_alpha_proposal.md` "Required behavior contract" items 1-8.
- **Family** pins the compilation family, because behavior differs between them:
  `G` generalized, `M` many_only, `S` solo (root-only). Rows without a family apply to all three.
- **Rank** follows the testing policy: `S` system contract, `A` behavioral unit contract,
  `D` regression reproduction.
- **Status**: `READY` (expected outcome fixed), `DECISION` (awaits an owner decision request),
  `CONFLICT` (proposal text disagrees with source), `FUTURE` (needs the new protocol to exist).
- Assert outcomes through public behavior: return values, raised type plus `__cause__`, constructor
  call counters in fixtures, store contents via public reuse-only lookup, disposal counts at cleanup.

## Item 1 - a supplied whole dependency removes its construction demand

- **R1a** (G, S-rank, READY). `Consumer(child: Child)`, Child `many` with a disposal method.
  Call with `override={"child": ext}`.
  - Current: Child is constructed and registered, then unused; cleanup disposes it.
  - Proposed: Child never constructed or registered; Consumer receives `ext` by identity.
  - Assert: Child ctor count 0, Consumer count 1, `ext` absent from every store, zero disposals.
- **R1b** (G, A-rank, READY). Shared provider with a surviving use: `Consumer(a: Svc, h: Holder)`,
  `Holder(svc: Svc)`, Svc `unique`. Supply `a`.
  - Current: Svc constructed.  Proposed: Svc constructed exactly once, for Holder only.
  - Assert: `h.svc` is the stored Svc; `consumer.a is ext`; Svc count 1.
- **R1c** (M, A-rank, READY). Five many dependencies, three supplied.
  - Current: six constructors.  Proposed: three (two remaining dependencies plus the consumer).
- **R1d** (G, A-rank, READY). Collection parameter supplied as `[]`.
  - Current: member provider constructed, consumer receives `[]`.  Proposed: consumer only.
- **R1e** (G, A-rank, READY). Deep 511-site tree: left root branch supplied, then both branches.
  - Current: 511 constructors each.  Proposed: 256, then 1. Count test only; no timing claim.

## Item 2 - a parameter override keeps its owner; presence decides

- **R2a** (all families, A-rank, READY). `Child(value)` with `override={"child>value": v}` for each
  `v` in `None`, `False`, `0`, `""`, `[]`.
  - Current and proposed agree: Child is constructed and receives `v` exactly. Front-door
    normalization keeps falsey values; only an empty payload `{}` means "no override".
  - Guards against a future truthiness shortcut in the new program.
- **R2b** (all families, A-rank, READY). `override={}` on an existing shared root.
  - Current: treated as no override, so reuse succeeds with no refusal. Pin this.

## Item 3 - selector syntax and matches are validated against declarations

- **R3a** (A-rank, READY). Keys `""`, `"  "`, `"*"`, `"**"`.
  - Current: `ValueError` from parsing, re-raised as `MeldExecutionError("Failed to apply
    overrides.")` with the ValueError as `__cause__`. Raised after root pre-cast hooks.
- **R3b** (A-rank, READY). Unmatched path below a supplied ancestor:
  `{"child": ext, "child>missing": 1}`.
  - Current and proposed: error, even though `child` is supplied. Validation is independent of cuts.
- **R3c** (G, A-rank, READY). `*token` where one shared physical `token` param is reached by two
  logical paths.
  - Current and proposed: error "matched 2 sockets"; `*name` counts declared logical paths.
- **R3d** (A-rank, CONFIRM). `"a>>b"` and `">a"`.
  - Current: empty segments are dropped, so these parse as `a>b` and `a`. Proposed item 3 says
    "validate syntax". The owner should confirm whether empty segments are errors.

## Item 4 - rules below a supplied or reused constructor

- **R4a** (G, A-rank, DECISION). `{"child": ext, "child>value": 5}` (valid nested rule).
  - Current: a discarded Child is built with `value=5`; `ext` is untouched; no error.
  - Proposed option (a): no construction, rule inactive, no error. Option (b): explicit error.
- **R4b** (G, S-rank, DECISION). Reused shared parent: CachedParent (unique) already exists;
  `cached>service>value=21` while FreshParent also needs SharedService.
  - Current: an existing shared step with targeted overrides raises MeldExecutionError.
  - Proposed (a): the rule is inactive on the reuse branch; FreshParent's service uses its own inputs.
- **R4c** (G, S-rank, DECISION). A rule through path A must not reach a shared descendant that
  only path B still uses, once A is supplied.
  - Current: a shared step receives every target for its spell, from every path.
  - Proposed (a): no cross-path effect.

## Item 5 - aliases normalize onto physical inputs; specificity is preserved

- **R5a** (G, A-rank, READY). Two PATH aliases to one shared physical param, same value.
  - Current and proposed: accepted; one construction receives the value.
- **R5b** (G, A-rank, READY). Two PATH aliases to one shared physical param, different values.
  - Current: no error. The alias with the highest `param_path_id` silently wins.
  - Proposed: reject incompatible active equal-rank inputs. The error type needs pinning.
- **R5c** (G, A-rank, DECISION). Equal-rank values whose `__ne__` raises, or whose comparison
  result has no truth value (array-like).
  - Current: the conflict check calls `existing != value`, so user code decides or raises.
  - Proposed: owner chooses identity, `!=`, or identity-then-scalar equality.
- **R5d** (G, A-rank, READY). `"a>x": 1` (PATH) plus `"**x": 2` (BROADCAST), where `a>x` and
  `b>x` are aliases of one shared physical param.
  - Current: each logical socket keeps its own winner, then the shared step writes by param name in
    `param_path_id` order. BROADCAST can therefore override PATH when `b>x` has the higher id.
    This is derived from the three code paths in the task notes; a probe should confirm it.
  - Proposed: PATH wins (specificity preserved across aliases).

## Item 6 - root capability, lifecycle and override-on-reuse refusal stay

- **R6a** (READY). Existing root on each shared route (`unique`, `unique_per_conduit`,
  `unique_per_spell_space`, lineage, cluster) plus any override: MeldExecutionError and zero
  constructors. Current matches.
- **R6b** (READY). Existing-creation root plus any override: always MeldExecutionError.
- **R6c** (READY). Non-resolvable root plus override: MeldExecutionError before override
  normalization, lazy validation and hooks.
- **R6d** (READY). `many` root plus override: constructs; no refusal path exists.

## Item 7 - unresolved descriptors fail honestly; Python errors stay ordinary

- **R7a** (per family, CONFLICT). Retained constructor missing a required argument.
  - Current: G and M raise MeldExecutionError("Error invoking spell ...") with the TypeError as
    `__cause__`; S lets the TypeError propagate unwrapped. The proposal wording assumes an ordinary
    Python error. Assert per family until the owner unifies it.
- **R7b** (G, S-rank, READY). A nested consumer whose SpellContract provider is missing.
  - Current: the parameter has no Phase 9 source, so it is omitted and the SpellContract descriptor
    default reaches the constructor. Proposed: fail with a clear error; type to pin.
- **R7c** (UNKNOWN). A supplied call on a graph with an incomplete baseline must not mark that
  baseline valid. Current behavior is not yet read from source.

## Item 8 - retry only before user construction; never replay constructors

- **R8a** (G, A-rank, READY). `A(b: B)`, where B registers and then A's constructor raises.
  - Current and proposed: B stays registered in its store, no constructor runs twice, and the
    error propagates. Pin current lifecycle behavior.
- **R8b** (FUTURE). Contended claim causes a retry before any user constructor or value comparison.
  Only testable after the claim protocol exists.

## Cross-cutting pins

- **H1** (READY). Root pre-cast hook fires before an invalid-selector rejection; activation and
  post hooks do not fire. The new preparation stage must keep or deliberately change this order.
- **X1** (READY). Supplied objects are never registered, purged, disposed or transferred.
  Current: override values only enter kwargs.

## Not covered here

Native lock order and writer coordination belong to melder_0's task. Performance claims are out of
scope. Validation of this matrix against a running interpreter: Not run.
