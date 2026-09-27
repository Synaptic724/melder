"""Release note section + 0.2.80 notch for the disposal-failure lane (melder_0, 2026-09-27). Usage: <repo root>"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import eol_lines
replace_lines = eol_lines.replace_lines

root = sys.argv[1]
note = os.path.join(root, "release_docs/0.2.77.md")
version = os.path.join(root, "src/melder/__version__.py")
print(replace_lines(version, '__version__ = "0.2.79"\n', '__version__ = "0.2.80"\n'))
print(replace_lines(note, "# Melder 0.2.79\n", "# Melder 0.2.80\n"))
print(replace_lines(note, """- **Room commands are unchanged.** The Nexus room commands and viewer methods of the same names keep
  their behaviour and access control.

## Override payload values reach the provider as the objects you gave
""", """- **Room commands are unchanged.** The Nexus room commands and viewer methods of the same names keep
  their behaviour and access control.

## Disposal runs every method and reports every failure

When one of an object's disposal methods raises, Melder now still runs the methods declared after it. With
a book whose `disposal_method_names` is `["close", "release"]`, an object whose `close()` raises still has
`release()` called; before, `release()` was skipped and whatever it releases leaked.

- **One error per failing method, with the real cause.** `purge`, leaving a `with conduit.enter_spellspace()`
  block and the other scope teardowns raise the same `ExceptionGroup` as before, and conduit cleanup still
  logs it. The group now holds one `RuntimeError` per failing method instead of one per object, and each
  error's `__cause__` is the exception the method raised, with its type and traceback.
- **One bad object cannot stop the rest.** Reporting a failure no longer relies on the failing object's
  `__str__`; an object whose `__str__` also fails is named by type and id, and the other objects in the
  scope are still disposed.
- **Order is unchanged.** Methods run in the order the book declares them, and objects are disposed newest
  first, as before.

## Override payload values reach the provider as the objects you gave
"""))
print(replace_lines(note, """  over every live conduit). The retired override-targeting internals and normal-meld emitters no longer
  appear, and the graph documents drop the modules this release deletes.
""", """  over every live conduit), and disposal that runs every declared method and reports each failure. The
  retired override-targeting internals and normal-meld emitters no longer appear, and the graph documents drop
  the modules this release deletes.
"""))
print(replace_lines(note, "- Agent documentation metadata and the whole-repository LLM bundles are rebuilt for 0.2.79.\n",
                    "- Agent documentation metadata and the whole-repository LLM bundles are rebuilt for 0.2.80.\n"))
