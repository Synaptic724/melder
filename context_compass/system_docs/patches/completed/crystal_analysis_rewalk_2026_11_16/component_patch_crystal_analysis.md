# component_patch_crystal_analysis

## Metadata
- Patch ID: crystal_analysis_rewalk_2026_11_16
- Component: crystal_analysis (custody strategies and `CrystalAnalyzer`), with the `RecordVersion` note
- Status: implemented at 0.2.8302; merged into the canonical system docs
- Owner: Mark (accountable); melder_0 (synaptic_python_developer)
- Created: 2026-11-16T12:16:00Z
- Updated: 2026-11-16T12:35:00Z

## Component Purpose and Boundary
- Current boundary: the analyzer walks one spell's module world per pass, classifying each module by the first
  custody strategy that claims it; user source claims any path under a user root.
- Target boundary: unchanged ownership. User source claims a path under a user root only when the path is outside
  every environment; the analyzer reuses answers within one pass only.

## Before/After Behavior Summary
- Before: `with_defaults()` makes the working directory the user root, so a `.venv` inside the project is user
  source - walked whatever the descent setting, fingerprinted, and retained when retention is on. Each import edge
  resolves its target's path and runs the custody chain again (about three `Path.resolve` calls per edge).
- After: a path under an interpreter site root, under `sys.prefix`/`sys.base_prefix`/`sys.exec_prefix`, or inside a
  directory named `site-packages` or `dist-packages` is never user source; it falls to `site_package` (a site root
  or the path-text fallback) or to `unknown`. Each distinct module is resolved and classified once per pass.

## Interface Deltas
- Inputs: `UserSourceCustodyStrategy(user_root_paths, *, environment_root_paths=())`; the analyzer supplies
  `resolve_environment_root_paths(site_package_root_paths)`.
- Outputs: new records list environment modules as `site_package` (or `unknown`) leaves with no fingerprint and
  no retained text; `record_version` 5.0.1. Result keys unchanged.
- Error semantics: unchanged; the environment checks are pure path comparisons and raise nothing.

## State and Lifecycle Deltas
- Owned state changes: `CrystalAnalyzer` owns two per-pass dicts (module path by name and object; matched custody
  by name, object and path), each entry holding its module object so an id cannot be reused within the pass.
- Lifecycle/cleanup changes: both dicts are cleared when `analyze_spell_root` starts and deleted by `cleanup()`
  after the strategies are cleaned. `UserSourceCustodyStrategy.cleanup()` deletes its environment roots too.

## Failure Mode Deltas
- New failure mode: a project whose root is itself the interpreter prefix (a venv created in the project directory)
  has no user source under it; documented as the owner's "environment wins" rule.
- Removed failure mode: third-party packages in a project venv fingerprinted, retained and walked as user source;
  per-bind cost proportional to every import edge of the world.
- Changed failure mode: none.

## Dependency and Ordering Constraints
1. The custody priority order is unchanged; only `UserSourceCustodyStrategy.matches` narrows.
2. The per-pass memo is keyed on the inputs `matches` and `resolve_module_path` are documented to depend on, so a
   memo hit returns what a fresh call would within the same pass.

## Validation Expectations
- Test/validation item: strategy-level environment rule (site root, prefix, directory names, user root outside).
- Test/validation item: analyzer-level nested-venv world under the project root (characterization tests updated on
  purpose to the owner's answer).
- Test/validation item: call-count pins for B (once per distinct module per pass; again on the next pass).
- Evidence target: tests/unit/melder/crystallizer/crystal_analysis/, run with the GIL off.

## Unknowns and Open Decisions
- UNKNOWN: none for the code path; the MelderOps timing is measured at closure.
- DECISION_REQUEST: none open.

## Context / Handoff Summary
- What changed: fixes A and B and the record-version note implemented as specified; warm analysis of one measured
  world with a `.venv` inside the project went from 2.8 s to 0.12 s (1,077 targets to 255; 18,888 Path.resolve to
  556), and of Melder's own aether world from 1.1 s to 0.20 s.
- Remaining risks: tests elsewhere that assumed venv packages are user source (the full suite decides).
- Next entrypoint: #327 Notes.
