"""
Add the injected_provider_first_direct_meld entry (0.2.8215) to the running release note.

Usage: python apply_release_note.py <repository root>
The example is the one run as written by ../release/release_example.py.
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from apply_support import ApplySession

s = ApplySession(sys.argv[1])
NOTE = "release_docs/next_version_release.md"

s.replace(NOTE, "# Melder 0.2.8214\n", "# Melder 0.2.8215\n")
s.insert_before(
    NOTE,
    "## Packaging and documentation\n",
    "## Fixed: a class bound after conjure melds directly after it was injected\n"
    "\n"
    "On a dynamic root, a class bound after `conjure()` and first built as another class's dependency could not be\n"
    "melded directly afterwards. The consumer's meld worked and received the dependency, but a direct meld of the\n"
    "dependency from the same scope raised `RuntimeError: Cannot build CreationContext before spell_codegen_creation\n"
    "exists.` The consumer's meld had compiled the dependency only inside the consumer's own plan and left it marked\n"
    "valid, so nothing compiled it for a meld of its own. Now the consumer's meld marks such a dependency as still\n"
    "owing its own resolution, and its first direct meld runs that resolution itself - no validation call, second\n"
    "conjure or dependency-first warm-up - and returns the instance its scope already holds (`unique_per_conduit`,\n"
    "`unique`) or a new one (`many`):\n"
    "\n"
    "```python\n"
    "book = Spellbook(aetheric_frame=\"app\")\n"
    "root = book.conjure(name=\"app-root\", dynamic=True)\n"
    "root.bind(spell=Service, existence=\"unique_per_conduit\")   # bound after conjure\n"
    "root.bind(spell=Consumer, existence=\"many\")\n"
    "scope = root.create_lesser_conduit()\n"
    "consumer = scope.meld(spell=Consumer)          # Service is built as Consumer's dependency\n"
    "assert scope.meld(spell=Service) is consumer.service   # raised RuntimeError before 0.2.8215\n"
    "```\n"
    "\n"
    "The same holds on the root, in named or unnamed and sibling lessers, through `SpellSpace.meld`, and with the\n"
    "conjure cache on. What stays the same: melding the dependency first, or binding both before `conjure()`, works\n"
    "as before; warm melds, validation verdicts and conjure do no extra work. A dependency marked this way pays one\n"
    "resolution pass on its first direct meld.\n"
    "\n",
)
s.replace(
    NOTE,
    "- Agent documentation metadata and the whole-repository LLM bundles are rebuilt for 0.2.8214.\n",
    "- The packaged system documents describe how a dependency compiled only inside a consumer's plan is marked and\n"
    "  resolved on its first direct meld, and the meld runtime's deferred lane; their line citations into\n"
    "  `spellbook.py`, `spellbook_creation_system.py` and `meld.py` are remeasured (several were already stale).\n"
    "- Agent documentation metadata and the whole-repository LLM bundles are rebuilt for 0.2.8215.\n",
)
long_lines = s.long_added_lines()
if long_lines:
    raise SystemExit("long added lines:\n" + "\n".join(long_lines))
for written in s.write():
    print("wrote", written)
