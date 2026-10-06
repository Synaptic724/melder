# component_patch_aether_singleton

## Metadata
- Patch ID: root_configuration_guards_2026_09_29
- Status: active
- Owner: user (agent melder_0)
- Created: 2026-09-29T23:43:57Z
- Updated: 2026-09-29T23:43:57Z

<!-- BEGIN ENTRY: "Aether: sealed spell-id regime guard" -->
## Before
- `Aether.configure` installs any AetherConfiguration and `Aether.activate` activates it. The regime
  (`_process_wide_unique_spell_ids`) is sealed when the first frame is born and never re-read, so a configuration
  installed afterwards with a different value is reported by `Aether.configuration` but not in force.
  EVIDENCE: src/melder/aether/aether.py:972-1050, src/melder/aether/aether.py:2474-2533.

## After
- While any frame exists, `configure(configuration)` refuses (RuntimeError, nothing installed) when
  `bool(configuration.process_wide_unique_spell_ids)` differs from the sealed regime; the check and the install run
  under the Aether lock that frame birth holds, so a concurrent first frame either sees the new configuration
  (and seals from it) or the install sees the frame (and is checked).
- `activate()` re-checks the installed configuration the same way before applying it (a still-mutable installed
  configuration can be changed between configure and activate).
- With no frame, behaviour is unchanged: any regime installs and the next first frame seals it.

## Interface Deltas
- New refusal only; signatures unchanged.

## State / Failure Deltas
- RuntimeError message names the sealed value, the requested value and the remedy (install before the first
  Spellbook, or keep the sealed value).

## Dependency / Ordering
- Restore stage 1 must not call `activate(configuration)` with a mismatching regime while frames exist (see the
  crystallizer component patch).

## Validation Expectations
- Unit/component: mismatching configure after a frame raises and leaves the previous configuration installed;
  matching configure after a frame succeeds; mismatching configure before any frame succeeds and is sealed by the
  next frame; activate refuses a configuration mutated to a mismatching regime after install.
<!-- END ENTRY: "Aether: sealed spell-id regime guard" -->
