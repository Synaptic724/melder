"""S7: corrections to s7_docs_components.py after re-reading the managed modules on 0.2.8246 (before its first run).

Each block between two unique markers is replaced; the run refuses when a marker is missing or repeated.
"""
import pathlib

P = pathlib.Path(__file__).with_name("s7_docs_components.py")
text = P.read_text(encoding="utf-8")


def replace_between(start: str, end: str, new: str) -> None:
    global text
    assert text.count(start) == 1, ("start", text.count(start), start[:80])
    a = text.index(start)
    b = text.index(end, a)
    assert text.count(end, a) >= 1
    b += len(end)
    text = text[:a] + new + text[b:]


replace_between(
    "- `ManagedSpellQuantity` (an `AbstractElasticPool`): keep",
    "never the pool.\n",
    """- `ManagedSpellQuantity` (an `AbstractElasticPool`): keep one version's idle objects (`_idle`, newest last), count
  the objects built and alive, reserve a place for a build (elastic: always; limited_quantity: below the limit, else
  an object released since the plan's empty pop, else `ManagedSpellExhaustedError`; queue: the same, waiting up to
  the timeout before it refuses), put an object back (the reset names in order, outside every lock, then the
  append; queue wakes one waiter; above the baseline the elastic band trims the oldest), give a failed build's
  place back (`abandon`), record the disposal-bearing `many` children built for an object (`adopt`), destroy an
  object (its disposal methods, then its recorded children newest first) and clean up (idle objects and every
  recorded child, failures in one ExceptionGroup). `create_object` and `acquire` refuse: the emitted plan builds,
  never the pool.
""",
)
replace_between(
    "- Leased objects (the plan's inline pop",
    "  version).\n",
    """- Leased objects (the plan's inline pop, or the miss's build) and refusals. `ManagedSpellQuantity.describe()`: the
  retention keys, identity (spell id and name, binding, frame, composing root), policy (mode, limit, timeout, reset
  and disposal names), `count`, `out_count` and `children_recorded`; `ReleaseManagedSpell().describe(cls)`: one such
  snapshot per pool of the class, plus `holding_conduit_id` and `active_version`.
""",
)
replace_between(
    "- The registry lock is a leaf held only to publish",
    "no edge joins frame -> conduit -> Book.\n",
    """- The registry lock is a leaf held only to publish; every read is lock-free. Creations registers and unregisters
  outside its store lock: owner stamping holds the Spell lock, takes the store's leaf lock for the map, releases it,
  then takes the registry's leaf lock to publish. No edge joins frame -> conduit -> Book.
""",
)
replace_between(
    "Invariants/Guarantees:\n- One pool per (root store",
    "the owner stamp follows it (0.2.8246).\n",
    """Invariants/Guarantees:
- One pool per (root store, managed spell version). `count` (objects built and alive) rises only in `reserve()`,
  after the mode's check, so it never exceeds the limit of a limited_quantity or queue pool; a released object the
  pool never built (a fresh override object) is pooled uncounted, because releases are trusted, never checked.
- The registry holds exactly the pools live root stores hold.
- A leasing site feeds exactly one consumer, so each lease goes to one holder or to the melding caller; the plan
  gives a lease back only when its consumer's construction fails or loses its cold race.
- A transfer disposes nothing: a pool moves as the store's `managed` row and the owner stamp follows it (0.2.8246).
""",
)
replace_between(
    "def first_class_line(path: str) -> str:",
    'return f"- `{path}`\\n  {purpose}\\n"\n',
    '''def first_class_line(path: str) -> str:
    """The inventory text of a module: its first class docstring's first paragraph, joined, without the period."""
    tree = ast.parse(pathlib.Path(path).read_text(encoding="utf-8"))
    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            paragraphs = [
                " ".join(line.strip() for line in block.split("\\n") if line.strip())
                for block in (ast.get_docstring(node) or "").split("\\n\\n")
            ]
            return [p for p in paragraphs if p][0].rstrip(".")
    raise AssertionError(path)


def inventory_row(path: str) -> str:
    """One entry by the inventory's rule: one line up to 120 characters, else the text on its own line, cut to 93
    characters plus '...' when it runs past 100 (the 39 cut entries measured 92-93)."""
    text = first_class_line(path)
    one = f"- `{path}` - {text}"
    if len(one) <= 120:
        return one + "\\n"
    if len(text) > 100:
        text = text[:93].rstrip() + "..."
    return f"- `{path}`\\n  {text}\\n"
''',
)
P.write_text(text, encoding="utf-8")
print("patched", len(text.splitlines()), "lines")
