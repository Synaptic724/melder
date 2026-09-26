# Measurement plan for tranche T1 (C-H signature determinism, C-A phase-8 pool digest)

Recorded 2026-09-26 by fable_0 (STORY-2026-09-26-signature-determinism-phase8-digest). All runs are
owner-run on the same machine and interpreter (native free-threaded 3.14t); every number is reported as
"Not run." until the owner supplies the output, which is filed in this directory with its date and command.
Medians over repeats; the noise band is the spread of the BEFORE repeats, and a delta inside that band is
reported as "no measurable change", not as an improvement.

## What each change is expected to improve, honestly
- C-A (phase-8 digest hoist): cold-path compute. Removes N pool-sized pickle+sha256 calls per cold
  conjure. On the 29-spell gauntlet book the absolute saving is small (unmeasured; single-digit
  milliseconds at most, possibly under one) and it grows quadratically with the spell count, so the
  clear demonstration is a scaled book. Warm conjure: no change (phases 8-11 are skipped there).
- C-H (one deterministic serializer): correctness, not speed. Cross-process cache hits for books whose
  SpellContract payloads carry objects (today such books miss every process); byte-identical signatures
  for everything else (no cache reset). On the gauntlet book the hit rate is already full, so C-H shows
  ZERO speed change there by design - its evidence is the determinism test and the hit-rate run below.

## Baselines (BEFORE) - capture first, same day, same machine
- B1 breakdown harness (caching disabled, 29 binds):
  `BENCH_BREAKDOWN_WORKERS=1,5 BENCH_BREAKDOWN_REPEATS=7 python benchmarks/testing_other_di/profile_phase_scheduler_breakdown.py`
  Record: per-phase wall and busy for every phase, the per-spell durations inside plan_group, par_eff.
- B2 cProfile attribution with a COLD cache (the 2026-09-25 dump was a full hit and skipped 8-11):
  delete the `__melder_cache__` folder for the gauntlet frame/conduit first, then
  `python -m pytest benchmarks/testing_other_di/test_real_world_gauntlet_cprofile.py -q -s` (or the
  harness's own entry) and keep the `.prof`. Record: ncalls and tottime of
  `serialize_codegen_signature_part`, `hash_codegen_signature`, `pickle.dumps`, and the cumtime of
  `_build_occurrence_graph_fast_key` / `_build_occurrence_graph_input_signature` (callees of `analyze`).
- B3 corpus fixture: the executor signatures (both lanes) and the phase-8 input signatures for every
  spell of the gauntlet book, written by a small owner-run script placed under this directory before the
  first edit (task 2 U3 prerequisite). This is the byte-compatibility oracle.
- B4 hot-path parity: `python benchmarks/testing_other_di/test_melder_gauntlet.py` once, per-scope-cycle
  create/cleanup/total lines (the epic's regression gate; this tranche does not touch the meld path).

## After task 2 (C-H)
- M1 determinism test (pytest, part of the change): the same book built in two subprocesses with
  `PYTHONHASHSEED=1` and `PYTHONHASHSEED=2` yields equal no-overrides and overrides executor signatures.
  Two fixtures: (a) the gauntlet book - must pass BEFORE and AFTER (byte-compatibility); (b) a book with
  an object-valued SpellContract override payload - documented to FAIL before (today's defect) and
  PASS after. Fixture (b) is the proof the change did something.
- M2 corpus check: B3 signatures unchanged after the edit for the gauntlet book. Any difference is a
  RISK note and a generation-bump decision, not a pass.
- M3 cross-process cache hit rate: process A runs the bind-conjure cycle and emits the `.melc`;
  process B (fresh interpreter) runs it again and reports the cache classification (`full_hit` expected)
  and the count of spells that had to rebuild phases 8-11. On the gauntlet book: full hit before and
  after (no change expected, recorded as such). On fixture (b): miss before, hit after.
  Command: `python benchmarks/testing_other_di/profile_bind_conjure_cycle.py` twice, or the fixture
  script under this directory if the cycle harness cannot select the book.
- M4 suites: `pytest -q tests/unit/melder/spellbook/spell_crafter tests/component/melder/spellbook`.

## After task 3 (C-A)
- M5 breakdown harness, identical command to B1: compare plan_group busy and wall at workers=1 and 5 and
  the per-spell plan_group durations (the per-root delta is the direct read). Report ms and percent with
  the BEFORE noise band; the expected shape is a uniform per-root reduction, largest on roots with the
  biggest pool rows (all roots pay the same pool cost today).
- M6 cProfile attribution, identical to B2: `serialize_codegen_signature_part`/`pickle.dumps` tottime and
  ncalls attributable to the two phase-8 key builders must drop from N pool-sized encodings to one pool
  digest plus N root-sized encodings. This is the unambiguous "did it do what it says" number even when
  M5 is inside noise on 29 spells.
- M7 scaling (proposed; needs one owner-run script under this directory): generate synthetic books of
  N = 29, 100, 300 classes with a fixed dependency shape, bind and conjure with caching disabled,
  repeats 5, BEFORE and AFTER. The quadratic term is visible here; on 29 spells it may not be.
- M8 hot-path parity: B4 again once; must be within run noise (no meld-path change was made).

## Reporting
- One table per metric in this directory: BEFORE, AFTER, delta, noise band, command, date, interpreter.
- A change with M5 inside the noise band and M6 showing the call reduction is reported as "structural
  change verified, no measurable wall-time gain at 29 spells"; the scaling run M7 then decides whether
  the gain exists at all in a regime the owner cares about.
