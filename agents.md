## Onboarding Directive

- Once you have found the social contract you must adhere to it fully.
- If you are new to this repository (or this is a fresh session), onboard as an agent developer before doing any work.
- Read and follow `context_compass/AGENTS.MD` as the canonical onboarding and execution policy.
- You must find line count of each file before reading it so you can understand how much you need to fully read.
- YOU MUST READ EVERYTHING TRUNCATION RISK IS HIGH USE 500 LOC iterations over each file so you do not miss any data.
- You must raw read everything no cheating no bullshit. Do not skip any files at all.
- After reading agents.md in context_compass dir you will receive a list of documents around 80+ get the line count for all of them and user parallel read specifically on documents that are not more than 500 LOC, for documents that are more than 500 LOC you must sequentially read them.
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
