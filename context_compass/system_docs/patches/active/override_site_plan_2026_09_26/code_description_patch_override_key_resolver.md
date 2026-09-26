# code_description_patch_override_key_resolver

## Metadata
- Patch ID: override_site_plan_2026_09_26
- Component: SpellCompiler and Validation Pipeline (override key resolution)
- Status: draft (S1)
- Owner: user (implementation: melder_0)
- Created: 2026-09-26T11:28:08Z
- Updated: 2026-09-26T11:28:08Z

## Trigger Justification
- New policy pipeline (key grammar, ranks, cuts, conflicts) whose result every later step compiles into
  code; the cut rule is a fixpoint and the UNIQUE count a dynamic program, both easy to get subtly wrong.

## Control-Flow Description (Pseudocode Level)
1. For each raw key in order, skip `"__args__"`, then `TargetSpec.parse(raw)`.
2. PATH: walk from the root site. At site s and segment i, look up parameter `segments[i]`; missing -> raise
   the PATH error. Last segment -> record target (s, name) with the prefix tuple of (site, param) pairs
   walked. Otherwise follow every `dependency_sites` entry of that parameter (a collection fans out); a
   parameter with no dependency sites -> raise the PATH error.
3. UNIQUE `*n`: matches = `param_index[n]`; count = sum of `path_counts[site]` over matches; 0 -> raise the
   zero error; more than 1 -> raise the "matched N sockets" error; else record the match.
4. BROADCAST `**n`: matches = `param_index[n]`; none -> raise; else record every match.
5. Positional arity N > 0: the root's first N positional-capable parameters (POSITIONAL_ONLY or
   POSITIONAL_OR_KEYWORD, in position order) become ARGS-rank targets with their `__args__` index.
6. Cut (P1): start with all candidates active; repeat until stable: targeted = targets of active candidates;
   drop every candidate one of whose prefixes is in targeted. Keys whose every candidate was dropped are
   reported in `inactive_keys`.
7. Winners: per target, the highest rank wins (ARGS 4 > PATH 3 > UNIQUE 2 > BROADCAST 1). Other distinct
   keys at the winning rank become `conflicts` entries (the first key in payload order is the winner).
8. Return `OverrideKeyResolution` (targets, winners, positional, conflicts, inactive keys).

## Edge/Error and Rollback Semantics
- Edge case 1: keys differing only in whitespace parse to the same spec; both are recorded and form an
  equal-rank conflict on their shared targets, as today's `!=` comparison does.
- Edge case 2: an inactive key is still fully validated (steps 2-4 run before step 6), matching contract
  item 3.
- Error behavior 1: errors are raised in payload order at the first invalid key; no partial result is
  returned.
- Rollback behavior: the resolver is pure; nothing to roll back.

## Invariants and Idempotency Expectations
- Invariant 1: the result is a pure function of (site graph, key tuple, arity); no store, spell or value
  is read.
- Invariant 2: every walk is bounded by key length times collection fan-out; no path list is built.
- Idempotency condition 1: resolving the same inputs twice yields equal resolutions.

## Explicit Non-Goals
- Non-goal 1: no value checks (the E1 guard is emitted by S3; S1 only reports conflicts).
- Non-goal 2: no demand, pruning or emission (S2/S3).

## Validation Focus Points
- Validation item 1: the Codex leak case (`{"p": o, "p>d>x": v}`) makes `p>d>x` inactive.
- Validation item 2: UNIQUE on a shared site reached by two paths raises "matched 2 sockets".
- Validation item 3: differential oracle parity with today's targeting for every valid and invalid key in
  the corpus, except the recorded collection PATH difference.

## Context / Handoff Summary
- What changed: resolver control flow fixed before code.
- Remaining unknowns: collection PATH coverage (see component patch).
- Next entrypoint: implementation in the S1 task.
