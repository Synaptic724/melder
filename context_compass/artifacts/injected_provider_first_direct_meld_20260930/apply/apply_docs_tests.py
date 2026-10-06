"""
Promote the injected_provider_first_direct_meld test surface (0.2.8215) into tests_components.md and remeasure the
tier counts the catalog states.

Usage: python apply_docs_tests.py <repository root>
Every anchor must match exactly once; nothing is written unless all do. The C1 core set must equal the union of the
catalogs' Key Files lists afterwards, or nothing is written.
"""
import datetime
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from apply_support import ApplySession

ROOT = sys.argv[1]
DOC = "context_compass/system_docs/tests_components.md"
NOW = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
s = ApplySession(ROOT)

UNIT_NEW = "tests/unit/melder/spellbook/test_spellbook_creation_system_dependency_flags.py"
COMPONENT_NEW = "tests/component/melder/aether/conduit/test_conduit_component_injected_provider_direct_meld.py"


def count_tests(relative: str, pattern: str = "test_*.py") -> int:
    """Count the files matching `pattern` under one tests directory, skipping bytecode caches."""
    return sum(1 for p in (pathlib.Path(ROOT) / relative).rglob(pattern) if "__pycache__" not in p.parts)


# Spellbook runtime and binding unit cluster: the target pass's flags, and where the lane that reads them is pinned.
s.insert_after(
    DOC,
    "  freeze and disposal priority; conjure cache-path classification and emission\n",
    "- the target pass's dependency flags (0.2.8215): an owned, resolvable dependency with no plan and no published\n"
    "  context is flagged `resolution_required` once (door epoch bumped, written under its own spell lock, ids\n"
    "  sorted), and only when the pass succeeds; own plans, published contexts, existing creations, non-resolvable\n"
    "  or borrowed spells, the target and already-flagged spells are left alone. The deferred lane that reads the\n"
    "  flag is pinned in the aether tree's `test_meld.py`: a spell that is neither an existing creation nor its\n"
    "  Phase 5 root runs the full target pass and must read resolution-valid; a failed pass re-flags and re-raises\n",
)
s.insert_after(
    DOC,
    "- `tests/unit/melder/spellbook/bind/test_stable_spell_fingerprint.py` (address-free fingerprints, 2026-09-26)\n",
    f"- `{UNIT_NEW}` (target-pass flags, 2026-09-30)\n",
)

# Aether component cluster: the first direct meld of an injected dependency.
s.insert_after(
    DOC,
    "  defaults when no configuration was installed), and the cleaned refusal\n",
    "- injected dependencies (0.2.8215): a provider bound after conjure and first built as a consumer's dependency\n"
    "  melds directly afterwards - the instance its scope holds for unique_per_conduit and unique, a new one for\n"
    "  many - in named and unnamed lessers, on the root, in sibling lessers (isolated), on a root holding a spell\n"
    "  at conjure, with system caching cold and warm, and through the SpellSpace door; provider-first and\n"
    "  bind-before-conjure controls\n",
)
s.insert_after(
    DOC,
    "- `tests/component/melder/aether/test_aether_spell_id_regime_property_component.py` (regime in force, 2026-09-30)\n",
    f"- `{COMPONENT_NEW}` (2026-09-30)\n",
)

# Tier counts, remeasured (several had drifted with earlier lanes' files).
unit_tests, unit_py = count_tests("tests/unit"), count_tests("tests/unit", "*.py")
component_tests, component_py = count_tests("tests/component"), count_tests("tests/component", "*.py")
integration_tests, integration_py = count_tests("tests/integration"), count_tests("tests/integration", "*.py")
rift = count_tests("tests/integration/melder/aether/rift")
COUNTS = [
    ("- the densest tier: 462 `test_*.py` modules among 465 `.py` files\n",
     f"- the densest tier: {unit_tests} `test_*.py` modules among {unit_py} `.py` files\n"),
    ("- The aether tree carries 183 `test_*.py` modules beneath these; they are the\n",
     f"- The aether tree carries {count_tests('tests/unit/melder/aether')} `test_*.py` modules beneath these; they"
     " are the\n"),
    ("the 45 test_*.py modules in\n  tests/unit/melder/crystallizer/",
     f"the {count_tests('tests/unit/melder/crystallizer')} test_*.py modules in\n  tests/unit/melder/crystallizer/"),
    ("- The spellbook tree carries 141 `test_*.py` modules beneath these; they are the\n",
     f"- The spellbook tree carries {count_tests('tests/unit/melder/spellbook')} `test_*.py` modules beneath these;"
     " they are the\n"),
    ("the 51 test_*.py modules in\n  tests/unit/melder/utilities/",
     f"the {count_tests('tests/unit/melder/utilities')} test_*.py modules in\n  tests/unit/melder/utilities/"),
    ("- 141 `test_*.py` modules among 143 `.py` files\n",
     f"- {component_tests} `test_*.py` modules among {component_py} `.py` files\n"),
    ("the 58 test_*.py modules in\n  tests/component/melder/aether/",
     f"the {count_tests('tests/component/melder/aether')} test_*.py modules in\n  tests/component/melder/aether/"),
    ("- The spellbook tree carries 71 `test_*.py` modules beneath these; they are the\n",
     f"- The spellbook tree carries {count_tests('tests/component/melder/spellbook')} `test_*.py` modules beneath"
     " these; they are the\n"),
    ("- 142 `test_*.py` modules among 149 `.py` files; the others are benches and the\n",
     f"- {integration_tests} `test_*.py` modules among {integration_py} `.py` files; the others are benches and"
     " the\n"),
    ("- The aether tree carries 36 `test_*.py` modules beneath these; they are the\n",
     f"- The aether tree carries {count_tests('tests/integration/melder/aether') - rift} `test_*.py` modules beneath"
     " these; they are the\n"),
    ("the 35 test_*.py modules in\n  tests/integration/melder/conduit/",
     f"the {count_tests('tests/integration/melder/conduit')} test_*.py modules in\n"
     "  tests/integration/melder/conduit/"),
    ("the 12 test_*.py modules in\n  tests/integration/melder/crystallizer/",
     f"the {count_tests('tests/integration/melder/crystallizer')} test_*.py modules in\n"
     "  tests/integration/melder/crystallizer/"),
    ("the 47 test_*.py modules in\n  tests/integration/melder/spellbook/",
     f"the {count_tests('tests/integration/melder/spellbook')} test_*.py modules in\n"
     "  tests/integration/melder/spellbook/"),
    ("The 745 test modules of the\n",
     f"The {unit_tests + component_tests + integration_tests} test modules of the\n"),
]
for old, new in COUNTS:
    s.replace(DOC, old, new)
# Counts this pass checks but does not change.
for relative, stated in (("tests/unit/melder/mutation_research", 20), ("tests/unit/melder/build_assets", 3),
                         ("tests/component/melder/crystallizer", 7), ("tests/component/melder/mutation_research", 1),
                         ("tests/component/melder/utilities", 4), ("tests/integration/melder/aether/rift", 3),
                         ("tests/integration/melder/live_sim", 2), ("tests/integration/melder/multithreading", 5),
                         ("tests/integration/melder/mutation_research", 2), ("tests/experimentation", 33)):
    if count_tests(relative) != stated:
        raise SystemExit(f"{relative}: {count_tests(relative)} test modules, the document says {stated}")

ENTRY = r"- path: `{0}`\n  start_line: 1\n  end_line: \d+\n  loc: \d+\n  verified_at: \S+\n(?:  note: .*\n)?"


def measured(path: str) -> str:
    """Return one freshly measured code-map entry for a file on disk."""
    loc = len((pathlib.Path(ROOT) / path).read_bytes().decode("utf-8").splitlines())
    return f"- path: `{path}`\n  start_line: 1\n  end_line: {loc}\n  loc: {loc}\n  verified_at: {NOW}\n"


def find_entry(path: str) -> str:
    """Return the one code-map entry block for `path` (with its note line, when present)."""
    matches = re.findall(ENTRY.format(re.escape(path)), s._load(DOC))
    if len(matches) != 1:
        raise AssertionError(f"code map entry for {path}: {len(matches)} matches")
    return matches[0]


s.insert_after(DOC, find_entry("tests/unit/melder/spellbook/bind/test_stable_spell_fingerprint.py"),
               measured(UNIT_NEW))
s.insert_after(DOC, find_entry("tests/component/melder/aether/test_aether_spell_id_regime_property_component.py"),
               measured(COMPONENT_NEW))

text = s._load(DOC)
code_map = text[text.index("## C1 Code Map (Core)"):text.index("## Diagrams")]
catalog = text[:text.index("## C1 Code Map (Core)")]
key_files = set()
for block in re.findall(r"Key Files \(C1\):\n((?:- .*\n|  .*\n)+)", catalog):
    key_files.update(re.findall(r"^- `([^`]+)`", block, re.M))
listed = set(re.findall(r"^- path: `([^`]+)`", code_map, re.M))
if key_files != listed:
    raise SystemExit(f"core set differs from the key-file union: missing {sorted(key_files - listed)}, "
                     f"extra {sorted(listed - key_files)}")
total = len(key_files)
count_line = re.search(r"above - (\d+) paths - and nothing else\.", text)
s.replace(DOC, count_line.group(0), f"above - {total} paths - and nothing else.")

s.replace(
    DOC,
    "## Context / Handoff Summary\n\n2026-09-30 per-frame spell worlds (0.2.8213-0.2.8214):",
    "## Context / Handoff Summary\n\n"
    "2026-09-30 injected dependencies (0.2.8215): two new files - the first direct meld of a dependency bound after\n"
    "conjure, across scopes, lifetimes, caching and the SpellSpace door (component), and the target pass's\n"
    "dependency flags (unit) - plus deferred-lane rows in the aether tree's `test_meld.py` (four new; four existing\n"
    f"rows now make their spell a Phase 5 root). The C1 core set gains the two key files ({total} paths). The tier\n"
    "counts are remeasured: several had not followed earlier lanes' new files (unit, component and integration\n"
    "totals and the aether, crystallizer, spellbook, utilities and conduit trees).\n"
    "\n"
    "2026-09-30 per-frame spell worlds (0.2.8213-0.2.8214):",
)

long_lines = s.long_added_lines()
if long_lines:
    raise SystemExit("long added lines:\n" + "\n".join(long_lines))
final = s._load(DOC)
final_map = final[final.index("## C1 Code Map (Core)"):final.index("## Diagrams")]
if len(set(re.findall(r"^- path: `([^`]+)`", final_map, re.M))) != total:
    raise SystemExit("core set is not the key-file union after the edit")
for written in s.write():
    print("wrote", written, "core set", total, "unit", unit_tests, unit_py, "component", component_tests,
          component_py, "integration", integration_tests, integration_py)
