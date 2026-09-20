# Existing-object gap analysis

Measured 2026-09-13 against workspace Melder 0.2.40 using Python 3.14.7 free-threaded.
Production source was not changed. Melder disk caching was disabled in these fixtures.

## What the run proves

The expanded experiment records 66 cases: 45 stock-runtime observations and 21 diagnostic
observations. Its green pytest result means every observation was captured and successful
paths preserved their asserted identities. It does not mean the recorded refusals are repaired.

The diagnostic replaces only the existing-instance branches of the Phase-8 and Phase-9
contract scanners in memory with an empty contract sequence. Ordinary class/factory behavior,
provider selection, validation, execution and cleanup remain real. Pytest restores both methods
after each case. Fourteen stock-failing injection scenarios then complete with exact identity.

| Area | Stock runtime | Two-scanner diagnostic | Classification |
| --- | --- | --- | --- |
| Direct, nested, pair and function injection | Non-callable planning refusal | Exact supplied object injected | Confirmed planning bug |
| Two-element collection and explicit named SpellMap | Same planning refusal | Original elements/order and selected object preserved | Same planning bug |
| Literal forward-name annotation | Binds, then planning refusal | Correct existing value injected | Same planning bug |
| Consumer override with an existing registered provider | Planning refusal before override executes | Replacement injected | Same planning bug |
| Consumer many/unique/lesser/spellspace lifetimes | Planning refusal | Expected consumer reuse; provider identity unchanged | Same planning bug |
| Linked provider through annotation or SpellContract | Local planning refusal at meld | Exact owner object injected; owner lookup survives borrower cleanup | Same planning bug |
| TYPE_CHECKING-only deferred annotation | NameError during consumer bind | Same NameError | Separate annotation bug |
| Same deferred annotation with a class provider | NameError during consumer bind | Not needed | Annotation bug is broader than existing instances |
| Ordinary required typed input, provider absent, future override intended | Phase-3 missing-provider refusal | Same refusal | Distinct declared-input design question |
| Wrong object advertised under a concrete/protocol frame | Bind accepts; scanner later refuses | Incompatible object injected; protocol method call fails | Admission/type-enforcement gap for owner decision |

The protocol class controls matter: WrongValue CLASS is rejected for missing read(), while a
WrongValue INSTANCE advertised with that same protocol is admitted. A compatible class is accepted.
Concrete spellframe types can also serve routing purposes; do not impose a new isinstance policy
on every frame without an explicit design decision.

## Working behavior and intentional restrictions

- Six actual root lookup forms work: ID, supplied object, class, logical name, explicit type frame,
  and named binding. The reuse-only meld_existing_spell door also returns the same object.
- This differs from consumer matching: earlier experiments show a concrete parameter annotation
  needs matching type-frame metadata for a prebuilt instance; root class lookup alone can succeed.
- Direct existing-object lookup works from root, lesser and spellspace scopes, before and after
  conjure-time registration. Scope release preserves subsequent owner lookup.
- Selected ordinary defaults and None remain honored with an existing provider registered.
  Explicit consumer overrides still replace an ordinary default.
- A nonempty override targeting the existing root itself is rejected; an empty dict is a no-op.
- Empty lists and dictionaries remain present existing values. Bool/int binds are explicitly
  refused as primitive spell targets; that refusal is distinct from falsey-object presence.
- An explicit dispose name on a prebuilt object is discarded; owner cleanup invokes it zero
  times. The class-binding control retains the name and invokes it once. This agrees with the
  current documented and tested class-profile-only disposal policy; changing custody is a decision.

## Regression coverage

The two stock integration files now contain 21 cases: 14 fail and 7 pass, with zero setup errors.
Thirteen failures reproduce existing-instance signature inspection; one reproduces deferred
annotation NameError. New failures cover repeated parameters, function injection, lesser and
spellspace consumers, linked annotation/contract injection, and the deferred annotation case.

Coverage defect: the older test named test_existing_instance_frame_type_hint_injects_existing
actually asserts PhaseExecutionError containing "not a callable object". Keep its current result
out of success claims, and update that expectation when the production repair is selected.

## Commands and evidence

```powershell
.venv_new/Scripts/python.exe -m pytest tests/experimentation/test_existing_instance_gap_experiment.py -q -s --tb=short -p no:cacheprovider -o faulthandler_timeout=30
.venv_new/Scripts/python.exe -m pytest tests/integration/melder/spellbook/test_existing_instance_planning.py tests/integration/melder/spellbook/test_existing_instance_additional_regressions.py -q --tb=short -p no:cacheprovider -o faulthandler_timeout=30
.venv_new/Scripts/python.exe -m ruff check --select F,I tests/experimentation/test_existing_instance_gap_experiment.py tests/integration/melder/spellbook/test_existing_instance_additional_regressions.py
```

- gaps_final.log/xml: 66 observations, 0.99 seconds, pytest exit 0.
- gap_observations.json: parsed rows, including all refusals and their exact stages.
- expanded_regressions.log/xml: 14 failed, 7 passed, 2.61 seconds, pytest exit 1.
- Scoped Ruff F/I: passed. Full Ruff proposes patterns conflicting with repository policy
  (PEP 604, removal of descriptor defaults/fixture aliases); no such policy changes were made.
- gaps_initial.log/xml: invalid frozen-config fixture attempt, not runtime evidence.
- gaps_corrected.log/xml: first valid run, retaining the new annotation traceback.

Original CommandOps/Iris acceptance was not rerun; these native cases complement its real inputs.
Serialization, cached-plan reload and concurrent stress were not exercised by this tranche.
The source read map and remaining implementation decisions live in the owning task.
