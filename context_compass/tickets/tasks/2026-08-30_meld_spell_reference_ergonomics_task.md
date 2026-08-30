# Task: Implement human-first meld identity ergonomics

## Metadata
- Task ID: TASK-2026-08-30-meld-spell-reference-ergonomics
- Story: STORY-2026-08-30-human-meld-identity-api
- Status: review
- Owner: cowork
- Agent Name: codex_1
- Priority: p1
- Created: 2026-08-30T19:08:29Z
- Updated: 2026-08-30T21:31:49Z

## Objective
Implement and validate the human-first public Meld identity contract discovered
during the initial ergonomics investigation: human strings resolve SpellNames,
implementation objects remain valid through `spell=`, and opaque machine
identities use explicit `spell_id=`; per-call construction inputs use the
concise public `override=` keyword.

## Ticket Contract
- ENTRY_GATE: Owner approved the human-first API epic, deterministic caller
  migration, and required patch artifacts; `attention_board.md` routes here.
- EXECUTION_BOUNDARY: Conduit and SpellSpace public identity dispatch,
  three-surface public override forwarding,
  repository-owned callers, README/UX examples, canonical component context,
  generated assets, and focused-to-complete supported validation.
- DEPENDENCIES: Canonical 19-item resolution contract, consumed patch artifacts,
  current source/component/graph context, and existing internal Meld fast doors.
- EXIT_GATE: Human-name, implementation-object, and explicit-ID forms execute
  across both public facades; callers/docs/assets are migrated; supported and
  deterministic checks pass.
- FAILURE_ESCALATION: Stop on internal fast-door drift, unresolved identity
  ambiguity, behavior outside Meld identity, or unsupported migration failures.

## Scope Boundaries
- In scope:
  - public Conduit and SpellSpace identity dispatch
  - public Conduit, SpellSpace, and capability-command override keyword
  - repository-owned `meld` callers, README, and UX/AIX examples
  - canonical component documentation and generated build assets
  - focused, supported-tier, example, static, asset, and diff validation
- Out of scope:
  - redesigning internal Meld signatures, compiled execution, or fast doors
  - unrelated DI/container behavior or reusable-provider design
  - new performance claims

## State Transition Event
- from_state: in_progress
- to_state: review
- transition_reason: The three public signatures, 83 executable callers,
  human/canonical documentation, generated assets, and complete supported
  suite now agree on `override=`.

## Steps / Checklist
- [x] Read README and relevant examples completely.
- [x] Slice the referenced components and graph nodes through verified indexes.
- [x] Read the complete public resolution implementation and relevant tests.
- [x] Produce an evidence-backed ergonomics assessment and recommendation.
- [x] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [x] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- Human-first Conduit and SpellSpace facade behavior.
- Concise public `override=` forwarding across all three public surfaces.
- Deterministically migrated repository-owned callers and human documentation.
- Synchronized component/build assets and complete validation evidence.

## Files / Paths Impacted
- `context_compass/attention_board.md`
- This task.
- `src/melder/aether/conduit/conduit.py`
- `src/melder/aether/conduit/spell_space/spell_space.py`
- `src/melder/nexus/rift/command_system/capability_command_system.py`
- `README.md`
- `UX_and_AIX_experiences/`
- `tests/`
- `context_compass/system_docs/src_components.md`
- `src/melder/_build_assets/`
- `context_compass/user_defined/meld_public_callsite_codemod.py`
- `tests/experimentation/test_meld_human_spell_name_string_experiment.py`
- `tests/integration/melder/aether/conduit/test_human_spell_name_resolution.py`

## Validation
- Complete supported suite: pass
  (`10,962 passed, 28 skipped, 15 xfailed, 1 xpassed`).
- Migrated conduit/spellbook surface: pass
  (`2,237 passed, 2 skipped, 3 xfailed, 1 xpassed`).
- Directly affected runnable examples: pass (`117 passed`).
- Focused resolution contract: pass (`25 passed`).
- Public override boundary tests: pass (`47 passed`).
- Override-heavy component/integration/experiment files: pass (`234 passed`).
- Migrated UX/AIX probe suites: pass (`109 passed`).
- Directly modified runnable override lessons: pass (5 of 5).
- Codemod dry run: pass (`CHECK: 0 call(s) across 0 file(s)`).
- Public `.meld(spell_name=...)` search across README, UX, and tests: zero matches.
- Warning-fatal build-asset check: all three assets current.
- EOL convention census: pass (zero committed-convention mismatches).
- Diff hygiene: pass
  (`git -c core.whitespace=cr-at-eol diff --check`).
- Full example harness: `552 passed, 4 failed`; all four failures are
  pre-existing curriculum-quality gates outside this epic and are recorded in Notes.

## Risks / Rollback Notes
- Broad caller migration can miss opaque ID variables; deterministic codemod
  checks plus complete supported tests cover the residual risk.
- Public and internal Meld identity contracts intentionally differ; rollback is
  the scoped facade/caller/documentation change set, not an internal fast-door rewrite.

## Applicable Anti-Patterns
- [x] No status transition without evidence-backed transition reason.
- [x] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [ ] No closure without acceptance confirmation and board-sync completion.

## Done Checklist
- [x] Steps complete and checked off
- [x] Deliverables produced and linked
- [x] Documentation update need identified
- [x] Validation status recorded
- [x] Unknown-first discipline followed (`UNKNOWN` promoted to `FACT` only with evidence)
- [x] Notes quality maintained (`SCORE_0_TO_10` >=
      `workflow.ticket_microcycle.minimum_note_score`)
- [x] Applicable anti-pattern checks are clear or escalated with evidence.
- [ ] Acceptance criteria reviewed with user and confirmed
- [ ] Board sync completed for successor routing or closure anchor update.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - `system_docs/patches/active/human_meld_identity_api_2026_08_30/architecture_patch.md`
  - `system_docs/patches/active/human_meld_identity_api_2026_08_30/component_patch_meld_resolution.md`
  - `system_docs/patches/active/human_meld_identity_api_2026_08_30/code_description_patch_meld_identity_dispatch.md`
- DISPOSITION: promote_to_documentation
- CLEANUP_TRIGGER: epic acceptance

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS:
- CONTEXT_TOPICS:
  - repeated spell selection at meld time
  - reusable resolution handles
- IF_UNKNOWN: none

## Noting Behavior
- Note focus: public call shape, source-backed behavior, usability impact, and next evidence target.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-08-30T21:31:49Z
  TYPE: MEASURE
  CLAIM: Final override migration gates pass: codemod zero; public README/UX
    `spell_override=` matches zero; all three assets current; zero EOL
    mismatches; CR-at-EOL-aware whitespace check exit zero; no tracked
    deletions; and the logical review diff remains bounded to the approved
    human-identity/override migration.
  EVIDENCE:
  - `context_compass/user_defined/meld_public_callsite_codemod.py:1-200`
  - `src/melder/_build_assets/_build_asset_runner.py:268-350`
  - `git ls-files --eol`
  - `git -c core.whitespace=cr-at-eol diff --check`
  IMPACT: Runtime, callers, human docs, canonical context, generated assets,
    EOL conventions, and supported tests agree on public `override=`.
  NEXT: Return the task, story, epic, and attention route to review; wait for
    owner acceptance before closure or artifact disposition.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-08-30T21:30:51Z
  TYPE: MEASURE
  CLAIM: The complete supported unit/component/integration suite passes the
    public override-keyword migration with 10,962 passed, 28 skipped, 15
    expected failures, one expected xpass, and exit code zero in 176.97 seconds.
  EVIDENCE:
  - `.venv_new\\Scripts\\python.exe -m pytest -q tests/unit tests/component tests/integration`
  IMPACT: The shorter public keyword introduces no supported runtime regression.
  NEXT: Repeat final codemod, keyword, asset, EOL, whitespace, and diff-scope
    checks, then return the epic/story/task to review.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-08-30T21:27:30Z
  TYPE: MEASURE
  CLAIM: Post-normalization static gates are fully green: zero EOL mismatches,
    EOL-aware whitespace check exit zero, all three build assets current,
    public human docs contain zero `spell_override=` syntax, and the codemod
    dry run reports zero calls across zero files.
  EVIDENCE:
  - `git ls-files --eol`
  - `git -c core.whitespace=cr-at-eol diff --check`
  - `context_compass/user_defined/meld_public_callsite_codemod.py:1-200`
  - `src/melder/_build_assets/_build_asset_runner.py:268-350`
  IMPACT: The complete supported suite is the remaining behavioral gate.
  NEXT: Run unit, component, and integration tiers with normal host temporary
    access, then classify any failure before review handoff.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-08-30T21:26:29Z
  TYPE: MEASURE
  CLAIM: Static migration gates pass: codemod dry run is zero; README/UX contain
    no public `spell_override=` syntax; all three public source signatures and
    docstrings expose `override`; warning-fatal build-asset check passes; and
    EOL-aware whitespace validation exits zero. The EOL census finds 12
    index-LF files left mixed/CRLF by manual edits/regeneration.
  EVIDENCE:
  - `context_compass/user_defined/meld_public_callsite_codemod.py:1-200`
  - `src/melder/aether/conduit/conduit.py:3955-4109`
  - `src/melder/aether/conduit/spell_space/spell_space.py:443-498`
  - `src/melder/nexus/rift/command_system/capability_command_system.py:1013-1081`
  - `src/melder/_build_assets/_build_asset_runner.py:268-350`
  IMPACT: Semantics and generated content are current; only deterministic EOL
    convention repair remains before broad validation.
  NEXT: Normalize exactly the 12 index-LF mismatches, require zero EOL mismatch,
    repeat static gates, then run the complete supported suite.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-08-30T21:25:26Z
  TYPE: MEASURE
  CLAIM: All five directly modified runnable lessons execute successfully in
    isolated processes. Flat constructor, deep exact-path, unique wildcard,
    broadcast, branch-graft, precedence, refusal, and lifetime assertions pass
    under the new public keyword.
  EVIDENCE:
  - `UX_and_AIX_experiences/02_intermediate/02_spellbinder_full_chain.py`
  - `UX_and_AIX_experiences/02_intermediate/08_spell_override_construction.py`
  - `UX_and_AIX_experiences/03_advanced/01_deep_spell_override_paths.py`
  - `UX_and_AIX_experiences/03_advanced/19_wildcard_and_broadcast_overrides.py`
  - `UX_and_AIX_experiences/04_expert/10_deep_overrides_paths_through_a_graph.py`
  IMPACT: The human-facing examples are executable documentation, not only
    textually migrated call sites.
  NEXT: Run the codemod dry run, public-keyword absence search, warning-fatal
    asset check, EOL restoration, and diff hygiene.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-08-30T21:25:06Z
  TYPE: MEASURE
  CLAIM: The migrated UX/AIX advanced, contract, and intermediate probe suites
    pass 109 tests. Public constructor, deep-path, wildcard, and broadcast
    examples execute through `override=`.
  EVIDENCE:
  - `UX_and_AIX_experiences/pytest_examples/test_advanced_probes.py`
  - `UX_and_AIX_experiences/pytest_examples/test_contract_probes.py`
  - `UX_and_AIX_experiences/pytest_examples/test_intermediate_probes.py`
  IMPACT: Curriculum-level behavioral coverage agrees with runtime and component tests.
  NEXT: Execute the five directly modified lesson scripts in isolated processes,
    then run codemod/keyword/asset/static gates.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-08-30T21:24:40Z
  TYPE: MEASURE
  CLAIM: Every mechanically migrated non-UX test file passes: 234 tests across
    override-heavy component, integration, and experiment surfaces. Flat,
    deep-path, wildcard, broadcast, spell-contract, fast-door, and error
    behavior remain unchanged under `override=`.
  EVIDENCE:
  - `tests/component/melder/aether/conduit/test_conduit_component_meld_overrides.py`
  - `tests/component/melder/aether/conduit/test_conduit_component_meld_overrides_deep.py`
  - `tests/integration/melder/spellbook/test_spellbook_integration_overrides.py`
  - `tests/integration/melder/spellbook/test_spellbook_integration_resolution_contract_more.py`
  IMPACT: Runtime override semantics are green across every migrated behavioral file.
  NEXT: Execute the migrated UX/AIX probe and runnable-example surface.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-08-30T21:24:18Z
  TYPE: MEASURE
  CLAIM: Focused public-boundary validation passes 47 tests across Conduit,
    SpellSpace, and the capability-command wrapper. Exact keyword delegation,
    identity normalization, and existing facade behavior remain green.
  EVIDENCE:
  - `tests/unit/melder/aether/conduit/test_conduit_facade.py`
  - `tests/unit/melder/aether/conduit/spell_space/test_spell_space.py`
  - `tests/unit/melder/aether/test_nexus.py:4934-4997`
  IMPACT: The three renamed signatures are stable enough for override-heavy
    behavioral validation.
  NEXT: Run every component/integration/experiment file mechanically migrated
    from public `spell_override=` to `override=`.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-08-30T21:23:56Z
  TYPE: FACT
  CLAIM: The capability-command boundary regression now passes a unique
    `override` payload and asserts the exact selected-Conduit call, including
    `override=override_payload`. It will fail if the wrapper drops, copies, or
    forwards the renamed keyword incorrectly.
  EVIDENCE:
  - `tests/unit/melder/aether/test_nexus.py:4934-4997`
  IMPACT: All three public surfaces now have direct delegation coverage before
    broader behavioral execution.
  NEXT: Run focused facade, SpellSpace, capability-command, override component/
    integration, and executable curriculum tests.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-08-30T21:23:20Z
  TYPE: RISK
  CLAIM: Existing Conduit and SpellSpace unit tests assert override delegation,
    but the capability-command test uses a permissive `**kwargs` lambda and
    checks only the returned sentinel. It would pass if `override` were
    dropped or forwarded under the wrong public keyword.
  EVIDENCE:
  - `tests/unit/melder/aether/test_nexus.py:4936-4985`
  - `tests/unit/melder/aether/conduit/test_conduit_facade.py:618-710`
  - `tests/unit/melder/aether/conduit/spell_space/test_spell_space.py:226-270`
  IMPACT: The third public surface lacks a regression for the exact renamed
    keyword boundary.
  NEXT: Replace the permissive callable with a Mock, pass an override payload,
    and assert the exact Conduit call before focused execution.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-08-30T21:22:32Z
  TYPE: FACT
  CLAIM: Canonical regeneration is synchronized. The component map remains 136
    sections and grows only from 8,374 to 8,376 lines; its index proof is fresh.
    Build output changes remain confined to the component payload/index plus
    the expected agent-documentation and bind-guard source fingerprints.
    Internal `Meld.meld(..., spell_override=...)` documentation remains intact.
  EVIDENCE:
  - `context_compass/system_docs/src_components_index.md:1-24`
  - `src/melder/_build_assets/_system_documents/payloads/src_components_payload.py:2449-2468`
  - `src/melder/_build_assets/_system_documents/payloads/src_components_payload.py:4659-4659`
  IMPACT: Authored and packaged docs reflect the public/internal boundary with
    no graph-topology or override-engine rewrite.
  NEXT: Run focused facade, SpellSpace, capability-command, override, curriculum,
    asset, codemod, public-keyword, and diff-hygiene validation.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-08-30T21:22:01Z
  TYPE: FACT
  CLAIM: Human-facing prose and canonical component context now use
    `override=` for the public Meld keyword. Remaining `spell_override`
    strings in UX are only stable lesson/test file identifiers; remaining
    component occurrences describe the intentionally unchanged internal Meld
    signature and override engine.
  EVIDENCE:
  - `README.md:650-661`
  - `UX_and_AIX_experiences/02_intermediate/08_spell_override_construction.py:1-45`
  - `UX_and_AIX_experiences/03_advanced/01_deep_spell_override_paths.py:1-60`
  - `UX_and_AIX_experiences/03_advanced/19_wildcard_and_broadcast_overrides.py:1-170`
  - `UX_and_AIX_experiences/04_expert/10_deep_overrides_paths_through_a_graph.py:1-170`
  - `context_compass/system_docs/src_components.md:2423-2501`
  IMPACT: Executable examples, public documentation, and canonical component
    semantics agree while internal terminology and stable file names remain intact.
  NEXT: Regenerate the component index and all deterministic build assets, then
    inspect generated diffs before validation.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-08-30T21:19:53Z
  TYPE: FACT
  CLAIM: The runtime/caller tranche is implemented and reread. Conduit,
    SpellSpace, and CapabilityCommandSystem expose typed `override=`
    parameters and forward the identical payload into internal
    `spell_override=`; 83 executable public calls across 23 test/UX files are
    migrated mechanically. Internal Meld signatures and override engines are untouched.
  EVIDENCE:
  - `src/melder/aether/conduit/conduit.py:3955-4109`
  - `src/melder/aether/conduit/spell_space/spell_space.py:443-498`
  - `src/melder/nexus/rift/command_system/capability_command_system.py:1013-1081`
  - `context_compass/user_defined/meld_public_callsite_codemod.py:1-200`
  IMPACT: Public ergonomics are shortened without behavior, allocation, error,
    gate, lifecycle, or internal naming drift.
  NEXT: Replace public-keyword prose in README/UX and canonical components,
    regenerate the component index and build assets, then begin focused tests.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-08-30T21:18:45Z
  TYPE: MEASURE
  CLAIM: The extended codemod dry run identifies 83 public
    `spell_override=` calls across 23 files. Targets are confined to
    Conduit/SpellSpace component and integration tests, three resolution
    experiments, and executable UX/AIX curriculum/probes. Internal Meld unit
    suites are absent from the candidate set.
  EVIDENCE:
  - `context_compass/user_defined/meld_public_callsite_codemod.py:1-200`
  - `tests/component/melder/aether/conduit/`
  - `tests/integration/melder/conduit/`
  - `tests/integration/melder/spellbook/`
  - `UX_and_AIX_experiences/`
  IMPACT: The mechanical migration is bounded and the internal-runtime exclusion
    works on the current repository inventory.
  NEXT: Rename the three public signatures, forward to internal
    `spell_override=`, apply the 83-call codemod, and inspect the exact diff
    before running tests.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-08-30T21:17:46Z
  TYPE: FACT
  CLAIM: The syntax-aware migration tool now treats identity and override
    routing as separate boundaries. Identity rewrites still exclude internal
    Meld and command receivers; `spell_override=` rewrites include public
    command surfaces but exclude only internal Meld receivers. Product source
    remains manual-review-only.
  EVIDENCE:
  - `context_compass/user_defined/meld_public_callsite_codemod.py:1-200`
  IMPACT: Repository test/curriculum callers can be migrated deterministically
    without renaming internal runtime keywords or changing command identity semantics.
  NEXT: Run the codemod dry inventory and inspect every reported file family
    before applying it.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-08-30T21:16:45Z
  TYPE: PLAN
  CLAIM: The amended patch gate is consumed and mapped. The architecture
    three-surface delta maps to public signatures/docstrings and delegation
    tests; the component no-semantics-change rule maps to direct forwarding of
    `override` as internal `spell_override`; the code-description invariant
    maps to leaving Meld, ConduitMeld, SpellSpaceMeld, SpellOverrider, compiled
    artifacts, and cache keys unchanged. Repository callers map to a
    syntax-aware codemod plus manual human-document prose updates.
  EVIDENCE:
  - `context_compass/system_docs/patches/active/human_meld_identity_api_2026_08_30/architecture_patch.md:1-58`
  - `context_compass/system_docs/patches/active/human_meld_identity_api_2026_08_30/component_patch_meld_resolution.md:1-38`
  - `context_compass/system_docs/patches/active/human_meld_identity_api_2026_08_30/code_description_patch_meld_identity_dispatch.md:1-43`
  IMPACT: Source editing is unblocked within a precise public-only keyword
    boundary and has explicit behavioral/static validation targets.
  NEXT: Extend the existing codemod to rename only public Meld-call keywords,
    inspect its dry-run inventory, then patch the three facade definitions.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-08-30T21:15:57Z
  TYPE: FACT
  CLAIM: The live definition inventory has six `meld` methods. Public
    `Conduit.meld`, `SpellSpace.meld`, and
    `CapabilityCommandSystem.meld` expose `spell_override=`; internal
    `Meld`, `ConduitMeld`, and `SpellSpaceMeld` own the precise runtime
    `spell_override` contract. The correct boundary is a three-signature
    public rename with forwarding into unchanged internal keywords.
  EVIDENCE:
  - `src/melder/aether/conduit/conduit.py:3955-4109`
  - `src/melder/aether/conduit/spell_space/spell_space.py:443-498`
  - `src/melder/nexus/rift/command_system/capability_command_system.py:1013-1081`
  - `src/melder/aether/conduit/meld/meld.py:350-441`
  IMPACT: Shortening the public call does not require renaming SpellOverrider,
    compiled artifacts, internal tests, or the override execution model.
  NEXT: Amend the active architecture/component/code-description patches with
    the three-surface `override=` delta and public-to-internal forwarding rule.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-08-30T21:14:24Z
  TYPE: DECISION
  CLAIM: Rename the user-facing Meld override keyword to `override=` across
    Conduit, SpellSpace, and public wrappers that expose the same operation.
    Preserve the internal `spell_override` vocabulary in Meld and
    CreationContext plumbing, and preserve payload behavior exactly.
  EVIDENCE:
  - Owner direction in the active task conversation, 2026-08-30
  IMPACT: Human call sites become shorter without widening the change into
    internal execution-plan terminology or semantics.
  NEXT: Update and consume the three active patch documents, then inventory
    every definition and call site before source edits.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-08-30T21:07:08Z
  TYPE: MEASURE
  CLAIM: Final EOL-aware review validation passes. All modified tracked text
    files match their committed convention (92 LF and 30 CRLF, zero mismatches);
    the CR-at-EOL-aware whitespace check exits zero; raw diff size is reduced
    from 18,813/18,782 to 2,306/2,275, with a CR-insensitive semantic view of
    1,134/1,103. Codemod dry run remains zero, the focused contract remains
    25/25, all assets remain current, and public `.meld(spell_name=...)`
    search remains empty.
  EVIDENCE:
  - `git ls-files --eol`
  - `git -c core.whitespace=cr-at-eol diff --check`
  - `context_compass/user_defined/meld_public_callsite_codemod.py:1-177`
  - `tests/integration/melder/spellbook/test_spellbook_integration_resolution_contract.py:191-279`
  IMPACT: The migration is behaviorally green, mechanically complete, and free
    of avoidable whole-file EOL churn. The review lane has no remaining technical blocker.
  NEXT: Present the delivered contract and validation proof for owner acceptance;
    do not close tickets or dispose patch artifacts before confirmation.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-08-30T21:05:40Z
  TYPE: DECISION
  CLAIM: Repository-convention audit finds the complementary mismatch: 15
    modified files are index-LF but working mixed/CRLF (10 source/docs and five
    generated assets). Normalize only those 15 to LF, retain the 30
    index-CRLF files as CRLF, and validate whitespace with
    `git -c core.whitespace=cr-at-eol diff --check`. That Git setting ignores
    only the legitimate CR byte while preserving every other whitespace check.
  EVIDENCE:
  - `git ls-files --eol`
  - `git -c core.whitespace=cr-at-eol diff --check`
  IMPACT: Every modified tracked file will match its committed EOL convention,
    raw review stats will represent semantic changes, and whitespace validation
    will stop reporting false positives on the repository's 30 CRLF files.
  NEXT: Normalize the 15 index-LF mismatches, then rerun EOL census, raw and
    CR-insensitive stats, configured whitespace check, codemod, assets, and
    focused tests.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-08-30T21:04:38Z
  TYPE: CONFLICT
  CLAIM: The 30-file EOL restoration succeeds: all committed-CRLF targets now
    report `w/crlf`, the focused contract file still passes 25 tests, and all
    build assets remain current. Plain `git diff --check` nevertheless treats
    the repository's CR byte as trailing whitespace on each changed line.
    Keeping LF makes that command green but reintroduces about 17,700
    non-semantic line changes; keeping committed CRLF produces the reviewable
    diff but requires Git's explicit CR-at-EOL whitespace handling.
  EVIDENCE:
  - `git ls-files --eol`
  - `git diff --check`
  - `tests/integration/melder/spellbook/test_spellbook_integration_resolution_contract.py:191-279`
  IMPACT: We must validate whitespace using the repository's actual mixed-EOL
    conventions rather than accepting either whole-file churn or false-positive
    CR warnings.
  NEXT: Run `git diff --check --ignore-cr-at-eol`, inspect `core.whitespace`,
    and confirm compact raw statistics before finalizing the review proof.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-08-30T21:03:35Z
  TYPE: DECISION
  CLAIM: Diff inflation is proven to be line-ending-only churn in 30 files.
    Raw statistics are 18,813 insertions and 18,782 deletions; ignoring terminal
    CR yields 1,134/1,103. `git ls-files --eol` identifies exactly 30 modified
    tracked files with committed CRLF and current LF, while 92 tracked files
    remain index-LF. Restore only those 30 files to their committed CRLF form
    with a byte-preserving mechanical pass.
  EVIDENCE:
  - `git diff --shortstat`
  - `git diff --ignore-cr-at-eol --shortstat`
  - `git ls-files --eol`
  IMPACT: The semantic migration remains unchanged while the raw review diff
    drops the avoidable whole-file churn and respects each file's existing
    repository convention.
  NEXT: Convert only the 30 `i/crlf w/lf` files, then require matching EOL
    state, compact raw stats, clean diff hygiene, zero codemod candidates, and
    focused behavioral green.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-08-30T21:02:10Z
  TYPE: UNKNOWN
  CLAIM: Final status confirms the intended `codex_features2` branch and
    `git diff --check` passes, but raw diff statistics report 127 tracked
    files with 18,813 insertions and 18,782 deletions. Git simultaneously emits
    LF-to-CRLF conversion warnings across the mechanically migrated files, so
    line-ending-only churn is the leading explanation but is not yet proven.
  EVIDENCE:
  - `git status --short --branch`
  - `git diff --stat`
  - `git diff --check`
  IMPACT: Review handoff must not accept a mechanically correct migration if
    its textual diff is inflated by avoidable line-ending conversion.
  NEXT: Compare raw and whitespace/EOL-insensitive numstats, inspect attributes
    and representative byte endings, then normalize only if the comparison
    proves non-semantic churn.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-08-30T21:01:36Z
  TYPE: FACT
  CLAIM: The task's title, objective, execution contract, scope, deliverables,
    and rollback text now describe the owner-approved implementation lane and
    agree with its review status, changed-file inventory, validation evidence,
    and handoff summary.
  EVIDENCE:
  - `context_compass/tickets/tasks/2026-08-30_meld_spell_reference_ergonomics_task.md:1-105`
  IMPACT: ContextCompass now presents one coherent, resumable record instead of
    mixing the superseded read-only investigation with the delivered migration.
  NEXT: Run final diff hygiene and inspect branch/worktree scope, then present
    the review handoff and request owner acceptance.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-08-30T20:46:02Z
  TYPE: FACT
  CLAIM: Review-state reread found that the task metadata still describes its
    original read-only investigation boundary even though the owner explicitly
    expanded this same routed task into the implementation and migration lane.
    The status, impacted-file list, validation, and handoff already reflect the
    implemented scope.
  EVIDENCE:
  - `context_compass/tickets/tasks/2026-08-30_meld_spell_reference_ergonomics_task.md:1-89`
  IMPACT: Leaving the original objective/contract/scope intact would make the
    ticket contradict its own authorized work and final evidence.
  NEXT: Reconcile only the task title, objective, contract, scope, deliverables,
    and risk text to the approved human-first implementation boundary.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-08-30T20:44:24Z
  TYPE: MEASURE
  CLAIM: Final migration gates pass. The no-argument codemod dry run reports
    zero calls across zero files; the corrected integration contract file
    reports 25 passes; README, UX, and tests contain zero public
    `.meld(spell_name=...)` references; all three build assets are current
    with SyntaxWarning fatal; and `git diff --check` exits zero.
  EVIDENCE:
  - `context_compass/user_defined/meld_public_callsite_codemod.py:1-177`
  - `tests/integration/melder/spellbook/test_spellbook_integration_resolution_contract.py:191-273`
  - `src/melder/_build_assets/_build_asset_runner.py:268-350`
  IMPACT: Behavioral, mechanical-migration, documentation-keyword, generated
    asset, and diff-hygiene gates are all satisfied. The ticket stack is ready
    for owner review and acceptance.
  NEXT: Move the task, story, epic, and attention route to review without
    closing or moving any ticket until the owner confirms acceptance.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-08-30T20:42:34Z
  TYPE: FACT
  CLAIM: The two stale integration-test contract bullets now match the executed
    public facade: machine lookup uses `spell_id=<spell_id>`, and keyword human
    lookup uses `spell="<ClassName>"`. The surrounding test implementations
    already used those exact forms, so no behavior changed.
  EVIDENCE:
  - `tests/integration/melder/spellbook/test_spellbook_integration_resolution_contract.py:191-273`
  IMPACT: Public contract prose and executable assertions are aligned without
    altering the intentionally ID-oriented internal Meld surface.
  NEXT: Run the codemod dry run, focused integration file, public-keyword
    absence search, build-asset check, and diff hygiene.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-08-30T20:42:11Z
  TYPE: FACT
  CLAIM: The generated `Meld.meld(spell_name=...)` component text is current
    and must remain because the internal abstract Meld door still accepts
    logical names while reserving positional strings for machine IDs. The
    integration contract file is behaviorally migrated but has two stale
    public-facade docstring bullets: one names ID-in-`spell`, and one names
    the retired public `spell_name=` keyword. The codemod's no-argument mode
    is its documented CHECK/dry-run path.
  EVIDENCE:
  - `src/melder/aether/conduit/meld/meld.py:350-441`
  - `context_compass/system_docs/src_components.md:4633-4659`
  - `tests/integration/melder/spellbook/test_spellbook_integration_resolution_contract.py:199-274`
  - `context_compass/user_defined/meld_public_callsite_codemod.py:145-177`
  IMPACT: Generated internal documentation needs no change; only two test
    comments need correction before the static migration gate can be called clean.
  NEXT: Update those two public-facade contract bullets, run the no-argument
    codemod dry run, execute the focused integration file, and repeat static checks.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-08-30T20:40:59Z
  TYPE: UNKNOWN
  CLAIM: Warning-fatal build-asset validation passes all three assets and
    `git diff --check` exits zero. The attempted codemod `--check` command is
    invalid because the script exposes only `--apply`; a broad text search
    also finds two `spell_name=` references whose public-versus-internal
    status is not yet established from their surrounding code.
  EVIDENCE:
  - `context_compass/user_defined/meld_public_callsite_codemod.py:1-177`
  - `src/melder/_build_assets/_system_documents/payloads/src_components_payload.py:4657-4657`
  - `tests/integration/melder/spellbook/test_spellbook_integration_resolution_contract.py:243-243`
  IMPACT: Asset and diff gates are green, but static migration completion cannot
    be claimed until the supported codemod dry-run form and both textual
    candidates are read and classified.
  NEXT: Read the codemod and the complete containing test/source-document
    sections, then run the supported dry run and correct only genuinely stale
    public-contract prose.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-08-30T20:40:25Z
  TYPE: MEASURE
  CLAIM: The complete supported unit/component/integration suite passes outside
    the sandbox with 10,962 passed, 28 skipped, 15 expected failures, one
    expected xpass, and exit code zero in 187.41 seconds. The preceding 187
    setup errors disappear entirely with normal host temporary-directory access.
  EVIDENCE:
  - `.venv_new\\Scripts\\python.exe -m pytest -q tests/unit tests/component tests/integration`
  IMPACT: The human SpellName and explicit machine-ID migration has full
    supported-suite behavioral proof; only final deterministic/static checks
    and review-state synchronization remain.
  NEXT: Run the warning-fatal build-asset check, codemod dry run, stale-keyword
    searches, and diff hygiene, then hand the ticket stack to review.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-08-30T20:36:54Z
  TYPE: BLOCKER
  CLAIM: The post-compaction supported-suite rerun reached 10,776 passes but
    ended with 187 setup errors. Every captured traceback fails before the test
    body because pytest cannot enumerate the sandbox-blocked global temporary
    root, raising WinError 5 from `os.scandir`.
  EVIDENCE:
  - `.venv_new\\Scripts\\python.exe -m pytest -q tests/unit tests/component tests/integration`
  - `C:\\Users\\Mark\\AppData\\Local\\Temp\\pytest-of-Mark`
  IMPACT: This invocation does not evidence a Meld regression; the complete
    supported gate remains unverified until the same command runs with normal
    host temporary-directory access.
  NEXT: Rerun the identical supported suite outside the filesystem sandbox and
    require a zero exit code before review handoff.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-08-30T20:20:00Z
  TYPE: MEASURE
  CLAIM: The two full-suite failure roots are corrected and their localized
    rerun passes all 106 tests. The new regression now isolates singleton state;
    the shared static Rift harness materializes all five cases through explicit IDs.
  EVIDENCE:
  - `tests/integration/melder/aether/conduit/test_human_spell_name_resolution.py:1-50`
  - `tests/integration/melder/aether/rift/static_rift_json_testbench_support.py:407-437`
  - `tests/integration/melder/aether/rift/test_static_rift_json_testbench_integration.py`
  IMPACT: Every failure from the first complete supported run has a green localized proof.
  NEXT: Rerun the complete supported suite and require zero failures.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-08-30T20:18:00Z
  TYPE: MEASURE
  CLAIM: Complete supported suite reports 10,856 passed, 28 skipped, 15 expected
    failures, 1 expected xpass, and 106 failures. Failure topology is two roots:
    the new integration test assumes clean Nexus/Aether singleton state, and 105
    static Rift JSON matrix cases fan out from one shared setup call still passing
    an ID through `spell=`.
  EVIDENCE:
  - `tests/integration/melder/aether/conduit/test_human_spell_name_resolution.py:1-37`
  - `tests/integration/melder/aether/rift/static_rift_json_testbench_support.py:390-430`
  - `tests/integration/melder/aether/rift/test_static_rift_json_testbench_integration.py:640-800`
  IMPACT: Full-suite failure is localized to one fixture-isolation correction and one mechanical ID call.
  NEXT: Mirror established singleton reset/cleanup in the new test, migrate the shared JSON setup call, then rerun the affected files before the full suite.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-08-30T20:13:00Z
  TYPE: MEASURE
  CLAIM: Directly affected example suites pass (`117 passed`); build-asset
    check passes all three assets with SyntaxWarning fatal; codemod dry run is
    zero; and diff hygiene exits zero after LF normalization. The full example
    harness baseline remains 552/556 because of four unrelated pre-existing
    curriculum gates already documented.
  EVIDENCE:
  - `UX_and_AIX_experiences/pytest_examples/test_beginner_examples.py`
  - `UX_and_AIX_experiences/pytest_examples/test_intermediate_examples.py`
  - `src/melder/_build_assets/_build_asset_runner.py:268-350`
  - `context_compass/user_defined/meld_public_callsite_codemod.py:1-177`
  IMPACT: Migration-specific examples, assets, static inventory, and diff hygiene are green.
  NEXT: Run the complete supported unit/component/integration suite as the final behavioral gate.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-08-30T20:11:00Z
  TYPE: BLOCKER
  CLAIM: Directly affected example suites pass (`117 passed`), build-asset check
    passes all three keys, and codemod dry run is zero. `git diff --check` fails
    because LibCST rewrote codemod-touched Python files with CRLF; inspected
    logical lines contain no trailing spaces, but Git classifies the terminal CR
    on every changed line as trailing whitespace in this checkout.
  EVIDENCE:
  - `tests/component/melder/aether/conduit/test_conduit_component_creations.py:277-278`
  - `context_compass/user_defined/meld_public_callsite_codemod.py:120-145`
  IMPACT: Behavior and asset validation are green, but diff hygiene is blocked
    until changed Python files are normalized back to repository LF bytes.
  NEXT: Normalize only modified test/UX Python files from CRLF to LF and rerun diff hygiene.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-08-30T20:09:00Z
  TYPE: MEASURE
  CLAIM: Runnable-example harness collects with `PYTHONPATH=src` and reports 552
    passed, 4 failed. All four failures are pre-existing curriculum-quality
    gates unrelated to meld migration: two examples have zero assertions, one
    untouched example lacks `SURFACE EXERCISED`, and the aggregate floor repeats
    the zero-assert condition. No failing assertion/header was changed here.
  EVIDENCE:
  - `UX_and_AIX_experiences/pytest_examples/test_example_contract.py:45-121`
  - `UX_and_AIX_experiences/02_intermediate/25_clusters_unique_per_cluster.py`
  - `UX_and_AIX_experiences/03_advanced/04_utility_system_logger.py`
  - `UX_and_AIX_experiences/01_beginner/07_strings_as_vocabulary.py`
  IMPACT: Migration examples executed within a mostly green harness; unrelated
    baseline curriculum gates remain outside this epic and must not be silently fixed.
  NEXT: Run the beginner/intermediate execution modules directly plus the exact build-asset check.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-08-30T20:07:00Z
  TYPE: BLOCKER
  CLAIM: The first example-harness command failed before collection because the
    harness is outside `tests/`, so `tests/conftest.py` did not add repository
    `src/` to `sys.path`; import failed with `ModuleNotFoundError: melder`.
  EVIDENCE:
  - `UX_and_AIX_experiences/pytest_examples/conftest.py:1-50`
  - `tests/conftest.py:1-18`
  IMPACT: No example executed and no behavior result exists from this invocation.
  NEXT: Rerun the same harness with repository `src` on `PYTHONPATH`.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-08-30T20:06:00Z
  TYPE: FACT
  CLAIM: Authored documentation and deterministic assets are synchronized.
    `src_components` remains 136 sections and is now 8,374 lines; generated
    system-document changes are limited to its range table, payload, and proof.
    Agent-documentation and bind-guard manifests retain 452/628 entries and move
    only their source fingerprints. Graph topology outputs are unchanged.
  EVIDENCE:
  - `context_compass/system_docs/src_components.md:2414-2640`
  - `context_compass/system_docs/src_components_index.md:1-166`
  - `src/melder/_build_assets/_system_documents/manifest/system_documents_manifest.py:20-90`
  IMPACT: Authored and packaged documentation now describe the green runtime identity contract.
  NEXT: Run the runnable-example harness and warning-fatal build-asset check.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-08-30T20:02:00Z
  TYPE: MEASURE
  CLAIM: Migrated conduit/spellbook behavioral surface is fully green: 2,237
    passed, 2 skipped, 3 expected failures, and 1 expected xpass. Conduit and
    SpellSpace scope, concurrency, fast-door, contracts, overrides, existence,
    lifecycle, and command-wrapper paths all retain behavior under explicit IDs.
  EVIDENCE:
  - `src/melder/aether/conduit/conduit.py:3955-4120`
  - `src/melder/aether/conduit/spell_space/spell_space.py:443-525`
  - `tests/integration/melder/aether/conduit/test_human_spell_name_resolution.py:1-37`
  IMPACT: Runtime/caller migration is validated; authored docs can now be updated to settled behavior.
  NEXT: Update README, UX contract language, and canonical component documentation, then regenerate indexes/assets.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-08-30T20:00:00Z
  TYPE: MEASURE
  CLAIM: Second migrated behavioral run reports 2,235 passed with only two
    failures. Both use bind-returned machine IDs stored in semantically opaque
    variables `holder_a` / `holder_b`; four calls remain on `spell=` because no
    syntax-only codemod can infer those values are IDs. No runtime assertion regressed.
  EVIDENCE:
  - `tests/integration/melder/conduit/test_conduit_integration_scope_structural_resolution.py:285-310`
  - `tests/integration/melder/conduit/test_conduit_integration_spellspace_scope_safety.py:204-225`
  IMPACT: The remaining migration is four explicit call-site corrections, not an API defect.
  NEXT: Change those four calls to `spell_id=`, rerun the same behavioral suite, and require full green.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-08-30T19:57:00Z
  TYPE: MEASURE
  CLAIM: First migrated behavioral run reports 2,201 passed, 2 skipped, 3
    expected failures, and 36 failures. Every reviewed failure is an unmigrated
    ID syntax (`ids["root"]`, `parent_ids[i]`, `sid`, and equivalent subscript/
    short-name forms) entering the new human-name lane; no facade, gate, scope,
    hook, existence, or compiled-door assertion regressed.
  EVIDENCE:
  - `tests/component/melder/aether/conduit/test_conduit_component_singleton_specialization.py:396-705`
  - `tests/integration/melder/conduit/test_conduit_integration_cluster_dependency.py:200-260`
  - `tests/integration/melder/conduit/test_conduit_integration_scope_resolution_alignment.py:1-700`
  IMPACT: The migration algorithm needs two additional syntactic ID forms; runtime implementation remains valid.
  NEXT: Extend the codemod for ID subscripts and `sid`, apply it, require a zero dry run, then rerun the identical behavioral suite.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-08-30T19:54:00Z
  TYPE: FACT
  CLAIM: Repository-owned public call-site migration is applied mechanically:
    643 calls across 103 test/UX files. A second syntax-aware dry run reports
    zero remaining eligible calls. README class-token resolutions now use human
    SpellName strings; its explicit version-ID examples use `spell_id=`. The
    capability command wrapper preserves its external contract and translates
    into the new Conduit facade.
  EVIDENCE:
  - `context_compass/user_defined/meld_public_callsite_codemod.py:1-160`
  - `README.md:275-376`
  - `src/melder/nexus/rift/command_system/capability_command_system.py:1013-1079`
  IMPACT: Runtime-owned callers and tests are syntactically aligned; behavioral
    migration can now be tested without generated documentation noise.
  NEXT: Run conduit/spellbook unit, component, and integration surfaces and
    classify only actual behavioral failures.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-08-30T19:49:00Z
  TYPE: MEASURE
  CLAIM: The corrected facade tranche passes completely (`48 passed`). Human
    positional and `spell=` names, explicit `spell_id=`, conflict rejection,
    Conduit delegation, and SpellSpace delegation all execute under the new contract.
  EVIDENCE:
  - `tests/integration/melder/aether/conduit/test_human_spell_name_resolution.py:1-37`
  - `tests/unit/melder/aether/conduit/test_conduit_facade.py:600-717`
  - `tests/unit/melder/aether/conduit/spell_space/test_spell_space.py:226-267`
  IMPACT: The public contract is stable enough to migrate repository-owned callers.
  NEXT: Inventory public-facade ID/name call sites by syntax and perform a deterministic migration.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-08-30T19:47:00Z
  TYPE: MEASURE
  CLAIM: First focused run proves the new experiment and integration contracts
    pass. Forty-four existing facade tests also pass; four fail solely because
    they assert retired public `spell_name=` or ID-in-`spell` forwarding. No
    internal Meld/CreationContext behavior failed.
  EVIDENCE:
  - `tests/integration/melder/aether/conduit/test_human_spell_name_resolution.py:1-37`
  - `tests/unit/melder/aether/conduit/test_conduit_facade.py:614-717`
  - `tests/unit/melder/aether/conduit/spell_space/test_spell_space.py:226-267`
  IMPACT: Runtime facade dispatch is sound; the next tranche is a bounded four-test contract migration.
  NEXT: Update only the four legacy facade assertions, rerun the identical focused command, and stop on any non-contract failure.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-08-30T19:46:00Z
  TYPE: FACT
  CLAIM: First implementation tranche is complete and reread. Public Conduit
    and SpellSpace facades now separate positional human names from explicit
    `spell_id=`, reject conflicting identities, and forward machine IDs into
    unchanged internal positional fast doors. Focused experiment and supported
    integration coverage encode human, keyword-human, machine, and conflict paths.
  EVIDENCE:
  - `src/melder/aether/conduit/conduit.py:3955-4120`
  - `src/melder/aether/conduit/spell_space/spell_space.py:443-525`
  - `tests/experimentation/test_meld_human_spell_name_string_experiment.py:1-34`
  - `tests/integration/melder/aether/conduit/test_human_spell_name_resolution.py:1-37`
  IMPACT: The facade contract is ready for focused execution before any broad caller migration.
  NEXT: Run the two focused regressions and relevant facade unit tests; stop on any behavior drift.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-08-30T19:44:00Z
  TYPE: PLAN
  CLAIM: Patch entry gate is consumed and mapped. Architecture identity boundary
    maps to both public facades and end-to-end regressions; component before/after
    maps to facade signatures plus caller migration; code dispatch steps map to
    pre-gate normalization and conflict tests; coverage rows map to focused,
    fast-door, example, asset, and full supported validation.
  EVIDENCE:
  - `context_compass/system_docs/patches/active/human_meld_identity_api_2026_08_30/architecture_patch.md:1-59`
  - `context_compass/system_docs/patches/active/human_meld_identity_api_2026_08_30/component_patch_meld_resolution.md:1-35`
  - `context_compass/system_docs/patches/active/human_meld_identity_api_2026_08_30/code_description_patch_meld_identity_dispatch.md:1-39`
  IMPACT: Required artifacts exist, are linked, agree with one another, and give
    an implementation/test mapping. Source editing is unblocked.
  NEXT: Patch the two public facades and focused regressions only, then validate
    that tranche before wider caller migration.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-08-30T19:40:00Z
  TYPE: DECISION
  CLAIM: Replace the public `spell_name=` slot with explicit `spell_id=` on
    `Conduit.meld` and `SpellSpace.meld`; positional strings become human
    SpellNames. Keep the internal concrete Meld doors ID-oriented and pass the
    explicit public ID into their existing positional fast lane. Inventory finds
    nine meld definitions and 1,169 textual calls across 210 files, but generated
    payloads and internal-door tests are not public migration targets.
  EVIDENCE:
  - `src/melder/aether/conduit/conduit.py:3955-4101`
  - `src/melder/aether/conduit/spell_space/spell_space.py:443-503`
  - `src/melder/aether/conduit/meld/conduit_meld.py:143-451`
  - `src/melder/aether/conduit/meld/spellspace_meld.py:168-468`
  IMPACT: Human and machine identities become deterministic without SHA-shape
    guessing or ID-path cache misses. Migration is contained to public callers,
    human documentation, tests, and derived documentation assets.
  NEXT: Implement the two public facade dispatches and focused regressions before
    migrating the wider call-site set.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-08-30T19:35:00Z
  TYPE: DECISION
  CLAIM: Implement the minimal compatibility rule at `Conduit.meld`: a string
    of length 64 retains the existing spell-id lane; every other string is
    forwarded as `spell_name`. Keep `spell_name=` as the explicit escape hatch
    for the pathological 64-character human identifier case. Update only README
    examples that currently retain a concrete class solely to meld it.
  EVIDENCE:
  - `src/melder/aether/conduit/conduit.py:3955-4101`
  - `src/melder/aether/conduit/meld/conduit_meld.py:238-339`
  - `README.md:275-376`
  IMPACT: Existing real spell IDs remain byte-for-byte compatible; human
    `meld("MyService")` gains the canonical A6 behavior with one length branch
    and no speculative multi-resolution path.
  NEXT: Patch the public facade, convert the focused experiment into a passing
    regression, add supported-suite coverage, and update affected README examples.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-08-30T19:33:00Z
  TYPE: MEASURE
  CLAIM: The requested experiment passes and proves current behavior. Explicit
    `spell_name="MyService"` resolves the service, while positional
    `meld("MyService")` raises `KeyError` with
    `[MELD] No spell found with spell_id: MyService`.
  EVIDENCE:
  - `tests/experimentation/test_meld_human_spell_name_string_experiment.py:1-34`
  IMPACT: Current runtime unambiguously routes positional human strings through
    the spell-id lane, contrary to the canonical A6 human SpellName contract.
  NEXT: Use this proof to authorize and implement the human positional-string correction.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-08-30T19:32:32Z
  TYPE: PLAN
  CLAIM: Add one characterization experiment comparing positional
    `meld("MyService")` with the explicit `spell_name="MyService"` control, then
    run only that file and report the observed branch and exception.
  EVIDENCE:
  - `src/melder/aether/conduit/meld/conduit_meld.py:238-339`
  IMPACT: The disputed behavior will be settled by execution rather than source interpretation.
  NEXT: Create and run the single experiment file.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-08-30T19:27:53Z
  TYPE: DECISION_REQUEST
  CLAIM: The owner requested README-only conversion from class-token melds to
    positional human SpellName strings. Current `ConduitMeld` and `SpellSpaceMeld`
    treat every positional string as a machine spell id; the existing address-form
    example proves this current behavior. Updating only README would publish
    examples that fail at runtime.
  EVIDENCE:
  - `src/melder/aether/conduit/meld/conduit_meld.py:238-339`
  - `src/melder/aether/conduit/meld/spellspace_meld.py:263-359`
  - `UX_and_AIX_experiences/01_beginner/26_meld_address_forms.py:26-46`
  IMPACT: A truthful README conversion requires the human positional-string
    compatibility path plus regression tests, or it must use the currently
    supported but less desirable `spell_name="MyService"` form.
  NEXT: Obtain owner approval to include the minimal runtime/test compatibility
    change required by `conduit.meld("MyService")` before editing README examples.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-08-30T19:26:14Z
  TYPE: CONFLICT
  CLAIM: The owner-supplied canonical resolution contract defines positional
    `conduit.meld("MyService")` as a human SpellName lookup, while current source
    treats every positional string as a machine `spell_id` and requires
    `spell_name="MyService"` for the logical-name route. The contract also assigns
    the same positional string shape to direct spell-id resolution, leaving an
    unresolved A1-versus-A6 disambiguation collision.
  EVIDENCE:
  - Owner-supplied `Melder DI Resolution Contract (19 Items)`, Sections A1 and A6
  - `src/melder/aether/conduit/meld/meld.py:350-428`
  - `src/melder/aether/conduit/meld/meld.py:1247-1330`
  - `src/melder/aether/conduit/meld/conduit_meld.py:238-339`
  IMPACT: Raw implementation references and opaque SHA ids were never intended
    to be mandatory for human root resolution. The current API drift explains
    why the README examples look wrong. A design ruling is required only for how
    low-level IDs coexist with the human positional string form.
  NEXT: Discuss the intended A1/A6 disambiguation with the owner before proposing
    any implementation or example rewrite.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-08-30T19:23:44Z
  TYPE: DECISION
  CLAIM: Supersede the spell-id recommendation. Human meld should primarily
    consume a human registration identity: either a typed `Binding[T]` returned
    by bind or an explicit human alias/address. Machine SHA IDs require a separate
    explicit/internal lane, and raw implementation-object lookup should remain a
    convenience rather than the beginner contract. The current `spell` union
    conflates all three identity classes and is the root API defect.
  EVIDENCE:
  - `src/melder/aether/conduit/meld/meld.py:350-542`
  - `src/melder/aether/conduit/meld/meld.py:1247-1418`
  - `src/melder/aether/conduit/meld/conduit_meld.py:143-451`
  - `src/melder/utilities/helpers/general_helpers.py:109-427`
  IMPACT: Beginner users should never need an implementation import or opaque SHA
    to obtain an instance. Meld still needs an identity because a conduit contains
    many spells, but that identity must be human-authored and stable.
  NEXT: Review the corrected recommendation, then open a design lane if the owner
    wants the human `Binding[T]`/alias contract implemented and examples rewritten.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-08-30T19:22:08Z
  TYPE: FACT
  CLAIM: Public `Spellbook.bind(...)` returns the canonical SHA256 `spell_id`,
    and public `Conduit.meld(...)` treats a positional string as that id through
    its cheapest warm lane. The implementation object is therefore not required
    after registration. Beginner examples discard the returned id and choose the
    raw class/object lookup form again.
  EVIDENCE:
  - `src/melder/aether/spellbook/spellbook.py:5030-5292`
  - `src/melder/aether/conduit/conduit.py:3955-4101`
  - `UX_and_AIX_experiences/01_beginner/01_hello_meld.py:18-29`
  - `UX_and_AIX_experiences/01_beginner/26_meld_address_forms.py:26-38`
  IMPACT: Current runnable first-contact material creates avoidable implementation
    coupling. The runtime already supports an implementation-independent identity,
    but the overloaded `spell` parameter and examples hide it.
  NEXT: Revise the recommendation around a first-class bind result / registration
    reference, with raw implementation-object lookup retained only as convenience.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-08-30T19:20:53Z
  TYPE: ALIGNMENT_CHECK
  CLAIM: The owner's concern is specifically that examples bind an implementation
    object, discard the registration identity, then require the same implementation
    object again as the meld lookup token. The earlier provider-only ruling answered
    repetition but did not address this implementation coupling.
  EVIDENCE:
  - `UX_and_AIX_experiences/01_beginner/01_hello_meld.py:18-29`
  - `UX_and_AIX_experiences/01_beginner/26_meld_address_forms.py:26-38`
  IMPACT: The investigation must judge the bind-result and meld-identity contract.
    A convenience provider alone would preserve the same wrong class-token coupling.
  NEXT: Read the complete public `Spellbook.bind` return path and its tests, then
    revise the API recommendation around a first-class registration identity.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-08-30T19:17:47Z
  TYPE: DECISION
  CLAIM: Keep selector-based `Conduit.meld(...)` as the general multi-spell door,
    but stop teaching "meld everywhere" or passing Conduit into business logic.
    Resolve application roots at composition/scope boundaries and use constructor
    injection below them. Add an optional typed spell-bound provider for repeated
    lazy/fresh resolution; reject argumentless meld on a general conduit as ambiguous.
  EVIDENCE:
  - `README.md:300-308`
  - `README.md:568-584`
  - `UX_and_AIX_experiences/01_beginner/27_pass_the_conduit_around.py:15-41`
  - `src/melder/aether/conduit/conduit.py:3955-4101`
  - `src/melder/aether/conduit/meld/conduit_meld.py:143-451`
  - `src/melder/aether/spellbook/bind/spell_index.py:12-160`
  IMPACT: The current implementation is fast but the taught UX encourages a
    service-locator pattern and avoidable repetition. A provider can remove the
    repetition without weakening Melder's runtime invariants if it delegates to
    the current public door and follows stable SpellIndex lineage identity.
  NEXT: Obtain owner direction on whether to implement the README/example
    correction only or open a design/implementation lane for the typed provider too.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-08-30T19:16:59Z
  TYPE: FACT
  CLAIM: Live source exposes no public spell-bound provider/resolver. Every
    Conduit and SpellSpace meld call still accepts a selector. The runtime
    removes most repeated lookup cost internally: hashable logical selectors
    cache to spell ids, and successful plain spell-id calls build a guarded fast
    door. The spell-owned `CreationContext` is not a safe public substitute
    because execution still requires the current Meld door for scope storage,
    gates, hooks, overrides, validity, and self-replacing executor slots.
  EVIDENCE:
  - `src/melder/aether/conduit/conduit.py:3955-4101`
  - `src/melder/aether/conduit/meld/conduit_meld.py:143-451`
  - `src/melder/aether/conduit/meld/meld.py:240-278`
  - `src/melder/aether/conduit/meld/creation_context/creation_context.py:237-309`
  - `tests/unit/melder/aether/conduit/meld/test_meld.py:982-1023`
  - `tests/component/melder/aether/conduit/test_conduit_component_fast_meld_door.py:200-229`
  IMPACT: Repeating a selector is not a material warm-path performance defect,
    but it is unnecessary caller ceremony and encourages passing the container
    into application functions as a service locator.
  NEXT: Compare the legitimate target-selection requirement with composition-root
    usage and define the smallest bound-provider design that preserves every door invariant.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-08-30T19:12:35Z
  TYPE: FACT
  CLAIM: The graph index itself is structurally current, but current source-byte
    hashes no longer match the graph sections for `Conduit`, `ConduitMeld`,
    `Meld`, or `SpellSpaceMeld`; only `CreationContext` matches. The graph remains
    useful for file routing but is not current-behavior evidence for this call path.
  EVIDENCE:
  - `context_compass/system_docs/src_graph.md:4057-4137`
  - `context_compass/system_docs/src_graph.md:4741-4787`
  - `context_compass/system_docs/src_graph.md:5000-5060`
  - `context_compass/system_docs/src_graph.md:5118-5168`
  IMPACT: Final behavior claims must cite live source functions. No graph-derived
    claim will be promoted to FACT merely because the routing section is authored.
  NEXT: Locate the exact live meld, lookup, context-cache, and execution methods,
    then read each complete method and its direct callees.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-08-30T19:11:46Z
  TYPE: FACT
  CLAIM: The component contract deliberately requires at least one identity
    input on every public meld. The door resolves that selector to a `Spell`,
    then uses a spell-bound `CreationContext` internally. Live-creation probes
    repeat the same lookup contract rather than accepting a previously resolved
    handle.
  EVIDENCE:
  - `context_compass/system_docs/src_components.md:2414-2523`
  - `context_compass/system_docs/src_components.md:4630-4656`
  - `context_compass/system_docs/src_components.md:5297-5317`
  IMPACT: Selector repetition is an explicit API-boundary choice. The internal
    architecture already has a more specific spell-bound execution object, so
    source must determine whether safely exposing or wrapping it is feasible.
  NEXT: Read the verified graph slices for ConduitMeld, Meld, SpellSpaceMeld,
    CreationContext, and the Conduit facade, then open the exact source methods.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-08-30T19:10:53Z
  TYPE: FACT
  CLAIM: Focused runnable examples repeat the selector on every resolution,
    including inside application functions that receive a conduit. Typed melding
    improves the returned variable's static type but does not infer selection;
    frame batching is demonstrated only through a user-written `meld_frame`
    wrapper, and `find_spell_by_id` returns a live `Spell` record rather than a
    reusable resolver.
  EVIDENCE:
  - `UX_and_AIX_experiences/01_beginner/16_typed_melding.py:17-24`
  - `UX_and_AIX_experiences/01_beginner/27_pass_the_conduit_around.py:15-41`
  - `UX_and_AIX_experiences/01_beginner/38_meld_a_frame_as_dict.py:20-35`
  - `UX_and_AIX_experiences/02_intermediate/13_spell_ids_and_lookup.py:16-29`
  IMPACT: The documented application model behaves like repeated service-location
    lookup. Any claim that a built-in bound handle already solves this must now
    be proven from source, not inferred from the examples.
  NEXT: Slice the Conduit, Meld, Creations/SpellSpace, and address-resolution
    component sections through the verified component index.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-08-30T19:09:53Z
  TYPE: FACT
  CLAIM: The README's human-facing resolution model requires a selector on every
    `meld`: class/object/id through `spell`, a class name through `spell_name`,
    or the full `spellframe` plus `binding_name` address. It shows passing a
    conduit around but exposes no reusable spell-bound resolver handle.
  EVIDENCE:
  - `README.md:275-289`
  - `README.md:311-349`
  - `README.md:462-469`
  - `README.md:732-738`
  IMPACT: The owner's repetition concern is accurate for the documented beginner
    API. Source inspection is still required before concluding the runtime lacks
    an alternative that the README simply omitted.
  NEXT: Read the focused runnable examples for address forms, typed melding,
    conduit passing, bootstrapping, and repeated resolution.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-08-30T19:08:29Z
  TYPE: PLAN
  CLAIM: Trace public `meld` examples downward through indexed component and graph
    context into the actual source, then distinguish mandatory spell selection
    from optional convenience surfaces before judging the ergonomics.
  EVIDENCE:
  - `context_compass/system_docs/src_components_index.md:2414-2637`
  - `context_compass/system_docs/src_components_index.md:5297-5307`
  IMPACT: The conclusion will reflect the API that runs rather than names or examples alone.
  NEXT: Read the root README and enumerate the exact example files that call `meld`.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
Implementation and migration are complete. Public Conduit and SpellSpace facades
resolve positional or `spell=` strings as human SpellNames, preserve class/function/
Protocol values in `spell=`, and reserve `spell_id=` for explicit machine IDs.
Conduit, SpellSpace, and CapabilityCommandSystem expose public `override=` and
forward it unchanged into internal `spell_override=`. Internal Meld fast doors
and override engines remain unchanged. The complete supported suite and all final
static/build gates pass. Await owner acceptance; do not close tickets or dispose
patch artifacts until confirmation.

## Project-Specific Additions
<!-- BEGIN USER-DEFINED: project_fields -->
<!-- END USER-DEFINED: project_fields -->
