"""Prove the candidate provenance check's five layers on recorded and synthetic attestations, with no network.

The recorded control is PyPI's real provenance of the pypi-attestations 0.0.30 wheel; the synthetic attestations are
built here, byte by byte, with the identity this repository's release-candidate run would sign with. Nothing reaches
TestPyPI, Sigstore or pip: those boundaries are replaced in each test that crosses them.
"""

import ast
import base64
import io
import json
import pathlib
import subprocess
import urllib.error
from collections.abc import Callable, Mapping, Sequence
from types import ModuleType
from typing import Optional

import pytest
import yaml


class Der:
    """Encode the DER a Fulcio signing certificate is written in, so a test can build an exact or a broken one."""

    @staticmethod
    def element(tag: int, content: bytes) -> bytes:
        """Return one DER element with its minimal definite length."""
        if len(content) < 0x80:
            return bytes([tag, len(content)]) + content
        size = (len(content).bit_length() + 7) // 8
        return bytes([tag, 0x80 | size]) + len(content).to_bytes(size, "big") + content

    @staticmethod
    def arcs(dotted: str) -> bytes:
        """Return the content octets of a dotted OBJECT IDENTIFIER, each arc in minimal base-128."""
        numbers = [int(arc) for arc in dotted.split(".")]
        body = bytearray()
        for value in (40 * numbers[0] + numbers[1], *numbers[2:]):
            septets = [value & 0x7F]
            value >>= 7
            while value:
                septets.append(0x80 | (value & 0x7F))
                value >>= 7
            body.extend(reversed(septets))
        return bytes(body)

    @classmethod
    def extension(cls, dotted: str, value: bytes, critical: bool = False) -> bytes:
        """Return one Extension: its OID, an optional critical flag and its OCTET STRING value."""
        flag = cls.element(0x01, b"\xff") if critical else b""
        return cls.element(0x30, cls.element(0x06, cls.arcs(dotted)) + flag + cls.element(0x04, value))

    @classmethod
    def subject_names(cls, *uris: str) -> bytes:
        """Return a SubjectAlternativeName extension naming each URI."""
        return cls.extension("2.5.29.17", cls.element(0x30, b"".join(cls.element(0x86, uri.encode("ascii"))
                                                                     for uri in uris)))

    @classmethod
    def claim(cls, dotted: str, text: str) -> bytes:
        """Return one Fulcio claim as Fulcio writes it: raw text up to .6, a DER UTF8String from .8 on."""
        value = text.encode("utf-8")
        return cls.extension(dotted, value if int(dotted.rsplit(".", 1)[1]) <= 6 else cls.element(0x0C, value))

    @classmethod
    def certificate(cls, extensions: Sequence[bytes], before_extensions: bytes = b"",
                    extensions_block: Optional[bytes] = None) -> bytes:
        """Return a certificate whose to-be-signed part holds placeholder fields and these extensions.

        Args:
            extensions: The Extension elements, in order.
            before_extensions: Raw elements inserted into the to-be-signed part just before the extensions block.
            extensions_block: The whole `[3]` element to use instead of the one built from extensions.
        """
        algorithm = cls.element(0x30, cls.element(0x06, cls.arcs("1.2.840.10045.4.3.3")))
        block = extensions_block if extensions_block is not None else cls.element(
            0xA3, cls.element(0x30, b"".join(extensions)))
        tbs = (cls.element(0xA0, cls.element(0x02, b"\x02")) + cls.element(0x02, b"\x01\x02") + algorithm
               + cls.element(0x30, b"") + cls.element(0x30, b"") + cls.element(0x30, b"") + cls.element(0x30, b"")
               + before_extensions + block)
        return cls.element(0x30, cls.element(0x30, tbs) + algorithm + cls.element(0x03, b"\x00signature"))


class Signer:
    """The identity this repository's release-candidate run signs with, written out independently of the script."""

    PREFIX = "1.3.6.1.4.1.57264.1."
    SHA = "a" * 40
    WORKFLOW_SHA = "b" * 40
    WORKFLOW = ("https://github.com/Synaptic724/melder/.github/workflows/release-candidate.yml"
                "@refs/heads/release_candidate")
    ISSUER = "https://token.actions.githubusercontent.com"

    @classmethod
    def claims(cls, run: str = "3003", attempt: str = "1", trigger: str = "push") -> dict[str, str]:
        """Return every claim Fulcio writes for a run of release-candidate.yml in the pypitest environment."""
        oid = cls.PREFIX
        return {
            oid + "1": cls.ISSUER, oid + "2": trigger, oid + "3": cls.SHA, oid + "4": "Release candidate",
            oid + "5": "Synaptic724/melder", oid + "6": "refs/heads/release_candidate",
            oid + "8": cls.ISSUER, oid + "9": cls.WORKFLOW, oid + "10": cls.WORKFLOW_SHA, oid + "11": "github-hosted",
            oid + "12": "https://github.com/Synaptic724/melder", oid + "13": cls.SHA,
            oid + "14": "refs/heads/release_candidate", oid + "15": "1001",
            oid + "16": "https://github.com/Synaptic724", oid + "17": "2002", oid + "18": cls.WORKFLOW,
            oid + "19": cls.WORKFLOW_SHA, oid + "20": trigger,
            oid + "21": f"https://github.com/Synaptic724/melder/actions/runs/{run}/attempts/{attempt}",
            oid + "22": "public", oid + "23": "pypitest", oid + "24": "repo:Synaptic724/melder:environment:pypitest",
        }

    @classmethod
    def certificate(cls, claims: Mapping[str, str], sans: Sequence[str] = ()) -> bytes:
        """Return a certificate carrying these claims and subject alternative names (the workflow by default)."""
        return Der.certificate([Der.subject_names(*(sans or (cls.WORKFLOW,))),
                                *(Der.claim(oid, value) for oid, value in claims.items())])

    @staticmethod
    def statement(name: str, sha256: str) -> dict[str, object]:
        """Return the PyPI publish statement of one file."""
        return {"_type": "https://in-toto.io/Statement/v1", "subject": [{"name": name, "digest": {"sha256": sha256}}],
                "predicateType": "https://docs.pypi.org/attestations/publish/v1", "predicate": None}

    @classmethod
    def provenance(cls, name: str, sha256: str, claims: Mapping[str, str],
                   publisher: Optional[Mapping[str, str]] = None,
                   statement: Optional[Mapping[str, object]] = None) -> dict[str, object]:
        """Return a provenance as TestPyPI's Integrity API answers it, holding one attestation of one file."""
        attestation = {
            "version": 1,
            "verification_material": {
                "certificate": base64.b64encode(cls.certificate(claims)).decode("ascii"),
                "transparency_entries": [{"logIndex": "1", "kindVersion": {"kind": "dsse", "version": "0.0.1"}}],
            },
            "envelope": {
                "statement": base64.b64encode(json.dumps(statement or cls.statement(name, sha256)).encode())
                .decode("ascii"),
                "signature": base64.b64encode(b"signature").decode("ascii"),
            },
        }
        record = publisher or {"kind": "GitHub", "repository": "Synaptic724/melder",
                               "workflow": "release-candidate.yml", "environment": "pypitest"}
        return {"version": 1, "attestation_bundles": [{"publisher": dict(record), "attestations": [attestation]}]}

    @classmethod
    def environment(cls, **changes: str) -> dict[str, str]:
        """Return GitHub's default variables for a push run of release-candidate.yml, with any changes applied."""
        values = {
            "GITHUB_SERVER_URL": "https://github.com", "GITHUB_REPOSITORY": "Synaptic724/melder",
            "GITHUB_REF": "refs/heads/release_candidate",
            "GITHUB_WORKFLOW_REF": cls.WORKFLOW.removeprefix("https://github.com/"),
            "GITHUB_SHA": cls.SHA, "GITHUB_WORKFLOW_SHA": cls.WORKFLOW_SHA, "GITHUB_REPOSITORY_ID": "1001",
            "GITHUB_REPOSITORY_OWNER_ID": "2002", "GITHUB_RUN_ID": "3003", "GITHUB_RUN_ATTEMPT": "2",
            "GITHUB_EVENT_NAME": "push",
        }
        values.update(changes)
        return values


def control_document(provenance: ModuleType) -> dict[str, object]:
    """Read the recorded control provenance as JSON."""
    directory = provenance.ProvenancePolicy.tool_directory()
    return json.loads((directory / provenance.ProvenanceControl.FIXTURE).read_bytes())


def identity_of(provenance: ModuleType, claims: Mapping[str, str], sans: Sequence[str] = ()) -> dict[str, object]:
    """Read back what the script sees in a synthetic certificate."""
    return provenance.certificate_identity(Signer.certificate(claims, sans))


def test_der_elements_read_short_and_long_lengths(provenance: ModuleType) -> None:
    """A short and a long definite length both bound the value exactly."""
    reader = provenance.DerReader
    short = Der.element(0x04, b"abc")
    assert reader.element(short, 0, len(short)) == (0x04, 2, 5)
    long = Der.element(0x04, b"x" * 300)
    assert reader.element(long, 0, len(long)) == (0x04, 4, 304)
    assert reader.children(short + long, 0, len(short) + len(long)) == [(0x04, 2, 5), (0x04, 9, 309)]


@pytest.mark.parametrize(("data", "message"), [
    (b"\x04", "truncated"),
    (b"\x1f\x01\x00", "multi-byte tag"),
    (b"\x04\x80", "indefinite or oversized"),
    (b"\x04\x85" + b"\x00" * 5, "indefinite or oversized"),
    (b"\x04\x81\x05abcde", "non-minimal length"),
    (b"\x04\x82\x00\x80" + b"x" * 128, "non-minimal length"),
    (b"\x04\x05abc", "overruns"),
])
def test_der_elements_refuse_every_form_der_forbids(provenance: ModuleType, data: bytes, message: str) -> None:
    """Truncation, multi-byte tags, indefinite, oversized or padded lengths and overruns are all refused."""
    with pytest.raises(ValueError, match=message):
        provenance.DerReader.element(data, 0, len(data))


def test_der_children_must_tile_their_parent(provenance: ModuleType) -> None:
    """An element that runs past its parent's end is refused, not read into the next field."""
    data = Der.element(0x04, b"ab") + b"\x04\x09cd"
    with pytest.raises(ValueError, match="overruns"):
        provenance.DerReader.children(data, 0, len(data))


@pytest.mark.parametrize("dotted", ["1.3.6.1.4.1.57264.1.8", "2.5.29.17", "1.3.6.1.4.1.57264.1.24", "2.999.3",
                                    "0.9.2342.19200300.100.1.1"])
def test_object_identifiers_decode_to_their_dotted_form(provenance: ModuleType, dotted: str) -> None:
    """Multi-byte arcs and the joint first arc decode exactly."""
    assert provenance.DerReader.object_identifier(Der.arcs(dotted)) == dotted


@pytest.mark.parametrize("value", [b"", b"\x2b\x86", b"\x2b\x80\x01"])
def test_malformed_object_identifiers_are_refused(provenance: ModuleType, value: bytes) -> None:
    """An empty value, an unterminated last arc and a padded arc are refused."""
    with pytest.raises(ValueError, match="object identifier"):
        provenance.DerReader.object_identifier(value)


def test_the_recorded_control_reads_as_its_real_signer(provenance: ModuleType) -> None:
    """The reader recovers every claim of a real Fulcio certificate, legacy claims included, and nothing else."""
    control = provenance.ProvenanceControl
    attestation = provenance.single_attestation(control_document(provenance), "the control", control.PUBLISHER)
    identity = provenance.certificate_identity(provenance.certificate_der(attestation, "the control"))
    assert identity["sans"] == [control.SAN]
    assert {oid: identity["claims"][oid] for oid in control.CLAIMS} == dict(control.CLAIMS)
    legacy = {oid: identity["claims"][oid] for oid in identity["claims"] if oid not in control.CLAIMS}
    assert legacy == {
        "1.3.6.1.4.1.57264.1.1": "https://token.actions.githubusercontent.com", "1.3.6.1.4.1.57264.1.2": "release",
        "1.3.6.1.4.1.57264.1.3": control.COMMIT, "1.3.6.1.4.1.57264.1.4": "release",
        "1.3.6.1.4.1.57264.1.5": "pypi/pypi-attestations", "1.3.6.1.4.1.57264.1.6": "refs/tags/v0.0.30",
    }
    provenance.check_identity(identity, control.expected(), "the control")
    provenance.check_statement(attestation, control.NAME, control.SHA256, "the control")


def test_certificate_identity_reads_claims_and_skips_unknown_extensions(provenance: ModuleType) -> None:
    """Known claims are decoded, a critical flag is allowed, and extensions outside the check are left out."""
    claims = Signer.claims()
    der = Der.certificate([Der.extension("2.5.29.15", b"\x03\x02\x07\x80", critical=True),
                           Der.subject_names(Signer.WORKFLOW),
                           *(Der.claim(oid, value) for oid, value in claims.items()),
                           Der.claim("1.3.6.1.4.1.57264.1.99", "future claim")])
    identity = provenance.certificate_identity(der)
    assert identity == {"sans": [Signer.WORKFLOW], "claims": claims}


@pytest.mark.parametrize(("der", "message"), [
    (Der.element(0x31, b""), "not one DER certificate"),
    (Der.element(0x30, Der.element(0x30, b"") + Der.element(0x30, b"")), "not one DER certificate"),
    (Der.certificate([]) + b"\x00", "not one DER certificate"),
    (Der.certificate([], extensions_block=Der.element(0xA2, Der.element(0x30, b""))), "no extensions block"),
    (Der.certificate([], before_extensions=Der.element(0xA3, Der.element(0x30, b""))), "no extensions block"),
    (Der.certificate([], extensions_block=Der.element(0xA3, Der.element(0x31, b""))), "no extensions block"),
    (Der.certificate([], extensions_block=Der.element(0xA3, Der.element(0x30, b"") + Der.element(0x30, b""))),
     "no extensions block"),
])
def test_a_certificate_without_one_extensions_block_is_refused(provenance: ModuleType, der: bytes,
                                                              message: str) -> None:
    """Anything but one certificate whose to-be-signed part holds exactly one extensions block is refused."""
    with pytest.raises(ValueError, match=message):
        provenance.certificate_identity(der)


@pytest.mark.parametrize("extension", [
    Der.element(0x30, Der.element(0x06, Der.arcs("2.5.29.17"))),
    Der.element(0x30, Der.element(0x06, Der.arcs("2.5.29.17")) + Der.element(0x02, b"\x01")
                + Der.element(0x04, b"")),
    Der.element(0x30, Der.element(0x04, b"") + Der.element(0x04, b"")),
    Der.element(0x31, Der.element(0x06, Der.arcs("2.5.29.17")) + Der.element(0x04, b"")),
    Der.element(0x30, Der.element(0x06, Der.arcs("2.5.29.17")) + Der.element(0x01, b"\xff")
                + Der.element(0x01, b"\xff") + Der.element(0x04, b"")),
])
def test_a_malformed_extension_is_refused(provenance: ModuleType, extension: bytes) -> None:
    """An extension that is not SEQUENCE { OID, [BOOLEAN], OCTET STRING } is refused."""
    with pytest.raises(ValueError, match="malformed extension"):
        provenance.certificate_identity(Der.certificate([extension]))


def test_a_repeated_extension_is_refused(provenance: ModuleType) -> None:
    """Two copies of one claim cannot both be read; the certificate is refused instead of picking one."""
    claim = Der.claim(Signer.PREFIX + "12", "https://github.com/Synaptic724/melder")
    with pytest.raises(ValueError, match="repeats extension"):
        provenance.certificate_identity(Der.certificate([claim, claim]))


@pytest.mark.parametrize("names", [
    Der.element(0x30, Der.element(0x81, b"someone@example.com")),
    Der.element(0x30, Der.element(0x86, Signer.WORKFLOW.encode()) + Der.element(0x82, b"example.com")),
])
def test_a_subject_name_that_is_not_a_uri_is_refused(provenance: ModuleType, names: bytes) -> None:
    """A GitHub Actions signer is named by its workflow URI only; an e-mail or DNS name is refused."""
    with pytest.raises(ValueError, match="not a URI"):
        provenance.certificate_identity(Der.certificate([Der.extension("2.5.29.17", names)]))


def test_malformed_subject_names_are_refused(provenance: ModuleType) -> None:
    """A SubjectAlternativeName value that is not one SEQUENCE is refused."""
    value = Der.element(0x30, Der.element(0x86, b"https://x")) + b"\x00"
    with pytest.raises(ValueError, match="subject alternative names are malformed"):
        provenance.certificate_identity(Der.certificate([Der.extension("2.5.29.17", value)]))


@pytest.mark.parametrize("value", [
    Der.element(0x13, b"public"),
    Der.element(0x0C, b"public") + b"\x00",
    b"public",
])
def test_a_text_claim_that_is_not_one_utf8_string_is_refused(provenance: ModuleType, value: bytes) -> None:
    """From .8 on a claim is exactly one DER UTF8String; another string type or trailing bytes are refused."""
    extension = Der.extension(Signer.PREFIX + "22", value)
    with pytest.raises(ValueError):
        provenance.certificate_identity(Der.certificate([extension]))


def expected_for_this_run(provenance: ModuleType, uploaded_here: bool = True, attempt: int = 1) -> dict[str, object]:
    """Return what the script demands of a candidate file in the push run Signer.environment describes."""
    return provenance.expected_identity(provenance.run_context(Signer.environment()), uploaded_here, attempt)


def test_the_expected_identity_of_an_uploaded_file_is_this_run(provenance: ModuleType) -> None:
    """A file this run uploaded must name every claim exactly, this run's id and its publish attempt included."""
    expected = expected_for_this_run(provenance, attempt=1)
    claims = Signer.claims(run="3003", attempt="1", trigger="push")
    assert expected == {"san": Signer.WORKFLOW, "patterns": {},
                        "exact": {oid: value for oid, value in claims.items() if int(oid.rsplit(".", 1)[1]) >= 8}}
    provenance.check_identity(identity_of(provenance, claims), expected, "melder.whl")


def test_an_uploaded_file_signed_by_another_attempt_or_event_is_refused(provenance: ModuleType) -> None:
    """The run invocation names the attempt that uploaded, and the trigger is this run's event."""
    expected = expected_for_this_run(provenance, attempt=1)
    with pytest.raises(ValueError, match="Run Invocation URI"):
        provenance.check_identity(identity_of(provenance, Signer.claims(attempt="2")), expected, "melder.whl")
    with pytest.raises(ValueError, match="Build Trigger"):
        provenance.check_identity(identity_of(provenance, Signer.claims(trigger="workflow_dispatch")), expected,
                                  "melder.whl")


def test_a_file_testpypi_already_had_may_come_from_another_run_at_this_commit(provenance: ModuleType) -> None:
    """A file uploaded earlier matches any run and attempt of this repository, from either allowed event."""
    expected = expected_for_this_run(provenance, uploaded_here=False)
    oid = Signer.PREFIX
    assert set(expected["patterns"]) == {oid + "20", oid + "21"}
    assert oid + "20" not in expected["exact"] and oid + "21" not in expected["exact"]
    for claims in (Signer.claims(run="2002", attempt="3", trigger="workflow_dispatch"), Signer.claims(run="9")):
        provenance.check_identity(identity_of(provenance, claims), expected, "melder.whl")


@pytest.mark.parametrize(("change", "claim"), [
    ({"1.3.6.1.4.1.57264.1.21": "https://github.com/someone/melder/actions/runs/1/attempts/1"}, "Run Invocation URI"),
    ({"1.3.6.1.4.1.57264.1.21": "https://github.com/Synaptic724/melder/actions/runs/1/attempts/0"},
     "Run Invocation URI"),
    ({"1.3.6.1.4.1.57264.1.20": "pull_request", "1.3.6.1.4.1.57264.1.2": "pull_request"}, "Build Trigger"),
    ({"1.3.6.1.4.1.57264.1.13": "c" * 40, "1.3.6.1.4.1.57264.1.3": "c" * 40}, "Source Repository Digest"),
])
def test_a_file_testpypi_already_had_still_needs_this_repository_and_commit(provenance: ModuleType,
                                                                           change: dict[str, str],
                                                                           claim: str) -> None:
    """The patterns allow another run of this workflow, never another repository, event or commit."""
    with pytest.raises(ValueError, match=claim):
        provenance.check_identity(identity_of(provenance, {**Signer.claims(), **change}),
                                  expected_for_this_run(provenance, uploaded_here=False), "melder.whl")


@pytest.mark.parametrize(("arc", "value", "name"), [
    ("8", "https://accounts.google.com", "Issuer"),
    ("9", Signer.WORKFLOW.replace("release_candidate", "dev"), "Build Signer URI"),
    ("10", "c" * 40, "Build Signer Digest"),
    ("11", "self-hosted", "Runner Environment"),
    ("12", "https://github.com/Synaptic724/melder-fork", "Source Repository URI"),
    ("14", "refs/heads/dev", "Source Repository Ref"),
    ("15", "1002", "Source Repository Identifier"),
    ("16", "https://github.com/someone", "Source Repository Owner URI"),
    ("17", "2003", "Source Repository Owner Identifier"),
    ("18", Signer.WORKFLOW.replace("release-candidate", "ci"), "Build Config URI"),
    ("19", "c" * 40, "Build Config Digest"),
    ("22", "private", "Source Repository Visibility At Signing"),
    ("23", "pypi", "Deployment Environment"),
    ("24", "repo:Synaptic724/melder:ref:refs/heads/release_candidate", "Token Subject"),
])
def test_every_claim_is_checked_on_its_own(provenance: ModuleType, arc: str, value: str, name: str) -> None:
    """Changing any one claim refuses the file, naming that claim with what was expected and what was found."""
    claims = {**Signer.claims(), Signer.PREFIX + arc: value}
    with pytest.raises(ValueError, match=name) as refusal:
        provenance.check_identity(identity_of(provenance, claims), expected_for_this_run(provenance), "melder.whl")
    assert repr(value) in str(refusal.value)
    assert "melder.whl" in str(refusal.value)


def test_a_missing_claim_is_refused(provenance: ModuleType) -> None:
    """A certificate without the Deployment Environment claim does not satisfy it by omission."""
    claims = {oid: value for oid, value in Signer.claims().items() if oid != Signer.PREFIX + "23"}
    with pytest.raises(ValueError, match=r"Deployment Environment \(1\.3\.6\.1\.4\.1\.57264\.1\.23\) is None"):
        provenance.check_identity(identity_of(provenance, claims), expected_for_this_run(provenance), "melder.whl")


@pytest.mark.parametrize("sans", [
    ("https://github.com/Synaptic724/melder/.github/workflows/release-candidate.yml@refs/heads/dev",),
    (Signer.WORKFLOW, "https://github.com/Synaptic724/melder/.github/workflows/ci.yml@refs/heads/release_candidate"),
])
def test_the_certificate_must_name_exactly_the_one_expected_signer(provenance: ModuleType,
                                                                  sans: tuple[str, ...]) -> None:
    """Another workflow URI, or a second name beside the right one, is refused."""
    with pytest.raises(ValueError, match="subject alternative names"):
        provenance.check_identity(identity_of(provenance, Signer.claims(), sans), expected_for_this_run(provenance),
                                  "melder.whl")


@pytest.mark.parametrize(("arc", "value"), [
    ("1", "https://accounts.google.com"),
    ("2", "workflow_dispatch"),
    ("3", "c" * 40),
    ("5", "someone/melder"),
    ("6", "refs/heads/dev"),
])
def test_a_deprecated_claim_must_agree_with_its_successor(provenance: ModuleType, arc: str, value: str) -> None:
    """Fulcio still writes the GitHub-specific claims .1 to .6; one that disagrees with its successor is refused."""
    claims = {**Signer.claims(), Signer.PREFIX + arc: value}
    with pytest.raises(ValueError, match=f"deprecated claim 1\\.3\\.6\\.1\\.4\\.1\\.57264\\.1\\.{arc} "):
        provenance.check_identity(identity_of(provenance, claims), expected_for_this_run(provenance), "melder.whl")


def test_every_difference_is_reported_together(provenance: ModuleType) -> None:
    """One refusal lists every claim that differs, so a reader fixes the publisher in one pass."""
    claims = {**Signer.claims(), Signer.PREFIX + "11": "self-hosted", Signer.PREFIX + "23": "pypi"}
    with pytest.raises(ValueError) as refusal:
        provenance.check_identity(identity_of(provenance, claims, ("https://example.com",)),
                                  expected_for_this_run(provenance), "melder.whl")
    message = str(refusal.value)
    assert "subject alternative names" in message and "Runner Environment" in message
    assert "Deployment Environment" in message


def test_the_run_context_is_read_from_githubs_variables(provenance: ModuleType) -> None:
    """A push run on release_candidate yields its repository, owner, commits, event, run and attempt."""
    assert provenance.run_context(Signer.environment()) == {
        "repository_id": "1001", "owner_id": "2002", "sha": Signer.SHA, "workflow_sha": Signer.WORKFLOW_SHA,
        "event": "push", "run_id": "3003", "run_attempt": 2,
    }
    dispatched = provenance.run_context(Signer.environment(GITHUB_EVENT_NAME="workflow_dispatch",
                                                           GITHUB_SHA="d" * 64, GITHUB_WORKFLOW_SHA="e" * 64))
    assert dispatched["event"] == "workflow_dispatch" and dispatched["sha"] == "d" * 64


@pytest.mark.parametrize(("name", "value"), [
    ("GITHUB_SERVER_URL", "https://github.example.com"),
    ("GITHUB_REPOSITORY", "someone/melder"),
    ("GITHUB_REF", "refs/heads/dev"),
    ("GITHUB_WORKFLOW_REF", "Synaptic724/melder/.github/workflows/ci.yml@refs/heads/release_candidate"),
    ("GITHUB_WORKFLOW_REF", "Synaptic724/melder/.github/workflows/release-candidate.yml@refs/heads/dev"),
])
def test_the_check_runs_only_as_this_repositorys_candidate_workflow(provenance: ModuleType, name: str,
                                                                    value: str) -> None:
    """Another server, repository, branch or workflow is refused before anything is fetched."""
    with pytest.raises(ValueError, match=name):
        provenance.run_context(Signer.environment(**{name: value}))


@pytest.mark.parametrize(("name", "value"), [
    ("GITHUB_SHA", "a" * 39), ("GITHUB_SHA", "A" * 40), ("GITHUB_WORKFLOW_SHA", ""),
    ("GITHUB_REPOSITORY_ID", "0"), ("GITHUB_REPOSITORY_ID", "01"), ("GITHUB_REPOSITORY_OWNER_ID", "x"),
    ("GITHUB_RUN_ID", "-1"), ("GITHUB_RUN_ATTEMPT", "0"), ("GITHUB_EVENT_NAME", "pull_request"),
    ("GITHUB_EVENT_NAME", "push|workflow_dispatch"),
])
def test_malformed_run_identifiers_are_refused(provenance: ModuleType, name: str, value: str) -> None:
    """Short or uppercase SHAs, padded or non-decimal ids and other events are refused."""
    with pytest.raises(ValueError, match=name):
        provenance.run_context(Signer.environment(**{name: value}))


def test_a_missing_run_variable_is_refused(provenance: ModuleType) -> None:
    """An absent variable is refused, not read as empty or defaulted."""
    environment = Signer.environment()
    del environment["GITHUB_RUN_ID"]
    with pytest.raises(ValueError, match="GITHUB_RUN_ID"):
        provenance.run_context(environment)


def build_files() -> dict[str, dict[str, object]]:
    """Return the identities of a candidate's two built files."""
    return {"melder-0.2.8300-py3-none-any.whl": {"sha256": "1" * 64, "size": 100},
            "melder-0.2.8300.tar.gz": {"sha256": "2" * 64, "size": 200}}


def test_the_upload_record_names_the_files_and_attempt_that_uploaded(provenance: ModuleType) -> None:
    """The publish job's outputs say which files it staged and in which attempt, possibly an earlier one."""
    environment = {"CANDIDATE_UPLOADED": '["melder-0.2.8300.tar.gz"]', "CANDIDATE_PUBLISH_ATTEMPT": "1"}
    assert provenance.upload_record(environment, build_files(), 2) == (frozenset({"melder-0.2.8300.tar.gz"}), 1)
    nothing = {"CANDIDATE_UPLOADED": "[]", "CANDIDATE_PUBLISH_ATTEMPT": "2"}
    assert provenance.upload_record(nothing, build_files(), 2) == (frozenset(), 2)


@pytest.mark.parametrize("uploaded", [None, "", "not json", '{"melder.whl": 1}', '["a", 1]',
                                      '["melder-0.2.8300.tar.gz", "melder-0.2.8300.tar.gz"]',
                                      '["melder-0.2.8299.tar.gz"]'])
def test_a_malformed_upload_list_is_refused(provenance: ModuleType, uploaded: Optional[str]) -> None:
    """A missing, non-JSON, non-list, mixed, repeated or foreign file list is refused."""
    environment = {"CANDIDATE_PUBLISH_ATTEMPT": "1"}
    if uploaded is not None:
        environment["CANDIDATE_UPLOADED"] = uploaded
    with pytest.raises(ValueError, match="CANDIDATE_UPLOADED"):
        provenance.upload_record(environment, build_files(), 1)


@pytest.mark.parametrize("attempt", [None, "", "0", "01", "x", "3"])
def test_a_malformed_or_future_publish_attempt_is_refused(provenance: ModuleType, attempt: Optional[str]) -> None:
    """The publish attempt must be an attempt of this run no later than the current one."""
    environment = {"CANDIDATE_UPLOADED": "[]"}
    if attempt is not None:
        environment["CANDIDATE_PUBLISH_ATTEMPT"] = attempt
    with pytest.raises(ValueError, match="CANDIDATE_PUBLISH_ATTEMPT"):
        provenance.upload_record(environment, build_files(), 2)


class Answer(io.BytesIO):
    """One urlopen answer: its body and the URL it was finally served from."""

    def __init__(self, body: bytes, url: str) -> None:
        """Hold the body to read and the URL urllib reports after any redirect."""
        super().__init__(body)
        self.url = url


def integrity_url(name: str) -> str:
    """Return the Integrity API address of one candidate file's provenance."""
    return f"https://test.pypi.org/integrity/melder/0.2.8300/{name}/provenance"


def unexpected_pause(seconds: float) -> None:
    """Fail a test whose answer is definitive and must not be retried."""
    raise AssertionError("A definitive answer must not be retried.")


def test_the_provenance_is_read_from_the_integrity_api_without_credentials(provenance: ModuleType,
                                                                          monkeypatch: pytest.MonkeyPatch) -> None:
    """One request to the file's provenance URL, asking for the Integrity API's JSON, with no credentials."""
    answers: list[Answer] = []
    name = "melder-0.2.8300-py3-none-any.whl"

    def answer(request: object, timeout: int) -> Answer:
        """Check the request at the network boundary and answer it."""
        assert request.full_url == integrity_url(name)
        assert request.get_header("Accept") == "application/vnd.pypi.integrity.v1+json"
        assert request.get_header("Authorization") is None
        assert timeout == 30
        answers.append(Answer(b'{"version": 1}', integrity_url(name)))
        return answers[-1]

    monkeypatch.setattr(provenance.urllib.request, "urlopen", answer)
    monkeypatch.setattr(provenance.time, "sleep", unexpected_pause)
    assert provenance.fetch_provenance("0.2.8300", name) == b'{"version": 1}'
    assert len(answers) == 1 and answers[0].closed


def test_a_redirected_provenance_answer_is_refused(provenance: ModuleType, monkeypatch: pytest.MonkeyPatch) -> None:
    """An answer served from another URL than the file's own is not that file's provenance."""
    monkeypatch.setattr(provenance.urllib.request, "urlopen",
                        lambda request, timeout: Answer(b"{}", "https://example.com/provenance"))
    with pytest.raises(ValueError, match="redirected"):
        provenance.fetch_provenance("0.2.8300", "melder.whl")


def test_a_late_provenance_is_waited_for(provenance: ModuleType, monkeypatch: pytest.MonkeyPatch) -> None:
    """TestPyPI may answer 404 just after the upload; the lookup retries and reads the first real answer."""
    answers: list[object] = [urllib.error.HTTPError(integrity_url("m.whl"), 404, "Not Found", {}, None),
                             urllib.error.HTTPError(integrity_url("m.whl"), 503, "Unavailable", {}, None),
                             Answer(b"{}", integrity_url("m.whl"))]
    pauses: list[float] = []

    def answer(request: object, timeout: int) -> object:
        """Answer 404, then 503, then the provenance."""
        reply = answers.pop(0)
        if isinstance(reply, BaseException):
            raise reply
        return reply

    monkeypatch.setattr(provenance.urllib.request, "urlopen", answer)
    monkeypatch.setattr(provenance.time, "sleep", pauses.append)
    assert provenance.fetch_provenance("0.2.8300", "m.whl") == b"{}"
    assert not answers and pauses == [provenance.ProvenancePolicy.RETRY_SECONDS] * 2


def test_a_provenance_that_never_appears_is_refused_by_name(provenance: ModuleType,
                                                           monkeypatch: pytest.MonkeyPatch) -> None:
    """A 404 that outlasts every attempt means the file has no attestation; the refusal says how to recover."""
    calls: list[int] = []
    pauses: list[float] = []

    def missing(request: object, timeout: int) -> None:
        """Answer 404 every time."""
        calls.append(1)
        raise urllib.error.HTTPError(integrity_url("m.whl"), 404, "Not Found", {}, None)

    monkeypatch.setattr(provenance.urllib.request, "urlopen", missing)
    monkeypatch.setattr(provenance.time, "sleep", pauses.append)
    with pytest.raises(ValueError, match="holds no provenance for m.whl") as refusal:
        provenance.fetch_provenance("0.2.8300", "m.whl")
    assert "new candidate version" in str(refusal.value)
    policy = provenance.ProvenancePolicy
    assert len(calls) == policy.LOOKUP_ATTEMPTS and pauses == [policy.RETRY_SECONDS] * (policy.LOOKUP_ATTEMPTS - 1)


@pytest.mark.parametrize("failure", [
    urllib.error.HTTPError("https://test.pypi.org/", 503, "Backend is unhealthy", {}, None),
    urllib.error.URLError("connection refused"),
    TimeoutError("The read operation timed out"),
], ids=["503", "connection", "timeout"])
def test_a_lasting_outage_propagates_after_the_bounded_retries(provenance: ModuleType,
                                                              monkeypatch: pytest.MonkeyPatch,
                                                              failure: Exception) -> None:
    """An outage is retried a bounded number of times and then its own error propagates."""
    calls: list[int] = []

    def unavailable(request: object, timeout: int) -> None:
        """Fail the same way every time."""
        calls.append(1)
        raise failure

    monkeypatch.setattr(provenance.urllib.request, "urlopen", unavailable)
    monkeypatch.setattr(provenance.time, "sleep", lambda seconds: None)
    with pytest.raises(type(failure)):
        provenance.fetch_provenance("0.2.8300", "m.whl")
    assert len(calls) == provenance.ProvenancePolicy.LOOKUP_ATTEMPTS


@pytest.mark.parametrize("status", [400, 401, 403, 410])
def test_a_definitive_error_is_not_retried(provenance: ModuleType, monkeypatch: pytest.MonkeyPatch,
                                          status: int) -> None:
    """Any other HTTP status is the answer, raised at once."""
    def refused(request: object, timeout: int) -> None:
        """Answer with a definitive error."""
        raise urllib.error.HTTPError("https://test.pypi.org/", status, "refused", {}, None)

    monkeypatch.setattr(provenance.urllib.request, "urlopen", refused)
    monkeypatch.setattr(provenance.time, "sleep", unexpected_pause)
    with pytest.raises(urllib.error.HTTPError):
        provenance.fetch_provenance("0.2.8300", "m.whl")


def publisher_record() -> dict[str, str]:
    """Return the publisher record TestPyPI keeps for this repository's Trusted Publisher."""
    return {"kind": "GitHub", "repository": "Synaptic724/melder", "workflow": "release-candidate.yml",
            "environment": "pypitest"}


def test_the_publisher_record_must_be_this_trusted_publisher(provenance: ModuleType) -> None:
    """Layer 2 accepts this repository's publisher, with extra keys, and names every key that differs."""
    expected = provenance.ProvenancePolicy.publisher()
    assert expected == publisher_record()
    document = Signer.provenance("m.whl", "1" * 64, Signer.claims(),
                                 publisher={**publisher_record(), "claims": {"sha": Signer.SHA}})
    assert provenance.single_attestation(document, "m.whl", expected)["version"] == 1
    wrong = Signer.provenance("m.whl", "1" * 64, Signer.claims(),
                              publisher={**publisher_record(), "workflow": "ci.yml", "environment": "pypi"})
    with pytest.raises(ValueError, match="not the expected Trusted Publisher") as refusal:
        provenance.single_attestation(wrong, "m.whl", expected)
    assert "workflow is 'ci.yml', expected 'release-candidate.yml'" in str(refusal.value)
    assert "environment is 'pypi', expected 'pypitest'" in str(refusal.value)


def mutated(document: Mapping[str, object], change: str) -> dict[str, object]:
    """Return a copy of a provenance with one named defect."""
    copy = json.loads(json.dumps(document))
    bundle = copy["attestation_bundles"][0]
    attestation = bundle["attestations"][0]
    if change == "version":
        copy["version"] = 2
    elif change == "two bundles":
        copy["attestation_bundles"].append(bundle)
    elif change == "no bundles":
        copy["attestation_bundles"] = []
    elif change == "no publisher":
        del bundle["publisher"]
    elif change == "two attestations":
        bundle["attestations"].append(attestation)
    elif change == "attestation version":
        attestation["version"] = 0
    elif change == "no log entry":
        attestation["verification_material"]["transparency_entries"] = []
    elif change == "no certificate":
        attestation["verification_material"]["certificate"] = ""
    return copy


@pytest.mark.parametrize("change", ["version", "two bundles", "no bundles", "no publisher", "two attestations",
                                    "attestation version", "no log entry", "no certificate"])
def test_a_provenance_of_any_other_shape_is_refused(provenance: ModuleType, change: str) -> None:
    """Exactly one bundle, one attestation, version 1, a certificate and a transparency-log entry, or refused."""
    document = mutated(Signer.provenance("m.whl", "1" * 64, Signer.claims()), change)
    with pytest.raises(ValueError):
        provenance.single_attestation(document, "m.whl", provenance.ProvenancePolicy.publisher())


@pytest.mark.parametrize("statement", [
    {**Signer.statement("other.whl", "1" * 64)},
    {**Signer.statement("m.whl", "2" * 64)},
    {**Signer.statement("m.whl", "1" * 64), "predicateType": "https://slsa.dev/provenance/v1"},
    {**Signer.statement("m.whl", "1" * 64), "predicate": {"buildType": "x"}},
    {**Signer.statement("m.whl", "1" * 64), "_type": "https://in-toto.io/Statement/v0.1"},
    {**Signer.statement("m.whl", "1" * 64), "subject": [{"name": "m.whl", "digest": {"sha256": "1" * 64}}] * 2},
    {**Signer.statement("m.whl", "1" * 64), "extra": True},
    {key: value for key, value in Signer.statement("m.whl", "1" * 64).items() if key != "predicate"},
])
def test_the_statement_must_name_exactly_this_file(provenance: ModuleType, statement: dict[str, object]) -> None:
    """Layer 5: another name, digest, predicate, statement type, a second subject or an extra key is refused."""
    document = Signer.provenance("m.whl", "1" * 64, Signer.claims(), statement=statement)
    attestation = provenance.single_attestation(document, "m.whl", provenance.ProvenancePolicy.publisher())
    with pytest.raises(ValueError, match="The statement of m.whl is"):
        provenance.check_statement(attestation, "m.whl", "1" * 64, "m.whl")


def test_the_statement_of_this_file_is_accepted(provenance: ModuleType) -> None:
    """The publish statement of this exact file and digest, with no predicate, passes layer 5."""
    document = Signer.provenance("m.whl", "1" * 64, Signer.claims())
    attestation = provenance.single_attestation(document, "m.whl", provenance.ProvenancePolicy.publisher())
    provenance.check_statement(attestation, "m.whl", "1" * 64, "m.whl")


@pytest.mark.parametrize(("field", "value"), [("statement", "not base64!"), ("statement", base64.b64encode(b"[")),
                                              ("signature", "%%%")])
def test_an_envelope_that_does_not_decode_is_refused(provenance: ModuleType, field: str, value: object) -> None:
    """A statement or signature that is not strict base64, or a statement that is not JSON, is refused."""
    document = Signer.provenance("m.whl", "1" * 64, Signer.claims())
    envelope = document["attestation_bundles"][0]["attestations"][0]["envelope"]
    envelope[field] = value.decode("ascii") if isinstance(value, bytes) else value
    attestation = provenance.single_attestation(document, "m.whl", provenance.ProvenancePolicy.publisher())
    with pytest.raises(ValueError, match="m.whl"):
        provenance.check_statement(attestation, "m.whl", "1" * 64, "m.whl")


def test_the_tool_lock_is_exact_hashed_pins_of_the_signers_versions(provenance: ModuleType) -> None:
    """The lock pins the publishing action's own pypi-attestations and sigstore, every pin with its hashes."""
    directory = provenance.ProvenancePolicy.tool_directory()
    pins = provenance.tool_pins((directory / provenance.ProvenancePolicy.TOOL_LOCK).read_text(encoding="utf-8"))
    assert pins["pypi-attestations"][0] == "0.0.30" and pins["sigstore"][0] == "4.5.1"
    assert provenance.ProvenanceControl.SHA256 in pins["pypi-attestations"][1]
    assert len(pins) == 33 and all(hashes for _, hashes in pins.values())


def test_the_lock_reader_follows_continuations_and_comments(provenance: ModuleType) -> None:
    """Continued lines and comments are read as pip reads them."""
    lock = ("# header\nalpha==1.0 \\\n    --hash=sha256:" + "a" * 64 + " \\\n    --hash=sha256:" + "b" * 64
            + "\nBeta_Two==2.0.1 --hash=sha256:" + "c" * 64 + "  # trailing\n")
    assert provenance.tool_pins(lock) == {"alpha": ("1.0", frozenset({"a" * 64, "b" * 64})),
                                          "beta_two": ("2.0.1", frozenset({"c" * 64}))}


@pytest.mark.parametrize("lock", [
    "alpha>=1.0 --hash=sha256:" + "a" * 64,
    "alpha==1.0",
    "alpha==1.0 --hash=sha256:" + "a" * 63,
    "alpha==1.0 --hash=md5:" + "a" * 32,
    "alpha==1.0 --hash=sha256:" + "a" * 64 + "\nAlpha==2.0 --hash=sha256:" + "b" * 64,
])
def test_a_lock_that_is_not_hashed_exact_pins_is_refused(provenance: ModuleType, lock: str) -> None:
    """A range, a missing or malformed hash, or a name pinned twice is refused."""
    with pytest.raises(ValueError, match="not one hashed exact pin"):
        provenance.tool_pins(lock)


def test_the_controls_are_the_recorded_attestation_and_two_tampered_copies(provenance: ModuleType) -> None:
    """The genuine control must verify; one copy expects another digest, one another signer."""
    control = provenance.ProvenanceControl
    fixture = str(provenance.ProvenancePolicy.tool_directory() / control.FIXTURE)
    good, digest, signer = provenance.control_entries()
    assert good == {"id": "control:known-good", "name": control.NAME, "sha256": control.SHA256, "provenance": fixture,
                    "identity": {"san": control.SAN, "exact": dict(control.CLAIMS), "patterns": {},
                                 "issuer": "https://token.actions.githubusercontent.com"}}
    assert digest["id"] == "control:wrong-digest" and digest["sha256"] != control.SHA256
    assert digest["sha256"][:-1] == control.SHA256[:-1] and digest["identity"] == good["identity"]
    assert signer["id"] == "control:wrong-signer" and signer["sha256"] == control.SHA256
    assert signer["identity"]["san"].endswith("@refs/tags/v0.0.29")
    assert {key: value for key, value in signer["identity"].items() if key != "san"} == {
        key: value for key, value in good["identity"].items() if key != "san"}


def copy_tool_directory(provenance: ModuleType, target: pathlib.Path) -> pathlib.Path:
    """Copy the verifier's directory so a test can alter its lock or control without touching the checkout."""
    source = provenance.ProvenancePolicy.tool_directory()
    target.mkdir()
    for name in (provenance.ProvenancePolicy.TOOL_LOCK, provenance.ProvenanceControl.FIXTURE,
                 provenance.ProvenancePolicy.VERIFIER):
        (target / name).write_bytes((source / name).read_bytes())
    return target


@pytest.mark.parametrize("change", ["version", "hash"])
def test_a_lock_that_no_longer_installs_the_control_is_refused(provenance: ModuleType, tmp_path: pathlib.Path,
                                                             monkeypatch: pytest.MonkeyPatch, change: str) -> None:
    """Moving pypi-attestations without refreshing the control fails before the tool is built."""
    directory = copy_tool_directory(provenance, tmp_path / "provenance")
    lock = directory / provenance.ProvenancePolicy.TOOL_LOCK
    text = lock.read_text(encoding="utf-8")
    if change == "version":
        text = text.replace("pypi-attestations==0.0.30", "pypi-attestations==0.0.31")
    else:
        text = text.replace(provenance.ProvenanceControl.SHA256, "f" * 64)
    lock.write_text(text, encoding="utf-8")
    monkeypatch.setattr(provenance.ProvenancePolicy, "tool_directory", staticmethod(lambda: directory))
    with pytest.raises(ValueError, match="refresh known_good_provenance.json"):
        provenance.control_entries()


def test_a_control_that_is_not_the_recorded_attestation_is_refused(provenance: ModuleType, tmp_path: pathlib.Path,
                                                                  monkeypatch: pytest.MonkeyPatch) -> None:
    """The script's own layers check the control first, so an edited fixture cannot pass as the control."""
    directory = copy_tool_directory(provenance, tmp_path / "provenance")
    fixture = directory / provenance.ProvenanceControl.FIXTURE
    document = json.loads(fixture.read_bytes())
    document["attestation_bundles"][0]["publisher"]["workflow"] = "other.yml"
    fixture.write_text(json.dumps(document), encoding="utf-8")
    monkeypatch.setattr(provenance.ProvenancePolicy, "tool_directory", staticmethod(lambda: directory))
    with pytest.raises(ValueError, match="not the expected Trusted Publisher"):
        provenance.control_entries()


def test_the_tool_environment_installs_exactly_the_hashed_lock(provenance: ModuleType, tmp_path: pathlib.Path,
                                                              monkeypatch: pytest.MonkeyPatch) -> None:
    """A fresh environment of this interpreter; pip isolated, hashed, wheels only, no deps, then pip check."""
    environments: list[pathlib.Path] = []
    commands: list[tuple[list[str], pathlib.Path]] = []

    class Builder:
        """Model venv's environment builder without creating an interpreter."""

        def __init__(self, with_pip: bool) -> None:
            """Require the bundled pip the tool is installed with."""
            assert with_pip

        def create(self, path: pathlib.Path) -> None:
            """Record where the environment was asked for."""
            environments.append(path)

    def run(command: list[str], check: bool, cwd: pathlib.Path) -> None:
        """Record each process and refuse an unchecked one."""
        assert check
        commands.append(([str(part) for part in command], cwd))

    monkeypatch.setattr(provenance.venv, "EnvBuilder", Builder)
    monkeypatch.setattr(provenance.subprocess, "run", run)
    python = provenance.tool_environment(tmp_path)
    assert environments == [tmp_path / "tools"]
    assert python == tmp_path / "tools" / ("Scripts/python.exe" if provenance.os.name == "nt" else "bin/python")
    lock = str(provenance.ProvenancePolicy.tool_directory() / "requirements.txt")
    assert commands == [
        ([str(python), "-m", "pip", "--isolated", "--disable-pip-version-check", "install", "--no-cache-dir",
          "--no-deps", "--only-binary=:all:", "--require-hashes", "--index-url", "https://pypi.org/simple/",
          "-r", lock], tmp_path),
        ([str(python), "-m", "pip", "--isolated", "--disable-pip-version-check", "check"], tmp_path),
    ]


def verifier_answering(outcomes: Mapping[str, Mapping[str, str]], requests: list[dict[str, object]],
                       extra: Optional[list[dict[str, str]]] = None
                       ) -> Callable[[list[str], bool, pathlib.Path], None]:
    """Return a subprocess.run stand-in that plays the verifier: it reads the request and writes these outcomes."""
    def run(command: list[str], check: bool, cwd: pathlib.Path) -> None:
        """Check the call, record the request and write one outcome per requested entry."""
        assert check and command[1] == "-I" and command[2].endswith("verify_attestations.py")
        request = json.loads(pathlib.Path(command[command.index("--request") + 1]).read_text(encoding="utf-8"))
        requests.append(request)
        results = [{"id": entry["id"], **outcomes.get(entry["id"], {"outcome": "verified"})}
                   for entry in request["entries"]] + (extra or [])
        pathlib.Path(command[command.index("--result") + 1]).write_text(
            json.dumps({"format": 1, "results": results}), encoding="utf-8")
    return run


def test_the_verifier_is_run_once_on_every_entry(provenance: ModuleType, tmp_path: pathlib.Path,
                                                monkeypatch: pytest.MonkeyPatch) -> None:
    """One isolated verifier process gets every entry and answers each exactly once."""
    requests: list[dict[str, object]] = []
    monkeypatch.setattr(provenance.subprocess, "run",
                        verifier_answering({"b": {"outcome": "refused", "reason": "no"}}, requests))
    entries = [{"id": "a", "name": "a.whl"}, {"id": "b", "name": "b.whl"}]
    outcomes = provenance.run_verifier(tmp_path / "python", entries, tmp_path)
    assert requests == [{"format": 1, "entries": entries}]
    assert outcomes == {"a": {"id": "a", "outcome": "verified"}, "b": {"id": "b", "outcome": "refused", "reason": "no"}}


@pytest.mark.parametrize(("outcomes", "extra"), [
    ({"a": {"outcome": "maybe"}}, None),
    ({}, [{"id": "a", "outcome": "verified"}]),
    ({}, [{"id": "c", "outcome": "verified"}]),
])
def test_a_verifier_answer_that_is_not_one_verdict_per_entry_is_refused(provenance: ModuleType,
                                                                       tmp_path: pathlib.Path,
                                                                       monkeypatch: pytest.MonkeyPatch,
                                                                       outcomes: dict[str, dict[str, str]],
                                                                       extra: Optional[list[dict[str, str]]]) -> None:
    """An unknown verdict, a repeated answer or an answer for an entry never asked about is refused."""
    monkeypatch.setattr(provenance.subprocess, "run", verifier_answering(outcomes, [], extra))
    with pytest.raises(ValueError, match="verifier"):
        provenance.run_verifier(tmp_path / "python", [{"id": "a"}, {"id": "b"}], tmp_path)


def test_a_verifier_that_cannot_work_ends_the_check(provenance: ModuleType, tmp_path: pathlib.Path,
                                                   monkeypatch: pytest.MonkeyPatch) -> None:
    """A verifier that exits non-zero (no trust root, a broken request) fails the run instead of judging it."""
    def broken(command: list[str], check: bool, cwd: pathlib.Path) -> None:
        """Fail like a verifier that could not load its trust root."""
        raise subprocess.CalledProcessError(1, command)

    monkeypatch.setattr(provenance.subprocess, "run", broken)
    with pytest.raises(subprocess.CalledProcessError):
        provenance.run_verifier(tmp_path / "python", [{"id": "a"}], tmp_path)


def verdicts(changes: Optional[Mapping[str, Mapping[str, str]]] = None) -> dict[str, Mapping[str, str]]:
    """Return the verdicts of a working tool on the controls and two candidates, with any changes."""
    values: dict[str, Mapping[str, str]] = {
        "control:known-good": {"outcome": "verified"},
        "control:wrong-digest": {"outcome": "refused", "reason": "digest"},
        "control:wrong-signer": {"outcome": "refused", "reason": "signer"},
        "candidate:a.whl": {"outcome": "verified"}, "candidate:b.tar.gz": {"outcome": "verified"},
    }
    values.update(changes or {})
    return values


def test_working_controls_and_verified_candidates_pass(provenance: ModuleType) -> None:
    """The tool verified the genuine control, refused both copies and verified every candidate."""
    provenance.require_outcomes(verdicts(), ["a.whl", "b.tar.gz"])


@pytest.mark.parametrize(("changes", "message"), [
    ({"control:known-good": {"outcome": "refused", "reason": "no trust root"}}, "cannot verify"),
    ({"control:wrong-digest": {"outcome": "verified"}}, "not checking"),
    ({"control:wrong-signer": {"outcome": "verified"}}, "not checking"),
    ({"candidate:b.tar.gz": {"outcome": "refused", "reason": "bad signature"}}, "b.tar.gz: bad signature"),
])
def test_a_tool_that_misjudges_a_control_or_a_refused_candidate_fails(provenance: ModuleType,
                                                                     changes: dict[str, Mapping[str, str]],
                                                                     message: str) -> None:
    """A tool that cannot verify, or that accepts a tampered copy, is not trusted; a refused candidate is named."""
    with pytest.raises(ValueError, match=message):
        provenance.require_outcomes(verdicts(changes), ["a.whl", "b.tar.gz"])


class CandidateRun:
    """A provenance job with every network and process boundary replaced, recording what crossed each one.

    TestPyPI answers from `documents`; the pinned tool is never built (its environment is a path) and the verifier
    process reads each request, records the provenance bytes every entry points at and answers from `outcomes`.
    """

    def __init__(self, provenance: ModuleType, monkeypatch: pytest.MonkeyPatch, tmp_path: pathlib.Path) -> None:
        """Install the replacements on the loaded script for this test only."""
        self.files = build_files()
        self.documents: dict[str, bytes] = {}
        self.fetched: list[str] = []
        self.tools: list[pathlib.Path] = []
        self.requests: list[dict[str, object]] = []
        self.stored: dict[str, bytes] = {}
        self.outcomes: dict[str, Mapping[str, str]] = {
            "control:wrong-digest": {"outcome": "refused", "reason": "subject does not match"},
            "control:wrong-signer": {"outcome": "refused", "reason": "SANs do not match"},
        }
        self.report = tmp_path / "reports" / "provenance.json"
        monkeypatch.setenv("RUNNER_TEMP", str(tmp_path))
        monkeypatch.setattr(provenance, "package_version", lambda: "0.2.8300")
        monkeypatch.setattr(provenance, "verified_files", lambda directory, version: self.files)
        monkeypatch.setattr(provenance, "fetch_provenance", self.fetch)
        monkeypatch.setattr(provenance, "tool_environment", self.tool)
        monkeypatch.setattr(provenance.subprocess, "run", self.verifier)
        monkeypatch.setattr(provenance, "git_output", lambda arguments: Signer.SHA)

    def fetch(self, version: str, name: str) -> bytes:
        """Answer one file's provenance as TestPyPI would."""
        assert version == "0.2.8300"
        self.fetched.append(name)
        return self.documents[name]

    def tool(self, root: pathlib.Path) -> pathlib.Path:
        """Stand in for building the tool environment inside the job's scratch directory."""
        self.tools.append(root)
        return root / "tools" / "bin" / "python"

    def verifier(self, command: list[str], check: bool, cwd: pathlib.Path) -> None:
        """Play the verifier process: record the request and the files it names, then answer every entry."""
        request = json.loads(pathlib.Path(command[command.index("--request") + 1]).read_text(encoding="utf-8"))
        self.requests.append(request)
        self.stored.update({entry["id"]: pathlib.Path(entry["provenance"]).read_bytes()
                            for entry in request["entries"]})
        results = [{"id": entry["id"], **self.outcomes.get(entry["id"], {"outcome": "verified"})}
                   for entry in request["entries"]]
        pathlib.Path(command[command.index("--result") + 1]).write_text(json.dumps({"format": 1, "results": results}),
                                                                         encoding="utf-8")

    def serve(self, wheel: Mapping[str, str], sdist: Mapping[str, str]) -> None:
        """Make TestPyPI hold an attestation of each built file signed with these claims."""
        for (name, identity), claims in zip(self.files.items(), (wheel, sdist), strict=True):
            self.documents[name] = json.dumps(Signer.provenance(name, str(identity["sha256"]), claims)).encode()


def rerun_environment() -> dict[str, str]:
    """Return a failed-jobs re-run (attempt 2) of a run whose first attempt uploaded only the wheel."""
    return Signer.environment(CANDIDATE_UPLOADED='["melder-0.2.8300-py3-none-any.whl"]', CANDIDATE_PUBLISH_ATTEMPT="1")


def test_every_candidate_file_is_checked_in_all_five_layers(provenance: ModuleType, tmp_path: pathlib.Path,
                                                            monkeypatch: pytest.MonkeyPatch) -> None:
    """The wheel this run uploaded and the sdist an earlier run uploaded both pass, and the report says how."""
    run = CandidateRun(provenance, monkeypatch, tmp_path)
    run.serve(Signer.claims(run="3003", attempt="1"),
              Signer.claims(run="2999", attempt="1", trigger="workflow_dispatch"))
    provenance.verify_candidate(tmp_path / "dist", run.report, rerun_environment())
    (request,) = run.requests
    ids = [entry["id"] for entry in request["entries"]]
    assert ids == ["control:known-good", "control:wrong-digest", "control:wrong-signer",
                   "candidate:melder-0.2.8300-py3-none-any.whl", "candidate:melder-0.2.8300.tar.gz"]
    wheel, sdist = request["entries"][3:]
    oid = Signer.PREFIX
    runs = "https://github.com/Synaptic724/melder/actions/runs/"
    assert wheel["identity"]["exact"][oid + "21"] == runs + "3003/attempts/1"
    assert wheel["identity"]["exact"][oid + "20"] == "push" and wheel["identity"]["patterns"] == {}
    assert set(sdist["identity"]["patterns"]) == {oid + "20", oid + "21"}
    assert {entry["identity"]["issuer"] for entry in (wheel, sdist)} == {Signer.ISSUER}
    assert wheel["sha256"] == "1" * 64 and sdist["sha256"] == "2" * 64
    for name in run.files:
        assert run.stored[f"candidate:{name}"] == run.documents[name]
    assert run.stored["control:known-good"] == (provenance.ProvenancePolicy.tool_directory()
                                                / provenance.ProvenanceControl.FIXTURE).read_bytes()
    assert run.tools == [run.tools[0]] and run.tools[0].parent == tmp_path
    report = json.loads(run.report.read_text(encoding="utf-8"))
    assert report == {
        "status": "provenance-verified", "version": "0.2.8300", "files": run.files,
        "provenance": {
            "melder-0.2.8300-py3-none-any.whl": {
                "uploaded_by_this_run": True, "build_trigger": "push",
                "run_invocation": "https://github.com/Synaptic724/melder/actions/runs/3003/attempts/1"},
            "melder-0.2.8300.tar.gz": {
                "uploaded_by_this_run": False, "build_trigger": "workflow_dispatch",
                "run_invocation": "https://github.com/Synaptic724/melder/actions/runs/2999/attempts/1"},
        },
        "publisher": publisher_record(), "signer": Signer.WORKFLOW,
        "controls": {"control:known-good": "verified", "control:wrong-digest": "refused",
                     "control:wrong-signer": "refused"},
        "repository": "Synaptic724/melder", "commit": Signer.SHA, "run_id": "3003", "run_attempt": "2",
        "publish_attempt": 1,
    }


@pytest.mark.parametrize(("uploaded", "sdist", "message"), [
    ('["melder-0.2.8300-py3-none-any.whl", "melder-0.2.8300.tar.gz"]', Signer.claims(run="3003", attempt="2"),
     "Run Invocation URI"),
    ('["melder-0.2.8300-py3-none-any.whl"]', {**Signer.claims(run="2999"), "1.3.6.1.4.1.57264.1.15": "1002"},
     "Source Repository Identifier"),
])
def test_a_wrong_signer_is_refused_before_the_tool_is_built(provenance: ModuleType, tmp_path: pathlib.Path,
                                                           monkeypatch: pytest.MonkeyPatch, uploaded: str,
                                                           sdist: dict[str, str], message: str) -> None:
    """The script's own layers refuse first: no tool environment, no verifier process, no report.

    One sdist was uploaded by this run but signed by another attempt; the other came from an earlier run of a
    repository with another id.
    """
    run = CandidateRun(provenance, monkeypatch, tmp_path)
    run.serve(Signer.claims(run="3003", attempt="1"), sdist)
    environment = Signer.environment(CANDIDATE_UPLOADED=uploaded, CANDIDATE_PUBLISH_ATTEMPT="1")
    with pytest.raises(ValueError, match=message):
        provenance.verify_candidate(tmp_path / "dist", run.report, environment)
    assert run.tools == [] and run.requests == [] and not run.report.exists()


def test_an_unreadable_provenance_is_refused_by_name(provenance: ModuleType, tmp_path: pathlib.Path,
                                                    monkeypatch: pytest.MonkeyPatch) -> None:
    """A provenance answer that is not JSON names the file and stops the check."""
    run = CandidateRun(provenance, monkeypatch, tmp_path)
    run.documents = {name: b"<html>maintenance</html>" for name in run.files}
    with pytest.raises(ValueError, match="provenance of melder-0.2.8300-py3-none-any.whl is not JSON"):
        provenance.verify_candidate(tmp_path / "dist", run.report, rerun_environment())
    assert run.tools == [] and not run.report.exists()


def test_a_candidate_sigstore_refuses_fails_the_run_without_a_report(provenance: ModuleType,
                                                                     tmp_path: pathlib.Path,
                                                                     monkeypatch: pytest.MonkeyPatch) -> None:
    """Every stdlib layer can pass and Sigstore still refuse (a forged certificate); that refusal decides."""
    run = CandidateRun(provenance, monkeypatch, tmp_path)
    run.serve(Signer.claims(run="3003", attempt="1"), Signer.claims(run="2999"))
    run.outcomes["candidate:melder-0.2.8300.tar.gz"] = {"outcome": "refused", "reason": "invalid signature"}
    with pytest.raises(ValueError, match="melder-0.2.8300.tar.gz: invalid signature"):
        provenance.verify_candidate(tmp_path / "dist", run.report, rerun_environment())
    assert len(run.requests) == 1 and not run.report.exists()


def test_the_controls_are_checked_before_testpypi_is_asked(provenance: ModuleType, tmp_path: pathlib.Path,
                                                          monkeypatch: pytest.MonkeyPatch) -> None:
    """A lock that no longer installs the control stops the check before any candidate is fetched."""
    run = CandidateRun(provenance, monkeypatch, tmp_path)
    directory = copy_tool_directory(provenance, tmp_path / "provenance")
    lock = directory / provenance.ProvenancePolicy.TOOL_LOCK
    lock.write_text(lock.read_text(encoding="utf-8").replace("pypi-attestations==0.0.30", "pypi-attestations==0.1.0"),
                    encoding="utf-8")
    monkeypatch.setattr(provenance.ProvenancePolicy, "tool_directory", staticmethod(lambda: directory))
    with pytest.raises(ValueError, match="pypi-attestations==0.1.0"):
        provenance.verify_candidate(tmp_path / "dist", run.report, rerun_environment())
    assert run.fetched == [] and run.tools == []


def test_the_command_line_verifies_dist_and_names_its_report(provenance: ModuleType, tmp_path: pathlib.Path,
                                                            monkeypatch: pytest.MonkeyPatch,
                                                            capsys: pytest.CaptureFixture[str]) -> None:
    """`verify` checks dist/ with the job's environment and prints where the report is; nothing else is offered."""
    calls: list[tuple[pathlib.Path, pathlib.Path, Mapping[str, str]]] = []
    monkeypatch.setattr(provenance, "verify_candidate",
                        lambda directory, report, environment: calls.append((directory, report, environment)))
    report = tmp_path / "provenance.json"
    assert provenance.main(["verify", "--report", str(report)]) == 0
    assert calls == [(pathlib.Path("dist"), report, provenance.os.environ)]
    assert capsys.readouterr().out == f"OK: verify; report={report}\n"
    with pytest.raises(SystemExit):
        provenance.main(["upload", "--report", str(report)])


def test_the_expected_publisher_is_the_job_that_uploads(provenance: ModuleType) -> None:
    """The identity the check demands is the publish job's own: this workflow, its environment, branch and events."""
    root = pathlib.Path(__file__).resolve().parents[3]
    policy = provenance.ProvenancePolicy
    document = yaml.load((root / ".github/workflows" / policy.WORKFLOW).read_text(encoding="utf-8"),
                         Loader=yaml.BaseLoader)
    publish = document["jobs"]["publish"]
    assert publish["environment"]["name"] == policy.ENVIRONMENT
    assert document["on"]["push"] == {"branches": [policy.REF.removeprefix("refs/heads/")]}
    assert set(document["on"]) == set(policy.TRIGGERS)
    upload = next(step for step in publish["steps"] if step.get("uses", "").startswith("pypa/gh-action-pypi-publish@"))
    assert upload["with"]["repository-url"] == "https://test.pypi.org/legacy/"
    assert policy.INTEGRITY_ROOT == "https://test.pypi.org/integrity/melder/"
    assert f'Repository = "https://github.com/{policy.REPOSITORY}"' in (root / "pyproject.toml").read_text(
        encoding="utf-8")
    assert policy.workflow_uri() == Signer.WORKFLOW


def test_the_pinned_verifier_agrees_with_this_script(provenance: ModuleType) -> None:
    """The verifier cannot be imported here (its closure is not installed), so its contract is read as source.

    It speaks the request format this script writes, accepts the same predicate, uses sigstore's own policy for
    every claim sigstore has one for and its own for the two it lacks, and imports the pinned tool.
    """
    policy = provenance.ProvenancePolicy
    tree = ast.parse((policy.tool_directory() / policy.VERIFIER).read_text(encoding="utf-8"))
    verifier = next(node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == "AttestationVerifier")
    constants: dict[str, ast.expr] = {}
    for node in verifier.body:
        if isinstance(node, ast.Assign) and isinstance(node.targets[0], ast.Name):
            constants[node.targets[0].id] = node.value
        elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name) and node.value is not None:
            constants[node.target.id] = node.value
    assert ast.literal_eval(constants["FORMAT"]) == 1
    assert ast.literal_eval(constants["PUBLISH_PREDICATE"]) == policy.PUBLISH_PREDICATE
    exact = constants["EXACT_POLICIES"]
    assert isinstance(exact, ast.Dict)
    sigstore_claims = [ast.literal_eval(key) for key in exact.keys if key is not None]
    claim = provenance.FulcioClaim
    assert sigstore_claims == list(claim.TEXT[:-2])
    assert set(claim.TEXT) - set(sigstore_claims) == {claim.DEPLOYMENT_ENVIRONMENT, claim.TOKEN_SUBJECT}
    imported = {alias.name.split(".")[0] for node in ast.walk(tree) if isinstance(node, ast.Import)
                for alias in node.names}
    imported |= {node.module.split(".")[0] for node in ast.walk(tree)
                 if isinstance(node, ast.ImportFrom) and node.module is not None}
    assert {"cryptography", "pypi_attestations", "sigstore"} <= imported


def test_the_claims_are_fulcios_github_signer_claims(provenance: ModuleType) -> None:
    """Raw legacy claims .1 to .6, UTF8String claims .8 to .24, each of the latter with a name for refusals."""
    claim = provenance.FulcioClaim
    assert claim.RAW == tuple(f"1.3.6.1.4.1.57264.1.{arc}" for arc in range(1, 7))
    assert claim.TEXT == tuple(f"1.3.6.1.4.1.57264.1.{arc}" for arc in range(8, 25))
    assert set(claim.NAMES) == set(claim.TEXT)
    assert claim.describe(claim.TOKEN_SUBJECT) == "Token Subject (1.3.6.1.4.1.57264.1.24)"
    assert claim.describe("1.3.6.1.4.1.57264.1.99") == "claim (1.3.6.1.4.1.57264.1.99)"
