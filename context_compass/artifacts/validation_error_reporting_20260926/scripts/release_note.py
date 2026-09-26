"""Add the conjure-report section to release_docs/next_version_release.md and correct two bullets (2026-09-26).

Usage: python release_note.py <repo_root>
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from patch_util import replace_block as _replace_block

note = pathlib.Path(sys.argv[1]) / "release_docs/next_version_release.md"


def replace_block(old: str, new: str) -> None:
    """Idempotent: skip when the new text is already present."""
    if new in note.read_text(encoding="utf-8").replace("\r\n", "\n"):
        print("already applied")
        return
    _replace_block(note, old, new)


replace_block("""- **The hint moved, it did not disappear.** `conjure(validation_warnings=True)` lists such a parameter as
  `REQUIRED_HOLE`, and the message now says that Melder injects collections only as `list[T]`.
- **`Any` is never injected.** `list[Any]` now draws the same "not a DI type" warning as `list[int]`.""",
"""- **The hint moved, it did not disappear.** `conjure(validation_warnings=True)` lists such a parameter as
  `REQUIRED_HOLE`; when the container holds one of your classes, as in `dict[str, Operation]`, the message
  says that Melder injects collections only as `list[T]`. Plain data such as `dict[str, Any]` gets no hint.
- **`Any` is never injected.** `list[Any]`, like `list[int]` or `list[str]`, is plain data you supply; it
  draws no list warning.""")

replace_block("""## Automatic creation-cache refresh after a Melder update""", """## Clearer errors when conjure refuses spells

When `conjure` refused spells, `SpellbookValidationError` printed every check that had run on them -
warnings included, each followed by a dump of its details - with 64-character spell ids, internal phase
names, and cycles written as ids. Some refusals printed no reason at all. The message now says which spells
failed, why, and what to change, by name:

```text
Spellbook validation failed. Broken spells: Holder.
Holder:
  - Spell 'Holder' (unique) depends on 'Leaf' (unique_per_spell_space), which lives for a shorter scope,
    so 'Holder' would keep a stale 'Leaf' after that scope ends. Give 'Holder' the same or a shorter
    existence (or many), or give 'Leaf' a longer one. [scope_ordering_violation]
```

- **Errors only.** Each broken spell gets one block listing its errors, each with what to change and its
  code in brackets. Warnings never block conjure, so they are only counted, with a pointer to
  `conjure(validation_warnings=True)`.
- **No more reasonless refusals.** A refusal found while resolving the conduit (scope ordering, a dependency
  the book cannot see, a cycle) used to print "(none recorded)"; its reason is now in the message. Errors
  that belong to no single spell are listed under "Whole-graph errors".
- **Names, not ids.** Cycles read `'CycleA' -> 'CycleB' -> 'CycleA'`, reported once per spell; a
  spell id appears, shortened, only where Melder has no name for it.
- **Internal errors are marked.** Checks of Melder's own bookkeeping are shown as `[internal]`, with a note
  to report them: they are Melder bugs, not problems in your code.
- **`*args: Any` and `**kwargs: Any` no longer break a spell.** A constructor accepting anything through
  variadic parameters annotated `Any` was refused as "variadic DI"; `Any` is never injected, so it now
  conjures.
- **Same exception, same data.** `SpellbookValidationError` and its `broken_spells` are unchanged, and it
  gains an optional keyword, `system_diagnostics`. The first line still starts with
  `Spellbook validation failed.` and contains `Broken spells:`; code matching other parts of the old text
  needs updating.

## Automatic creation-cache refresh after a Melder update""")
print("release note updated")
