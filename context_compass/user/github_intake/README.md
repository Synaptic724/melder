# github_intake

Purpose
- Store raw GitHub tickets copied in by automation (e.g., Copilot).
- Keep intake separate from active work management.

Workflow
- New tickets go into context_compass/user/github_intake/tickets/ as .md files.
- Agents triage and move tickets into the active branch backlog.
- Use context_compass/system/ai_restricted/work_management/work_item_add.py to create linked work items from a ticket.
- Use context_compass/system/ai_restricted/work_management/ticket_promote.py to create a root work item directly from a ticket.

Example
```bash
python context_compass/system/ai_restricted/work_management/ticket_promote.py \
  --repo-root . \
  --agent-id <agent_id> \
  --ticket-path context_compass/user/github_intake/tickets/epic.md \
  --bucket backlog \
  --kind epic \
  --child-items-json '[{"kind":"task","target_path":"src/pkg/foo.py","ctx_path":"src/pkg/foo.py"}]'
```

Notes
- Do not edit context_compass state or ctx files here.
