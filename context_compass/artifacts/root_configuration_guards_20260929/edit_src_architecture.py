"""Doc pass for the root configuration guards (M1-M4, 0.2.8209-0.2.8212) in src_architecture.md
(melder_0, 2026-09-30). Exact-anchor replacements; the document is LF and stays LF."""
import pathlib
import sys

DOC = pathlib.Path(sys.argv[1])
STAMP = sys.argv[2]

EDITS = [
    # System boundary: Aether root configuration, the value snapshot, Nexus bootstrap.
    ("""- `Aether.create_configuration()`,
  `Aether.create_configuration_builder()`, `Aether.configure(...)`, and
  `Aether.activate(...)` for root logger-policy installation
""", """- `Aether.create_configuration()`,
  `Aether.create_configuration_builder()`, `Aether.configure(...)`, and
  `Aether.activate(...)` for root logger-policy installation; while any frame
  exists both refuse a configuration whose `process_wide_unique_spell_ids`
  differs from the regime the first frame sealed (0.2.8209)
- `get_configuration_dictionary()` on `AetherConfiguration`,
  `CrystallizerConfiguration`, `MutationResearchConfiguration` and
  `NexusConfiguration` (0.2.8212): a snapshot of the property values a root
  configuration holds, so a host can compare policies without private access
"""),
    ("""- `Nexus.configure(...)`, `Nexus.activate(...)`, `Nexus.create_rift(...)`,
  and `Nexus.create_rift_configuration(...)` for AR bootstrap.
""", """- `Nexus.configure(...)`, `Nexus.activate(...)`, `Nexus.create_rift(...)`,
  and `Nexus.create_rift_configuration(...)` for AR bootstrap. While Nexus is
  active, `configure(...)` and `activate(...)` handed another configuration
  refuse (0.2.8210); deactivate first.
"""),
    # Boot sequence, conjure: the refusal before settlement.
    ("""     A missing posture returns the caller's flag unchanged and defers to the
     honest refusal in `SpellbookCreationSystem.check_system_state`. The
     EFFECTIVE mode is then threaded down the whole chain - creation system,
""", """     A missing posture returns the caller's flag unchanged and defers to the
     honest refusal in `SpellbookCreationSystem.check_system_state`. BEFORE
     settling, conjure refuses the active-Crystallizer configuration discipline
     on the mode settlement would produce (`_effective_conjure_mode`,
     0.2.8211), so a refused conjure leaves the frame posture as it was. The
     EFFECTIVE mode is then threaded down the whole chain - creation system,
"""),
    ("""   - `Nexus.configure(...)` installs frozen process-wide AR policy.
""", """   - `Nexus.configure(...)` installs frozen process-wide AR policy. It refuses
     while Nexus is active, as does `activate(...)` handed another
     configuration (0.2.8210).
"""),
    # Operational invariants: the new entry, newest first.
    ("""## Operational Invariants
""", """## Operational Invariants
- Root configuration guards for hosts (2026-09-30, 0.2.8209-0.2.8212): a host that embeds Melder next to another
  Melder user gets root configuration it can trust. While any frame exists, the installed Aether configuration's
  `process_wide_unique_spell_ids` equals the regime sealed at the first frame: `Aether.configure` and
  `Aether.activate` refuse a configuration saying otherwise and install nothing, under the lock frame birth
  holds. An active Nexus keeps its policy object: `configure`, and `activate` handed another object (identity,
  not values), refuse until `deactivate()` - the rule Crystallizer and MutationResearch already had; restore
  stage 4 deactivates an active Nexus before activating the reloaded configuration, as stage 3 does for
  MutationResearch. A dynamic conjure refused by the active-Crystallizer configuration discipline is refused on
  the PREDICTED effective mode before the frame posture is settled, and checked again on the settled mode in the
  transaction window, because another Book can settle the shared frame in between. The four root
  configurations expose `get_configuration_dictionary()`, a lock-guarded snapshot of the properties they hold
  (values by reference; it never freezes or validates). The Aether record carries only the logger half of its
  configuration, so a restore never meets a regime mismatch - and a world recorded under per-frame ids restores
  under process-wide ids (known gap, unchanged).
  EVIDENCE: `src/melder/aether/aether.py:Aether._refuse_regime_change_while_frames_exist`,
  `src/melder/nexus/nexus.py:Nexus.configure`, `Nexus.activate`,
  `src/melder/crystallizer/crystal_loader_system/restore_engine.py:RestoreEngine._replay_nexus`,
  `src/melder/aether/spellbook/spellbook.py:Spellbook._effective_conjure_mode`,
  `Spellbook._refuse_recorded_conjure_after_mutable_binds` and
  `src/melder/aether/aether_configuration.py:AetherConfiguration.get_configuration_dictionary`.
"""),
    # Settle-then-inherit evidence: remeasured after M3 moved the lines.
    ("""  - src/melder/aether/spellbook/spellbook.py:6502-6542
    (`Spellbook._settle_or_inherit_conjure_mode`; in-place settle :6529-6541,
    effective-mode return :6542)
  - src/melder/aether/spellbook/spellbook.py:6637
    (`conjure` resolves the effective mode as it enters the transaction window,
    passing `dynamic=self._settle_or_inherit_conjure_mode(dynamic)`)
""", """  - src/melder/aether/spellbook/spellbook.py:6502-6545
    (`Spellbook._settle_or_inherit_conjure_mode`; in-place settle :6532-6544,
    effective-mode return :6545; remeasured 2026-09-30)
  - src/melder/aether/spellbook/spellbook.py:6758
    (`conjure` resolves the effective mode as it enters the transaction window,
    passing `dynamic=self._settle_or_inherit_conjure_mode(dynamic)`)
"""),
    # Failure modes: the two new refusals and the settled-frame fix.
    ("""## Failure Modes and Error Paths
""", """## Failure Modes and Error Paths
- `Aether.configure(configuration)` and `Aether.activate()` raise RuntimeError while frames exist when the
  configuration's `process_wide_unique_spell_ids` differs from the sealed regime; the message names both values
  and the remedy (install it before the first frame, or keep the sealed value). Before 0.2.8209 the
  configuration was installed and reported while the old regime stayed in force.
  EVIDENCE: `src/melder/aether/aether.py:Aether._refuse_regime_change_while_frames_exist`.
- `Nexus.configure(...)`, and `Nexus.activate(...)` handed a configuration other than the installed one, raise
  RuntimeError "Cannot reconfigure Nexus while it is active. Deactivate it first." (0.2.8210). Before, a live
  Nexus's policy was replaced, unfrozen, under existing Rifts.
  EVIDENCE: `src/melder/nexus/nexus.py:Nexus.configure` and `Nexus.activate`.
- A dynamic conjure refused by the active-Crystallizer configuration discipline no longer settles its frame
  (0.2.8211). Before, the frame was left frozen dynamic, so every later conjure there - automatic ones included -
  inherited dynamic and was refused too.
  EVIDENCE: `src/melder/aether/spellbook/spellbook.py:Spellbook.conjure`.
"""),
    # Code map: remeasured extents of the touched files.
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
    ("""- path: `src/melder/mutation_research/mutation_configuration.py`
  start_line: 1
  end_line: 659
  loc: 659
  verified_at: 2026-08-02T13:00:45Z
""", """- path: `src/melder/mutation_research/mutation_configuration.py`
  start_line: 1
  end_line: 693
  loc: 693
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
    # Information sources: the restore engine and the Nexus configuration now carry cited contracts.
    ("""- `src/melder/aether/aether_configuration.py`
""", """- `src/melder/aether/aether_configuration.py`
- `src/melder/nexus/configuration/nexus_configuration.py`
- `src/melder/crystallizer/crystal_loader_system/restore_engine.py`
"""),
    # Handoff summary: newest first.
    ("""## Context / Handoff Summary

""", """## Context / Handoff Summary

2026-09-30 root configuration guards (0.2.8209-0.2.8212): Aether refuses a spell-id regime other than the one its
first frame sealed while frames exist; an active Nexus refuses another configuration (restore stage 4 deactivates
it first); a dynamic conjure refused by the recorded-world configuration discipline no longer settles its frame;
the four root configurations expose `get_configuration_dictionary()`. The boundary list, the boot sequence, the
operational invariants, the failure modes and the code map carry it; the component map carries the per-root
contracts. Still open: the Aether record does not carry the spell-id regime, so a world recorded under per-frame
ids restores under process-wide ids. The code map's `aether.py` extent also now counts the 0.2.8208 frame lookups.

"""),
]

text = DOC.read_bytes().decode("utf-8")
assert "\r\n" not in text
for old, new in EDITS:
    assert text.count(old) == 1, old[:80]
    text = text.replace(old, new.replace("STAMP", STAMP), 1)
DOC.write_bytes(text.encode("utf-8"))
print("edited", DOC.name, len(text.splitlines()), "lines")
