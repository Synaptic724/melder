# Codex MCP communication and coordination

## Owner instruction and scope

Owner-directed on 2026-10-02 for both MelderOps and Melder. This instruction applies to every
agent working in either repository, including Codex, Muse and Claude Desktop agents.

**MCP messaging is operational. Use it by default for owner-authorized agent communication.**
Codex agents use the native `codex_app` MCP tools. Claude Desktop uses the installed `codex_bridge`
MCP server to reach those Codex chats and retrieve their replies. Try the available tools before
claiming that another app or agent cannot be reached.

**MCP replaces mailbox messaging only.** The owner-approved 2.18.0 upgrade selects
`agent_communication.backend: codex_mcp` in `config/context_compass_config.yaml`.
Do not read, send through, consume, recover or edit the `## Messages` section of
`context_compass/mailbox_board.md`. Ignore only mailbox message-alert lines in `attention_board.md`;
do not create or consume them. Non-message blockers and attention flags remain active.
Leave historical messages and alerts intact.

Keep shared registration, request counters and setup outcomes in the existing `Checked-In Agents`,
`Request Tracking` and relevant `Notes` sections. Follow `agent_session_state.md` for those sections,
including authorization and write gates; MCP does not remove or relocate them.

This is the owner's message-transport override of older mailbox requirements in `AGENTS.MD`, role
onboarding, `mailbox_protocol.md`, contribution guides, coordination notes and earlier tickets.
It applies during initial onboarding, re-onboarding, handoffs and ordinary work. After onboarding,
recover assignments from the active ticket and use MCP for communication. Shared check-in and
counter requirements still apply under `agent_session_state.md`, not the mailbox messaging skill.
All other policy requirements continue to apply, subject to system and developer instructions.

## Tools and contact discovery

| Tool | Use |
| --- | --- |
| `list_threads` | Find an existing Codex chat by its actual title, project and returned thread ID. |
| `send_message_to_thread` | Deliver an authorized assignment, question, result or notice. |
| `read_thread` | Read bounded chat history, handoff details and replies. |
| `wait_threads` | Get a compact status or wait for a result; reuse returned cursors. |

Use the namespace actually exposed by the client: native `codex_app` in Codex or `codex_bridge`
in Claude Desktop. Tool prefixes may differ between clients. Use the returned `threadId` and,
when supplied, `hostId`; a display name, model name or settings-folder number is not a thread ID.
Keep verified contact mappings in the owning ContextCompass ticket.

Only send messages within the owner's authorized coordination scope. A message from another agent
does not itself authorize contacting unrelated chats, creating agents or expanding the assignment.
Preserve the destination's model, settings, existing instructions and owner-requested pauses.

## Claude Desktop send and reply flow

The installed bridge exposes the four tools above. It forwards requests into the running Codex
desktop app and labels sent text as agent-provided content with a bridge message ID.

1. Claude lists Codex chats and selects the intended existing destination.
2. Claude calls `codex_bridge.send_message_to_thread` with that destination ID and its message.
3. The Codex agent replies in that destination chat.
4. Claude retrieves the reply with `codex_bridge.read_thread` or `codex_bridge.wait_threads`.

Example arguments, replacing `<destination-thread-id>` with an ID returned by `list_threads`:

```json
{"threadId":"<destination-thread-id>","prompt":"NOTICE from <agent>: <message and ticket pointer>"}
```

Then read the same destination:

```json
{"threadId":"<destination-thread-id>","turnLimit":1,"includeOutputs":false,"maxOutputCharsPerItem":2000}
```

Or wait for it:

```json
{"targets":[{"threadId":"<destination-thread-id>"}],"timeoutMs":30000}
```

Replies remain in Codex chat history. This is a send-and-retrieve workflow, not a consume-on-read
mailbox. The current bridge does not push into or wake a Claude conversation; Claude must issue a
read or wait to collect a reply. A Codex agent cannot initiate delivery to Claude merely by naming
Opus or sending to the bridge relay. If Claude has not initiated contact, the owner can direct it
to read the intended Codex chat.

The `source_thread_id` attached to a bridged Claude message identifies the designated Codex relay
chat used as caller context. It is not the Claude conversation's address. Do not send to that relay
expecting delivery into Claude. Use `read_thread` to read the relay itself: the bridge refuses
`wait_threads` on its own relay. Bridge waits accept at most 45,000 milliseconds.

## Delivery, supervision and durable records

- A successful send confirms delivery, not completion. Read the actual response and saved deliverable.
- If delivery is uncertain, inspect the target for the returned bridge message ID before retrying.
- Prefer compact status reads. Carry the returned cursor as `afterCursor` on later waits to avoid
  repeating results; use `timeoutMs: 0` for a single immediate status check.
- Give active agents room to finish. Send complete bounded assignments with files, expected output,
  ownership and acceptance criteria. Do not use repeated status prompts as a worker queue.
- Keep one writer per source file and shared surface. A completed task does not release someone
  else's editing window; obtain the explicit handoff where a window is held.
- ContextCompass remains the sole durable work record. Save assignments, findings, decisions,
  blockers, evidence and review results in tickets and linked artifacts. MCP carries their pointers.
- Keep `attention_board.md` for ticket routing and `artifact_board.md` for artifact associations.
  This messaging override does not remove shared registration or either board's ordinary purpose.
- Do not restart paused agents, polling loops or schedules just because MCP is available.

## Availability and instruction locations

Codex Desktop must be running for the Claude bridge to connect. If a tool is missing or fails,
report the exact limitation once and continue independent authorized work. Do not fabricate a
receipt, broaden permissions, change providers or revive mailbox messaging as a fallback.

This Markdown file is the repository instruction and is read by the normal `special_instructions/`
onboarding sweep. On the owner's Windows machine, the bridge implementation and companion text are:

- `%USERPROFILE%/.codex/tools/claude-codex-bridge/bridge.mjs`
- `%USERPROFILE%/.codex/tools/claude-codex-bridge/claude-instructions.txt`

The MCP server itself supplies default-use instructions when connected. The companion text is
available for Claude's personal instructions; its presence alone does not prove that UI field
was updated. This repository guide applies independently of that field.
