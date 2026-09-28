"""Close the probe ticket in place (before the move to tickets/tasks/completed/): metadata, transition, checklists,
deliverables, files, validation, artifact links and the handoff summary. Usage: python <this> <ticket> <now>.
"""
import pathlib
import re
import sys

path = pathlib.Path(sys.argv[1])
now = sys.argv[2]
text = path.read_bytes().decode("utf-8")
assert "\r" not in text


def swap(old: str, new: str) -> None:
    global text
    assert text.count(old) == 1, (old[:70], text.count(old))
    text = text.replace(old, new)


swap("- Status: in_progress\n", "- Status: done\n")
text, n = re.subn(r"^- Updated: .*$", f"- Updated: {now}\n- Completed: {now}\n"
                  "- Closure Basis: owner turn-in in chat (2026-09-28): \"ok cool yeah fix the problem you have yourself and\n"
                  "  send it, finish off your fixes and turn in the remaining things please go ahead\".",
                  text, count=1, flags=re.M)
assert n == 1
swap(
    "  recorded with evidence by the scope_exit_dispose lane.\n\n## Steps / Checklist\n",
    "  recorded with evidence by the scope_exit_dispose lane.\n"
    "- from_state: in_progress\n"
    "- to_state: done\n"
    "- transition_reason: Landed at 0.2.8204 with docs, graph, release note, assets and bundles current; final suites\n"
    "  green on three interpreters; closed on the owner's turn-in directive (DECISION note 2026-09-28T00:59:15Z).\n"
    "\n## Steps / Checklist\n",
)
start = text.index("## Steps / Checklist\n")
end = text.index("## Deliverables\n")
text = text[:start] + text[start:end].replace("- [ ] ", "- [x] ") + text[end:]
start = text.index("## Applicable Anti-Patterns\n")
end = text.index("## Artifact Links (Optional)\n")
text = text[:start] + text[start:end].replace("- [ ] ", "- [x] ") + text[end:]
swap(
    "## Deliverables\n"
    "- A correct SpellSpace live-creation probe for `many`, its regression test, docs, notch and release-note entry.\n",
    "## Deliverables\n"
    "- The SpellSpace door's live-creation probe reads `many` from the space's own store and reports\n"
    "  \"spellspace_many\" with the space id (spellspace_meld.py; probe and class contracts updated).\n"
    "- Tests: one unit test rewritten and one added (test_concrete_meld_subclasses.py), one component test added\n"
    "  (test_conduit_component_spellspace_creations.py); all three red on 0.2.8203.\n"
    "- `__version__` 0.2.8204 and a release-note section; src_components promoted (probe scope, store selection,\n"
    "  two failure modes, flow step, C1, handoff); graph (SpellSpaceMeld and melder.__version__ accepted);\n"
    "  build assets and LLM bundles rebuilt, both checks OK.\n",
)
swap(
    "## Files / Paths Impacted\n- Exact list in the PLAN note before src edits.\n",
    "## Files / Paths Impacted\n"
    "- src/melder/aether/conduit/meld/spellspace_meld.py\n"
    "- src/melder/__version__.py\n"
    "- tests/unit/melder/aether/conduit/meld/test_concrete_meld_subclasses.py\n"
    "- tests/component/melder/aether/conduit/test_conduit_component_spellspace_creations.py\n"
    "- release_docs/next_version_release.md\n"
    "- context_compass/system_docs/src_components.md and src_components_index.md\n"
    "- context_compass/system_docs/graph/ (spellspace_meld.json, __version__.json authored; 8 asset descriptors\n"
    "  re-extracted), src_graph.md and src_graph_index.md\n"
    "- src/melder/_build_assets/ (agent_documentation, bind_guard, graph_adjacency, system_documents index and\n"
    "  manifest, src_components and src_graph payloads)\n"
    "- llm_support/ (src, tests and other bundles, their indexes, manifest.json)\n"
    "- context_compass/system_docs/patches/completed/spellspace_probe_many_2026_09_28/\n"
    "- context_compass/artifacts/spellspace_probe_many_20260928/\n",
)
swap(
    "## Validation\n- Not run.\n",
    "## Validation\n"
    "- Red before / green after: the 3 new or rewritten tests failed on 0.2.8203 (red_0_2_8203.txt) and the two\n"
    "  touched files passed after the fix, 50 tests (green_touched_gil0.txt); repro before and after.\n"
    "- 0.2.8204 on the VM copy: every tests/ tree green on 3.14t GIL off (tests/unit/github_workflows not\n"
    "  collectable there: no PyYAML); conduit set plus probe consumers 2442 passed with the GIL on and on the GIL\n"
    "  build (suites_0_2_8204_vm.txt).\n"
    "- Final after the rebuilds: version/asset/system-document set 288 passed, 1 skipped, on all three; conduit\n"
    "  set 2442 on GIL off (suites_final_0_2_8204_vm.txt). Asset --check OK; LLM --check OK with\n"
    "  --include-untracked.\n"
    "- Benchmarks: not run - the probe is not on the meld path (FACT note 2026-09-28T00:32:23Z).\n"
    "- Coverage: Not run.\n",
)
swap(
    "  - system_docs/patches/active/spellspace_probe_many_2026_09_28/architecture_patch.md\n"
    "  - system_docs/patches/active/spellspace_probe_many_2026_09_28/component_patch_meld_resolution_runtime.md\n"
    "- DISPOSITION: retain_as_reference\n",
    "  - system_docs/patches/completed/spellspace_probe_many_2026_09_28/architecture_patch.md\n"
    "  - system_docs/patches/completed/spellspace_probe_many_2026_09_28/component_patch_meld_resolution_runtime.md\n"
    "- DISPOSITION: retain_as_reference (artifacts); promote_to_documentation (patch lane, archived to completed)\n",
)
start = text.index("## Context / Handoff Summary\n")
end = text.index("## Project-Specific Additions\n")
summary = (
    "## Context / Handoff Summary\n"
    "State (2026-09-28): done. At 0.2.8204 the SpellSpace door's live-creation probe reads `many` from the space's\n"
    "own store - where every emitter registers a disposal-bearing `many` melded through a space and where the\n"
    "space's purge retires it - and reports \"spellspace_many\" with the space id; it no longer counts the owner\n"
    "conduit's `many`. The conduit probe, storage routing and the meld path are unchanged. Docs (src_components,\n"
    "including two corrected Meld runtime claims), graph, release note, assets and bundles are current; suites\n"
    "green on three interpreters. Follow-ups for the owner, not done here: the ConduitMeld probe contract's\n"
    "lifetime wording (docstring only), the tool paths in the system docs' `## Indexing` sections, and fable_0's\n"
    "stale Meld, ConduitMeld and Spellbook graph nodes.\n"
    "\n"
)
text = text[:start] + summary + text[end:]
for line in text.split("\n"):
    if len(line) > 120:
        assert " " not in line.strip().lstrip("- ").split(":")[0], line
path.write_bytes(text.encode("utf-8"))
print("ticket closed in place")
