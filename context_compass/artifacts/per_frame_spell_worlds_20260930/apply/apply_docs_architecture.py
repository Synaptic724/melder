"""
Promote the per_frame_spell_worlds patch (A 0.2.8213, B 0.2.8214) into src_architecture.md.

Usage: python apply_docs_architecture.py <repository root>
Every anchor must match exactly once; nothing is written unless all do.
"""
import datetime
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from apply_support import ApplySession

ROOT = sys.argv[1]
DOC = "context_compass/system_docs/src_architecture.md"
NOW = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
s = ApplySession(ROOT)

# Metadata.
s.replace(DOC, "- Created: 2026-01-17\n- Updated: 2026-09-28\n", "- Created: 2026-01-17\n- Updated: 2026-09-30\n")

# Glossary.
s.insert_after(
    DOC,
    "- Key-set plan: the code one override key set compiles to in a `SitePlanOverrideRuntime`; it builds only what\n"
    "  the payload does not supply. The empty key set is the normal plan of the many_only and generalized\n"
    "  families (2026-09-26).\n",
    "- Custody key: the key the Crystallizer's record keeps one spell's crystal under - the spell id under\n"
    "  process-wide spell ids, `\"<spell_id>@<frame>\"` under per-frame ids, where one spell id can be bound in\n"
    "  several frames (0.2.8214).\n",
)

# Boundary list: the regime read, then the frame-aware record verbs.
s.insert_after(
    DOC,
    "  exists both refuse a configuration whose `process_wide_unique_spell_ids`\n"
    "  differs from the regime the first frame sealed (0.2.8209)\n",
    "- `Aether.process_wide_unique_spell_ids` (0.2.8213): a read-only, lock-free answer to which spell-id regime is\n"
    "  in force - the sealed value once a frame exists, before that the installed configuration's value, else True\n",
)
s.replace(
    DOC,
    "  inactive; `create_spell_index_crystal` / `create_contract_crystal` are\n"
    "  the builder companions the seams emit through\n",
    "  inactive; `create_spell_index_crystal` / `create_contract_crystal` are\n"
    "  the builder companions the seams emit through. Since 0.2.8214 `emit_spell_activity`, `emit_spell_removed`\n"
    "  and `get_spell_crystal` take `frame_name`: under per-frame spell ids it names one frame's copy of a spell,\n"
    "  and the two emit verbs refuse without it while recording\n",
)

# Operational invariants: the root-guards gap closes; the new invariant follows it.
s.replace(
    DOC,
    "  (values by reference; it never freezes or validates). The Aether record carries only the logger half of its\n"
    "  configuration, so a restore never meets a regime mismatch - and a world recorded under per-frame ids restores\n"
    "  under process-wide ids (known gap, unchanged).\n",
    "  (values by reference; it never freezes or validates). The Aether record carried only the logger half of its\n"
    "  configuration until 0.2.8213; it now carries the regime too (next invariant).\n",
)
s.insert_before(
    DOC,
    "- Shared document-view initialization (2026-09-28): a non-None section tuple signals a complete index,\n",
    "- Per-frame spell worlds record and restore intact (2026-09-30, 0.2.8213-0.2.8214). Every Aether root twin carries\n"
    "  the spell-id regime in force (`process_wide_unique_spell_ids`, read from `Aether.process_wide_unique_spell_ids`;\n"
    "  the utility system's logger re-emission reads it only from an initialized, uncleaned Aether), and restore stage 1\n"
    "  installs it while the live regime can still change - no configuration installed, no frame born - so the frames\n"
    "  stage 5 births seal it. When the live regime is already fixed (a configured Aether or a live frame) and differs,\n"
    "  stage 1 files a shortfall naming both regimes and rebuilds under the live one, so the sealed-regime guard never\n"
    "  fires from a restore; it refuses before anything is built when the live regime is process-wide and the record\n"
    "  binds one spell id in two frames. Spell custody is keyed by the spell id's uniqueness scope: the bare spell id\n"
    "  under process-wide ids (default worlds keep their record shape) and `\"<spell_id>@<frame>\"` under per-frame ids,\n"
    "  so a class bound in two frames keeps one crystal per frame. Journal entries, checkpoint and formation payload\n"
    "  keys and `describe_spell_crystals()` keys are custody keys; removal and activity address one frame's copy, and a\n"
    "  lookup by a bare spell id without a frame answers its lowest key. Restore replays custody per Book: bind order,\n"
    "  the member-index lookup and recorded-to-live spell translation (selections, staged anchors, contract grants by\n"
    "  the granting conduit's Book) are per Book, and a formation retarget re-keys frame-scoped keys for its target\n"
    "  frame. RecordVersion 4.0.0 fences the new keys from older readers; 3.x records stay readable (their keys are\n"
    "  process-wide keys). Recording still changes no runtime behaviour.\n"
    "  EVIDENCE: `src/melder/aether/aether.py:Aether.process_wide_unique_spell_ids`,\n"
    "  `src/melder/aether/aether_configuration.py:AetherConfiguration.from_recorded_payload`,\n"
    "  `src/melder/crystallizer/crystals/spell_crystal.py:SpellCrystal.custody_key`,\n"
    "  `src/melder/crystallizer/persistence/persistence_profile.py:PersistenceProfile.get_spell_crystal`,\n"
    "  `src/melder/crystallizer/crystal_loader_system/restore_engine.py:RestoreEngine._replay_aether_configuration`,\n"
    "  `RestoreEngine._book_bind_order` and\n"
    "  `src/melder/crystallizer/crystal_loader_system/load_admission.py:LoadAdmission._retarget_payloads`.\n",
)

# Failure modes.
s.insert_before(
    DOC,
    "- `Nexus.configure(...)`, and `Nexus.activate(...)` handed a configuration other than the installed one, raise\n",
    "- A restore raises \"restore failed at stage 'aether_configuration'\" (the all-or-nothing wrapper; nothing was\n"
    "  built) when the record binds one spell id in two frames - possible only under per-frame ids - and the live\n"
    "  regime is already fixed process-wide by a configured Aether or a live frame; the chained RuntimeError names\n"
    "  the remedy (restore into an unconfigured Aether with no frame, or configure per-frame ids before the first\n"
    "  frame; 0.2.8214). A recorded regime the live world cannot take otherwise files a shortfall on\n"
    "  (\"aether\", \"process_wide_unique_spell_ids\"): `recorded_per_frame_ids_restored_under_process_wide_ids` or\n"
    "  its mirror (0.2.8213). Before 0.2.8213 such worlds restored under process-wide ids with no report, and before\n"
    "  0.2.8214 one frame's copy of a class bound in two frames was lost at record time while the restore reported\n"
    "  complete.\n"
    "  EVIDENCE:\n"
    "  `src/melder/crystallizer/crystal_loader_system/restore_engine.py:RestoreEngine._replay_aether_configuration`.\n"
    "- Under per-frame spell ids, `Crystallizer.emit_spell_removed` and `emit_spell_activity` raise ValueError without\n"
    "  `frame_name` while recording (0.2.8214); every Melder call site passes its Book's frame.\n"
    "  EVIDENCE: `src/melder/crystallizer/crystallizer.py:Crystallizer._custody_key_for`.\n",
)

# Record-version lines.
s.replace(
    DOC,
    "to \"2.0.0\" for non-resolvable policy and \"3.0.0\" for named lesser topology. The cache folder remains.\n",
    "to \"2.0.0\" for non-resolvable policy, \"3.0.0\" for named lesser topology and \"4.0.0\" for frame-scoped\n"
    "custody keys (0.2.8214). The cache folder remains.\n",
)
s.replace(
    DOC,
    "- RECORD VERSIONING: RecordVersion \"3.0.0\" stamps every durable\n",
    "- RECORD VERSIONING: RecordVersion \"4.0.0\" stamps every durable\n",
)

# C1 code map: remeasure the touched entries, add the two record/restore owners.
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
        "src/melder/aether/spellbook/spellbook.py",
        "src/melder/aether/aether_configuration.py",
        "src/melder/aether/aether.py",
        "src/melder/aether/aether_utility_system.py",
        "src/melder/crystallizer/crystallizer.py",
        "src/melder/crystallizer/crystals/spell_crystal.py",
):
    remeasure(touched)


def entry(path: str, note: str) -> str:
    """Return one new measured code-map entry."""
    loc = len((pathlib.Path(ROOT) / path).read_bytes().decode("utf-8").splitlines())
    return (
        f"- path: `{path}`\n  start_line: 1\n  end_line: {loc}\n  loc: {loc}\n  verified_at: {NOW}\n"
        f"  note: {note}\n"
    )


s.insert_before(
    DOC,
    "- path: `src/melder/crystallizer/crystal_analysis/conduit_hierarchy.py`\n",
    entry(
        "src/melder/crystallizer/persistence/persistence_profile.py",
        "the record: custody keyed by custody key (per frame under per-frame spell ids,\n"
        "    0.2.8214), journal and checkpoint capture.",
    )
    + entry(
        "src/melder/crystallizer/crystal_loader_system/restore_engine.py",
        "staged restore driver; stage 1 installs or reports the recorded spell-id regime,\n"
        "    stage 6 replays custody per Book (0.2.8213-0.2.8214).",
    ),
)

# Information sources.
s.insert_after(
    DOC,
    "- `src/melder/crystallizer/crystal_loader_system/restore_engine.py`\n",
    "- `src/melder/crystallizer/crystallizer.py`\n"
    "- `src/melder/crystallizer/crystals/spell_crystal.py`\n"
    "- `src/melder/crystallizer/persistence/persistence_profile.py`\n"
    "- `src/melder/crystallizer/persistence/record_version.py`\n"
    "- `src/melder/crystallizer/crystal_loader_system/load_admission.py`\n"
    "- `src/melder/aether/aether_utility_system.py`\n",
)

# Handoff summary.
s.replace(
    DOC,
    "## Context / Handoff Summary\n\n2026-09-30 root configuration guards (0.2.8209-0.2.8212):",
    "## Context / Handoff Summary\n\n"
    "2026-09-30 per-frame spell worlds (0.2.8213-0.2.8214): the Aether record carries the spell-id regime and restore\n"
    "stage 1 installs it, or reports or refuses when the live regime is already fixed; spell custody is keyed\n"
    "\"<spell_id>@<frame>\" under per-frame ids, so a class bound in two frames keeps both copies, and restore replays\n"
    "custody per Book; RecordVersion 4.0.0. The boundary list, the glossary, the operational invariants, the failure\n"
    "modes, the record-version lines and the code map carry it; the component map carries the per-surface contracts.\n"
    "The root-guards entry's \"still open\" item below is closed.\n\n"
    "2026-09-30 root configuration guards (0.2.8209-0.2.8212):",
)

long_lines = s.long_added_lines()
if long_lines:
    raise SystemExit("long added lines:\n" + "\n".join(long_lines))
for written in s.write():
    print("wrote", written)
