"""Prove the release provenance check: PyPI's attestation of every released file, checked after the upload.

The release check runs the candidate check's five layers (`test_candidate_provenance.py` proves them) with the
publication workflow's identity. These tests prove what is the release's own: its policy, the run identity of a
published release and of a manual dispatch on prod, the signer every released file must name, PyPI's Integrity API,
and the whole check with every network and process boundary replaced. The recorded control - PyPI's real
provenance of the pypi-attestations 0.0.30 wheel, signed by a `release` event at a tag in the `pypi` environment -
proves that the release identity reproduces a real release certificate claim for claim. Nothing reaches PyPI,
Sigstore or pip.
"""

import base64
import hashlib
import io
import json
import pathlib
import subprocess
import time
import urllib.error
import urllib.request
from collections.abc import Mapping, Sequence
from types import ModuleType
from typing import Optional

import pytest
import yaml

from tests.unit.github_workflows.test_candidate_provenance import Der, Signer, control_document, copy_tool_directory


class ReleaseSigner:
    """The identity a release run of python-publish.yml signs with, written out independently of the script."""

    PREFIX = "1.3.6.1.4.1.57264.1."
    SHA = "c" * 40
    WORKFLOW_SHA = "d" * 40
    TAG = "v0.2.8300"
    TAG_REF = "refs/tags/v0.2.8300"
    PROD_REF = "refs/heads/prod"
    ISSUER = "https://token.actions.githubusercontent.com"
    PUBLISHER: Mapping[str, str] = {"kind": "GitHub", "repository": "Synaptic724/melder",
                                    "workflow": "python-publish.yml", "environment": "pypi"}

    @staticmethod
    def workflow(ref: str) -> str:
        """Return python-publish.yml's URI at a ref: the SAN, Build Signer URI and Build Config URI."""
        return f"https://github.com/Synaptic724/melder/.github/workflows/python-publish.yml@{ref}"

    @classmethod
    def claims(cls, ref: str = TAG_REF, run: str = "4004", attempt: str = "1",
               trigger: str = "release") -> dict[str, str]:
        """Return every claim Fulcio writes for a run of python-publish.yml in the pypi environment."""
        oid = cls.PREFIX
        workflow = cls.workflow(ref)
        return {
            oid + "1": cls.ISSUER, oid + "2": trigger, oid + "3": cls.SHA, oid + "4": "Publish Python Package",
            oid + "5": "Synaptic724/melder", oid + "6": ref,
            oid + "8": cls.ISSUER, oid + "9": workflow, oid + "10": cls.WORKFLOW_SHA, oid + "11": "github-hosted",
            oid + "12": "https://github.com/Synaptic724/melder", oid + "13": cls.SHA, oid + "14": ref,
            oid + "15": "1001",
            oid + "16": "https://github.com/Synaptic724", oid + "17": "2002", oid + "18": workflow,
            oid + "19": cls.WORKFLOW_SHA, oid + "20": trigger,
            oid + "21": f"https://github.com/Synaptic724/melder/actions/runs/{run}/attempts/{attempt}",
            oid + "22": "public", oid + "23": "pypi", oid + "24": "repo:Synaptic724/melder:environment:pypi",
        }

    @classmethod
    def certificate(cls, claims: Mapping[str, str], sans: Sequence[str] = ()) -> bytes:
        """Return a certificate carrying these claims and SANs (by default the Build Signer URI the claims name)."""
        return Der.certificate([Der.subject_names(*(sans or (claims[cls.PREFIX + "9"],))),
                                *(Der.claim(oid, value) for oid, value in claims.items())])

    @classmethod
    def provenance(cls, name: str, sha256: str, claims: Mapping[str, str],
                   publisher: Optional[Mapping[str, str]] = None) -> dict[str, object]:
        """Return a provenance as PyPI's Integrity API answers it, holding one attestation of one file.

        It is the candidate tests' provenance of the file with this signer's certificate and PyPI's publisher record.
        """
        document = Signer.provenance(name, sha256, claims, publisher=publisher or cls.PUBLISHER)
        material = document["attestation_bundles"][0]["attestations"][0]["verification_material"]
        material["certificate"] = base64.b64encode(cls.certificate(claims)).decode("ascii")
        return document

    @classmethod
    def environment(cls, **changes: str) -> dict[str, str]:
        """Return the provenance job's variables for a published release (attempt 2 re-running the check alone)."""
        values = {
            "GITHUB_SERVER_URL": "https://github.com", "GITHUB_REPOSITORY": "Synaptic724/melder",
            "GITHUB_REF": cls.TAG_REF,
            "GITHUB_WORKFLOW_REF": cls.workflow(cls.TAG_REF).removeprefix("https://github.com/"),
            "GITHUB_SHA": cls.SHA, "GITHUB_WORKFLOW_SHA": cls.WORKFLOW_SHA, "GITHUB_REPOSITORY_ID": "1001",
            "GITHUB_REPOSITORY_OWNER_ID": "2002", "GITHUB_RUN_ID": "4004", "GITHUB_RUN_ATTEMPT": "2",
            "GITHUB_EVENT_NAME": "release", "RELEASE_TAG": cls.TAG, "RELEASE_PUBLISH_ATTEMPT": "1",
        }
        values.update(changes)
        return values

    @classmethod
    def dispatch_environment(cls, **changes: str) -> dict[str, str]:
        """Return the provenance job's variables for a manual dispatch on prod, which has no release tag."""
        return cls.environment(**{"GITHUB_REF": cls.PROD_REF, "GITHUB_EVENT_NAME": "workflow_dispatch",
                                  "GITHUB_WORKFLOW_REF": cls.workflow(cls.PROD_REF).removeprefix("https://github.com/"),
                                  "RELEASE_TAG": "", **changes})


def identity_of(release_provenance: ModuleType, claims: Mapping[str, str],
                sans: Sequence[str] = ()) -> dict[str, object]:
    """Read back what the script sees in a synthetic release certificate."""
    return release_provenance.certificate_identity(ReleaseSigner.certificate(claims, sans))


def expected_for(release_provenance: ModuleType, environment: Mapping[str, str],
                 attempt: int = 1) -> dict[str, object]:
    """Return what the script demands of every released file in the run an environment describes."""
    return release_provenance.release_identity(release_provenance.release_context(environment), attempt)


def test_the_release_policy_is_the_publication_workflows_trusted_publisher(release_provenance: ModuleType) -> None:
    """PyPI's publisher record and signer: this repository's python-publish.yml in pypi, read from pypi.org."""
    policy = release_provenance.ReleaseProvenancePolicy
    assert policy.publisher() == dict(ReleaseSigner.PUBLISHER)
    assert policy.INDEX_NAME == "PyPI" and policy.INTEGRITY_ROOT == "https://pypi.org/integrity/melder/"
    assert policy.workflow_uri(ReleaseSigner.TAG_REF) == ReleaseSigner.workflow(ReleaseSigner.TAG_REF)
    assert policy.workflow_uri() == ReleaseSigner.workflow(ReleaseSigner.PROD_REF)
    assert set(policy.TRIGGERS) == {"release", "workflow_dispatch"} and policy.ENTRY_PREFIX == "release"
    shared = release_provenance.ProvenancePolicy
    assert issubclass(policy, shared)
    for name in ("SERVER", "REPOSITORY", "OWNER", "ISSUER", "RUNNER", "VISIBILITY", "STATEMENT_TYPE",
                 "PUBLISH_PREDICATE", "INTEGRITY_MEDIA_TYPE", "TOOL_INDEX", "TOOL_LOCK", "VERIFIER"):
        assert getattr(policy, name) == getattr(shared, name), name
    assert policy.tool_directory() == shared.tool_directory()


def test_the_expected_publisher_is_the_job_that_uploads(release_provenance: ModuleType, policy: ModuleType) -> None:
    """The identity the check demands is pypi-publish's own: this workflow, its environment, its events and prod."""
    root = pathlib.Path(__file__).resolve().parents[3]
    release = release_provenance.ReleaseProvenancePolicy
    document = yaml.load((root / ".github/workflows" / release.WORKFLOW).read_text(encoding="utf-8"),
                         Loader=yaml.BaseLoader)
    upload_job = document["jobs"]["pypi-publish"]
    assert upload_job["environment"]["name"] == release.ENVIRONMENT
    assert set(document["on"]) == set(release.TRIGGERS)
    upload = upload_job["steps"][-1]
    assert upload["uses"].startswith("pypa/gh-action-pypi-publish@") and "repository-url" not in upload["with"]
    # A manual dispatch is publication only on prod (ci_policy.py), the ref the check expects without a tag.
    sha = "e" * 40
    policy.validate_release("workflow_dispatch", release.REF, {}, sha, sha, sha)
    with pytest.raises(ValueError, match="Manual publication must run on prod"):
        policy.validate_release("workflow_dispatch", "refs/heads/release_candidate", {}, sha, sha, sha)


def test_the_candidate_policy_keeps_its_index_and_takes_a_ref(provenance: ModuleType) -> None:
    """The shared layers read TestPyPI from the candidate's policy, whose signer URI can be asked at any ref."""
    candidate = provenance.ProvenancePolicy
    assert candidate.INDEX_NAME == "TestPyPI" and candidate.USER_AGENT == "melder-candidate-ci"
    assert candidate.workflow_uri() == Signer.WORKFLOW
    assert candidate.workflow_uri("refs/heads/dev") == Signer.WORKFLOW.replace("release_candidate", "dev")
    assert "new candidate version" in candidate.missing_provenance("m.whl")


def test_a_published_release_runs_at_its_tag(release_provenance: ModuleType) -> None:
    """A release event's run is at refs/tags/<its tag>, with its repository, owner, commits, run and attempt."""
    assert release_provenance.release_context(ReleaseSigner.environment()) == {
        "repository_id": "1001", "owner_id": "2002", "sha": ReleaseSigner.SHA,
        "workflow_sha": ReleaseSigner.WORKFLOW_SHA,
        "event": "release", "ref": ReleaseSigner.TAG_REF, "tag": ReleaseSigner.TAG, "run_id": "4004", "run_attempt": 2,
    }


def test_a_manual_dispatch_runs_on_prod_without_a_tag(release_provenance: ModuleType) -> None:
    """A manual dispatch is checked at refs/heads/prod and carries no release tag."""
    context = release_provenance.release_context(ReleaseSigner.dispatch_environment(GITHUB_SHA="f" * 64,
                                                                                  GITHUB_WORKFLOW_SHA="f" * 64))
    assert (context["event"], context["ref"], context["tag"]) == ("workflow_dispatch", ReleaseSigner.PROD_REF, "")
    assert context["sha"] == context["workflow_sha"] == "f" * 64


@pytest.mark.parametrize(("changes", "name"), [
    ({"GITHUB_SERVER_URL": "https://github.example.com"}, "GITHUB_SERVER_URL"),
    ({"GITHUB_REPOSITORY": "someone/melder"}, "GITHUB_REPOSITORY"),
    ({"GITHUB_REF": "refs/tags/v0.2.8299"}, "GITHUB_REF"),
    ({"GITHUB_REF": "refs/heads/prod"}, "GITHUB_REF"),
    ({"GITHUB_WORKFLOW_REF": "Synaptic724/melder/.github/workflows/ci.yml@refs/tags/v0.2.8300"}, "GITHUB_WORKFLOW_REF"),
    ({"GITHUB_WORKFLOW_REF": "Synaptic724/melder/.github/workflows/python-publish.yml@refs/heads/prod"},
     "GITHUB_WORKFLOW_REF"),
    ({"GITHUB_EVENT_NAME": "push"}, "GITHUB_EVENT_NAME"),
    ({"GITHUB_EVENT_NAME": "pull_request"}, "GITHUB_EVENT_NAME"),
    ({"GITHUB_EVENT_NAME": ""}, "GITHUB_EVENT_NAME"),
    ({"RELEASE_TAG": ""}, "RELEASE_TAG"),
    ({"GITHUB_SHA": "c" * 39}, "GITHUB_SHA"),
    ({"GITHUB_WORKFLOW_SHA": "D" * 40}, "GITHUB_WORKFLOW_SHA"),
    ({"GITHUB_REPOSITORY_ID": "0"}, "GITHUB_REPOSITORY_ID"),
    ({"GITHUB_REPOSITORY_OWNER_ID": "02002"}, "GITHUB_REPOSITORY_OWNER_ID"),
    ({"GITHUB_RUN_ID": "x"}, "GITHUB_RUN_ID"),
    ({"GITHUB_RUN_ATTEMPT": "0"}, "GITHUB_RUN_ATTEMPT"),
])
def test_the_check_runs_only_as_this_repositorys_release(release_provenance: ModuleType, changes: dict[str, str],
                                                         name: str) -> None:
    """Another server, repository, tag, workflow or event, or a malformed identifier, is refused before any fetch."""
    with pytest.raises(ValueError, match=name):
        release_provenance.release_context(ReleaseSigner.environment(**changes))


@pytest.mark.parametrize(("changes", "message"), [
    ({"RELEASE_TAG": "v0.2.8300"}, "RELEASE_TAG is 'v0.2.8300'; a manual dispatch publishes from refs/heads/prod"),
    ({"GITHUB_REF": "refs/heads/dev",
      "GITHUB_WORKFLOW_REF": "Synaptic724/melder/.github/workflows/python-publish.yml@refs/heads/dev"}, "GITHUB_REF"),
])
def test_a_manual_dispatch_publishes_only_from_prod_with_no_tag(release_provenance: ModuleType,
                                                                changes: dict[str, str], message: str) -> None:
    """A dispatch that carries a release tag, or runs on another branch, is refused, the tag by its own rule."""
    with pytest.raises(ValueError, match=message):
        release_provenance.release_context(ReleaseSigner.dispatch_environment(**changes))


def test_a_missing_run_variable_is_refused(release_provenance: ModuleType) -> None:
    """An absent variable is refused, not read as empty or defaulted."""
    environment = ReleaseSigner.environment()
    del environment["GITHUB_REPOSITORY_ID"]
    with pytest.raises(ValueError, match="GITHUB_REPOSITORY_ID"):
        release_provenance.release_context(environment)


def test_the_publish_attempt_is_the_upload_jobs_own(release_provenance: ModuleType) -> None:
    """The attempt that uploaded may be this one or, after a re-run of the check alone, an earlier one."""
    assert release_provenance.publish_attempt({"RELEASE_PUBLISH_ATTEMPT": "1"}, 2) == 1
    assert release_provenance.publish_attempt({"RELEASE_PUBLISH_ATTEMPT": "2"}, 2) == 2


@pytest.mark.parametrize("attempt", [None, "", "0", "01", "x", "3"])
def test_a_malformed_or_future_publish_attempt_is_refused(release_provenance: ModuleType,
                                                          attempt: Optional[str]) -> None:
    """The publish attempt must be an attempt of this run no later than the current one."""
    environment = {} if attempt is None else {"RELEASE_PUBLISH_ATTEMPT": attempt}
    with pytest.raises(ValueError, match="RELEASE_PUBLISH_ATTEMPT"):
        release_provenance.publish_attempt(environment, 2)


def test_every_released_file_must_name_this_runs_upload_exactly(release_provenance: ModuleType) -> None:
    """Every claim is exact: the workflow at the tag, the commit, this run's upload attempt and event; no pattern."""
    expected = expected_for(release_provenance, ReleaseSigner.environment(), attempt=1)
    claims = ReleaseSigner.claims(ref=ReleaseSigner.TAG_REF, run="4004", attempt="1", trigger="release")
    assert expected == {"san": ReleaseSigner.workflow(ReleaseSigner.TAG_REF), "patterns": {},
                        "exact": {oid: value for oid, value in claims.items() if int(oid.rsplit(".", 1)[1]) >= 8}}
    release_provenance.check_identity(identity_of(release_provenance, claims), expected, "melder.whl")


def test_a_dispatched_release_must_name_prod(release_provenance: ModuleType) -> None:
    """A manual dispatch's files name the workflow on prod and the workflow_dispatch event."""
    expected = expected_for(release_provenance, ReleaseSigner.dispatch_environment(), attempt=1)
    claims = ReleaseSigner.claims(ref=ReleaseSigner.PROD_REF, trigger="workflow_dispatch")
    assert expected["san"] == ReleaseSigner.workflow(ReleaseSigner.PROD_REF) and expected["patterns"] == {}
    release_provenance.check_identity(identity_of(release_provenance, claims), expected, "melder.whl")
    with pytest.raises(ValueError, match="Source Repository Ref"):
        release_provenance.check_identity(identity_of(release_provenance, ReleaseSigner.claims(
            ref=ReleaseSigner.TAG_REF, trigger="workflow_dispatch"), (ReleaseSigner.workflow(ReleaseSigner.PROD_REF),)),
            expected, "melder.whl")


@pytest.mark.parametrize(("change", "name"), [
    ({"21": "https://github.com/Synaptic724/melder/actions/runs/4004/attempts/2"}, "Run Invocation URI"),
    ({"21": "https://github.com/Synaptic724/melder/actions/runs/4005/attempts/1"}, "Run Invocation URI"),
    ({"20": "workflow_dispatch", "2": "workflow_dispatch"}, "Build Trigger"),
    ({"14": "refs/heads/prod", "6": "refs/heads/prod"}, "Source Repository Ref"),
    ({"13": "e" * 40, "3": "e" * 40}, "Source Repository Digest"),
    ({"10": "e" * 40}, "Build Signer Digest"),
    ({"19": "e" * 40}, "Build Config Digest"),
    ({"23": "pypitest"}, "Deployment Environment"),
    ({"24": "repo:Synaptic724/melder:environment:pypitest"}, "Token Subject"),
    ({"15": "1002"}, "Source Repository Identifier"),
    ({"17": "2003"}, "Source Repository Owner Identifier"),
    ({"11": "self-hosted"}, "Runner Environment"),
    ({"22": "private"}, "Source Repository Visibility At Signing"),
    ({"18": ReleaseSigner.workflow(ReleaseSigner.TAG_REF).replace("python-publish", "release-candidate")},
     "Build Config URI"),
])
def test_every_release_claim_is_checked_on_its_own(release_provenance: ModuleType, change: dict[str, str],
                                                   name: str) -> None:
    """Changing any one claim refuses the file, naming that claim with what was expected and what was found."""
    claims = {**ReleaseSigner.claims(), **{ReleaseSigner.PREFIX + arc: value for arc, value in change.items()}}
    with pytest.raises(ValueError, match=name) as refusal:
        release_provenance.check_identity(identity_of(release_provenance, claims),
                                          expected_for(release_provenance, ReleaseSigner.environment()),
                                          "melder-0.2.8300.tar.gz")
    assert "melder-0.2.8300.tar.gz" in str(refusal.value)


def test_a_candidate_attestation_cannot_pass_as_a_release(release_provenance: ModuleType) -> None:
    """A file the candidate run signed for TestPyPI names another workflow, ref and environment: refused here."""
    candidate = Der.certificate([Der.subject_names(Signer.WORKFLOW),
                                 *(Der.claim(oid, value) for oid, value in Signer.claims().items())])
    with pytest.raises(ValueError) as refusal:
        release_provenance.check_identity(release_provenance.certificate_identity(candidate),
                                          expected_for(release_provenance, ReleaseSigner.environment()), "melder.whl")
    message = str(refusal.value)
    for claim in ("subject alternative names", "Build Signer URI", "Deployment Environment", "Token Subject"):
        assert claim in message, claim


class ControlRelease:
    """The real control's run, as the release check would see it: pypi/pypi-attestations' release of v0.0.30."""

    ENVIRONMENT: Mapping[str, str] = {
        "GITHUB_SERVER_URL": "https://github.com", "GITHUB_REPOSITORY": "pypi/pypi-attestations",
        "GITHUB_REF": "refs/tags/v0.0.30",
        "GITHUB_WORKFLOW_REF": "pypi/pypi-attestations/.github/workflows/release.yml@refs/tags/v0.0.30",
        "GITHUB_SHA": "845bfac2f2912912fb2d1ab96775ac75708279c4",
        "GITHUB_WORKFLOW_SHA": "845bfac2f2912912fb2d1ab96775ac75708279c4", "GITHUB_REPOSITORY_ID": "772247423",
        "GITHUB_REPOSITORY_OWNER_ID": "2964877", "GITHUB_RUN_ID": "30366799661", "GITHUB_RUN_ATTEMPT": "1",
        "GITHUB_EVENT_NAME": "release", "RELEASE_TAG": "v0.0.30",
    }

    @staticmethod
    def policy(release_provenance: ModuleType) -> type:
        """Return the release policy with the control's repository and workflow in place of Melder's."""
        class Policy(release_provenance.ReleaseProvenancePolicy):
            """pypi/pypi-attestations' PyPI Trusted Publisher: release.yml in the pypi environment."""

            OWNER = "pypi"
            REPOSITORY = "pypi/pypi-attestations"
            WORKFLOW = "release.yml"

        return Policy


def test_the_release_identity_reproduces_a_real_release_attestation(release_provenance: ModuleType) -> None:
    """The release rules, given the control's run, demand exactly the claims PyPI's real attestation carries.

    The control was signed by a published GitHub release at its tag in the `pypi` environment, the kind of run
    Melder's publication is, so this is the release identity checked against a real Fulcio certificate rather than
    against claims written for the test.
    """
    control = release_provenance.ProvenanceControl
    policy = ControlRelease.policy(release_provenance)
    context = release_provenance.release_context(ControlRelease.ENVIRONMENT, policy)
    expected = release_provenance.release_identity(context, 1, policy)
    assert expected == {"san": control.SAN, "exact": dict(control.CLAIMS), "patterns": {}}
    document = control_document(release_provenance)
    attestation = release_provenance.single_attestation(document, "the control", policy.publisher())
    der = release_provenance.certificate_der(attestation, "the control")
    certificate = release_provenance.certificate_identity(der)
    release_provenance.check_identity(certificate, expected, "the control")
    release_provenance.check_statement(attestation, control.NAME, control.SHA256, "the control")
    with pytest.raises(ValueError, match="Run Invocation URI"):
        release_provenance.check_identity(certificate, release_provenance.release_identity(context, 2, policy),
                                          "the control")


class Answer(io.BytesIO):
    """One urlopen answer: its body and the URL it was finally served from."""

    def __init__(self, body: bytes, url: str) -> None:
        """Hold the body to read and the URL urllib reports after any redirect."""
        super().__init__(body)
        self.url = url


def pypi_url(name: str) -> str:
    """Return the address of one released file's provenance on PyPI's Integrity API."""
    return f"https://pypi.org/integrity/melder/0.2.8300/{name}/provenance"


def test_the_release_reads_pypis_integrity_api_without_credentials(release_provenance: ModuleType,
                                                                  monkeypatch: pytest.MonkeyPatch) -> None:
    """One request to the file's provenance on pypi.org, as the release check, with no credentials."""
    name = "melder-0.2.8300-py3-none-any.whl"
    answers: list[Answer] = []

    def answer(request: urllib.request.Request, timeout: int) -> Answer:
        """Check the request at the network boundary and answer it."""
        assert request.full_url == pypi_url(name)
        assert request.get_header("Accept") == "application/vnd.pypi.integrity.v1+json"
        assert request.get_header("User-agent") == "melder-release-ci"
        assert request.get_header("Authorization") is None and timeout == 30
        answers.append(Answer(b'{"version": 1}', pypi_url(name)))
        return answers[-1]

    monkeypatch.setattr(urllib.request, "urlopen", answer)
    monkeypatch.setattr(time, "sleep", lambda seconds: pytest.fail("a definitive answer was retried"))
    policy = release_provenance.ReleaseProvenancePolicy
    assert release_provenance.fetch_provenance("0.2.8300", name, policy) == b'{"version": 1}'
    assert len(answers) == 1 and answers[0].closed


def test_a_released_file_pypi_never_attested_is_refused_with_what_to_check(release_provenance: ModuleType,
                                                                          monkeypatch: pytest.MonkeyPatch) -> None:
    """A 404 that outlasts every retry means no attestation; the refusal says the file is out and what to check."""
    calls: list[str] = []

    def missing(request: urllib.request.Request, timeout: int) -> None:
        """Answer 404 every time."""
        calls.append(request.full_url)
        raise urllib.error.HTTPError(request.full_url, 404, "Not Found", {}, None)

    monkeypatch.setattr(urllib.request, "urlopen", missing)
    monkeypatch.setattr(time, "sleep", lambda seconds: None)
    policy = release_provenance.ReleaseProvenancePolicy
    with pytest.raises(ValueError, match="PyPI holds no provenance for m.whl") as refusal:
        release_provenance.fetch_provenance("0.2.8300", "m.whl", policy)
    assert "cannot be replaced" in str(refusal.value) and "BRANCH_WORKFLOW.md" in str(refusal.value)
    assert calls == [pypi_url("m.whl")] * policy.LOOKUP_ATTEMPTS


def test_a_redirected_release_answer_is_refused_naming_pypi(release_provenance: ModuleType,
                                                           monkeypatch: pytest.MonkeyPatch) -> None:
    """An answer served from another URL is not the file's provenance."""
    monkeypatch.setattr(urllib.request, "urlopen", lambda request, timeout: Answer(b"{}", "https://example.com/x"))
    with pytest.raises(ValueError, match="PyPI answered the provenance of m.whl from https://example.com/x"):
        release_provenance.fetch_provenance("0.2.8300", "m.whl", release_provenance.ReleaseProvenancePolicy)


@pytest.mark.parametrize(("changes", "message"), [
    ({}, None),
    ({"release:b.tar.gz": {"outcome": "refused", "reason": "bad signature"}}, "b.tar.gz: bad signature"),
    ({"control:wrong-signer": {"outcome": "verified"}}, "not checking"),
])
def test_release_entries_are_judged_by_their_own_prefix(release_provenance: ModuleType,
                                                        changes: dict[str, Mapping[str, str]],
                                                        message: Optional[str]) -> None:
    """The verifier's verdicts on `release:` entries decide, after the controls split as they must."""
    outcomes: dict[str, Mapping[str, str]] = {
        "control:known-good": {"outcome": "verified"}, "control:wrong-digest": {"outcome": "refused"},
        "control:wrong-signer": {"outcome": "refused"}, "release:a.whl": {"outcome": "verified"},
        "release:b.tar.gz": {"outcome": "verified"}, **changes,
    }
    if message is None:
        release_provenance.require_outcomes(outcomes, ["a.whl", "b.tar.gz"], "release")
    else:
        with pytest.raises(ValueError, match=message) as refusal:
            release_provenance.require_outcomes(outcomes, ["a.whl", "b.tar.gz"], "release")
        assert "TestPyPI" not in str(refusal.value)


def test_released_files_must_be_this_tags_version(release_provenance: ModuleType, tmp_path: pathlib.Path) -> None:
    """The downloaded pair is verified again with the release tag, which must name the package version."""
    (tmp_path / "melder-0.2.8300-py3-none-any.whl").write_bytes(b"wheel")
    (tmp_path / "melder-0.2.8300.tar.gz").write_bytes(b"sdist")
    with pytest.raises(ValueError, match="Release tag 'v0.2.8299' does not match package version '0.2.8300'"):
        release_provenance.released_files(tmp_path, "0.2.8300", "v0.2.8299")


def test_released_files_returns_each_files_digest_after_the_check(release_provenance: ModuleType,
                                                                 tmp_path: pathlib.Path,
                                                                 monkeypatch: pytest.MonkeyPatch) -> None:
    """After the distributions pass, each file is identified by its sha256 and size, in name order."""
    checked: list[tuple[pathlib.Path, str, str]] = []
    monkeypatch.setattr(release_provenance, "verify_distributions",
                        lambda directory, version, tag: checked.append((directory, version, tag)))
    (tmp_path / "b.tar.gz").write_bytes(b"sdist")
    (tmp_path / "a.whl").write_bytes(b"wheel")
    files = release_provenance.released_files(tmp_path, "0.2.8300", "")
    assert checked == [(tmp_path, "0.2.8300", "")]
    assert list(files) == ["a.whl", "b.tar.gz"]
    assert files["a.whl"] == {"sha256": hashlib.sha256(b"wheel").hexdigest(), "size": 5}


class ReleaseRun:
    """A Release / provenance job with every network and process boundary replaced, recording what crossed each one.

    PyPI answers from `documents`; the distributions are given (`released_files` is replaced and records its
    arguments); the pinned tool is never built (its environment is a path) and the verifier process reads each
    request, records the provenance bytes every entry points at and answers from `outcomes`.
    """

    def __init__(self, release_provenance: ModuleType, monkeypatch: pytest.MonkeyPatch,
                 tmp_path: pathlib.Path) -> None:
        """Install the replacements on the loaded script for this test only."""
        self.files = {"melder-0.2.8300-py3-none-any.whl": {"sha256": "1" * 64, "size": 100},
                      "melder-0.2.8300.tar.gz": {"sha256": "2" * 64, "size": 200}}
        self.module = release_provenance
        self.documents: dict[str, bytes] = {}
        self.fetched: list[tuple[str, str, type]] = []
        self.selected: list[tuple[pathlib.Path, str, str]] = []
        self.tools: list[pathlib.Path] = []
        self.requests: list[dict[str, object]] = []
        self.stored: dict[str, bytes] = {}
        self.outcomes: dict[str, Mapping[str, str]] = {
            "control:wrong-digest": {"outcome": "refused", "reason": "subject does not match"},
            "control:wrong-signer": {"outcome": "refused", "reason": "SANs do not match"},
        }
        self.directory = tmp_path / "dist"
        self.report = tmp_path / "reports" / "provenance.json"
        self.scratch = tmp_path
        monkeypatch.setattr(release_provenance, "package_version", lambda: "0.2.8300")
        monkeypatch.setattr(release_provenance, "released_files", self.select)
        monkeypatch.setattr(release_provenance, "fetch_provenance", self.fetch)
        monkeypatch.setattr(release_provenance, "tool_environment", self.tool)
        monkeypatch.setattr(release_provenance, "git_output", lambda arguments: ReleaseSigner.SHA)
        monkeypatch.setattr(subprocess, "run", self.verifier)

    def select(self, directory: pathlib.Path, version: str, tag: str) -> dict[str, dict[str, object]]:
        """Stand in for re-verifying the downloaded pair, recording the version and tag it was asked for."""
        self.selected.append((directory, version, tag))
        return self.files

    def fetch(self, version: str, name: str, policy: type) -> bytes:
        """Answer one file's provenance as PyPI would, recording the index the check asked."""
        self.fetched.append((version, name, policy))
        return self.documents[name]

    def tool(self, root: pathlib.Path) -> pathlib.Path:
        """Stand in for building the tool environment inside the job's scratch directory."""
        self.tools.append(root)
        return root / "tools" / "bin" / "python"

    def verifier(self, command: list[str], check: bool, cwd: pathlib.Path) -> None:
        """Play the verifier process: record the request and the files it names, then answer every entry."""
        assert check and command[1] == "-I" and command[2].endswith("verify_attestations.py")
        request = json.loads(pathlib.Path(command[command.index("--request") + 1]).read_text(encoding="utf-8"))
        self.requests.append(request)
        self.stored.update({entry["id"]: pathlib.Path(entry["provenance"]).read_bytes()
                            for entry in request["entries"]})
        results = [{"id": entry["id"], **self.outcomes.get(entry["id"], {"outcome": "verified"})}
                   for entry in request["entries"]]
        pathlib.Path(command[command.index("--result") + 1]).write_text(
            json.dumps({"format": 1, "results": results}), encoding="utf-8")

    def serve(self, wheel: Mapping[str, str], sdist: Mapping[str, str],
              publisher: Optional[Mapping[str, str]] = None) -> None:
        """Make PyPI hold an attestation of each built file signed with these claims."""
        for (name, identity), claims in zip(self.files.items(), (wheel, sdist), strict=True):
            self.documents[name] = json.dumps(
                ReleaseSigner.provenance(name, str(identity["sha256"]), claims, publisher)).encode()

    def verify(self, environment: Mapping[str, str]) -> None:
        """Run the check as the job does, with its scratch space under this test's directory."""
        self.module.verify_release(self.directory, self.report, {**environment, "RUNNER_TEMP": str(self.scratch)})


def test_every_released_file_is_checked_in_all_five_layers(release_provenance: ModuleType, tmp_path: pathlib.Path,
                                                           monkeypatch: pytest.MonkeyPatch) -> None:
    """Both files of a published release pass; the tool sees exact identities and the report says who signed."""
    run = ReleaseRun(release_provenance, monkeypatch, tmp_path)
    run.serve(ReleaseSigner.claims(attempt="1"), ReleaseSigner.claims(attempt="1"))
    run.verify(ReleaseSigner.environment())
    policy = release_provenance.ReleaseProvenancePolicy
    assert run.selected == [(run.directory, "0.2.8300", ReleaseSigner.TAG)]
    assert run.fetched == [("0.2.8300", name, policy) for name in run.files]
    (request,) = run.requests
    assert [entry["id"] for entry in request["entries"]] == [
        "control:known-good", "control:wrong-digest", "control:wrong-signer",
        "release:melder-0.2.8300-py3-none-any.whl", "release:melder-0.2.8300.tar.gz"]
    expected = expected_for(release_provenance, ReleaseSigner.environment(), attempt=1)
    for entry, (name, identity) in zip(request["entries"][3:], run.files.items(), strict=True):
        assert entry["identity"] == {**expected, "issuer": ReleaseSigner.ISSUER}
        assert entry["name"] == name and entry["sha256"] == identity["sha256"]
        assert run.stored[f"release:{name}"] == run.documents[name]
    assert run.tools == [run.tools[0]] and run.tools[0].parent == tmp_path
    invocation = "https://github.com/Synaptic724/melder/actions/runs/4004/attempts/1"
    assert json.loads(run.report.read_text(encoding="utf-8")) == {
        "status": "provenance-verified", "index": "PyPI", "version": "0.2.8300", "files": run.files,
        "provenance": {name: {"run_invocation": invocation, "build_trigger": "release"} for name in run.files},
        "publisher": dict(ReleaseSigner.PUBLISHER), "signer": ReleaseSigner.workflow(ReleaseSigner.TAG_REF),
        "controls": {"control:known-good": "verified", "control:wrong-digest": "refused",
                     "control:wrong-signer": "refused"},
        "repository": "Synaptic724/melder", "commit": ReleaseSigner.SHA, "event": "release",
        "ref": ReleaseSigner.TAG_REF, "run_id": "4004", "run_attempt": 2, "publish_attempt": 1,
    }


def test_a_dispatched_release_is_checked_against_prod(release_provenance: ModuleType, tmp_path: pathlib.Path,
                                                      monkeypatch: pytest.MonkeyPatch) -> None:
    """A manual dispatch's files are checked without a tag, as the workflow on prod, from workflow_dispatch."""
    run = ReleaseRun(release_provenance, monkeypatch, tmp_path)
    claims = ReleaseSigner.claims(ref=ReleaseSigner.PROD_REF, trigger="workflow_dispatch", attempt="2")
    run.serve(claims, claims)
    run.verify(ReleaseSigner.dispatch_environment(RELEASE_PUBLISH_ATTEMPT="2"))
    assert run.selected == [(run.directory, "0.2.8300", "")]
    report = json.loads(run.report.read_text(encoding="utf-8"))
    assert (report["event"], report["ref"], report["publish_attempt"]) == ("workflow_dispatch",
                                                                          ReleaseSigner.PROD_REF, 2)
    assert report["signer"] == ReleaseSigner.workflow(ReleaseSigner.PROD_REF)


@pytest.mark.parametrize(("sdist", "publisher", "message"), [
    (ReleaseSigner.claims(attempt="2"), None, "Run Invocation URI"),
    (Signer.claims(), None, "does not name the expected signer"),
    (ReleaseSigner.claims(), {**ReleaseSigner.PUBLISHER, "workflow": "release-candidate.yml"},
     "not the expected Trusted Publisher"),
    (ReleaseSigner.claims(), {**ReleaseSigner.PUBLISHER, "environment": "pypitest"},
     "environment is 'pypitest', expected 'pypi'"),
])
def test_a_wrong_signer_or_publisher_is_refused_before_the_tool_is_built(release_provenance: ModuleType,
                                                                        tmp_path: pathlib.Path,
                                                                        monkeypatch: pytest.MonkeyPatch,
                                                                        sdist: dict[str, str],
                                                                        publisher: Optional[dict[str, str]],
                                                                        message: str) -> None:
    """The script's own layers refuse first: no tool environment, no verifier process, no report.

    The sdist was signed by another attempt, or by the candidate's TestPyPI identity, or PyPI's record names
    another publisher.
    """
    run = ReleaseRun(release_provenance, monkeypatch, tmp_path)
    run.serve(ReleaseSigner.claims(), sdist)
    if publisher is not None:
        name = "melder-0.2.8300.tar.gz"
        run.documents[name] = json.dumps(ReleaseSigner.provenance(name, "2" * 64, sdist, publisher)).encode()
    with pytest.raises(ValueError, match=message) as refusal:
        run.verify(ReleaseSigner.environment())
    assert "melder-0.2.8300.tar.gz" in str(refusal.value)
    assert run.tools == [] and run.requests == [] and not run.report.exists()


def test_sigstore_refusing_a_released_file_fails_without_a_report(release_provenance: ModuleType,
                                                                  tmp_path: pathlib.Path,
                                                                  monkeypatch: pytest.MonkeyPatch) -> None:
    """Every stdlib layer can pass and Sigstore still refuse (a forged certificate); that refusal decides."""
    run = ReleaseRun(release_provenance, monkeypatch, tmp_path)
    run.serve(ReleaseSigner.claims(), ReleaseSigner.claims())
    run.outcomes["release:melder-0.2.8300.tar.gz"] = {"outcome": "refused", "reason": "invalid signature"}
    with pytest.raises(ValueError, match="Sigstore refused the attestation of melder-0.2.8300.tar.gz: invalid"):
        run.verify(ReleaseSigner.environment())
    assert len(run.requests) == 1 and not run.report.exists()


def test_an_unreadable_release_provenance_is_refused_by_name(release_provenance: ModuleType, tmp_path: pathlib.Path,
                                                             monkeypatch: pytest.MonkeyPatch) -> None:
    """A provenance answer that is not JSON names the file and stops the check."""
    run = ReleaseRun(release_provenance, monkeypatch, tmp_path)
    run.documents = {name: b"<html>maintenance</html>" for name in run.files}
    with pytest.raises(ValueError, match="PyPI's provenance of melder-0.2.8300-py3-none-any.whl is not JSON"):
        run.verify(ReleaseSigner.environment())
    assert run.tools == [] and not run.report.exists()


def test_the_run_is_checked_before_anything_is_read(release_provenance: ModuleType, tmp_path: pathlib.Path,
                                                    monkeypatch: pytest.MonkeyPatch) -> None:
    """A run at another ref, or without the upload's attempt, refuses before the files or PyPI are read."""
    run = ReleaseRun(release_provenance, monkeypatch, tmp_path)
    with pytest.raises(ValueError, match="GITHUB_REF"):
        run.verify(ReleaseSigner.environment(GITHUB_REF="refs/tags/v0.2.8299"))
    environment = ReleaseSigner.environment()
    del environment["RELEASE_PUBLISH_ATTEMPT"]
    with pytest.raises(ValueError, match="RELEASE_PUBLISH_ATTEMPT"):
        run.verify(environment)
    assert run.selected == [] and run.fetched == [] and run.tools == []


def test_the_controls_are_checked_before_pypi_is_asked(release_provenance: ModuleType, tmp_path: pathlib.Path,
                                                       monkeypatch: pytest.MonkeyPatch) -> None:
    """A lock that no longer installs the control stops the check before any released file is fetched."""
    run = ReleaseRun(release_provenance, monkeypatch, tmp_path)
    directory = copy_tool_directory(release_provenance, tmp_path / "provenance")
    lock = directory / release_provenance.ProvenancePolicy.TOOL_LOCK
    lock.write_text(lock.read_text(encoding="utf-8").replace("pypi-attestations==0.0.30", "pypi-attestations==0.1.0"),
                    encoding="utf-8")
    monkeypatch.setattr(release_provenance.ProvenancePolicy, "tool_directory", staticmethod(lambda: directory))
    with pytest.raises(ValueError, match="pypi-attestations==0.1.0"):
        run.verify(ReleaseSigner.environment())
    assert run.fetched == [] and run.tools == []


def test_the_command_line_verifies_dist_and_names_its_report(release_provenance: ModuleType, tmp_path: pathlib.Path,
                                                            monkeypatch: pytest.MonkeyPatch,
                                                            capsys: pytest.CaptureFixture[str]) -> None:
    """`verify` checks dist/ with the job's environment and prints where the report is; nothing else is offered."""
    calls: list[tuple[pathlib.Path, pathlib.Path, Mapping[str, str]]] = []
    monkeypatch.setattr(release_provenance, "verify_release",
                        lambda directory, report, environment: calls.append((directory, report, environment)))
    report = tmp_path / "provenance.json"
    assert release_provenance.main(["verify", "--report", str(report)]) == 0
    assert calls == [(pathlib.Path("dist"), report, release_provenance.os.environ)]
    assert capsys.readouterr().out == f"OK: verify; report={report}\n"
    with pytest.raises(SystemExit):
        release_provenance.main(["upload", "--report", str(report)])
