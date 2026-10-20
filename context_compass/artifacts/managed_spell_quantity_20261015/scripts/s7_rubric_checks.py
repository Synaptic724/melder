"""S7 D7: the measurable half of the system-document quality rubric, for the four documents, from disk.

Per document: H1 count, duplicate section names, headings with an unclosed bracket, the required section contract
in order, portability and absolute-path hits, the C1 map (fields present, path exists, extent equal to the file's
line count today, verified_at), the Key Files join (source paths against the graph index; test paths by existence)
and, for the two component maps, the twelve entry fields of every C3/C2 entry with the ones that are thin (under 60
characters of content). Semantic scoring (fidelity, depth, mirror) is done by reading; this script only measures.
Run from the repository root: python <this file>
"""
import pathlib
import re
from collections import Counter

DOCS = pathlib.Path("context_compass/system_docs")
ARCH_CONTRACT = ["Metadata", "Scope and Intent", "Indexing", "DO NOT ASSUME / Unknowns Gate", "Unknowns",
                 "System Context (C4)", "System Boundary and External Interfaces", "Architecture Summary (C4)",
                 "Entrypoints and Runtime Guardrails", "Boot and Configuration Sequence", "Data Flows and Sequences",
                 "Operational Invariants", "Failure Modes and Error Paths", "C1 Code Map (Core Only)", "Diagrams",
                 "Information Sources", "Context / Handoff Summary"]
COMP_CONTRACT = ["Metadata", "Scope", "Indexing", "DO NOT ASSUME / Unknowns Gate", "Unknowns", "C3 Components Catalog",
                 "C2 Subcomponents Catalog", "Method-Level Call Flows (C1)", "C1 Code Map (Core)", "Diagrams",
                 "Information Sources", "Context / Handoff Summary"]
FIELDS = ["Purpose", "Responsibilities", "Inputs", "Outputs", "Owned State", "Lifecycle/Cleanup",
          "Concurrency/Threading", "Invariants/Guarantees", "Failure Modes", "Observability", "Extension Points",
          "Key Files (C1)"]
PORTABILITY = re.compile(r"context_compass/|agent_onboarding/|tools/system_documents/|index_document\.py|system_docs/|"
                         r"patches/active/")
ABSOLUTE = re.compile(r"([A-Za-z]:\\\\|^\s*-?\s*path:\s*[`']?/)")
UNCLOSED = re.compile(r"^#{1,6} .*[(\[][^)\]]*$")


def headings(lines):
    """(line number, level, text) of every heading outside fenced code."""
    out, fence = [], None
    for number, line in enumerate(lines, 1):
        stripped = line.strip()
        marker = re.match(r"^(`{3,}|~{3,})", stripped)
        if marker:
            if fence is None:
                fence = marker.group(1)
            elif stripped.startswith(fence):
                fence = None
            continue
        if fence is None:
            m = re.match(r"^(#{1,6}) (.*)$", line)
            if m:
                out.append((number, len(m.group(1)), m.group(2).strip()))
    return out


def file_lines(path):
    """Line count of a file as splitlines() counts it."""
    return len(pathlib.Path(path).read_bytes().decode("utf-8", "replace").splitlines())


def c1_entries(lines):
    """Parse `- path:` records with their four fields."""
    entries, i = [], 0
    while i < len(lines):
        m = re.match(r"^\s*-\s*path:\s*`([^`]+)`", lines[i])
        if m:
            record = {"path": m.group(1), "line": i + 1}
            for j in range(i + 1, min(i + 8, len(lines))):
                if re.match(r"^\s*-\s*path:", lines[j]):
                    break
                f = re.match(r"^\s*(start_line|end_line|loc|verified_at):\s*(\S+)", lines[j])
                if f:
                    record[f.group(1)] = f.group(2)
            entries.append(record)
        i += 1
    return entries


def graph_sources():
    """Source paths keyed in the graph index."""
    text = (DOCS / "src_graph_index.md").read_text(encoding="utf-8")
    return set(re.findall(r"^\| [0-9]+-[0-9]+ \| `([^`]+)`", text, re.M))


def entries_fields(lines, hs):
    """Field presence and size for every '### Component:' / '### Subcomponent:' entry."""
    units = [(n, t) for n, lvl, t in hs if lvl == 3 and re.match(r"Component: ", t)]
    ends = [n for n, lvl, t in hs]
    report = []
    for n, title in units:
        later = [e for e in ends if e > n]
        end = (later[0] - 1) if later else len(lines)
        body = lines[n:end]
        sizes, current = {}, None
        for line in body:
            label = re.match(r"^\s*-?\s*\**(" + "|".join(re.escape(f) for f in FIELDS) + r")\**:\s*(.*)$", line)
            if label:
                current = label.group(1)
                sizes[current] = sizes.get(current, 0) + len(label.group(2).strip())
            elif current:
                sizes[current] += len(line.strip())
        missing = [f for f in FIELDS if f not in sizes]
        thin = [f for f in FIELDS if f in sizes and sizes[f] < 60]
        report.append((n, title, missing, thin))
    return report


def check(name, contract, component):
    """Print the measured facts of one document."""
    lines = (DOCS / name).read_bytes().decode("utf-8").split("\n")
    if lines and lines[-1] == "":
        lines.pop()
    hs = headings(lines)
    print(f"=== {name}: {len(lines)} lines, {len(hs)} headings")
    print("H1:", sum(1 for _, lvl, _ in hs if lvl == 1))
    names = Counter(t for _, lvl, t in hs if lvl in (2, 3))
    dups = {t: c for t, c in names.items() if c > 1}
    deep = Counter(t for _, lvl, t in hs if lvl >= 4)
    print("duplicate indexed (H2/H3) names:", dups or "none", "| repeated H4+ texts (not indexed):",
          {t[:60]: c for t, c in deep.items() if c > 1} or "none")
    print("unclosed-bracket headings:", [n for n, lvl, t in hs if UNCLOSED.match("#" * lvl + " " + t)] or "none")
    h2 = [t for _, lvl, t in hs if lvl == 2]
    positions = [h2.index(c) if c in h2 else None for c in contract]
    missing = [c for c, p in zip(contract, positions) if p is None]
    present = [p for p in positions if p is not None]
    print("contract missing:", missing or "none", "| in order:", present == sorted(present),
          "| extra H2:", [t for t in h2 if t not in contract])
    port = [(i + 1, m.group(0)) for i, line in enumerate(lines) for m in [PORTABILITY.search(line)] if m]
    print("portability hits:", port or "none")
    absolute = [(i + 1, line.strip()[:60]) for i, line in enumerate(lines) if ABSOLUTE.search(line)]
    print("absolute-path hits:", absolute or "none")
    entries = c1_entries(lines)
    bad_fields = [e["line"] for e in entries if not all(k in e for k in ("start_line", "end_line", "loc",
                                                                         "verified_at"))]
    missing_files = [e["path"] for e in entries if not pathlib.Path(e["path"]).is_file()]
    drift = [(e["path"], e.get("end_line"), file_lines(e["path"])) for e in entries
             if pathlib.Path(e["path"]).is_file() and "end_line" in e
             and e.get("start_line") == "1" and int(e["end_line"]) != file_lines(e["path"])]
    stamps = Counter((e.get("verified_at") or "")[:10] for e in entries)
    print(f"C1 records: {len(entries)}; incomplete: {bad_fields or 'none'}; missing files: {missing_files or 'none'};"
          f" extent drift: {drift or 'none'}")
    print("C1 verified_at by day:", dict(sorted(stamps.items())))
    cited = set()
    for i, line in enumerate(lines):
        if "Key Files (C1):" in line:
            cited.update(re.findall(r"`([^`]*)`", line))
            j = i + 1
            while j < len(lines) and re.match(r"^\s*-\s+`", lines[j]):
                cited.update(re.findall(r"`([^`]*)`", lines[j]))
                j += 1
    cited = {c for c in cited if not re.search(r"[*?]", c) and "/" in c}
    if name == "src_architecture.md":
        c1_src = {e["path"] for e in entries if e["path"].startswith("src/") and e["path"].endswith(".py")}
        print(f"C1 source paths: {len(c1_src)}; not in the graph index: {sorted(c1_src - graph_sources()) or 'none'}")
    if name.startswith("src_"):
        unresolved = sorted(c for c in cited if c.startswith("src/") and c not in graph_sources())
        print(f"Key Files citations: {len(cited)} paths; not in the graph index: {unresolved or 'none'}")
    else:
        absent = sorted(c for c in cited if not pathlib.Path(c).exists())
        print(f"Key Files citations: {len(cited)} paths; missing on disk: {absent or 'none'}")
    if component:
        report = entries_fields(lines, hs)
        incomplete = [(n, t[:50], m) for n, t, m, _ in report if m]
        thin = Counter(f for _, _, _, th in report for f in th)
        print(f"C3 entries: {len(report)}; with a missing field: {len(incomplete)}; thin fields by name: {dict(thin)}")
        for n, t, _, th in report:
            if th:
                print("   thin", n, t[:60], th)
        for n, t, m in incomplete[:12]:
            print("   missing", n, t, m)


check("src_architecture.md", ARCH_CONTRACT, False)
check("tests_architecture.md", ARCH_CONTRACT, False)
check("src_components.md", COMP_CONTRACT, True)
check("tests_components.md", COMP_CONTRACT, True)
