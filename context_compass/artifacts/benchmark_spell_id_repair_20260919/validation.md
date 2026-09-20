# Benchmark selector compatibility repair

Owning task: `tickets/tasks/2026-09-19_repair_benchmark_spell_id_lookup_task.md`.

## Cause and change

Public Conduit/SpellSpace `meld(spell=<string>)` selects a logical name. `Spellbook.bind` returns a
machine spell ID, which must be passed as `spell_id=...`. The gauntlet used that hash as a name and
therefore raised a missing logical-key error before running its workload.

- Fixed 21 selectors in the standalone Melder gauntlet first.
- The reviewed codemod then fixed 113 equivalent selectors across another 22 files.
- Also corrected three obsolete public `spell_override=` keywords to `override=` in the same calls.
- Total: 134 ID selector corrections in 23 benchmark/profile files, plus three override keywords.
- Internal synthetic door benchmarks retain their positional/internal keyword shapes.
- No runtime API, workload, assertion, lifetime declaration or scope semantics changed.

## Codemod safety

`patch_benchmark_selectors.py` defaults to dry-run. It uses `call_inventory.json` to match exact
file/line/callee/expression tuples, confines writes to the requested directory, edits only keyword
bytes, and checks the parsed result against an AST with only those intended keyword changes.
It validates all plans before writing, rejects concurrent input changes, and records before/after
hashes. `codemod_dry_run.json` and `codemod_applied.json` retain the plans and applied result.

Directory-wide AST checks confirm every Python file parses, no `meld(spell=...)` calls remain, and
no other spell keyword receives an ID-shaped value. Whitespace checks pass in the changed directory.

## Executed checks

- `gauntlet_red.xml`: original standalone failure reproduced before editing.
- `gauntlet_green.xml`: two iterations with all three lanes, passed.
- `gauntlet_default.xml`: default 1000 iterations and one thread, passed in 1.10s.
- `benchmark_compat.xml`: 18 passed, including all eight conduit/deep-graph cases, five shallow
  graph smoke cases and five Melder override cases. Override runs used their existing defaults.
- `adapter_smoke.json`: nine additional adapter checks passed: basic singleton/transient; lite/heavy
  overhead in both modes; multithreading adapter routes; shallow rotation across all graphs; codegen
  root/scoped/mixed/positional-override/targeted-override routes. Basic/overhead loops were reduced
  to 20 timed and two warmup calls for compatibility, not performance measurement.
- Repository `other` bundle rebuilt; source/tests/other freshness checks and all source-asset checks pass.
  Source package version remains 0.2.43. Full directory benchmark matrix and repository suite: Not run.

## Separate pre-existing shared-gauntlet failure

The tenth extra adapter check fails before reaching any changed meld call. Isolated fresh-process
execution confirms the same problem in `test_real_world_gauntlet.py:968`: its adapter calls
`configure_aether_frame(...)` before setting `phase_scheduler_workers_per_spellbook`, and that
subsequent mutation raises `RuntimeError: Cannot modify configuration after it is frozen.`
Evidence: `shared_gauntlet_isolated.log`. This is a different setup-order failure, retained for
follow-up rather than changing setup/lifetime behavior as part of the requested keyword-only codemod.

## Environment

`.venv_new`, Python 3.14.7 free-threaded, uv `--no-sync --offline`, `-X gil=0`, pytest cacheprovider
disabled. No package install, source runtime change, commit, release or purge implementation.
