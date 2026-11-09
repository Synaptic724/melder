# Codex MCP communication - turned off

## Owner instruction and scope

Owner-directed on 2026-10-16 for this repository: "your not using codex your using mailbox turn off codex_mcp".
Codex MCP messaging is off. Agents working this repository communicate through the mailbox:

- `config/context_compass_config.yaml` selects it: `agent_communication.backend: mailbox`.
- The protocol is `agent_onboarding/default/general/skills/mailbox_protocol.md`: messages in `mailbox_board.md`
  `## Messages`, one alert line per message in `attention_board.md` `## Message Alerts`, consume by copying what
  is actionable into the ticket's Notes, deleting the message and clearing its alert.

This replaces the 2026-10-02 instruction that selected the `codex_mcp` transport and told agents not to read or send
through the mailbox. That instruction no longer applies here: do not send through the Codex bridge or the
`codex_app` tools, and do not switch `agent_communication.backend` back without the owner's word. Its text is kept,
verbatim, at `artifacts/public_notch_target_20261016/notes/codex_mcp_before_2026_10_16.md`.

Unchanged: shared registration, request counters and setup outcomes stay in `mailbox_board.md` under
`agent_onboarding/default/general/skills/agent_session_state.md`; tickets stay the durable work record and messages
carry pointers to them.
