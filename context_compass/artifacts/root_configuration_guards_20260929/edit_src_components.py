"""Doc pass for the root configuration guards (M1-M4, 0.2.8209-0.2.8212) in src_components.md
(melder_0, 2026-09-30). Exact-anchor replacements; the document is LF and stays LF. Line citations that M1-M3
moved are remeasured by symbol, as are four nexus.py citations in the ACL flow that were already stale."""
import pathlib
import sys

DOC = pathlib.Path(sys.argv[1])
STAMP = sys.argv[2]

EDITS = [
    # Aether singleton: sealed regime.
    ("""  EVIDENCE: `src/melder/aether/aether.py:Aether._resolve_lookup_frame`, `Aether.get_conduit_by_name`,
  `Aether.get_conduit_by_id` and `Aether._find_live_conduit`.

Failure Modes:
- ValueError for missing frames, duplicate registry entries, or not-found lookups. A not-found conduit
  lookup names the searched frame and points at the wider lookup (0.2.79).
""", """  EVIDENCE: `src/melder/aether/aether.py:Aether._resolve_lookup_frame`, `Aether.get_conduit_by_name`,
  `Aether.get_conduit_by_id` and `Aether._find_live_conduit`.
- Sealed spell-id regime (0.2.8209): the first frame born seals `_process_wide_unique_spell_ids` from the
  installed configuration (frozen defaults when none is installed) and it is never re-read while frames exist.
  `configure` and `activate` therefore refuse, under the lock frame birth holds, a configuration whose
  `process_wide_unique_spell_ids` differs, and install nothing - so `configuration` never reports a regime that
  is not in force. With no frame any regime installs and the next first frame seals it.
  EVIDENCE: `src/melder/aether/aether.py:Aether._refuse_regime_change_while_frames_exist`, `Aether.configure`
  and `Aether.activate`.

Failure Modes:
- ValueError for missing frames, duplicate registry entries, or not-found lookups. A not-found conduit
  lookup names the searched frame and points at the wider lookup (0.2.79).
- RuntimeError from `configure(...)` / `activate()` while frames exist when the configuration's spell-id regime
  differs from the sealed one; the message names both values and the remedy (0.2.8209).
"""),
    # Spellbook core: remeasured lock-order citation.
    ("""  - src/melder/aether/spellbook/spellbook.py:7016-7027 (`_run_structural_phases`
    at :7016; the caller-held-lock precondition is stated at :7027)
""", """  - src/melder/aether/spellbook/spellbook.py:7121-7132 (`_run_structural_phases`
    at :7121; the caller-held-lock precondition is stated at :7132; remeasured 2026-09-30)
"""),
    # Spellbook core: the configuration discipline refusal before settlement.
    ("""- `SpellbookConfiguration` must be frozen before Conduit creation.
- Existing-object spells are registered into Creations on conjure/bind.

Failure Modes:
- `SpellbookValidationError` when Phase 1-4 produces broken spells.
""", """- `SpellbookConfiguration` must be frozen before Conduit creation.
- Existing-object spells are registered into Creations on conjure/bind.
- A conjure refused by the recorded-world configuration discipline has no posture side effect (0.2.8211):
  `conjure` starts the CONJURE transaction, predicts the effective mode (`_effective_conjure_mode`, pure, branch
  for branch the same as `_settle_or_inherit_conjure_mode`), refuses on it, and only then settles. The
  transaction window checks again on the SETTLED mode, because Books are separate transaction identities and
  another Book can settle the shared frame between prediction and settlement.
  EVIDENCE: `src/melder/aether/spellbook/spellbook.py:Spellbook.conjure`, `Spellbook._effective_conjure_mode`,
  `Spellbook._refuse_recorded_conjure_after_mutable_binds` and `Spellbook._conjure_within_transaction_window`.

Failure Modes:
- `SpellbookValidationError` when Phase 1-4 produces broken spells.
- RuntimeError "... requires the SpellbookConfiguration to be finalized BEFORE the first bind" when a conjure
  would run dynamic, the Crystallizer is active and binds ran while the configuration was still mutable
  (`_binds_before_configuration_count`). Since 0.2.8211 the refusal leaves the frame posture as it was; before,
  it left an unsettled frame frozen dynamic, so later conjures there - automatic ones included - were refused.
"""),
    # Crystallizer component: discipline timing and restore stage 4.
    ("""- The conjure configuration-discipline guard refuses a dynamic conjure over
  binds that ran while the spellbook configuration was mutable (recorded
  worlds are never born config-incoherent).
""", """- The conjure configuration-discipline guard refuses a dynamic conjure over
  binds that ran while the spellbook configuration was mutable (recorded
  worlds are never born config-incoherent). Since 0.2.8211 it refuses before
  the frame posture is settled, so the refusal changes nothing.
- Restore stage 4 (`RestoreEngine._replay_nexus`) deactivates an ACTIVE live
  Nexus before activating the reloaded configuration, because an active Nexus
  refuses reconfiguration since 0.2.8210 - the same deactivate-first act stage 3
  performs for MutationResearch. A recorded "disabled" still replays
  enable-then-disable.
"""),
    # AR runtime surface: Nexus keeps its policy while active.
    ("""Invariants/Guarantees:
- `Nexus` is the only intended public root for Rift-domain work.
""", """Invariants/Guarantees:
- An active `Nexus` keeps its installed policy object (0.2.8210): `configure(...)`, and `activate(...)` handed
  another object (identity, not values), raise until `deactivate()` - the rule Crystallizer and
  MutationResearch already had. A live Nexus reads its policy at every Rift validation, so a swap would change
  the rules under existing Rifts. `activate()` and `activate(installed)` still re-enable; an inactive Nexus
  accepts any configuration. EVIDENCE: `src/melder/nexus/nexus.py:Nexus.configure` and `Nexus.activate`.
- `Nexus` is the only intended public root for Rift-domain work.
"""),
    ("""Failure Modes:
- Unconfigured or disabled `Nexus` operations fail fast.
""", """Failure Modes:
- Unconfigured or disabled `Nexus` operations fail fast.
- RuntimeError "Cannot reconfigure Nexus while it is active. Deactivate it first." from `configure(...)`, or
  from `activate(...)` handed a configuration other than the installed one, on an active Nexus (0.2.8210).
"""),
    # C2: root configuration assembly and the value snapshot.
    ("""Contract/Interface:
- `create_configuration()`
- `create_configuration_builder()`
- `configure(...)`
- `activate(...)`
Data Structures:
- Installed `AetherConfiguration` plus the one-shot
  `AetherConfigurationBuilder`.
""", """Contract/Interface:
- `create_configuration()`
- `create_configuration_builder()`
- `configure(...)` - refuses a spell-id regime other than the sealed one while frames exist (0.2.8209)
- `activate(...)` - re-checks the sealed regime, so a mutable configuration edited after install is caught
- `AetherConfiguration.get_configuration_dictionary()` (0.2.8212), shared with the Crystallizer,
  MutationResearch and Nexus configurations: a new dict of the properties the configuration holds, read under
  its lock after `check_cleaned()`; values by reference; never freezes or validates; only set properties appear.
  EVIDENCE: `src/melder/aether/aether_configuration.py:AetherConfiguration.get_configuration_dictionary`,
  `src/melder/crystallizer/configuration/crystallizer_configuration.py:CrystallizerConfiguration.get_configuration_dictionary`,
  `src/melder/mutation_research/mutation_configuration.py:MutationResearchConfiguration.get_configuration_dictionary`
  and `src/melder/nexus/configuration/nexus_configuration.py:NexusConfiguration.get_configuration_dictionary`.
Data Structures:
- Installed `AetherConfiguration` plus the one-shot
  `AetherConfigurationBuilder`.
"""),
    ("""Contract/Interface:
- `set_property(...)`, `with_defaults()`, `with_unrestricted_module_mutations(...)`,
- `validate()`, `freeze()`, `finalize()`, `activate()`
""", """Contract/Interface:
- `set_property(...)`, `with_defaults()`, `with_unrestricted_module_mutations(...)`,
- `validate()`, `freeze()`, `finalize()`, `activate()`
- `get_configuration_dictionary()` - value snapshot of the properties held (0.2.8212)
"""),
    ("""Contract/Interface:
- `create_configuration()`, `configure(...)`, `activate(...)`, `deactivate()`
- `create_spell_crystal(...)`
""", """Contract/Interface:
- `create_configuration()`, `configure(...)`, `activate(...)`, `deactivate()`
- `create_spell_crystal(...)`
- `CrystallizerConfiguration.get_configuration_dictionary()` - value snapshot of the properties held (0.2.8212)
"""),
    # Flow: conjure.
    ("""### Flow: Conjure -> Phases -> Conduit
1. `Spellbook.conjure(...)`:
   - Validates and freezes `SpellbookConfiguration`.
""", """### Flow: Conjure -> Phases -> Conduit
1. `Spellbook.conjure(...)`:
   - Starts the CONJURE transaction, refuses the recorded-world configuration discipline on the predicted
     mode (`_effective_conjure_mode`), then settles or inherits the frame mode (0.2.8211); the window re-checks
     the discipline on the settled mode.
   - Validates and freezes `SpellbookConfiguration`.
"""),
    # Mediator plane citations moved by M1 (both occurrences carry the same line).
    ("""  - src/melder/aether/aether.py:762-795
  - src/melder/aether/aether.py:1219-1264
""", """  - src/melder/aether/aether.py:762-795
  - src/melder/aether/aether.py:1288-1333
"""),
    ("""- src/melder/aether/aether.py:209-222
- src/melder/aether/aether.py:1219-1264
""", """- src/melder/aether/aether.py:209-222
- src/melder/aether/aether.py:1288-1333
"""),
    # Frame ACL fan-out flow: nexus.py citations remeasured by symbol (were already stale before 0.2.8210).
    ("`Nexus._on_frame_acl_changed(frame_name)` (`src/melder/nexus/nexus.py:2579`),",
     "`Nexus._on_frame_acl_changed(frame_name)` (`src/melder/nexus/nexus.py:2740`),"),
    ("""     `src/melder/nexus/nexus.py:1375`)""", """     `src/melder/nexus/nexus.py:1536`)"""),
    ("""     (`src/melder/nexus/nexus.py:2491`) - the single-frame path and the batch""",
     """     (`src/melder/nexus/nexus.py:2652`) - the single-frame path and the batch"""),
    ("""     `src/melder/nexus/nexus.py:1343`)""", """     `src/melder/nexus/nexus.py:1504`)"""),
    # Code map extents.
    ("""- path: `src/melder/aether/aether_configuration.py`
  start_line: 1
  end_line: 885
  loc: 885
  verified_at: 2026-09-26T20:10:34Z
""", """- path: `src/melder/aether/aether_configuration.py`
  start_line: 1
  end_line: 920
  loc: 920
  verified_at: STAMP
"""),
    ("""- path: `src/melder/aether/spellbook/spellbook.py`
  start_line: 1
  end_line: 7222
  loc: 7222
  verified_at: 2026-09-26T20:10:34Z
""", """- path: `src/melder/aether/spellbook/spellbook.py`
  start_line: 1
  end_line: 7327
  loc: 7327
  verified_at: STAMP
"""),
    ("""- path: `src/melder/aether/aether.py`
  start_line: 1
  end_line: 2690
  loc: 2690
  verified_at: 2026-09-27T11:46:59Z
""", """- path: `src/melder/aether/aether.py`
  start_line: 1
  end_line: 2911
  loc: 2911
  verified_at: STAMP
"""),
    ("""- path: `src/melder/crystallizer/configuration/crystallizer_configuration.py`
  start_line: 1
  end_line: 1063
  loc: 1063
  verified_at: 2026-08-02T13:00:45Z
""", """- path: `src/melder/crystallizer/configuration/crystallizer_configuration.py`
  start_line: 1
  end_line: 1097
  loc: 1097
  verified_at: STAMP
"""),
    ("""- path: `src/melder/nexus/nexus.py`
  start_line: 1
  end_line: 3565
  loc: 3565
  verified_at: 2026-09-23T11:33:20Z
""", """- path: `src/melder/nexus/nexus.py`
  start_line: 1
  end_line: 3582
  loc: 3582
  verified_at: STAMP
"""),
    ("""- path: `src/melder/crystallizer/crystal_loader_system/restore_engine.py`
  start_line: 1
  end_line: 2768
  loc: 2768
  verified_at: 2026-09-23T11:33:20Z
- path: `src/melder/mutation_research/mutation_configuration.py`
  start_line: 1
  end_line: 659
  loc: 659
  verified_at: 2026-08-02T13:00:45Z
""", """- path: `src/melder/crystallizer/crystal_loader_system/restore_engine.py`
  start_line: 1
  end_line: 2780
  loc: 2780
  verified_at: STAMP
- path: `src/melder/mutation_research/mutation_configuration.py`
  start_line: 1
  end_line: 693
  loc: 693
  verified_at: STAMP
"""),
    # Metadata and handoff.
    ("""- Created: 2026-01-17
- Updated: 2026-09-28
""", """- Created: 2026-01-17
- Updated: 2026-09-30
"""),
    ("""## Context / Handoff Summary

""", """## Context / Handoff Summary

2026-09-30 root configuration guards (0.2.8209-0.2.8212): the Aether Singleton entry and its root configuration
subcomponent carry the sealed spell-id regime and its refusal; the AR Runtime Surface entry carries the active
Nexus refusal and the Crystallizer entry restore stage 4's deactivate-first; the Spellbook Core entry and the
conjure flow carry the refusal before settlement and its re-check in the window; the four root configurations'
`get_configuration_dictionary()` is listed under their subcomponents. Remeasured: the mediator plane's
`_frame_creation_transaction` citation, the `_run_structural_phases` citation, four nexus.py citations in the
frame ACL fan-out flow (already stale before this pass), and the code-map extents of the touched files.

"""),
]

text = DOC.read_bytes().decode("utf-8")
assert "\r\n" not in text
for old, new in EDITS:
    assert text.count(old) == 1, (text.count(old), old[:90])
    text = text.replace(old, new.replace("STAMP", STAMP), 1)
DOC.write_bytes(text.encode("utf-8"))
print("edited", DOC.name, len(text.splitlines()), "lines")
