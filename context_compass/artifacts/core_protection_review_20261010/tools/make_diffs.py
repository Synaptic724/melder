"""Build per-lane diffs (line endings normalized) and a SHA256 manifest for the hand-back evidence packs.

melder_1, 2026-10-10. Run from anywhere on the device VM after the turn-in moves and the final rebuild:
    python make_diffs.py
It reads HEAD blobs with read-only git (GIT_OPTIONAL_LOCKS=0) and writes each lane's diffs/ and
file_manifest.md into its evidence pack. The tests_components split uses the review lane's preservation
baseline (the state after scan_bind, 09:49Z), kept outside the repository.
"""
import collections, difflib, hashlib, os, re, subprocess, sys
REPO = os.path.expanduser("~/mnt/melder_private")
ART = os.path.join(REPO, "context_compass", "artifacts")
OUT_DIRS = {"scan_bind": os.path.join(ART, "scan_bind_option_parity_20261010"),
            "review": os.path.join(ART, "core_protection_review_20261010")}
os.chdir(REPO)
env = dict(os.environ, GIT_OPTIONAL_LOCKS="0")

def head_text(path):
    proc = subprocess.run(["git", "cat-file", "-p", "HEAD:" + path], capture_output=True, env=env)
    if proc.returncode != 0:
        return None
    return proc.stdout.replace(b"\r\n", b"\n").decode("utf-8")

def work_text(path):
    with open(path, "rb") as fh:
        return fh.read().replace(b"\r\n", b"\n").decode("utf-8")

def udiff(old, new, path, old_label=None, new_label=None):
    old_lines = [] if old is None else old.splitlines(keepends=True)
    new_lines = [] if new is None else new.splitlines(keepends=True)
    a = old_label or ("/dev/null" if old is None else "a/" + path)
    b = new_label or ("/dev/null" if new is None else "b/" + path)
    out = list(difflib.unified_diff(old_lines, new_lines, a, b, n=3))
    return "".join(line if line.endswith("\n") else line + "\n\\ No newline at end of file\n" for line in out)

def numstat(old, new):
    old_lines = [] if old is None else old.splitlines()
    new_lines = [] if new is None else new.splitlines()
    sm = difflib.SequenceMatcher(a=old_lines, b=new_lines, autojunk=False)
    added = removed = 0
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag in ("replace", "delete"):
            removed += i2 - i1
        if tag in ("replace", "insert"):
            added += j2 - j1
    return added, removed

def sha256(path):
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()

LANES = {
    "scan_bind": {
        "authored": [
            "src/melder/aether/spellbook/bind/scan.py",
            "src/melder/aether/spellbook/spellbook.py",
            "src/melder/__version__.py",
            "README.md",
            "release_docs/next_version_release.md",
            "context_compass/system_docs/src_architecture.md",
            "context_compass/system_docs/src_components.md",
            "context_compass/system_docs/graph/melder/aether/spellbook/bind/scan.json",
            "context_compass/system_docs/graph/melder/aether/spellbook/spellbook.json",
            "tests/unit/melder/spellbook/test_scan_bind_option_parity.py",
            "tests/component/melder/spellbook/test_scan_bind_parity_component.py",
            "context_compass/system_docs/patches/completed/scan_bind_option_parity_2026_10_10/architecture_patch.md",
            "context_compass/system_docs/patches/completed/scan_bind_option_parity_2026_10_10/component_patch_scan_bind.md",
            "context_compass/system_docs/patches/completed/scan_bind_option_parity_2026_10_10/code_description_patch_scan_module.md",
        ],
        "generated": [
            "context_compass/system_docs/src_architecture_index.md",
            "context_compass/system_docs/src_components_index.md",
            "context_compass/system_docs/src_graph.md",
            "context_compass/system_docs/src_graph_index.md",
            "context_compass/system_docs/graph/melder/_build_assets/_agent_documentation/manifest/agent_documentation_manifest.json",
            "context_compass/system_docs/graph/melder/_build_assets/_bind_guard/manifest/bind_guard_manifest.json",
            "context_compass/system_docs/graph/melder/_build_assets/_system_documents/manifest/graph_adjacency_manifest.json",
            "context_compass/system_docs/graph/melder/_build_assets/_system_documents/manifest/system_documents_index.json",
            "context_compass/system_docs/graph/melder/_build_assets/_system_documents/manifest/system_documents_manifest.json",
            "context_compass/system_docs/graph/melder/_build_assets/_system_documents/payloads/src_architecture_payload.json",
            "context_compass/system_docs/graph/melder/_build_assets/_system_documents/payloads/src_components_payload.json",
            "context_compass/system_docs/graph/melder/_build_assets/_system_documents/payloads/src_graph_payload.json",
            "src/melder/_build_assets/_agent_documentation/manifest/agent_documentation_manifest.py",
            "src/melder/_build_assets/_bind_guard/manifest/bind_guard_manifest.py",
            "src/melder/_build_assets/_system_documents/manifest/graph_adjacency_manifest.py",
            "src/melder/_build_assets/_system_documents/manifest/system_documents_index.py",
            "src/melder/_build_assets/_system_documents/manifest/system_documents_manifest.py",
            "src/melder/_build_assets/_system_documents/payloads/src_architecture_payload.py",
            "src/melder/_build_assets/_system_documents/payloads/src_components_payload.py",
            "src/melder/_build_assets/_system_documents/payloads/src_graph_payload.py",
            "llm_support/llm_full_src.txt",
            "llm_support/llm_full_src_index.md",
            "llm_support/llm_full_other.txt",
            "llm_support/llm_full_other_index.md",
        ],
    },
    "review": {
        "authored": [
            "tests/unit/melder/crystallizer/crystal_analysis/test_custody_boundary_characterization.py",
            "tests/unit/melder/spellbook/bind/test_internal_registration_identity.py",
            "tests/integration/melder/crystallizer/test_recorded_leaf_source_read_integration.py",
            "tests/integration/melder/mutation_research/test_research_lane_runtime_isolation_integration.py",
            "tests/integration/melder/aether/test_codegen_core_boundary_integration.py",
        ],
        "generated": [
            "context_compass/system_docs/tests_components_index.md",
            "llm_support/llm_full_tests.txt",
            "llm_support/llm_full_tests_index.md",
            "llm_support/manifest.json",
        ],
    },
}
summary = collections.defaultdict(list)
for lane, groups in LANES.items():
    lane_dir = os.path.join(OUT_DIRS[lane], "diffs")
    os.makedirs(lane_dir, exist_ok=True)
    combined = []
    for path in groups["authored"]:
        old, new = head_text(path), work_text(path)
        combined.append(udiff(old, new, path))
        added, removed = numstat(old, new)
        summary[lane].append(("authored", path, "new" if old is None else "modified", added, removed, sha256(path)))
    for path in groups["generated"]:
        old, new = head_text(path), work_text(path)
        added, removed = numstat(old, new) if os.path.getsize(path) < 3_000_000 else ("n/a", "n/a")
        summary[lane].append(("generated", path, "new" if old is None else "modified", added, removed, sha256(path)))
    with open(os.path.join(lane_dir, lane + "_authored.diff"), "w", encoding="utf-8", newline="\n") as fh:
        fh.write("".join(combined))
# tests_components.md: split between the lanes at the review lane's preservation baseline.
tc = "context_compass/system_docs/tests_components.md"
baseline = open(os.path.expanduser("~/cc_work/tests_components_before_t2.md"), "rb").read().replace(b"\r\n", b"\n").decode()
multiset = open(os.path.expanduser("~/cc_work/tc_before_t2.txt"), "rb").read().replace(b"\r\n", b"\n").decode()
def _uniq_counter(text):
    """Parse `uniq -c` output (count, one space, the whitespace-collapsed line) into a Counter."""
    counter = collections.Counter()
    for line in text.split("\n"):
        if not line.strip():
            continue
        match = re.match(r"^\s*(\d+) (.*)$", line)
        counter[match.group(2)] += int(match.group(1))
    return counter

def _collapsed_counter(text):
    """Collapse runs of blanks to one space, drop empty lines, count the rest (the multiset's own shape)."""
    counter = collections.Counter()
    for line in text.split("\n"):
        collapsed = re.sub(r"[ \t]+", " ", line)
        if collapsed.strip():
            counter[collapsed] += 1
    return counter

print("baseline .md matches the 11:44 preservation multiset:", _collapsed_counter(baseline) == _uniq_counter(multiset))
head_tc, work_tc = head_text(tc), work_text(tc)
with open(os.path.join(OUT_DIRS["scan_bind"], "diffs", "tests_components_scan_bind_part.diff"), "w", newline="\n") as fh:
    fh.write(udiff(head_tc, baseline, tc, "a/" + tc + " (HEAD)", "b/" + tc + " (after scan_bind, 09:49Z)"))
with open(os.path.join(OUT_DIRS["review"], "diffs", "tests_components_review_part.diff"), "w", newline="\n") as fh:
    fh.write(udiff(baseline, work_tc, tc, "a/" + tc + " (after scan_bind, 09:49Z)", "b/" + tc + " (final)"))
summary["scan_bind"].append(("authored", tc + " (scan_bind part)", "modified", *numstat(head_tc, baseline), "-"))
summary["review"].append(("authored", tc + " (review part)", "modified", *numstat(baseline, work_tc), sha256(tc)))
for lane, rows in summary.items():
    with open(os.path.join(OUT_DIRS[lane], "file_manifest.md"), "w", newline="\n") as fh:
        fh.write("| kind | path | status | +lines | -lines | sha256 (final bytes) |\n| --- | --- | --- | --- | --- | --- |\n")
        for row in rows:
            fh.write("| {0} | `{1}` | {2} | {3} | {4} | `{5}` |\n".format(*row))
    print(lane, len(rows), "rows")
