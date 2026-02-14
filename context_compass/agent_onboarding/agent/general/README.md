# General Career (Shared)

This folder holds onboarding materials shared by all agent careers.

Contents
- behavioral_guidelines/: narrative flow and execution guidance
- policies/: policy router and enforcement references
- skills/: skill docs and certification materials
- SKILLS.md: shared skill index and read order for all careers
- agent_onboarding/agent/general/examples/: canonical JSON and workflow examples
- examples/: ticket and doc examples (within context_compass)

Role-specific overrides should live under their career directory and only include
material that differs from these shared defaults.

DO NOT ASSUME / Unknowns Gate
Rule: No Unverified Claims.
Any statement that is not directly supported by evidence must be treated as UNKNOWN.

Evidence means at least one of:
- A specific source file reference (preferred: file + symbol/method/class name).
- A citation to an explicit, already-verified artifact (e.g., a prior approved doc section).

If not evidenced => UNKNOWN.

UNKNOWN items must be explicitly labeled UNKNOWN (or added to an Unknowns section).
UNKNOWN items must be investigated by reading the relevant source(s).
If investigation cannot be completed (missing source access, ambiguity, or time),
the item must remain UNKNOWN and must not be promoted to fact.

No reasonable assumptions.
Do not infer behavior from naming, patterns, conventions, or typical frameworks.
Only the code/docs count.

When unsure:
- Mark it UNKNOWN.
- Identify the most likely evidence target (file + symbol).
- Investigate, then update the doc (or leave it UNKNOWN).
