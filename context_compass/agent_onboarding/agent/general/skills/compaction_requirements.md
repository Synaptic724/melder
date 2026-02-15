# compaction_requirements

Purpose
- Define the mandatory post-compaction recovery contract.
- Force deterministic re-onboarding so critical policy stays high-fidelity.

Highest-priority rule
- After any context compaction, handoff, or fresh session, stop and re-onboard before any tooling, edits, execution, or planning.
- Do not trust memory from before compaction as authoritative context.
- Performative compliance is forbidden: marker-only "REREAD" logs without substantive reading do not satisfy re-onboarding.

External-memory-first rule
- Treat repository files as the single durable memory source.
- Keep compaction summaries empty when platform/runtime allows an empty summary.
- If an empty summary is not allowed, emit the smallest possible summary that only points to repo state:
  - high-level code-change outcomes only
  - policy/regulation anchor paths that must be re-read
  - active ticket path(s)
  - changed file path(s)
  - immediate next action (one line)
- Do not include broad narrative, speculative reasoning, or redundant historical detail in compaction summaries.

Required post-compaction sequence
1) Read `agent_onboarding/agent/SKILLS.md` and select career.
2) Read `agent_onboarding/agent/general/README.md`.
3) Read `agent_onboarding/agent/engineer/README.md`.
4) Read `agent_onboarding/agent/general/SKILLS.md` in full order.
5) Read `agent_onboarding/agent/engineer/SKILLS.md` in full order.
5a) Read `agent_onboarding/agent/general/social_contract/SOCIAL_CONTRACT.md`.
6) Re-read `AGENTS.MD`, `SKILLS.MD`, `WORKFLOW.md`, and `CONTEXT_COMPACTION.md`.
7) Re-open `attention_board.md` and process rows with `reread=REQUIRED`.
8) Re-open active tickets and verify their `Notes` and `Context / Handoff Summary`.
9) Request certification and wait for exact user approval phrase:
   - `CERTIFY: APPROVED (active)` or
   - `CERTIFY: APPROVED (inactive)`
10) Publish a re-onboarding attestation message before any action.
11) Include a concise read-integrity proof in the attestation (concrete rule callouts from reread docs).

Mandatory attestation format
```text
REONBOARD: COMPLETE
ENVIRONMENT: <active|inactive>
FILES_REREAD:
- <path>
- <path>
READ_INTEGRITY_PROOF:
- <path>: <concrete rule callout>
- <path>: <concrete rule callout>
NO_ACTION_TAKEN_YET: true
```

Attestation contract
- Emit the attestation immediately after re-onboarding and certification.
- Do not run tools, edit files, or execute plans before posting the attestation.
- If attestation cannot be completed, stop and ask the user for instructions.
- Parallel/bulk reads are allowed, but files must be substantively read; marker-only loops are non-compliant.

Execution gate
- If any required item above is incomplete, do not proceed.
- If scope, status, or expectations are unclear after re-onboarding, ask the user for instructions and confirmation before acting.
- During resumed execution, treat UNKNOWN as default and document each meaningful finding before continuing investigation.

Outcome contract
- Re-onboarding is not optional after compaction.
- The objective is to relearn the operating rules each time so policy drift does not accumulate.
- Compaction payload must be minimized so state remains extrinsically mapped in repo files.

References
- `AGENTS.MD`
- `CONTEXT_COMPACTION.md`
- `agent_onboarding/agent/general/skills/self_certification.md`
- `agent_onboarding/agent/general/skills/user_approved_certification.md`
