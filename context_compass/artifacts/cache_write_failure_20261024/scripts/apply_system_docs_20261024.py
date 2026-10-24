"""Promote the cache-save fix into src_architecture and src_components (melder_0, 2026-10-24; F5).

Dry run by default; `--apply` writes. Anchored read-modify-write of both documents, all-or-nothing: each document
must still equal its baseline copy (/tmp/m0_mq/f5/<doc>.orig.md, taken with the content-preservation multiset before
the first edit), every anchor must match exactly once (all misses are reported together), and every new line fits
120 characters unless it holds a source path. Numeric citations into spellbook.py past the edit are remapped and each
pair is proved against a line map of HEAD's spellbook.py (/tmp/m0_mq/f5/spellbook.py.head) and the current file:
the cited HEAD line and the new line must be one equal line of the two. The stale settle-then-inherit inner citations,
the `_run_structural_phases` precondition citation and the re-measured cache-flag range are checked by content.
Historical citations inside the handoff summaries are left as written.

Replaces apply_system_docs_20261024_first_try.py, whose run stopped on an anchor (src_components' three seam
citations carry a trailing description) before writing anything.
"""
import datetime
import difflib
import pathlib
import sys
from typing import Callable, Dict, List, Tuple

ROOT = pathlib.Path.home() / "mnt/melder_private"
DOCS = ROOT / "context_compass/system_docs"
BASE = pathlib.Path("/tmp/m0_mq/f5")
NOW = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
CACHE = "src/melder/utilities/caching_system/caching_system.py"
BOOK = "src/melder/aether/spellbook/spellbook.py"
SPELL = "src/melder/aether/spellbook/spell.py"
PORTABILITY = ("context_compass/", "agent_onboarding/", "tools/system_documents/", "index_document.py",
               "system_docs/", "patches/active/")
ERRORS: List[str] = []


def once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        ERRORS.append(f"ANCHOR {label}: found {count}")
        return text
    for line in new.split("\n"):
        if len(line) > 120 and "src/" not in line and not line.startswith("|"):
            ERRORS.append(f"WIDTH {label}: {len(line)}: {line}")
        for marker in PORTABILITY:
            if marker in line:
                ERRORS.append(f"PORTABILITY {label}: {marker}: {line}")
    return text.replace(old, new)


def loc(rel: str) -> int:
    return len((ROOT / rel).read_text(encoding="utf-8").splitlines())


def book_line_map() -> Dict[int, int]:
    head = (BASE / "spellbook.py.head").read_text(encoding="utf-8").splitlines()
    new = (ROOT / BOOK).read_text(encoding="utf-8").splitlines()
    mapping: Dict[int, int] = {}
    for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(None, head, new, autojunk=False).get_opcodes():
        if tag == "equal":
            for k in range(i2 - i1):
                mapping[i1 + k + 1] = j1 + k + 1
    return mapping


def prove_remaps() -> None:
    mapping = book_line_map()
    pairs: List[Tuple[int, int]] = [
        (3949, 3969), (4022, 4042), (4024, 4044), (4087, 4107), (4248, 4268), (4525, 4545), (4558, 4578),
        (4653, 4673), (4734, 4754), (4768, 4788), (4878, 4898), (6147, 6167), (6163, 6183), (6624, 6644),
        (6629, 6649), (7485, 7505), (7553, 7573), (7583, 7603), (7595, 7615), (7596, 7616), (7809, 7829),
        (8172, 8192), (8183, 8203), (8193, 8213)]
    for old, new in pairs:
        if mapping.get(old) != new:
            ERRORS.append(f"REMAP spellbook.py:{old} maps to {mapping.get(old)}, not {new}")
    lines = (ROOT / BOOK).read_text(encoding="utf-8").splitlines()
    content = {
        7603: "if dynamic and not frame_configuration._frozen:",
        7615: "self._aetheric_frame.bind_frame_configuration(frame_configuration)",
        7616: "return frame_configuration.system_state is SystemState.dynamic",
        8203: "Caller must hold the Spellbook lock for deterministic conjure ordering.",
        1179: "if not self._cache_emit_required:",
        1181: "with self._lock:",
        1184: "self._cache_emit_required = False",
        1186: "return self._get_or_create_caching_system().emit()",
        1189: "self._cache_emit_required = True",
    }
    for number, expected in content.items():
        if expected not in lines[number - 1]:
            ERRORS.append(f"CONTENT spellbook.py:{number}: {lines[number - 1].strip()!r}")


def architecture(text: str) -> str:
    text = once(text, "## Operational Invariants\n- Cluster admission reserves one conduit at a time (0.2.8265)", """\
## Operational Invariants
- Cache saves are best-effort (2026-10-24, 0.2.8266; TASK-2026-10-24-cache_file_write_failure_fails_meld, on the
  owner's go, chat 2026-10-24: "yeah go ahead with all hte recommended things you need to do"): a creation-cache
  bundle is an accelerator - a missing or unreadable one already only made the cache cold - so a save the operating
  system refuses no longer fails the call that triggered it. `CachingSystem.emit()` returns True when the bundle was
  written and False when the folder, the temp write or the rename raised OSError; it never raises one. A refused
  save removes the temp file it started (one it cannot remove is logged with its path), leaves the bundle on disk as
  it was, keeps every staged payload in memory and logs the refusal - at WARNING the first time for that bundle, with
  the path, the error and the remedies (a writable cache folder; on Windows an exclusion from real-time scanning; or
  `with_system_caching_enabled(False)` for the frame), at DEBUG after. Each writer saves through its own temp file,
  `<conduit>.meldercache.<pid>.<thread id>.tmp`, so processes sharing a frame and root name never share one. On
  Windows only (`RETRY_REFUSED_RENAME`) a rename refused with PermissionError - [WinError 5] while another handle,
  such as an on-access scanner, holds the bundle open - is retried: five attempts within about 100 ms. POSIX renames
  do not refuse for sharing, so elsewhere the first refusal is final. `Spellbook._emit_cache_file_if_required`,
  which every meld door, the end of conjure and the explicit save call, returns what `emit()` returned and leaves its
  save flag cleared after a refusal: no meld retries the save or waits on it, and the next staging or conjure saves
  what is still staged. Any other error of a save still restores the flag and propagates (the end of conjure logs
  it). `Spell.emit_cache_file()` returns False for a refused save. Locks: the save runs under the CachingSystem's
  RLock as before and the Book lock is taken only around the flag; a Windows retry sleeps under the CachingSystem's
  lock, delaying only that Book's cache calls; no lock or lock-order edge is added. The cache envelope and its
  generation (23) are unchanged.
  EVIDENCE: `src/melder/utilities/caching_system/caching_system.py:CachingSystem.emit`,
  `CachingSystem._write_current_cache_to_disk_locked`, `CachingSystem._replace_bundle_locked`,
  `CachingSystem._log_refused_save_locked`,
  `src/melder/aether/spellbook/spellbook.py:Spellbook._emit_cache_file_if_required` and
  `src/melder/aether/spellbook/spell.py:Spell.emit_cache_file`.
- Cluster admission reserves one conduit at a time (0.2.8265)""", "arch invariant")
    text = once(text, "## Failure Modes and Error Paths\n- Fixed in 0.2.8263:", """\
## Failure Modes and Error Paths
- Fixed in 0.2.8266: a creation-cache save the operating system refuses no longer fails the meld that triggered it.
  Every meld door saves the bundle after building its object when the meld staged new cache (a spell compiled at its
  first meld - one bound after conjure, for example), and the save raised its OSError to the caller: on Windows
  PermissionError [WinError 5] from the rename while another handle held the bundle (MelderOps' `Spectrum.configure`
  failed so on 0.2.8265; the holder there is not identified - an on-access scanner is suspected), on any platform for
  a read-only cache folder or a full disk. The object had been built and stored - a `unique` came back from the next
  meld, a `many` was lost to its caller, a managed lease stayed out of its pool for good - and while the refusal
  lasted every meld of the Book raised; the refused rename also left `<conduit>.meldercache.tmp` beside the bundle.
  Now the meld returns its object, the pool keeps its place, and the save logs one WARNING per bundle and removes
  its temp file.
  EVIDENCE: `src/melder/utilities/caching_system/caching_system.py:CachingSystem.emit` and
  `src/melder/aether/spellbook/spellbook.py:Spellbook._emit_cache_file_if_required`.
- Breaking (0.2.8266): `Spell.emit_cache_file()` returns False when the operating system refuses the save (the
  Book's cache utility logs it), where it raised the OSError; True still means the bundle was written, and False
  also covers caching off and nothing staged since the last save.
  EVIDENCE: `src/melder/aether/spellbook/spell.py:Spell.emit_cache_file`.
- Fixed in 0.2.8263:""", "arch failure modes")
    text = once(text, f"""\
- path: `{BOOK}`
  start_line: 1
  end_line: 8378
  loc: 8378
  verified_at: 2026-10-19T14:19:12Z
""", f"""\
- path: `{BOOK}`
  start_line: 1
  end_line: {loc(BOOK)}
  loc: {loc(BOOK)}
  verified_at: {NOW}
""", "arch map spellbook")
    text = once(text, """\
    `_apply_notch` no longer journals (0.2.8262). `_destroy_spell_index` drops a route only when it routes its
    key to the destroyed index and releases only the departing member's claim, by spell_id (0.2.8263).
""", """\
    `_apply_notch` no longer journals (0.2.8262). `_destroy_spell_index` drops a route only when it routes its
    key to the destroyed index and releases only the departing member's claim, by spell_id (0.2.8263).
    `_emit_cache_file_if_required` returns the save's bool and leaves its flag cleared after a refused save (0.2.8266).
""", "arch map spellbook note")
    text = once(text, f"""\
- path: `{SPELL}`
  start_line: 1
  end_line: 2027
  loc: 2027
  verified_at: 2026-10-19T00:01:11Z
""", f"""\
- path: `{SPELL}`
  start_line: 1
  end_line: {loc(SPELL)}
  loc: {loc(SPELL)}
  verified_at: {NOW}
""", "arch map spell")
    text = once(text, """\
    (0.2.8257); `_spell_index_unless_cleaned` lists the root's teardown among its readers (0.2.8259).
""", """\
    (0.2.8257); `_spell_index_unless_cleaned` lists the root's teardown among its readers (0.2.8259).
    `emit_cache_file` returns False for a refused save (0.2.8266).
""", "arch map spell note")
    text = once(text, f"""\
- path: `{CACHE}`
  start_line: 1
  end_line: 918
  loc: 918
  verified_at: 2026-10-18T20:24:47Z
  note: release-bound creation-cache admission, the envelope's world stamp and atomic persistence;
    generation 22, "managed_settings_leave_spell_id" (0.2.8254). Generation 23, "binding_manifest_keys" (0.2.8258).
""", f"""\
- path: `{CACHE}`
  start_line: 1
  end_line: {loc(CACHE)}
  loc: {loc(CACHE)}
  verified_at: {NOW}
  note: release-bound creation-cache admission, the envelope's world stamp and atomic persistence;
    generation 22, "managed_settings_leave_spell_id" (0.2.8254). Generation 23, "binding_manifest_keys" (0.2.8258).
    `emit()` is best-effort: a bool, a per-writer temp file, a Windows-only rename retry, one WARNING per bundle
    (0.2.8266).
""", "arch map cache")
    text = once(text, "## Context / Handoff Summary\n\n2026-10-19 cluster admission (0.2.8265):", """\
## Context / Handoff Summary

2026-10-24 cache saves are best-effort (0.2.8266; TASK-2026-10-24-cache_file_write_failure_fails_meld, on the
owner's go "yeah go ahead with all hte recommended things you need to do"): a save the operating system refuses no
longer fails a meld - `CachingSystem.emit()` returns False and logs, its temp file is per writer and removed, a
Windows sharing refusal of the rename is retried, and the Book leaves its save flag cleared; `Spell.emit_cache_file()`
returns False (Breaking). A new operational invariant, two failure modes (one fixed, one Breaking) and the code map
(three files remeasured) carry it; the component map carries the per-component contracts. Numeric citations into
spellbook.py past the edit moved 20 lines and were remapped line by line; the settle-then-inherit inner citations
(:6971-6983, :6984), stale since an earlier lane, point at the settlement block and its return again. Open: the
Windows holder behind the owner's failure is not identified (an on-access scanner is suspected).

2026-10-19 cluster admission (0.2.8265):""", "arch summary")
    citations = [
        ("`src/melder/aether/spellbook/spellbook.py:4022-4024`, which states the",
         "`src/melder/aether/spellbook/spellbook.py:4042-4044`, which states the"),
        ("  - src/melder/aether/spellbook/spellbook.py:4525 (`_add_to_spell_index` entry)\n",
         "  - src/melder/aether/spellbook/spellbook.py:4545 (`_add_to_spell_index` entry)\n"),
        ("  - src/melder/aether/spellbook/spellbook.py:4558 (`_apply_add_to_index` seam)\n",
         "  - src/melder/aether/spellbook/spellbook.py:4578 (`_apply_add_to_index` seam)\n"),
        ("EVIDENCE: src/melder/aether/spellbook/spellbook.py:4087-4878 (the three seams, remeasured 2026-10-16 at 0.2.8251);",
         "EVIDENCE: src/melder/aether/spellbook/spellbook.py:4107-4898 (the three seams, remeasured 2026-10-24 at 0.2.8266);"),
        ("   - src/melder/aether/spellbook/spellbook.py:4087-4248\n   - src/melder/aether/spellbook/spellbook.py:4558-4653\n"
         "   - src/melder/aether/spellbook/spellbook.py:4768-4878\n",
         "   - src/melder/aether/spellbook/spellbook.py:4107-4268\n   - src/melder/aether/spellbook/spellbook.py:4578-4673\n"
         "   - src/melder/aether/spellbook/spellbook.py:4788-4898\n"),
        ("  - src/melder/aether/spellbook/spellbook.py:7553-7596\n"
         "    (`Spellbook._settle_or_inherit_conjure_mode`; in-place settle :6971-6983,\n"
         "    effective-mode return :6984; remeasured 2026-10-16 at 0.2.8251)\n"
         "  - src/melder/aether/spellbook/spellbook.py:7809\n",
         "  - src/melder/aether/spellbook/spellbook.py:7573-7616\n"
         "    (`Spellbook._settle_or_inherit_conjure_mode`; in-place settle :7603-7615,\n"
         "    effective-mode return :7616; remeasured 2026-10-24 at 0.2.8266)\n"
         "  - src/melder/aether/spellbook/spellbook.py:7829\n"),
    ]
    for number, (old, new) in enumerate(citations, 1):
        text = once(text, old, new, f"arch citation {number}")
    return text


def components(text: str) -> str:
    text = once(text, """\
  `src/melder/utilities/caching_system/caching_system.py:CachingSystem.CACHE_VERSION_HISTORY`.
EVIDENCE: `src/melder/utilities/caching_system/caching_system.py:CachingSystem`,
`src/melder/aether/spellbook/spellbook.py:Spellbook._emit_cache_file_if_required` and
""", """\
  `src/melder/utilities/caching_system/caching_system.py:CachingSystem.CACHE_VERSION_HISTORY`.
- Best-effort saves (2026-10-24, 0.2.8266): `CachingSystem.emit()` returns True when the bundle was written and False
  when an OSError of the folder, the temp write or the rename refused the save; it never raises one. The write saves
  through `<conduit>.meldercache.<pid>.<thread id>.tmp` (`_temp_bundle_path`) and renames it in
  `_replace_bundle_locked` - on Windows (`RETRY_REFUSED_RENAME`) a PermissionError is retried up to
  `REPLACE_ATTEMPTS` (5) attempts with `REPLACE_RETRY_DELAY_SECONDS` (0.01 s) times the attempt between them, about
  100 ms under the instance lock; elsewhere the first refusal is final - and replaces `_cache_data` only after the
  rename. A refusal removes the temp file it started (`_discard_temp_bundle_locked`; an OSError there is logged at
  WARNING with the leftover path), keeps every staged payload in memory and logs through
  `_log_refused_save_locked`: WARNING the first time for the instance (slot `_refused_save_logged`, deleted in
  cleanup), DEBUG after, naming the bundle, the error, that melds are unaffected, and the remedies.
  `Spellbook._emit_cache_file_if_required` returns emit's result and leaves `_cache_emit_required` cleared after a
  refusal - the meld doors (ten call sites) and the end of conjure ignore the result and `_emit_cache_file` passes
  it on, so no meld fails on a refused save or retries it - while any other exception restores the flag and
  propagates (the end of conjure logs it). `Spell.emit_cache_file()` returns False for a refused save (Breaking).
  The envelope and the generation (23) are unchanged.
  EVIDENCE: `src/melder/utilities/caching_system/caching_system.py:CachingSystem.emit`,
  `CachingSystem._write_current_cache_to_disk_locked`, `CachingSystem._replace_bundle_locked`,
  `src/melder/aether/spellbook/spellbook.py:Spellbook._emit_cache_file_if_required` and
  `src/melder/aether/spellbook/spell.py:Spell.emit_cache_file`.
EVIDENCE: `src/melder/utilities/caching_system/caching_system.py:CachingSystem`,
`src/melder/aether/spellbook/spellbook.py:Spellbook._emit_cache_file_if_required` and
""", "comp cache bullet")
    text = once(text, """\
Failure Modes:
- `SpellbookValidationError` when Phase 1-4 produces broken spells.
""", """\
Failure Modes:
- `SpellbookValidationError` when Phase 1-4 produces broken spells.
- A creation-cache save the operating system refuses raises nothing (0.2.8266): `_emit_cache_file_if_required`
  returns False with its flag cleared and the CachingSystem logs the refusal once per bundle at WARNING. Until
  0.2.8266 every meld door raised the OSError after building its object - on Windows PermissionError [WinError 5] -
  and, while the refusal lasted, every meld of the Book.
""", "comp failure mode")
    text = once(text, """\
5. A subsequent compatible run follows the existing cache-hit and context-hydration paths.
""", """\
5. A subsequent compatible run follows the existing cache-hit and context-hydration paths.
6. A save the operating system refuses fails neither the conjure nor the meld that triggered it (0.2.8266):
   CachingSystem.emit returns False, logs and keeps the staged payloads, and _emit_cache_file_if_required
   leaves the flag cleared, so the next staging or conjure writes the bundle.
""", "comp flow")
    text = once(text, f"""\
- path: `{CACHE}`
  start_line: 1
  end_line: 918
  loc: 918
  verified_at: 2026-10-18T20:32:16Z
  note: release-bound creation-cache admission and atomic envelope persistence; generation 22 (0.2.8254).
    Generation 23, the binding hash in the structural key and the world stamp (0.2.8258).
""", f"""\
- path: `{CACHE}`
  start_line: 1
  end_line: {loc(CACHE)}
  loc: {loc(CACHE)}
  verified_at: {NOW}
  note: release-bound creation-cache admission and atomic envelope persistence; generation 22 (0.2.8254).
    Generation 23, the binding hash in the structural key and the world stamp (0.2.8258).
    The save is best-effort: `emit()` returns a bool and never raises OSError (0.2.8266).
""", "comp map cache")
    text = once(text, f"""\
- path: `{BOOK}`
  start_line: 1
  end_line: 8378
  loc: 8378
  verified_at: 2026-10-19T14:19:12Z
""", f"""\
- path: `{BOOK}`
  start_line: 1
  end_line: {loc(BOOK)}
  loc: {loc(BOOK)}
  verified_at: {NOW}
""", "comp map spellbook")
    text = once(text, f"""\
- path: `{SPELL}`
  start_line: 1
  end_line: 2027
  loc: 2027
  verified_at: 2026-10-19T00:01:11Z
""", f"""\
- path: `{SPELL}`
  start_line: 1
  end_line: {loc(SPELL)}
  loc: {loc(SPELL)}
  verified_at: {NOW}
""", "comp map spell")
    text = once(text, "## Context / Handoff Summary\n\n2026-10-19 cluster admission (0.2.8265):", """\
## Context / Handoff Summary

2026-10-24 cache saves are best-effort (0.2.8266; TASK-2026-10-24-cache_file_write_failure_fails_meld): the Spellbook
Core's release-bound cache entry describes the save's bool, the per-writer temp file, the Windows-only rename retry,
the one WARNING per bundle and the save flag left cleared after a refusal; its failure modes gain the refused save;
the cold-cache flow gains its refusal step; the CachingSystem, Spellbook and Spell code-map extents are remeasured.
Numeric citations into spellbook.py past the edit moved 20 lines and were remapped; the `_run_structural_phases`
precondition citation (:7423, stale since an earlier lane) points at its docstring line again, and the cache-flag
citation at the re-measured method. Verify next: the Windows holder behind the owner's failure (unidentified).

2026-10-19 cluster admission (0.2.8265):""", "comp summary")
    citations = [
        ("spellbook.py:3949, 4087", "spellbook.py:3969, 4107"),
        ("spellbook.py:4525, 4558", "spellbook.py:4545, 4578"),
        ("spellbook.py:4734, 4768", "spellbook.py:4754, 4788"),
        ("  - src/melder/aether/spellbook/spellbook.py:8172-8193 (`_run_structural_phases`; the caller-held-lock\n"
         "    precondition is stated at :7423; remeasured 2026-10-16 at 0.2.8248)\n",
         "  - src/melder/aether/spellbook/spellbook.py:8192-8213 (`_run_structural_phases`; the caller-held-lock\n"
         "    precondition is stated at :8203; remeasured 2026-10-24 at 0.2.8266)\n"),
        ("  - src/melder/aether/spellbook/spellbook.py:1166-1177 (the cache-emit flag re-checked and set under `_lock`)\n",
         "  - src/melder/aether/spellbook/spellbook.py:1179-1189 (the cache-emit flag re-checked and cleared under `_lock`,\n"
         "    and set again under it when the save raises; remeasured 2026-10-24 at 0.2.8266)\n"),
        ("  - src/melder/aether/spellbook/spellbook.py:4087-4248 (`_apply_notch`)\n",
         "  - src/melder/aether/spellbook/spellbook.py:4107-4268 (`_apply_notch`)\n"),
        ("  - src/melder/aether/spellbook/spellbook.py:4558-4653 (`_apply_add_to_index`)\n",
         "  - src/melder/aether/spellbook/spellbook.py:4578-4673 (`_apply_add_to_index`)\n"),
        ("  - src/melder/aether/spellbook/spellbook.py:4768-4878 (`_apply_remove_from_index`)\n",
         "  - src/melder/aether/spellbook/spellbook.py:4788-4898 (`_apply_remove_from_index`)\n"),
        ("src/melder/aether/spellbook/spellbook.py:6624-6629 (`Spellbook._initialize_configuration`, the\n"
         "    configuration-mismatch branch; remeasured 2026-10-16 at 0.2.8248)",
         "src/melder/aether/spellbook/spellbook.py:6644-6649 (`Spellbook._initialize_configuration`, the\n"
         "    configuration-mismatch branch; remeasured 2026-10-24 at 0.2.8266)"),
        ("  - src/melder/aether/spellbook/spellbook.py:6147-6163 (`Spellbook.bind\n",
         "  - src/melder/aether/spellbook/spellbook.py:6167-6183 (`Spellbook.bind\n"),
        ("spellbook.py:4087, 4558, 4768", "spellbook.py:4107, 4578, 4788"),
        ("`src/melder/aether/spellbook/spellbook.py:7485`; the patch-lane copy cited",
         "`src/melder/aether/spellbook/spellbook.py:7505`; the patch-lane copy cited"),
    ]
    for number, (old, new) in enumerate(citations, 1):
        text = once(text, old, new, f"comp citation {number}")
    # The two copies of the 4022-4024 citation (the boundary list and the SpellIndex mutation subcomponent).
    old_cite = "src/melder/aether/spellbook/spellbook.py:4022-4024"
    if text.count(old_cite) != 2:
        ERRORS.append(f"ANCHOR comp 4022-4024: found {text.count(old_cite)}")
    text = text.replace(old_cite, "src/melder/aether/spellbook/spellbook.py:4042-4044")
    return text


def main() -> None:
    apply = sys.argv[1:] == ["--apply"]
    prove_remaps()
    staged: Dict[str, str] = {}
    edits: Tuple[Tuple[str, Callable[[str], str]], ...] = (
        ("src_architecture.md", architecture), ("src_components.md", components))
    for name, edit in edits:
        current = (DOCS / name).read_text(encoding="utf-8")
        baseline = (BASE / name.replace(".md", ".orig.md")).read_text(encoding="utf-8")
        if current != baseline:
            sys.exit(f"RACE {name}: changed since the baseline; nothing written")
        text = edit(current)
        if "\r" in text:
            ERRORS.append(f"CR {name}")
        staged[name] = text
        print(name, len(current.splitlines()), "->", len(text.splitlines()), "lines")
    if ERRORS:
        print("\n".join(ERRORS))
        sys.exit(f"{len(ERRORS)} problem(s); nothing written")
    if not apply:
        print("dry run OK; nothing written (pass --apply)")
        return
    for name, text in staged.items():
        (DOCS / name).write_text(text, encoding="utf-8", newline="\n")
        print("wrote", name)


if __name__ == "__main__":
    main()
