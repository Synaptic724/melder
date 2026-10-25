"""Verify the PEP 740 provenance of every candidate file on TestPyPI before any probe installs one.

The release candidate's provenance job runs `verify` after the upload. For every built distribution it reads the
provenance that TestPyPI's Integrity API holds and checks it in five layers:

1. a provenance exists;
2. its one bundle's publisher record is this repository's release-candidate workflow in the `pypitest`
   environment;
3. Sigstore verifies its one attestation on the production trust root (certificate chain, transparency log,
   signature);
4. the signing certificate carries this run's identity, claim by claim;
5. the attested statement names exactly this file and its sha256, with the PyPI publish predicate.

Layers 1, 2, 4 and 5 are checked here with the standard library; layer 4 by reading the certificate's extensions
from its DER. Layers 3 and 4 are then checked by the pinned pypi-attestations and sigstore in their own environment
(`.github/provenance/verify_attestations.py`), which first has to verify a recorded genuine attestation and refuse
two tampered copies of it, so a tool that cannot verify, or does not check, fails the run instead of passing it.
"""

import argparse
import base64
import json
import os
import pathlib
import re
import subprocess
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request
import venv
from collections.abc import Mapping, Sequence
from typing import Optional, TypedDict

from ci_policy import git_output, object_value, text_value
from testpypi_candidate import FileIdentity, TestIndexPolicy, package_version, verified_files


class RunContext(TypedDict):
    """This run's identity, read from GitHub's default environment variables and checked before use."""

    repository_id: str
    owner_id: str
    sha: str
    workflow_sha: str
    event: str
    run_id: str
    run_attempt: int


class ExpectedIdentity(TypedDict):
    """The signing identity one attestation must carry: its one SAN and its Fulcio claims, exact or by pattern."""

    san: str
    exact: dict[str, str]
    patterns: dict[str, str]


class CertificateIdentity(TypedDict):
    """What a signing certificate says about its signer: its URI subject alternative names and its Fulcio claims."""

    sans: list[str]
    claims: dict[str, str]


class ProvenancePolicy:
    """Hold the candidate provenance check's fixed identity, endpoints and retry bounds.

    The identity is the TestPyPI Trusted Publisher the owner configures (BRANCH_WORKFLOW.md): this repository, the
    `release-candidate.yml` workflow on `release_candidate`, the `pypitest` environment. Change it here, and only
    deliberately, when one of those changes.
    """

    INTEGRITY_ROOT = "https://test.pypi.org/integrity/melder/"
    INTEGRITY_MEDIA_TYPE = "application/vnd.pypi.integrity.v1+json"
    SERVER = "https://github.com"
    OWNER = "Synaptic724"
    REPOSITORY = "Synaptic724/melder"
    WORKFLOW = "release-candidate.yml"
    REF = "refs/heads/release_candidate"
    ENVIRONMENT = "pypitest"
    ISSUER = "https://token.actions.githubusercontent.com"
    RUNNER = "github-hosted"
    VISIBILITY = "public"
    TRIGGERS: tuple[str, ...] = ("push", "workflow_dispatch")
    STATEMENT_TYPE = "https://in-toto.io/Statement/v1"
    PUBLISH_PREDICATE = "https://docs.pypi.org/attestations/publish/v1"
    # TestPyPI may answer 404 for a moment after an upload; a 404 that outlasts every attempt means no provenance.
    LOOKUP_ATTEMPTS = 6
    RETRY_SECONDS = 10
    TOOL_INDEX = "https://pypi.org/simple/"
    TOOL_LOCK = "requirements.txt"
    VERIFIER = "verify_attestations.py"

    @classmethod
    def publisher(cls) -> dict[str, str]:
        """Return the publisher record TestPyPI must hold for every candidate file (layer 2)."""
        return {"kind": "GitHub", "repository": cls.REPOSITORY, "workflow": cls.WORKFLOW,
                "environment": cls.ENVIRONMENT}

    @classmethod
    def workflow_uri(cls) -> str:
        """Return the signing workflow's URI: the certificate's SAN, Build Signer URI and Build Config URI."""
        return f"{cls.SERVER}/{cls.REPOSITORY}/.github/workflows/{cls.WORKFLOW}@{cls.REF}"

    @staticmethod
    def tool_directory() -> pathlib.Path:
        """Return `.github/provenance/`, which holds the verifier, its hashed lock and the recorded control."""
        return pathlib.Path(__file__).resolve().parents[1] / "provenance"


class FulcioClaim:
    """Name the Fulcio signing-certificate extensions that identify a GitHub Actions signer.

    The OIDs and their meaning are Fulcio's (sigstore/fulcio, docs/oid-info.md). The claims from .8 on are DER
    UTF8Strings; the deprecated GitHub-specific claims .1 to .6, which Fulcio still writes, are raw text, and each
    must agree with its successor when present.
    """

    PREFIX = "1.3.6.1.4.1.57264.1."
    ISSUER_V1 = PREFIX + "1"
    TRIGGER_V1 = PREFIX + "2"
    SHA_V1 = PREFIX + "3"
    NAME_V1 = PREFIX + "4"
    REPOSITORY_V1 = PREFIX + "5"
    REF_V1 = PREFIX + "6"
    ISSUER = PREFIX + "8"
    BUILD_SIGNER_URI = PREFIX + "9"
    BUILD_SIGNER_DIGEST = PREFIX + "10"
    RUNNER_ENVIRONMENT = PREFIX + "11"
    SOURCE_REPOSITORY_URI = PREFIX + "12"
    SOURCE_REPOSITORY_DIGEST = PREFIX + "13"
    SOURCE_REPOSITORY_REF = PREFIX + "14"
    SOURCE_REPOSITORY_IDENTIFIER = PREFIX + "15"
    SOURCE_REPOSITORY_OWNER_URI = PREFIX + "16"
    SOURCE_REPOSITORY_OWNER_IDENTIFIER = PREFIX + "17"
    BUILD_CONFIG_URI = PREFIX + "18"
    BUILD_CONFIG_DIGEST = PREFIX + "19"
    BUILD_TRIGGER = PREFIX + "20"
    RUN_INVOCATION_URI = PREFIX + "21"
    SOURCE_REPOSITORY_VISIBILITY = PREFIX + "22"
    DEPLOYMENT_ENVIRONMENT = PREFIX + "23"
    TOKEN_SUBJECT = PREFIX + "24"
    SUBJECT_ALTERNATIVE_NAME = "2.5.29.17"
    RAW: tuple[str, ...] = (ISSUER_V1, TRIGGER_V1, SHA_V1, NAME_V1, REPOSITORY_V1, REF_V1)
    TEXT: tuple[str, ...] = (ISSUER, BUILD_SIGNER_URI, BUILD_SIGNER_DIGEST, RUNNER_ENVIRONMENT, SOURCE_REPOSITORY_URI,
                             SOURCE_REPOSITORY_DIGEST, SOURCE_REPOSITORY_REF, SOURCE_REPOSITORY_IDENTIFIER,
                             SOURCE_REPOSITORY_OWNER_URI, SOURCE_REPOSITORY_OWNER_IDENTIFIER, BUILD_CONFIG_URI,
                             BUILD_CONFIG_DIGEST, BUILD_TRIGGER, RUN_INVOCATION_URI, SOURCE_REPOSITORY_VISIBILITY,
                             DEPLOYMENT_ENVIRONMENT, TOKEN_SUBJECT)
    LEGACY: Mapping[str, str] = {ISSUER_V1: ISSUER, TRIGGER_V1: BUILD_TRIGGER, SHA_V1: SOURCE_REPOSITORY_DIGEST,
                                 REF_V1: SOURCE_REPOSITORY_REF}
    NAMES: Mapping[str, str] = {
        ISSUER: "Issuer", BUILD_SIGNER_URI: "Build Signer URI", BUILD_SIGNER_DIGEST: "Build Signer Digest",
        RUNNER_ENVIRONMENT: "Runner Environment", SOURCE_REPOSITORY_URI: "Source Repository URI",
        SOURCE_REPOSITORY_DIGEST: "Source Repository Digest", SOURCE_REPOSITORY_REF: "Source Repository Ref",
        SOURCE_REPOSITORY_IDENTIFIER: "Source Repository Identifier",
        SOURCE_REPOSITORY_OWNER_URI: "Source Repository Owner URI",
        SOURCE_REPOSITORY_OWNER_IDENTIFIER: "Source Repository Owner Identifier",
        BUILD_CONFIG_URI: "Build Config URI", BUILD_CONFIG_DIGEST: "Build Config Digest",
        BUILD_TRIGGER: "Build Trigger", RUN_INVOCATION_URI: "Run Invocation URI",
        SOURCE_REPOSITORY_VISIBILITY: "Source Repository Visibility At Signing",
        DEPLOYMENT_ENVIRONMENT: "Deployment Environment", TOKEN_SUBJECT: "Token Subject",
    }

    @classmethod
    def describe(cls, oid: str) -> str:
        """Return a claim's name with its OID, for a refusal message."""
        return f"{cls.NAMES.get(oid, 'claim')} ({oid})"


class ProvenanceControl:
    """A recorded genuine attestation that proves the pinned tool can verify and can refuse.

    The control is PyPI's provenance of the pypi-attestations 0.0.30 wheel, the very file the tool lock installs,
    recorded from PyPI's Integrity API on 2026-10-24 (`known_good_provenance.json`). The tool must verify it and
    refuse two tampered copies: one with another digest, one expecting another signer. Its sha256 must be among
    the lock's hashes for that wheel, so moving the lock without refreshing the control fails here.
    """

    FIXTURE = "known_good_provenance.json"
    PROJECT = "pypi-attestations"
    VERSION = "0.0.30"
    NAME = "pypi_attestations-0.0.30-py3-none-any.whl"
    SHA256 = "b3a9c53f6cb89e5e7b5b70e6cfca97cfc66008c1ed54087355e06e40071cef21"
    PUBLISHER: Mapping[str, str] = {"kind": "GitHub", "repository": "pypi/pypi-attestations",
                                    "workflow": "release.yml", "environment": "pypi"}
    SAN = "https://github.com/pypi/pypi-attestations/.github/workflows/release.yml@refs/tags/v0.0.30"
    WRONG_SAN = "https://github.com/pypi/pypi-attestations/.github/workflows/release.yml@refs/tags/v0.0.29"
    COMMIT = "845bfac2f2912912fb2d1ab96775ac75708279c4"
    CLAIMS: Mapping[str, str] = {
        FulcioClaim.ISSUER: "https://token.actions.githubusercontent.com",
        FulcioClaim.BUILD_SIGNER_URI: SAN, FulcioClaim.BUILD_SIGNER_DIGEST: COMMIT,
        FulcioClaim.RUNNER_ENVIRONMENT: "github-hosted",
        FulcioClaim.SOURCE_REPOSITORY_URI: "https://github.com/pypi/pypi-attestations",
        FulcioClaim.SOURCE_REPOSITORY_DIGEST: COMMIT, FulcioClaim.SOURCE_REPOSITORY_REF: "refs/tags/v0.0.30",
        FulcioClaim.SOURCE_REPOSITORY_IDENTIFIER: "772247423",
        FulcioClaim.SOURCE_REPOSITORY_OWNER_URI: "https://github.com/pypi",
        FulcioClaim.SOURCE_REPOSITORY_OWNER_IDENTIFIER: "2964877",
        FulcioClaim.BUILD_CONFIG_URI: SAN, FulcioClaim.BUILD_CONFIG_DIGEST: COMMIT,
        FulcioClaim.BUILD_TRIGGER: "release",
        FulcioClaim.RUN_INVOCATION_URI: "https://github.com/pypi/pypi-attestations/actions/runs/30366799661/attempts/1",
        FulcioClaim.SOURCE_REPOSITORY_VISIBILITY: "public", FulcioClaim.DEPLOYMENT_ENVIRONMENT: "pypi",
        FulcioClaim.TOKEN_SUBJECT: "repo:pypi/pypi-attestations:environment:pypi",
    }
    GOOD = "control:known-good"
    WRONG_DIGEST = "control:wrong-digest"
    WRONG_SIGNER = "control:wrong-signer"

    @classmethod
    def expected(cls, san: Optional[str] = None) -> ExpectedIdentity:
        """Return the control's signing identity, or the same identity with another SAN."""
        return {"san": san or cls.SAN, "exact": dict(cls.CLAIMS), "patterns": {}}

    @classmethod
    def entry(cls, entry_id: str, sha256: str, identity: ExpectedIdentity,
              fixture: pathlib.Path) -> dict[str, object]:
        """Return one verifier entry for the recorded control, with the digest and signer it is checked against."""
        return {"id": entry_id, "name": cls.NAME, "sha256": sha256, "provenance": str(fixture),
                "identity": {**identity, "issuer": ProvenancePolicy.ISSUER}}


class DerReader:
    """Read the DER a signing certificate's extensions are written in, refusing every form DER does not allow.

    It reads structure only - tags, lengths, object identifiers, strings - and verifies nothing; the certificate's
    authenticity is layer 3's job. Every read is bounded by its parent element.
    """

    @staticmethod
    def element(data: bytes, offset: int, end: int) -> tuple[int, int, int]:
        """Return the tag, the value's start and the value's end of the element at offset.

        Raises:
            ValueError: For a truncated element, a multi-byte tag, an indefinite, oversized or non-minimal length,
                or an element that overruns end.
        """
        if offset + 2 > end:
            raise ValueError("The signing certificate's DER is truncated.")
        tag, first = data[offset], data[offset + 1]
        if tag & 0x1F == 0x1F:
            raise ValueError("The signing certificate's DER uses a multi-byte tag.")
        start = offset + 2
        length = first
        if first & 0x80:
            count = first & 0x7F
            if count == 0 or count > 4 or start + count > end:
                raise ValueError("The signing certificate's DER uses an indefinite or oversized length.")
            length = int.from_bytes(data[start:start + count], "big")
            if length < 0x80 or data[start] == 0:
                raise ValueError("The signing certificate's DER uses a non-minimal length.")
            start += count
        if start + length > end:
            raise ValueError("A DER element overruns the element that holds it.")
        return tag, start, start + length

    @classmethod
    def children(cls, data: bytes, start: int, end: int) -> list[tuple[int, int, int]]:
        """Return every element between start and end, which must tile that span exactly."""
        items: list[tuple[int, int, int]] = []
        offset = start
        while offset < end:
            items.append(cls.element(data, offset, end))
            offset = items[-1][2]
        return items

    @staticmethod
    def object_identifier(value: bytes) -> str:
        """Decode a DER OBJECT IDENTIFIER's value into its dotted form.

        Raises:
            ValueError: For an empty value, a non-minimal arc or an unterminated last arc.
        """
        if not value or value[-1] & 0x80:
            raise ValueError("The signing certificate holds a malformed object identifier.")
        arcs: list[int] = []
        current = 0
        fresh = True
        for byte in value:
            if fresh and byte == 0x80:
                raise ValueError("The signing certificate holds a non-minimal object identifier.")
            current = (current << 7) | (byte & 0x7F)
            fresh = not byte & 0x80
            if fresh:
                arcs.append(current)
                current = 0
        head = min(arcs[0] // 40, 2)
        return ".".join(str(arc) for arc in (head, arcs[0] - 40 * head, *arcs[1:]))


def certificate_identity(der: bytes) -> CertificateIdentity:
    """Read a signing certificate's subject alternative names and Fulcio claims from its DER.

    Only the extensions block of the to-be-signed certificate is read. Claims under Fulcio's prefix are decoded
    when their OID is one this check knows (raw text for .1 to .6, a DER UTF8String from .8 on); others are left
    out. A repeated extension, or a subject alternative name that is not a URI, is refused.

    Raises:
        ValueError: When the DER is not one certificate, has no extensions block, or any part of it is malformed.
    """
    tag, start, end = DerReader.element(der, 0, len(der))
    parts = DerReader.children(der, start, end) if tag == 0x30 and end == len(der) else []
    if len(parts) != 3 or parts[0][0] != 0x30:
        raise ValueError("The signing certificate is not one DER certificate.")
    blocks = [item for item in DerReader.children(der, parts[0][1], parts[0][2]) if item[0] == 0xA3]
    inner = DerReader.children(der, blocks[0][1], blocks[0][2]) if len(blocks) == 1 else []
    if len(inner) != 1 or inner[0][0] != 0x30:
        raise ValueError("The signing certificate has no extensions block.")
    identity: CertificateIdentity = {"sans": [], "claims": {}}
    seen: set[str] = set()
    for extension in DerReader.children(der, inner[0][1], inner[0][2]):
        oid, value = extension_value(der, extension)
        if oid in seen:
            raise ValueError(f"The signing certificate repeats extension {oid}.")
        seen.add(oid)
        if oid == FulcioClaim.SUBJECT_ALTERNATIVE_NAME:
            identity["sans"] = uri_names(value)
        elif oid in FulcioClaim.RAW:
            identity["claims"][oid] = value.decode("utf-8")
        elif oid in FulcioClaim.TEXT:
            text = DerReader.element(value, 0, len(value))
            if text[0] != 0x0C or text[2] != len(value):
                raise ValueError(f"Certificate claim {FulcioClaim.describe(oid)} is not one DER UTF8String.")
            identity["claims"][oid] = value[text[1]:text[2]].decode("utf-8")
    return identity


def extension_value(der: bytes, extension: tuple[int, int, int]) -> tuple[str, bytes]:
    """Return one Extension's dotted OID and the content of its OCTET STRING value.

    An Extension is SEQUENCE { extnID OBJECT IDENTIFIER, critical BOOLEAN DEFAULT FALSE, extnValue OCTET STRING }.

    Raises:
        ValueError: When the element does not have that shape.
    """
    fields = DerReader.children(der, extension[1], extension[2]) if extension[0] == 0x30 else []
    if (len(fields) not in (2, 3) or fields[0][0] != 0x06 or fields[-1][0] != 0x04
            or (len(fields) == 3 and fields[1][0] != 0x01)):
        raise ValueError("The signing certificate holds a malformed extension.")
    oid = DerReader.object_identifier(der[fields[0][1]:fields[0][2]])
    return oid, der[fields[-1][1]:fields[-1][2]]


def uri_names(value: bytes) -> list[str]:
    """Return the URIs of a SubjectAlternativeName extension's GeneralNames, refusing every other kind of name."""
    tag, start, end = DerReader.element(value, 0, len(value))
    if tag != 0x30 or end != len(value):
        raise ValueError("The signing certificate's subject alternative names are malformed.")
    names: list[str] = []
    for kind, name_start, name_end in DerReader.children(value, start, end):
        if kind != 0x86:
            raise ValueError(f"The signing certificate names a subject that is not a URI (tag {kind:#04x}).")
        names.append(value[name_start:name_end].decode("ascii"))
    return names


def check_identity(identity: CertificateIdentity, expected: ExpectedIdentity, label: str) -> None:
    """Require the certificate to carry exactly the expected signer, claim by claim (layer 4).

    The certificate must have exactly one subject alternative name, the expected one; every exact claim must be
    present and equal; every pattern claim present and matched in full; and every deprecated GitHub claim Fulcio
    still writes must agree with its successor. All differences are reported together.

    Raises:
        ValueError: Naming each claim that differs, with what was expected and what the certificate holds.
    """
    problems: list[str] = []
    if identity["sans"] != [expected["san"]]:
        problems.append(f"its subject alternative names are {identity['sans']}, expected exactly "
                        f"[{expected['san']!r}]")
    claims = identity["claims"]
    for oid, value in expected["exact"].items():
        if claims.get(oid) != value:
            problems.append(f"{FulcioClaim.describe(oid)} is {claims.get(oid)!r}, expected {value!r}")
    for oid, pattern in expected["patterns"].items():
        found = claims.get(oid)
        if found is None or re.fullmatch(pattern, found) is None:
            problems.append(f"{FulcioClaim.describe(oid)} is {found!r}, which does not match {pattern!r}")
    for legacy, successor in FulcioClaim.LEGACY.items():
        if legacy in claims and claims[legacy] != claims.get(successor):
            problems.append(f"deprecated claim {legacy} is {claims[legacy]!r} but {FulcioClaim.describe(successor)} "
                            f"is {claims.get(successor)!r}")
    if FulcioClaim.REPOSITORY_V1 in claims and claims.get(FulcioClaim.SOURCE_REPOSITORY_URI) != (
            f"{ProvenancePolicy.SERVER}/{claims[FulcioClaim.REPOSITORY_V1]}"):
        problems.append(f"deprecated claim {FulcioClaim.REPOSITORY_V1} is {claims[FulcioClaim.REPOSITORY_V1]!r} but "
                        f"{FulcioClaim.describe(FulcioClaim.SOURCE_REPOSITORY_URI)} is "
                        f"{claims.get(FulcioClaim.SOURCE_REPOSITORY_URI)!r}")
    if problems:
        raise ValueError(f"The signing certificate of {label} does not name the expected signer: "
                         + "; ".join(problems) + ".")


def run_context(environment: Mapping[str, str]) -> RunContext:
    """Read and check this run's identity from GitHub's default environment variables.

    The run must belong to the expected repository, server, ref and workflow, from an allowed event; its commit
    SHAs must be full and its numeric identifiers decimal.

    Raises:
        ValueError: Naming the variable that is missing or differs.
    """
    fixed = {"GITHUB_SERVER_URL": ProvenancePolicy.SERVER, "GITHUB_REPOSITORY": ProvenancePolicy.REPOSITORY,
             "GITHUB_REF": ProvenancePolicy.REF,
             "GITHUB_WORKFLOW_REF": ProvenancePolicy.workflow_uri().removeprefix(ProvenancePolicy.SERVER + "/")}
    for name, value in fixed.items():
        if environment.get(name) != value:
            raise ValueError(f"{name} is {environment.get(name)!r}; the provenance check runs only as {value!r}.")
    formats = {"GITHUB_SHA": r"[0-9a-f]{40}(?:[0-9a-f]{24})?", "GITHUB_WORKFLOW_SHA": r"[0-9a-f]{40}(?:[0-9a-f]{24})?",
               "GITHUB_REPOSITORY_ID": r"[1-9][0-9]*", "GITHUB_REPOSITORY_OWNER_ID": r"[1-9][0-9]*",
               "GITHUB_RUN_ID": r"[1-9][0-9]*", "GITHUB_RUN_ATTEMPT": r"[1-9][0-9]*",
               "GITHUB_EVENT_NAME": "|".join(ProvenancePolicy.TRIGGERS)}
    for name, pattern in formats.items():
        if re.fullmatch(pattern, environment.get(name, "")) is None:
            raise ValueError(f"{name} is {environment.get(name)!r}; expected it to match {pattern!r}.")
    return {"repository_id": environment["GITHUB_REPOSITORY_ID"], "owner_id": environment["GITHUB_REPOSITORY_OWNER_ID"],
            "sha": environment["GITHUB_SHA"], "workflow_sha": environment["GITHUB_WORKFLOW_SHA"],
            "event": environment["GITHUB_EVENT_NAME"], "run_id": environment["GITHUB_RUN_ID"],
            "run_attempt": int(environment["GITHUB_RUN_ATTEMPT"])}


def upload_record(environment: Mapping[str, str], files: Mapping[str, FileIdentity],
                  run_attempt: int) -> tuple[frozenset[str], int]:
    """Read which files the publish job uploaded, and in which attempt, from its outputs.

    The publish job reports the files it staged (`CANDIDATE_UPLOADED`, a JSON list) and its run attempt
    (`CANDIDATE_PUBLISH_ATTEMPT`). A failed-jobs re-run of this job alone keeps both from the attempt that
    uploaded, so the attempt may be below this run's.

    Returns:
        The uploaded file names and the publish attempt.

    Raises:
        ValueError: When either output is missing or malformed, names a file this run did not build, or names an
            attempt after this one.
    """
    try:
        uploaded = json.loads(environment.get("CANDIDATE_UPLOADED", ""))
    except json.JSONDecodeError:
        uploaded = None
    if (not isinstance(uploaded, list) or not all(isinstance(name, str) for name in uploaded)
            or len(set(uploaded)) != len(uploaded) or not set(uploaded) <= set(files)):
        raise ValueError(f"CANDIDATE_UPLOADED must list distinct files of this build; got "
                         f"{environment.get('CANDIDATE_UPLOADED')!r}.")
    attempt = environment.get("CANDIDATE_PUBLISH_ATTEMPT", "")
    if re.fullmatch(r"[1-9][0-9]*", attempt) is None or int(attempt) > run_attempt:
        raise ValueError(f"CANDIDATE_PUBLISH_ATTEMPT must be an attempt of this run up to {run_attempt}; got "
                         f"{attempt!r}.")
    return frozenset(uploaded), int(attempt)


def expected_identity(context: RunContext, uploaded_here: bool, publish_attempt: int) -> ExpectedIdentity:
    """Return the signing identity a candidate file's attestation must carry.

    Every file was signed by this repository's release-candidate workflow on `release_candidate` at this commit,
    in the `pypitest` environment, on a GitHub-hosted runner. A file this run uploaded was signed by this run's
    publish attempt, from this run's event; a file TestPyPI already had was uploaded by an earlier run of the same
    workflow at the same commit (same-commit rebuilds hash the same, and prepare-upload refuses different bytes),
    from either allowed event.
    """
    policy = ProvenancePolicy
    exact = {
        FulcioClaim.ISSUER: policy.ISSUER, FulcioClaim.BUILD_SIGNER_URI: policy.workflow_uri(),
        FulcioClaim.BUILD_SIGNER_DIGEST: context["workflow_sha"], FulcioClaim.RUNNER_ENVIRONMENT: policy.RUNNER,
        FulcioClaim.SOURCE_REPOSITORY_URI: f"{policy.SERVER}/{policy.REPOSITORY}",
        FulcioClaim.SOURCE_REPOSITORY_DIGEST: context["sha"], FulcioClaim.SOURCE_REPOSITORY_REF: policy.REF,
        FulcioClaim.SOURCE_REPOSITORY_IDENTIFIER: context["repository_id"],
        FulcioClaim.SOURCE_REPOSITORY_OWNER_URI: f"{policy.SERVER}/{policy.OWNER}",
        FulcioClaim.SOURCE_REPOSITORY_OWNER_IDENTIFIER: context["owner_id"],
        FulcioClaim.BUILD_CONFIG_URI: policy.workflow_uri(), FulcioClaim.BUILD_CONFIG_DIGEST: context["workflow_sha"],
        FulcioClaim.SOURCE_REPOSITORY_VISIBILITY: policy.VISIBILITY,
        FulcioClaim.DEPLOYMENT_ENVIRONMENT: policy.ENVIRONMENT,
        FulcioClaim.TOKEN_SUBJECT: f"repo:{policy.REPOSITORY}:environment:{policy.ENVIRONMENT}",
    }
    runs = re.escape(f"{policy.SERVER}/{policy.REPOSITORY}/actions/runs/")
    if uploaded_here:
        exact[FulcioClaim.BUILD_TRIGGER] = context["event"]
        exact[FulcioClaim.RUN_INVOCATION_URI] = (f"{policy.SERVER}/{policy.REPOSITORY}/actions/runs/"
                                                 f"{context['run_id']}/attempts/{publish_attempt}")
        patterns: dict[str, str] = {}
    else:
        patterns = {FulcioClaim.BUILD_TRIGGER: "|".join(policy.TRIGGERS),
                    FulcioClaim.RUN_INVOCATION_URI: runs + r"[1-9][0-9]*/attempts/[1-9][0-9]*"}
    return {"san": policy.workflow_uri(), "exact": exact, "patterns": patterns}


def fetch_provenance(version: str, name: str) -> bytes:
    """Read one file's provenance from TestPyPI's Integrity API (layer 1).

    A 404 is retried, since TestPyPI may answer one for a moment after the upload, and so are the statuses in
    `TestIndexPolicy.TRANSIENT_STATUSES`, timeouts and failed connections: up to `LOOKUP_ATTEMPTS` tries,
    `RETRY_SECONDS` apart, each retry printed. Every other status raises at once. A response from any URL but the
    one asked for is refused. No credentials are sent.

    Raises:
        ValueError: When TestPyPI still answers 404 after the last attempt, or redirected the request.
        urllib.error.URLError: When the last attempt's failure was another HTTP status or a network error.
    """
    url = (ProvenancePolicy.INTEGRITY_ROOT + urllib.parse.quote(version, safe="") + "/"
           + urllib.parse.quote(name, safe="") + "/provenance")
    request = urllib.request.Request(url, headers={"User-Agent": "melder-candidate-ci",
                                                   "Accept": ProvenancePolicy.INTEGRITY_MEDIA_TYPE})
    attempt = 1
    while True:
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                if response.url != url:
                    raise ValueError(f"TestPyPI answered the provenance of {name} from {response.url}; "
                                     "refusing a redirected answer.")
                return response.read()
        except urllib.error.HTTPError as error:
            error.close()
            if error.code != 404 and error.code not in TestIndexPolicy.TRANSIENT_STATUSES:
                raise
            if attempt == ProvenancePolicy.LOOKUP_ATTEMPTS:
                if error.code == 404:
                    raise ValueError(
                        f"TestPyPI holds no provenance for {name}: it was uploaded without Trusted Publishing (by "
                        "an API token, before this check existed), or the upload's attestation was not accepted. "
                        "Choose a new candidate version so this workflow uploads every file with an attestation."
                    ) from error
                raise
            failure = f"HTTP {error.code}"
        except (urllib.error.URLError, TimeoutError, ConnectionError) as error:
            if attempt == ProvenancePolicy.LOOKUP_ATTEMPTS:
                raise
            failure = type(error).__name__
        print(f"TestPyPI provenance lookup for {name} failed ({failure}), attempt {attempt} of "
              f"{ProvenancePolicy.LOOKUP_ATTEMPTS}; retrying in {ProvenancePolicy.RETRY_SECONDS}s.", flush=True)
        time.sleep(ProvenancePolicy.RETRY_SECONDS)
        attempt += 1


def single_attestation(document: object, label: str, publisher: Mapping[str, str]) -> Mapping[str, object]:
    """Return a provenance's one attestation after checking its shape and publisher record (layer 2).

    The provenance must be version 1 with exactly one attestation bundle, whose publisher record holds every
    expected key with its expected value (other keys, such as `claims`, are allowed) and whose one attestation is
    version 1 with a certificate and at least one transparency-log entry.

    Raises:
        ValueError: Naming what differs.
    """
    provenance = object_value(document, f"The provenance of {label}")
    bundles = provenance.get("attestation_bundles")
    if provenance.get("version") != 1 or not isinstance(bundles, list) or len(bundles) != 1:
        raise ValueError(f"The provenance of {label} must be version 1 with exactly one attestation bundle.")
    bundle = object_value(bundles[0], f"The attestation bundle of {label}")
    record = object_value(bundle.get("publisher"), f"The publisher record of {label}")
    differences = [f"{key} is {record.get(key)!r}, expected {value!r}" for key, value in publisher.items()
                   if record.get(key) != value]
    if differences:
        raise ValueError(f"TestPyPI's publisher record for {label} is not the expected Trusted Publisher: "
                         + "; ".join(differences) + ".")
    attestations = bundle.get("attestations")
    if not isinstance(attestations, list) or len(attestations) != 1:
        raise ValueError(f"The provenance of {label} must hold exactly one attestation.")
    attestation = object_value(attestations[0], f"The attestation of {label}")
    material = object_value(attestation.get("verification_material"), f"The verification material of {label}")
    entries = material.get("transparency_entries")
    if attestation.get("version") != 1 or not isinstance(entries, list) or not entries:
        raise ValueError(f"The attestation of {label} must be version 1 with a transparency-log entry.")
    text_value(material.get("certificate"), f"The signing certificate of {label}")
    return attestation


def base64_field(value: object, label: str) -> bytes:
    """Decode one strict base64 field of an attestation, refusing anything else."""
    try:
        return base64.b64decode(text_value(value, label), validate=True)
    except ValueError as error:
        raise ValueError(f"{label} is not valid base64.") from error


def check_statement(attestation: Mapping[str, object], name: str, sha256: str, label: str) -> None:
    """Require the attested statement to name exactly this file and digest with the publish predicate (layer 5).

    Raises:
        ValueError: When the envelope or statement is malformed or differs from what the PyPI publish attestation
            of this exact file holds.
    """
    envelope = object_value(attestation.get("envelope"), f"The envelope of {label}")
    base64_field(envelope.get("signature"), f"The signature of {label}")
    try:
        statement = json.loads(base64_field(envelope.get("statement"), f"The statement of {label}"))
    except json.JSONDecodeError as error:
        raise ValueError(f"The statement of {label} is not JSON.") from error
    expected = {"_type": ProvenancePolicy.STATEMENT_TYPE, "subject": [{"name": name, "digest": {"sha256": sha256}}],
                "predicateType": ProvenancePolicy.PUBLISH_PREDICATE}
    found = object_value(statement, f"The statement of {label}")
    if set(found) != {*expected, "predicate"} or found.get("predicate") not in (None, {}) or any(
            found.get(key) != value for key, value in expected.items()):
        raise ValueError(f"The statement of {label} is {json.dumps(found, sort_keys=True)}; expected "
                         f"{json.dumps({**expected, 'predicate': None}, sort_keys=True)}.")


def certificate_der(attestation: Mapping[str, object], label: str) -> bytes:
    """Return the DER of an attestation's signing certificate."""
    material = object_value(attestation.get("verification_material"), f"The verification material of {label}")
    return base64_field(material.get("certificate"), f"The signing certificate of {label}")


def tool_pins(lock: str) -> dict[str, tuple[str, frozenset[str]]]:
    """Read a hashed requirements lock: each pin's version and its sha256 hashes.

    Raises:
        ValueError: When a requirement is not an exact `name==version` pin with at least one sha256 hash, or a
            name is pinned twice.
    """
    pins: dict[str, tuple[str, frozenset[str]]] = {}
    logical = " ".join(line.split("#", 1)[0] for line in lock.splitlines()).replace("\\", " ")
    for requirement in re.split(r"\s+(?=[A-Za-z0-9])", logical.strip()):
        match = re.fullmatch(r"([A-Za-z0-9][A-Za-z0-9._-]*)==([^\s=]+)((?:\s+--hash=sha256:[0-9a-f]{64})+)\s*",
                             requirement)
        if match is None or match.group(1).lower() in pins:
            raise ValueError(f"The tool lock holds a requirement that is not one hashed exact pin: {requirement!r}.")
        pins[match.group(1).lower()] = (match.group(2), frozenset(re.findall(r"[0-9a-f]{64}", match.group(3))))
    return pins


def control_entries() -> list[dict[str, object]]:
    """Check the recorded control with this script's own layers and return its three verifier entries.

    The control's sha256 must be one of the lock's hashes for the pypi-attestations wheel the lock installs. The
    entries are the genuine control, which the tool must verify, and two tampered copies it must refuse: another
    digest, and another expected signer.

    Raises:
        ValueError: When the fixture, the lock or their pairing is not as recorded.
    """
    directory = ProvenancePolicy.tool_directory()
    pins = tool_pins((directory / ProvenancePolicy.TOOL_LOCK).read_text(encoding="utf-8"))
    version, hashes = pins.get(ProvenanceControl.PROJECT, ("", frozenset()))
    if version != ProvenanceControl.VERSION or ProvenanceControl.SHA256 not in hashes:
        raise ValueError(f"The tool lock pins {ProvenanceControl.PROJECT}=={version or 'nothing'} without the "
                         f"control's wheel ({ProvenanceControl.SHA256}); refresh {ProvenanceControl.FIXTURE} for the "
                         "wheel the lock installs.")
    fixture = directory / ProvenanceControl.FIXTURE
    attestation = single_attestation(json.loads(fixture.read_bytes()), "the control", ProvenanceControl.PUBLISHER)
    check_statement(attestation, ProvenanceControl.NAME, ProvenanceControl.SHA256, "the control")
    check_identity(certificate_identity(certificate_der(attestation, "the control")), ProvenanceControl.expected(),
                   "the control")
    control = ProvenanceControl
    wrong_digest = control.SHA256[:-1] + ("0" if control.SHA256[-1] != "0" else "1")
    return [control.entry(control.GOOD, control.SHA256, control.expected(), fixture),
            control.entry(control.WRONG_DIGEST, wrong_digest, control.expected(), fixture),
            control.entry(control.WRONG_SIGNER, control.SHA256, control.expected(control.WRONG_SAN), fixture)]


def tool_environment(root: pathlib.Path) -> pathlib.Path:
    """Create a fresh environment of this interpreter with exactly the hashed tool lock installed.

    pip runs isolated from user and environment configuration, without its cache, dependency resolution or
    source builds, and refuses any file whose hash the lock does not list; `pip check` must then pass.

    Returns:
        The environment's interpreter.
    """
    environment = root / "tools"
    venv.EnvBuilder(with_pip=True).create(environment)
    python = environment / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
    lock = ProvenancePolicy.tool_directory() / ProvenancePolicy.TOOL_LOCK
    subprocess.run([str(python), "-m", "pip", "--isolated", "--disable-pip-version-check", "install",
                    "--no-cache-dir", "--no-deps", "--only-binary=:all:", "--require-hashes",
                    "--index-url", ProvenancePolicy.TOOL_INDEX, "-r", str(lock)], check=True, cwd=root)
    subprocess.run([str(python), "-m", "pip", "--isolated", "--disable-pip-version-check", "check"],
                   check=True, cwd=root)
    return python


def run_verifier(python: pathlib.Path, entries: Sequence[Mapping[str, object]],
                 root: pathlib.Path) -> dict[str, Mapping[str, object]]:
    """Run the pinned verifier on every entry and return its outcome for each, by entry id (layers 3 and 4).

    Raises:
        subprocess.CalledProcessError: When the verifier cannot do the work (for example, no trust root).
        ValueError: When its result is malformed or does not answer every entry exactly once.
    """
    request = root / "verifier-request.json"
    result = root / "verifier-result.json"
    request.write_text(json.dumps({"format": 1, "entries": list(entries)}, indent=2) + "\n", encoding="utf-8")
    subprocess.run([str(python), "-I", str(ProvenancePolicy.tool_directory() / ProvenancePolicy.VERIFIER),
                    "--request", str(request), "--result", str(result)], check=True, cwd=root)
    document = object_value(json.loads(result.read_text(encoding="utf-8")), "The verifier's result")
    results = document.get("results")
    if document.get("format") != 1 or not isinstance(results, list):
        raise ValueError("The verifier's result has another format.")
    outcomes: dict[str, Mapping[str, object]] = {}
    for value in results:
        item = object_value(value, "A verifier outcome")
        entry_id = text_value(item.get("id"), "A verifier outcome's id")
        if entry_id in outcomes or item.get("outcome") not in ("verified", "refused"):
            raise ValueError(f"The verifier answered {entry_id!r} twice or with an unknown outcome.")
        outcomes[entry_id] = item
    if set(outcomes) != {str(entry["id"]) for entry in entries}:
        raise ValueError("The verifier did not answer every attestation it was given exactly once.")
    return outcomes


def require_outcomes(outcomes: Mapping[str, Mapping[str, object]], candidates: Sequence[str]) -> None:
    """Accept the verifier's verdicts only when the controls split as they must and every candidate verified.

    Raises:
        ValueError: When the tool refused the genuine control (it cannot verify here), accepted a tampered copy
            (it is not checking), or refused a candidate file (naming the file and Sigstore's reason).
    """
    good = outcomes[ProvenanceControl.GOOD]
    if good.get("outcome") != "verified":
        raise ValueError(f"The pinned tool refused the recorded genuine attestation ({good.get('reason')}); it "
                         "cannot verify in this environment, so none of its verdicts can be trusted.")
    for entry_id in (ProvenanceControl.WRONG_DIGEST, ProvenanceControl.WRONG_SIGNER):
        if outcomes[entry_id].get("outcome") != "refused":
            raise ValueError(f"The pinned tool accepted a tampered copy of the recorded attestation ({entry_id}); "
                             "it is not checking, so none of its verdicts can be trusted.")
    refused = [f"{name}: {outcomes[f'candidate:{name}'].get('reason')}" for name in candidates
               if outcomes[f"candidate:{name}"].get("outcome") != "verified"]
    if refused:
        raise ValueError("Sigstore refused the TestPyPI attestation of " + "; ".join(refused) + ".")


def verify_candidate(directory: pathlib.Path, report: pathlib.Path, environment: Mapping[str, str]) -> None:
    """Verify every built file's TestPyPI provenance in five layers, then write the evidence report.

    The built files are verified again first (`verified_files`), so the digests the provenance must name are this
    run's. The recorded control and every candidate are checked with this script's layers before the tool
    environment is built; the tool then checks them all in one process. The report is written only after every
    check has passed.
    """
    version = package_version()
    files = verified_files(directory, version)
    context = run_context(environment)
    uploaded, publish_attempt = upload_record(environment, files, context["run_attempt"])
    with tempfile.TemporaryDirectory(prefix="melder-provenance-", dir=os.environ.get("RUNNER_TEMP")) as scratch:
        root = pathlib.Path(scratch)
        entries = control_entries()
        evidence: dict[str, dict[str, object]] = {}
        for name, identity in files.items():
            raw = fetch_provenance(version, name)
            try:
                document = json.loads(raw)
            except json.JSONDecodeError as error:
                raise ValueError(f"TestPyPI's provenance of {name} is not JSON.") from error
            attestation = single_attestation(document, name, ProvenancePolicy.publisher())
            check_statement(attestation, name, identity["sha256"], name)
            certificate = certificate_identity(certificate_der(attestation, name))
            expected = expected_identity(context, name in uploaded, publish_attempt)
            check_identity(certificate, expected, name)
            stored = root / f"{name}.provenance.json"
            stored.write_bytes(raw)
            entries.append({"id": f"candidate:{name}", "name": name, "sha256": identity["sha256"],
                            "provenance": str(stored), "identity": {**expected, "issuer": ProvenancePolicy.ISSUER}})
            evidence[name] = {"uploaded_by_this_run": name in uploaded,
                              "run_invocation": certificate["claims"][FulcioClaim.RUN_INVOCATION_URI],
                              "build_trigger": certificate["claims"][FulcioClaim.BUILD_TRIGGER]}
        require_outcomes(run_verifier(tool_environment(root), entries, root), sorted(files))
    write_report(report, version, files, evidence, publish_attempt, environment)


def write_report(path: pathlib.Path, version: str, files: Mapping[str, FileIdentity],
                 evidence: Mapping[str, Mapping[str, object]], publish_attempt: int,
                 environment: Mapping[str, str]) -> None:
    """Retain this run's verified provenance identity as a small, credential-free JSON report."""
    path.parent.mkdir(parents=True, exist_ok=True)
    report = {
        "status": "provenance-verified", "version": version, "files": dict(files), "provenance": dict(evidence),
        "publisher": ProvenancePolicy.publisher(), "signer": ProvenancePolicy.workflow_uri(),
        "controls": {ProvenanceControl.GOOD: "verified", ProvenanceControl.WRONG_DIGEST: "refused",
                     ProvenanceControl.WRONG_SIGNER: "refused"},
        "repository": environment.get("GITHUB_REPOSITORY", "local"),
        "commit": git_output(("rev-parse", "HEAD^{commit}")),
        "run_id": environment.get("GITHUB_RUN_ID", "local"),
        "run_attempt": environment.get("GITHUB_RUN_ATTEMPT", "local"), "publish_attempt": publish_attempt,
    }
    path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")


def main(argv: Optional[Sequence[str]] = None) -> int:
    """Verify the candidate's TestPyPI provenance; never upload or install anything but the pinned tool."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("operation", choices=("verify",))
    parser.add_argument("--directory", type=pathlib.Path, default=pathlib.Path("dist"))
    parser.add_argument("--report", type=pathlib.Path, required=True)
    args = parser.parse_args(argv)
    verify_candidate(args.directory, args.report, os.environ)
    print(f"OK: {args.operation}; report={args.report}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
