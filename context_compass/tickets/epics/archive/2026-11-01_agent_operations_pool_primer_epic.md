> **Moved to GitHub Issues on 2026-11-07:** https://github.com/Synaptic724/melder/issues/218
> This file is read-only history; the Issue is the live record.

# Epic: Clarify the existing Melder agent cheat sheet and add compact pool guidance

## Metadata
- Epic ID: EPIC-2026-11-01-agent-operations-pool-primer
- Status: draft
- Owner: Melder documentation maintainer; implementation claimant not yet established.
- Agent Name: unassigned
- Agent Role: UNKNOWN; documentation implementation claimant not yet established.
- Priority: p2
- Created: 2026-11-01T11:35:06Z
- Updated: 2026-11-01T11:35:06Z
- Target Window: UNKNOWN; no delivery date committed.
- Related Program/Initiative: Existing agent operating guide; managed spell documentation.

## Problem / Opportunity
The existing top-level `agents/MELDER_AGENT_OPERATIONS.md` is the agent operating cheat sheet
routed by root `agents.md`. It is already substantial: 669 lines / 53,413 bytes at the verified
native baseline. Its core table and lifetime section should make the basic runtime easier to
understand without expanding into a second manual. The current lifetime table omits
`managed_spell_quantity`; scattered pooled-handle cautions do not explain the application-facing
lease/release/reset cycle.

The existing `docs/intermediate/managed-spells.md`, README pool section and intermediate
examples 42-48 already supply the detailed material. Reuse them rather than reproduce them.

## MRP Alignment (Most Reasonable Product)
One concise, source-accurate entry point helps agents choose a supported operation, understand
who owns the object and end its use correctly. Completeness means safe essential guidance,
not exhaustive implementation detail or a new onboarding system.

## Ticket Contract
- ENTRY_GATE: Re-read the current guide, root routing and relevant public pool implementation,
  examples and local claims at the intended source revision; reconcile any newer canonical
  ticket for this same outcome before editing.
- EXECUTION_BOUNDARY: Improve the existing guide's short mental model, lifetime/pool explanation,
  navigation and directly affected evidence/version qualification only. No runtime changes.
- DEPENDENCIES: Existing managed-spell documentation and supported public implementation.
  No dependency on future consumer-specific pooling adoption.
- EXIT_GATE: Final guide satisfies the acceptance criteria; all required checks and distinct
  review are evidenced against its exact revision; any child work is dispositioned.
- FAILURE_ESCALATION: Report a concrete source/prose contradiction or file collision with
  evidence; preserve existing edits and resolve only the affected boundary.

## Goals (Outcomes)
- Explain Melder's definition -> scope -> resolve/use -> cleanup flow more plainly in the
  existing short introduction.
- Let an agent identify when managed pools fit, obtain/use/return a lease safely and find
  the detailed supported guide when needed.
- Keep this a fast operational router, not a longer full reference manual.

## Non-Goals (Explicit Exclusions)
- No new parallel guide, broad onboarding rewrite, pool implementation, logging adoption,
  benchmark, packaging release, API redesign or authority/ACL changes.
- Do not reopen completed managed-pool feature/examples epics or claim consumer adoption.

## Scope Boundaries
- In scope: `agents/MELDER_AGENT_OPERATIONS.md`, with existing anchors and valid safety
  boundaries retained; minimal directly necessary link corrections.
- Out of scope: unrelated sections, generated documentation bundles, runtime/tests source
  changes, dependency updates and release operations.

## State Transition Event
- from_state: draft
- to_state: draft
- transition_reason: Requested bounded documentation epic published; initial draft, implementation not started.

## Success Metrics
- One existing guide remains the entry point; no parallel document.
- One compact pool primer, one small public usage example and links to existing detail.
- Record before/after word and line counts plus changed headings; avoid material net growth
  by replacing or consolidating overlapping prose rather than repeatedly appending.

## Requirements (Functional + Non-Functional)
1. Clarify the short core model in section 1 without recataloguing every subsystem.
2. Add the managed lifetime to the section 4 table and a nearby compact pool subsection.
   Distinguish application managed objects from internally recycled lesser/SpellSpace handles.
3. Explain bind/configure -> meld or injection borrows -> holder uses -> release -> declared reset
   -> reuse. Prefer a small `with root.managed_spell_meld(...)` example using public `md` APIs;
   name `md.ReleaseManagedSpell().release(obj)` for explicit return.
4. Summarize elastic, limited_quantity and queue in a compact table: idle retention versus
   alive-object capacity, refusal versus bounded waiting. Verify exact current behavior;
   do not imply a queue is a background worker, FIFO fairness or a constructor deadline.
5. Make ownership/lifetime explicit: root owns the pool; the holder returns each borrowed
   object once and stops using it afterwards. Request holders should finish before root
   teardown. Reset is not disposal; do not imply root teardown disposes still-leased objects.
   Do not promise raw-release identity checking or thread safety of a shared lease wrapper.
6. Explain reset-failure and exhaustion consequences briefly, linking details instead of
   embedding full edge-case tutorials. Preserve HOST/AGENT authority distinctions.
7. Add a fast-routing pool link and source-lookup/deeper-guide pointers. Prefer replacing
   repeated cautions with one authoritative concise statement.
8. Qualify changed content against the actual reviewed source/version; do not relabel all
   historical recipes runtime-verified merely because the new pool example was checked.

## Constraints / Assumptions
Documentation only. The guide has historical version/review pins alongside later targeted
corrections; refresh or qualify affected assertions narrowly, never fabricate a whole-guide audit.
Implementation claimant, source checkout and timing remain unassigned. Existing writer claims prevail.

## Dependencies / External References
- Existing guide: `agents/MELDER_AGENT_OPERATIONS.md`.
- Root routing: `agents.md`.
- Managed spell guide: `docs/intermediate/managed-spells.md`.
- `README.md`, "Managed Spell Quantities".
- `UX_and_AIX_experiences/02_intermediate/42_*` through `48_*`, especially lease/reset/request scopes.
- `src/melder/aether/conduit/creations/managed_spell_quantity.py`.
- `src/melder/aether/conduit/creations/release_managed_spell.py`.
- `src/melder/aether/conduit/creations/managed_spell_lease.py`.
- Public Conduit meld facade: `src/melder/aether/conduit/conduit.py`.
- Completed native pool documentation epic:
  `context_compass/tickets/epics/completed/2026-10-18_managed_spell_examples_and_docs_epic.md`.
  It supplies prior work, not a duplicate of this cheat-sheet update.
- Prepared draft's hosted source pin: `af8c9b9cdf94470a03103bd523bd11f8f8ec1064`.
- Native publication baseline: `de33cff49aa402e04d0f3d5e1e0e65d5b049b3dc`, branch `codex_features2`.
  Guide blob `9c5414330fe7cd0c1f200f0b878f5354dc50c20a` matches the verified hosted guide.
  Implementation entry must resolve the actual current source rather than presume these revisions equal.

## Milestones (Track Progress)
- [ ] Confirm exact current source, existing guide baseline and concise section-level edit plan.
- [ ] Improve the existing guide and validate the changed example/links/claims.
- [ ] Distinct final review; deliver the exact diff, evidence and bounded completion.

## Stories (Required to Complete)
No child tickets created at intake. This explicitly requested epic owns one bounded documentation
outcome. Apply the installed native template/lifecycle when selecting any necessary child work;
do not split ordinary drafting, checking and review into unnecessary parallel outcomes.
If a genuinely distinct outcome emerges, resolve scope before adding it.

## Tasks (Cross-Cutting or Epic-Level)
- [ ] Read relevant source and reuse existing managed-pool detail.
- [ ] Apply the compact guide edit, preserving unrelated user/agent changes.
- [ ] Verify changed example, mode/lifecycle claims, anchors and before/after size.
- [ ] Review final revision distinctly and record criterion-level disposition.

## Acceptance Criteria (Epic Done)
- [ ] Existing guide clearly explains the basic Melder flow and includes managed pools.
- [ ] Compact pool guidance covers public use, modes, release/reset, ownership and end-of-life
  obligations without asserting unsupported guarantees or internals as public operations.
- [ ] At least one small copyable public example is checked against the final supported source;
  positive reuse/reset and exception-safe return are exercised in an authorized disposable environment.
- [ ] Links/anchors resolve; lifecycle statements agree with current source and existing detailed docs.
- [ ] Before/after size and diff demonstrate a focused edit, not broad expansion.
- [ ] Exact source, actual commands/results and intentional review are recorded; unrun checks
  remain unrun and no documentation change is claimed before it exists.

## Risks / Mitigations
- Conflating scope-shell recycling with managed application objects: state the distinction once.
- Confusing reset, release and disposal: show one explicit lifecycle and link the full guide.
- Version drift or concurrent edits: pin inputs, re-read before writing and preserve unrelated text.
- Overlong guide: replace/consolidate, reuse links, omit internal algorithms and duplicated lessons.

## Applicable Anti-Patterns
- [ ] No documentation completion claim from ticket publication.
- [ ] No pool safety/performance guarantee without source/evidence.
- [ ] No duplicate tutorial or rewritten unrelated onboarding.
- [ ] No takeover of another writer's current source or execution record.

## Validation / Test Approach
Source-to-prose review of changed claims; Markdown/link/anchor check; execute the new/changed
small example on the supported Python/Melder baseline under existing authorized test practice.
Use existing pool examples/tests as references, not inherited proof that this edit ran.
No tests or implementation performed by this ticket-composition step.

## Rollout / Adoption Plan
Land the guide edit through the existing repository documentation workflow. Existing
`agents.md` continues pointing to the same file; no new entry point or release needed.

## Open Questions
Actual implementation claimant and final source revision are resolved at entry. Technical
facts are discoverable from source; no new product design decision is requested.

## Decision Log
2026-11-01: Mark requested an epic to make the existing agent cheat sheet clearer and add compact
pool guidance; prefer clarification/replacement to growth. Implementation is not started.
2026-11-01T11:35:06Z: Publish one unassigned draft through the configured native local ticket backend.
No GitHub mirror, implementation claim or active-worker routing is created by this publication.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS: Existing guide and final repository diff; no separate deliverable required.
- DISPOSITION: promote_to_documentation
- CLEANUP_TRIGGER: Completion; preserve validation evidence in the canonical work record.

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS: none
- CONTEXT_TOPICS: Existing guide; managed pool public lifecycle.
- IF_UNKNOWN: none

## Contribution Attribution
- Ticket/Work Author(s): dot; bounded documentation epic composer; prepared draft supplied by parent Ops.
- Ticket/Work Author(s): gpt_ops_1; native template/routing adaptation and publication; this initial native draft.
- Published By: gpt_ops_1; native local filesystem publication on DESKTOP-HCNUTDQ at 2026-11-01T11:35:06Z.
- Independent Review: None claimed. Composition self-review by gpt_ops_1; guide implementation remains unreviewed.

## Notes
- DATETIME: 2026-11-01T11:26:05Z
  AUTHOR: dot
  AUTHOR_ROLE: bounded documentation epic composer
  TYPE: FACT
  CLAIM: Existing guide lacks managed lifetime/compact pool primer; prior full pool documentation exists.
  EVIDENCE:
  - agents/MELDER_AGENT_OPERATIONS.md (blob 9c5414330fe7cd0c1f200f0b878f5354dc50c20a)
  - docs/intermediate/managed-spells.md (prepared draft reports blob cc2fd748f433db6eb6b7d262a5fb2f71ce526783)
  IMPACT: Reuse source-accurate detail and edit the existing entry point only.
  NEXT: Claim the bounded guide edit after current source/custody checks.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-11-01T11:35:06Z
  AUTHOR: gpt_ops_1
  AUTHOR_ROLE: parent-assigned native documentation ticket publisher
  TYPE: FACT
  CLAIM: One requested draft epic published through the selected local backend after exact duplicate recheck.
  EVIDENCE:
  - context_compass/config/context_compass_config.yaml:112-116
  - context_compass/templates/epic_template.md
  - context_compass/tickets/README.md
  - agents/MELDER_AGENT_OPERATIONS.md:1-669
  IMPACT: Native canonical backlog record exists; guide and runtime implementation have not started.
  NEXT: An eligible Melder documentation maintainer establishes implementation custody at entry.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

## Closure Confirmation
- [ ] Work walkthrough shared with user.
- [ ] Criteria, actual checks/review and acceptance recorded.
- [ ] Applicable anti-pattern checks clear or explicitly unresolved.

## Noting Behavior
Record material scope/source/validation decisions with attribution and exact evidence;
preserve prior history without duplicating tactical logs.

## Context / Handoff Summary
Native Context Compass is the configured canonical ticket route in Synaptic724/melder.
No GitHub mirror is created. The fresh duplicate recheck accompanies this publication;
the earlier targeted native search found no same guide/pool-onboarding outcome. Completed pool
documentation remains supporting history. The existing backlog lane holds this unassigned draft,
with no new active-worker board row or execution claim.

No guide edit or runtime test performed. Next owner is an eligible Melder documentation maintainer
after source/custody checks. Reuse existing pool documentation; do not start a broad rewrite or another
product pooling outcome. Publisher returns exact saved content/hash and readback separately.

## Project-Specific Additions
<!-- BEGIN USER-DEFINED: project_fields -->
<!-- END USER-DEFINED: project_fields -->
