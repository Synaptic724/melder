# memory_management

Purpose
- Define how durable context is stored and maintained in this repo.

Policy
- Use `epics/`, `stories/`, and `tasks/` tickets as the primary durable memory.
- Use `attention_board.md` as routing-only state to select the active ticket.
- Store decisions, assumptions, and handoff context in ticket sections.
- Maintain a `## Notes` section in active tickets for in-flight findings with
  `path:line` evidence pointers.
- Use UNKNOWN as the default claim state and promote to FACT only when evidence is attached.
- `00_overview.md` is optional and should not replace ticket notes or board routing.
- Avoid separate memory stores or ad-hoc JSON logs.

Safety rules
- Never store secrets in tickets or docs.
- Prefer concise, evidence-based notes over speculative memory.

References
- `SKILLS.MD`
- `WORKFLOW.md`
- `agent_onboarding/agent/general/skills/active_documentation.md`
