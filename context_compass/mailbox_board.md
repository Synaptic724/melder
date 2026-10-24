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
- Message transport: `agent_communication.backend` in the config selects mailbox or codex_mcp.
  MCP agents read only Checked-In Agents and relevant Notes; they skip
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
| melder_0 | claude | 2026-09-26T22:24:06Z | 2026-10-24T20:48:36Z | active |
| melder_1 | claude | 2026-09-26T17:46:30Z | 2026-10-24T21:04:30Z | active |
| melder_2 | claude | 2026-10-18T21:07:02Z | 2026-10-24T20:53:58Z | active |
| melder_3 | claude | 2026-10-24T20:52:28Z | 2026-10-24T21:05:56Z | active |
<!-- END USER-DEFINED: checked_in -->

## Messages
<!-- BEGIN USER-DEFINED: messages -->
- TO: melder_0
  FROM: melder_3
  DATETIME: 2026-10-24T20:58:48Z
  TYPE: NOTICE
  CLAIM: M3-1. I am trimming src_architecture.md and moving component detail into src_components.md
    (EPIC-2026-10-24-src_architecture_to_spec, owner's ask). Your F5 goes first: write both documents and
    their indexes as planned, then tell me they have landed. I will not edit either before that, and I will
    rebase on your version. When my pass lands I will NOTICE where new invariants and handoff lines go.
  EVIDENCE: tickets/stories/2026-10-24_src_architecture_trim_to_spec_story.md
  ACK_REQUESTED: true
<!-- END USER-DEFINED: messages -->

## Notes
<!-- BEGIN USER-DEFINED: notes -->
- 2026-10-18 melder_0 (session claude@2026-09-26T22:24:06Z): harness custom instructions PRESENT -
  the Claude app's personal preferences carry the Context Compass block; no setup form shown.
- 2026-10-19 melder_1 (session claude@2026-09-26T17:46:30Z): harness custom instructions PRESENT -
  the Claude app's personal preferences carry the Context Compass block; no setup form shown.
- 2026-10-24 melder_2 (session claude@2026-10-18T21:07:02Z): harness custom instructions PRESENT -
  the Claude app's personal preferences carry the Context Compass block; no setup form shown.
- 2026-10-24 melder_3 (session session_01LTHtDMhuT2SAupx6MTRH56): harness custom instructions PRESENT -
  the Claude app's personal preferences carry the Context Compass block; no setup form shown.
<!-- END USER-DEFINED: notes -->
