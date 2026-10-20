"""Record full CI evidence and verify it before reusing an unchanged source tree."""

import argparse
import json
import os
import pathlib
import re
import urllib.parse
import urllib.request
from collections.abc import Mapping, Sequence
from typing import Optional

from check_candidate_run import commit_id, positive_integer
from ci_policy import (git_output, object_value, read_event, require_ci_results, text_value,
                       validate_route, validation_requirements)


class SourceQualificationPolicy:
    """Define the versioned, bounded source-proof format and trusted producer workflow."""

    SCHEMA = 1
    WORKFLOW = ".github/workflows/ci.yml"
    PAGE_SIZE = 100
    MAX_PAGES = 10
    MAX_RECORD_BYTES = 65536


def mappings(value: object, label: str) -> list[Mapping[str, object]]:
    """Require an API list of objects; malformed evidence cannot become an empty result."""
    if not isinstance(value, list):
        raise ValueError(f"{label} must be a list.")
    return [object_value(item, label) for item in value]


def github_json(repository: str, endpoint: str, query: Mapping[str, object]) -> object:
    """Read JSON from the fixed GitHub API without logging or forwarding its credential to artifacts."""
    if re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", repository) is None:
        raise ValueError("Invalid GitHub repository identity.")
    if endpoint.startswith(("/", "http:", "https:")):
        raise ValueError("An API endpoint must be repository-relative.")
    suffix = "?" + urllib.parse.urlencode(query) if query else ""
    request = urllib.request.Request(
        f"https://api.github.com/repos/{repository}/{endpoint}{suffix}",
        headers={"Accept": "application/vnd.github+json",
                 "Authorization": f"Bearer {text_value(os.environ.get('GITHUB_TOKEN'), 'GITHUB_TOKEN')}",
                 "User-Agent": "melder-source-qualification"},
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.load(response)


def github_items(repository: str, endpoint: str, key: Optional[str] = None,
                 **query: object) -> list[Mapping[str, object]]:
    """Read all bounded API pages, refusing truncation instead of choosing incomplete evidence."""
    result: list[Mapping[str, object]] = []
    for page in range(1, SourceQualificationPolicy.MAX_PAGES + 1):
        payload = github_json(repository, endpoint, {
            **query, "per_page": SourceQualificationPolicy.PAGE_SIZE, "page": page,
        })
        values = object_value(payload, endpoint).get(key) if key is not None else payload
        rows = mappings(values, endpoint)
        result.extend(rows)
        if len(rows) < SourceQualificationPolicy.PAGE_SIZE:
            return result
    raise ValueError("Source qualification history exceeds the pagination bound; establish fresh evidence.")


def latest_run(runs: Sequence[Mapping[str, object]]) -> Mapping[str, object]:
    """Select the newest applicable CI run without falling back past a failed or pending run."""
    if not runs:
        raise ValueError("No full CI qualification found. Run CI manually on the intended preprod/RC branch.")
    numbers = [positive_integer(run.get("run_number")) for run in runs]
    if len(numbers) != len(set(numbers)):
        raise ValueError("Ambiguous source CI run evidence.")
    return runs[numbers.index(max(numbers))]


def assert_fields(actual: Mapping[str, object], expected: Mapping[str, object], label: str) -> None:
    """Require exact values and types, so booleans and string coercions cannot impersonate IDs."""
    differences = [key for key, value in expected.items()
                   if type(actual.get(key)) is not type(value) or actual.get(key) != value]
    if differences:
        raise ValueError(f"{label} differs in {', '.join(differences)}.")


def select_run(repository: str, source_sha: str, tree: str, run: Mapping[str, object],
               event: str, branch: str, head_sha: str, head_branch: str,
               pr_number: int = 0, base_sha: str = "") -> dict[str, object]:
    """Bind a complete successful CI run to one non-expired run/attempt-specific artifact.

    The API owns run provenance; the downloaded JSON must later prove the actual
    tested merge tree. Artifact presence alone is never sufficient.
    """
    run_id = positive_integer(run.get("id"))
    attempt = positive_integer(run.get("run_attempt"))
    for field in ("repository", "head_repository"):
        if object_value(run.get(field), field).get("full_name") != repository:
            raise ValueError("Source CI repository identity does not match.")
    assert_fields(run, {"path": SourceQualificationPolicy.WORKFLOW, "event": event,
                        "head_sha": head_sha, "head_branch": head_branch,
                        "status": "completed", "conclusion": "success"},
                  f"Source CI https://github.com/{repository}/actions/runs/{run_id}")
    name = f"source-qualification-{run_id}-{attempt}"
    artifacts = [artifact for artifact in github_items(repository, f"actions/runs/{run_id}/artifacts", "artifacts")
                 if artifact.get("name") == name]
    if len(artifacts) != 1 or artifacts[0].get("expired") is not False:
        raise ValueError(f"Missing, expired or ambiguous {name}. Run full CI again on {branch}.")
    expected = {
        "schema": SourceQualificationPolicy.SCHEMA, "repository": repository,
        "run_id": run_id, "run_attempt": attempt, "event": event,
        "target_branch": branch, "head_sha": head_sha, "base_sha": base_sha,
        "pull_request": pr_number, "tree_sha": tree, "full_runtime": True, "package_required": True,
    }
    return {"source_sha": source_sha, "artifact_id": positive_integer(artifacts[0].get("id")),
            "artifact_name": name, "expected": expected}


def merged_pull_request(repository: str, sha: str, branch: str) -> Mapping[str, object]:
    """Resolve the PR that actually produced this commit, never merely one containing it."""
    candidates = [
        pr for pr in github_items(repository, f"commits/{sha}/pulls")
        if pr.get("merge_commit_sha") == sha and isinstance(pr.get("merged_at"), str)
        and pr["merged_at"] and object_value(pr.get("base"), "base").get("ref") == branch
    ]
    if len(candidates) != 1:
        raise ValueError(f"No unique merged PR proves {branch}:{sha}. Run full CI manually on {branch}.")
    pr = candidates[0]
    base = object_value(pr["base"], "base")
    head = object_value(pr.get("head"), "head")
    if object_value(base.get("repo"), "base.repo").get("full_name") != repository:
        raise ValueError("Source PR base repository does not match.")
    validate_route(branch, text_value(head.get("ref"), "head.ref"),
                   text_value(object_value(head.get("repo"), "head.repo").get("full_name"), "head.repo"),
                   repository)
    return pr


def select_for_commit(repository: str, sha: str, branch: str, tree: str) -> dict[str, object]:
    """Resolve full preprod or release-fix qualification for the exact promoted tree.

    Exact-commit manual CI takes precedence when present. Otherwise a preprod
    merge resolves to its full PR run; an RC preprod promotion follows that
    preprod commit once. A release-fix merge resolves to its own full PR run.
    """
    if branch not in ("preprod", "release_candidate"):
        raise ValueError("Release source requires full preprod or candidate-fix qualification.")
    commit = object_value(github_json(repository, f"git/commits/{commit_id(sha)}", {}), "commit")
    assert_fields(commit, {"sha": sha}, "Source commit")
    if commit_id(object_value(commit.get("tree"), "tree").get("sha")) != tree:
        raise ValueError("Promotion tree differs from its source; qualify the changed contents first.")
    manual = github_items(repository, "actions/workflows/ci.yml/runs", "workflow_runs",
                          head_sha=sha, branch=branch, event="workflow_dispatch")
    if manual:
        return select_run(repository, sha, tree, latest_run(manual), "workflow_dispatch", branch, sha, branch)
    pr = merged_pull_request(repository, sha, branch)
    head = object_value(pr["head"], "head")
    head_sha = commit_id(head.get("sha"))
    parents = mappings(commit.get("parents"), "commit.parents")
    if len(parents) != 2 or commit_id(parents[1].get("sha")) != head_sha:
        raise ValueError("Promotion must preserve its PR head as a normal merge parent; requalify manually.")
    base_sha = commit_id(parents[0].get("sha"))
    if branch == "release_candidate" and head["ref"] == "preprod":
        return select_for_commit(repository, head_sha, "preprod", tree)
    number = positive_integer(pr.get("number"))
    runs = github_items(repository, "actions/workflows/ci.yml/runs", "workflow_runs",
                        head_sha=head_sha, branch=head["ref"], event="pull_request")
    # GitHub may erase run.pull_requests after merge. The downloaded full-run
    # record, not that mutable association list, must prove the PR identity.
    return select_run(repository, sha, tree, latest_run(runs), "pull_request", branch,
                      head_sha, text_value(head["ref"], "head.ref"), number, base_sha)


def require_clean_tracked_checkout() -> None:
    """Reject real index/content/mode changes without mistaking checkout EOL policy for mutation.

    A legacy CRLF blob under text/eol=lf can be reported dirty even when its
    checked-out bytes match HEAD exactly. Only unchanged regular-file modes and
    identical unfiltered blob IDs clear that false positive. Never normalize or
    restore files, ignore whitespace, or waive an entire directory. Untracked
    reports/caches remain outside this tracked-source contract.
    """
    staged = git_output(("diff", "--cached", "--name-only", "--no-renames", "--no-ext-diff", "-z", "HEAD", "--"))
    if staged:
        paths = staged.rstrip("\0").split("\0")
        raise ValueError(f"Tracked staged modifications cannot be qualified: {paths[:10]!r}. Commit intended changes first.")
    raw = git_output(("diff", "--raw", "--no-abbrev", "--no-renames", "--no-ext-diff", "-z", "HEAD", "--"))
    if not raw:
        return
    records = raw.split("\0")
    if records[-1] != "" or len(records) % 2 != 1:
        raise ValueError("Malformed tracked-checkout diff; refusing incomplete source evidence.")
    changed: list[str] = []
    for offset in range(0, len(records) - 1, 2):
        metadata, path = records[offset], records[offset + 1]
        fields = metadata.split()
        if not metadata.startswith(":") or len(fields) != 5 or not path:
            raise ValueError("Malformed tracked-checkout diff entry; refusing source qualification.")
        before, after, blob, _, status = fields
        if status != "M" or before[1:] != after or after not in ("100644", "100755"):
            changed.append(path)
        elif git_output(("hash-object", "--no-filters", "--", path)) != commit_id(blob):
            changed.append(path)
    if changed:
        raise ValueError(
            f"Tracked checkout modifications cannot be qualified: {changed[:10]!r} "
            f"({len(changed)} paths). Commit intended edits or restore the selected revision, then rerun CI."
        )


def checkout_identity() -> tuple[str, str]:
    """Require the exact event commit and unchanged tracked bytes/modes; return its commit/tree IDs."""
    sha = commit_id(git_output(("rev-parse", "HEAD^{commit}")))
    if sha != commit_id(os.environ.get("GITHUB_SHA")):
        raise ValueError("Checkout differs from GITHUB_SHA; source evidence cannot be reused.")
    require_clean_tracked_checkout()
    return sha, commit_id(git_output(("rev-parse", "HEAD^{tree}")))


def select_source() -> dict[str, object]:
    """Select evidence for an unchanged preprod-to-RC PR or the current RC publication checkout."""
    repository = text_value(os.environ.get("GITHUB_REPOSITORY"), "GITHUB_REPOSITORY")
    event_name = os.environ.get("GITHUB_EVENT_NAME", "")
    event = read_event()
    ref = os.environ.get("GITHUB_REF", "")
    sha, tree = checkout_identity()
    if event_name == "pull_request":
        if validation_requirements(event_name, event, ref, repository) != (False, False, True):
            raise ValueError("This PR does not use preprod source qualification.")
        head = object_value(object_value(event["pull_request"], "pull_request")["head"], "head")
        return select_for_commit(repository, commit_id(head.get("sha")), "preprod", tree)
    if event_name in ("push", "workflow_dispatch") and ref == "refs/heads/release_candidate":
        return select_for_commit(repository, sha, "release_candidate", tree)
    raise ValueError("Source proof consumption requires a preprod promotion PR or an RC checkout.")


def full_record() -> dict[str, object]:
    """Create evidence only after a complete full-profile CI dependency set succeeded.

    A PR record identifies its tested merge parents and tree, rather than
    confusing the run API's head SHA with the actual merge checkout.
    Light profiles cannot emit this record, even if their other jobs are green.
    """
    runtime, package, _ = require_ci_results()
    if not runtime:
        raise ValueError("A light CI run cannot issue full runtime qualification.")
    sha, tree = checkout_identity()
    event_name = os.environ["GITHUB_EVENT_NAME"]
    event = read_event()
    branch = os.environ.get("GITHUB_REF", "").removeprefix("refs/heads/")
    head_sha, base_sha, number = sha, "", 0
    if event_name == "pull_request":
        pr = object_value(event["pull_request"], "pull_request")
        head = object_value(pr["head"], "head")
        base = object_value(pr["base"], "base")
        branch = text_value(base["ref"], "base.ref")
        head_sha, base_sha = commit_id(head.get("sha")), commit_id(base.get("sha"))
        number = positive_integer(pr.get("number"))
        parents = git_output(("rev-list", "--parents", "-n", "1", "HEAD")).split()
        if parents != [sha, base_sha, head_sha]:
            raise ValueError("PR checkout parents differ from the event; rerun current merge qualification.")
    return {
        "schema": SourceQualificationPolicy.SCHEMA,
        "repository": text_value(os.environ.get("GITHUB_REPOSITORY"), "GITHUB_REPOSITORY"),
        "run_id": positive_integer(int(os.environ["GITHUB_RUN_ID"])),
        "run_attempt": positive_integer(int(os.environ["GITHUB_RUN_ATTEMPT"])),
        "event": event_name, "target_branch": branch, "head_sha": head_sha, "base_sha": base_sha,
        "pull_request": number, "checkout_sha": sha, "tree_sha": tree,
        "full_runtime": True, "package_required": package,
    }


def validate_proof(proof: Mapping[str, object], expected: Mapping[str, object]) -> None:
    """Require the exact versioned full-runtime record and tested tree, not just an artifact name."""
    if set(proof) != set(expected) | {"checkout_sha"}:
        raise ValueError("Source qualification record has unexpected or missing fields.")
    commit_id(proof.get("checkout_sha"))
    assert_fields(proof, expected, "Full CI qualification")
    if expected["event"] == "workflow_dispatch" and proof["checkout_sha"] != expected["head_sha"]:
        raise ValueError("Manual qualification checkout differs from its run head.")


def read_record(path: pathlib.Path) -> Mapping[str, object]:
    """Read a bounded JSON proof as data; never import or execute downloaded artifacts."""
    with path.open("rb") as stream:
        raw = stream.read(SourceQualificationPolicy.MAX_RECORD_BYTES + 1)
    if len(raw) > SourceQualificationPolicy.MAX_RECORD_BYTES:
        raise ValueError("Source qualification record is too large.")
    return object_value(json.loads(raw), "qualification record")


def write_record(path: pathlib.Path, record: Mapping[str, object]) -> None:
    """Write one job-owned JSON report after its evidence has been validated."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main(argv: Optional[Sequence[str]] = None) -> int:
    """Record, select, or verify source evidence; all GitHub access is read-only."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("operation", choices=("record", "select", "verify"))
    parser.add_argument("--record", type=pathlib.Path, default=pathlib.Path("reports/qualification.json"))
    parser.add_argument("--selection", type=pathlib.Path, default=pathlib.Path("reports/source-selection.json"))
    args = parser.parse_args(argv)
    if args.operation == "record":
        write_record(args.record, full_record())
    elif args.operation == "select":
        selection = select_source()
        write_record(args.selection, selection)
        expected = object_value(selection["expected"], "expected")
        with pathlib.Path(os.environ["GITHUB_OUTPUT"]).open("a", encoding="utf-8") as output:
            output.write(f"run-id={expected['run_id']}\nartifact-id={selection['artifact_id']}\n")
    else:
        saved = read_record(args.selection)
        current = select_source()
        if saved != current:
            raise ValueError("Source qualification changed while downloading; rerun the proof check.")
        validate_proof(read_record(args.record), object_value(current["expected"], "expected"))
        print(f"OK: full CI qualifies tree {object_value(current['expected'], 'expected')['tree_sha']}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
