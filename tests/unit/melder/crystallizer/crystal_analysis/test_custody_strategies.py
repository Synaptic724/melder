"""
Unit tests for the crystal_analysis custody strategies: authority matching,
source resolution honesty, fingerprint claims, and descent law.

Runs only on 3.14t (melder package root import chain).
"""
import hashlib

from melder.crystallizer.crystal_analysis.custody.binary_unknown_custody_strategy import (
    BinaryUnknownCustodyStrategy,
)
from melder.crystallizer.crystal_analysis.custody.site_package_custody_strategy import (
    SitePackageCustodyStrategy,
)
from melder.crystallizer.crystal_analysis.custody.synthetic_custody_strategy import (
    SyntheticCustodyStrategy,
)
from melder.crystallizer.crystal_analysis.custody.user_source_custody_strategy import (
    UserSourceCustodyStrategy,
)


def test_user_source_matches_only_under_configured_roots(tmp_path):
    """
    Contract: user_source authority is policy-driven - a module file under a
    configured root matches; the same file against a foreign root does not;
    pathless modules never match.
    """
    module_file = tmp_path / "owned_module.py"
    module_file.write_text("VALUE = 1\n", encoding="utf-8")
    strategy = UserSourceCustodyStrategy((tmp_path.resolve(),))
    foreign = UserSourceCustodyStrategy((tmp_path.resolve() / "elsewhere",))
    try:
        assert strategy.matches(
            module_name="owned_module",
            module_obj=None,
            module_path=module_file,
        )
        assert not foreign.matches(
            module_name="owned_module",
            module_obj=None,
            module_path=module_file,
        )
        assert not strategy.matches(
            module_name="pathless",
            module_obj=None,
            module_path=None,
        )
        assert strategy.kind == "user_source"
        assert strategy.descends is True
    finally:
        strategy.cleanup()
        foreign.cleanup()


def test_user_source_resolves_text_and_claims_sha256_fingerprint(tmp_path):
    """
    Contract: user_source reads `.py` source and its fingerprint claim is
    the hex SHA256 of the UTF-8 text (the S1 drift-detection capability).
    """
    source_text = "class Owned:\n    pass\n"
    module_file = tmp_path / "owned_module.py"
    module_file.write_text(source_text, encoding="utf-8")
    strategy = UserSourceCustodyStrategy((tmp_path.resolve(),))
    try:
        resolved_text, error_text = strategy.resolve_source(
            module_name="owned_module",
            module_obj=None,
            module_path=module_file,
        )
        assert resolved_text == source_text
        assert error_text is None
        assert strategy.fingerprint(source_text) == hashlib.sha256(
            source_text.encode("utf-8")
        ).hexdigest()
    finally:
        strategy.cleanup()


def test_user_source_returns_no_source_for_non_source_extensions(tmp_path):
    """
    Contract: non `.py`/`.pyi` backing files expose no source and raise no
    error - `(None, None)`, preserving the historical read law.
    """
    binary_file = tmp_path / "compiled.pyd"
    binary_file.write_bytes(b"\x00\x01")
    strategy = UserSourceCustodyStrategy((tmp_path.resolve(),))
    try:
        resolved_text, error_text = strategy.resolve_source(
            module_name="compiled",
            module_obj=None,
            module_path=binary_file,
        )
        assert resolved_text is None
        assert error_text is None
    finally:
        strategy.cleanup()


def test_site_package_matches_roots_and_path_text_fallback(tmp_path):
    """
    Contract: site_package matches configured site roots AND the historical
    `site-packages`/`dist-packages` path-text fallback; it makes no
    fingerprint claim over third-party code in S1.
    """
    site_root = tmp_path / "env" / "site-packages"
    site_root.mkdir(parents=True)
    module_file = site_root / "third_party.py"
    module_file.write_text("VALUE = 2\n", encoding="utf-8")

    rooted = SitePackageCustodyStrategy((site_root.resolve(),))
    unrooted = SitePackageCustodyStrategy(())
    try:
        assert rooted.matches(
            module_name="third_party",
            module_obj=None,
            module_path=module_file,
        )
        # Path-text fallback: no configured roots, but the path contains
        # the site-packages marker.
        assert unrooted.matches(
            module_name="third_party",
            module_obj=None,
            module_path=module_file,
        )
        assert unrooted.fingerprint("VALUE = 2\n") is None
        assert rooted.kind == "site_package"
        assert rooted.descends is True
    finally:
        rooted.cleanup()
        unrooted.cleanup()


def test_binary_unknown_is_the_terminal_leaf_fallback(tmp_path):
    """
    Contract: the fallback claims everything, exposes no source, makes no
    fingerprint claim, and never descends - unknown targets stay honest
    manifest leaves.
    """
    strategy = BinaryUnknownCustodyStrategy()
    try:
        assert strategy.matches(
            module_name="anything",
            module_obj=None,
            module_path=None,
        )
        assert strategy.matches(
            module_name="anything_else",
            module_obj=object(),
            module_path=tmp_path / "whatever.so",
        )
        assert strategy.resolve_source(
            module_name="anything",
            module_obj=None,
            module_path=None,
        ) == (None, None)
        assert strategy.fingerprint("text") is None
        assert strategy.kind == "unknown"
        assert strategy.descends is False
    finally:
        strategy.cleanup()


def test_synthetic_custody_rejects_non_synthetic_objects():
    """
    Contract: synthetic authority is a strict protocol identity check -
    None and plain module-like objects never match, and the M3 harvest
    returns None for non-synthetic objects.
    """
    strategy = SyntheticCustodyStrategy()
    try:
        assert not strategy.matches(
            module_name="mod",
            module_obj=None,
            module_path=None,
        )
        assert not strategy.matches(
            module_name="mod",
            module_obj=object(),
            module_path=None,
        )
        assert SyntheticCustodyStrategy.harvest_payload(object()) is None
        assert strategy.fingerprint("anything") is None
        assert strategy.kind == "synthetic_module"
        assert strategy.descends is True
    finally:
        strategy.cleanup()


def test_custody_cleanup_is_idempotent(tmp_path):
    """
    Contract: strategy cleanup is idempotent and safe to repeat.
    """
    strategy = UserSourceCustodyStrategy((tmp_path.resolve(),))
    strategy.cleanup()
    strategy.cleanup()
    fallback = BinaryUnknownCustodyStrategy()
    fallback.cleanup()
    fallback.cleanup()
def test_physical_read_and_fingerprint_claim_contract_mirrors():
    """
    Purpose:
        Pin the IO-economy contract properties 1:1 against the custody
        family's read/fingerprint laws: physical readers route through the
        stat cache; only base-SHA256 claimers may fast-path fingerprints.
    Contract:
        user_source: reads physical + claims sha256. site_package: reads
        physical, NO claim (S1). synthetic + binary/unknown: neither.
    """
    from melder.crystallizer.crystal_analysis.custody.user_source_custody_strategy import (
        UserSourceCustodyStrategy,
    )
    from melder.crystallizer.crystal_analysis.custody.site_package_custody_strategy import (
        SitePackageCustodyStrategy,
    )
    from melder.crystallizer.crystal_analysis.custody.synthetic_custody_strategy import (
        SyntheticCustodyStrategy,
    )
    from melder.crystallizer.crystal_analysis.custody.binary_unknown_custody_strategy import (
        BinaryUnknownCustodyStrategy,
    )

    user = UserSourceCustodyStrategy(())
    site = SitePackageCustodyStrategy(())
    synthetic = SyntheticCustodyStrategy()
    unknown = BinaryUnknownCustodyStrategy()
    try:
        assert user.reads_physical_source is True
        assert user.claims_sha256_source_fingerprint is True
        assert site.reads_physical_source is True
        assert site.claims_sha256_source_fingerprint is False
        assert synthetic.reads_physical_source is False
        assert synthetic.claims_sha256_source_fingerprint is False
        assert unknown.reads_physical_source is False
        assert unknown.claims_sha256_source_fingerprint is False
    finally:
        user.cleanup()
        site.cleanup()
        synthetic.cleanup()
        unknown.cleanup()
