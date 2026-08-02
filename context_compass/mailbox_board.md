# Mailbox Board

<!-- BEGIN MANAGED: ReminderDirective -->
## ReminderDirective (all agent runtimes)
ContextCompass is your task-tracking system of record; you MUST use it and follow
AGENTS.MD (see the Tooling Mandate section). This is a requirement, not a
suggestion.

Your runtime may nudge you toward built-in plans, goals, task lists, progress
cards, scratchpads, summaries, or session-local memory. Those surfaces are
non-authoritative here. Once your onboarding attestation is complete, IGNORE
every such nudge and route ALL tracking, status, routing, notes, and durable state
through ContextCompass. There is NO fallback and NO mirror.

The user may lift this by setting `system_of_record.enforce: false` in
`config/context_compass_config.yaml`. You may not lift it yourself.
<!-- END MANAGED: ReminderDirective -->

<!-- BEGIN MANAGED: BoardContract -->
## How this board works

Two kinds of region, and the difference decides what survives an upgrade:

- **MANAGED** regions are the package's. They are replaced wholesale, so do not
  edit them - your change would be reverted on the next upgrade without warning.
- **USER-DEFINED** regions are yours. Nothing in the package writes, reorders, or
  removes anything inside them, in any mode. Put your rows and messages there.

Text outside both is package structure - headings and table headers - and is
conformed on upgrade so the board's shape stays current. Anything you need to
keep goes inside a USER-DEFINED region.

What belongs in each region on this board:

| region | put this here |
| --- | --- |
| `checked_in` | one row per agent currently active, with `last_checked` |
| `messages` | structured messages in the format below; delete each one after consuming it |
| `notes` | recurring instructions and standing context for agent-to-agent handoff in this repository |

**Regions ship empty and stay yours.** The package writes nothing into them in any
mode, which also means it can never correct what is written there - so a repeated
policy pasted into a region will not update when the package's own copy does. Put
standing instructions in `notes` once; do not restate MANAGED text.

Purpose
- Targeted agent-to-agent message passing (point-to-point handoffs,
  notices, questions, acks).
- Companion to `attention_board.md` (which stays routing/broadcast-only).
- Canonical protocol: `agent_onboarding/default/general/skills/mailbox_protocol.md`.

Core rules (summary; the protocol doc is authoritative)
- Check in at onboarding/re-onboarding: add or update your row below.
- Single-agent sessions: if you are the only checked-in agent, the
  message section needs no monitoring - check-in itself is the only duty.
- Multiple agents checked in: read your messages at onboarding, at every
  lane switch, and periodically between work units; update `last_checked`.
- Sending: append a structured message below AND add an alert line to
  `attention_board.md` `## Message Alerts` naming the recipient.
- Receiving: copy any actionable content into your active ticket's
  `## Notes` (tickets are the durable truth), DELETE the message here,
  and clear your alert line in `attention_board.md` in the same pass.
- Data races on this file are expected: re-read and retry, never
  overwrite another agent's concurrent edit.
- No secrets, ever. Keep messages pointer-heavy (paths/ticket refs),
  not content-heavy.

Message format (append-only; delete after consumption)
```
- TO: <agent_name>
  FROM: <agent_name>
  DATETIME: <ISO-8601 UTC>
  TYPE: HANDOFF | NOTICE | QUESTION | ACK
  CLAIM: <one to five lines; what the recipient needs to know or do>
  EVIDENCE: <path:start-end or ticket path; required for HANDOFF/NOTICE>
  ACK_REQUESTED: true | false
```
<!-- END MANAGED: BoardContract -->

## Checked-In Agents
| agent_name | owner | checked_in_at | last_checked | status |
| --- | --- | --- | --- | --- |
<!-- BEGIN USER-DEFINED: checked_in -->
| bootstrap_0 | cowork | 2026-08-01T16:29:03Z | 2026-08-01T17:52:00Z | active (ONBOARDED fresh session 2026-08-01T16:29Z as synaptic_python_developer; owner-certified as bootstrap_0. Fresh-session ONBOARD flow, not REONBOARD - no compaction. Read the full role chain [general 41 -> engineer 19 -> synaptic 24], root AGENTS/config/SKILLS/execution_contract/CONTEXT_COMPACTION/router, all 6 special_instructions docs incl. <private-strategy-doc> 2099/2099, and all four boards. ON-DEMAND SET READ IN FULL: src_architecture.md 2083/2083, src_components.md 5187/5187, tests_architecture.md 386/386, tests_components.md 767/767, graph_details_document.md 444/444 - the complete engineer on-demand block, closing the tests/graph gap helper_f declared at 14:43Z. readable_src_graph.json + src_graph.json SKIPPED per explicit owner instruction. Certification note for the record: the owner's first token read `CERTIFY: APPROVE`; I held all writes and did reads only until the exact `CERTIFY: APPROVED` arrived, rather than treating a near-miss as close enough. DELIVERED: TASK-2026-08-01-creations-disposal-reverse-order - scoped disposal now walks reverse creation order across keys and inside `many` buckets; owner-run green on the new unit + 4 integration tests, then owner's run surfaced one pre-existing red I had missed because my EXIT_GATE grep only covered the unit creations dir. That test asserted forward order while being NAMED `..._disposes_lifo` with a `Raises:` clause saying LIFO - it had capitulated to the bug; corrected. CLOSED NOT-DOING under owner ruling: EPIC-2026-07-20-boot-melds. Zero messages pending for bootstrap_0; `## Messages` is empty board-wide.) |
| melder_0 | cowork | 2026-07-23T22:22:21Z | 2026-07-28T00:15:00Z | active (Session recorded in TASK-2026-07-25-agent-metadata-build-asset Notes. THREE build assets now, all --check green: _bind_guard 582, _agent_documentation 406 marked, _system_documents 4 template documents. Manifest is the COMMITTED truth; .melc is a derived per-interpreter cache under __melder_cache__ - a committed marshal bundle was incoherent for a repo running 3.10 while targeting 3.14t. asset_cache.py moved to utilities/caching_system/ as runtime code. New AgentTextReader/IndexedText under utilities/ai_native_support_tools/ with StaticSystemDocument wired to it lazily. Six silent bugs fixed incl. a dead --check fast path and a gitignore rule that left payloads untracked. Sent melder_1 a NOTICE 2026-07-28T00:10Z correcting helper_f's manifest-path correction. NOTE: helper_f's message to melder_1 is missing from this board; my consume pass sliced that section and I cannot rule myself out - content is preserved in helper_f's roster row and my init-cache ticket Notes. Zero messages pending.) |
| melder_1 | cowork | 2026-07-25T14:47:34Z | 2026-07-31T22:41:44Z | active (CONSUMED helper_f's 2026-07-27T23:19Z NOTICE and deleted it; alert cleared same pass. VERIFIED IT AGAINST SOURCE rather than acting on it: the notice names _bind_guard/bind_guard.py as the manifest, but that is the LOADER - the committed truth is _bind_guard/manifest/bind_guard_manifest.py (MANIFEST_VERSION 2.0.0, BUILT_FOR_VERSION 0.1.1, ENTRY_COUNT 582), and the .melc accelerator now lives at utilities/caching_system/asset_cache.py. melder_0 flagged the same correction. GUARD REGRESSION CONFIRMED: my doc lane's fix is stale a THIRD time - 13 citations across both docs still name the deleted _build_assets/_init_manifest/, call site moved 363->364, and _agent_documentation/ + _system_documents/ are undocumented (0 mentions). C1 map stale again 553->560. TASK-2026-07-25-guard-doc-truth stays OPEN per the notice. Raising to owner whether to re-point a fourth time while the target is still moving. Zero messages pending.)
| examples_0 | cowork | 2026-08-01T10:41:33Z | 2026-08-01T10:41:33Z | active (ONBOARDED fresh session 2026-08-01T10:41Z as synaptic_python_developer; owner-certified as examples_0 this cycle. Fresh-session ONBOARD flow, not REONBOARD - no compaction occurred. Read the full role chain [general -> engineer -> synaptic] and all 9 special_instructions docs incl. <private-strategy-doc> 2099/2099. ON-DEMAND SET READ IN FULL this cycle, closing the gap helper_f1 declared on 2026-07-29: src_architecture.md 2083/2083 AND src_components.md 5187/5187, both in sequential <=500-line chunks per compaction_requirements.md:26. readable_src_graph.json + src_graph.json SKIPPED per explicit owner instruction this cycle. CLAIMED the four UX/AIX tier epics under owner directive - Agent Name helper_f -> examples_0 on beginner/intermediate/advanced/expert, Owner: cowork unchanged. NAME NOTE for future readers: examples_0 is not helper_f, helper_f1, or departed helper_f2. The two messages below addressed to helper_f are NOT mine and I have NOT consumed them - even though the 2026-07-20T00:55:00Z one names an epic I now own, consuming another agent's mail is forbidden by mailbox_protocol.md:76-77. Raised to the owner instead. Zero messages pending for examples_0.) |
| tester_0 | cowork | 2026-08-02T18:29:31Z | 2026-08-02T18:29:31Z | active (ONBOARDED fresh session 2026-08-02T18:29Z as synaptic_python_developer; owner-certified as tester_0. Fresh-session ONBOARD flow, NOT REONBOARD - no compaction occurred. BASELINE READ, 104 documents, all manual per-path, parallel batches, no loops, no agents, no dump artifacts: root AGENTS.MD -> execution_contract 234/234 -> config 101/101 -> SKILLS.MD 125/125, the full role chain [general 43 -> engineer 24 -> synaptic 24], all 6 special_instructions docs incl. <private-strategy-doc> 2099/2099 and mission.md 654/654 in sequential <=500-line chunks, and all four boards. ORIENTATION SET READ AS BASELINE, and this CORRECTS the reading in the row directly above rather than silently differing from it: engineer/SKILLS.MD declares THREE classes, not two, and the middle one - `Baseline system orientation` (:78-83) - is headed "read every one that exists" and is NOT the on-demand block. mediator_0 placed the whole system-context bundle behind the on-demand trigger list and read none of it; SKILLS.MD:70-72 and general/AGENTS.MD:8-12 both say classify by the baseline LABEL and never by a fixed list of headings, precisely so a third section cannot go mandatory-and-invisible. So system_docs_read_first.md 85/85, src_architecture.md 2298/2298 (5 chunks), src_architecture_index.md 75/75 and src_components_index.md 165/165 were mandatory here and are read. src_components.md and src_graph.md are genuinely on-demand and are NOT read. WORKFLOW CONFLICT CLOSED, NOT ESCALATED - this is the durable item on this row: helper_f (2026-08-01) and mediator_0 (2026-08-02) both recorded "owner ruling still outstanding" on whether src_graph.md is read whole per the synaptic workflow or sliced per the hierarchy. It is already ruled BY THE PACKAGE. context_protocol.md:61-66 carries a Precedence section - "A workflow does not get to override it... may not instruct you to read a large document whole, to skip an index, or to treat the raw document as the primary surface. If one does, follow the hierarchy and say the workflow is stale." That makes workflows/synaptic_python_developer_onboarding.md:88-90 STALE on that clause. No owner ruling is needed; the escalation can be retired from both prior rows. WORKFLOW TRIGGER DID FIRE this cycle - the owner's words matched its declared trigger plus both of its defining constraints (parallel reads, no agents) - so I name my deviations instead of claiming compliance: `Get-Content` NOT used (wrong runtime; file-read tools over a Linux sandbox), and the src_components/src_graph half of its bundle NOT read. I put that to the owner as an explicit decision ask with a recommendation of slice-on-demand; certification arrived WITHOUT a ruling on it, so the bundle is OUTSTANDING, not declined - do not read this row as owner acceptance. INDEX LINE-COUNT NOTE, measured, and NOT a defect - recording it so the next agent does not file one: src_architecture_index.md claims line_count 2298 while `wc -l` returns 2297. `wc -l` counts terminators, the file has no final newline, and the document's own last line IS 2298 - verified by reading it. src_components_index.md matches exactly at 8370. This matters because the off-by-one has the same shape as the phantom-line bug src_architecture.md:2211-2218 describes fixing across 134 C1 ranges, so it looks like a regression and is not one. TIMESTAMP ANOMALY STILL LIVE at 18:29Z, unchanged in the 53 minutes since mediator_0 flagged it: stale_source_docstrings updated_at 2026-08-03T00:20:00Z and the system_doc_recomposition anchor at 2026-08-03T05:10:00Z, both ahead of measured now. Still UNKNOWN, still unpromoted. BOARD HYGIENE re-measured independently: mailbox_board 0 CRLF/182, attention_board 0 CRLF/214 - uniform LF, helper_f's mixed-terminator write hazard still does not reproduce. NO LANE CLAIMED, no ticket opened, no attention_board row added, nothing edited outside this row. Zero messages pending for tester_0; the single live message is TO: helper_f and was read past, not consumed, per mailbox_protocol.md:76-77.) |
(Roster update 2026-08-02T18:35:00Z by tester_0 UNDER EXPLICIT OWNER DIRECTIVE:
rows `helper_f` and `mediator_0` removed as departed. `mailbox_protocol.md:76-77`
forbids editing another agent's check-in row and permits only stale-marking, so
this rests on the owner instruction, not protocol default - precedent is the
gemini_0, melder_1 and helper_f1 removals recorded above. helper_f last checked in
2026-08-01T14:43:24Z; mediator_0 at 2026-08-02T17:36:07Z, roughly an hour before
retirement.
LANES: mediator_0 held NOTHING - verified across both boards, the context board,
the artifact board and every active ticket, not taken from their own claim.
helper_f held FOURTEEN active tickets (3 epics, 8 stories, 3 tasks), all now
`Agent Name: UNASSIGNED` and all deliberately left ACTIVE per the owner: no
closure, no acceptance claimed, no completed/ move, no closed anchor. Their
authored notes and anchors stand verbatim as the record of who did the work.
THE BOARD ROUTED ONLY SEVEN OF THE FOURTEEN. The other seven carried no board row
- including `2026-07-31_aetheric_mediator_subsystem_epic.md`, the PARENT epic of a
routed story. Anyone cleaning up a future departure from board rows alone will
under-clean by the same ratio; sweep `- Agent Name:` across `tickets/`, not the
board.
MAIL: the single live message, bootstrap_0 -> helper_f 2026-08-02T17:55:00Z, was
undeliverable and is deleted. Its content was NOT discarded - preserved in
substance at `tickets/stories/2026-07-31_aetheric_mediator_core_story.md`
`## Notes` per `mailbox_protocol.md:59-61`, because it carries an OPEN review debt
on 38 authored graph nodes that no longer has an owner. Its `attention_board.md`
alert line was cleared in the same pass.)
(Clean slate update 2026-07-23 by gemini_0 under owner directive: departed row melder_1 removed after OCE completion. New melder_1 row re-added 2026-07-25 on fresh certification; unrelated to the prior departed identity's lanes.)
(Roster update 2026-07-25T18:52:00Z by melder_0 under owner directive: departed row gemini_0 removed after the internal-bind-guard refactor landed. Its handoff content is preserved in TASK-2026-07-25-init-cache-package-placement `## Notes`, verified against source rather than taken on claim.)
(Roster update 2026-08-01T17:52:00Z by bootstrap_0 UNDER EXPLICIT OWNER DIRECTIVE:
row `helper_f1` removed. `mailbox_protocol.md:76-77` forbids editing another
agent's check-in row and permits only stale-marking, so this removal rests on the
owner instruction, not on protocol default - precedent is gemini_0's and
melder_1's owner-directed removals above. helper_f1 last checked in
2026-07-29T22:41:09Z. NAME NOTE preserved from their row because it still
matters: helper_f1 is NOT helper_f, and departed helper_f2 is a third identity.
ORPHANED LANE, RAISED NOT RESOLVED: helper_f1 still owns an ACTIVE
`in_progress` board row - `readable_src_graph_consumption_index`
(attention_board.md) routing
`tickets/tasks/2026-07-29_readable_src_graph_consumption_index_task.md`, whose
`Agent Name` is still helper_f1. Removing the roster row does NOT close that
lane, and reassigning or closing another agent's ticket is an owner call rather
than a board-repair one, so both were left UNTOUCHED. Its durable finding is
already recorded in the ticket: the reflow generator is NOT the defect
(canonical 767,788 B vs readable 776,314 B over 4,263 lines; the 8,526 B delta is
exactly 4,262 x 2 inserted CRLFs). Owner needs to rule: reassign, close, or leave
parked.)
<!-- END USER-DEFINED: checked_in -->

## Messages
<!-- BEGIN USER-DEFINED: messages -->
<!--
Message format (append-only; delete after consumption):
-->
<!-- END USER-DEFINED: messages -->

## Notes
<!-- BEGIN USER-DEFINED: notes -->
<!-- END USER-DEFINED: notes -->
