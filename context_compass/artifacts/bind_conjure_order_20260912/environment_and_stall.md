# Python environment upgrade and profiling-stall diagnosis

## Environment result

The existing `.venv_new` now runs CPython 3.14.7 free-threaded through uv 0.12.13.
The exact interpreter was already installed by uv, so no download was required.

Executed from the repository root:

```powershell
uv venv --allow-existing --no-python-downloads --python 'C:/Users/Mark/AppData/Roaming/uv/python/cpython-3.14.7+freethreaded-windows-x86_64-none/python.exe' .venv_new
```

`--allow-existing` preserved the environment's packages. The previous `pyvenv.cfg`, Scripts
directory and virtualenv helper files are retained locally in `environment_backup/` for rollback.
That backup and uv's working cache are ignored by Git; package inventories remain tracked evidence.
The old Program Files interpreter was not removed or modified.

Verification completed:

- `python.exe` and `python3.14t.exe` both report 3.14.7 free-threaded.
- The pytest executable still works and reports 9.1.1.
- Before/after inventories contain the same 40 package names and versions, with no differences.
- `uv pip check --python .venv_new/Scripts/python.exe` reports all packages compatible.
- Importing Melder, pytest, coverage, yaml and libcst keeps the GIL disabled.
- Importing the optional competing container's `dependency_injector.providers` enables the GIL
  with its extension warning. That module is not imported by the five-object benchmark.
- Nine cache benchmark processes passed on the upgraded interpreter; every process asserts
  both the free-threaded build flag and that the GIL is actually disabled.

This changes the Python interpreter, not the Melder package version or runtime source.
uv's documented upgrade behavior is described in
[Python versions](https://docs.astral.sh/uv/concepts/python-versions/#upgrading-python-versions).
The previous environment was based on a non-uv interpreter, so it was explicitly rebound with
[uv venv --allow-existing](https://docs.astral.sh/uv/reference/cli/#uv-venv--allow-existing).

## What stalled

The original cache timing cycles had already completed. The stall occurred when a subsequent
diagnostic enabled `cProfile` and ran another bind/conjure cycle with scheduler worker threads.
The main thread waited for the phase latch; worker stacks stopped at ordinary Python execution
sites such as `SpellRequirements.spell_id`, `Future.done`, and `_run_spell_chunk`.
This happened before cache classification/loading, so it was not evidence of a cache-read deadlock.

The same bounded reproduction, using the same source and installed packages, produced:

| Interpreter | Unprofiled preparation | Profiled repetition |
| --- | --- | --- |
| CPython 3.14.0 free-threaded | Completed | Stalled; watchdog dumped stacks and exited after 10 seconds |
| CPython 3.14.7 free-threaded | Completed | Completed; pytest passed in 0.58 seconds |

The evidence isolates a version-dependent profiler/free-threading interaction. The exact upstream
C-level defect or fixing commit has not been identified; the newer build resolves this reproduction.
No Melder runtime fix was made. Saved logs: `profile_repro_3140.log`, `profile_repro_3147.log`.

The reproduction is `test_profile_stall_reproduction` in
`tests/experimentation/test_dynamic_bind_conjure_order_cache_speed_experiment.py`.
Run it alone with `MELDER_BIND_ORDER_PROFILE_REPRO=1`. It deliberately has a hard-exit watchdog.
For the old base interpreter, append `.venv_new/Lib/site-packages` to `PYTHONPATH` to use the same
installed package versions; keep `src` on that path and disable pytest plugin autoload.

## Separate diagnostic setup failures

The first directory created by `TemporaryDirectory` could not be traversed by the restricted
Windows process token. The benchmark now creates a unique directory with inherited workspace
permissions and checks its resolved containment before cleanup. This is test setup only.

An autospecced spy then failed on Python 3.14.0 because `unittest.mock._get_signature_object`
called `inspect.signature` with default annotation evaluation. The production method's
`Spellbook` annotation is imported only under `TYPE_CHECKING`, so that evaluation raised NameError.
On 3.14.7 the same stdlib helper passes `annotation_format=Format.FORWARDREF`, and the spy succeeds.
Both stdlib implementations were read directly and the same pilot passed after the upgrade.

Final timing uses neither cProfile nor spies. Call-through spies run afterward in discarded
diagnostic cycles, with exact assertions for payload reads, publication, compilation and writes.

## Source evidence for cache behavior

- `src/melder/aether/spellbook/spellbook_creation_system.py:201-286`: conjure orchestration;
  a full hit skips plan phases, while structural and foundational phases still run.
- `src/melder/aether/spellbook/spellbook_creation_system.py:412-570`: cache classification and
  per-spell payload loading; an empty live spell set cannot be a full hit.
- `src/melder/aether/spellbook/spellbook_creation_system.py:954-1138`: activate, publish cached
  contexts, stage missing payloads and write at the conjure boundary.
- `src/melder/aether/spellbook/spellbook.py:5026-5293`: late bind stamps ownership and cache
  emission posture, but never loads a saved payload.
- `src/melder/aether/spellbook/spellbook_creation_system.py:1541-1634` and `:2229-2298`:
  target-local resolution runs foundational and plan phases with no cache-consumption branch.
- `src/melder/aether/spellbook/spellbook.py:939-1052`: existing cached IDs suppress export and
  writes; new payloads mark the bundle for emission at an operation boundary.
- `src/melder/aether/conduit/meld/creation_context/creation_context_factory.py:164-181`:
  publication stages newly compiled payloads when caching is enabled.
- `src/melder/utilities/caching_system/caching_system.py:153-204` and `:465-490`:
  constructing the caching utility reads its disk bundle, even for an empty conjure.

The measured result and per-object timings are in `cache_results_3147.md`.
