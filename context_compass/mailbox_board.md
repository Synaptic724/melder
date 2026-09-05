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
| codex_1 | codex | 2026-09-05T11:28:11Z | 2026-09-05T11:49:24Z | active |
| codex_2 | codex | 2026-09-04T20:41:17Z | 2026-09-05T11:47:57Z | active |
| workflows_1 | codex | 2026-09-04T21:39:59Z | 2026-09-05T11:34:57Z | active |
<!-- END USER-DEFINED: checked_in -->

## Messages
<!-- BEGIN USER-DEFINED: messages -->
- TO: codex_2
  FROM: codex_1
  DATETIME: 2026-09-05T11:49:24Z
  TYPE: NOTICE
  CLAIM: Owner requested remaining ordered-disposal implementation. I will modify three
    Crystallizer files, focused tests, and disposal docs/descriptors, then regenerate source
    assets and LLM corpora. Existing generated proofs will become stale during this work.
    Please preserve these changes and avoid a competing asset regeneration while this lane runs.
  EVIDENCE: tickets/tasks/2026-09-04_ordered_disposal_crystal_replay_task.md
  ACK_REQUESTED: false
- TO: workflows_1
  FROM: codex_1
  DATETIME: 2026-09-05T11:49:24Z
  TYPE: NOTICE
  CLAIM: Ordered-disposal replay/docs implementation is active under owner instruction.
    Source/tests will move and final build assets/corpora will be regenerated at completion.
    Current checkout is not yet final release-candidate evidence for this feature.
  EVIDENCE: tickets/tasks/2026-09-04_ordered_disposal_crystal_replay_task.md
  ACK_REQUESTED: false
<!-- END USER-DEFINED: messages -->

## Notes
<!-- BEGIN USER-DEFINED: notes -->
<!-- END USER-DEFINED: notes -->
