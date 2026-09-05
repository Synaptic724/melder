"""Require exact-source TestPyPI qualification before prod promotion or publication."""

import json
import os
import pathlib
import re
import urllib.parse
import urllib.request
from collections.abc import Mapping, Sequence

from ci_policy import git_output, object_value, read_event, text_value, validate_route
from verify_distributions import assignment


def commit_id(value: object) -> str:
    """Require a full Git commit identity before using it as a Git argument or API filter."""
    if not isinstance(value, str) or re.fullmatch(r"[0-9a-f]{40}(?:[0-9a-f]{24})?", value) is None:
        raise ValueError("Candidate evidence requires a full commit SHA.")
    return value


def positive_integer(value: object) -> int:
    """Require positive API identifiers/counters, rejecting booleans and string coercion."""
    if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
        raise ValueError("Invalid candidate run identifier or counter.")
    return value


def candidate_source(event_name: str, event: Mapping[str, object], repository: str,
                     parents: Sequence[str]) -> str:
    """Find the PR's candidate head or the second parent of a production promotion merge.

    PR identity must describe this repository's release_candidate -> prod route.
    Production requires the merge-commit route; direct/squashed commits cannot
    provide candidate provenance and are refused rather than guessed from a branch.
    """
    if event_name == "pull_request":
        pr = object_value(event.get("pull_request"), "pull_request")
        head = object_value(pr.get("head"), "head")
        base = object_value(pr.get("base"), "base")
        head_repo = object_value(head.get("repo"), "head.repo")
        base_repo = object_value(base.get("repo"), "base.repo")
        if base.get("ref") != "prod" or base_repo.get("full_name") != repository:
            raise ValueError("Candidate proof is only valid for this repository's prod PR.")
        validate_route("prod", text_value(head.get("ref"), "head.ref"),
                       text_value(head_repo.get("full_name"), "head.repo.full_name"), repository)
        return commit_id(head.get("sha"))
    if event_name not in ("release", "workflow_dispatch", "push") or len(parents) != 3:
        raise ValueError("Production must be a normal candidate PR merge; direct/squashed commits cannot publish.")
    for parent in parents:
        commit_id(parent)
    return parents[2]


def require_qualified_run(payload: Mapping[str, object], repository: str, sha: str) -> Mapping[str, object]:
    """Require the latest exact-SHA candidate run to be complete, successful, and from this workflow.

    Do not fall back to an older green run when the newest run is pending/failed.
    A rerun's current attempt and conclusion come from GitHub's run record.
    Rejection identifies the inspected run and differing fields so callers can
    diagnose upstream qualification failures without weakening this gate.
    """
    raw_runs = payload.get("workflow_runs")
    if not isinstance(raw_runs, list) or not raw_runs:
        raise ValueError("No TestPyPI candidate qualification exists for this source commit.")
    runs = [object_value(value, "workflow run") for value in raw_runs]
    latest = max(runs, key=lambda run: positive_integer(run.get("run_number")))
    if sum(run["run_number"] == latest["run_number"] for run in runs) != 1:
        raise ValueError("Ambiguous candidate run evidence.")
    for field in ("repository", "head_repository"):
        if object_value(latest.get(field), field).get("full_name") != repository:
            raise ValueError("Candidate workflow repository identity does not match.")
    run_id = positive_integer(latest.get("id"))
    attempt = positive_integer(latest.get("run_attempt"))
    expected = {"head_sha": sha, "head_branch": "release_candidate",
                "path": ".github/workflows/release-candidate.yml",
                "status": "completed", "conclusion": "success"}
    differences = [f"{key}={latest.get(key)!r} (expected {value!r})"
                   for key, value in expected.items() if latest.get(key) != value]
    if differences:
        raise ValueError(
            f"Candidate qualification has not passed for {sha}: {'; '.join(differences)}. "
            f"Inspect https://github.com/{repository}/actions/runs/{run_id} (attempt {attempt}). "
            "Complete or fix that RC workflow, then rerun this prod check."
        )
    if latest.get("event") not in ("push", "workflow_dispatch"):
        raise ValueError("Candidate qualification must originate from its branch push/manual workflow.")
    return latest


def github_runs(repository: str, sha: str) -> Mapping[str, object]:
    """Read only candidate workflow runs through the fixed GitHub API; never expose its token."""
    if re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", repository) is None:
        raise ValueError("Invalid GitHub repository identity.")
    query = urllib.parse.urlencode({"branch": "release_candidate", "head_sha": commit_id(sha),
                                   "per_page": 100})
    url = f"https://api.github.com/repos/{repository}/actions/workflows/release-candidate.yml/runs?{query}"
    token = text_value(os.environ.get("GITHUB_TOKEN"), "GITHUB_TOKEN")
    request = urllib.request.Request(url, headers={
        "Accept": "application/vnd.github+json", "Authorization": f"Bearer {token}",
        "User-Agent": "melder-candidate-ci",
    })
    with urllib.request.urlopen(request, timeout=30) as response:
        return object_value(json.load(response), "GitHub workflow runs")


def main() -> int:
    """Check candidate source/tree, final package version, and hosted qualification; write nothing."""
    repository = text_value(os.environ.get("GITHUB_REPOSITORY"), "GITHUB_REPOSITORY")
    sha = candidate_source(os.environ.get("GITHUB_EVENT_NAME", ""), read_event(), repository,
                           git_output(("rev-list", "--parents", "-n", "1", "HEAD")).split())
    if git_output(("rev-parse", f"{sha}^{{tree}}")) != git_output(("rev-parse", "HEAD^{tree}")):
        raise ValueError("Prod merge tree differs from the candidate; synchronize and qualify that exact tree.")
    version = assignment(pathlib.Path("src/melder/__version__.py").read_text(encoding="utf-8"), "__version__")
    if re.fullmatch(r"(?:\d+!)?\d+(?:\.\d+)*(?:\.post\d+)?", version) is None:
        raise ValueError("Prod requires a final package version; finalize and requalify the RC first.")
    run = require_qualified_run(github_runs(repository, sha), repository, sha)
    print(f"OK: candidate {sha}, version {version}, run {run['id']}, attempt {run['run_attempt']}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
