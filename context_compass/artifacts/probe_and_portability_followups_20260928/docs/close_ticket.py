"""Closure edits for the probe and portability follow-ups ticket (melder_0, 2026-09-28)."""
import pathlib
import re
import sys

ticket = pathlib.Path(sys.argv[1])
now = sys.argv[2]
raw = ticket.read_bytes().decode("utf-8")
crlf = "\r\n" in raw
t = raw.replace("\r\n", "\n")


def swap(text: str, old: str, new: str) -> str:
    assert text.count(old) == 1, (text.count(old), old[:60])
    return text.replace(old, new, 1)


def tick(text: str, start: str, end: str) -> str:
    a = text.index(start)
    b = text.index(end, a)
    return text[:a] + text[a:b].replace("- [ ]", "- [x]") + text[b:]


t = swap(t, "- Status: in_progress\n", "- Status: done\n")
t, n = re.subn(r"^- Updated: .*$", f"- Updated: {now}", t, count=1, flags=re.M)
assert n == 1
t = swap(t, f"- Updated: {now}\n", f"- Updated: {now}\n- Completed: {now}\n"
         "- Closure Basis: owner direction in chat (2026-09-28): \"just keep iterating anything you got left\", "
         "then \"ok continue\"\n  after the remaining steps were named as this turn-in.\n")
t = swap(t, "  rebuild waived for now; both follow-ups are recorded with evidence in the closed probe task.\n",
         "  rebuild waived for now; both follow-ups are recorded with evidence in the closed probe task.\n"
         "- from_state: in_progress\n- to_state: done\n"
         "- transition_reason: Docstrings and portability landed at 0.2.8205 with docs, graph and the release note;"
         " the\n  waived rebuild is covered by workflows_0's 0.2.8206 rebuild, checks OK; closed on the owner's"
         " direction\n  (DECISION note 2026-09-28T08:38:55Z).\n")
t = tick(t, "## Steps / Checklist\n", "## Deliverables\n")
t = swap(t, "- An accurate ConduitMeld probe contract; two system documents that name no path into the tooling.\n",
         "- conduit_meld.py docstrings (six places) name the store each lifetime uses (`many` and"
         " `unique_per_conduit`:\n  the conduit's store; `unique`: the Spell owner; lineage: the lineage root;"
         " cluster: the elected leader) and\n  replace the stale active-spellspace claim with the released-space"
         " refusal; no code changed.\n"
         "- src_architecture and src_components: `## Indexing` keeps its prose and heading rules without the tool"
         "\n  commands or the tooling's specification; patch-lane and skill paths became logical names;"
         " conduit_meld.py\n  remeasured in the C1 map; one handoff paragraph each; indexes rebuilt.\n"
         "- Graph: ConduitMeld prose rewritten from the full read and accepted; `__version__` 0.2.8205 and a"
         " release-note\n  packaging bullet.\n")
t = swap(t, "- Exact list in the PLAN note before edits.\n",
         "- src/melder/aether/conduit/meld/conduit_meld.py (docstrings only)\n"
         "- src/melder/__version__.py (0.2.8204 -> 0.2.8205)\n"
         "- release_docs/next_version_release.md (header, packaging bullet)\n"
         "- context_compass/system_docs/src_architecture.md and src_architecture_index.md\n"
         "- context_compass/system_docs/src_components.md and src_components_index.md\n"
         "- context_compass/system_docs/graph/ (conduit_meld.json authored and accepted; the extraction re-hashed"
         "\n  __version__, eight asset descriptors and duplicate_spell_name_strategy), src_graph.md and"
         " src_graph_index.md\n"
         "- context_compass/artifacts/probe_and_portability_followups_20260928/\n")
t = swap(t, "## Validation\n- Not run.\n",
         "## Validation\n"
         "- 0.2.8205, before the rebuild (assets stale by the owner's waiver): meld/conduit tests 1915 passed; the"
         "\n  package/asset/system-document set 287 passed, 1 skipped, 1 failed - the stamped-assets test, expected"
         " while\n  assets were stale (validation_0_2_8205_stale_assets.txt); 3.14t PYTHON_GIL=0.\n"
         "- 0.2.8206, after workflows_0's rebuild: both portability checks 0 hits on both documents; index --check"
         " OK;\n  asset --check OK; LLM --check --include-untracked OK; test_package_version_metadata.py 4 passed\n"
         "  (validation_0_2_8206_after_rebuild.txt).\n"
         "- Full suite, benchmarks: not run - docstring and document text only, nothing on the meld path.\n"
         "- Coverage: Not run.\n")
t = tick(t, "## Applicable Anti-Patterns\n", "## Done Checklist\n")
t = tick(t, "## Done Checklist\n", "## Artifact Links (Optional)\n")
t = swap(t, "- DISPOSITION: retain_as_reference\n",
         "- DISPOSITION: retain_as_reference (apply and edit scripts, graph run logs and walker reports,"
         " preservation\n  report, validation logs)\n")
t = swap(t, "Opened 2026-09-28T01:08:20Z. Follow-ups lane: ConduitMeld probe docstring and system-document"
         " portability. Next: read\nconduit_meld.py whole.\n",
         "State (2026-09-28): done. At 0.2.8205 the ConduitMeld docstrings name the store each lifetime uses and"
         " no longer\npromise an active-spellspace check (no code changed), and src_architecture / src_components"
         " name no path into\nthe documentation tooling (both portability checks return nothing; indexes current)."
         " The graph's ConduitMeld\nnode is accepted against the source. The asset and bundle rebuild waived for"
         " this pass is covered by\nworkflows_0's 0.2.8206 rebuild; both checks OK. Follow-up for fable_0, not"
         " done here: the stale Meld and\nSpellbook graph nodes.\n")
for i, line in enumerate(t.split("\n"), 1):
    if len(line) > 120 and " " in line.strip():
        print("LONG", i, len(line))
if crlf:
    t = t.replace("\n", "\r\n")
ticket.write_bytes(t.encode("utf-8"))
print("closed", now, "crlf", crlf)
