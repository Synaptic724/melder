"""S4 landing: system-document edits for the minted index's frame registration.

STORY-2026-10-17-minted_index_missing_from_frame_registry, from notes/s4_docs_draft.md and the three patch docs.
src_architecture, src_components, tests_components and tests_architecture. Anchors are section headers or short
phrases that melder_0's S1/S2 documentation does not reach, so it can land first; each old text must occur exactly
once. Code-map records are found by path and remeasured from disk; the test counts S4 moves (integration tier,
spellbook integration tree, the three tiers' total, the core key-file union) are recounted from disk. New lines stay
within 120 characters unless a long backticked token makes them unbreakable; LF only.
Usage (repository root): land_s4_docs.py --notch 0.2.82NN --check | --apply
"""
import datetime
import pathlib
import re
import sys
import textwrap

DOCS = pathlib.Path("context_compass/system_docs")
STAMP = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
TODAY = STAMP[:10]
STORY = "STORY-2026-10-17-minted_index_missing_from_frame_registry"
TEST_FILE = "test_separated_version_is_known_to_its_frame_integration.py"
TEST_PATH = "tests/integration/melder/spellbook/" + TEST_FILE
S9_TEST_PATH = ("tests/integration/melder/spellbook/"
                "test_direct_cleanup_refuses_active_member_with_parked_versions_integration.py")
UNIT_PATH = "tests/unit/melder/mutation_research/test_mutation_research_root.py"
SPELLBOOK = "src/melder/aether/spellbook/spellbook.py"
SPELL = "src/melder/aether/spellbook/spell.py"
RESEARCH = "src/melder/mutation_research/mutation_research.py"
OWNER_WORD = ("\"it should properly follow the general spell index creation and registry binding processes the same "
              "way it does during bind\"")


class LandingError(Exception):
    """A document does not hold the text or record this landing expects."""


ARCH_INVARIANT = (
    "- A version moved into an index of its own is known to its frame ({D}, {N}; the owner's word, chat\n"
    "  2026-10-18: \"it should properly follow the general spell index creation and registry binding processes the\n"
    "  same way it does during bind\"): `Spellbook._apply_remove_from_index` mints the fresh index as Bind creates one\n"
    "  (`SpellIndex(initial_id=spell_id)`) and, right after its Book-locked move, registers it in the frame's spell\n"
    "  registry the way a post-conjure `bind` registers the index it creates - bind's guard (the Book is conjured)\n"
    "  and call (`Aether._register_single_spell_index` under the Book's root conduit). Every walk of that registry\n"
    "  then finds the version, parked there or notched active: `find_index_for_spell` and\n"
    "  `find_conduit_id_for_spell`, and through them the Conduit's spell_id lookups, a grant and an ownership\n"
    "  transfer by spell_id, bind's collision guard (`Aether._check_for_spell`, in the frame and across frames under\n"
    "  process-wide spell ids) and MutationResearch residency. The index leaves the registry when it empties\n"
    "  (`_destroy_spell_index`, as an index bind created does) or with its root:\n"
    "  `_unregister_conduit_spells_from_aether`, which only the root's teardown calls, unregisters the index of every\n"
    "  parked version beside the active versions' indexes, so the frame keeps no entry for a torn-down root.\n"
    "  Residency calls a version active only when its index selects it and the frame's lineage registry tracks it as\n"
    "  that index's current version (`SpellSystemStates.get_by_index_id(...).current_spell_id`): the minted index\n"
    "  selects its parked member (activation takes a notch; the owner's ruling, 2026-10-17) and no lineage tracks\n"
    "  that member until a notch registers it, so it reads parked; members of every other index read as before. No\n"
    "  new index state, and nothing persisted, cached or emitted changes. Locks: the registration takes the frame\n"
    "  lock alone after the Book lock is released (bind's order); the teardown reads each parked version's index\n"
    "  under the Book lock through the spell's own lock (Book -> spell, Book teardown's order) and unregisters with\n"
    "  the frame lock alone; residency takes the lineage registry's lock, then the state's, each alone. Until {N}\n"
    "  the minted index was never registered, so the version was unknown to its frame by spell_id - the Conduit\n"
    "  lookups raised \"not found in any conduit\", a grant and a transfer by spell_id were refused, and another Book\n"
    "  could bind its spell_id - and residency read it `declared_only`.\n"
    "  EVIDENCE: `src/melder/aether/spellbook/spellbook.py:Spellbook._apply_remove_from_index`,\n"
    "  `Spellbook._unregister_conduit_spells_from_aether`, `Spellbook._destroy_spell_index`,\n"
    "  `src/melder/aether/aether.py:Aether._register_single_spell_index`, `Aether._check_for_spell`,\n"
    "  `src/melder/aether/aetheric_frame/aetheric_frame.py:AethericFrame.find_index_for_spell`,\n"
    "  `AethericFrame.unregister_conduit_spells`, `src/melder/aether/conduit/conduit.py:Conduit._cleanup_normal_conduit`,\n"
    "  `src/melder/mutation_research/mutation_research.py:MutationResearch._locate_live_membership` and\n"
    "  `src/melder/aether/spellbook/spell.py:Spell._spell_index_unless_cleaned`.\n"
)

ARCH_FAILURE = (
    "- Fixed in {N}: a version moved into an index of its own with `remove_from_spell_index` is found by its\n"
    "  spell_id. The frame never listed that index, so `Conduit.get_spell_by_spell_id` and `get_conduit_by_spell_id`\n"
    "  raised ValueError \"Spell version <id> not found in any conduit.\" for a version the conduit's own Book owns,\n"
    "  parked there or notched active; a grant (`add_spell_to_contract(spell_id=...)`) and an ownership transfer by\n"
    "  spell_id raised the same; another Book bound its spell_id - of the frame, or of another frame under\n"
    "  process-wide spell ids - so two Books held one spell_id, and a Book not yet conjured then had its conjure\n"
    "  refused; and `residency_view` read it `declared_only`. A second bind now raises the existing RuntimeError\n"
    "  \"Spell ID collision detected: this object is already registered as spell_id <id>. ...\".\n"
    "  EVIDENCE: `src/melder/aether/spellbook/spellbook.py:Spellbook._apply_remove_from_index` and\n"
    "  `src/melder/aether/aether.py:Aether._check_for_spell`.\n"
)

HANDOFF_HEAD = "## Context / Handoff Summary\n\n"
ARCH_HANDOFF = (
    "{D} the minted index is registered ({N}; " + STORY + ", on the owner's word " + OWNER_WORD + "): the "
    "index `remove_from_spell_index` mints is registered with the frame as a post-conjure `bind` registers the "
    "index it creates, the root's teardown unregisters it with the rest, and residency reads its version parked "
    "until a notch. A new operational invariant, a fixed failure mode, the index mutation sequence and the code "
    "map carry it; the 0.2.8256 invariant's and the 0.2.8253 failure mode's filed gap is marked fixed; the "
    "component map carries the per-component contracts. No new index state (the owner withdrew it)."
)

SRC_ARCHITECTURE = [
    ("## Operational Invariants\n", "## Operational Invariants\n" + ARCH_INVARIANT),
    ("## Failure Modes and Error Paths\n", "## Failure Modes and Error Paths\n" + ARCH_FAILURE),
    (
        "  and a minted index is missing from the frame registry\n"
        "  (STORY-2026-10-17-minted_index_missing_from_frame_registry). The check is",
        "  and a minted index was missing from the frame registry (fixed in {N};\n"
        "  STORY-2026-10-17-minted_index_missing_from_frame_registry). The check is",
    ),
    (
        "the Conduit lookup still raises \"not\n"
        "  found in any conduit\" for such a version, because the index the move mints is missing from the frame registry\n"
        "  (pre-existing; STORY-2026-10-17-minted_index_missing_from_frame_registry). `Conduit.get_spell_permissions`\n",
        "the Conduit lookup still raised \"not\n"
        "  found in any conduit\" for such a version until {N}, because the index the move mints was missing from the\n"
        "  frame registry (STORY-2026-10-17-minted_index_missing_from_frame_registry). `Conduit.get_spell_permissions`\n",
    ),
    (
        "     index, remove mints a fresh inactive index instead of destroying anything;\n",
        "     index, remove mints a fresh inactive index instead of destroying anything\n"
        "     and registers it with the frame as `bind` registers the index it creates ({N});\n",
    ),
    (
        "    composition emission; the old conduit/frame facades are GONE, 2026-07-11).\n",
        "    composition emission; the old conduit/frame facades are GONE, 2026-07-11); residency calls a version\n"
        "    active only while the frame's lineage registry tracks it as its index's current version ({N}).\n",
    ),
]

ARCH_NOTES = {
    SPELLBOOK: ("`_apply_remove_from_index` registers the index it mints with the frame as `bind` registers its new "
                "one, and the root's teardown unregisters the indexes that hold only parked versions ({N})"),
    SPELL: "`_spell_index_unless_cleaned` lists the root's teardown among its readers ({N})",
    RESEARCH: None,
}

COMP_HANDOFF = (
    "{D} the minted index is registered ({N}; " + STORY + ", on the owner's word): the SpellIndex Mutation "
    "Surface and the index-move flow say `remove_from_spell_index` registers the index it mints in the frame's "
    "spell registry as a post-conjure `bind` registers the index it creates, and that the index leaves with its "
    "root; AethericFrame Services names every writer and reader of the registry; the ResearchSet package's "
    "residency bullet calls a version active only while its lineage tracks it; the code map remeasures "
    "spellbook.py, spell.py and mutation_research.py, and the numeric citations into them were remapped line by "
    "line."
)

SRC_COMPONENTS = [
    (
        "  remove never destroys - it mints a fresh inactive index for the separated\n"
        "  spell and leaves the source with its remaining members.\n",
        "  remove never destroys - it mints a fresh inactive index for the separated\n"
        "  spell and leaves the source with its remaining members. Remove then registers\n"
        "  the fresh index in the frame's spell registry the way a post-conjure `bind`\n"
        "  registers the index it creates - bind's guard (the Book is conjured) and call\n"
        "  (`Aether._register_single_spell_index` under the Book's root conduit; {N}) -\n"
        "  so the lookups by spell_id, a grant or transfer by spell_id and bind's\n"
        "  collision guard find the separated version, parked or notched active there;\n"
        "  the index leaves the registry when it empties (`_destroy_spell_index`) or with\n"
        "  its root (`_unregister_conduit_spells_from_aether`, the root's teardown).\n",
    ),
    (
        "   outside the source index, or its only member). Any raise -> `end_transaction(success=False)` and the raise\n"
        "   propagates.\n",
        "   outside the source index, or its only member). After its Book-locked move, remove registers the index it\n"
        "   minted with the frame (`Aether._register_single_spell_index`, the Book's root conduit, the frame lock\n"
        "   alone; {N}). Any raise -> `end_transaction(success=False)` and the raise propagates.\n",
    ),
    (
        "- Maintain selected-spell registry.\n",
        "- Maintain selected-spell registry.\n"
        "- List every index a conjured Book owns in the spell registry under the Book's root conduit ({N}): conjure\n"
        "  registers the indexes with an active version, a post-conjure `bind` the index it creates and\n"
        "  `remove_from_spell_index` the index it mints; `_destroy_spell_index` unregisters an emptied index and the\n"
        "  root's teardown every index the root registered, the parked-only ones included. `find_index_for_spell`,\n"
        "  `find_conduit_id_for_spell` and the cleanup-safe probes walk it.\n",
    ),
    (
        "  runtime truth (frame scan via `find_index_for_spell`; selected member ->\n"
        "  `active`, unselected member -> `parked`), custody probe (`stored`;\n",
        "  runtime truth (frame scan via `find_index_for_spell`; a member its index\n"
        "  selects and its lineage tracks as current -> `active`, any other member ->\n"
        "  `parked` - a version moved into an index of its own reads parked until a\n"
        "  notch, {N}), custody probe (`stored`;\n",
    ),
]

TESTS_CLUSTER_ENTRY = (
    "- a version moved into an index of its own is known to its frame ({N};\n"
    "  `" + TEST_FILE + "`, 12 tests): in a dynamic world with English\n"
    "  active and French parked on English's index under its own binding name, after\n"
    "  `remove_from_spell_index(French)` the frame finds French's index under the lender and both Conduit lookups\n"
    "  answer, parked and notched active; a linked borrower's grant by spell_id gives a parked or an active copy as\n"
    "  French is; a transfer by spell_id moves French to the target root; a second bind of French's spell_id is\n"
    "  refused by another Book of the frame and of another frame, conjured or not; the lender's teardown takes\n"
    "  French's index out of the frame and a new Book may bind French; moving French back leaves no registered\n"
    "  index behind; and residency reads French parked in its own index, then active after a notch\n"
)

TESTS_RECORD = (
    "- path: `" + TEST_PATH + "`\n"
    "  start_line: 1\n  end_line: {LOC}\n  loc: {LOC}\n  verified_at: " + STAMP + "\n"
    "  note: a version moved into an index of its own is found by spell_id, granted, transferred and guarded\n"
    "    against a second bind; the root's teardown takes its index; residency reads it parked ({N}).\n"
)

TESTS_HANDOFF = (
    "{D} the minted index is registered ({N}; " + STORY + "): the Spellbook Integration Cluster gains `"
    + TEST_FILE + "` (12 tests: the version found, granted and transferred by spell_id, parked and notched "
    "active; a second bind refused in the frame and across frames; the root's teardown; the move back; "
    "residency), a key file with a code-map record; the residency unit file's record is remeasured (a selected "
    "version no lineage tracks reads parked). Counts are recounted from disk ({COUNTS}); the core key-file union "
    "is recounted from the catalogs ({UNION} paths; it read one short since 0.2.8256's key file)."
)

TESTS_COMPONENTS = [
    (
        "Key Files (C1):\n- `tests/integration/melder/spellbook/test_spellbook_integration_core.py`\n",
        TESTS_CLUSTER_ENTRY
        + "Key Files (C1):\n- `tests/integration/melder/spellbook/test_spellbook_integration_core.py`\n",
    ),
    (
        "- `" + S9_TEST_PATH + "` (2026-10-18)\n",
        "- `" + S9_TEST_PATH + "` (2026-10-18)\n"
        "- `" + TEST_PATH + "` ({D})\n",
    ),
    (
        "- `" + S9_TEST_PATH + "`\n- direct filesystem inventory of `tests/`\n",
        "- `" + S9_TEST_PATH + "`\n- `" + TEST_PATH + "`\n- direct filesystem inventory of `tests/`\n",
    ),
]

TESTS_ARCH_HANDOFF = (
    "{D} the minted index is registered ({N}): the inventory is recounted from disk ({COUNTS}) - the lane adds "
    "one integration module (a version moved into an index of its own, known to its frame), catalogued in "
    "`tests_components`, and changes one unit module (the residency join's frame doubles). No tier, conftest, "
    "declared marker or shared support module changes, and no extent in this map moves."
)


def fill(text: str, notch: str) -> str:
    """Put the notch and the landing day into a text."""
    return text.replace("{N}", notch).replace("{D}", TODAY)


def paragraph(text: str) -> str:
    """One handoff paragraph wrapped at 116 columns, followed by the blank line that separates paragraphs."""
    lines = textwrap.wrap(text, width=116, break_on_hyphens=False, break_long_words=False)
    return "\n".join(lines) + "\n\n"


def add_handoff(text: str, body: str, label: str) -> str:
    """Put a handoff paragraph first under the Context / Handoff Summary heading."""
    return replace_once(text, HANDOFF_HEAD, HANDOFF_HEAD + paragraph(body), label)


def measure(path: str) -> int:
    """Line count of a repository file as the code maps record it (`splitlines`, no phantom last line)."""
    return len(pathlib.Path(path).read_bytes().splitlines())


def count_tree(rel: str) -> tuple:
    """(`.py` files, `test_*.py` files) under a test tree, pycache excluded."""
    files = [p for p in pathlib.Path(rel).rglob("*.py") if "__pycache__" not in p.parts]
    return len(files), len([p for p in files if p.name.startswith("test_")])


def record_bounds(text: str, path: str) -> tuple:
    """Offsets of the code-map record for `path`: its head line and every indented line after it."""
    head = "- path: `" + path + "`\n"
    if text.count(head) != 1:
        raise LandingError("record for %s found %d times" % (path, text.count(head)))
    start = text.index(head)
    end = start + len(head)
    while end < len(text) and text[end] == " ":
        end = text.index("\n", end) + 1
    return start, end


def append_to_note(block: str, addition: str) -> str:
    """Append '; <addition>.' to a record's note, rewrapping only its last line (the note must end with '.')."""
    lines = block.rstrip("\n").split("\n")
    if sum(1 for line in lines if line.startswith("  note: ")) != 1 or not lines[-1].endswith("."):
        raise LandingError("unexpected note shape: %r" % lines[-1][:80])
    prefix = "  note: " if lines[-1].startswith("  note: ") else "    "
    content = lines[-1][len(prefix):-1] + "; " + addition + "."
    lines[-1:] = textwrap.wrap(content, width=116, initial_indent=prefix, subsequent_indent="    ",
                               break_on_hyphens=False, break_long_words=False)
    return "\n".join(lines) + "\n"


def remeasure(text: str, path: str, addition, notch: str) -> str:
    """Set a record's extent and stamp from disk; append to its note when an addition is given."""
    start, end = record_bounds(text, path)
    loc = measure(path)
    block, hits = re.subn(r"\n  end_line: \d+\n  loc: \d+\n  verified_at: \S+\n",
                          "\n  end_line: %d\n  loc: %d\n  verified_at: %s\n" % (loc, loc, STAMP), text[start:end])
    if hits != 1:
        raise LandingError("extent fields of %s not found once" % path)
    if addition:
        block = append_to_note(block, addition.replace("{N}", notch))
    return text[:start] + block + text[end:]


def key_file_union(text: str) -> int:
    """Distinct backticked paths in every `Key Files (C1)` list before the core section."""
    paths = set()
    inside = False
    for line in text[:text.index("Core is the DEDUPLICATED UNION")].split("\n"):
        if line.startswith("Key Files (C1):"):
            inside = True
            continue
        if inside:
            match = re.match(r"^- `([^`]+)`", line)
            if match:
                paths.add(match.group(1))
            elif not (line.startswith("- ") or line.startswith("  ")):
                inside = False
    return len(paths)


def replace_once(text: str, old: str, new: str, label: str) -> str:
    """Replace `old` with `new`, refusing unless `old` occurs exactly once."""
    count = text.count(old)
    if count != 1:
        raise LandingError("%s: old text found %d times: %r" % (label, count, old[:90]))
    return text.replace(old, new, 1)


def sub_once(text: str, pattern: str, repl, label: str) -> str:
    """Regex-substitute exactly once (multiline), refusing on zero or several matches."""
    result, hits = re.subn(pattern, repl, text, flags=re.M)
    if hits != 1:
        raise LandingError("%s: pattern matched %d times" % (label, hits))
    return result


def too_long(line: str) -> bool:
    """A line over 120 characters is allowed only when a backticked token of 60 or more makes it unbreakable."""
    if len(line) <= 120:
        return False
    return not any(len(token) >= 60 for token in re.findall(r"`([^`]+)`", line))


def next_notch(version: str) -> str:
    """The notch after `version` in the owner's decimal reading (0.2.8256 -> 0.2.8257)."""
    head, third = version.rsplit(".", 1)
    return "%s.%d" % (head, int(third) + 1)


def check_notch(notch: str) -> None:
    """The notch must read 0.2.82NN and be __version__ or the number right after it."""
    if not re.fullmatch(r"0\.2\.82\d\d", notch):
        raise LandingError("--notch must read 0.2.82NN, got %r" % notch)
    text = pathlib.Path("src/melder/__version__.py").read_text(encoding="utf-8")
    current = re.search(r'^__version__ = "([^"]+)"$', text, re.M).group(1)
    if notch not in (current, next_notch(current)):
        raise LandingError("--notch %s is neither __version__ (%s) nor the next number" % (notch, current))
    print("__version__", current, "notch", notch)


def edit_src_architecture(text: str, notch: str) -> str:
    for index, (old, new) in enumerate(SRC_ARCHITECTURE, 1):
        text = replace_once(text, old, fill(new, notch), "src_architecture #%d" % index)
    for path, addition in ARCH_NOTES.items():
        text = remeasure(text, path, addition, notch)
    if "- `" + RESEARCH + "`\n" not in text:
        text = replace_once(text, "## Information Sources\n",
                            "## Information Sources\n- `" + RESEARCH + "`\n", "src_architecture sources")
    return add_handoff(text, fill(ARCH_HANDOFF, notch), "src_architecture handoff")


def edit_src_components(text: str, notch: str) -> str:
    for index, (old, new) in enumerate(SRC_COMPONENTS, 1):
        text = replace_once(text, old, fill(new, notch), "src_components #%d" % index)
    for path in (SPELLBOOK, SPELL, RESEARCH):
        text = remeasure(text, path, None, notch)
    return add_handoff(text, fill(COMP_HANDOFF, notch), "src_components handoff")


def counts() -> dict:
    """The disk counts S4's documents state."""
    found = {name: count_tree("tests/" + name) for name in ("unit", "component", "integration")}
    found["spellbook"] = count_tree("tests/integration/melder/spellbook")
    found["total"] = sum(found[name][1] for name in ("unit", "component", "integration"))
    return found


def edit_tests_components(text: str, notch: str, found: dict) -> str:
    for index, (old, new) in enumerate(TESTS_COMPONENTS, 1):
        text = replace_once(text, old, fill(new, notch), "tests_components #%d" % index)
    start, end = record_bounds(text, S9_TEST_PATH)
    loc = measure(TEST_PATH)
    text = text[:end] + TESTS_RECORD.replace("{LOC}", str(loc)).replace("{N}", notch) + text[end:]
    text = remeasure(text, UNIT_PATH, None, notch)
    start, end = record_bounds(text, UNIT_PATH)
    note = ("  note: the root's residency join; a selected version that no lineage tracks reads parked ("
            + notch + ").\n")
    text = text[:end] + note + text[end:] if "  note: " not in text[start:end] else text
    integration_py, integration_test = found["integration"]
    text = sub_once(text, r"^- \d+ `test_\*\.py` modules among \d+ `\.py` files \(recounted \d{4}-\d\d-\d\d\); the "
                          r"others are benches and the$",
                    "- %d `test_*.py` modules among %d `.py` files (recounted %s); the others are benches and the"
                    % (integration_test, integration_py, TODAY), "integration count")
    text = sub_once(text, r"the \d+ test_\*\.py modules in\n  tests/integration/melder/spellbook/",
                    "the %d test_*.py modules in\n  tests/integration/melder/spellbook/" % found["spellbook"][1],
                    "spellbook tree count")
    text = sub_once(text, r"The \d+ test modules of the\nthree CI tiers",
                    "The %d test modules of the\nthree CI tiers" % found["total"], "three-tier total")
    union = key_file_union(text)
    records = len(re.findall(r"^- path: `", text, re.M))
    if union != records:
        raise LandingError("key-file union %d differs from the code-map records %d" % (union, records))
    text = sub_once(text, r"above - \d+ paths \(recounted \d{4}-\d\d-\d\d\)",
                    "above - %d paths (recounted %s)" % (union, TODAY), "key-file union")
    summary = ("unit %d of %d `.py`, component %d of %d, integration %d of %d, spellbook tree %d; %d test modules in "
               "the three tiers" % (found["unit"][1], found["unit"][0], found["component"][1],
                                     found["component"][0], integration_test, integration_py,
                                     found["spellbook"][1], found["total"]))
    handoff = fill(TESTS_HANDOFF, notch).replace("{UNION}", str(union)).replace("{COUNTS}", summary)
    return add_handoff(text, handoff, "tests_components handoff")


def edit_tests_architecture(text: str, notch: str, found: dict) -> str:
    integration_py, integration_test = found["integration"]
    text = sub_once(text, r"^- `integration/`: \d+ `\.py` files, \d+ of them `test_\*\.py`",
                    "- `integration/`: %d `.py` files, %d of them `test_*.py`" % (integration_py, integration_test),
                    "integration inventory")
    text = sub_once(text, r"the three tiers' \d+ `test_\*\.py`", "the three tiers' %d `test_*.py`" % found["total"],
                    "three-tier total")
    summary = ("unit %d `.py`, component %d, integration %d; %d test modules in the three tiers"
               % (found["unit"][0], found["component"][0], integration_py, found["total"]))
    return add_handoff(text, fill(TESTS_ARCH_HANDOFF, notch).replace("{COUNTS}", summary),
                       "tests_architecture handoff")


PLAN = [
    ("src_architecture.md", edit_src_architecture),
    ("src_components.md", edit_src_components),
    ("tests_components.md", edit_tests_components),
    ("tests_architecture.md", edit_tests_architecture),
]


def main() -> None:
    args = sys.argv[1:]
    if len(args) != 3 or args[0] != "--notch" or args[2] not in ("--check", "--apply"):
        raise SystemExit(__doc__)
    notch = args[1]
    problems = []
    results = {}
    try:
        check_notch(notch)
        found = counts()
        print("disk counts:", found)
        for name, edit in PLAN:
            raw = (DOCS / name).read_bytes()
            if b"\r\n" in raw:
                raise LandingError("CRLF in " + name)
            before = raw.decode("utf-8")
            after = edit(before, notch, found) if "tests_" in name else edit(before, notch)
            for line in after.split("\n"):
                if too_long(line) and line not in before.split("\n"):
                    problems.append("%s: new line of %d chars: %s" % (name, len(line), line))
            results[name] = after
            print("%s: %d -> %d lines" % (name, before.count("\n"), after.count("\n")))
    except LandingError as error:
        problems.append(str(error))
    if problems:
        for problem in problems:
            print("PROBLEM", problem)
        raise SystemExit(1)
    if args[2] == "--apply":
        for name, text in results.items():
            path = DOCS / name
            path.write_bytes(text.encode("utf-8"))
            if path.read_bytes().decode("utf-8") != text:
                raise SystemExit("read-back mismatch: " + name)
        print("applied at", STAMP)


main()
