#!/usr/bin/env python3
"""Trim src_architecture to its authoring spec; move the MutationResearch boundary inventory to src_components.

EPIC-2026-10-24-src_architecture_to_spec, STORY-2026-10-24-src_architecture_trim_to_spec (melder_3). Version 2.1.

    python3 trim_src_architecture.py --arch <src_architecture.md> --comp <src_components.md> --src <repo root>
        --out <dir> [--history <old src_architecture.md> <old src_components.md>] [--apply]

--src is the repository root: the C1 ranges are remeasured from it and one EVIDENCE line is computed from it.

Every operation asserts that its anchor occurs exactly once; any miss stops the run before anything is written.
Without --apply only <dir> is written: both results, a per-operation report of every removed and added line, and the
whole-run multiset accounting over both documents. --history names the two documents at a git revision; removed
lines found there are history, the rest are listed as unaccounted. With --apply both documents are rewritten in place.
"""
import argparse
import collections
import datetime
import pathlib
import re
import sys
import textwrap


class OpError(Exception):
    """An operation's anchor did not match exactly once."""


def norm(line):
    return " ".join(line.split())


def multiset(text):
    return collections.Counter(norm(x) for x in text.split("\n") if x.strip())


def wrap(paragraph, first="", rest="", width=116):
    return textwrap.wrap(paragraph, width=width, initial_indent=first, subsequent_indent=rest,
                         break_on_hyphens=False, break_long_words=False)


class Doc:
    def __init__(self, name, text):
        self.name = name
        self.text = text
        self.log = []

    def apply(self, label, fn, allow_noop=False):
        before = self.text
        after = fn(before)
        if after == before and not allow_noop:
            raise OpError(f"{self.name}: {label}: no change")
        b, a = multiset(before), multiset(after)
        self.log.append((label, b - a, a - b))
        self.text = after


def section_range(ls, heading):
    hits = [i for i, x in enumerate(ls) if x == heading]
    if len(hits) != 1:
        raise OpError(f"section {heading!r}: {len(hits)} matches")
    s = hits[0]
    e = next((i for i in range(s + 1, len(ls)) if ls[i].startswith("## ")), len(ls))
    return s, e


def entry_range(ls, s, e, prefix, label):
    starts = [i for i in range(s + 1, e) if ls[i].startswith("- ")]
    hits = [i for i in starts if ls[i].startswith(prefix)]
    if len(hits) != 1:
        raise OpError(f"{label}: entry {prefix[:70]!r}: {len(hits)} matches")
    a = hits[0]
    later = [i for i in starts if i > a]
    b = later[0] if later else e
    while b > a + 1 and ls[b - 1].strip() == "":
        b -= 1
    return a, b


def evidence_tail(entry):
    idx = [i for i, x in enumerate(entry) if x.startswith("  EVIDENCE")]
    if not idx:
        raise OpError(f"no EVIDENCE in entry {entry[0][:60]!r}")
    return entry[idx[0]:]


def replace_once(old, new):
    def fn(text):
        n = text.count(old)
        if n != 1:
            raise OpError(f"anchor found {n} times: {old[:90]!r}")
        return text.replace(old, new, 1)
    return fn


def regex_once(pattern, repl):
    def fn(text):
        new, n = re.subn(pattern, repl, text, count=0, flags=re.M)
        if n != 1:
            raise OpError(f"pattern matched {n} times: {pattern[:90]!r}")
        return new
    return fn


def remove_entry(section, prefix):
    def fn(text):
        ls = text.split("\n")
        s, e = section_range(ls, section)
        a, b = entry_range(ls, s, e, prefix, "remove")
        return "\n".join(ls[:a] + ls[b:])
    return fn


def rewrite_entry(section, prefix, build):
    def fn(text):
        ls = text.split("\n")
        s, e = section_range(ls, section)
        a, b = entry_range(ls, s, e, prefix, "rewrite")
        return "\n".join(ls[:a] + build(ls[a:b]) + ls[b:])
    return fn


def replace_block(start_prefix, end_contains, new_lines, within=None, eat_blank_before=False):
    def fn(text):
        ls = text.split("\n")
        lo, hi = (0, len(ls)) if within is None else section_range(ls, within)
        starts = [i for i in range(lo, hi) if ls[i].startswith(start_prefix)]
        if len(starts) != 1:
            raise OpError(f"block start {start_prefix[:70]!r}: {len(starts)} matches")
        a = starts[0]
        ends = [i for i in range(a, hi) if end_contains in ls[i]]
        if not ends:
            raise OpError(f"block end {end_contains[:70]!r} not found")
        b = ends[0]
        if eat_blank_before and a > 0 and ls[a - 1].strip() == "":
            a -= 1
        return "\n".join(ls[:a] + new_lines + ls[b + 1:])
    return fn


def split_lead(s):
    """First top-level clause of a note: up to a ';' or a sentence end outside parentheses and backticks."""
    depth, tick = 0, False
    for i, ch in enumerate(s):
        if ch == "`":
            tick = not tick
        elif not tick:
            if ch == "(":
                depth += 1
            elif ch == ")":
                depth = max(0, depth - 1)
            elif depth == 0 and (ch == ";" or (ch == "." and s[i + 1:i + 2] == " ")):
                return s[:i], s[i + 1:]
    return None, None


RESEARCH_SET_NOTES = {
    "grouped_research_node.py": "`GroupedResearchNode`, the composition node of the formal research record.",
    "network_versioner.py": "`NetworkVersioner`, part of the formal research record.",
    "research_journal.py": "`ResearchJournal`, part of the formal research record.",
    "research_lane.py": "`ResearchLane` with `LaneState` and `LaneType`, part of the formal research record.",
    "research_node.py": "`ResearchNode`, part of the formal research record.",
    "research_set.py": "`ResearchSet`, the facade of the formal research record.",
    "residence_registry.py": "`ResidenceRegistry`, part of the formal research record.",
    "transition_entry.py": "`TransitionEntry` with `TransitionAct`, part of the formal research record.",
}
KEEP_NOTE = ("src/melder/_build_assets/_bind_guard/manifest/bind_guard_manifest.py",)
MR_ROOT_NOTE = "hosted mutation-research root owned by Aether (ResearchSet registry + composition emission)."
STRAY_DIR_LINE = "  (directory description carried forward) the formal research record:"


def trim_c1_notes(text):
    ls = text.split("\n")
    s, e = section_range(ls, "## C1 Code Map (Core Only)")
    out, i, stray = ls[:s], s, 0
    while i < e:
        if ls[i].startswith(STRAY_DIR_LINE):
            stray += 1
            i += 1
            continue
        if not ls[i].startswith("  note:"):
            out.append(ls[i])
            i += 1
            continue
        j = i + 1
        while j < e and ls[j].startswith("    "):
            j += 1
        block = ls[i:j]
        body = " ".join(x.strip() for x in block)[len("note:"):].strip()
        path = next((ls[k] for k in range(i - 1, s, -1) if ls[k].startswith("- path:")), "")
        new = None
        name = path.rsplit("/", 1)[-1].rstrip("`")
        if "/mutation_research/research_set/" in path and name in RESEARCH_SET_NOTES:
            new = RESEARCH_SET_NOTES[name]
        elif path.endswith("/mutation_research/mutation_research.py`"):
            new = MR_ROOT_NOTE
        elif "0.2." in body and not any(k in path for k in KEEP_NOTE):
            lead, rest = split_lead(body)
            if lead is not None and "0.2." in rest:
                new = lead.rstrip(" ,") + "."
        if new is None:
            out.extend(block)
        else:
            out.extend(wrap("note: " + new, first="  ", rest="    "))
        i = j
    if stray != 1:
        raise OpError(f"stray directory line: {stray} matches")
    return "\n".join(out + ls[e:])


C1_HEADING = "## C1 Code Map (Core Only)"
C1_INTRO_NEW = wrap(
    "Ranges are MEASURED, never estimated: `start_line`/`end_line` are the file's own extent and `loc` is its line "
    "count, read from disk at `verified_at`. A directory is never an entry; it is expanded into its modules. `note` is "
    "a short description of the file beside the five contract fields; what changed in a file is recorded in the "
    "Context / Handoff Summary, not in its note.")


def c1_intro(text):
    ls = text.split("\n")
    s, e = section_range(ls, C1_HEADING)
    starts = [i for i in range(s, e) if ls[i].startswith("Ranges are MEASURED, never estimated:")]
    ends = [i for i in range(s, e) if ls[i].startswith("contract fields are the contract; the note is additional.")]
    if len(starts) != 1 or len(ends) != 1 or ends[0] < starts[0] or ls[s + 1].strip() != "":
        raise OpError("C1 intro anchors")
    a, b = starts[0], ends[0] + 1
    while b < e and ls[b].strip() == "":
        b += 1
    ls = ls[:a] + ls[b:]
    return "\n".join(ls[:s + 2] + C1_INTRO_NEW + [""] + ls[s + 2:])


def c1_remeasure(src_root, stamp):
    """Remeasure every C1 entry from disk: whole-file range, splitlines() count, verified_at = this run."""
    def fn(text):
        ls = text.split("\n")
        s, e = section_range(ls, C1_HEADING)
        count = 0
        for i in range(s, e):
            m = re.match(r"^- path: `([^`]+)`$", ls[i])
            if not m:
                continue
            path = src_root / m.group(1)
            if not path.is_file():
                raise OpError(f"C1 path does not resolve: {m.group(1)}")
            n = len(path.read_bytes().decode("utf-8").splitlines())
            fields = {}
            for j in range(i + 1, min(i + 6, e)):
                mm = re.match(r"^  (start_line|end_line|loc|verified_at): ", ls[j])
                if mm:
                    fields[mm.group(1)] = j
            if set(fields) != {"start_line", "end_line", "loc", "verified_at"}:
                raise OpError(f"C1 entry fields incomplete: {m.group(1)}")
            ls[fields["start_line"]] = "  start_line: 1"
            ls[fields["end_line"]] = f"  end_line: {n}"
            ls[fields["loc"]] = f"  loc: {n}"
            ls[fields["verified_at"]] = f"  verified_at: {stamp}"
            count += 1
        if count == 0:
            raise OpError("no C1 entries")
        return "\n".join(ls)
    return fn


def link_type_check_citation(src_root):
    """The Runtime Type Names citation of Conduit.link's type check, measured from the source."""
    def fn(text):
        lines = (src_root / "src/melder/aether/conduit/conduit.py").read_text(encoding="utf-8").split("\n")
        a = [i + 1 for i, x in enumerate(lines) if x.strip() == "if not isinstance(target_conduit, Conduit):"]
        b = [i + 1 for i, x in enumerate(lines)
             if x.strip().startswith('raise TypeError(f"Expected Conduit-compatible object')]
        if len(a) != 1 or len(b) != 1 or not 0 < b[0] - a[0] <= 3:
            raise OpError("Conduit.link type check not found in conduit.py")
        return regex_once(
            r"conduit\.py:\d+-\d+ \(the check and the raise -\n    cited as :4342-4344 in the patch lane, which was off "
            r"by one\)", f"conduit.py:{a[0]}-{b[0]} (the check and the raise)")(text)
    return fn


OI = "## Operational Invariants"
FM = "## Failure Modes and Error Paths"

INVARIANT_REMOVALS = [
    "- Owner-store constants on the warm path (2026-10-03, 0.2.8221)",
    "- Executor-cache world stamp (2026-10-03, 0.2.8220)",
    "- Annotation matching by address key (2026-10-03, 0.2.8218;",
    "- Lazy `instance_results` (2026-10-03, 0.2.8217)",
    "- Many registration trim (2026-10-02, 0.2.8216)",
    "- Injected dependencies resolve on their first direct meld (2026-09-30, 0.2.8215)",
    "- Per-frame spell worlds record and restore intact (2026-09-30, 0.2.8213-0.2.8214)",
    "- Shared document-view initialization (2026-09-28)",
    "- Compiler pool reads (2026-09-26)",
    "- Override key-set plans and the site-plan runtime (2026-09-26)",
    "- Deterministic codegen signatures and live contract override operands (2026-09-26)",
    "- Structural snapshot (2026-09-26)",
    "- Process-stable spell ids and complete cache bundles (2026-09-26)",
    "- Door-held first builds (2026-09-26, 0.2.73)",
    "- Creation-cache release compatibility (2026-09-24)",
    "- Dynamic named recording stores detached ancestor values inside each surviving named twin.",
    "- Nexus named lifecycle replaces existing payloads and clears names/parents into pooled records",
    "- Pooled hook ownership (2026-09-22)",
    "- Pool return completes creation disposal before clearing local lifecycle hooks",
    "- Hook setters/register methods validate full batches and use existing writer locks.",
    "- Bind lifecycle hooks (2026-09-22)",
    "- Pre receives the supplied reference; activation/post receive the actual Spell.",
    "- Graduation configuration and hook ownership (2026-09-22)",
    "- Old Book-specific configured hooks, runtime Bind changes and lesser/Space Conduit/Meld overlays",
    "- Scoped creation purge (2026-09-21)",
    "- Non-resolvable definitions keep descriptive local topology",
    "- Nexus binds capability and selected dependency/reference/direct-base links",
    "- SpellCrystal records the native capability.",
    "- Selector-sensitive required inputs reuse the existing frame-key watcher.",
    "- Phase-5 dependency visibility is broader than canonical artifact publication.",
]

INVARIANT_TRIMS = [
    ("  construction; the Phase-4 warning SPELLMAP_BINDING_NAME_NOT_NORMALIZED is retired; the structural snapshot\n"
     "  records the normalized name, so its rows and every cache format are unchanged. A consumer whose default carries\n"
     "  a mixed-case descriptor name gets a new spell id once, because the bind fingerprint hashes default reprs.\n",
     "  construction.\n"),
    ("  recorded name as a category and file a `spell_crystal` shortfall. Cache generation 20 retires bundles captured\n"
     "  under the name matcher.\n",
     "  recorded name as a category and file a `spell_crystal` shortfall.\n"),
    ("  (values by reference; it never freezes or validates). The Aether record carried only the logger half of its\n"
     "  configuration until 0.2.8213; it now carries the regime too (next invariant).\n",
     "  (values by reference; it never freezes or validates).\n"),
    ("  acquisition clears it, and a released space refuses meld and purge. The flag's two writes per cycle are\n"
     "  paid back on the same path (inline managed exit and stack push, one idle-deque read, no SpellSpace sweep\n"
     "  call when none is open), so a scope cycle costs no more than before on 3.14t and the GIL build (measured\n"
     "  2026-09-27). A pooled lesser handle is not checked on `Conduit.meld`, the hottest door: using a scope\n"
     "  after cleanup stays a caller contract violation there.\n",
     "  acquisition clears it, and a released space refuses meld and purge. A pooled lesser handle is not checked on\n"
     "  `Conduit.meld`, the hottest door: using a scope after cleanup stays a caller contract violation there.\n"),
    ("  source text, never a ForwardRef owner or a memory address. Bind fingerprints hash that text, so a class\n"
     "  annotated with a `TYPE_CHECKING`-only type keeps one spell id across processes. The class binding\n"
     "  profile reads class-level annotations the same way, so a field typed with such a name counts in the\n"
     "  fingerprint (affected classes changed id once when this landed; until 0.2.8257 - the spell_id now\n"
     "  reads an annotate function's code, never an annotation's value). Every annotation in `src/melder`\n"
     "  evaluates once its `TYPE_CHECKING` imports are bound, enforced by a unit guard.\n",
     "  source text, never a ForwardRef owner or a memory address. The class binding profile reads class-level\n"
     "  annotations the same way. Every annotation in `src/melder` evaluates once its `TYPE_CHECKING` imports are\n"
     "  bound, enforced by a unit guard.\n"),
    ("  cannot form a wait cycle; the former store-held builds deadlocked against unique builders and purge.\n"
     "  Purge takes the same build lock before the store lock. Cache generation 10 rejects executors emitted\n"
     "  with the previous locking. Warm meld paths take no lock, unchanged.\n",
     "  cannot form a wait cycle. Purge takes the same build lock before the store lock. Warm meld paths take no lock.\n"),
    ("  True preserves the existing v4-binding fingerprint; False uses a separate hash domain (until 0.2.8257;\n"
     "  resolvable is a binding-manifest field since 0.2.8258 and no part of the spell_id). Application\n",
     "  Since 0.2.8258 resolvable is a binding-manifest field and no part of the spell_id. Application\n"),
    ("  never refuses these parameters. Cache generation 11 retires executors emitted before this wiring.\n",
     "  never refuses these parameters.\n"),
    ("  defaults retain existing DI inference. The compiled-cache semantic version advances to 8 so the\n"
     "  existing mismatch check automatically rejects plans using the former precedence.\n"
     "  EVIDENCE: `src/melder/aether/spellbook/spell_compiler/spell_requirements_finder/spell_requirements_finder.py:"
     "SpellRequirementsFinder._classify_parameter`.\n"
     "  EVIDENCE: `src/melder/utilities/caching_system/caching_system.py:CachingSystem.CACHE_VERSION_HISTORY`.\n",
     "  defaults retain existing DI inference.\n"
     "  EVIDENCE: `src/melder/aether/spellbook/spell_compiler/spell_requirements_finder/spell_requirements_finder.py:"
     "SpellRequirementsFinder._classify_parameter`.\n"),
    ("  its `cleanup()` returns at the `_cleaned` check before that reset (corrected\n"
     "  2026-10-01: this said teardown was identity-checked). The explicit reset\n",
     "  its `cleanup()` returns at the `_cleaned` check before that reset. The explicit reset\n"),
    ("    max_transaction_wait_time_in_seconds (recounted 2026-09-27; this said twelve,\n"
     "    with six disable flags) - and then calls\n",
     "    max_transaction_wait_time_in_seconds - and then calls\n"),
    ("  check - a leased space melds whether or not it is the top of its thread's stack (corrected 2026-09-27:\n"
     "  this line claimed an active-spellspace rule the source never had).\n",
     "  check - a leased space melds whether or not it is the top of its thread's stack.\n"),
]

VERDICT_MIDDLE = wrap(
    "A spell_id is the object's code, so a rebind of the same class after `cleanup_spell` mints the same spell_id for a "
    "new Spell; without the retirement the removed definition's `valid` verdict would be read as current. The "
    "retirement and its lock order are in src_components (Subcomponents: SpellSystemStates Registry, Conduit Resolution "
    "State). The surviving product of a removed definition is deliberately left alive in its scope: for `many` the "
    "replacement builds anew; for a slotted existence (`unique_per_conduit` and kin) it keeps its id-keyed slot, the "
    "replacement's first meld there returns it, and an override against it is refused as against any stored shared "
    "instance (owner ruling 2026-10-03).", first="  ", rest="  ")


def build_verdicts(entry):
    third = entry[2]
    cut = "starts with none."
    if cut not in third:
        raise OpError("verdict entry: third line changed")
    return entry[:2] + [third[:third.index(cut) + len(cut)]] + VERDICT_MIDDLE + evidence_tail(entry)


POINTER = wrap(
    "Component mechanics recorded here before 0.2.8228 live in their src_components entries, not here: the "
    "creation-cache envelope (generations 9, 12, 15 and 19 - release admission, complete bundles, the structural "
    "snapshot, the executor world stamp) in Component: Spellbook Core (Binding and Conjure); site-plan emission (the "
    "key-set plan runtime, door-held roots, lazy `instance_results`, owner-store constants, deterministic codegen "
    "signatures, compiler pool reads, Phase-5 publication, OVERRIDE_REQUIRED sockets, the selector watcher) in "
    "Component: SpellCompiler and Validation Pipeline; `many` registration, slot guards and purge in Component: "
    "Creations and SpellSpace and Component: Meld Resolution Runtime, which also carries the injected-dependency flag "
    "and pooled Meld hooks; hook baselines, pool return, bind-hook stages and graduation in Component: Conduit Runtime "
    "(Normal and Lesser) and Component: Spellbook Core (Binding and Conjure); custody keys, per-frame record replay, "
    "named-scope recording and the native-capability record in Component: Crystallizer Root, Persistence Record, And "
    "Module-World Surfaces; the named-record lifecycle and published capability links in Component: Nexus Descriptor "
    "And ACL Managers; the document-view key map in Component: Packaged Hardcopy Documents And Public Helper Exports.",
    first="- ", rest="  ")


def insert_pointer(text):
    ls = text.split("\n")
    s, e = section_range(ls, OI)
    k = e - 1 if ls[e - 1].strip() == "" else e
    return "\n".join(ls[:k] + POINTER + ls[k:])


FM_TRIMS = [
    ("  typing.Protocol.\" (0.2.8222, Breaking). Any other non-string, non-class object is refused the same way. Before,\n"
     "  the class was accepted and matched by name as a label, so a same-named single annotation resolved its members.\n",
     "  typing.Protocol.\" (0.2.8222, Breaking). Any other non-string, non-class object is refused the same way.\n"),
    ("  and the remedy (install it before the first frame, or keep the sealed value). Before 0.2.8209 the\n"
     "  configuration was installed and reported while the old regime stayed in force.\n",
     "  and the remedy (install it before the first frame, or keep the sealed value).\n"),
    ("  its mirror (0.2.8213). Before 0.2.8213 such worlds restored under process-wide ids with no report, and before\n"
     "  0.2.8214 one frame's copy of a class bound in two frames was lost at record time while the restore reported\n"
     "  complete.\n",
     "  its mirror (0.2.8213).\n"),
    ("  RuntimeError \"Cannot reconfigure Nexus while it is active. Deactivate it first.\" (0.2.8210). Before, a live\n"
     "  Nexus's policy was replaced, unfrozen, under existing Rifts.\n",
     "  RuntimeError \"Cannot reconfigure Nexus while it is active. Deactivate it first.\" (0.2.8210).\n"),
    ("  (0.2.79). Before 0.2.79 `Aether.get_conduit_by_name` answered over roots only, so a live named lesser raised\n"
     "  \"not found\" while its frame's Cloud returned it.\n",
     "  (0.2.79).\n"),
    ("  warnings are only counted, and Melder's own consistency codes are marked [internal] to report. Before, a\n"
     "  conduit-verdict refusal printed \"(none recorded)\" and every message carried 64-character spell ids. A\n"
     "  constructor that takes its own class is refused the same way (SELF_DEPENDENCY, naming the parameter); before,\n"
     "  conjure aborted with PhaseExecutionError \"DagNode cannot depend on itself\". A spell that only needs a cycle is\n"
     "  named as its consumer (\"cannot be built: it needs 'Y' ... 'X' itself is not part of that cycle\"), not as a\n"
     "  member.\n",
     "  warnings are only counted, and Melder's own consistency codes are marked [internal] to report. A constructor\n"
     "  that takes its own class is refused the same way (SELF_DEPENDENCY, naming the parameter). A spell that only\n"
     "  needs a cycle is named as its consumer (\"cannot be built: it needs 'Y' ... 'X' itself is not part of that\n"
     "  cycle\"), not as a member.\n"),
    ("  or destroyed inside its own block leaves the stack without error. Before 0.2.8203 a kept handle melded\n"
     "  into the idle shell and the next lease was served what it built, and a lesser cleaned inside its own\n"
     "  managed SpellSpace made that block's exit raise \"stack corruption\".\n",
     "  or destroyed inside its own block leaves the stack without error.\n"),
    ("  per failing disposal method, chained from what that method raised (0.2.80); before 0.2.80 an object's\n"
     "  first failure ended its disposal and the original exception was dropped, and before 0.2.8203 conduit\n"
     "  paths only logged these groups.\n",
     "  per failing disposal method, chained from what that method raised (0.2.80).\n"),
]

FM_REMOVALS = [
    "- A warm creation cache no longer replays an executor compiled in another world (fixed in 0.2.8220)",
    "- A definition melded, removed with `cleanup_spell` and bound again at the same address (same class, spellframe and",
    "- `with conduit:` no longer holds the conduit lock (Breaking, 0.2.8203)",
]

FM_REWRITES = [
    ("- A meld that races a link sever, an uncontract or an unbind of a spell its resolution pass is planning no",
     wrap("A meld that races a link sever, an uncontract or an unbind of a spell its resolution pass is planning "
          "raises SpellbookValidationError, as a meld starting a moment later does, and the next meld resolves "
          "against the current links and contracts (0.2.8227).", first="- ", rest="  ")),
    ("- A spell bound on a live dynamic root after conjure and first built as a consumer's dependency no longer fails its",
     wrap("A spell bound on a live dynamic root after conjure and first built as a consumer's dependency, whose own "
          "full target pass leaves it unresolved for the conduit (a visibility failure), makes its first direct meld "
          "raise SpellbookValidationError, and its flag stays set (0.2.8215).", first="- ", rest="  ")),
    ("- A dynamic conjure refused by the active-Crystallizer configuration discipline no longer settles its frame",
     ["- A dynamic conjure refused by the active-Crystallizer configuration discipline does not settle its frame",
      "  (0.2.8211)."]),
    ("- A SpellMap default naming its provider's binding name or string category in another case no longer raises",
     wrap("A non-string `binding_name` on a SpellMap or SpellContract raises TypeError (0.2.8226); a SpellMap default "
          "matches its provider's binding name and string category in any case.", first="- ", rest="  ")),
]

RECIPE_NEW = ["### Verifying the `path:line` citations in this document", ""] + wrap(
    "The index checks this document's structure, not the `path:line` citations in its `EVIDENCE:` blocks, and those "
    "rot silently when code moves: the file keeps existing, the citation keeps parsing, and it points at the wrong "
    "code. The citation check - every cited file exists and every range lies inside it - is kept once, in "
    "src_components' Indexing section, and covers this document too. In-bounds is necessary, not sufficient: open a "
    "citation you rely on, confirm the symbol is there, and cite a function by its `def` line.") + [""]

UNKNOWNS_NEW = [
    "  A path sweep and a symbol sweep are DIFFERENT CHECKS. A path resolves whenever",
    "  the file exists, which stays true through every rename INSIDE that file, so a",
    "  green path sweep says nothing about whether the symbols are real. Both were",
    "  re-verified as of 2026-08-02 - paths via the graph join, symbols against an",
    "  index of every `class` and `def` in `src/`. Do not widen a future stamp beyond",
    "  what was actually run.",
]

MR_NEW = wrap(
    "`Aether.mutation_research` as the access path to the hosted mutation root: its configuration lifecycle "
    "(`create_configuration()`, `create_configuration_builder()`, `configure(...)`, `activate(...)`), the ResearchSet "
    "registry (`research_set(...)`, `create_research_set(...)`, `list_research_set_names()`) and the agent verb surface "
    "of a ResearchSet (spells and compositions, lanes, joins, history, campaigns, network snapshots), the research "
    "record (world entries, promotions, residency, campaigns, diffs), the foresight and crystal-well reads over recorded "
    "source, candidate preview and synthesis, and the composition reads. The spellbook's bind, bind_inactive and notch "
    "confirmation points auto-record while the root is active. The user surface is the Rift rooms' `research_*` "
    "commands, advertised via `list_supported_command_methods`. Spellbook and Conduit expose the root through borrowed "
    "read-only `mutation_research` properties; frames carry no mutation dimension. The full verb inventory is in "
    "src_components (Subcomponent: MutationResearch Root (ResearchSet Registry)).", first="- ", rest="  ")

PROMOTED_NEW = wrap(
    "The four sections below are owner-ruled architecture decisions promoted from completed patch lanes between "
    "2026-07-07 and 2026-07-12. When they were promoted RecordVersion was \"1.0.0\"; it advanced to \"2.0.0\" for "
    "non-resolvable policy, \"3.0.0\" for named lesser topology and \"4.0.0\" for frame-scoped custody keys (0.2.8214), "
    "then by minor additions to \"4.1.0\" (0.2.8222), \"4.2.0\" (0.2.8242) and \"4.3.0\" (0.2.8258). The cache folder "
    "remains.")

DISPOSAL_OLD = (
    "policy source. Receiving-book order wins on replay. Until 0.2.8257 the order was part of the\n"
    "spell_id and the loader followed changed binding IDs without rewriting the original record or\n"
    "existing live IDs; since then the order is a binding-manifest field, so a receiving book's order\n"
    "keeps the spell_id, moves the binding hash and is reported in the restore's `binding_changes`\n"
    "(0.2.8258).\n")
DISPOSAL_NEW = (
    "policy source. Receiving-book order wins on replay. The order is a binding-manifest field, so a\n"
    "receiving book's order keeps the spell_id, moves the binding hash and is reported in the restore's\n"
    "`binding_changes` (0.2.8258).\n")

HANDOFF_ENTRY = wrap(
    "2026-10-24 src_architecture to its authoring spec (documentation only; EPIC-2026-10-24-src_architecture_to_spec, "
    "the owner's ask): component mechanics recorded here before 0.2.8228 - cache envelope generations, site-plan "
    "emission, store and slot locks, hook maps, recording keys - now live only in their src_components entries, named "
    "at the end of Operational Invariants, and that period's fixed-defect and correction history left Failure Modes and "
    "the other sections; the MutationResearch interface inventory moved verbatim to src_components (Subcomponent: "
    "MutationResearch Root (ResearchSet Registry)); C1 notes keep their descriptions, not per-version changes; the "
    "citation check is kept once, in src_components' Indexing; three paths into the documentation tooling are gone. "
    "This change log keeps the entries from 0.2.8228 on, the release-note boundary. Still unknown: see Unknowns. Where "
    "to start: What Melder Is (Read This First), the Architecture Summary, then src_components by component name.")

HANDOFF_OLDER = wrap(
    "OLDER HISTORY: the entries for 0.2.8227 and earlier (2026-07-25 to 2026-10-04), with the record of the 2026-08-01 "
    "and 2026-08-02 recompositions, were removed on 2026-10-24. They are in git history - commit 3bedd65bb holds this "
    "document as it stood before the trim - and the changes from 0.2.8202 to 0.2.8227 are in the release note "
    "`release_docs/0.2.8227.md`. The 2026-08-01 recomposition's migration file (patch lane "
    "system_doc_recompose_2026_08_01) was deleted in commit 0fddab923; what src_components did not absorb from it is in "
    "git history only.") + [""] + [
    "DECISIONS IN FORCE, carried from the 2026-07-25 summary; the section named carries each one:"] + \
    wrap("Melder is framed as a Dependency Graph Runtime; DI-style binding and resolution are a SUBSET capability, not "
         "the whole model (Architecture Summary; What Melder Is (Read This First) since 2026-10-15).",
         first="- ", rest="  ") + \
    wrap("Internal-bind refusal is one module-level function over a committed manifest, exact match, no MRO "
         "inheritance (Entrypoints and Runtime Guardrails).", first="- ", rest="  ") + \
    wrap("Conjure follows settle-then-inherit: the conduit inherits the world's mode rather than policing the "
         "caller's flag (Operational Invariants).", first="- ", rest="  ") + \
    wrap("Structural mutation is admitted through one moded scope-acquisition gate (src_components, Component: "
         "Transaction Admission Plane (Scope Acquisition)).", first="- ", rest="  ") + \
    wrap("The crystallizer is a passive sink; recording never changes runtime behaviour (Persistence & Restore "
         "Architecture).", first="- ", rest="  ")

COMP_HANDOFF_ENTRY = wrap(
    "2026-10-24 src_architecture to its authoring spec (documentation only; EPIC-2026-10-24-src_architecture_to_spec): "
    "Subcomponent: MutationResearch Root (ResearchSet Registry) carries, at the end of its Contract/Interface list, "
    "the MutationResearch boundary inventory moved verbatim from src_architecture's System Boundary and External "
    "Interfaces, which keeps a summary; the inventory overlaps the entry's own list until the epic's src_components "
    "pass folds the two. src_architecture no longer repeats the component mechanics it recorded before 0.2.8228 and "
    "names, at the end of its Operational Invariants, the entries here that carry them, so those entries are now the "
    "only record of them. No component contract changed. Verify next: that src_components pass.")


def handoff(text):
    ls = text.split("\n")
    s, e = section_range(ls, "## Context / Handoff Summary")
    if e != len(ls):
        raise OpError("handoff is not the last section")
    cuts = [i for i in range(s, e) if ls[i].startswith("2026-10-04 live unlink race (0.2.8227):")]
    if len(cuts) != 1 or ls[s + 1].strip() != "":
        raise OpError("handoff anchors")
    c = cuts[0]
    return "\n".join(ls[:s + 1] + [""] + HANDOFF_ENTRY + [""] + ls[s + 2:c] + HANDOFF_OLDER + [""])


def comp_handoff(text):
    ls = text.split("\n")
    s, _ = section_range(ls, "## Context / Handoff Summary")
    if ls[s + 1].strip() != "":
        raise OpError("components handoff anchor")
    return "\n".join(ls[:s + 2] + COMP_HANDOFF_ENTRY + [""] + ls[s + 2:])


def subsection(ls, section, h3):
    s, e = section_range(ls, section)
    hits = [i for i in range(s, e) if ls[i] == h3]
    if len(hits) != 1:
        raise OpError(f"subsection {h3!r} in {section!r}: {len(hits)} matches")
    a, b = hits[0], e
    while b > a and ls[b - 1].strip() == "":
        b -= 1
    return a, b, e


def run(arch_text, comp_text, today, src_root, stamp):
    arch, comp = Doc("src_architecture", arch_text), Doc("src_components", comp_text)
    captured = {}
    h3 = "### Verifying the `path:line` citations in this document"
    al, cl = arch.text.split("\n"), comp.text.split("\n")
    a1, b1, _ = subsection(al, "## Indexing", h3)
    a2, b2, _ = subsection(cl, "## Indexing", h3)
    if al[a1:b1] != cl[a2:b2]:
        raise OpError("the citation recipe differs between the two documents; not deduplicating")

    def recipe(text):
        ls = text.split("\n")
        a, _, e = subsection(ls, "## Indexing", h3)
        return "\n".join(ls[:a] + RECIPE_NEW + ls[e:])

    arch.apply("metadata Updated", regex_once(r"^- Updated: \d{4}-\d{2}-\d{2}$", f"- Updated: {today}"),
               allow_noop=True)
    arch.apply("indexing correction note", replace_once(
        "tooling, which does not ship with this document (corrected 2026-09-28: this\n"
        "section used to paste those commands and cite the tooling's own specification).\n",
        "tooling, which does not ship with this document.\n"))
    arch.apply("citation recipe kept once, in src_components", recipe)
    arch.apply("unknowns re-verification narrative", replace_block(
        "  The 2026-06-12 path/rename sweep that produced this list is COMPLETE. Its",
        "`## Indexing`. Do not widen a future stamp beyond what was actually run.", UNKNOWNS_NEW,
        within="## Unknowns"))
    arch.apply("glossary re-absorption note", replace_block(
        "RE-ABSORBED 2026-08-02. This section was moved to the patch lane during the",
        "The 17 contract sections remain present and in contract order around it.", [],
        within="## Glossary and Core Terms", eat_blank_before=True))
    arch.apply("boundary CORRECTED note", replace_block(
        "  CORRECTED 2026-08-02: this document previously said the Conduit \"delegates to",
        "opposite correctly. The code settles it, and since 0.2.8249 all three Conduit docstrings say so.", [],
        within="## System Boundary and External Interfaces"))

    def mr_build(entry):
        captured["mr"] = list(entry)
        return MR_NEW
    arch.apply("MutationResearch boundary bullet -> summary", rewrite_entry(
        "## System Boundary and External Interfaces",
        "- `Aether.mutation_research` as the access path to the hosted mutation root,", mr_build))
    arch.apply("cleanup sequence re-absorption note", replace_once(
        "to report. Re-absorbed 2026-08-02 from the patch lane and extended from three\n"
        "types to seven; each `cleanup()` was verified present on the class named.\n", "to report.\n"))
    arch.apply("runtime type names re-absorption note", replace_once(
        "Re-absorbed 2026-08-02 from the patch lane; every class below was verified to\n"
        "exist in `src/` and the enforcement citation was re-measured on the way in.\n\n", ""))
    arch.apply("runtime type names citation: patch-lane note out, range remeasured", link_type_check_citation(src_root))
    arch.apply("extension points re-absorption note", replace_once(
        "Re-absorbed 2026-08-02 from the patch lane; every named seam verified present.\n", ""))
    for prefix in INVARIANT_REMOVALS:
        arch.apply(f"invariant removed: {prefix[2:60]}", remove_entry(OI, prefix))
    arch.apply("invariant condensed: per-conduit verdicts", rewrite_entry(
        OI, "- Per-conduit verdicts retire with their definition (2026-10-03, 0.2.8219)", build_verdicts))
    for k, (old, new) in enumerate(INVARIANT_TRIMS, 1):
        arch.apply(f"invariant history trim {k}", replace_once(old, new))
    arch.apply("invariants: pointer to src_components", insert_pointer)
    for k, (old, new) in enumerate(FM_TRIMS, 1):
        arch.apply(f"failure-mode history trim {k}", replace_once(old, new))
    for prefix in FM_REMOVALS:
        arch.apply(f"failure mode removed: {prefix[2:60]}", remove_entry(FM, prefix))
    for prefix, head in FM_REWRITES:
        arch.apply(f"failure mode rewritten: {prefix[2:60]}",
                   rewrite_entry(FM, prefix, lambda entry, head=head: head + evidence_tail(entry)
                                 if any(x.startswith("  EVIDENCE") for x in entry) else head))
    arch.apply("promoted patch decisions intro", replace_block(
        "The four sections below were promoted out of COMPLETED patch lanes between",
        "custody keys (0.2.8214). The cache folder remains.", PROMOTED_NEW,
        within="## Promoted Patch Decisions (re-absorbed 2026-08-02)"))
    arch.apply("persistence topology artifact path", replace_once(
        "the V3 subsystem model (canonical anchor:\n"
        "artifacts/2026-07-09_crystallizer_philosophy_v3.md). Owner-run 614/614\n"
        "across the crystallizer test tree validates it.\n", "the V3 subsystem model.\n"))
    arch.apply("C1 intro moved to the top", c1_intro)
    arch.apply("C1 notes: descriptions only", trim_c1_notes)
    arch.apply("C1 ranges remeasured from disk", c1_remeasure(src_root, stamp), allow_noop=True)
    arch.apply("C1 carried-forward non-path note", regex_once(
        r"\n+Non-path notes carried forward from the previous revision:\n"
        r"- Registration refusal itself lives in `src/melder/aether/spellbook/bind/bind\.py`\n+", "\n\n"))
    arch.apply("ordered disposal diagram history", replace_once(DISPOSAL_OLD, DISPOSAL_NEW))
    arch.apply("handoff: new entry, recent log kept, older history out", handoff)

    def comp_insert(text):
        ls = text.split("\n")
        hits = [i for i, x in enumerate(ls) if x == "### Subcomponent: MutationResearch Root (ResearchSet Registry)"]
        if len(hits) != 1:
            raise OpError("MutationResearch Root subcomponent")
        h = hits[0]
        end = next(i for i in range(h + 1, len(ls)) if ls[i].startswith(("### ", "## ")))
        ds = [i for i in range(h, end) if ls[i] == "Data Structures:"]
        if len(ds) != 1:
            raise OpError("MutationResearch Root: Data Structures")
        label = wrap("Boundary inventory, moved verbatim from src_architecture (System Boundary and External "
                     "Interfaces) on 2026-10-24; src_architecture keeps a summary:", first="- ", rest="  ")
        return "\n".join(ls[:ds[0]] + label + captured["mr"] + ls[ds[0]:])
    comp.apply("metadata Updated", regex_once(r"^- Updated: \d{4}-\d{2}-\d{2}$", f"- Updated: {today}"),
               allow_noop=True)
    comp.apply("MutationResearch boundary inventory moved in", comp_insert)
    comp.apply("handoff: new entry", comp_handoff)
    return arch, comp


LEAK = re.compile(r"context_compass/|agent_onboarding/|tools/system_documents/|index_document\.py|system_docs|"
                  r"patches/active/|artifacts/20|design_engineer/")
ABSOLUTE = re.compile(r"([A-Za-z]:\\|^\s*-?\s*path:\s*[`']?/)")
CONTRACT = ["## Metadata", "## Scope and Intent", "## Indexing", "## DO NOT ASSUME / Unknowns Gate", "## Unknowns",
            "## System Context (C4)", "## System Boundary and External Interfaces", "## Architecture Summary (C4)",
            "## Entrypoints and Runtime Guardrails", "## Boot and Configuration Sequence",
            "## Data Flows and Sequences", "## Operational Invariants", "## Failure Modes and Error Paths",
            "## C1 Code Map (Core Only)", "## Diagrams", "## Information Sources", "## Context / Handoff Summary"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--arch", required=True)
    ap.add_argument("--comp", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--src", required=True)
    ap.add_argument("--history", nargs=2)
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()
    arch_p, comp_p, out = pathlib.Path(args.arch), pathlib.Path(args.comp), pathlib.Path(args.out)
    arch_t, comp_t = arch_p.read_text(encoding="utf-8"), comp_p.read_text(encoding="utf-8")
    started = datetime.datetime.now(datetime.timezone.utc)
    today, stamp = started.strftime("%Y-%m-%d"), started.strftime("%Y-%m-%dT%H:%M:%SZ")
    try:
        arch, comp = run(arch_t, comp_t, today, pathlib.Path(args.src), stamp)
    except OpError as exc:
        print(f"STOPPED, nothing written: {exc}")
        return 2
    heads = [x for x in arch.text.split("\n") if x.startswith("## ")]
    problems = []
    if [h for h in heads if h in CONTRACT] != CONTRACT:
        problems.append("contract sections missing or out of order")
    leaks = [f"{i}: {x[:100]}" for i, x in enumerate(arch.text.split("\n"), 1) if LEAK.search(x) or ABSOLUTE.search(x)]
    if leaks:
        problems.append("paths into the tooling or absolute paths: " + "; ".join(leaks))
    added = collections.Counter()
    for _, _, a in arch.log + comp.log:
        added += a
    wide = [x for x in added if len(x) > 118]
    out.mkdir(parents=True, exist_ok=True)
    (out / "src_architecture.result.md").write_text(arch.text, encoding="utf-8")
    (out / "src_components.result.md").write_text(comp.text, encoding="utf-8")
    report = []
    for doc in (arch, comp):
        for label, removed, add in doc.log:
            report.append(f"### {doc.name}: {label}  (-{sum(removed.values())} +{sum(add.values())} lines)")
            report += [f"- {x}" for x in sorted(removed.elements())] + [f"+ {x}" for x in sorted(add.elements())]
            report.append("")
    (out / "operations_report.md").write_text("\n".join(report), encoding="utf-8")
    before = multiset(arch_t) + multiset(comp_t)
    after = multiset(arch.text) + multiset(comp.text)
    gone, new = before - after, after - before
    (out / "preservation_removed.txt").write_text("\n".join(sorted(gone.elements())) + "\n", encoding="utf-8")
    (out / "preservation_added.txt").write_text("\n".join(sorted(new.elements())) + "\n", encoding="utf-8")
    if args.history:
        hist = multiset(pathlib.Path(args.history[0]).read_text(encoding="utf-8")) + \
            multiset(pathlib.Path(args.history[1]).read_text(encoding="utf-8"))
        unacc = gone - hist
        (out / "preservation_unaccounted.txt").write_text("\n".join(sorted(unacc.elements())) + "\n",
                                                          encoding="utf-8")
        print(f"removed lines found in the history revision: {sum((gone & hist).values())}; "
              f"not found there: {sum(unacc.values())} (preservation_unaccounted.txt)")
    n_a0, n_a1 = len(arch_t.split("\n")) - 1, len(arch.text.split("\n")) - 1
    n_c0, n_c1 = len(comp_t.split("\n")) - 1, len(comp.text.split("\n")) - 1
    print(f"src_architecture {n_a0} -> {n_a1} ({n_a1 - n_a0:+d}); src_components {n_c0} -> {n_c1} ({n_c1 - n_c0:+d})")
    print(f"operations: {len(arch.log)} + {len(comp.log)}; removed lines {sum(gone.values())}, "
          f"added lines {sum(new.values())} (both documents, non-blank, normalized)")
    print("added lines over 118 chars (normalized):", len(wide), *[w[:80] for w in wide][:5], sep="\n  ")
    if problems:
        print("PROBLEMS:", *problems, sep="\n  ")
        return 3
    if args.apply:
        arch_p.write_text(arch.text, encoding="utf-8")
        comp_p.write_text(comp.text, encoding="utf-8")
        print("APPLIED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
