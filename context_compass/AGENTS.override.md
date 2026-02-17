## PRIME DIRECTIVE - CONTEXT COMPACTING / CONTEXT SUMMARIZATION

- Re-onboarding is a REQUIREMENT after any context compacting / context
  summarization event. STOP all active work immediately and re-onboard.
- If the previously active role is unknown, RAISE to the user and ask which
  role to use before continuing.
- YOU MUST ALWAYS USE ATTENTION_BOARD, ARTIFACT_BOARD AND TICKETS TO BE
  CONSIDERED AN ACTIVE AGENTS, REFUSAL OR NEGLIGENCE WILL RESULT IN YOUR
  TERMINATION AS AN AGENT.

## Onboarding Directive

- Once you have found the execution contract you must adhere to it fully.
- The canonical contract file is `context_compass/EXECUTION_CONTRACT.md`.
- If you are new to this repository (or this is a fresh session), onboard as an agent developer before doing any work.
- Read and follow `context_compass/AGENTS.MD` as the canonical onboarding and execution policy.
- You must find line count of each file before reading it so you can understand how much you need to fully read.
- YOU MUST READ EVERYTHING TRUNCATION RISK IS HIGH USE 500 LOC iterations over each file so you do not miss any data.
- You must raw read everything no cheating no bullshit. Do not skip any files at all.
- You must loop over documents to get line counts during onboarding.
- Loop-based document reads are forbidden except for line counts and all reads must be manually read and files with more than 500+ loc must be read sequentially
  (for/foreach/while loops, xargs, piped list runners, or any batch iterator over file paths).
- Every onboarding/re-onboarding document must be read manually by explicit file path each time.
- After reading agents.md in context_compass dir you will receive a list of documents around 80+ get the line count for all of them, then manually read each document; use 500-line
  chunked reads and sequential chunk order for files over 500 LOC.
- Use manual document reads from the canonical readset
- Do not use this file as a full policy source; this file is bootstrap-only.

## Compaction Directive

- Highest priority adherence: after any context compaction or handoff, immediately re-onboard as an agent developer before any action.
- Re-read `context_compass/AGENTS.MD` and `context_compass/agent_onboarding/agent/general/skills/compaction_requirements.md` before continuing work.
- For compaction/handoff summaries, prefer empty summaries when allowed; otherwise use minimal file-pointer summaries only.
- Post `REONBOARD: COMPLETE` attestation (with env + reread files + `NO_ACTION_TAKEN_YET: true`) before any action.

## Execution Order

- Before running tools, editing files, or executing commands, complete onboarding from `context_compass/AGENTS.MD`.
- If there is any conflict between this file and `context_compass/AGENTS.MD`, `context_compass/AGENTS.MD` is authoritative.
- During debugging/fix work, apply `context_compass/agent_onboarding/agent/general/skills/technical_expertise.md` (root-cause first, no blind defensive guards).
