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
| `notes` | standing handoff context and per-session custom-instruction setup outcomes |

**Regions ship empty and stay yours.** The package writes nothing into them in any
mode, which also means it can never correct what is written there - so a repeated
policy pasted into a region will not update when the package's own copy does. Put
standing instructions in `notes` once; do not restate MANAGED text.

Purpose
- Shared registration and setup outcomes in every communication mode.
- Mailbox-mode message passing (point-to-point handoffs, notices, questions, acks).
- Companion to `attention_board.md` (which stays routing/broadcast-only).
- Shared state: `agent_onboarding/default/general/skills/agent_session_state.md`.
- Unused in `github_issues` mode: agent issues hold the roster, setup notes and
  messages (`agent_onboarding/default/general/skills/github/issues_backend.md`).
- Message transport: `agent_communication.backend` in the config selects mailbox,
  codex_mcp or claude_internal_communication. Agents on codex_mcp or
  claude_internal_communication read only Checked-In Agents and relevant Notes; they skip
  the messaging rules below and the Messages region. Existing messages remain untouched.

Shared state rules
- Check in at onboarding/re-onboarding: add or update your row below.
- State writes need effective onboarding authorization.
- Keep per-session setup outcomes in Notes and preserve other agents' state.
- Data races on this file are expected: re-read and retry, never overwrite another agent's edit.

Mailbox messaging rules (mailbox mode only; mailbox_protocol.md is authoritative)
- Single-agent sessions: if you are the only checked-in agent, the
  message section needs no monitoring.
- Multiple agents checked in: read your messages at onboarding, at every
  lane switch, and periodically between work units; update `last_checked`.
- Sending: append a structured message below AND add an alert line to
  `attention_board.md` `## Message Alerts` naming the recipient.
- Receiving: copy any actionable content into your active ticket's
  `## Notes` (tickets are the durable truth), DELETE the message here,
  and clear your alert line in `attention_board.md` in the same pass.
- No secrets, ever. Keep messages pointer-heavy (paths/ticket refs),
  not content-heavy.

Message format (mailbox mode only; append-only, delete after consumption)
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
<!-- melder_0 reassigned by the owner 2026-11-07 to session claude@2026-11-07T08:52:02Z; prior: session_01NXa4DfhVXtR5LXnw23inye. -->
| melder_0 | claude | 2026-11-07T08:52:02Z | 2026-11-07T18:37:27Z | departed |
| melder_1 | claude | 2026-09-26T17:46:30Z | 2026-10-25T14:58:20Z | stale |
| melder_2 | claude | 2026-10-18T21:07:02Z | 2026-10-25T15:04:54Z | stale |
<!-- command_5 native session 01a18f23-96ee-7302-936a-5d5135e286d4; initial Melder certificate c5-melder-initial-certification-20261101. -->
| command_5 | codex | 2026-11-01T11:46:57Z | 2026-11-02T12:46:40Z | stale |
<!-- END USER-DEFINED: checked_in -->

## Messages
<!-- BEGIN USER-DEFINED: messages -->
<!-- END USER-DEFINED: messages -->

## Notes
<!-- BEGIN USER-DEFINED: notes -->
- 2026-10-19 melder_1 (session claude@2026-09-26T17:46:30Z): harness custom instructions PRESENT -
  the Claude app's personal preferences carry the Context Compass block; no setup form shown.
- 2026-10-24 melder_2 (session claude@2026-10-18T21:07:02Z): harness custom instructions PRESENT -
  the Claude app's personal preferences carry the Context Compass block; no setup form shown.
- 2026-10-25 melder_0 (session session_01NXa4DfhVXtR5LXnw23inye): harness custom instructions PRESENT -
  the Claude app's personal preferences carry the Context Compass block; no setup form shown.
- DATETIME: 2026-11-01T11:42:38Z
  AUTHOR: gpt_ops_1
  AUTHOR_ROLE: verified transport and parent-delegated captain-record publisher
  TYPE: DECISION
  EVENT_ID: c5-melder-initial-certification-20261101
  CERTIFICATION_AUTHORITY: Parent Sera/Ops under Mark's standing initial-project certification delegation.
  AUTHENTICATED_PARENT: 01a18dd2-18a5-7487-b678-bac7de14802a
  ENACTED_BY: gpt_ops_1; delegated recording only, not an independent captain identity.
  PROJECT: Synaptic724/melder; native melder_private checkout; local tickets and mailbox selected.
  SESSION: 01a18f23-96ee-7302-936a-5d5135e286d4
  AGENT_NAME: command_5
  TITLE: agent: command_5
  ROLE: synaptic_python_developer
  CERTIFY: APPROVED
  BASIS: C5's attributed initial ONBOARD/read-integrity attestation and reported completed required reads/checks.
  VERIFICATION: C5 endpoint/current identity and selected native procedure checked; reported source hashes match.
  READ_ATTESTATION: C5 performed the reads; neither parent Sera/Ops nor gpt_ops_1 claims to have performed them for C5.
  SOURCE:
  - Effective personal AGENTS.md, PROJECT AUTHORITY / CONTEXT COMPASS; initial certification delegated to Sera/Ops.
  - Authenticated parent instruction in existing gpt_ops_1 relay; bounded certification after procedure verification.
  - https://github.com/Synaptic724/priv_melderops/issues/656#issuecomment-6557367033
  - context_compass/agent_onboarding/default/general/skills/self_certification.md
  - context_compass/agent_onboarding/default/general/skills/agent_session_state.md
  - Architecture SHA256 33A833E00A2F7B9C00E47E1E60952F03DE9DD0E8CECF13A480B45C9EC2E1E654.
  - Components SHA256 1F79EAC290555C63B69F685020C0AA90B7ACBFB8BC31ABCBDB292972C7E61370.
  SCOPE: Initial Melder-project role certification for this exact C5 session; retained Ops identity is unchanged.
  NEXT: C5 writes its own first check-in/setup outcome, then its distinct native Task linked to Ops656.
  LIMITS: No source/test/runtime effect, access change, persistent permission or bypass of scoped write approval.
  PRESERVED: Other roster entries and holds; C5 owns its presence/setup row; required reads are not waived.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- 2026-11-01T11:51:57Z command_5 (codex; native session 01a18f23-96ee-7302-936a-5d5135e286d4):
  initial Melder entry/certificate verified; harness custom instructions PRESENT; no setup form or global edit.
  Addressed certification notice captured in TASK-2026-11-01-cleaned-enum-native-persistence Notes, then consumed.
  First check-in2026-11-01T11:46:57Z remains; historical roster/certificate entries are preserved.
- 2026-11-07 melder_0 (session claude@2026-11-07T08:52:02Z; Claude Code in the Claude desktop app): harness custom
  instructions ABSENT - ~/.claude/CLAUDE.md does not exist, CLAUDE_CONFIG_DIR is unset and there is no
  ~/.claude/rules; the setup form was offered once and the owner declined ("use agents.md"). No global edit.
- 2026-11-07T18:22:46Z melder_0 (session claude@2026-11-07T08:52:02Z; re-onboarding after a compaction): harness
  custom instructions now PRESENT - the owner's ~/.claude/CLAUDE.md (written 2026-11-07T15:16:57Z) carries the
  Context Compass block, including retained certification across compaction; the instruction source changed, so the
  outcome above is superseded. No setup form shown, no global edit.
2026-11-07: moved to GitHub Issues (`work_tracking.backend: github_issues`). Nothing reads this board any more; the live records start at the header issue: https://github.com/Synaptic724/melder/issues/263
<!-- END USER-DEFINED: notes -->
