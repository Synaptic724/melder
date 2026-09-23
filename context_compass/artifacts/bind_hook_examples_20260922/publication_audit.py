"""Verify new lesson downloads and consolidate the bounded example reruns."""

import hashlib
import json
from pathlib import Path
import sys
import xml.etree.ElementTree as ET
import zipfile


def main() -> None:
    """Check byte fidelity and record final per-example outcomes without rerunning tests."""
    root = Path.cwd()
    artifacts = root / "context_compass/artifacts/bind_hook_examples_20260922"
    lessons = (
        ("intermediate", "02_intermediate", "40_bind_lifecycle_hooks.py"),
        ("expert", "04_expert", "37_review_agent_bindings.py"),
    )
    verified: list[dict[str, str]] = []
    for level, directory, filename in lessons:
        source = Path("UX_and_AIX_experiences") / directory / filename
        expected = (root / source).read_bytes()
        page = f"examples/{level}/{Path(filename).stem.replace('_', '-')}.html"
        assert (root / "docs/_build/html" / page).is_file(), page
        for output in ("source", "html"):
            downloads = root / "docs/_build" / output / "downloads"
            assert (downloads / directory / filename).read_bytes() == expected
            with zipfile.ZipFile(downloads / f"{level}-examples.zip") as bundle:
                assert bundle.read(source.as_posix()) == expected
        verified.append({"source": source.as_posix(), "page": page,
                         "sha256": hashlib.sha256(expected).hexdigest()})

    outcomes: dict[tuple[str, str], str] = {}
    for filename in ("tier_examples.xml", "followup.xml", "protocol_temp_retry.xml"):
        for case in ET.parse(artifacts / filename).iter("testcase"):
            outcome = "passed"
            if case.find("failure") is not None or case.find("error") is not None:
                outcome = "failed"
            elif case.find("skipped") is not None:
                outcome = "skipped"
            outcomes[(case.attrib["classname"], case.attrib["name"])] = outcome
    assert len(outcomes) == 76, len(outcomes)
    assert all(outcome == "passed" for outcome in outcomes.values()), outcomes
    report = {"lessons": verified, "unique_examples_passed_across_runs": len(outcomes),
              "qualification_reports": ["tier_examples.xml", "followup.xml", "protocol_temp_retry.xml"],
              "hosted_publication": False}
    (artifacts / "publication_audit.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    sys.stdout.write(json.dumps(report, indent=2) + "\n")


if __name__ == "__main__":
    main()
