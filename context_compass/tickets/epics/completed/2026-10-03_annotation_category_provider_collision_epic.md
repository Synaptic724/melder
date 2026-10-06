# Epic: Separate annotation provider lookup from spellframe categories

## Metadata
- Epic ID: EPIC-2026-10-03-annotation_category_provider_collision
- Status: done
- Owner: project owner; native implementation owner to be assigned after review
- Agent Name: command_2 (evidence author), fable_1 (native implementation owner, 2026-10-03)
- Priority: p1
- Created: 2026-10-03T22:21:08Z
- Updated: 2026-10-04T12:20:00Z

- Completed: 2026-10-04T12:20:00Z
- Summary: Native repair landed at Melder 0.2.8222 (fable_1; story and two tasks completed): spellframe kind recorded on the
  binding, concrete-class frames refused, kind-aware Phase 3, crystal frame kind (record 4.1.0), generation 20;
  docs, graph, release note, assets and bundles current. Closed by owner directive (2026-10-04 06:12 local); the
  exit gate's consumer item - the unchanged Actions replacement test on a delivered build - was not reported and
  stays with the owner; a failure there opens a new task.
- Target Window: owner-selected after Anthropic review
- Related Program/Initiative: MelderOps native Actions factory acceptance
- Related Epic: tickets/epics/2026-10-03_rebind_after_first_meld_epic.md

## Problem / Opportunity

On installed Melder 0.2.8220, a constructor annotation for a Spectrum object also matches
unrelated definitions registered in the spellframe category named "spectrum". Phase 3 treats
the category key as a provider key and raises an ambiguity before MelderOps can meld a
CommandCenter with its explicit constructor override.

A standalone public-API probe uses a fresh Aether for every case. Class and string Spectrum
annotations both pass when the competing Toolbox uses a different category. Both fail when
Toolbox shares the "spectrum" category; the error lists Spectrum and Toolbox as candidates.
Its JUnit records 4 tests, 2 passed, 2 failed, 0 errors/skips, exit 1, on Python 3.14.7t
with GIL disabled and installed Melder 0.2.8220. The source and installed matcher/helper
bytes matched for this run.

The real MelderOps Actions replacement test errors earlier, during Spectrum.configure(),
with 15 candidates for CommandCenter.spectrum. Its unchanged single-case retest on the same
installed wheel records 1 test, 1 error, exit 1, with 250 source/test pins unchanged. That
application result is a separate consumer acceptance gate; the small native probe isolates
the category collision itself.

The related rebind-after-first-meld repair landed at 0.2.8219. Four isolated native rebind
cases pass on 0.2.8220. This epic tracks the later annotation/category collision, not another
codegen or removal/rebind repair.

## Owner Decision Already Recorded

The owner clarified in the MelderOps Actions story that a spellframe name such as "spectrum"
is a category, not a spell. Keep the MelderOps category and named bindings. A Spectrum type
annotation must not make every member of that category a Spectrum provider. Native matching
semantics need review before any implementation is chosen.

## How MelderOps Binds and Constructs These Objects

The paths below are in the sibling priv_commandops repository. They are review pointers;
their current SHA256 values are recorded under Evidence Pins.

| Boundary | Current behavior | Source |
| --- | --- | --- |
| Address labels | CommandCenterDefinitions.SPECTRUM is "spectrum"; COMMAND_CENTER is "command_center". The table assigns each framework class one area. | ../priv_commandops/src/melder_ops/command_center/spectrum/bootstraps/command_center_definitions.py:103-116,270-280,310-352 |
| Host declaration | SpectrumHostBootstrap binds the Spectrum class as a unique at ("spectrum", "Spectrum"). | ../priv_commandops/src/melder_ops/command_center/spectrum/bootstraps/spectrum_host_bootstrap.py:75-94 |
| Framework inputs | MelderRuntime binds the actual MelderConfiguration, SpectrumConfig, IrisConfig and InterchangeConfig instances as named uniques in "spectrum". | ../priv_commandops/src/melder_ops/command_center/spectrum/melder_setup/runtime.py:345-395 |
| Managers | FrameworkManagersBootstrap binds 14 manager/service classes as uniques at their table-assigned spellframes with class-name bindings; many use the "spectrum" category. | ../priv_commandops/src/melder_ops/command_center/spectrum/bootstraps/framework_managers_bootstrap.py:78-103 |
| Center declaration | MelderRuntime binds CommandCenter as a many class at "command_center", then finalizes the target with validation. The ambiguity is raised here, before any center instance exists. | ../priv_commandops/src/melder_ops/command_center/spectrum/melder_setup/runtime.py:397-445 |
| Consumer contract | CommandCenter.__init__ requires keyword-only spectrum: Spectrum and stores it as a borrowed host. | ../priv_commandops/src/melder_ops/command_center/command_center.py:118-196 |
| Consumer construction | After configure, Spectrum creates the center scope and calls conduit.meld("command_center", override={..., "spectrum": self, ...}). That override occurs too late to prevent the earlier bind-time Phase 3 ambiguity. | ../priv_commandops/src/melder_ops/command_center/spectrum/spectrum.py:1557-1691 |

## Native Matching Path to Review

- src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_3.py:185-230:
  _annotation_key normalizes a class or string to a lowercase key; _spell_keys returns
  both the normalized spellframe key and normalized spell-name/type key.
- src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_3.py:233-365:
  the scan accepts either key, and _build_candidate_index inserts every spell under
  both. A category member therefore enters a plain type-annotation candidate bucket.
- src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_3.py:365-495:
  the indexed lookup and _resolve_single_by_annotation reject multiple candidates.
- src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_3.py:761-887:
  the local-frame DAG invokes single-annotation resolution during structural validation.
- src/melder/utilities/helpers/general_helpers.py:239-271:
  normalize_frame_key lowercases class names, strings, and fallback values.

## MRP Alignment

Ordinary type injection must identify providers without silently broadening a category into
a type. Callers should be able to group many definitions under a spellframe while still using
truthful constructor annotations. Explicit address selection remains available for intentional
category/binding lookups. The native matcher, its indexed path, and its scan path need one
coherent contract before a repaired wheel is accepted by MelderOps.

## Ticket Contract
- ENTRY_GATE: Owner requested this evidence epic for Anthropic review. This draft assigns no
  native source writer and authorizes no implementation or application test run.
- EXECUTION_BOUNDARY: Native annotation candidate selection, explicit address/category
  selection, index/scan parity and focused regressions. MelderOps bindings are consumer context.
- DEPENDENCIES: The saved four-case public-API probe, installed 0.2.8220 receipt, owner category
  ruling, and existing rebind epic as a distinct completed-fix boundary.
- EXIT_GATE: Owner-approved semantics are implemented and reviewed; class/string public-API
  category cases and relevant native regressions pass on a verified delivered build; the
  unchanged Actions replacement test is rerun against that build and its outcome adjudicated;
  normal Melder documentation/version/build obligations and ticket closure are complete.
- FAILURE_ESCALATION: If Protocol/frame or string-annotation contracts conflict with the
  proposed type/category separation, return a concrete design decision before source edits.

## Goals (Outcomes)
- A Spectrum annotation selects the Spectrum provider even when other classes share
  spellframe="spectrum".
- A spellframe remains a category; explicit spellframe/binding_name or SpellMap addressing
  retains its intentional selection semantics.
- Class, string and ForwardRef annotations, existing-object registrations, and the indexed
  and scan resolvers follow one documented matching contract.

## Non-Goals
- Renaming the MelderOps "spectrum" category or CommandCenter.spectrum parameter.
- Widening a truthful constructor annotation to Any/object or adding a default workaround.
- Changing the already repaired first-meld/rebind lifecycle or rerunning its accepted native
  cases without changed bytes or a specific new defect.
- Claiming the Actions integration is green before its unchanged test passes on a repaired wheel.

## Scope and Proposed Review Sequence
1. Anthropic reviewers inspect the native matcher, helper, public bind/meld API and existing
   Protocol/frame semantics. Record which annotations mean type providers and which syntax
   explicitly selects a category/address. Do not infer this from normalized name equality.
2. The assigned native maintainer designs the smallest correction and paired indexed/scan
   regressions. The owner resolves any compatibility tradeoff before implementation.
3. After review and source repair, run the four-case public-API probe and focused native
   regression selection on the exact new source/wheel. Preserve raw JUnit and full hashes.
4. Install the verified repaired wheel in the MelderOps application environment under one
   runner lease, then run the unchanged Actions replacement case. Record any separate failure.

## Acceptance Criteria
- The four-case probe passes all class/string and category-control variants on a delivered
  Melder build; unrelated category members are absent from type-provider candidates.
- Explicit frame/binding-name lookup, Protocol/frame semantics and existing-object injection
  retain their reviewed behavior; indexed and scan candidate membership agree.
- The unchanged Actions replacement test passes, or a new independent failure is recorded
  and routed without claiming this epic's consumer exit gate.
- Saved source, wheel, test and JUnit hashes identify the actual validated bytes.
- No MelderOps-side rename, Any/default, private cache edit or premature owner-acceptance claim.

## Evidence Pins and External References

| Evidence | SHA256 or result |
| --- | --- |
| Current native matcher, compiler_phase_3.py | F6D5A4CD99E44C381F646C1410D722E06B7898FB2F9669D409A6F72982793032 |
| Current native normalization helper, general_helpers.py | 736FB07FF0C9A2BD4B7FDC136A8115C1F8CBD814B07B1BBE501A06E7FB506C65 |
| Public-API probe script in priv_commandops | 8DC6BBC74BDE30895121B38B07323F7BC6482E06AD8F120160DB2607F94AECEA |
| Four-case JUnit in priv_commandops | 2F1647407270405357B2ACB4EBD89D404CCB3D5AFCAA851A5777556343D7FBAE; 2 pass / 2 fail |
| Installed Melder 0.2.8220 wheel in priv_commandops | 0FD76ED964AEB42470148B734CC0599A271A2F88562A860692F330D355F940DD |
| Unchanged Actions single-case JUnit in priv_commandops | C5E0E76A4AFAA1E598FD9A764C3035C283F129DF90692482CB3136570C4BE9CE; 1 error |

- ../priv_commandops/context_compass/artifacts/2026-10-03_actions_native_factory/test_spectrum_category_collision.py
- ../priv_commandops/context_compass/artifacts/2026-10-03_actions_native_factory/category_collision_receipt.json
- ../priv_commandops/context_compass/artifacts/2026-10-03_actions_native_factory/category_collision.xml
- ../priv_commandops/context_compass/artifacts/2026-10-03_actions_native_factory/opus_actions_acceptance_receipt.json
- ../priv_commandops/context_compass/tickets/stories/2026-10-03_actions_native_factory_story.md
- tickets/epics/2026-10-03_rebind_after_first_meld_epic.md

MelderOps binding files at this handoff: runtime.py 0FAB092F, spectrum.py 71B7382A,
command_center.py CAAB12B8, framework_managers_bootstrap.py E5B295DB,
spectrum_host_bootstrap.py 7A7ACEEB and command_center_definitions.py 24D85FA1
(SHA256 prefixes, full hashes available from the source files).

## Open Questions for Anthropic Review
- What exact public syntax distinguishes type-provider injection from intentional category
  selection when a class name and spellframe normalize to the same string?
- How should string annotations and ForwardRefs retain parity with class annotations without
  making every same-named category member a provider?
- Which Protocol/shape-frame use cases intentionally rely on spellframe matching, and how
  should those continue to work after type/category separation?
- Can the indexed and scan paths share the same candidate predicate without a fallback
  that hides ambiguity or materially regresses hot-path resolution?

## Risks / Mitigations
- Changing native candidate matching may break supported Protocol/frame resolution. Review
  those callers and regressions before selecting a predicate.
- A narrow class-only fix could leave string, ForwardRef, existing-object or indexed/scan
  paths inconsistent. Validate each path explicitly.
- The real Actions test can still expose another issue after host configure succeeds.
  Preserve its exact JUnit and classify any later failure independently.
- Concurrent MelderOps source movement can invalidate consumer evidence. Recheck raw hashes
  before application acceptance; do not infer a pass from an older wheel.

## Artifact Links
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS: none created by this draft; external saved evidence is listed above.
- DISPOSITION: retain_as_reference

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS: none
- CONTEXT_TOPICS: annotation/provider versus category semantics
- IF_UNKNOWN: UNKNOWN

## Notes
- DATETIME: 2026-10-03T22:21:08Z
  TYPE: FACT
  CLAIM: The exact public-API probe fails only when the unrelated Toolbox shares the
    "spectrum" category; controls pass for both class and string annotations.
  EVIDENCE:
  - ../priv_commandops/context_compass/artifacts/2026-10-03_actions_native_factory/category_collision_receipt.json
  - ../priv_commandops/context_compass/artifacts/2026-10-03_actions_native_factory/category_collision.xml
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_3.py:185-495
  IMPACT: Native type-provider matching and category membership need separate semantics.
  NEXT: Give this draft and the exact paths/hashes to the owner-selected Anthropic reviewers.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-10-04T11:58:00Z
  TYPE: DECISION
  CLAIM: The native repair landed at Melder 0.2.8222 (fable_1): a spellframe is a string category or a Protocol
    contract (concrete classes refused at bind - Breaking), the binding records its kind, and Phase 3 selects by
    the annotation's kind, so a type annotation never reads a same-named category as its provider set. The exit
    gate's remaining items are owner-owed: the tier run after the final regressions and the unchanged Actions
    replacement test on a delivered 0.2.8222 build.
  EVIDENCE:
  - tickets/tasks/completed/2026-10-04_repair_annotation_kind_matching_task.md:14-24
  - tickets/stories/2026-10-03_annotation_type_vs_category_matching_story.md:157-172
  IMPACT: program direction settled; the epic closes on the owner's acceptance report.
  NEXT: owner runs the tiers and the Actions case; a failure opens a new task under this epic.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

## Context / Handoff Summary
Draft epic only. No native source, test-suite, version, wheel, shared board or artifact-board
write is part of this creation. The owner will select Anthropic reviewers and an implementation
owner after reading the public-API reproduction and binding context. No review or fix is claimed.
