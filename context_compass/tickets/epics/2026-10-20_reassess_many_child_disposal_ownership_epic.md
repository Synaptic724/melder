# Epic: Explore disposal ownership of Many dependencies, including possible removal

## Metadata
- Epic ID: EPIC-2026-10-20-reassess_many_child_disposal_ownership
- Status: in_progress
- Owner: Mark (architecture and policy decision)
- Agent Name: melder_1 (executor since 2026-10-24; expert_1 authored revision 1)
- Agent Role: synaptic_python_developer
- Priority: p2
- Created: 2026-10-20T21:59:39Z
- Updated: 2026-10-24T22:09:11Z
- Revision: 1
- Target Window: Unscheduled; no investigation or implementation batch activated.
- Related Program/Initiative: Melder runtime ownership and lifecycle design.

## Problem / Opportunity
Reassess the released feature "A `many` dependency is disposed with the object that holds it."
The question is whether automatic holder ownership remains the right contract when a Many
dependency is injected into a `unique` or another longer-lived holder, escapes that holder,
is handed to another consumer, or has application-managed disposal. Possible removal is an
open architectural option. This epic records no decision to remove or change the feature.

The feature addressed a concrete historical failure: a shorter-lived resolving scope could
dispose a Many dependency while its longer-lived holder remained available. The completed
2026-10-14 Many-child epic records the registration repair in 0.2.8235. The completed slotted
lifetime epic records adoption, holder purge and transfer behavior in 0.2.8238 and the later
owner ruling that structural correctness does not imply policing arbitrary userland objects.
Those completed records remain history, with their authorship and completion intact.

The opportunity is a decision-ready ownership model that distinguishes construction provenance,
an ordinary Python reference and a disposal obligation. A retained reference to a disposed object
or an application callback that disposes a dependency twice is a risk to examine against that
model, not a newly proven defect. This pass authors the epic; it does not reproduce such risks.

## MRP Alignment (Most Reasonable Product)
The smallest complete outcome is an evidence-backed comparison and an explicit owner decision.
It must preserve the rationale for the existing rule and explain the complete lifecycle of
every proposed replacement. Removing automatic adoption without specifying who disposes each
dependency would leave the core contract incomplete. Keeping it without explaining escaped
references and application disposal would leave the user's responsibility unclear.

## Ticket Contract
- ENTRY_GATE: This draft is authorized as one local canonical epic. Before future investigation,
  a verified authorized assignment names its scope and investigator, who verifies current source
  and follows the local execution gates. Saving this draft starts no execution lane.
- EXECUTION_BOUNDARY: Current permission is ticket authorship and saved-record readback only.
  The proposed epic concerns Many dependency ownership, alternatives, compatibility and test
  design. No implementation, product tests, release notes, generated assets or external writes.
- DEPENDENCIES: The released 0.2.8265 contract; both completed 2026-10-14 ownership epics; current
  Creations and site-plan lowering source; Mark's retained architecture-decision authority.
- EXIT_GATE: If exploration is later activated, a current-source dossier covers every lifecycle
  case below, compares all three alternatives, proposes discriminating checks and migration,
  and records Mark's decision or explicit deferral. Ticket creation alone does not satisfy it.
- FAILURE_ESCALATION: Preserve a missing source, real ownership collision or denied operation;
  stop only the affected work and identify its actual unblock owner. Ask Mark about unresolved
  architecture choices. Do not execute a proposed option or substitute another ticket route.

## Goals (Outcomes)
- Explain why automatic adoption was introduced and which guarantees users now depend on.
- Compare retaining the rule, explicit ownership choices and removing automatic adoption.
- Define the intended handoff point and the responsibility when construction never reaches it.
- Separate runtime-owned disposal records from references retained or reassigned by application code.
- Produce an owner-selectable contract, compatibility impact and proposed acceptance matrix.

## Non-Goals (Explicit Exclusions)
- Selecting removal, an opt-in default or an ownership-transfer API in this draft.
- Runtime changes, test execution or new test files, benchmarks, release notes or asset rebuilds.
- Creating child tickets, scheduling work, assigning another agent or starting implementation.
- A separate cluster/shared-object investigation or ticket; that request was canceled.
- Changes to cluster membership, leadership, shared-store policy or MelderOps MO180.
- Reopening or rewriting completed epics, the parked existing-object redesign or current boards.
- Tracking arbitrary live references, relying on garbage collection or revoking Python references.
- Redesigning managed pools, lease/release behavior or all existing-object bindings.

## Scope Boundaries
- In scope: Many dependencies constructed for `unique`, `unique_per_conduit`,
  `unique_per_spell_space`, `unique_per_conduit_lineage` and `unique_per_conduit_cluster` holders;
  direct Many and Many-under-Many controls; disposal-bearing and non-disposal-bearing cases;
  successful publication, failure before handoff, purge, store teardown, escape and transfer.
- In scope: Existing holder-transfer options and rollback as compatibility surfaces of this
  feature. Naming the cluster lifetime here covers its existing holder behavior only.
- Out of scope: Every product mutation and executable investigation in the current ticket-only
  pass. Future work requires its own selected scope; this draft grants no additional authority.
- Write boundary now: This epic file only. Preserve README, release files, completed records,
  attention/mailbox/artifact boards and all unrelated work byte-for-byte.

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason (2026-10-24, melder_1): the owner chose removal (DECISION note of 2026-10-24T19:58:35Z);
  STORY-2026-10-24-remove_many_child_holder_ownership carries it. Revision 1's draft transition follows.
- from_state (revision 1): draft
- to_state (revision 1): draft
- transition_reason: Initial planning record saved under ticket-only authorization. No execution
  transition, policy selection, implementation acceptance or historical-ticket reopening occurs.

## Success Metrics
- One canonical exploration epic, with no duplicate local or GitHub implementation record.
- Three comparable alternatives, each accounting for construction, ownership handoff and disposal.
- Every lifecycle row below has a proposed observable check and a named unresolved decision.
- No unsupported claim of a present defect, successful test, adopted API or assigned executor.
- A future decision states compatibility, migration and the exact remaining authorized work.

## Requirements (Functional + Non-Functional)
### Baseline and rationale
- F1: Trace the released rule by construction route and holder lifetime. Distinguish a child
  built for the holder from a caller-supplied override, a separately melded object and a later
  field assignment. Do not infer ownership by inspecting arbitrary Python attributes.
- F2: Preserve the historical rationale: wrong-scope disposal under a live holder, children left
  behind during a holder move, and children retained after holder purge. Historical red/green
  receipts explain those fixes; they do not prove a new defect or requalify the current source.
- F3: Account for holders with no disposal methods. Current adoption can create a holder record
  with an empty method list so its disposal-bearing children still have a recorded owner.

### Alternatives requiring an owner decision
| Alternative | Contract to explore | Benefit to assess | Cost or unresolved obligation |
| --- | --- | --- | --- |
| Keep automatic adoption | A constructed Many dependency's disposal record follows its slotted holder. | Preserves the released protection and holder purge/move behavior. | Explain escape, manual disposal and the exact limits of inferred ownership. |
| Make ownership explicit | Compare an opt-in rule with a deliberate adoption/release/ownership-transfer operation. No API or default selected. | Makes disposal responsibility expressible at a defined boundary. | Decide where policy belongs, what absence means, transfer/failure atomicity and migration. |
| Remove automatic adoption | Specify the replacement owner and disposal trigger for each route before proposing removal. | May simplify the model when injection should provide only a reference. | Avoid silently restoring early disposal; account for orphaned children, cleanup duties and breaking behavior. |

- F4: Compare the options with the same scenarios and evidence. Include keeping the current
  default while documenting its limits; do not make API expansion a prerequisite for a decision.
- F5: For opt-in or explicit handoff, decide whether policy attaches to the dependency binding,
  holder binding or injection edge; distinguish disposal-method configuration from ownership.
  No proposed name, flag, method signature or default becomes an adopted contract here.
- F6: For removal, distinguish removing adoption from removing disposal registration entirely.
  Specify whether a dependency remains scope-owned, becomes caller-owned, or uses another
  explicitly selected owner. Evaluate each consequence instead of assuming the old model is safe.

### Lifecycle cases to resolve
- F7: Specify the successful ownership-handoff point, its publication/adoption ordering and its
  observable guarantees. Keep failure before holder construction/publication separate from a
  successfully published holder: no completed handoff may be assumed when the holder never exists.
- F8: Define responsibility for each child already built when a later child, the holder
  constructor, publication or a callback fails. Include a losing cold-build race and retry.
  Determine disposal timing and error propagation without assuming immediate disposal is required.
- F9: Cover direct Many and Many-under-Many independently. A policy for longer-lived holders
  must not silently change the resolving scope's existing transient cleanup obligations.
- F10: Cover disposal binding: no matching methods, explicit per-bind names, book-level candidates,
  method order, and a holder's callback that also disposes a child. Separate one runtime disposal
  obligation from arbitrary application calls; do not assume every disposal method is idempotent.
- F11: Cover escaped child references, a retained holder after purge/teardown, reassignment into
  another holder and deliberate external ownership transfer. Identify whether each is an ordinary
  reference handoff or a supported transfer of disposal responsibility; document who owns it next.
- F12: Compare holder purge, direct child-spell purge and live-creation probes, repeated purge/meld,
  whole-store teardown, disposal failure aggregation and holder-before-child ordering.
- F13: Cover `transfer_spell_ownership` with `move_creations=True` and `False`, failed transfer
  rollback and an already-populated receiving slot. Preserve the distinction between moving
  recorded children and transferring every dependency or delivering a working application setup.
- F14: Map the boundary with managed objects' separately recorded children and caller-supplied
  instances. Preserve their current contracts unless Mark explicitly expands this exploration.

### Compatibility and evidence
- N1: For each option, identify changed user obligations, cleanup timing, error surfaces, purge
  counts/probes, transfer rows, codegen/specializer eligibility, cache admission and persistence.
  Determine whether any record/cache format or binding-manifest change is actually necessary.
- N2: Propose upgrade and downgrade behavior, old/new policy coexistence and migration guidance.
  A deprecation period or compatibility adapter is an option to evaluate, not already selected.
- N3: Preserve keyed store operations and current lock-order boundaries as design constraints.
  Assess cold construction, warm meld and teardown costs; make no unmeasured performance claim.
- N4: Use complete relevant source units and pinned evidence for future conclusions. Keep observed
  code, historical reports, hypotheses and unrun checks distinct. No reference-count/GC guarantee
  or global exactly-once disposal claim may be inferred from the current record representation.

## Constraints / Assumptions
- Melder is an agent runtime. Structural ownership and application object validity are distinct;
  a retained reference alone does not prove wrong structure or a defect.
- The released behavior stays the baseline until Mark explicitly selects another contract.
- An explicit disposal name configures a callback; it does not by itself settle ownership intent.
- This draft is not an implementation design approval, a test receipt or a new work assignment.
- Current source was inspected selectively for the stated baseline, not audited end-to-end.

## Dependencies / External References
- Published feature and release: https://github.com/Synaptic724/melder/releases/tag/0.2.8265
- Release tag commit: `2d6c75233f530b9f044a57832e0d74d620503c41` (verified GitHub ref).
- Local source base: `2f17867cddd608e66103e56c96f7fa5af995cdbd`, branch `codex_features2`.
- Both commits have source tree `2e8ba6af3fbe139018b84b3ce9b24937544e35e3`; docs and curriculum
  trees also match. This establishes source identity, not executable qualification.
- `context_compass/tickets/epics/completed/2026-10-14_many_child_follows_holder_epic.md`
- `context_compass/tickets/epics/completed/2026-10-14_slotted_lifetime_ownership_fixes_epic.md`
- `context_compass/tickets/epics/backlog/2026-09-13_existing_object_lifecycle_ownership_epic.md`
  is a related, owner-parked supplied-object redesign; leave it parked. Coordinate only if a
  later selected design actually intersects it. It is not this outcome's canonical record.
- `src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/site_plan_lowering.py`
  (`SitePlanEmission._place`, `_emit_context`, `_emit_many`, `_emit_miss`).
- `src/melder/aether/conduit/creations/creations.py`
  (`HolderDisposalEntry`, `adopt_children`, disposal, purge, extract/restore).
- `src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py`
  is a future full-route investigation target, not fully reviewed in this authoring pass.
- `src/melder/aether/spellbook/bind/bind.py` and binding-manifest/restore/cache machinery are
  future impact-map targets if explicit policy or removal is selected for investigation.
- Existing regression entry points to reread before any separately authorized executable work:
  `tests/component/melder/aether/conduit/test_conduit_component_many_child_disposed_with_its_holder.py`
  `tests/integration/melder/conduit/test_conduit_integration_many_child_disposed_with_its_holder.py`
  `tests/integration/melder/conduit/test_conduit_integration_holder_children_lifetime.py`
  `tests/unit/melder/aether/conduit/creations/test_creations_holder_children.py`

## Milestones (Track Progress)
- [x] M0: Save a source-pinned, self-reviewed exploration epic within the ticket-only boundary.
- [ ] M1: Investigation scope and investigator selected through verified project authority.
- [ ] M2: Source-backed scenario matrix and three-option comparison delivered, if authorized.
- [ ] M3: Compatibility/migration and proposed acceptance agreed; Mark decides or explicitly defers.

## Stories (Required to Complete)
- [x] Story: STORY-2026-10-24-remove_many_child_holder_ownership - remove holder ownership of `many`
  dependencies: a `many` belongs to the scope that built it (melder_1, on the owner's decision of 2026-10-24;
  done 2026-10-24, notched 0.2.8267: tickets/stories/completed/2026-10-24_remove_many_child_holder_ownership_story.md).
Revision 1's text, before the decision:
No child stories are created or assigned by this pass. Proposed workstreams, if later selected:
- [ ] Establish current ownership and failure/handoff semantics across the required routes.
- [ ] Compare the three policy alternatives and escaped/transferred-reference responsibilities.
- [ ] Complete compatibility, migration and discriminating test design for the owner's decision.
These descriptions are planning subjects, not invented story IDs or queued execution.

## Tasks (Cross-Cutting or Epic-Level)
- [x] Search for an existing canonical exploration and preserve overlapping historical work.
- [x] Read the selected full epic composition and relevant rationale/current source.
- [x] Record scope, evidence limits, unselected decisions and the next responsible owner.
- [ ] After authorization, reconcile the selected investigation with actual local routing.
- [ ] After exploration, reconcile all evidence and owner disposition before epic closure.

## Acceptance Criteria (Epic Done)
- A current-source route matrix accounts for every F1-F14 case without conflating a Python
  reference, a supplied override, a constructed dependency and a disposal obligation.
- All three options have explicit lifecycle owners/triggers, pre-handoff failure handling,
  callback/double-disposal analysis, escaped/transfer cases, error behavior and costs/unknowns.
- Compatibility and migration cover existing applications, purge/probes, transfer/rollback,
  generated plans/specialization and any genuinely affected cache or record contracts.
- Proposed tests distinguish the options through observable effects. No proposed or historical
  check is represented as a new passing run; any future authorized runs report exact revisions.
- Mark records retain, explicit-policy direction, removal, or explicit deferral with rationale.
  The epic may complete with a decision to keep the feature; implementation is not required.
- Required exploration evidence/review and actual child/routing disposition are reconciled at
  future closure. This draft remains open; M0 completion is only ticket-authoring delivery.

## Risks / Mitigations
- Early disposal may return under a scope-only replacement: retain the original short-scope,
  live-holder counterexamples as decision controls and require a complete replacement owner contract.
- Double disposal may occur when application callbacks overlap runtime obligations: investigate
  exact callback routes and responsibility; do not label it a present bug without a reproducer.
- Escaped references may outlive their recorded owner: distinguish intended application work from
  incorrect registry ownership, and state the limits of any proposed explicit handoff.
- A child built before a failed holder may be retained: determine intended owner and timing first;
  do not assume every retained object is a leak or that immediate disposal is always correct.
- Removing adoption may change holder purge and transfer even if simple teardown still works:
  evaluate each operation separately, including failure and rollback.
- Scope could spread into supplied-object or managed-pool redesign: keep those contracts as
  boundaries and return an actual expansion decision to Mark before dependent work.

## Applicable Anti-Patterns
- [x] No claim that removal, an opt-in default or a new API has already been approved.
- [x] No new defect asserted from a retained reference or a double-disposal hypothesis alone.
- [x] No historical epic reopened, rewritten, copied as current work or assigned to its old author.
- [x] No implementation, executable checks, child tickets, board/mailbox changes or remote writes.
- [ ] No future epic closure based solely on this draft or historical test receipts.

## Validation / Test Approach
Current pass: source and ticket inspection, separate author self-review and saved-file readback
only. Product tests, examples, benchmarks, builds, coverage and hosted CI: Not run.

The following checks are proposals for an authorized exploration, not new tests or passing results:
| Scenario | Observable evidence the future comparison should obtain |
| --- | --- |
| All five slotted holder lifetimes first built through a shorter resolving scope | Identity and disposal events before/after resolver exit and actual owner cleanup. |
| Direct Many and Many-under-Many | Fresh identities and correct cleanup of the resolving scope's own entries. |
| Holder without disposal methods; child with and without disposal methods | Which disposal obligations are registered and which callbacks actually run. |
| Constructor/later-child failure before handoff | No published holder; account for each built child, its owner and eventual disposal/error. |
| Cold race and retry | One published holder, separate accounting for unused children, no assumed successful handoff. |
| Holder purge, repeat purge/meld and child-spell purge/probes | Target count, replacement identity, surviving obligations and ordered disposal events. |
| Holder callback also closes its child | Separate runtime calls from application calls; establish whether duplicate disposal is intended, rejected or mitigated. |
| Escaped child, retained holder and reassigned child | Record ownership and observable object state independently; identify any supported handoff. |
| Move enabled/disabled, transfer failure and receiving slot already populated | Exact owner/record movement and rollback; no implicit dependency or application-setup promise. |
| One disposal callback raises | Remaining selected callbacks attempted, ordering and visible aggregated failure preserved or explicitly changed. |
| Binding-policy and cache/restore compatibility | Explicit differences for old/new policy and replay; identify actual format/admission changes. |
| Managed and externally supplied boundary controls | Existing separately owned obligations stay within their selected contracts. |

Use event counters/order and real public scope/purge/transfer boundaries where possible. Avoid
wall-clock thresholds and assertions coupled only to private storage shape. Existing tests are
candidate controls to reread, not proof that every proposed case is already covered.

## Rollout / Adoption Plan
No rollout is started. First deliver the comparison for Mark's decision. If he keeps the rule,
record the rationale and any separately authorized documentation work. If he chooses explicit
policy or removal, define a bounded implementation contract, migration and required validation
before authorizing product changes. Release timing, code pushes and publication remain separate.

## Open Questions
1. Does injection of a newly constructed Many dependency imply disposal ownership by default?
2. If explicit policy is preferable, where does it live and what does an unspecified policy mean?
3. What exact event transfers responsibility, and who owns already-built children before it?
4. Should holder purge and owner teardown share one ownership policy, or need explicit differences?
5. Can an escaped/reassigned child transfer disposal responsibility, and through which supported act?
6. How should a holder callback that also disposes its child coexist with runtime disposal names?
7. If automatic adoption is removed, which owner replaces it on every construction/failure route?
8. Which compatibility/migration, cache or persisted-policy consequences follow from each option?
9. Which existing managed/supplied-object boundaries must remain fixed for a useful bounded decision?

## Decision Log
- 2026-10-20: Author one coherent local exploration epic, including possible feature removal as an
  open decision. No implementation, tests, release notes, implementation batch or MO180 changes.
- 2026-10-20: The separate cluster/shared-object ticket request is canceled; no such ticket is created.
- 2026-10-20: Preserve both completed October 14 epics and the parked supplied-object redesign.
  This epic reassesses policy; it does not reverse the historical fixes or their acceptance.
- 2026-10-20: Current record stays draft. Mark owns the architecture choice; future assignments
  use verified project authority. No investigator, implementer or reviewer is assigned here.
- 2026-10-24 (melder_1): the owner chose removal of automatic holder ownership, placement included
  ("lets rip it out because it should behave like autofac"); managed pools and the specializer decline
  stay. The epic moves to in_progress with one story.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS: none newly created; existing evidence is referenced above.
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: None in this ticket-only pass; no artifact or historical evidence is deleted.

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS: none
- CONTEXT_TOPICS: Many dependency ownership; publication handoff; disposal and compatibility.
- IF_UNKNOWN: none; unresolved design questions are explicit above.

## Contribution Attribution
- Ticket/Work Author(s): expert_1; synaptic_python_developer; prose, scoped source inspection and
  proposed exploration/test design; revision 1 at the source/cutoff below.
- Published By: expert_1 to the local filesystem on Mark's machine. No GitHub issue publication.
- Independent Review: None claimed. The author performed a separate scope/evidence self-review.
  No architectural alternative or future implementation is accepted by that review.

## Notes
- DATETIME: 2026-10-20T21:59:39Z
  AUTHOR: expert_1
  AUTHOR_ROLE: synaptic_python_developer; ticket author
  TYPE: FACT
  CLAIM: The existing local backend selects the complete epic template. No equivalent new
    reassessment epic was found in active/backlog/completed local epic searches; GitHub Issue
    queries for Many ownership and holder terms returned no matches. The supplied-object
    lifecycle epic is explicitly parked and has a different outcome. The two October 14 epics
    are completed historical prerequisites, not active redesign or replacement tickets.
  EVIDENCE:
  - context_compass/config/context_compass_config.yaml:112-135
  - context_compass/templates/epic_template.md:1-164
  - context_compass/tickets/epics/backlog/2026-09-13_existing_object_lifecycle_ownership_epic.md:3-15
  - context_compass/tickets/epics/completed/2026-10-14_many_child_follows_holder_epic.md:3-23
  - context_compass/tickets/epics/completed/2026-10-14_slotted_lifetime_ownership_fixes_epic.md:3-23
  IMPACT: One new local canonical draft is appropriate; no duplicate Issue or historical rewrite.
  NEXT: Route a future scoped investigation through verified project authority when selected.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-20T21:59:39Z
  AUTHOR: expert_1
  AUTHOR_ROLE: synaptic_python_developer; ticket author
  TYPE: FACT
  CLAIM: Source inspection shows children registered before holder construction and adopted
    after publication; adoption moves matching child identities from Many buckets to a holder
    record. Disposal attempts the holder then its recorded children, and extraction/restoration
    carries those children. These observations anchor the questions; no risk was reproduced and
    no new executable qualification is claimed. Release-tag/source identity was verified at
    observation cutoff 2026-10-20T21:58:26Z; local source base is 2f17867cddd608e66103e56c96f7fa5af995cdbd.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/site_plan_lowering.py:1543-1632
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/site_plan_lowering.py:1683-1772
  - src/melder/aether/conduit/creations/creations.py:1021-1106
  - src/melder/aether/conduit/creations/creations.py:580-611
  - src/melder/aether/conduit/creations/creations.py:1313-1423
  - src/melder/aether/conduit/creations/creations.py:1538-1760
  - https://api.github.com/repos/Synaptic724/melder/git/refs/tags/0.2.8265
  IMPACT: Keep pre-handoff failure and escaped-reference/double-disposal questions explicit,
    without describing a policy hypothesis or historical fix as a newly proven runtime defect.
  NEXT: Obtain a future scoped assignment if the comparison is selected; all three options remain open.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-24T19:04:39Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: The owner's position (chat 2026-10-24): "if I meld an object that has transient objects, its up to the
    users dispose rule to cleanup the objects inside it, we don't need to take over their responsibilities, unless
    the conduit is cleaned up as a path". Autofac's documented model matches it: an object is disposed when the
    scope that resolved it ends; a singleton, and a transient injected into it (a captive dependency), live until
    the container is disposed; the one cascade is the opt-in Owned<T>, whose disposal ends its own scope and
    releases the object and its non-shared disposable dependencies; ExternallyOwned is never disposed. Today's
    purge of a slotted holder detaches its HolderDisposalEntry and disposes the holder, then its adopted children
    newest first - that cascade, applied to every holder unasked. Proposed to the owner: a holder's purge runs only
    the holder's disposal methods; whole-store disposal, transfer carriage and the child-spell purge exclusion stay.
    Open with the owner: after that purge, keep the children on the conduit's record (Autofac's way; a second close
    when the holder's own rule closed them) or forget them (the holder's rule is the only closer).
  EVIDENCE:
  - src/melder/aether/conduit/creations/creations.py:580-610
  - src/melder/aether/conduit/creations/creations.py:1313-1422
  - https://autofac.readthedocs.io/en/latest/lifetime/disposal.html
  - https://autofac.readthedocs.io/en/latest/advanced/owned-instances.html
  - https://autofac.readthedocs.io/en/latest/lifetime/captive-dependencies.html
  IMPACT: Removal of the purge cascade has the owner's direction; the keep-or-forget answer decides what a holder's
    purge does with the children's records. No src edit until a routed lane exists.
  NEXT: Record the owner's keep-or-forget answer here as a DECISION, then open the change lane on his word.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-24T19:53:57Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: ALIGNMENT_CHECK
  CLAIM: The owner's scope (chat 2026-10-24, pointing at the release-note section he pasted): "when you cleanup a
    unique of any kind its many types are also cleaned up just because thats the new feature you guys added" and
    "we're not talking about purge". He wants the feature removed, not the purge-only change the FACT note above
    proposed. Restated to him for his go: a `many` dependency built for a slotted holder is recorded and disposed
    by the scope that builds it, like any `many` (the spellspace, else the conduit); a holder's cleanup runs only
    its own disposal methods, and what it holds is its own dispose rule's business. The 0.2.8235 placement and the
    0.2.8238 adoption go, and the release note is rewritten; the 0.2.8234 result returns (a lesser or spellspace
    that built the holder closes its `many` when it ends while the holder lives on), which his rule leaves to the
    user.
  EVIDENCE:
  - release_docs/next_version_release.md:213-267
  - src/melder/aether/conduit/creations/creations.py:1021-1106
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/site_plan_lowering.py:1543-1582
  IMPACT: The FACT note's purge-only proposal is superseded: the change reverts the whole feature.
  NEXT: On the owner's go, record his DECISION here and open the lane (story, board row, patch, failing tests first).
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-24T19:58:35Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION
  CLAIM: The owner's decision (chat 2026-10-24): "yeah so lets rip it out because it should behave like autofac not
    mysteriously cleanup transient objects". Alternative selected: remove automatic adoption AND the 0.2.8235
    placement, as restated in the ALIGNMENT_CHECK above: a `many` dependency built for a slotted holder of any kind
    is recorded and disposed by the scope that builds it (the spellspace, else the conduit), like any `many`; a
    holder's cleanup runs only its own disposal methods; what the holder holds is its own dispose rule's business.
    Replacement owner per route (F6, F7): the resolving scope's store, at registration, before the holder exists.
    Out of scope unless the owner widens it: managed pools' separately recorded children (F14) and the opt-in
    specializer's decline of many-into-holder graphs, which stops an unused dependency being built on every warm
    meld and is not ownership.
  EVIDENCE: release_docs/next_version_release.md:213-267
  IMPACT: The epic moves from draft to in_progress with melder_1; one story carries the removal under the patch
    gate, its notch, the release-note rewrite and the rebuild.
  NEXT: Open the story and its board row, then the patch, then failing tests.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-24T22:09:11Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: The owner's decision is implemented: STORY-2026-10-24-remove_many_child_holder_ownership is turned in at
    0.2.8267. A disposal-bearing `many` built for any slotted holder registers in the meld's innermost scope, a
    holder's cleanup runs only its own disposal, the 0.2.8235 placement and the 0.2.8238 holder record are removed;
    managed pools' recorded children and the specializer's decline are unchanged (F14 and the decision's scope). The
    release note leads its section with the Breaking change and the remedies (meld the holder where it lives, or
    leave the dependency without disposal methods). Per lifecycle row: the replacement owner is the resolving scope's
    store (F6-F7); a child built before a failed holder stays in that store like any `many` (F8); purge, probes and
    transfer follow the store that recorded the child (F12-F13). The rebuild runs last in the story.
  EVIDENCE:
  - context_compass/tickets/stories/completed/2026-10-24_remove_many_child_holder_ownership_story.md:1-8
  - release_docs/next_version_release.md:213-277
  IMPACT: The owner's decision is recorded and carried out; the exploration criteria it made moot (the full route
    matrix and three-option dossier) stay unticked, so closing the epic on that decision is the owner's call.
  NEXT: Ask the owner whether to close the epic.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

## Closure Confirmation
- [ ] Exploration walkthrough delivered and owner disposition recorded.
- [ ] All epic criteria and applicable required evidence/review satisfied.
- [ ] Actual child/routing disposition reconciled under the then-current authorized scope.
Ticket authoring is delivered separately; these unchecked boxes keep the exploration open.

## Noting Behavior
- Record cross-workstream findings, alternative tradeoffs, decisions and remaining boundaries.
- Keep historical Notes append-only; update the single current resume view at material changes.
- Attach exact source/revision evidence and distinguish hypotheses from reproduced behavior.
- Child evidence may be linked if actual children are authorized later; do not invent their IDs.

## Context / Handoff Summary
Current (2026-10-24T22:09:11Z, melder_1): the owner decided removal - a `many` dependency belongs to the scope that
built it, and a holder's cleanup runs only its own disposal (DECISION note of 2026-10-24T19:58:35Z) - and
STORY-2026-10-24-remove_many_child_holder_ownership carried it out at 0.2.8267 (turned in; FACT note above).
Next: the owner's word on closing this epic. Revision 1's summary follows as written.

Revision 1 is a local, ticket-only draft exploring whether to retain, make explicit or remove
holder-owned Many disposal. Source base 2f17867cddd608e66103e56c96f7fa5af995cdbd matches released
0.2.8265 source at 2d6c75233f530b9f044a57832e0d74d620503c41; cutoff 2026-10-20T21:58:26Z.
Rationale and selected current store/emission paths were read; the scenario matrix and validation
remain proposals. No product tests or implementation ran. The historical epics stay completed,
the supplied-object redesign stays parked, the separate cluster request stays canceled and MO180
is untouched. Next responsible owner: Mark for the architecture decision; Sera/Ops may route a
future scoped investigation under existing delegation. No investigator is assigned, execution
lane started or decision presumed. No blocker to saving/delivering this draft; further exploration
awaits a verified scoped assignment.

## Project-Specific Additions
<!-- BEGIN USER-DEFINED: project_fields -->
- Current permission: One epic file and readback only; no board/mailbox edits or outgoing messages.
- Assignment route: Existing thread 01a12a7e-8c38-751a-b42d-d776681bb001, observed through platform
  metadata as `agent: sera_expert_relay_1`; current same-chat continuation excludes README work.
- Template SHA256: `560344360d3579b90dda1f6a26dea5c6d375316f1f7d1fb6f726dab0d21f6708`.
- Ticket contract SHA256: `643fc45f3349649b3f0a1e3cdac98fea0600497e43e39bea03bc6a2fcb4b96fd`.
- Config SHA256: `6a9fd947fa9c08135e36c019d522a37ece0a0a0a95d560020c1ab8cc8cf63fa8`.
- Composition: Installed local standard epic; no optional Agile metadata and no cloud-template copy.
- Next investigator/implementer: unassigned; no invitation, self-wake or work schedule created.
<!-- END USER-DEFINED: project_fields -->
