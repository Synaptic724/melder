"""Apply melder_1's 0.2.8267 entry to release_docs/next_version_release.md.

Usage: python apply_release_note_20261024.py <path to next_version_release.md> <previous version> <new version>
Every edit is anchored on text and asserts a single match; the file is written only if it is unchanged since read.
"""
import pathlib
import sys

path = pathlib.Path(sys.argv[1])
previous, version = sys.argv[2], sys.argv[3]
raw = path.read_bytes()
doc = raw.decode("utf-8")
assert "\r\n" not in doc
report = []


def exact(old, new):
    global doc
    assert doc.count(old) == 1, (doc.count(old), old[:90])
    doc = doc.replace(old, new)
    report.append(new)


SECTION = (
    "## A `many` dependency belongs to the scope that built it, not to the object that holds it\n"
    "\n"
    "**Breaking change:** a `many` dependency with disposal methods is now always recorded and disposed by the scope that\n"
    "built it - the spell space, else the conduit that melded - also when it is built for a longer-lived object (a\n"
    "`unique`, `unique_per_conduit`, `unique_per_spell_space`, `unique_per_conduit_lineage` or `unique_per_conduit_cluster`\n"
    "spell). Cleaning up that object - purging it, or the end of the creations that hold it - runs only the object's own\n"
    "disposal methods; what it does with the objects it holds is up to those methods. From 0.2.8235 to 0.2.8265 such a\n"
    "dependency belonged to the object that held it: it was recorded with the object's owner, disposed right after the\n"
    "object when the object was purged, and moved with the object to another root. That is removed on the owner's\n"
    "decision, so Melder behaves like Autofac: an object is disposed by the scope that built it, and cleaning up one\n"
    "object never cleans up the objects it was given.\n"
    "\n"
    "```python\n"
    "class Connection:\n"
    "    def __init__(self) -> None:\n"
    "        self.closed = False\n"
    "\n"
    "    def close(self) -> None:\n"
    "        self.closed = True\n"
    "\n"
    "\n"
    "class Repository:\n"
    "    def __init__(self, connection: Connection) -> None:\n"
    "        self.connection = connection\n"
    "\n"
    "\n"
    "book = md.Spellbook()\n"
    "book.bind(spell=Connection, existence=\"many\", disposal_method_names=[\"close\"])\n"
    "book.bind(spell=Repository, existence=\"unique\")\n"
    "root = book.conjure()\n"
    "\n"
    "with root.enter_lesser_conduit() as request:\n"
    "    repository = request.meld(\"Repository\")      # first built inside the request scope\n"
    "\n"
    "assert repository.connection.closed              # the request scope closed the connection it built\n"
    "assert root.meld(\"Repository\") is repository     # the root still serves the same repository\n"
    "```\n"
    "\n"
    "The calls are the same as in 0.2.8235-0.2.8265; only Melder's answer differs: those releases left the connection\n"
    "open here and closed it when the root ended. The repository now holds a closed connection because the scope that\n"
    "built the connection has ended - what Autofac does when a singleton keeps a dependency from a shorter scope. To keep\n"
    "the connection as long as the repository, meld the repository first where it lives (`root.meld(\"Repository\")`), so\n"
    "the root builds the connection and closes it when the root ends; or bind `Connection` without disposal methods and\n"
    "close it in the repository's own disposal method.\n"
    "\n"
    "Purge, the live-creation probes and transfers follow the same rule:\n"
    "\n"
    "- Purging the object disposes the object alone. Its `many` dependencies are disposed when their scope ends, and\n"
    "  their disposal failures are raised there (0.2.8238-0.2.8265 disposed them right after the object and raised their\n"
    "  failures with its own).\n"
    "- `purge` and `has_live_creation` for the dependency's `many` spell count every instance its scope recorded, also\n"
    "  one a live object still holds (they skipped those).\n"
    "- `transfer_spell_ownership(..., move_creations=True)` moves the object, not its `many` dependencies, which stay\n"
    "  with the scope that built them (0.2.8238-0.2.8265 moved them with it); with `include_dependencies=True` the\n"
    "  dependency's spell moves too, and its objects with it.\n"
    "\n"
    "What stays the same: a `many` spell melded directly, and the `many` dependencies of a `many` spell, are recorded\n"
    "with the scope that melds them, as before; a `many` dependency without disposal methods is not recorded at all;\n"
    "managed pools keep the `many` dependencies of their objects with each object (see `Existence.managed_spell_quantity`\n"
    "below); warm melds run exactly the code they ran before, and cache files and saved records are unchanged.\n"
    "\n"
    "With `generalized_singleton_specialization_enabled` (opt-in, off by default), a root whose graph passes a `many`\n"
    "dependency to a longer-lived object is still not specialized: the specialized path would build a new dependency on\n"
    "every warm meld, which the stored object never uses.\n"
    "\n"
)
start = "## A `many` dependency is disposed with the object that holds it\n"
end = "dependency on every warm meld, which the stored holder never used.\n\n"
assert doc.count(start) == 1
i = doc.index(start)
j = doc.index(end, i) + len(end)
old = doc[i:j]
assert "Until 0.2.8234" in old and "root.purge(\"Repository\")" in old, old[:200]
assert doc[j:].startswith("## A root that is torn down leaves its cluster")
doc = doc[:i] + SECTION + doc[j:]
report.append(SECTION)

exact(
    "- The packaged system documents describe where a `many` dependency built for a longer-lived object is recorded (with\n"
    "  the holder's owner), the store selection and live-creation probe that follow, and the specializer's eligibility.\n",
    "- The packaged system documents describe where a `many` dependency built for a longer-lived object is recorded (the\n"
    "  scope that built it, since 0.2.8267), the store selection and live-creation probe that follow, and the\n"
    "  specializer's eligibility.\n",
)
exact(
    "- The packaged system documents describe a root leaving its cluster at teardown, the team store a cluster owns,\n"
    "  the record that carries a slotted object's `many` children through purge, transfer and disposal, and the\n"
    "  transfer default and handover; the code-map extents of the files these changes touched are remeasured.\n",
    "- The packaged system documents describe a root leaving its cluster at teardown, the team store a cluster owns, and\n"
    "  the transfer default and handover; the code-map extents of the files these changes touched are remeasured.\n",
)
exact(
    "- The internal-bind guard manifest holds 630 entries at 0.2.8257 (628 at 0.2.8244, 622 at 0.2.8227):\n"
    "  `SpellCodeDigest` and `BindingManifest` joined at 0.2.8257; `HolderDisposalEntry`, the record that keeps a slotted\n"
    "  object's `many` children with it, joined at 0.2.8238, `ManagedSpellMode` at 0.2.8242, the managed pool\n"
    "  (`ManagedSpellQuantity`) and `ManagedSpellExhaustedError` at 0.2.8243, and `ReleaseManagedSpell` and\n"
    "  `ManagedSpellLease` at 0.2.8244.\n",
    "- The internal-bind guard manifest holds 629 entries at 0.2.8267 (630 at 0.2.8257, 628 at 0.2.8244, 622 at\n"
    "  0.2.8227): `HolderDisposalEntry`, the record that kept a slotted object's `many` children with it, joined at\n"
    "  0.2.8238 and left at 0.2.8267; `SpellCodeDigest` and `BindingManifest` joined at 0.2.8257, `ManagedSpellMode` at\n"
    "  0.2.8242, the managed pool (`ManagedSpellQuantity`) and `ManagedSpellExhaustedError` at 0.2.8243, and\n"
    "  `ReleaseManagedSpell` and `ManagedSpellLease` at 0.2.8244.\n",
)
exact(
    f"- Agent documentation metadata and the whole-repository LLM bundles are rebuilt for {previous}.\n",
    "- The packaged system documents (`melder.__architecture__`, `melder.__components__`) and the packaged graph describe a\n"
    "  `many` dependency belonging to the scope that built it: one registration rule in the compiled plans, a holder's\n"
    "  cleanup running only its own disposal, what purge, the live-creation probe and a transfer do with the dependency,\n"
    "  and the specializer's decline kept; the removed holder record is marked as removed. The scopes guide\n"
    "  (`docs/intermediate/scopes.md`) and the ownership guide (`docs/intermediate/ownership.md`) say a `many` dependency\n"
    "  belongs to the conduit or spell space that built it and stays there through a transfer, and the packaged test\n"
    "  documents describe the new tests; the code-map extents of the changed files are remeasured, and line citations\n"
    "  into `conduit.py` and `creations.py` remapped.\n"
    f"- Agent documentation metadata and the whole-repository LLM bundles are rebuilt for {version}.\n",
)
assert doc.startswith(f"# Melder {previous}\n")
doc = f"# Melder {version}\n" + doc[len(f"# Melder {previous}\n"):]

for block in report:
    for line in block.split("\n"):
        if len(line) > 120:
            print("LONG", len(line), line[:100])
assert path.read_bytes() == raw, "the release note changed while the edits were prepared"
path.write_bytes(doc.encode("utf-8"))
print("wrote", path, len(doc.split("\n")) - 1, "lines")
