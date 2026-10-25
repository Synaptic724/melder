"""Verify PEP 740 attestations with Sigstore; runs only inside the provenance check's pinned tool environment.

`.github/scripts/testpypi_provenance.py` builds that environment from `requirements.txt` beside this file and
calls this script with a request it wrote: one entry per attestation, each naming a recorded provenance file, the
distribution's file name and sha256, and the signing identity the attestation must carry (its one subject
alternative name and every Fulcio claim, exact or by pattern). For each entry this script runs pypi-attestations'
`Attestation.verify` on Sigstore's production trust root - the certificate chain to Fulcio, the transparency-log
entry and the signature - under a policy that requires every expected claim, and writes one outcome per entry:
`verified`, or `refused` with the reason. It decides nothing about what the outcomes mean (the recorded controls
must split, every candidate must verify); the caller does. It exits non-zero only when it cannot do the work: an
unreadable request, or a trust root it cannot load.

This is the one script under `.github/` that imports packages outside the standard library, which is why it lives
here and not in `.github/scripts/`: it never runs on a bare interpreter.
"""

import argparse
import json
import pathlib
import re
import sys
from collections.abc import Callable, Mapping, Sequence
from typing import TYPE_CHECKING, Optional, cast

from cryptography.hazmat import asn1
from cryptography.x509 import ExtensionNotFound, ObjectIdentifier
from pypi_attestations import Distribution, Provenance
from sigstore.errors import VerificationError as PolicyError
from sigstore.verify import policy

if TYPE_CHECKING:
    from cryptography.x509 import Certificate


class ClaimReader:
    """Read one Fulcio claim from a signing certificate the way sigstore's own claim policies read it."""

    @staticmethod
    def text(cert: Certificate, oid: ObjectIdentifier) -> str:
        """Return the claim stored under oid, decoded from its DER UTF8String.

        Args:
            cert: The signing certificate sigstore is verifying.
            oid: A Fulcio claim from 1.3.6.1.4.1.57264.1.8 on, the claims written as DER UTF8Strings.

        Returns:
            The claim's text.

        Raises:
            sigstore.errors.VerificationError: When the certificate lacks the extension or its value is not one
                DER UTF8String; sigstore turns that into a refusal of the attestation.
        """
        try:
            extension = cert.extensions.get_extension_for_oid(oid).value
        except ExtensionNotFound:
            raise PolicyError(f"Certificate lacks claim {oid.dotted_string}.") from None
        try:
            return asn1.decode_der(str, cast(bytes, extension.value))
        except ValueError as error:
            raise PolicyError(f"Certificate claim {oid.dotted_string} is not one DER UTF8String: {error}") from None


class ExtensionEquals:
    """A sigstore verification policy requiring one Fulcio claim to equal one text value.

    sigstore ships an equality policy for each of Fulcio's claims 1.3.6.1.4.1.57264.1.8 to .22; this one serves the
    claims it has no class for, Deployment Environment (.23) and Token Subject (.24), with the same decoding.
    """

    def __init__(self, oid: str, value: str) -> None:
        """Hold the claim's OID and the exact text it must carry.

        Args:
            oid: The claim's dotted OID.
            value: The text the claim must equal.
        """
        self._oid = ObjectIdentifier(oid)
        self._value = value

    def verify(self, cert: Certificate) -> None:
        """Refuse the certificate unless the claim equals the expected value.

        Raises:
            sigstore.errors.VerificationError: When the claim is missing, malformed or different.
        """
        found = ClaimReader.text(cert, self._oid)
        if found != self._value:
            raise PolicyError(f"Certificate claim {self._oid.dotted_string} is {found!r}, expected {self._value!r}.")


class ExtensionMatches:
    """A sigstore verification policy requiring one Fulcio claim to match a regular expression in full.

    It serves the claims the caller accepts within a set, such as the run of an attestation another run of the
    same workflow uploaded.
    """

    def __init__(self, oid: str, pattern: str) -> None:
        """Hold the claim's OID and the pattern its whole text must match.

        Args:
            oid: The claim's dotted OID.
            pattern: A regular expression, matched with `re.fullmatch`.
        """
        self._oid = ObjectIdentifier(oid)
        self._pattern = re.compile(pattern)

    def verify(self, cert: Certificate) -> None:
        """Refuse the certificate unless the claim matches the pattern in full.

        Raises:
            sigstore.errors.VerificationError: When the claim is missing, malformed or does not match.
        """
        found = ClaimReader.text(cert, self._oid)
        if self._pattern.fullmatch(found) is None:
            raise PolicyError(f"Certificate claim {self._oid.dotted_string} is {found!r}, which does not match "
                              f"{self._pattern.pattern!r}.")


class AttestationVerifier:
    """Verify each request entry's attestation with Sigstore and report verified or refused.

    The identity policy is an `AllOf` of: sigstore's `Identity` (the one subject alternative name, issued by the
    expected issuer), sigstore's own equality policy for each expected claim it has one for, `ExtensionEquals` for
    the others, and `ExtensionMatches` for each pattern. `Attestation.verify` applies it after verifying the
    certificate chain, the transparency-log entry and the signature, then checks the statement's one subject
    against the file's name and sha256 and its predicate type.
    """

    FORMAT = 1
    PUBLISH_PREDICATE = "https://docs.pypi.org/attestations/publish/v1"
    EXACT_POLICIES: Mapping[str, Callable[[str], policy.VerificationPolicy]] = {
        "1.3.6.1.4.1.57264.1.8": policy.OIDCIssuerV2,
        "1.3.6.1.4.1.57264.1.9": policy.OIDCBuildSignerURI,
        "1.3.6.1.4.1.57264.1.10": policy.OIDCBuildSignerDigest,
        "1.3.6.1.4.1.57264.1.11": policy.OIDCRunnerEnvironment,
        "1.3.6.1.4.1.57264.1.12": policy.OIDCSourceRepositoryURI,
        "1.3.6.1.4.1.57264.1.13": policy.OIDCSourceRepositoryDigest,
        "1.3.6.1.4.1.57264.1.14": policy.OIDCSourceRepositoryRef,
        "1.3.6.1.4.1.57264.1.15": policy.OIDCSourceRepositoryIdentifier,
        "1.3.6.1.4.1.57264.1.16": policy.OIDCSourceRepositoryOwnerURI,
        "1.3.6.1.4.1.57264.1.17": policy.OIDCSourceRepositoryOwnerIdentifier,
        "1.3.6.1.4.1.57264.1.18": policy.OIDCBuildConfigURI,
        "1.3.6.1.4.1.57264.1.19": policy.OIDCBuildConfigDigest,
        "1.3.6.1.4.1.57264.1.20": policy.OIDCBuildTrigger,
        "1.3.6.1.4.1.57264.1.21": policy.OIDCRunInvocationURI,
        "1.3.6.1.4.1.57264.1.22": policy.OIDCSourceRepositoryVisibility,
    }

    def __init__(self, offline: bool) -> None:
        """Choose how the trust root is loaded.

        Args:
            offline: Use the trust root bundled with the pinned sigstore instead of refreshing it from Sigstore's
                TUF repository. CI never passes it; it exists for a local run with no network to that repository.
        """
        self._offline = offline

    def identity_policy(self, identity: Mapping[str, object]) -> policy.AllOf:
        """Build the policy that requires every part of the expected signing identity.

        Args:
            identity: The request's `identity` object: `san` and `issuer` (strings), `exact` and `patterns`
                (objects mapping a dotted claim OID to a string).

        Returns:
            One `AllOf` policy; it is never empty, because `Identity` is always its first member.

        Raises:
            KeyError, TypeError: When the identity object is malformed (a broken request, not a refusal).
        """
        exact = cast(Mapping[str, str], identity["exact"])
        patterns = cast(Mapping[str, str], identity["patterns"])
        children: list[policy.VerificationPolicy] = [
            policy.Identity(identity=str(identity["san"]), issuer=str(identity["issuer"])),
        ]
        for oid, value in sorted(exact.items()):
            factory = self.EXACT_POLICIES.get(oid)
            children.append(factory(value) if factory is not None else ExtensionEquals(oid, value))
        children.extend(ExtensionMatches(oid, pattern) for oid, pattern in sorted(patterns.items()))
        return policy.AllOf(children)

    def verify_entry(self, entry: Mapping[str, object]) -> dict[str, str]:
        """Verify one entry's attestation and return its outcome.

        Args:
            entry: `id`, `name` (the distribution's file name), `sha256`, `provenance` (the path of the recorded
                Integrity API answer) and `identity` (see `identity_policy`).

        Returns:
            `{"id", "outcome": "verified", "predicate_type"}`, or `{"id", "outcome": "refused", "reason"}` when the
            provenance is malformed, holds anything but one bundle with one attestation, fails Sigstore's
            verification or the identity policy, or attests anything but the PyPI publish predicate.

        Raises:
            OSError: When the provenance file cannot be read.
            sigstore.errors.Error: When the trust root cannot be loaded; that is an environment failure, not a
                verdict, so it ends the run.
        """
        entry_id = str(entry["id"])
        raw = pathlib.Path(str(entry["provenance"])).read_bytes()
        try:
            bundles = Provenance.model_validate_json(raw).attestation_bundles
            if len(bundles) != 1 or len(bundles[0].attestations) != 1:
                return {"id": entry_id, "outcome": "refused",
                        "reason": "the provenance must hold exactly one bundle with exactly one attestation"}
            distribution = Distribution(name=str(entry["name"]), digest=str(entry["sha256"]))
            predicate_type, predicate = bundles[0].attestations[0].verify(
                self.identity_policy(cast(Mapping[str, object], entry["identity"])), distribution,
                staging=False, offline=self._offline,
            )
        except ValueError as error:
            # pydantic's ValidationError and pypi-attestations' AttestationError are both ValueErrors; sigstore's
            # own VerificationError reaches here wrapped in the latter.
            return {"id": entry_id, "outcome": "refused", "reason": str(error)}
        if predicate_type != self.PUBLISH_PREDICATE or predicate not in (None, {}):
            return {"id": entry_id, "outcome": "refused",
                    "reason": f"the attestation's predicate is {predicate_type!r} with {predicate!r}, expected "
                              f"{self.PUBLISH_PREDICATE!r} with none"}
        return {"id": entry_id, "outcome": "verified", "predicate_type": predicate_type}


def main(argv: Optional[Sequence[str]] = None) -> int:
    """Verify every entry of a request and write one outcome per entry.

    Returns:
        0 once every entry has an outcome; a refusal is an outcome, not a failure of this script.

    Raises:
        ValueError: When the request has another format or no entry list.
    """
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--request", type=pathlib.Path, required=True)
    parser.add_argument("--result", type=pathlib.Path, required=True)
    parser.add_argument("--offline", action="store_true",
                        help="use the bundled trust root (local runs only; CI never passes this)")
    args = parser.parse_args(argv)
    request = json.loads(args.request.read_text(encoding="utf-8"))
    if not isinstance(request, dict) or request.get("format") != AttestationVerifier.FORMAT \
            or not isinstance(request.get("entries"), list):
        raise ValueError(f"Unreadable verifier request {args.request}; expected format {AttestationVerifier.FORMAT}.")
    verifier = AttestationVerifier(offline=args.offline)
    results = [verifier.verify_entry(cast(Mapping[str, object], entry)) for entry in request["entries"]]
    args.result.write_text(json.dumps({"format": AttestationVerifier.FORMAT, "results": results}, indent=2) + "\n",
                           encoding="utf-8")
    for result in results:
        print(f"{result['id']}: {result['outcome']}" + (f" ({result['reason']})" if "reason" in result else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
