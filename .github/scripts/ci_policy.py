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

    BRANCHES: tuple[str, ...] = ("dev", "preprod", "release_candidate", "prod")
    PROMOTIONS: Mapping[str, str] = {
        "preprod": "dev", "release_candidate": "preprod", "prod": "release_candidate",
    }
    CANDIDATE_JOBS: tuple[str, ...] = ("authorize", "source-qualification", "build", "publish", "install")
    FULL_JOBS: tuple[str, ...] = ("source-assets", "repo-assets", "tests", "documentation")
    GAUNTLET_JOBS: tuple[str, ...] = (
        "real-world-gauntlet", "persistent-runtime-gauntlet", "shallow-all-thread-scaling",
    )
    REQUIRED_JOBS: tuple[str, ...] = (
        "branch-policy", "hygiene", *FULL_JOBS, *GAUNTLET_JOBS, "source-qualification",
    )
    # Which test manifests a run's runtime tests cover (runtime_releases): every one, or only the floor and
    # the newest. python_runtime_matrix.py discover accepts exactly these values.
    FULL_RELEASES: str = "all"
    SLICED_RELEASES: str = "floor-and-newest"
    RUNTIME_RELEASES: tuple[str, ...] = (FULL_RELEASES, SLICED_RELEASES)


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
    repository. Promotion follows dev -> preprod -> release_candidate -> prod.
    Same-repository release-fix/* PRs can prepare/fix the frozen candidate without
    pulling later preprod features. Unknown bases and forged forks raise ValueError.
    """
    for value, label in ((base, "base"), (head, "head"),
                         (head_repository, "head repository"), (repository, "repository")):
        text_value(value, label)
    if base not in CIPolicy.BRANCHES:
        raise ValueError(f"Unsupported PR base {base!r}; ordinary changes must target dev.")
    if base == head and head_repository == repository:
        raise ValueError("A same-repository PR must have different head and base branches.")
    if base == "dev":
        if head in CIPolicy.BRANCHES[1:] and head_repository != repository:
            raise ValueError("Permanent-branch synchronization must originate in this repository.")
        return False
    required_head = CIPolicy.PROMOTIONS[base]
    preparation = (base == "release_candidate" and head.startswith("release-fix/")
                   and len(head) > len("release-fix/"))
    if head_repository != repository or (head != required_head and not preparation):
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
        raise ValueError(f"CI ref must name a supported permanent branch; received {ref!r}.")
    return ref != "refs/heads/dev"


def validation_requirements(event_name: str, event: Mapping[str, object], ref: str,
                            repository: str) -> tuple[bool, bool, bool, bool]:
    """Return runtime, package, source-proof, and gauntlet requirements for a validated event.

    Dev/preprod PRs, release-fix PRs and manual CI run full qualification; runtime_releases decides how
    many test manifests that covers (a PR into dev tests only the floor and the newest).
    Only the validated dev-to-preprod PR also requires all three benchmark jobs.
    Unchanged preprod promotions reuse source evidence; prod promotions consume
    the separate exact-candidate gate. Ordinary pushes have no source-CI profile.
    """
    packages = package_required(event_name, event, ref, repository)
    if event_name == "workflow_dispatch":
        return True, packages, False, False
    if event_name != "pull_request":
        raise ValueError("Source CI runs on pull requests or explicit manual qualification, not pushes.")
    pr = object_value(event["pull_request"], "pull_request")
    base = object_value(pr["base"], "base")["ref"]
    head = object_value(pr["head"], "head")["ref"]
    if base == "prod":
        return False, False, False, False
    if base == "release_candidate" and head == "preprod":
        return False, False, True, False
    return True, packages, False, base == "preprod" and head == "dev"


def runtime_releases(event_name: str, event: Mapping[str, object], ref: str, repository: str) -> str:
    """Return which test manifests a validated event's runtime tests cover: every one, or the floor and newest.

    A pull request into dev tests the floor and the newest manifest on every runner (owner ruling,
    2026-10-05). Every route that can produce release evidence - the dev-to-preprod promotion,
    release-fix pull requests and manual CI - tests every manifest, so a defect specific to a middle
    patch is caught at the promotion at the latest, and a sliced run never qualifies a release
    (ci_qualification.py refuses to record one). Routes that skip the runtime tests report "all",
    which nothing reads.

    Args:
        event_name: GITHUB_EVENT_NAME.
        event: The parsed GitHub event payload.
        ref: GITHUB_REF.
        repository: GITHUB_REPOSITORY.

    Returns:
        CIPolicy.SLICED_RELEASES for a pull request into dev, otherwise CIPolicy.FULL_RELEASES.

    Raises:
        ValueError: When validation_requirements refuses the event; an invalid route never selects a
            smaller matrix.
    """
    validation_requirements(event_name, event, ref, repository)
    if event_name == "pull_request":
        pr = object_value(event["pull_request"], "pull_request")
        if object_value(pr["base"], "base")["ref"] == "dev":
            return CIPolicy.SLICED_RELEASES
    return CIPolicy.FULL_RELEASES


def require_success(results: Mapping[str, object], require_package: bool,
                    require_runtime: bool = True, require_source: bool = False,
                    require_gauntlet: bool = False) -> None:
    """Require complete dependency evidence and success for the selected validation profile.

    Optional jobs may succeed or be explicitly skipped; failure/cancellation
    never becomes success. Missing or unknown slots always fail, even when a
    profile legitimately omits the full suite.
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
        required = (name in ("branch-policy", "hygiene")
                    or name in CIPolicy.FULL_JOBS and require_runtime
                    or name == "packages" and require_package
                    or name == "source-qualification" and require_source
                    or name in CIPolicy.GAUNTLET_JOBS and require_gauntlet)
        allowed = ("success",) if required else ("success", "skipped")
        if result not in allowed:
            failures.append(f"{name}={result!r}")
    if failures:
        raise ValueError("Required CI did not succeed: " + ", ".join(failures))


def require_ci_results() -> tuple[bool, bool, bool, bool]:
    """Recompute requirements from event identity and verify both flags and job results.

    The branch job's outputs control scheduling, but cannot silently waive a
    requirement by emitting an empty or incorrect flag, nor shrink the runtime
    matrix by reporting the wrong release selection (CI_RUNTIME_RELEASES). Return
    the verified profile for consumers such as the full-qualification record writer.
    """
    event_name = os.environ.get("GITHUB_EVENT_NAME", "")
    event = read_event()
    ref = os.environ.get("GITHUB_REF", "")
    repository = os.environ.get("GITHUB_REPOSITORY", "")
    requirements = validation_requirements(event_name, event, ref, repository)
    for name, required in zip(("RUNTIME", "PACKAGE", "SOURCE", "GAUNTLET"), requirements, strict=True):
        if os.environ.get(f"CI_{name}_REQUIRED") != str(required).lower():
            raise ValueError(f"Missing/invalid {name.lower()} requirement from branch-policy.")
    if os.environ.get("CI_RUNTIME_RELEASES") != runtime_releases(event_name, event, ref, repository):
        raise ValueError("Missing/invalid runtime releases from branch-policy.")
    require_success(object_value(json.loads(os.environ["CI_JOB_RESULTS"]), "needs"),
                    requirements[1], requirements[0], requirements[2], requirements[3])
    return requirements


def case_collisions(paths: Sequence[str]) -> list[list[str]]:
    """Return tracked paths colliding case-insensitively in deterministic groups."""
    grouped: dict[str, list[str]] = {}
    for path in paths:
        grouped.setdefault(path.casefold(), []).append(path)
    return [sorted(group) for _, group in sorted(grouped.items()) if len(group) > 1]


def require_candidate_success(results: Mapping[str, object]) -> None:
    """Require every candidate stage to succeed, including the complete install matrix."""
    if set(results) != set(CIPolicy.CANDIDATE_JOBS):
        raise ValueError("Incomplete candidate dependency evidence; all five stages are required.")
    failures = [name for name in CIPolicy.CANDIDATE_JOBS
                if object_value(results[name], f"needs.{name}").get("result") != "success"]
    if failures:
        raise ValueError(f"Candidate qualification failed or was skipped: {failures}.")


def validate_candidate_head(event_name: str, ref: str, event_sha: str,
                            checkout_sha: str, advertisement: str) -> None:
    """Authorize only the current candidate branch, refusing stale runs and manual wrong-ref use.

    Git's exact branch advertisement must agree with both event and checkout.
    No cached tracking ref, abbreviated SHA, PR event, or deleted branch suffices.
    """
    branch = "refs/heads/release_candidate"
    if event_name not in ("push", "workflow_dispatch") or ref != branch:
        raise ValueError("TestPyPI publication must run on release_candidate, from push or manual dispatch.")
    if re.fullmatch(r"[0-9a-f]{40}(?:[0-9a-f]{24})?", event_sha) is None:
        raise ValueError("Candidate publication requires a full commit SHA.")
    if checkout_sha != event_sha or advertisement.strip() != f"{event_sha}\t{branch}":
        raise ValueError("Candidate branch moved or checkout differs; qualify the current candidate again.")


def git_output(arguments: Sequence[str]) -> str:
    """Execute one explicit Git argument vector and return stdout, raising on failure."""
    result = subprocess.run(["git", *arguments], check=True, capture_output=True, text=True,
                            encoding="utf-8")
    return result.stdout.strip()


def remote_tag_commit(output: str, tag: str) -> str:
    """Resolve one exact remote tag from Git's tab-separated ref advertisement.

    Annotated tags advertise both the tag object and a peeled target; use the
    target when present. Missing, duplicate, or malformed identity evidence raises
    ValueError. Exact matching avoids accepting a suffix match from ls-remote's
    glob rules. No tags are fetched, created, updated, or trusted from local state.
    """
    ref = f"refs/tags/{text_value(tag, 'release.tag_name')}"
    observed: dict[str, str] = {}
    for line in output.splitlines():
        if not line:
            continue
        fields = line.split("\t")
        if len(fields) != 2:
            raise ValueError("Malformed remote tag advertisement; refusing publication.")
        sha, name = fields
        if name not in (ref, ref + "^{}"):
            continue
        if name in observed or re.fullmatch(r"[0-9a-f]{40}(?:[0-9a-f]{24})?", sha) is None:
            raise ValueError("Ambiguous or invalid remote release-tag identity.")
        observed[name] = sha
    if ref not in observed:
        raise ValueError(f"Release tag {tag!r} is missing from origin; refusing publication.")
    return observed.get(ref + "^{}", observed[ref])


def current_release_tag(event: Mapping[str, object]) -> str:
    """Read the release tag's live target without relying on checkout-cached tags."""
    release = object_value(event.get("release"), "release")
    tag = text_value(release.get("tag_name"), "release.tag_name")
    ref = f"refs/tags/{tag}"
    return remote_tag_commit(
        git_output(("ls-remote", "--exit-code", "--tags", "origin", ref, ref + "^{}")), tag,
    )


def validate_release(event_name: str, ref: str, event: Mapping[str, object],
                     event_sha: str, checkout_sha: str, prod_sha: str,
                     tag_sha: Optional[str] = None) -> None:
    """Require a final release/manual-prod event and exact current-prod commit identity.

    Published prereleases are not final publication authorization. Manual dispatch
    must select prod. Event, checkout, and prod SHAs must be full commit IDs and
    equal. Release events also require the live remote tag target to equal that
    commit. Moved/missing tag evidence or prod movement raises ValueError. No
    branches or tags are modified, and manual prod dispatch does not need a tag.
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
        if tag_sha is None:
            raise ValueError("Live remote release-tag identity is required before publication.")
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
    if event_name == "release" and tag_sha != event_sha:
        raise ValueError(
            f"Release tag no longer points to the qualified commit: tag={tag_sha}, "
            f"qualified={event_sha}. Requalify the intended release."
        )


def read_event() -> Mapping[str, object]:
    """Read the GitHub-provided event file as data; fail if it is absent or malformed."""
    path = pathlib.Path(text_value(os.environ.get("GITHUB_EVENT_PATH"), "GITHUB_EVENT_PATH"))
    return object_value(json.loads(path.read_text(encoding="utf-8")), "event")


def main(argv: Optional[Sequence[str]] = None) -> int:
    """Execute one read-only CI gate; print a diagnostic and return nonzero on refusal."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("gate", choices=("branch", "merge-ready", "hygiene", "release-head",
                                        "candidate-head", "candidate-ready"))
    args = parser.parse_args(argv)
    try:
        if args.gate == "branch":
            event_name = os.environ.get("GITHUB_EVENT_NAME", "")
            event = read_event()
            ref = os.environ.get("GITHUB_REF", "")
            repository = os.environ.get("GITHUB_REPOSITORY", "")
            requirements = validation_requirements(event_name, event, ref, repository)
            releases = runtime_releases(event_name, event, ref, repository)
            with pathlib.Path(os.environ["GITHUB_OUTPUT"]).open("a", encoding="utf-8") as output:
                for name, required in zip(("runtime", "package", "source", "gauntlet"), requirements, strict=True):
                    output.write(f"{name}-required={str(required).lower()}\n")
                output.write(f"runtime-releases={releases}\n")
        elif args.gate == "merge-ready":
            require_ci_results()
        elif args.gate == "hygiene":
            collisions = case_collisions(git_output(("ls-files", "-z")).split("\0")[:-1])
            if collisions:
                raise ValueError(f"Tracked paths collide case-insensitively: {collisions}")
        elif args.gate == "candidate-ready":
            require_candidate_success(object_value(json.loads(os.environ["CI_JOB_RESULTS"]), "needs"))
        elif args.gate == "candidate-head":
            validate_candidate_head(
                os.environ.get("GITHUB_EVENT_NAME", ""), os.environ.get("GITHUB_REF", ""),
                os.environ.get("GITHUB_SHA", ""), git_output(("rev-parse", "HEAD^{commit}")),
                git_output(("ls-remote", "--exit-code", "--heads", "origin",
                            "refs/heads/release_candidate")),
            )
        else:
            event_name = os.environ.get("GITHUB_EVENT_NAME", "")
            event = read_event()
            tag_sha = current_release_tag(event) if event_name == "release" else None
            # Read prod after the tag so the last remote query remains the
            # current production-head check immediately before publication.
            git_output(("fetch", "--no-tags", "origin",
                        "+refs/heads/prod:refs/remotes/origin/prod"))
            event_sha = text_value(os.environ.get("GITHUB_SHA"), "GITHUB_SHA")
            validate_release(event_name, os.environ.get("GITHUB_REF", ""), event, event_sha,
                             git_output(("rev-parse", "HEAD^{commit}")),
                             git_output(("rev-parse", "refs/remotes/origin/prod^{commit}")),
                             tag_sha=tag_sha)
    except (ValueError, KeyError, OSError, subprocess.CalledProcessError) as error:
        print(f"CI gate refused: {error}", file=sys.stderr)
        return 1
    print(f"OK: {args.gate}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
