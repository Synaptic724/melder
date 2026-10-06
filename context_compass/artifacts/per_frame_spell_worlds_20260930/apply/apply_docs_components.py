"""
Promote the per_frame_spell_worlds patch (A 0.2.8213, B 0.2.8214) into src_components.md.

Usage: python apply_docs_components.py <repository root>
Every anchor must match exactly once; nothing is written unless all do.
"""
import datetime
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from apply_support import ApplySession

ROOT = sys.argv[1]
DOC = "context_compass/system_docs/src_components.md"
NOW = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
s = ApplySession(ROOT)

# Aether Singleton: responsibility and the regime-in-force invariant.
s.insert_after(
    DOC,
    "- Privately host singleton support roots for utility logging, crystallizer\n"
    "  policy/activation, and Nexus AR behavior.\n",
    "- Report the spell-id regime in force through `process_wide_unique_spell_ids` (0.2.8213).\n",
)
s.insert_after(
    DOC,
    "  EVIDENCE: `src/melder/aether/aether.py:Aether._refuse_regime_change_while_frames_exist`, `Aether.configure`\n"
    "  and `Aether.activate`.\n",
    "- Regime in force (0.2.8213): `process_wide_unique_spell_ids` answers without a lock - the sealed value once any\n"
    "  frame exists, before that the installed configuration's value (the one the next first frame seals), else\n"
    "  True. Frame birth writes the seal before it inserts the frame, both under the Aether lock, so a reader that\n"
    "  sees a frame sees the seal. The Crystallizer records it in the Aether twin and keys spell custody by it;\n"
    "  restore stage 1 reads it to tell whether a recorded regime can still be installed.\n"
    "  EVIDENCE: `src/melder/aether/aether.py:Aether.process_wide_unique_spell_ids`.\n",
)

# Crystallizer component: record-version lines, the dated block, owned state, failure modes.
s.replace(
    DOC,
    "- RecordVersion is 3.0.0. Valid older root-only records remain readable; older major-2 readers refuse\n"
    "  new topology. Live loads require caller quiescence of ordinary scope creation/return and lineage.\n",
    "- RecordVersion was 3.0.0 for this change (4.0.0 since 0.2.8214). Valid older root-only records remain\n"
    "  readable; older major-2 readers refuse new topology. Live loads require caller quiescence of ordinary\n"
    "  scope creation/return and lineage.\n",
)
s.replace(
    DOC,
    "- Record major 2 introduced capability protection; current major 3 also protects named lesser topology.\n",
    "- Record major 2 introduced capability protection; major 3 also protects named lesser topology and major 4\n"
    "  frame-scoped custody keys (0.2.8214).\n",
)
s.replace(
    DOC,
    "  id, spell custody split active/inactive by spell SHA), three singleton\n",
    "  id, spell custody split active/inactive by custody key - the spell SHA, or\n"
    "  \"<SHA>@<frame>\" under per-frame spell ids, 0.2.8214), three singleton\n",
)
s.insert_after(
    DOC,
    "  `emit(...)` of an unsupported twin type raises `TypeError`.\n",
    "- Under per-frame spell ids `emit_spell_removed` / `emit_spell_activity` raise ValueError without\n"
    "  `frame_name` while recording; a restore whose record binds one spell id in two frames raises at stage\n"
    "  'aether_configuration' when the live regime is fixed process-wide (0.2.8214).\n",
)
s.insert_before(
    DOC,
    "Responsibilities:\n- Own configured/activated crystallizer policy at the hosted root.\n",
    "Per-frame spell worlds (2026-09-30, 0.2.8213-0.2.8214):\n"
    "- Regime: every AetherCrystal payload carries `process_wide_unique_spell_ids` - the configuration seam its own\n"
    "  value, the utility system's re-emission the Aether's regime in force (omitted when no initialized, uncleaned\n"
    "  Aether can answer). `AetherConfiguration.from_recorded_payload` applies it before its freeze or lists it\n"
    "  under \"missing\" (a 3.x record keeps the default, True).\n"
    "- Custody key: `SpellCrystal` captures `frame_name` from `spell.aetheric_frame` and `custody_key` - the spell\n"
    "  id, or `\"<spell_id>@<frame>\"` when built with `per_frame_custody` (`create_spell_crystal` passes\n"
    "  `not aether.process_wide_unique_spell_ids`); statics `compose_custody_key` / `spell_id_of_custody_key`\n"
    "  (split at the first \"@\"; a SHA256 id holds none). `describe()` carries both.\n"
    "- Record: both custody maps keep their names but are keyed by custody key; replace-on-emit, activity moves and\n"
    "  removal address one key, so under per-frame ids a Book touches only its own frame's copy. Journal entries,\n"
    "  checkpoint and formation payload keys and `describe_spell_crystals()` keys are custody keys; spell_activity\n"
    "  and spell_removed payloads carry \"spell_id\" and \"custody_key\". `get_spell_crystal(spell_id,\n"
    "  frame_name=None)` answers the frame's key first, then the exact key (a bare id or a full custody key), then -\n"
    "  only without a frame - the lowest `\"<spell_id>@\"` key, active before inactive; KeyError otherwise.\n"
    "  `capture_index_graft` takes each member's custody from the index's own Book (members stay keyed by spell id).\n"
    "- Facade: `emit_spell_removed(spell_id, frame_name=None)` and `emit_spell_activity(spell_id, active,\n"
    "  frame_name=None)` are NO-OPs while inactive; while recording they address `_custody_key_for(spell_id,\n"
    "  frame_name)` - the spell id under process-wide ids (frame ignored), the frame's key under per-frame ids, and\n"
    "  ValueError without a frame. Spellbook's removal and park/promote sites pass their frame; crystal creation and\n"
    "  transfer re-emission need none (the crystal reads its spell's frame; transfers stay in one frame).\n"
    "- Restore: stage 1 installs the recorded regime while the live one is unfixed, files\n"
    "  `recorded_per_frame_ids_restored_under_process_wide_ids` (or its mirror) when it is fixed and differs -\n"
    "  rebuilding under the live regime - and refuses before anything is built when the live regime is process-wide\n"
    "  and the folded custody binds one spell id in two frames (an entry's frame: payload \"frame_name\", else its\n"
    "  Book's, else \"default\"). Stage 6 orders each Book's binds by its bind_order mapped to its own custody keys,\n"
    "  binds with the payload's spell id, finds a member's index within its Book, and translates recorded spell ids\n"
    "  per Book (selections, staged anchors, contract details by the granting conduit's Book).\n"
    "- Analysis: a formation retarget rewrites custody `frame_name` and re-keys frame-scoped keys for the target\n"
    "  frame; `ImpactEngine.blast_radius_of_spell` falls back to the lowest key whose payload \"id\" is the spell id.\n"
    "- RecordVersion 4.0.0: an older reader refuses a new record instead of folding two frames' copies into one;\n"
    "  3.x records stay readable. MutationResearch stays keyed by spell id (code identity both copies share).\n"
    "- EVIDENCE: `src/melder/crystallizer/crystals/spell_crystal.py:SpellCrystal.custody_key`,\n"
    "  `src/melder/crystallizer/persistence/persistence_profile.py:PersistenceProfile.get_spell_crystal`,\n"
    "  `src/melder/crystallizer/crystallizer.py:Crystallizer._custody_key_for`,\n"
    "  `src/melder/crystallizer/crystal_loader_system/restore_engine.py:RestoreEngine._replay_aether_configuration`,\n"
    "  `RestoreEngine._book_bind_order`, `RestoreEngine._translate_spell`,\n"
    "  `src/melder/crystallizer/crystal_loader_system/load_admission.py:LoadAdmission._retarget_payloads` and\n"
    "  `src/melder/crystallizer/crystal_analysis/impact_engine.py:ImpactEngine.blast_radius_of_spell`.\n"
    "\n",
)

# Subcomponents.
s.insert_after(
    DOC,
    "- `activate(...)` - re-checks the sealed regime, so a mutable configuration edited after install is caught\n",
    "- `Aether.process_wide_unique_spell_ids` (0.2.8213) - the regime in force, read lock-free (the sealed value once\n"
    "  a frame exists, else the installed configuration's, else True)\n"
    "- `AetherConfiguration.emit_configured_twin_when_recording` records `process_wide_unique_spell_ids`, and\n"
    "  `from_recorded_payload` reloads it before its freeze or lists it under \"missing\" (0.2.8213)\n",
)
s.replace(
    DOC,
    "- `create_configuration()`, `configure(...)`, `activate(...)`, `deactivate()`\n"
    "- `create_spell_crystal(...)`\n",
    "- `create_configuration()`, `configure(...)`, `activate(...)`, `deactivate()`\n"
    "- `create_spell_crystal(...)` - keys the crystal \"<spell_id>@<frame>\" under per-frame spell ids (0.2.8214)\n"
    "- `get_spell_crystal(spell_id, frame_name=None)`, `emit_spell_removed(spell_id, frame_name=None)` and\n"
    "  `emit_spell_activity(spell_id, active, frame_name=None)` - address one custody key (0.2.8214)\n",
)
s.insert_after(
    DOC,
    "  surfaces, and topological module load order via delegating properties.\n",
    "- Keys its record entry (0.2.8214): `frame_name` (from `spell.aetheric_frame`) and `custody_key` - the spell\n"
    "  id, or \"<spell_id>@<frame>\" when built with `per_frame_custody`; statics `compose_custody_key` and\n"
    "  `spell_id_of_custody_key` (split at the first \"@\").\n",
)
s.insert_after(
    DOC,
    "- `_analysis` (one carried `CrystalAnalysisResult`; the pre-decomposition\n"
    "  per-map slots were absorbed into it).\n",
    "- `_frame_name`, `_custody_key` (0.2.8214).\n",
)
s.insert_after(
    DOC,
    "  `resolve_safe_logger`, `resolve_channel_logger`.\n",
    "- `emit_root_twin_when_recording` - re-emits the Aether twin from live logger truth plus the Aether's regime in\n"
    "  force, read only from an initialized, uncleaned Aether (else omitted and a restore reports it missing;\n"
    "  0.2.8213).\n",
)

# Promoted restore detail: correct the stale translation claim.
s.insert_after(
    DOC,
    "  RuntimeError. Shortfall ledger reports everything unreplayable (hooks,\n"
    "  non-hydratable targets, cluster leadership, index subscriptions, MR).\n",
    "- Corrected 2026-09-30: a spell SHA changes when the receiving policy changes its bind signature, and the\n"
    "  report then maps it (2026-09-05); since 0.2.8214 that translation is per Book, and stage 1 installs,\n"
    "  reports or refuses the recorded spell-id regime (see the Crystallizer component's per-frame block).\n",
)
s.replace(
    DOC,
    "  CURRENT \"2.0.0\", key \"record_version\"): stamps to_cached_item,\n",
    "  CURRENT \"4.0.0\" since 0.2.8214 (\"2.0.0\" when promoted), key \"record_version\"): stamps to_cached_item,\n",
)


def remeasure(path: str) -> None:
    """Rewrite one code-map entry's end_line, loc and verified_at from the file on disk."""
    text = s._load(DOC)
    pattern = re.compile(
        r"- path: `" + re.escape(path) + r"`\n  start_line: 1\n  end_line: \d+\n  loc: \d+\n  verified_at: \S+\n"
    )
    matches = pattern.findall(text)
    if len(matches) != 1:
        raise AssertionError(f"code map entry for {path}: {len(matches)} matches")
    loc = len((pathlib.Path(ROOT) / path).read_bytes().decode("utf-8").splitlines())
    s.replace(
        DOC,
        matches[0],
        f"- path: `{path}`\n  start_line: 1\n  end_line: {loc}\n  loc: {loc}\n  verified_at: {NOW}\n",
    )


for touched in (
        "src/melder/aether/aether.py",
        "src/melder/aether/aether_configuration.py",
        "src/melder/aether/aether_utility_system.py",
        "src/melder/crystallizer/crystallizer.py",
        "src/melder/crystallizer/crystals/spell_crystal.py",
        "src/melder/aether/spellbook/spellbook.py",
        "src/melder/crystallizer/persistence/persistence_profile.py",
        "src/melder/crystallizer/persistence/persistence_system.py",
        "src/melder/crystallizer/crystal_loader_system/restore_engine.py",
        "src/melder/crystallizer/crystal_loader_system/load_admission.py",
        "src/melder/crystallizer/crystal_analysis/impact_engine.py",
):
    remeasure(touched)

# Handoff summary.
s.replace(
    DOC,
    "## Context / Handoff Summary\n\n2026-09-30 root configuration guards (0.2.8209-0.2.8212):",
    "## Context / Handoff Summary\n\n"
    "2026-09-30 per-frame spell worlds (0.2.8213-0.2.8214): the Aether Singleton entry carries the regime-in-force\n"
    "read; its root configuration and utility-host subcomponents carry the regime in the Aether twin and its reload;\n"
    "the Crystallizer entry carries a dated block (custody keys, frame-aware verbs, stage 1 install / shortfall /\n"
    "refusal, per-Book replay, retarget, impact read, RecordVersion 4.0.0) and its record-version lines; the\n"
    "Crystallizer Root and SpellCrystal Manifest subcomponents list the new surface. Corrected: the promoted restore\n"
    "detail's \"spell SHAs never translate\" (they translate when a receiving policy changes them, per Book since\n"
    "0.2.8214) and the promoted RecordVersion \"2.0.0\". Remeasured: the code-map extents of the eleven touched files.\n"
    "\n"
    "2026-09-30 root configuration guards (0.2.8209-0.2.8212):",
)

long_lines = s.long_added_lines()
if long_lines:
    raise SystemExit("long added lines:\n" + "\n".join(long_lines))
for written in s.write():
    print("wrote", written)
