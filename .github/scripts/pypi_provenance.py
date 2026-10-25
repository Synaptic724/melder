"""Verify the PEP 740 provenance of every file of a final release on PyPI, after the upload.

The publication workflow's provenance job (Release / provenance) runs `verify` once `pypi-publish` has uploaded the
release by Trusted Publishing. For every built distribution it reads the provenance PyPI's Integrity API holds and
checks it in the same five layers as the release candidate's check (`testpypi_provenance.py`), with the release's
identity:

1. a provenance exists;
2. its one bundle's publisher record is this repository's `python-publish.yml` in the `pypi` environment;
3. Sigstore verifies its one attestation on the production trust root (certificate chain, transparency log,
   signature);
4. the signing certificate names this run's upload, claim by claim: the workflow at the run's ref (the release tag,
   or `prod` for a manual dispatch), the released commit, this run and the attempt that uploaded, its event, the
   `pypi` environment;
5. the attested statement names exactly this file and its sha256, with the PyPI publish predicate.

The layers, the pinned verifier, its lock and its recorded control are the candidate check's, imported from
`testpypi_provenance.py`; only the policy and the run identity are the release's. The files are already on PyPI
when this runs, so a refusal cannot unpublish them: it fails the run, naming the file and what differs, before the
release is announced.
"""

import argparse
import json
import os
import pathlib
import re
import tempfile
from collections.abc import Mapping, Sequence
from typing import Optional, TypedDict

from ci_policy import git_output
from testpypi_candidate import FileIdentity, file_identity, package_version
from testpypi_provenance import (ExpectedIdentity, FulcioClaim, ProvenanceControl, ProvenancePolicy, certificate_der,
                                 certificate_identity, check_identity, check_statement, control_entries,
                                 fetch_provenance, require_outcomes, run_verifier, single_attestation,
                                 tool_environment)
from verify_distributions import verify_distributions


class ReleaseContext(TypedDict):
    """This publication run's identity, read from GitHub's default environment variables and checked before use.

    `ref` is the full ref the run and its signing certificate name; `tag` is the release's tag, or empty for a
    manual dispatch on prod.
    """

    repository_id: str
    owner_id: str
    sha: str
    workflow_sha: str
    event: str
    ref: str
    tag: str
    run_id: str
    run_attempt: int


class ReleaseProvenancePolicy(ProvenancePolicy):
    """Hold the release provenance check's identity: PyPI's Trusted Publisher for the publication workflow.

    The owner configures that publisher on PyPI (BRANCH_WORKFLOW.md): this repository, `python-publish.yml`, the
    `pypi` environment. A publication run starts from a published GitHub release, at that release's tag, or from a
    manual dispatch on `prod`, so the ref its certificate names is the run's own (`release_context`); every other
    expected value is fixed here or inherited. The server, repository, owner, issuer, runner, visibility, statement
    format, retry bounds and the pinned tool are `ProvenancePolicy`'s; this class overrides the index, the workflow,
    the environment, the events and the refusal for a missing provenance. Change it only deliberately, together
    with the publisher on PyPI.
    """

    INDEX_NAME = "PyPI"
    INTEGRITY_ROOT = "https://pypi.org/integrity/melder/"
    USER_AGENT = "melder-release-ci"
    WORKFLOW = "python-publish.yml"
    ENVIRONMENT = "pypi"
    # A manual dispatch publishes from prod; a published release runs at TAG_REF_PREFIX + its tag.
    REF = "refs/heads/prod"
    TAG_REF_PREFIX = "refs/tags/"
    RELEASE_EVENT = "release"
    TRIGGERS: tuple[str, ...] = ("release", "workflow_dispatch")
    # The verifier entries of released files are `release:<file>`; the controls keep their own ids.
    ENTRY_PREFIX = "release"

    @classmethod
    def missing_provenance(cls, name: str) -> str:
        """Return the refusal for a released file PyPI still holds no provenance for after the last lookup.

        The upload has already happened, so the remedy is to find out why before the release is announced: the
        Trusted Publisher, or the upload step's log.
        """
        return (f"PyPI holds no provenance for {name}: it was uploaded without Trusted Publishing, or PyPI did not "
                "accept its attestation. The file is published and cannot be replaced: compare PyPI's Trusted "
                "Publisher for melder with BRANCH_WORKFLOW.md and read the Publish to PyPI log before announcing "
                "this release.")


def release_context(environment: Mapping[str, str],
                    policy: type[ReleaseProvenancePolicy] = ReleaseProvenancePolicy) -> ReleaseContext:
    """Read and check this publication run's identity from GitHub's default environment variables.

    The run must come from one of the policy's events: a published release, whose tag the workflow passes as
    `RELEASE_TAG` from the event and whose ref is that tag, or a manual dispatch on `prod`, which has no tag. Its
    server, repository, ref and workflow ref must be the policy's at that ref; its commit SHAs must be full and its
    numeric identifiers decimal. A tag that does not name the package version is refused later, with the files
    (`released_files`).

    Args:
        environment: The job's environment variables.
        policy: The identity to check against; `ReleaseProvenancePolicy` in CI.

    Returns:
        The checked run identity.

    Raises:
        ValueError: Naming the variable that is missing or differs.
    """
    event = environment.get("GITHUB_EVENT_NAME", "")
    if event not in policy.TRIGGERS:
        raise ValueError(f"GITHUB_EVENT_NAME is {event!r}; the release provenance check runs only for "
                         f"{', '.join(policy.TRIGGERS)}.")
    tag = environment.get("RELEASE_TAG", "")
    if event == policy.RELEASE_EVENT and not tag:
        raise ValueError("RELEASE_TAG is ''; a published release's check needs that release's tag.")
    if event != policy.RELEASE_EVENT and tag:
        raise ValueError(f"RELEASE_TAG is {tag!r}; a manual dispatch publishes from {policy.REF} with no tag.")
    ref = (policy.TAG_REF_PREFIX + tag) if tag else policy.REF
    fixed = {"GITHUB_SERVER_URL": policy.SERVER, "GITHUB_REPOSITORY": policy.REPOSITORY, "GITHUB_REF": ref,
             "GITHUB_WORKFLOW_REF": policy.workflow_uri(ref).removeprefix(policy.SERVER + "/")}
    for name, value in fixed.items():
        if environment.get(name) != value:
            raise ValueError(f"{name} is {environment.get(name)!r}; this {event} run's check runs only as {value!r}.")
    formats = {"GITHUB_SHA": r"[0-9a-f]{40}(?:[0-9a-f]{24})?", "GITHUB_WORKFLOW_SHA": r"[0-9a-f]{40}(?:[0-9a-f]{24})?",
               "GITHUB_REPOSITORY_ID": r"[1-9][0-9]*", "GITHUB_REPOSITORY_OWNER_ID": r"[1-9][0-9]*",
               "GITHUB_RUN_ID": r"[1-9][0-9]*", "GITHUB_RUN_ATTEMPT": r"[1-9][0-9]*"}
    for name, pattern in formats.items():
        if re.fullmatch(pattern, environment.get(name, "")) is None:
            raise ValueError(f"{name} is {environment.get(name)!r}; expected it to match {pattern!r}.")
    return {"repository_id": environment["GITHUB_REPOSITORY_ID"], "owner_id": environment["GITHUB_REPOSITORY_OWNER_ID"],
            "sha": environment["GITHUB_SHA"], "workflow_sha": environment["GITHUB_WORKFLOW_SHA"], "event": event,
            "ref": ref, "tag": tag, "run_id": environment["GITHUB_RUN_ID"],
            "run_attempt": int(environment["GITHUB_RUN_ATTEMPT"])}


def publish_attempt(environment: Mapping[str, str], run_attempt: int) -> int:
    """Read which attempt of this run uploaded the release, from the upload job's output.

    `pypi-publish` reports its run attempt (`RELEASE_PUBLISH_ATTEMPT`). A failed-jobs re-run of the provenance job
    alone keeps that output from the attempt that uploaded, so it may be below this run's attempt; the attestations
    name it.

    Raises:
        ValueError: When the output is missing or malformed, or names an attempt after this one.
    """
    attempt = environment.get("RELEASE_PUBLISH_ATTEMPT", "")
    if re.fullmatch(r"[1-9][0-9]*", attempt) is None or int(attempt) > run_attempt:
        raise ValueError(f"RELEASE_PUBLISH_ATTEMPT must be an attempt of this run up to {run_attempt}; got "
                         f"{attempt!r}.")
    return int(attempt)


def release_identity(context: ReleaseContext, attempt: int,
                     policy: type[ReleaseProvenancePolicy] = ReleaseProvenancePolicy) -> ExpectedIdentity:
    """Return the signing identity every released file's attestation must carry (layer 4).

    PyPI takes a file name once and the upload job never skips an existing file, so every file of this release was
    uploaded, and signed, by this run's upload attempt: the publication workflow at the run's ref and commit, from
    the run's event, in the `pypi` environment, on a GitHub-hosted runner of this public repository. Every claim is
    exact; unlike the candidate check, nothing is matched by pattern.

    Args:
        context: The checked run identity (`release_context`).
        attempt: The attempt that uploaded (`publish_attempt`).
        policy: The identity's fixed values; `ReleaseProvenancePolicy` in CI.
    """
    signer = policy.workflow_uri(context["ref"])
    exact = {
        FulcioClaim.ISSUER: policy.ISSUER, FulcioClaim.BUILD_SIGNER_URI: signer,
        FulcioClaim.BUILD_SIGNER_DIGEST: context["workflow_sha"], FulcioClaim.RUNNER_ENVIRONMENT: policy.RUNNER,
        FulcioClaim.SOURCE_REPOSITORY_URI: f"{policy.SERVER}/{policy.REPOSITORY}",
        FulcioClaim.SOURCE_REPOSITORY_DIGEST: context["sha"], FulcioClaim.SOURCE_REPOSITORY_REF: context["ref"],
        FulcioClaim.SOURCE_REPOSITORY_IDENTIFIER: context["repository_id"],
        FulcioClaim.SOURCE_REPOSITORY_OWNER_URI: f"{policy.SERVER}/{policy.OWNER}",
        FulcioClaim.SOURCE_REPOSITORY_OWNER_IDENTIFIER: context["owner_id"],
        FulcioClaim.BUILD_CONFIG_URI: signer, FulcioClaim.BUILD_CONFIG_DIGEST: context["workflow_sha"],
        FulcioClaim.BUILD_TRIGGER: context["event"],
        FulcioClaim.RUN_INVOCATION_URI: (f"{policy.SERVER}/{policy.REPOSITORY}/actions/runs/{context['run_id']}"
                                         f"/attempts/{attempt}"),
        FulcioClaim.SOURCE_REPOSITORY_VISIBILITY: policy.VISIBILITY,
        FulcioClaim.DEPLOYMENT_ENVIRONMENT: policy.ENVIRONMENT,
        FulcioClaim.TOKEN_SUBJECT: f"repo:{policy.REPOSITORY}:environment:{policy.ENVIRONMENT}",
    }
    return {"san": signer, "exact": exact, "patterns": {}}


def released_files(directory: pathlib.Path, version: str, tag: str) -> dict[str, FileIdentity]:
    """Verify the downloaded distributions again and return each file's identity.

    The wheel and sdist must be the verified pair for this version, and a release tag must name that version
    (`verify_distributions`), so the digests the provenance must name are this run's build.

    Raises:
        ValueError: When the files or the tag are not the release's.
    """
    verify_distributions(directory, version, tag)
    return {path.name: file_identity(path) for path in sorted(directory.iterdir())}


def verify_release(directory: pathlib.Path, report: pathlib.Path, environment: Mapping[str, str]) -> None:
    """Verify every released file's PyPI provenance in five layers, then write the evidence report.

    The run's identity is checked first, then the built files are verified again against the version and the
    release tag. The recorded control and every released file are checked with the candidate check's own layers
    (1, 2, 4 and 5) before the tool environment is built, so a wrong signer refuses before anything is installed;
    the pinned tool then checks layers 3 and 4 for all of them in one process, and its verdicts count only when it
    verified the genuine control and refused both tampered copies. The report is written only after every check
    has passed.

    Raises:
        ValueError: Naming the file and what differs, for any refused layer, run variable or file.
        urllib.error.URLError: When PyPI could not be read after the bounded retries.
        subprocess.CalledProcessError: When the tool environment could not be built or the verifier could not run.
    """
    policy = ReleaseProvenancePolicy
    context = release_context(environment)
    attempt = publish_attempt(environment, context["run_attempt"])
    version = package_version()
    files = released_files(directory, version, context["tag"])
    expected = release_identity(context, attempt)
    with tempfile.TemporaryDirectory(prefix="melder-release-provenance-",
                                     dir=environment.get("RUNNER_TEMP")) as scratch:
        root = pathlib.Path(scratch)
        entries = control_entries()
        evidence: dict[str, dict[str, object]] = {}
        for name, identity in files.items():
            raw = fetch_provenance(version, name, policy)
            try:
                document = json.loads(raw)
            except json.JSONDecodeError as error:
                raise ValueError(f"PyPI's provenance of {name} is not JSON.") from error
            attestation = single_attestation(document, name, policy.publisher())
            check_statement(attestation, name, identity["sha256"], name)
            certificate = certificate_identity(certificate_der(attestation, name))
            check_identity(certificate, expected, name)
            stored = root / f"{name}.provenance.json"
            stored.write_bytes(raw)
            entries.append({"id": f"{policy.ENTRY_PREFIX}:{name}", "name": name, "sha256": identity["sha256"],
                            "provenance": str(stored), "identity": {**expected, "issuer": policy.ISSUER}})
            evidence[name] = {"run_invocation": certificate["claims"][FulcioClaim.RUN_INVOCATION_URI],
                              "build_trigger": certificate["claims"][FulcioClaim.BUILD_TRIGGER]}
        require_outcomes(run_verifier(tool_environment(root), entries, root), sorted(files), policy.ENTRY_PREFIX)
    write_report(report, version, files, evidence, context, attempt)


def write_report(path: pathlib.Path, version: str, files: Mapping[str, FileIdentity],
                 evidence: Mapping[str, Mapping[str, object]], context: ReleaseContext, attempt: int) -> None:
    """Retain this release's verified provenance identity as a small, credential-free JSON report.

    It names the index, the version, each file's sha256 and size and the run and trigger its certificate names, the
    publisher and signer checked, the controls' verdicts, and the run: repository, checked-out commit, event, ref,
    run, attempt and the attempt that uploaded.
    """
    policy = ReleaseProvenancePolicy
    path.parent.mkdir(parents=True, exist_ok=True)
    report = {
        "status": "provenance-verified", "index": policy.INDEX_NAME, "version": version, "files": dict(files),
        "provenance": dict(evidence), "publisher": policy.publisher(), "signer": policy.workflow_uri(context["ref"]),
        "controls": {ProvenanceControl.GOOD: "verified", ProvenanceControl.WRONG_DIGEST: "refused",
                     ProvenanceControl.WRONG_SIGNER: "refused"},
        "repository": policy.REPOSITORY, "commit": git_output(("rev-parse", "HEAD^{commit}")),
        "event": context["event"], "ref": context["ref"], "run_id": context["run_id"],
        "run_attempt": context["run_attempt"], "publish_attempt": attempt,
    }
    path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")


def main(argv: Optional[Sequence[str]] = None) -> int:
    """Verify the release's PyPI provenance; never upload or install anything but the pinned tool."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("operation", choices=("verify",))
    parser.add_argument("--directory", type=pathlib.Path, default=pathlib.Path("dist"))
    parser.add_argument("--report", type=pathlib.Path, required=True)
    args = parser.parse_args(argv)
    verify_release(args.directory, args.report, os.environ)
    print(f"OK: {args.operation}; report={args.report}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
