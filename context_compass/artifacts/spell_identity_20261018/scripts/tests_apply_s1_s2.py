"""melder_0, 2026-10-18: apply the S1 and S2 test changes of EPIC-2026-10-18-spell_identity_is_the_code to a root.

The same edit lists run against the /tmp working mirror (where the tests are run, the GIL off and on) and, at the
landing, against the repository. Anchored and all-or-nothing (`apply_common.Applier`); new test modules are copied
from the staged folder.

    python3 tests_apply_s1_s2.py --root /tmp/m0_mq/wt [--check] [--batch doubles ...]
"""
import argparse
import pathlib
import sys
from typing import Callable, Dict, List, Tuple

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from apply_common import Applier


class TestApplier(Applier):
    """Applier with a counted replace-all for anchors a file repeats on purpose."""

    def edit_all(self, rel: str, old: str, new: str, expected: int, label: str) -> None:
        """Replace every `old` in one file, refusing unless it occurs exactly `expected` times."""
        text = self._load(rel)
        count = text.count(old)
        if count != expected:
            self.errors.append(f"ANCHOR-ALL {label} in {rel}: found {count}, expected {expected}: {old[:70]!r}")
            return
        self.texts[rel] = text.replace(old, new)
        self.counts[rel] = self.counts.get(rel, 0) + count

    def edit_preserving(self, rel: str, pairs: List[Tuple[str, str]], label: str) -> None:
        """
        Edit a file whose committed copy mixes CRLF and LF lines (git i/mixed) without normalizing it.

        Each `old`, written with LF, is matched in its CRLF form exactly once and replaced by `new` in CRLF, so only
        the lines it replaces change and every other line keeps its own ending. Anchors must lie in CRLF lines.
        """
        if rel not in self.texts:
            raw = (self.root / rel).read_bytes().decode("utf-8")
            self.texts[rel] = raw
            self.originals[rel] = raw
            # The text keeps its own endings, so writing maps nothing.
            self.newline[rel] = "\n"
        text = self.texts[rel]
        for index, (old, new) in enumerate(pairs):
            old_crlf = old.replace("\n", "\r\n")
            count = text.count(old_crlf)
            if count != 1:
                self.errors.append(f"ANCHOR {label}#{index} in {rel}: found {count}: {old[:70]!r}")
                continue
            text = text.replace(old_crlf, new.replace("\n", "\r\n"))
            self.counts[rel] = self.counts.get(rel, 0) + 1
        self.texts[rel] = text


def batches() -> Dict[str, Callable[[TestApplier], None]]:
    """The edit batches in landing order; each module exposes `apply(applier)`."""
    import tests_edits_bind
    import tests_edits_component_bind
    import tests_edits_doubles
    import tests_edits_fingerprint
    import tests_edits_inherited
    import tests_edits_lifecycle_hooks
    import tests_edits_managed
    import tests_edits_new_tests
    import tests_edits_ordered_disposal
    import tests_edits_ordered_replay
    import tests_edits_one_object_a
    import tests_edits_one_object_b
    import tests_edits_profile_strategy
    import tests_edits_resolvable_registration
    return {
        "doubles": tests_edits_doubles.apply,
        "bind": tests_edits_bind.apply,
        "managed": tests_edits_managed.apply,
        "fingerprint": tests_edits_fingerprint.apply,
        "profile_strategy": tests_edits_profile_strategy.apply,
        "component_bind": tests_edits_component_bind.apply,
        "lifecycle_hooks": tests_edits_lifecycle_hooks.apply,
        "inherited": tests_edits_inherited.apply,
        "ordered_disposal": tests_edits_ordered_disposal.apply,
        "resolvable_registration": tests_edits_resolvable_registration.apply,
        "ordered_replay": tests_edits_ordered_replay.apply,
        "one_object_a": tests_edits_one_object_a.apply,
        "one_object_b": tests_edits_one_object_b.apply,
        "new_tests": tests_edits_new_tests.apply,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", required=True)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--backup", default="/tmp/m0_mq/bak_tests")
    parser.add_argument("--batch", nargs="*", default=None)
    args = parser.parse_args()
    applier = TestApplier(pathlib.Path(args.root).expanduser(), pathlib.Path(args.backup))
    for name, apply in batches().items():
        if args.batch is None or name in args.batch:
            apply(applier)
    applier.commit(args.check)


if __name__ == "__main__":
    main()
