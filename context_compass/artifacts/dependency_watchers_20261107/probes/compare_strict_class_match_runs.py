"""
Compare two junit XML runs of the suite: matching as shipped against strict class matching.

Owner: TASK-2026-11-07-inventory_class_resolution_of_framed_spells (T1), melder_0.

Purpose:
    Turn the two runs `run_strict_class_match_suite.sh` writes into T1's test list: every
    test whose outcome differs between the shipped run and the strict run, grouped by
    file, with the first line of the strict run's failure message.

Usage:
    python compare_strict_class_match_runs.py <shipped.xml> <strict.xml>

Output:
    Plain text on stdout: per-mode outcome counts, then each differing test as
    `<shipped outcome> -> <strict outcome>  <node>` with its message beneath, grouped by
    file. A test present in one run only is listed as `absent` on the other side.
"""
import sys
import xml.etree.ElementTree as ElementTree
from collections import Counter
from typing import Dict, List, Tuple


class JunitOutcomes:
    """
    The per-test outcomes of one junit XML file.

    Contract:
        - A test is keyed `<classname>::<name>` as pytest writes them.
        - Outcome: `failed` (a <failure>), `error` (an <error>), `xfailed` (a <skipped>
          of type pytest.xfail), `skipped` (any other <skipped>), else `passed`.
        - The message is the first line of the failure, error or skip message, or "".
    """

    def __init__(self, path: str) -> None:
        """
        Parse one junit XML file.

        Args:
            path: The file to read.

        Raises:
            xml.etree.ElementTree.ParseError: The file is not well-formed XML.
        """
        self.path: str = path
        self.outcomes: Dict[str, Tuple[str, str]] = {}
        root = ElementTree.parse(path).getroot()
        for case in root.iter("testcase"):
            key = f"{case.get('classname', '')}::{case.get('name', '')}"
            self.outcomes[key] = self._outcome_of(case)

    @staticmethod
    def _outcome_of(case: ElementTree.Element) -> Tuple[str, str]:
        """
        Classify one <testcase> element.

        Args:
            case: The element.

        Returns:
            Tuple[str, str]: The outcome and the first line of its message.
        """
        for tag, outcome in (("failure", "failed"), ("error", "error")):
            child = case.find(tag)
            if child is not None:
                return outcome, JunitOutcomes._first_line(child)
        skipped = case.find("skipped")
        if skipped is not None:
            if skipped.get("type", "") == "pytest.xfail":
                return "xfailed", JunitOutcomes._first_line(skipped)
            return "skipped", JunitOutcomes._first_line(skipped)
        return "passed", ""

    @staticmethod
    def _first_line(element: ElementTree.Element) -> str:
        """
        Return the first non-empty line of an element's message attribute or text.

        Args:
            element: A failure, error or skipped element.

        Returns:
            str: The line, or "".
        """
        text = element.get("message") or element.text or ""
        for line in text.splitlines():
            if line.strip():
                return line.strip()[:400]
        return ""


def compare(shipped: JunitOutcomes, strict: JunitOutcomes) -> List[str]:
    """
    Render the comparison report.

    Args:
        shipped: The run with matching as shipped.
        strict: The run with the strict class rule.

    Returns:
        List[str]: The report lines.
    """
    lines: List[str] = []
    for label, run in (("shipped", shipped), ("strict", strict)):
        counts = Counter(outcome for outcome, _ in run.outcomes.values())
        rendered = ", ".join(f"{name} {counts[name]}" for name in sorted(counts))
        lines.append(f"{label}: {len(run.outcomes)} tests - {rendered} ({run.path})")
    differing: Dict[str, List[str]] = {}
    for key in sorted(set(shipped.outcomes) | set(strict.outcomes)):
        before = shipped.outcomes.get(key, ("absent", ""))
        after = strict.outcomes.get(key, ("absent", ""))
        if before[0] == after[0]:
            continue
        file_part = key.split("::", 1)[0]
        entry = f"  {before[0]} -> {after[0]}  {key}"
        message = after[1] or before[1]
        if message:
            entry += f"\n      {message}"
        differing.setdefault(file_part, []).append(entry)
    total = sum(len(entries) for entries in differing.values())
    lines.append(f"differing tests: {total} in {len(differing)} files")
    for file_part in sorted(differing):
        lines.append(file_part)
        lines.extend(differing[file_part])
    return lines


def main(argv: List[str]) -> int:
    """
    Compare the two runs named on the command line.

    Args:
        argv: `[script, shipped.xml, strict.xml]`.

    Returns:
        int: 0 on success, 2 on a usage error.
    """
    if len(argv) != 3:
        print("usage: compare_strict_class_match_runs.py <shipped.xml> <strict.xml>", file=sys.stderr)
        return 2
    report = compare(JunitOutcomes(argv[1]), JunitOutcomes(argv[2]))
    print("\n".join(report))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
