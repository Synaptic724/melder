"""Correct the disposal sentence beside the docs sweep's replay edit in configuration.md (melder_0, 2026-10-18).

The paragraph the docs sweep edited also says a failing disposal method stops the object's remaining methods. Since
0.2.80 every declared method runs and the failures are raised together (`Creations._attempt_cleanup`,
`Creations.cleanup`). One anchored edit on the CRLF page; `--write` writes, keeping the original in /tmp.
"""
import sys
from pathlib import Path


class DisposalSentence:
    """The one edit."""

    REL = "docs/intermediate/configuration.md"
    OLD = ("Existing scope/key/bucket teardown order is unchanged. Within one object, a\r\n"
           "method failure stops its remaining methods; other objects still receive cleanup.\r\n")
    NEW = ("Existing scope/key/bucket teardown order is unchanged. Within one object, every\r\n"
           "declared method runs even when an earlier one fails, and other objects still\r\n"
           "receive cleanup; the failures are raised together, as one `ExceptionGroup`, once\r\n"
           "cleanup ends.\r\n")

    def run(self, root: Path, write: bool) -> None:
        """Apply the edit once, or exit naming why not."""
        path = root / self.REL
        raw = path.read_bytes()
        text = raw.decode("utf-8")
        if text.count(self.OLD) != 1:
            sys.exit(f"ANCHOR {self.REL}: {text.count(self.OLD)}")
        out = text.replace(self.OLD, self.NEW).encode("utf-8")
        if not write:
            print("CHECK OK", self.REL)
            return
        backup = Path("/tmp/m0_mq/bak_docs_identity/configuration.md.pre_disposal_sentence")
        backup.parent.mkdir(parents=True, exist_ok=True)
        backup.write_bytes(raw)
        path.write_bytes(out)
        if path.read_bytes() != out:
            sys.exit("READBACK failed")
        print("WROTE", self.REL)


def main() -> None:
    DisposalSentence().run(Path(sys.argv[1]).resolve(), "--write" in sys.argv)


if __name__ == "__main__":
    main()
