"""Read-only branch, merge-result, repository, and publication gates for CI."""

import argparse
import json
import os
import pathlib
import re
import subprocess
import sys
from collections.abc import Mapping, Sequence
from typing import Optional, cast


class CIPolicy:
    """Hold immutable CI names and branch routes shared by the command-line gates."""

    BRANCHES: tuple[str, ...] = ("dev", "preprod", "prod")
    PROMOTIONS: Mapping[str, str] = {"preprod": "dev", "prod": "preprod"}
    REQUIRED_JOBS: tuple[str, ...] = (
        "branch-policy", "hygiene", "source-assets", "repo-assets", "tests",
    )


def object_value(value: object, label: str) -> Mapping[str, object]:
    """Require a JSON object at an external input boundary; raise ValueError otherwise."""
    if not isinstance(value, Mapping):
        raise ValueError(f"{label} must be a JSON object; refusing incomplete CI evidence.")
    return cast(Mapping[str, object], value)


def text_value(value: object, label: str) -> str:
    """Require a nonempty string in event metadata; never invent an absent identity."""
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{label} must be a nonempty string; check the workflow event.")
    return value


def validate_route(base: str, head: str, head_repository: str, repository: str) -> bool:
    """Validate a PR route and return whether distribution verification is required.

    Contributions enter dev. Permanent-branch synchronization must come from this
    repository; preprod accepts only dev and prod accepts only preprod. Unknown
    bases and forged fork promotion branches raise ValueError. No refs are changed.
    """
    for value, label in ((base, "base"), (head, "head"),
                         (head_repository, "head repository"), (repository, "repository")):
        text_value(value, label)
    if base not in CIPolicy.BRANCHES:
        raise ValueError(f"Unsupported PR base {base!r}; ordinary changes must target dev.")
    if base == head and head_repository == repository:
        raise ValueError("A same-repository PR must have different head and base branches.")
    if base == "dev":
        if head in ("preprod", "prod") and head_repository != repository:
            raise ValueError("Permanent-branch synchronization must originate in this repository.")
        return False
    required_head = CIPolicy.PROMOTIONS[base]
    if head_repository != repository or head != required_head:
        raise ValueError(
            f"Promotion into {base} requires {repository}:{required_head}; "
            f"received {head_repository}:{head}."
        )
    return True


def package_required(event_name: str, event: Mapping[str, object], ref: str,
                     repository: str) -> bool:
    """Resolve a supported event's branch policy without accepting ambiguous metadata.

    PR payloads establish both repository identities. Push/manual CI events must
    select a permanent branch. Returns a package requirement; raises ValueError
    for unsupported events, refs, or incomplete payloads.
    """
    text_value(repository, "GITHUB_REPOSITORY")
    if event_name == "pull_request":
        pr = object_value(event.get("pull_request"), "pull_request")
        base = object_value(pr.get("base"), "pull_request.base")
        head = object_value(pr.get("head"), "pull_request.head")
        base_repo = object_value(base.get("repo"), "pull_request.base.repo")
        head_repo = object_value(head.get("repo"), "pull_request.head.repo")
        if base_repo.get("full_name") != repository:
            raise ValueError("PR base repository does not match GITHUB_REPOSITORY.")
        return validate_route(
            text_value(base.get("ref"), "base.ref"),
            text_value(head.get("ref"), "head.ref"),
            text_value(head_repo.get("full_name"), "head.repo.full_name"), repository,
        )
    if event_name not in ("push", "workflow_dispatch"):
        raise ValueError(f"Unsupported CI event {event_name!r}; refusing an implicit route.")
    if ref not in tuple(f"refs/heads/{branch}" for branch in CIPolicy.BRANCHES):
        raise ValueError(f"CI push/manual ref must be dev, preprod, or prod; received {ref!r}.")
    return ref != "refs/heads/dev"


def require_success(results: Mapping[str, object], require_package: bool) -> None:
    """Fail closed unless the complete expected dependency set actually succeeded.

    The packages job may be skipped only for dev. Unknown/missing jobs and every
    other non-success conclusion raise ValueError, including a skipped test matrix.
    This function never treats the absence of a failing job as successful evidence.
    """
    expected = set(CIPolicy.REQUIRED_JOBS) | {"packages"}
    if set(results) != expected:
        raise ValueError(
            f"Incomplete CI dependency evidence: missing={sorted(expected - set(results))}; "
            f"unexpected={sorted(set(results) - expected)}."
        )
    failures: list[str] = []
    for name in sorted(expected):
        result = object_value(results[name], f"needs.{name}").get("result")
        allowed = ("success", "skipped") if name == "packages" and not require_package else ("success",)
        if result not in allowed:
            failures.append(f"{name}={result!r}")
    if failures:
        raise ValueError("Required CI did not succeed: " + ", ".join(failures))


def case_collisions(paths: Sequence[str]) -> list[list[str]]:
    """Return tracked paths colliding case-insensitively in deterministic groups."""
    grouped: dict[str, list[str]] = {}
    for path in paths:
        grouped.setdefault(path.casefold(), []).append(path)
    return [sorted(group) for _, group in sorted(grouped.items()) if len(group) > 1]


def git_output(arguments: Sequence[str]) -> str:
    """Execute one explicit Git argument vector and return stdout, raising on failure."""
    result = subprocess.run(["git", *arguments], check=True, capture_output=True, text=True,
                            encoding="utf-8")
    return result.stdout.strip()


def validate_release(event_name: str, ref: str, event: Mapping[str, object],
                     event_sha: str, checkout_sha: str, prod_sha: str) -> None:
    """Require a final release/manual-prod event and exact current-prod commit identity.

    Published prereleases are not final publication authorization. Manual dispatch
    must select prod. All three SHAs must be full hexadecimal commit IDs and equal;
    a prod movement since qualification raises ValueError. No branches are modified.
    """
    if event_name == "release":
        release = object_value(event.get("release"), "release")
        if event.get("action") != "published":
            raise ValueError("Only a published final release authorizes package publication.")
        if release.get("draft") is not False or release.get("prerelease") is not False:
            raise ValueError("Draft/prerelease events do not authorize final PyPI publication.")
        tag = text_value(release.get("tag_name"), "release.tag_name")
        if ref != f"refs/tags/{tag}":
            raise ValueError("The release tag does not match the workflow ref.")
    elif event_name != "workflow_dispatch" or ref != "refs/heads/prod":
        raise ValueError("Manual publication must run on prod; PR/push events cannot publish.")
    for sha in (event_sha, checkout_sha, prod_sha):
        if re.fullmatch(r"[0-9a-f]{40}(?:[0-9a-f]{24})?", sha) is None:
            raise ValueError("Publication requires full, resolved commit SHAs.")
    if event_sha != checkout_sha or checkout_sha != prod_sha:
        raise ValueError(
            f"Publication requires current prod HEAD: event={event_sha}, "
            f"checkout={checkout_sha}, prod={prod_sha}. Requalify the intended release."
        )


def read_event() -> Mapping[str, object]:
    """Read the GitHub-provided event file as data; fail if it is absent or malformed."""
    path = pathlib.Path(text_value(os.environ.get("GITHUB_EVENT_PATH"), "GITHUB_EVENT_PATH"))
    return object_value(json.loads(path.read_text(encoding="utf-8")), "event")


def main(argv: Optional[Sequence[str]] = None) -> int:
    """Execute one read-only CI gate; print a diagnostic and return nonzero on refusal."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("gate", choices=("branch", "merge-ready", "hygiene", "release-head"))
    args = parser.parse_args(argv)
    try:
        if args.gate == "branch":
            required = package_required(os.environ.get("GITHUB_EVENT_NAME", ""), read_event(),
                                        os.environ.get("GITHUB_REF", ""),
                                        os.environ.get("GITHUB_REPOSITORY", ""))
            with pathlib.Path(os.environ["GITHUB_OUTPUT"]).open("a", encoding="utf-8") as output:
                output.write(f"package-required={str(required).lower()}\n")
        elif args.gate == "merge-ready":
            required_text = os.environ.get("CI_PACKAGE_REQUIRED", "")
            if required_text not in ("true", "false"):
                raise ValueError("Missing/invalid package requirement from branch-policy.")
            results = object_value(json.loads(os.environ["CI_JOB_RESULTS"]), "needs")
            require_success(results, required_text == "true")
        elif args.gate == "hygiene":
            collisions = case_collisions(git_output(("ls-files", "-z")).split("\0")[:-1])
            if collisions:
                raise ValueError(f"Tracked paths collide case-insensitively: {collisions}")
        else:
            git_output(("fetch", "--no-tags", "origin",
                        "+refs/heads/prod:refs/remotes/origin/prod"))
            event_sha = text_value(os.environ.get("GITHUB_SHA"), "GITHUB_SHA")
            validate_release(os.environ.get("GITHUB_EVENT_NAME", ""),
                             os.environ.get("GITHUB_REF", ""), read_event(), event_sha,
                             git_output(("rev-parse", "HEAD^{commit}")),
                             git_output(("rev-parse", "refs/remotes/origin/prod^{commit}")))
    except (ValueError, KeyError, OSError, subprocess.CalledProcessError) as error:
        print(f"CI gate refused: {error}", file=sys.stderr)
        return 1
    print(f"OK: {args.gate}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
