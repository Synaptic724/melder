# architecture_patch

## Metadata
- Patch ID: crystal_analysis_rewalk_2026_11_16
- Status: implemented at 0.2.8302; deltas merged into src_components, src_architecture, tests_components and the
  source graph
- Owner: Mark (accountable); melder_0 (synaptic_python_developer) authors and implements
- Ticket: https://github.com/Synaptic724/melder/issues/327
- Created: 2026-11-16T12:16:00Z
- Updated: 2026-11-16T12:35:00Z

## Patch Scope and Non-Goals
- Objective: a bind with the crystallizer active stops paying for installed packages and for repeated per-edge work.
  Two changes, decided by the owner on 2026-11-16 (#327 DECISION note): (A) an environment wins over any user
  source root in custody classification; (B) one analysis pass resolves each distinct module's path once and
  matches its custody once.
- Non-goals: no reuse between analyses (fix C was not taken; the analyzer stays "current on every analysis"); no
  change to the record's keys or shape; no distribution provenance for descent-off leaves (review D3, Note 19 -
  a separate question); no change to `analyze_payload`; no MelderOps change.

## Changed-Components Matrix
| component | change_type | rationale | depends_on |
|---|---|---|---|
| crystal_analysis custody (`UserSourceCustodyStrategy`) | modify | a path in an environment is never user source | none |
| crystal_analysis analyzer (`CrystalAnalyzer`) | modify | passes environment roots to user custody; per-pass dedup | custody |
| persistence record version (`RecordVersion`) | modify | record-version note for the classification change | none |

## Interface and Boundary Deltas
- `UserSourceCustodyStrategy.__init__` gains keyword `environment_root_paths: Tuple[Path, ...] = ()`; `matches`
  returns False for a path under one of them or inside a `site-packages`/`dist-packages` directory.
- `CrystalAnalyzer.resolve_environment_root_paths(site_package_root_paths)` (new public static): the given site
  roots plus the interpreter's `sys.prefix`, `sys.base_prefix` and `sys.exec_prefix`, resolved and deduplicated.
- `CrystalAnalyzer.__init__` builds the default user custody with those environment roots; signature unchanged.
- `RecordVersion.CURRENT` 5.0.0 -> 5.0.1 (PATCH: no shape change, read by 5.0.0 code; the gate stays major 5).
- No change to `SpellCrystal`, `Crystallizer`, the result's describe() keys, or any public entry point.

## Cross-Component Invariants
- Custody stays first-match in priority order (synthetic, user_source, site_package, unknown); A narrows what
  user_source claims, so an environment module falls to site_package (site root or path text) or unknown.
- Every `analyze_spell_root` pass is live: the per-pass memo is reset when a pass starts and never outlives the
  analyzer; two passes over an unchanged world resolve and classify independently.
- A pass's result is identical with and without B for the same environment (B removes repeated questions only).

## Migration and Rollout Order
1. Failing-first pins: environment rule (strategy and analyzer), per-pass dedup counts, record version 5.0.1.
2. Custody: `UserSourceCustodyStrategy` environment roots and directory-name rule.
3. Analyzer: `resolve_environment_root_paths`, wiring, per-pass memo in `_walk_module_dependencies`/`_match_custody`.
4. Record version 5.0.1 and its history comment; update the characterization tests on purpose.
5. Docs (docstrings, system docs, graph descriptors), release note, notch 0.2.8302, rebuild last.

## Rollback Strategy
- Rollback trigger: a restore, preflight or MutationResearch path that depended on venv packages being user source.
- Rollback steps: revert the custody rule (A) independently of B; B carries no recorded state.
- Post-rollback verification: the custody characterization tests return to the 2026-10-10 expectations.

## Validation Expectations and Evidence Plan
- A: a module under a nested venv's site-packages classifies `site_package`, unfingerprinted, under the project root.
- A: sys prefixes are environment roots; a `site-packages`/`dist-packages` directory is never user source.
- B: one pass calls `resolve_module_path` and the custody chain once per distinct (module name, module object).
- B: a second pass, on a fresh or the same analyzer, asks again.
- Suites: tests/unit, tests/component and tests/integration under melder/crystallizer, GIL off; the MelderOps test
  re-timed against this build.

## Ticket Coverage Map
- Epic: none
- Story: none
- Tasks: #327

## Unknowns and Decision Requests
- UNKNOWN: the MelderOps configure time after A + B. Measured instead: 50 MelderOps module roots, warm, from 3.94 s
  to 0.147 s per analysis on average (789 to 173 targets). The configure itself fails earlier on any Melder since
  0.2.8300 (a class lookup reaches only a spell bound bare), so MelderOps re-times it after adapting.
- DECISION_REQUEST: none open; A rule, B and the record-version note decided 2026-11-16.

## Context / Handoff Summary
- What changed: fixes A and B and the record-version note are implemented at 0.2.8302 as specified here, with the
  pins listed under Validation; the durable deltas are merged into the canonical system docs and the graph.
- What remains: the MelderOps re-timing and the owner's acceptance on #327.
- Next entrypoint: component_patch_crystal_analysis.md.
