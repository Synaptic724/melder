"""Shared helpers for melder_0's staged, all-or-nothing record passes over Context Compass files (2026-10-18).

`Record` stages read-modify-write edits and flushes them only when every anchor matched once, every new line
fits 120 characters and no text holds a CR. `resync` keeps the evidence ranges written this session true when an
edit above a cited block moves it: a ticket-note citation follows its note (by its first four lines), a
patch-doc citation follows its block (by its first line and its bullet or numbered extent).
"""
import datetime
import pathlib
import re
import shutil
import sys
from typing import Dict, List, Optional, Tuple


class Record:
    """One staged pass; subclasses add the edits."""

    REPO = pathlib.Path.home() / "mnt/melder_private"
    ROOT = REPO / "context_compass"
    BACKUP = pathlib.Path("/tmp/m0_mq/bak_t6")
    EPIC = "tickets/epics/2026-10-18_spell_identity_is_the_code_epic.md"
    S1 = "tickets/stories/2026-10-18_spell_id_hashes_the_object_code_story.md"
    S2 = "tickets/stories/2026-10-18_binding_manifest_hash_story.md"
    S3 = "tickets/stories/2026-10-18_revalidate_on_binding_change_story.md"
    S4 = "tickets/stories/2026-10-18_one_registration_per_object_story.md"
    S5 = "tickets/stories/2026-10-18_spell_id_migration_story.md"
    BOARD = "attention_board.md"
    ARTIFACTS = "artifact_board.md"
    MAILBOX = "mailbox_board.md"
    PATCHES = "system_docs/patches/active/spell_identity_is_the_code_2026_10_18"
    FAMILY = (EPIC, S1, S2, S3, S4, S5)
    SESSION_NOTES = ("2026-10-18T16:18:35Z", "2026-10-18T16:24:12Z", "2026-10-18T16:32:46Z",
                     "2026-10-18T17:05:55Z", "2026-10-18T17:23:22Z")

    def __init__(self, label: str) -> None:
        self.now = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        self.label = label
        self.staged: Dict[str, str] = {}
        self.original: Dict[str, str] = {}

    def read(self, rel: str) -> str:
        if rel in self.staged:
            return self.staged[rel]
        return (self.ROOT / rel).read_text(encoding="utf-8")

    def stage(self, rel: str, text: str) -> None:
        if rel not in self.original and (self.ROOT / rel).exists():
            self.original[rel] = (self.ROOT / rel).read_text(encoding="utf-8")
        self.staged[rel] = text

    @staticmethod
    def check_width(block: str, label: str) -> None:
        for line in block.split("\n"):
            if len(line) > 120 and "context_compass/" not in line and not line.startswith("| ") \
                    and not line.startswith("|---"):
                sys.exit(f"WIDTH {label}: {len(line)}: {line}")

    def once(self, text: str, old: str, new: str, label: str) -> str:
        count = text.count(old)
        if count != 1:
            sys.exit(f"ANCHOR {label}: found {count}")
        self.check_width(new, label)
        return text.replace(old, new)

    def set_field(self, rel: str, field: str) -> None:
        """Set the single `- <field>: <value>` metadata line of a file to now."""
        text = self.read(rel)
        found = re.findall(rf"^- {re.escape(field)}: \S+$", text, flags=re.M)
        if len(found) != 1:
            sys.exit(f"FIELD {field} in {rel}: {len(found)}")
        self.stage(rel, text.replace(found[0], f"- {field}: {self.now}"))

    def whole(self, rel: str) -> str:
        count = len(self.read(rel).rstrip("\n").split("\n"))
        return f"context_compass/{rel}:1-{count}"

    def doc_block(self, rel: str, first: str) -> str:
        """`context_compass/rel:a-b` of the bullet or numbered block whose first line starts with `first`."""
        lines = self.read(rel).split("\n")
        starts = [i for i, line in enumerate(lines) if line.startswith(first)]
        if len(starts) != 1:
            sys.exit(f"BLOCK {rel} {first}: {len(starts)}")
        end = self.block_end(lines, starts[0])
        return f"context_compass/{rel}:{starts[0] + 1}-{end + 1}"

    def doc_section(self, rel: str, heading: str) -> str:
        lines = self.read(rel).split("\n")
        starts = [i for i, line in enumerate(lines) if line == heading]
        if len(starts) != 1:
            sys.exit(f"HEADING {heading}: {len(starts)}")
        end = starts[0] + 1
        while end < len(lines) and not lines[end].startswith("## "):
            end += 1
        while lines[end - 1].strip() == "":
            end -= 1
        return f"context_compass/{rel}:{starts[0] + 1}-{end}"

    @staticmethod
    def block_end(lines: List[str], start: int) -> int:
        end = start
        while end + 1 < len(lines):
            nxt = lines[end + 1]
            if nxt.strip() == "" or nxt.startswith("- ") or nxt.startswith("#") or nxt.startswith("|") \
                    or re.match(r"^\d+\. ", nxt):
                break
            end += 1
        return end

    def note_range(self, rel: str, marker: str, type_line: str) -> str:
        lines = self.read(rel).split("\n")
        hits = [i for i, line in enumerate(lines)
                if line == marker and i + 3 < len(lines) and lines[i + 3] == type_line]
        if len(hits) != 1:
            sys.exit(f"NOTE {rel} {marker} {type_line}: found {len(hits)}")
        end = hits[0] + 1
        while end < len(lines) and lines[end] != "":
            end += 1
        return f"context_compass/{rel}:{hits[0] + 1}-{end}"

    @staticmethod
    def note(now: str, kind: str, claim: List[str], evidence: List[str], impact: List[str], nxt: List[str],
             reread: str, score: int) -> str:
        lines = [f"- DATETIME: {now}", "  AUTHOR: melder_0", "  AUTHOR_ROLE: synaptic_python_developer",
                 f"  TYPE: {kind}", "  CLAIM: " + claim[0]] + ["    " + c for c in claim[1:]]
        if len(evidence) == 1 and len("  EVIDENCE: " + evidence[0]) <= 120:
            lines.append("  EVIDENCE: " + evidence[0])
        else:
            lines += ["  EVIDENCE:"] + [f"  - {e}" for e in evidence]
        lines += ["  IMPACT: " + impact[0]] + ["    " + c for c in impact[1:]]
        lines += ["  NEXT: " + nxt[0]] + ["    " + c for c in nxt[1:]]
        lines += [f"  REREAD: {reread}", f"  SCORE_0_TO_10: {score}"]
        return "\n".join(lines)

    def append_notes(self, rel: str, notes: List[str], label: str) -> None:
        text = self.read(rel)
        text = self.once(text, "\n\n## Closure Confirmation\n",
                         "\n\n" + "\n\n".join(notes) + "\n\n## Closure Confirmation\n", label)
        self.stage(rel, text)

    @staticmethod
    def _note_spans(text: str) -> Dict[Tuple[int, int], Tuple[str, ...]]:
        lines = text.split("\n")
        spans = {}
        for i, line in enumerate(lines):
            if line.startswith("- DATETIME: ") and i + 3 < len(lines):
                end = i + 1
                while end < len(lines) and lines[end] != "":
                    end += 1
                spans[(i + 1, end)] = tuple(lines[i:i + 4])
        return spans

    def _relocate_doc(self, old: str, new: str, a: int, b: int) -> Optional[Tuple[int, int]]:
        old_lines = old.split("\n")
        new_lines = new.split("\n")
        block = old_lines[a - 1:b]
        if not block:
            return None
        hits = [i for i, line in enumerate(new_lines) if line == block[0]]
        if len(hits) != 1:
            return None
        start = hits[0]
        if new_lines[start:start + len(block)] == block:
            return (start + 1, start + len(block))
        return (start + 1, self.block_end(new_lines, start) + 1)

    def resync(self) -> None:
        """Move this session's citations into edited files to where their targets now stand."""
        moved = {rel for rel in self.staged if rel in self.original}
        for holder in self.FAMILY:
            text = self.read(holder)
            lines = text.split("\n")
            changed = False
            note_start = None
            for i, line in enumerate(lines):
                if line.startswith("- DATETIME: "):
                    note_start = line[len("- DATETIME: "):]
                elif line == "":
                    note_start = None
                # Only notes of earlier passes: this pass's citations are computed from the staged text.
                if note_start not in self.SESSION_NOTES:
                    continue
                for match in re.finditer(r"context_compass/(\S+?):(\d+)-(\d+)", line):
                    rel, a, b = match.group(1), int(match.group(2)), int(match.group(3))
                    if rel not in moved:
                        continue
                    old, new = self.original[rel], self.staged[rel]
                    if rel.startswith("tickets/"):
                        key = self._note_spans(old).get((a, b))
                        if key is None:
                            continue
                        target = {v: k for k, v in self._note_spans(new).items()}.get(key)
                    else:
                        target = self._relocate_doc(old, new, a, b)
                    if target is None or target == (a, b):
                        continue
                    replacement = f"context_compass/{rel}:{target[0]}-{target[1]}"
                    lines[i] = lines[i].replace(match.group(0), replacement)
                    print(f"resync {holder}: {rel}:{a}-{b} -> {target[0]}-{target[1]}")
                    changed = True
            if changed:
                self.stage(holder, "\n".join(lines))

    def flush(self) -> None:
        for rel, text in self.staged.items():
            if "\r" in text:
                sys.exit(f"CR in {rel}")
        self.BACKUP.mkdir(parents=True, exist_ok=True)
        for rel, text in self.staged.items():
            path = self.ROOT / rel
            if path.exists():
                shutil.copy2(path, self.BACKUP / (pathlib.Path(rel).name + ".pre_" + self.label))
            path.write_text(text, encoding="utf-8", newline="\n")
            print("wrote", rel)
