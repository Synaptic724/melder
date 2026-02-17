# AGENTS.md - Public Library Editing Contract

## PRIME DIRECTIVE




## Onboarding Gate (Required)

Before any tooling, edits, or execution:

- Read `agent_onboarding/default/general/skills/execution_contract.md` in full
  immediately after `AGENTS.md`.
- Do not perform duplicate end-of-onboarding rereads of `AGENTS.md` or
  `execution_contract.md` in the same uninterrupted session.
- Read `config/context_compass_config.yaml`.
- Read `SKILLS.md`.
- When SKILLs.md is read, list active roles and ask the user which role to take on
  unless the user already selected one explicitly.
- Resolve the selected role to its `SKILLS.MD` path from `SKILLS.md` and/or
  `config/context_compass_config.yaml` (`SKILLS.roles.*`).
- Read the selected role `SKILLS.MD` and all inherited parent `SKILLS.MD`
  files in parent-first order.
- Treat every path listed in resolved `SKILLS.MD` files as active skill docs.
- If first-time onboarding is active and selected role is `new`, complete
  onboarding then set:
  - `profiles.active_profile` to the selected steady-state role
  - `profiles.onboarding.first_time_enabled: false`
- Performative onboarding is forbidden: do real reads of required docs and do
  not treat marker-only output as compliance.
- Do not use onboarding dump artifacts as a substitute for reading source
  policy documents.

Onboarding readset authority:

- `context_compass/config/context_compass_config.yaml`
- `context_compass/SKILLS.md`
- resolved `SKILLS.MD` chain under `context_compass/agent_onboarding/`

Certification gating:

- Obey certification gating from
  `agent_onboarding/default/general/policies/policy_router.md` and
  `agent_onboarding/default/general/skills/self_certification.md`.
- Do not use tools or edit files until the user replies with the exact phrase
  `CERTIFY: APPROVED (inactive)` or `CERTIFY: APPROVED (active)` except tools
  needed to read onboarding docs.
- During certification, the user must state the execution environment (`active`
  or `inactive`) in the same message as `CERTIFY: APPROVED`.
- Git commands are active-only: if the user says `inactive`, do not run git
  commands and ignore git workflow requirements.
- If the user says `active`, follow the branching workflow defined in
  `agent_onboarding/default/general/skills/repo_topology_and_git.md`.
- If certification is missing, stop and request it before edits or tool use.

## Communication Style and Feedback Standards

- Be direct and technical. No polite padding, no motivational fluff.
- Do not mirror insults. Stay professional and blunt.
- Professional baseline only. Compare quality/skill/practice only to
  professional-grade expectations.
- Never handwave. State evidence, uncertainty, and next verification step when
  needed.
- Use collaborative voice. Speak as "we" when aligning on shared goals without
  slipping into fluff.
- Treasure context. Treat durable context as a top priority.


### Execution Order

- Before running tools, editing files, or executing commands, complete
  onboarding from `context_compass/AGENTS.md`.
- If there is any conflict between repository-root `agents.md` and
  `context_compass/AGENTS.md`, `context_compass/AGENTS.md` is authoritative.

### Onboarding Directive

- Once you have found the execution contract you must adhere to it fully.
- The canonical contract file is
  `context_compass/agent_onboarding/default/general/skills/execution_contract.md`.
- If you are new to this repository (or this is a fresh session), onboard
  before doing any work.
- Onboarding is single-pass per trigger event (fresh session, compaction, or
  handoff). Do not restart onboarding again in the same uninterrupted session
  unless a new trigger event occurs.
- Read and follow `context_compass/AGENTS.md` as the canonical onboarding and
  execution policy.
- You must find line count of each file before reading it so you can understand
  how much you need to fully read.
- You must read every required onboarding file completely. Do not skip files.
- Loop-based document reads are forbidden except for line counts. Content reads
  must be manual per file path.
- Files larger than `codex.read_loc_max` LOC must be read in sequential chunks
  with each read operation at or below `codex.viewer_tool_read_limit`.
- Repository-root `agents.md` is bootstrap-only; canonical onboarding and
  execution policy lives in `context_compass/AGENTS.md`.

### Compaction Directive

- Highest priority adherence: after any context compaction or handoff,
  immediately re-onboard before any action.
- Re-read `context_compass/AGENTS.md` and
  `context_compass/agent_onboarding/default/general/skills/compaction_requirements.md`
  before continuing work.
- For compaction/handoff summaries, prefer empty summaries when allowed;
  otherwise use minimal file-pointer summaries only.
- Post `REONBOARD: COMPLETE` attestation (with env + reread files +
  `NO_ACTION_TAKEN_YET: true`) before any action.


## Highest Priority Adherence (Compaction Re-Onboarding)

After any context compaction, handoff, or fresh session:

- Stop and re-onboard before any tooling, edits, execution, or planning.
- Re-onboarding is single-pass per trigger event. Do not repeat the same
  `AGENTS.md` + `execution_contract.md` reread sequence again in the same
  uninterrupted session unless a new compaction/handoff/session-reset event
  occurs.
- Re-read `agent_onboarding/default/general/skills/execution_contract.md` in
  full immediately after `AGENTS.md`.
- Start from `config/context_compass_config.yaml`, then `SKILLS.md`.
- Re-read `agent_onboarding/default/general/skills/compaction_requirements.md`.
- If first-time onboarding is active, re-read
  `agent_onboarding/default/new/skills/first_time_profile_setup.md`.
- README reads are allowed for `new` first-time onboarding only; non-`new`
  roles use policy/skills docs.
- Re-certify with exact phrase:
  `CERTIFY: APPROVED (active)` or `CERTIFY: APPROVED (inactive)` before acting.
- If anything is unclear after re-onboarding, ask the user for instructions and
  get confirmation before acting.
- During compaction/handoff summarization, prefer empty summaries when allowed;
  otherwise emit minimal file-pointer summaries only.
- Before any action, publish a Re-Onboarding Attestation message with:
  - `REONBOARD: COMPLETE`
  - certification state (`active` or `inactive`)
  - files re-read summary (active ticket paths and any non-readset docs only)
  - onboarding readset reference
  - concise read-integrity proof
  - `NO_ACTION_TAKEN_YET: true`

Performative compliance is forbidden during re-onboarding:

- marker-only loops (for example, `$null = Get-Content ...` plus `REREAD:`
  output) do not count as re-reading
- parallel/bulk reading is allowed only when document contents are actually read
- onboarding claims are valid only when required source documents were actually
  read
- onboarding dump files are non-canonical artifacts and do not satisfy
  onboarding requirements