"""melder_0, 2026-10-18: re-wrap the bullet blocks a fragment replacement left over 120 characters (the hard cap),
keeping this session's evidence ranges true through `Record.resync`."""
import pathlib
import sys
import textwrap

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from cc_record import Record


class Reflow(Record):
    """Re-wrap every top-level bullet block holding a prose line over the cap, in the given files."""

    WIDTH = 116

    def reflow(self, rel: str) -> None:
        lines = self.read(rel).split("\n")
        out = []
        i = 0
        while i < len(lines):
            line = lines[i]
            if line.startswith("- "):
                end = i + 1
                while end < len(lines) and lines[end].startswith("  ") and not lines[end].lstrip().startswith("- "):
                    end += 1
                block = lines[i:end]
                long_prose = [b for b in block if len(b) > 120 and "context_compass/" not in b]
                if long_prose:
                    words = " ".join(part.strip() for part in block)[2:]
                    block = textwrap.wrap(words, width=self.WIDTH, initial_indent="- ", subsequent_indent="  ",
                                          break_long_words=False, break_on_hyphens=False)
                    print(f"reflow {rel}:{i + 1}-{end} -> {len(block)} lines")
                out.extend(block)
                i = end
                continue
            out.append(line)
            i += 1
        self.stage(rel, "\n".join(out))


def main() -> None:
    record = Reflow("reflow")
    for rel in (record.PATCHES + "/architecture_patch.md", record.PATCHES + "/component_patch_binding_pipeline.md",
                record.S2):
        record.reflow(rel)
    record.resync()
    record.flush()


if __name__ == "__main__":
    main()
