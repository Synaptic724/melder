"""Append S1's MEASURE note (the code digest v2 prototype) and sync S1's Artifact Links, Updated and handoff.

melder_0, 2026-10-18. Run from context_compass/: python3 artifacts/spell_identity_20261018/scripts/record_s1_measure.py
"""
import pathlib
import sys
import textwrap

STAMP = sys.argv[1]
STORY = pathlib.Path("tickets/stories/2026-10-18_spell_id_hashes_the_object_code_story.md")


def wrap(label: str, text: str) -> str:
    """One note field: first line after the label, continuation lines indented four spaces, width 116."""
    lines = textwrap.wrap(text, width=116, initial_indent="  " + label + ": ", subsequent_indent="    ",
                          break_on_hyphens=False, break_long_words=False)
    return "\n".join(lines)


CLAIM = (
    "The code digest v2 prototype (outside src/) holds the owner's calls 1-3 on 3.14.7t. Rules: a function is its "
    "deoptimized instruction stream (co_code, EXTENDED_ARG folded) with each LOAD_CONST replaced by its order of first "
    "use and the used constants hashed by value, plus its argument counts, flags without CO_HAS_DOCSTRING, name tables "
    "and exception table, its defaults, the code of its __annotate__, its closure values (a __classdict__ cell is a "
    "marker), its type parameters and its __dict__ minus __wrapped__; a class is its module, qualname, metaclass, "
    "direct bases and, per MRO entry, the namespace digest of code outside the standard library (standard library and "
    "builtins by qualified name), a namespace being every __dict__ entry except interpreter bookkeeping (_abc_impl "
    "opaque); values go by value (scalars, containers, enum members with their values), classes by name unless nested "
    "(then digested), functions by code, typing objects by text, standard-library and Melder objects by type, user "
    "objects by type and data (slots, then __dict__, cached_property values skipped), cycles marked. All 42 cases "
    "(E01-E34) behave as designed. The id moves for a base-class method body, a class-level value, a tuple's order, a "
    "nested class, a decorator argument, property, static and class method bodies, a dataclass default, an enum "
    "value, a field or parameter annotation, a user metaclass body, an except clause, a local rename (counted), a type "
    "parameter bound, another module, a factory's captured value, object data, nested object data, a mangled slot, a "
    "bound method's self data, partial arguments, a lambda default and two standard-library loggers (today's id moves "
    "for four of these). It stays for docstrings, comments and blank lines (a try/except method too), the same source "
    "executed twice, equal object data, a held lock or logger, self-reference, a cached_property read, 20000 calls "
    "(specialization), annotations read, a runtime-checkable isinstance, ABC.register, sys.monitoring LINE and "
    "INSTRUCTION events and sys.settrace; a class-level dict mutated at runtime moves it (an object is hashed as it is "
    "at bind). Byte-identical across hash seeds 1 and 2 and GIL 0 and 1. Corpus: all 782 classes and functions of "
    "src/melder digest without error into 782 distinct digests, identical across the four runs; per target, cold "
    "(fresh memo) median 0.29 ms, p95 1.5 ms, max 7.5 ms; warm (code digests memoized) median 0.11 ms, p95 0.45 ms; "
    "today's fingerprint median 0.064 ms, p95 0.16 ms. The first prototype's dis walk cost 1172 ms over Melder's 5952 "
    "code objects, the co_code walk 46 ms. Found on the way: in 3.14 co_consts[0] holds the docstring or else the first "
    "constant, which the optimizer may leave unused, so constants must be read by value, never by index."
)
IMPACT = (
    "S1's design docs can state the digest as a contract with a measured cost: about 0.1 to 0.3 ms more per bind, paid "
    "at bind and never at meld. Only code objects may be memoized; classes and functions are mutable."
)
NEXT = "Write the architecture patch, the Binding Pipeline component patch and the code-description patch."
EVIDENCE = [
    "context_compass/artifacts/spell_identity_20261018/probes/code_digest_v2.py:1-346",
    "context_compass/artifacts/spell_identity_20261018/probes/probe_code_digest_cases.py:1-234",
    "context_compass/artifacts/spell_identity_20261018/runs/probe_code_digest_cases_gil0_seed1.txt:1-42",
    "context_compass/artifacts/spell_identity_20261018/probes/probe_code_digest_corpus.py:1-90",
    "context_compass/artifacts/spell_identity_20261018/runs/probe_code_digest_corpus_gil0_seed1.txt:1-6",
    "context_compass/artifacts/spell_identity_20261018/runs/corpus_digests_gil0_seed1.tsv:1-782",
]

note = "\n".join([
    f"- DATETIME: {STAMP}", "  AUTHOR: melder_0", "  AUTHOR_ROLE: synaptic_python_developer", "  TYPE: MEASURE",
    wrap("CLAIM", CLAIM), "  EVIDENCE:", *("  - " + item for item in EVIDENCE), wrap("IMPACT", IMPACT),
    wrap("NEXT", NEXT), "  REREAD: REQUIRED", "  SCORE_0_TO_10: 9",
]) + "\n\n"

text = STORY.read_text(encoding="utf-8")
anchor = "## Closure Confirmation"
assert text.count(anchor) == 1
text = text.replace(anchor, note + anchor)

edits = [
    ("- Updated: 2026-10-18T12:15:14Z\n", f"- Updated: {STAMP}\n"),
    ("- ARTIFACTS_REQUIRED: false\n- ARTIFACT_PATHS:\n  - none yet (the design's probes are rowed under the epic)\n",
     "- ARTIFACTS_REQUIRED: true\n- ARTIFACT_PATHS:\n"
     "  - artifacts/spell_identity_20261018/probes/code_digest_v2.py (the code digest v2 prototype)\n"
     "  - artifacts/spell_identity_20261018/probes/probe_code_digest_cases.py (E01-E34)\n"
     "  - artifacts/spell_identity_20261018/probes/probe_code_digest_corpus.py (src/melder corpus, cost)\n"
     "  - artifacts/spell_identity_20261018/runs/ (four runs of each: hash seeds 1 and 2, GIL 0 and 1)\n"),
    ("- CLEANUP_TRIGGER: rows are added when this story produces its own artifacts\n",
     "- CLEANUP_TRIGGER: at closure the probes stay as the design's evidence; each case becomes a regression test\n"),
    ("- Next: read Bind's fingerprint and the binding profile whole; extend the prototype to bases, class-level\n"
     "  values and object data; write the architecture patch, the code-hash component patch and its code\n"
     "  description.\n",
     "- Done: Bind's fingerprint and the binding profile read whole; the prototype extended to bases, class-level\n"
     "  values, object data and closures, and measured (MEASURE note).\n"
     "- Next: the architecture patch, the Binding Pipeline component patch and the code-description patch, for the\n"
     "  owner's approval.\n"),
]
for old, new in edits:
    assert text.count(old) == 1, old[:60]
    text = text.replace(old, new)
STORY.write_text(text, encoding="utf-8")
print("S1 updated", STAMP)
