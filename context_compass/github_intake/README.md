# github_intake

Purpose
- Store raw GitHub tickets copied in by automation (e.g., Copilot).
- Keep intake separate from active work management.

Workflow
- New tickets go into context_compass/github_intake/tickets/ as .md files.
- Agents triage and move tickets into the active branch backlog.
- Use context_compass/tools/work_item_add.py to create linked work items from a ticket.
- Use context_compass/tools/ticket_promote.py to create a root work item directly from a ticket.

Notes
- Do not edit context_compass state or ctx files here.
