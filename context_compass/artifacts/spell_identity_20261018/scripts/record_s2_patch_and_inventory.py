"""Record S1's patch updates and S2's inventory, patch and mapping in the tickets and boards.

After update_patches_b_strict.py and align_patches_after_b.py: S2 gets its inventory FACT note (the spell_id-keyed
caches and stores, re-read on 0.2.8255 after the compaction), a DECISION note (the record field moves to S5; the
four managed settings are in the binding hash) and its PLAN mapping; S1 a FACT note on its updated patches; the
epic a FACT note, Milestone 1 and its handoff; the board rows and the artifact rows follow. Source ranges are
computed from the files, never typed. All-or-nothing: nothing is written unless every anchor matches once.
"""
import datetime
import pathlib
import re
import shutil
import sys


class Record:
    """One read-modify-write pass, staged and then flushed."""

    REPO = pathlib.Path.home() / "mnt/melder_private"
    ROOT = REPO / "context_compass"
    BACKUP = pathlib.Path("/tmp/m0_mq/bak_t5")
    EPIC = "tickets/epics/2026-10-18_spell_identity_is_the_code_epic.md"
    S1 = "tickets/stories/2026-10-18_spell_id_hashes_the_object_code_story.md"
    S2 = "tickets/stories/2026-10-18_binding_manifest_hash_story.md"
    BOARD = "attention_board.md"
    ARTIFACTS = "artifact_board.md"
    PATCHES = "system_docs/patches/active/spell_identity_is_the_code_2026_10_18"
    SNAP = "src/melder/aether/spellbook/spell_compiler/structural_snapshot/structural_snapshot.py"
    SCS = "src/melder/aether/spellbook/spellbook_creation_system.py"
    BOOK = "src/melder/aether/spellbook/spellbook.py"
    CACHE = "src/melder/utilities/caching_system/caching_system.py"
    DOOR = "src/melder/aether/conduit/meld/conduit_meld.py"
    STATES = "src/melder/aether/aetheric_frame/dev_ops/spell_system_states/spell_system_states.py"
    CRYSTAL = "src/melder/crystallizer/crystals/spell_crystal.py"
    GEN = "src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized"

    def __init__(self) -> None:
        self.now = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        self.staged: dict = {}

    def read(self, rel: str) -> str:
        if rel in self.staged:
            return self.staged[rel]
        return (self.ROOT / rel).read_text(encoding="utf-8")

    def stage(self, rel: str, text: str) -> None:
        self.staged[rel] = text

    @staticmethod
    def once(text: str, old: str, new: str, label: str) -> str:
        if text.count(old) != 1:
            sys.exit(f"ANCHOR {label}: found {text.count(old)}")
        for line in new.split("\n"):
            if len(line) > 120 and not line.startswith("|") and not line.endswith("|") \
                    and "context_compass/" not in line and "src/" not in line:
                sys.exit(f"WIDTH {label}: {len(line)}: {line}")
        return text.replace(old, new)

    def src_lines(self, rel: str) -> list:
        return (self.REPO / rel).read_text(encoding="utf-8").split("\n")

    def method(self, rel: str, name: str) -> str:
        """`rel:start-end` of a method: its `def` line to the line before the next member at its indentation."""
        lines = self.src_lines(rel)
        starts = [i for i, line in enumerate(lines) if re.match(rf"^    def {re.escape(name)}\(", line)]
        if len(starts) != 1:
            sys.exit(f"METHOD {name}: {len(starts)}")
        start = starts[0]
        while start > 0 and lines[start - 1].startswith("    @"):
            start -= 1
        end = starts[0] + 1
        while end < len(lines) and not re.match(r"^    (def |@|[A-Za-z_][A-Za-z_0-9]*: )", lines[end]) \
                and not re.match(r"^class ", lines[end]):
            end += 1
        while lines[end - 1].strip() == "":
            end -= 1
        return f"{rel}:{start + 1}-{end}"

    def span(self, rel: str, first: str, last: str) -> str:
        """`rel:start-end` from the first line containing `first` to the next line containing `last`."""
        lines = self.src_lines(rel)
        starts = [i for i, line in enumerate(lines) if first in line]
        if len(starts) < 1:
            sys.exit(f"SPAN {first}")
        start = starts[0]
        end = next((i for i in range(start, len(lines)) if last in lines[i]), None)
        if end is None:
            sys.exit(f"SPAN END {last}")
        return f"{rel}:{start + 1}-{end + 1}"

    def note_range(self, rel: str, marker: str, type_line: str) -> str:
        lines = self.read(rel).split("\n")
        hits = [i for i, line in enumerate(lines)
                if line == marker and i + 3 < len(lines) and lines[i + 3] == type_line]
        if len(hits) != 1:
            sys.exit(f"NOTE {marker} {type_line}: {len(hits)}")
        end = hits[0] + 1
        while end < len(lines) and lines[end] != "":
            end += 1
        return f"context_compass/{rel}:{hits[0] + 1}-{end}"

    def doc_section(self, name: str, heading: str) -> str:
        rel = f"{self.PATCHES}/{name}"
        lines = self.read(rel).split("\n")
        starts = [i for i, line in enumerate(lines) if line == heading]
        if len(starts) != 1:
            sys.exit(f"HEADING {heading}: {len(starts)}")
        end = starts[0] + 1
        while end < len(lines) and not lines[end].startswith("## "):
            end += 1
        while lines[end - 1].strip() == "":
            end -= 1
        return f"context_compass/{rel}:{starts[0] + 1}-{end}"

    def doc_whole(self, name: str) -> str:
        rel = f"{self.PATCHES}/{name}"
        count = len(self.read(rel).rstrip("\n").split("\n"))
        return f"context_compass/{rel}:1-{count}"

    @staticmethod
    def evidence(paths: list) -> list:
        return ["  EVIDENCE:"] + [f"  - {path}" for path in paths]

    def s2(self) -> None:
        now = self.now
        inventory = "\n".join([
            f"- DATETIME: {now}",
            "  AUTHOR: melder_0",
            "  AUTHOR_ROLE: synaptic_python_developer",
            "  TYPE: FACT",
            "  CLAIM: The spell_id-keyed caches and stores, read on 0.2.8255 (the inventory task). Both creation-cache tiers",
            "    trust the spell_id to cover the binding: the structural key is {format, spell_id, annotation_refs}, its",
            "    docstring saying \"the spell id already covers the spell's own signature, names, existence and",
            "    resolvability\"; the world stamp hashes the sorted pool ids, the posture and the sorted borrowed ids; a",
            "    structural hit needs a well-formed payload, the live stamp, replayable and the live key. The executor tier",
            "    classifies with that same stamp: a full hit needs every live payload-eligible id cached and the bundle's",
            "    recorded stamp equal to the live one, else mixed (some ids cached) or full miss; a non-full-hit conjure",
            "    removes every package, restages every live id and records the stamp after them. A meld stages a package",
            "    only for an id the bundle lacks. So under S1 a binding changed under one spell_id would hit both tiers;",
            "    the binding hash in the key and the stamp closes it (component_patch_creation_cache.md). The in-process",
            "    stores need nothing: a fast meld door holds its Spell object and checks its door epoch and context, so a",
            "    cleaned Spell misses (AttributeError) and the full lane rebuilds; per-conduit verdicts are retired on",
            "    register_index and unregister_index (0.2.8219). The record needs no new field in this landing: the",
            "    SpellCrystal records every manifest field and a restore replays them through bind, which rebuilds the",
            "    manifest. UNKNOWN, S3's: whether a slotted store entry kept under a spell_id hands the old object to a",
            "    rebind with another existence (the 2026-10-03 surviving-product ruling); the blast-radius run probes it.",
        ] + self.evidence([
            self.method(self.SNAP, "structural_key"),
            self.method(self.SNAP, "world_stamp"),
            self.method(self.SNAP, "payload_well_formed"),
            self.method(self.SNAP, "classify"),
            self.method(self.SCS, "_build_conjure_cache_state"),
            self.method(self.SCS, "_stage_spell_payloads_at_conjure_end"),
            self.method(self.BOOK, "_emit_spell_cache"),
            self.span(self.CACHE, "Since generation 19 the envelope also carries", "world carries the same stamp"),
            self.span(self.DOOR, "fast_entry = self._fast_meld_doors.get(spell)", "return instance"),
            self.method(self.STATES, "_forget_resolution_verdicts_locked"),
            self.method(self.CRYSTAL, "describe"),
        ]) + [
            "  IMPACT: S2's component patches can state the cache keys exactly and leave the record, the doors and the",
            "    verdicts alone; the Creations-slot question goes to S3 with a probe.",
            "  NEXT: The DECISION and PLAN notes below; then the blast-radius run with S1.",
            "  REREAD: REQUIRED",
            "  SCORE_0_TO_10: 9",
        ])
        decision = "\n".join([
            f"- DATETIME: {now}",
            "  AUTHOR: melder_0",
            "  AUTHOR_ROLE: synaptic_python_developer",
            "  TYPE: DECISION",
            "  CLAIM: Within the owner's word to land S1 with S2's cache keys: (1) the binding hash joins the SpellCrystal in",
            "    S5, with the record's other changes and its RecordVersion, not in this landing - the crystal already",
            "    records every field the manifest holds and a restore rebuilds the same manifest through bind, so \"the",
            "    record round-trips the manifest\" holds without a format change; the Requirements, Acceptance Criteria",
            "    and EXIT_GATE say so. (2) The four managed settings are in the binding hash: a change of them is a",
            "    binding change and misses both cache tiers once (conservative; no emitted plan reads them); whether such",
            "    a change revalidates or only rebinds the pool stays S3's question. (3) Spell builds its manifest in",
            "    `__init__` from its own arguments, so bind, restore and graft need no new keyword.",
        ] + self.evidence([
            self.doc_section("component_patch_binding_pipeline.md", "## S2 (same landing): the binding manifest"),
            self.doc_whole("component_patch_creation_cache.md"),
        ]) + [
            "  IMPACT: S2 stays inside spell.py, the new binding_manifest.py and the cache files; S5 owns the record change.",
            "  NEXT: The PLAN mapping below.",
            "  REREAD: REQUIRED",
            "  SCORE_0_TO_10: 8",
        ])
        plan = "\n".join([
            f"- DATETIME: {now}",
            "  AUTHOR: melder_0",
            "  AUTHOR_ROLE: synaptic_python_developer",
            "  TYPE: PLAN",
            "  CLAIM: Patch section -> implementation -> validation. (1) Binding Pipeline, S2 section -> binding_manifest.py",
            "    (BindingManifest: value fields, `build`, `binding_hash`, `describe`) and spell.py (the `binding_manifest`",
            "    slot appended last, built at the end of `__init__`, the `binding_hash` property, `describe`, kept through",
            "    cleanup like spell_id) -> test_binding_manifest.py: each field moves the hash, nothing else does, two",
            "    processes and GIL modes agree; a bound, a staged and a restored Spell carry the manifest their bind implies.",
            "    (2) Creation-cache patch, Interface Deltas -> structural_snapshot.py (`PAYLOAD_FORMAT` 2, `structural_key`",
            "    with `binding_hash`, `world_stamp` lines `<id>=<binding_hash>`, `payload_well_formed`, the docstrings) ->",
            "    the structural-snapshot tests moved to format 2, a stamp test per binding field. (3) The same patch's",
            "    generation -> caching_system.py (23 \"binding_manifest_keys\" with its history comment) -> a generation-22",
            "    bundle loads cold. (4) Its docstring rows -> spellbook_creation_system.py (`_build_conjure_cache_state`'s",
            "    comment), generalized_manifest_no_overrides_compiler.py and generalized_manifest.py -> the docstring",
            "    audit. (5) Its integration expectation -> `unique` then `many` in a fresh Aether: structural miss,",
            "    executor mixed, a new provider per meld; the same world twice a full hit. (6) The bind-guard manifest",
            "    regenerated (628 -> 630, with SpellCodeDigest) at the rebuild. spell.py waits for M1-37 (M1-36).",
        ] + self.evidence([
            self.doc_section("component_patch_binding_pipeline.md", "## S2 (same landing): the binding manifest"),
            self.doc_section("component_patch_creation_cache.md", "## Interface Deltas"),
            self.doc_section("component_patch_creation_cache.md", "## Validation Expectations"),
            self.doc_section("architecture_patch.md", "## Changed-Components Matrix"),
        ]) + [
            "  IMPACT: The patch gate's consumption mapping is in place before any S2 code.",
            "  NEXT: The blast-radius run with S1 in a /tmp mirror; read the mailbox for M1-37.",
            "  REREAD: REQUIRED",
            "  SCORE_0_TO_10: 8",
        ])
        t = self.read(self.S2)
        t = self.once(t, "- Updated: 2026-10-18T15:01:53Z\n", f"- Updated: {now}\n", "s2 updated")
        t = self.once(t,
            "- EXIT_GATE: a binding change without a code change misses both cache tiers; the record round-trips the manifest;\n"
            "  byte-identical across processes; docs.\n",
            "- EXIT_GATE: a binding change without a code change misses both cache tiers; a restore rebuilds the same manifest\n"
            "  from the record (its binding hash joins the record in S5); byte-identical across processes; docs.\n",
            "s2 exit")
        t = self.once(t,
            "- The Spell carries the manifest and its hash; `Spell.describe` and the record (the SpellCrystal) show both.\n",
            "- The Spell carries the manifest and its hash; `Spell.describe` shows both. The record (the SpellCrystal) already\n"
            "  records every field and a restore rebuilds the manifest through bind; the hash joins the record in S5.\n",
            "s2 req")
        t = self.once(t,
            "- [ ] Task: the component patch (Binding Pipeline: the manifest; the creation cache's keys; the record).\n"
            "- [ ] Task: inventory every spell_id-keyed cache and store (it feeds S3).\n",
            "- [x] Task: the component patches - the manifest (Binding Pipeline, S2 section) and the creation cache's keys\n"
            "  (component_patch_creation_cache.md), written 2026-10-18; the record's field moves to S5 (DECISION note).\n"
            "- [x] Task: inventory every spell_id-keyed cache and store (FACT note; the Creations slot goes to S3).\n",
            "s2 tasks")
        t = self.once(t, "- The record carries the manifest and a restore replays it.\n",
                      "- A restore rebuilds the same manifest and binding hash from the record (the SpellCrystal records every\n"
                      "  field today).\n", "s2 acceptance")
        t = self.once(t,
            "- Which managed settings belong to the binding hash, or to a pool-only setting (S3's question).\n",
            "- The four managed settings are in the binding hash (DECISION note); whether a change of them revalidates or\n"
            "  only rebinds the pool is S3's question.\n", "s2 open")
        t = self.once(t,
            "- 2026-10-18T15:01:53Z: in_progress on the owner's word to land S1 with this story (the epic's DECISION note).\n",
            "- 2026-10-18T15:01:53Z: in_progress on the owner's word to land S1 with this story (the epic's DECISION note).\n"
            f"- {now}: the inventory (FACT note), the record field moved to S5 and the managed settings in the hash\n"
            "  (DECISION note), the component patches and the mapping (PLAN note).\n", "s2 log")
        t = self.once(t,
            "- ARTIFACTS_REQUIRED: false\n"
            "- ARTIFACT_PATHS:\n"
            "  - none yet (the design's probes are rowed under the epic)\n"
            "- DISPOSITION: retain_as_reference\n"
            "- CLEANUP_TRIGGER: rows are added when this story produces its own artifacts\n",
            "- ARTIFACTS_REQUIRED: true\n"
            "- ARTIFACT_PATHS:\n"
            f"  - {self.PATCHES}/component_patch_binding_pipeline.md (S2 section)\n"
            f"  - {self.PATCHES}/component_patch_creation_cache.md (cache keys)\n"
            "  - the design's probes are rowed under the epic\n"
            "- DISPOSITION: promote_to_documentation (the patch docs, at landing)\n"
            "- CLEANUP_TRIGGER: the patch docs are promoted to the system documents at landing and archived at turn-in\n",
            "s2 artifacts")
        t = self.once(t, "  SCORE_0_TO_10: 7\n\n## Closure Confirmation\n",
                      "  SCORE_0_TO_10: 7\n\n" + inventory + "\n\n" + decision + "\n\n" + plan + "\n\n## Closure Confirmation\n",
                      "s2 notes")
        t = self.once(t,
            "- State: in_progress (melder_0), discovery: lands with S1 on the owner's word (the epic's DECISION note of\n",
            "- State: in_progress (melder_0), implementation: lands with S1 on the owner's word (the epic's DECISION note of\n",
            "s2 state")
        t = self.once(t,
            "- Next: the inventory of spell_id-keyed caches and stores; the component patch; then the landing with S1.\n",
            "- Done: the inventory (FACT note), the component patches (Binding Pipeline S2 section, creation cache), the\n"
            "  record field moved to S5 and the managed settings in the hash (DECISION note), the mapping (PLAN note).\n"
            "- Next: the blast-radius run with S1 in a /tmp mirror; the landing pass once spell.py is back (M1-37).\n",
            "s2 next")
        self.stage(self.S2, t)

    def s1(self) -> None:
        now = self.now
        note = "\n".join([
            f"- DATETIME: {now}",
            "  AUTHOR: melder_0",
            "  AUTHOR_ROLE: synaptic_python_developer",
            "  TYPE: FACT",
            "  CLAIM: S1's patches are updated for the owner's word and decisions (the epic's DECISION notes of",
            "    2026-10-18T14:14:10Z and 15:01:53Z), nothing in src/: the architecture patch is approved and records his",
            "    decisions as DECIDED (the third-party-object reading - type, version and address-free repr - stated for",
            "    him to narrow), invariant 4 counts repr() of an installed third-party object, invariant 7 names the key and",
            "    the stamp, the new invariant 8 states decision B, the matrix gains the binding manifest and the creation",
            "    cache (bind-guard 628 -> 630), and the statements table gains the creation system's and the caching",
            "    system's stamp text and five \"fingerprint\" statements (meld.py, contract/details.py, inspector_utility.py).",
            "    The Binding Pipeline patch carries the corrected refusal texts with no duplicate option, the S2 section",
            "    and the file order (M1-36). The code-description patch states B: a third-party class, metaclass or",
            "    function named `<qualified> <dist>==<version>`, a third-party object `ext:` with its repr, site-packages",
            "    detection and the version lookup. The Spell Examination Profiles patch is approved with its",
            "    recommendation (the fields go).",
        ] + self.evidence([
            self.doc_whole("architecture_patch.md"),
            self.doc_whole("component_patch_binding_pipeline.md"),
            self.doc_whole("code_description_patch_spell_code_digest.md"),
            self.doc_whole("component_patch_spell_examination_profiles.md"),
        ]) + [
            "  IMPACT: S1's patches match what lands; the PLAN note's mapping stands, with SpellCodeDigest gaining the",
            "    site-packages check and the version lookup (measured on the device: importlib.metadata.version about",
            "    0.2 ms, packages_distributions 14.7 ms once).",
            "  NEXT: The blast-radius run in a /tmp mirror with S2.",
            "  REREAD: REQUIRED",
            "  SCORE_0_TO_10: 8",
        ])
        t = self.read(self.S1)
        t = self.once(t, "- Updated: 2026-10-18T15:01:53Z\n", f"- Updated: {now}\n", "s1 updated")
        t = self.once(t,
            "- Bind's cost: code digests memoized; a class over a large third-party base costs milliseconds (D9); measured on\n"
            "  the gauntlet at landing.\n",
            "- Bind's cost: code digests memoized; a class over a large third-party base costs milliseconds when digested\n"
            "  (D9), and decision B names installed bases instead (a version lookup); measured on the gauntlet at landing.\n",
            "s1 risks")
        t = self.once(t,
            f"- 2026-10-18T15:01:53Z: the owner's word to land this story now, with S2's cache keys; duplicates strictly refused, S6\n"
            "  parked (the epic's DECISION note).\n",
            f"- 2026-10-18T15:01:53Z: the owner's word to land this story now, with S2's cache keys; duplicates strictly refused, S6\n"
            "  parked (the epic's DECISION note).\n"
            f"- {now}: the patches updated for decision B and strict uniqueness (FACT note).\n", "s1 log")
        t = self.once(t, "  SCORE_0_TO_10: 8\n\n## Closure Confirmation\n",
                      "  SCORE_0_TO_10: 8\n\n" + note + "\n\n## Closure Confirmation\n", "s1 note")
        t = self.once(t,
            "- Next: the patches updated for B and strict uniqueness; the blast-radius run in a /tmp mirror; the landing\n"
            "  pass with S2.\n",
            "- Done since: the patches updated for B and strict uniqueness (FACT note).\n"
            "- Next: the blast-radius run in a /tmp mirror; the landing pass with S2 once spell.py and spellbook.py are\n"
            "  back (M1-37).\n", "s1 next")
        self.stage(self.S1, t)

    def epic(self) -> None:
        now = self.now
        note = "\n".join([
            f"- DATETIME: {now}",
            "  AUTHOR: melder_0",
            "  AUTHOR_ROLE: synaptic_python_developer",
            "  TYPE: FACT",
            "  CLAIM: Milestone 1 is met: the architecture patch and S1's patches are approved by the owner's word to land",
            "    and updated for his decisions (decision B, strict uniqueness, S6 parked); S2's patches are written - the",
            "    binding manifest (Binding Pipeline, S2 section) and the creation cache's keys (generation 23) - with S2's",
            "    inventory, decisions and mapping in its story. Nothing in src/ yet. The binding hash joins the record in",
            "    S5, not this landing (S2's DECISION note).",
            "  EVIDENCE:",
            f"  - context_compass/{self.PATCHES}/architecture_patch.md:1-{len(self.read(self.PATCHES + '/architecture_patch.md').rstrip(chr(10)).split(chr(10)))}",
            f"  - {self.note_range(self.S1, f'- DATETIME: {now}', '  TYPE: FACT')}",
            f"  - {self.note_range(self.S2, f'- DATETIME: {now}', '  TYPE: FACT')}",
            f"  - {self.note_range(self.S2, f'- DATETIME: {now}', '  TYPE: DECISION')}",
            "  IMPACT: S1 and S2 move to the blast-radius run; their spell.py and spellbook.py edits wait for M1-37.",
            "  NEXT: The blast-radius run in a /tmp mirror.",
            "  REREAD: REQUIRED",
            "  SCORE_0_TO_10: 8",
        ])
        t = self.read(self.EPIC)
        t = self.once(t, "- Updated: 2026-10-18T15:38:29Z\n", f"- Updated: {now}\n", "ep updated")
        t = self.once(t,
            "- [ ] Milestone 1: the owner's calls on the edges; the architecture patch and the first component patches approved.\n",
            "- [x] Milestone 1: the owner's calls on the edges; the architecture patch and the first component patches approved.\n",
            "ep milestone")
        t = self.once(t,
            "- [ ] Task: the architecture patch for the epic; a component patch per story before its code (the architecture\n"
            "  patch and S1's patches written 2026-10-18; the owner's approval pending).\n",
            "- [ ] Task: the architecture patch for the epic; a component patch per story before its code (the architecture\n"
            "  patch and S1's and S2's patches approved by the owner's word to land, 2026-10-18; S3-S5 before their code).\n",
            "ep task")
        t = self.once(t,
            "  binding and caching patterns later (DECISION note).\n\n## Artifact Links (Optional)",
            "  binding and caching patterns later (DECISION note).\n"
            f"- {now}: Milestone 1 met - S1's patches updated, S2's written (FACT note).\n\n## Artifact Links (Optional)",
            "ep log")
        t = self.once(t, "  SCORE_0_TO_10: 8\n\n## Closure Confirmation\n",
                      "  SCORE_0_TO_10: 8\n\n" + note + "\n\n## Closure Confirmation\n", "ep note")
        t = self.once(t,
            "- Next: (1) S1's patches updated for B and strict uniqueness, S2's component patch; (2) the blast-radius run\n"
            "  in a /tmp mirror; (3) the landing pass - red tests, src, green, the moved tests, the whole tree with the\n"
            "  GIL off and on, docs, notches, the rebuild last.\n",
            f"- Done since: S1's patches updated for B and strict uniqueness, S2's patches written (FACT note of\n"
            f"  {now}).\n"
            "- Next: (1) the blast-radius run in a /tmp mirror; (2) M1-37 sets the order with S9; (3) the landing pass -\n"
            "  red tests, src, green, the moved tests, the whole tree with the GIL off and on, docs, notches, the rebuild\n"
            "  last.\n", "ep next")
        self.stage(self.EPIC, t)

    def boards(self) -> None:
        now = self.now
        b = self.read(self.BOARD)
        b = self.once(b,
            "| Land S1 with S2's cache keys on the owner's word: patches, the blast-radius run, the landing pass. |",
            "| The blast-radius run in a /tmp mirror; then the landing pass of S1 and S2 (spell.py with M1-37). |",
            "bd epic next")
        b = self.once(b,
            "| tickets/epics/2026-10-18_spell_identity_is_the_code_epic.md | 2026-10-18T15:01:53Z | REQUIRED |",
            f"| tickets/epics/2026-10-18_spell_identity_is_the_code_epic.md | {now} | REQUIRED |", "bd epic time")
        b = self.once(b,
            "| Update S1's patches for decision B and strict uniqueness; then the blast-radius run in a /tmp mirror. |",
            "| The blast-radius run in a /tmp mirror (the prototype digest for the fingerprint, GIL off and on). |",
            "bd s1 next")
        b = self.once(b,
            "| tickets/stories/2026-10-18_spell_id_hashes_the_object_code_story.md | 2026-10-18T15:01:53Z | REQUIRED |",
            f"| tickets/stories/2026-10-18_spell_id_hashes_the_object_code_story.md | {now} | REQUIRED |", "bd s1 time")
        b = self.once(b,
            "| binding_manifest_hash | in_progress | discovery | claude | melder_0 | none | Inventory the spell_id-keyed "
            "caches and stores; write S2's component patch. |",
            "| binding_manifest_hash | in_progress | implementation | claude | melder_0 | none | The blast-radius run with "
            "S1; the landing pass once spell.py is back (M1-37). |", "bd s2 next")
        b = self.once(b,
            "| tickets/stories/2026-10-18_binding_manifest_hash_story.md | 2026-10-18T15:01:53Z | REQUIRED |",
            f"| tickets/stories/2026-10-18_binding_manifest_hash_story.md | {now} | REQUIRED |", "bd s2 time")
        self.stage(self.BOARD, b)
        a = self.read(self.ARTIFACTS)
        a = self.once(a,
            "| The epic's architecture patch and S1's Binding Pipeline, Spell Examination Profiles and code-description "
            "patches; the owner's approval before any src edit; S2-S5 add theirs. | 2026-10-18T13:42:22Z | REQUIRED |",
            "| The epic's architecture patch, S1's Binding Pipeline, Spell Examination Profiles and code-description "
            "patches and S2's binding manifest (Binding Pipeline, S2 section) and creation-cache patch, approved by the "
            f"owner's word to land (2026-10-18T15:01:53Z); S3-S5 add theirs. | {now} | REQUIRED |", "ab epic")
        row = (f"| tickets/stories/2026-10-18_binding_manifest_hash_story.md | {self.PATCHES}/component_patch_creation_cache.md "
               "| patch_doc | active | promote_to_documentation | S2's creation-cache patch (the binding hash in the "
               "structural key and the world stamp, generation 23); its manifest is the Binding Pipeline patch's S2 "
               f"section in the same folder. | {now} | REQUIRED |\n")
        a = self.once(a, "<!-- END USER-DEFINED: active_artifacts -->", row + "<!-- END USER-DEFINED: active_artifacts -->",
                      "ab s2 row")
        a = self.once(a,
            "update_patches_b_strict.py (S1's patches for decision B and strict uniqueness, S2's binding manifest and "
            "creation-cache patch); probes/ and runs/ are rowed under S1. |",
            "update_patches_b_strict.py and align_patches_after_b.py (S1's patches for decision B and strict uniqueness, "
            "S2's binding manifest and creation-cache patch) and record_s2_patch_and_inventory.py (their record); "
            "probes/ and runs/ are rowed under S1. |", "ab scripts")
        a = re.sub(r"(record_s2_patch_and_inventory\.py \(their record\); probes/ and runs/ are rowed under S1\. \| )"
                   r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z( \|)", rf"\g<1>{now}\g<2>", a, count=1)
        self.stage(self.ARTIFACTS, a)

    def run(self) -> None:
        self.s2()
        self.s1()
        self.epic()
        self.boards()
        for rel, text in self.staged.items():
            if "\r" in text:
                sys.exit(f"CR in {rel}")
        for rel, text in self.staged.items():
            shutil.copy2(self.ROOT / rel, self.BACKUP / (pathlib.Path(rel).name + ".pre_record"))
            (self.ROOT / rel).write_text(text, encoding="utf-8", newline="\n")
        print("OK", self.now, sorted(self.staged))


if __name__ == "__main__":
    Record().run()
