# context_window_budget

Purpose
- Prevent repeated context compaction caused by broad, unfocused repository scans.
- Force incremental discovery with durable notes in active tickets.

Core rule
- Do not attempt to read "the whole repo" during one investigation pass.
- Discovery must happen in bounded slices, with evidence logged before scope expands.
- UNKNOWN is the default claim state until evidence promotes the claim to FACT.
- Strict/relaxed microcycle enforcement is controlled by
  `config/context_compass_config.yaml`.

Scope budgeting protocol (mandatory)
1) Start from `attention_board.md` and the active ticket only.
2) Investigate until one meaningful finding is identified.
3) Immediately append a `## Notes` entry in the active ticket.
4) Do not continue investigation until the note has:
   - evidence (`path:start_line-end_line`),
   - impact,
   - concrete next step.
5) Repeat the loop for each additional meaningful finding.

Expansion gate
- If work requires jumping outside the current subsystem, record why in ticket notes first.
- If planned discovery exceeds 10 files in one pass, ask the user to confirm expansion.

Required note payload per meaningful finding
- `DATE`
- `TYPE` (`FACT` | `UNKNOWN` | `HYPOTHESIS` | `DECISION` | `PLAN` | `MEASURE` | `RISK`)
- `CLAIM`
- `EVIDENCE` (`path:start_line-end_line`; use `start=end` for single-line evidence)
- `IMPACT`
- `NEXT`
- `REREAD` (`REQUIRED` | `HELPFUL`)
- `SCORE_0_TO_10` (compaction usefulness score; improve notes below 8)

Anti-patterns
- Reading architecture + components + large code trees with no ticket notes in between.
- Deferring all findings to an end-of-pass summary.
- Keeping critical findings only in temporary chat context.
- Implementing directly from `UNKNOWN` or `HYPOTHESIS` without evidence-backed promotion.

Success criteria
- Active tickets remain sufficient to resume work after compaction without replaying large context.
- Each meaningful finding leaves explicit evidence and a concrete next action.

References
- `agent_onboarding/agent/general/skills/active_documentation.md`
- `agent_onboarding/agent/general/skills/reactive_documentation.md`
- `agent_onboarding/agent/general/skills/compaction_requirements.md`
- `WORKFLOW.md`
