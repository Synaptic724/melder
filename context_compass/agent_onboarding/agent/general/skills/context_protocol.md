# context_protocol

Purpose
- Make architecture/components docs and tickets the primary source of truth.
- Treat code as a last resort after documented context is consulted.

When to use
- Before any code edits, investigations, or architectural changes.

Required flow
- Read `system_docs/README.md` and `system_docs/README.md` first.
- Review `attention_board.md` first, then open the linked active ticket(s) for current intent.
- Open code only when docs are insufficient or stale.
- If docs are stale, update them before proceeding with feature work.

Rules
- Always prefer documented context over assumptions.
- Treat UNKNOWN as default until evidence is attached.
- Keep architecture/components docs in sync with actual boundaries.
- If a doc is missing, create it before implementing related changes.

Examples
- `agent_onboarding/agent/general/README.md`

