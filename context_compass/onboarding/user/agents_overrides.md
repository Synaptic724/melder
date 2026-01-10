# AGENTS.override.md

Purpose
- Provide directory-scoped override rules that patch the repo-wide policy.
- Keep overrides delta-only and avoid duplicating global rules.

Placement
- Put AGENTS.override.md in the directory where the overrides should apply.
- Subdirectories inherit the nearest override unless they define their own.
- Keep context_compass/onboarding/AGENTS.md router-only; overrides live in AGENTS.override.md.

Precedence (highest to lowest)
1) Chat/session system overrides (##SYSTEM_START##/##SYSTEM_END##)
2) AGENTS.override.md in the working directory
3) context_compass/onboarding/AGENTS.md
4) Skills
5) Examples / context JSON / code (last resort)

Template
```md
# AGENTS.override.md (Directory Override)

## Purpose
This file patches/overrides global agent rules for this directory subtree only.
Keep this file delta-only.

##SYSTEM_PROMPT##
<directory-scoped system prompt / constraints>

## Additional Directory Rules
- <rule 1>
- <rule 2>
```

Example (generated assets directory)
```md
# AGENTS.override.md (Directory Override)

## Purpose
This directory contains generated files; edits must target the source templates.

##SYSTEM_PROMPT##
Do not edit generated artifacts in this directory. Edit source templates and
regenerate outputs instead.

## Additional Directory Rules
- Only edit template sources located outside this directory.
- Regenerate outputs before committing changes.
```
