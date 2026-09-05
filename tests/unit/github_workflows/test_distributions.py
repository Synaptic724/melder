"""Exercise archive/version rejection using small real wheel and sdist fixtures."""

import io
import pathlib
import tarfile
import zipfile
from types import ModuleType
from typing import Optional

import pytest


def package_files(subject: ModuleType) -> dict[str, bytes]:
    """Create a minimal package carrying the documented required manifests and payloads."""
    files = {name: b"# packaged asset\n" for name in subject.DistributionPolicy.REQUIRED}
    files["melder/__version__.py"] = b'__version__ = "0.3.0"\n'
    for name in subject.DistributionPolicy.VERSION_MANIFESTS:
        files[name] = b'BUILT_FOR_VERSION = "0.3.0"\n'
    return files


def metadata(version: str = "0.3.0", name: str = "melder") -> bytes:
    """Build wheel/sdist core metadata with an explicit supported Python requirement."""
    return f"Name: {name}\nVersion: {version}\nRequires-Python: >=3.14\n".encode("utf-8")


def write_archives(directory: pathlib.Path, subject: ModuleType,
                   wheel_changes: Optional[dict[str, Optional[bytes]]] = None,
                   sdist_changes: Optional[dict[str, Optional[bytes]]] = None,
                   symlink: bool = False) -> None:
    """Write real bounded fixture archives, optionally introducing one deliberate defect.

    Changes with None remove a member. Tar streams and zip handles are closed on
    every path. All artifacts remain beneath pytest's temporary directory.
    """
    files = package_files(subject)
    wheel = {**files, "melder-0.3.0.dist-info/METADATA": metadata()}
    sdist = {f"melder-0.3.0/src/{name}": content for name, content in files.items()}
    sdist["melder-0.3.0/PKG-INFO"] = metadata()
    for target, changes in ((wheel, wheel_changes), (sdist, sdist_changes)):
        for name, content in (changes or {}).items():
            if content is None:
                target.pop(name)
            else:
                target[name] = content
    with zipfile.ZipFile(directory / "melder-0.3.0-py3-none-any.whl", "w") as archive:
        for name, content in wheel.items():
            # Preserve deliberately malformed spellings instead of letting the
            # Windows ZipInfo constructor turn the bad fixture into a valid path.
            info = zipfile.ZipInfo()
            info.filename = name
            archive.writestr(info, content)
    with tarfile.open(directory / "melder-0.3.0.tar.gz", "w:gz") as archive:
        for name, content in sdist.items():
            info = tarfile.TarInfo(name)
            info.size = len(content)
            with io.BytesIO(content) as stream:
                archive.addfile(info, stream)
        if symlink:
            info = tarfile.TarInfo("melder-0.3.0/src/melder/link.py")
            info.type = tarfile.SYMTYPE
            info.linkname = "../../outside.py"
            archive.addfile(info)


def test_valid_archives_match_checkout_and_tag(distributions: ModuleType,
                                              tmp_path: pathlib.Path) -> None:
    """Accept a complete wheel/sdist pair for either plain or v-prefixed version tags."""
    write_archives(tmp_path, distributions)
    distributions.verify_distributions(tmp_path, "0.3.0", "v0.3.0")
    distributions.verify_distributions(tmp_path, "0.3.0", "0.3.0")


@pytest.mark.parametrize("tag", ["v0.3.1", "vv0.3.0", "v0.3.0rc1"])
def test_wrong_release_tag_refuses_artifacts(distributions: ModuleType,
                                            tmp_path: pathlib.Path, tag: str) -> None:
    """A tag cannot relabel a different package version or strip arbitrary v prefixes."""
    write_archives(tmp_path, distributions)
    with pytest.raises(ValueError, match="tag"):
        distributions.verify_distributions(tmp_path, "0.3.0", tag)


def test_missing_or_duplicate_distribution_count_is_refused(distributions: ModuleType,
                                                           tmp_path: pathlib.Path) -> None:
    """Refuse an empty or ambiguous upload directory before inspecting its contents."""
    with pytest.raises(ValueError, match="one wheel and one sdist"):
        distributions.verify_distributions(tmp_path, "0.3.0")
    write_archives(tmp_path, distributions)
    (tmp_path / "extra.whl").write_bytes(b"not a wheel")
    with pytest.raises(ValueError, match="one wheel and one sdist"):
        distributions.verify_distributions(tmp_path, "0.3.0")


def test_unverified_extra_upload_file_is_refused(distributions: ModuleType,
                                                tmp_path: pathlib.Path) -> None:
    """Every file passed to the upload action must belong to the inspected distribution pair."""
    write_archives(tmp_path, distributions)
    (tmp_path / "extra.zip").write_bytes(b"unverified package")
    with pytest.raises(ValueError, match="outside the verified"):
        distributions.verify_distributions(tmp_path, "0.3.0")


@pytest.mark.parametrize("member", [
    "../escaped.py", "/absolute.py", "C:/drive.py", "melder\\bad.py", "melder/ok.py\x00bad",
    "other_package/module.py", "melder/cache.melc", "melder/__pycache__/a.pyc",
])
def test_wheel_rejects_unsafe_or_unrelated_members(distributions: ModuleType,
                                                 tmp_path: pathlib.Path, member: str) -> None:
    """Package verification catches traversal, cache leakage, and unrelated top-level roots."""
    write_archives(tmp_path, distributions, wheel_changes={member: b"bad"})
    with pytest.raises(ValueError):
        distributions.verify_distributions(tmp_path, "0.3.0")


@pytest.mark.parametrize("member", [
    "melder-0.3.0/../escaped.py", "melder-0.3.0/tests/test_x.py",
    "melder-0.3.0/src/melder/private.sqlite", "another-root/README.md",
])
def test_sdist_rejects_unsafe_or_unrelated_members(distributions: ModuleType,
                                                 tmp_path: pathlib.Path, member: str) -> None:
    """The source archive must obey its own release boundary as well as the wheel's."""
    write_archives(tmp_path, distributions, sdist_changes={member: b"bad"})
    with pytest.raises(ValueError):
        distributions.verify_distributions(tmp_path, "0.3.0")


def test_sdist_links_are_not_ignored(distributions: ModuleType, tmp_path: pathlib.Path) -> None:
    """A non-regular tar member cannot evade verification by being omitted from a file list."""
    write_archives(tmp_path, distributions, symlink=True)
    with pytest.raises(ValueError, match="non-regular"):
        distributions.verify_distributions(tmp_path, "0.3.0")


@pytest.mark.parametrize("archive", ["wheel", "sdist"])
def test_required_runtime_asset_must_ship_in_both_archives(distributions: ModuleType,
                                                         tmp_path: pathlib.Path,
                                                         archive: str) -> None:
    """Losing the PEP 561 marker must fail qualification of either distribution."""
    if archive == "wheel":
        write_archives(tmp_path, distributions, wheel_changes={"melder/py.typed": None})
    else:
        write_archives(tmp_path, distributions,
                       sdist_changes={"melder-0.3.0/src/melder/py.typed": None})
    with pytest.raises(ValueError, match="missing required assets"):
        distributions.verify_distributions(tmp_path, "0.3.0")


@pytest.mark.parametrize("archive", ["wheel", "sdist"])
def test_archive_metadata_version_must_match_checkout(distributions: ModuleType,
                                                     tmp_path: pathlib.Path, archive: str) -> None:
    """Neither a wheel nor an sdist built from another version may pass the final guard."""
    if archive == "wheel":
        write_archives(tmp_path, distributions,
                       wheel_changes={"melder-0.3.0.dist-info/METADATA": metadata("0.3.1")})
    else:
        write_archives(tmp_path, distributions,
                       sdist_changes={"melder-0.3.0/PKG-INFO": metadata("0.3.1")})
    with pytest.raises(ValueError, match="versions"):
        distributions.verify_distributions(tmp_path, "0.3.0")


def test_asset_version_mismatch_is_detected(distributions: ModuleType,
                                           tmp_path: pathlib.Path) -> None:
    """A current wheel version cannot hide a stale bind-guard asset version."""
    name = "melder/_build_assets/_bind_guard/manifest/bind_guard_manifest.py"
    write_archives(tmp_path, distributions, wheel_changes={name: b'BUILT_FOR_VERSION = "0.2.0"\n'})
    with pytest.raises(ValueError, match="versions"):
        distributions.verify_distributions(tmp_path, "0.3.0")


def test_wrong_package_identity_is_refused(distributions: ModuleType, tmp_path: pathlib.Path) -> None:
    """Do not publish another package merely because its filename resembles melder."""
    write_archives(tmp_path, distributions,
                   wheel_changes={"melder-0.3.0.dist-info/METADATA": metadata(name="unrelated")})
    with pytest.raises(ValueError, match="must describe melder"):
        distributions.verify_distributions(tmp_path, "0.3.0")


def test_version_assignment_is_literal_and_never_executed(distributions: ModuleType) -> None:
    """The verifier reads literals safely instead of importing package initialization code."""
    assert distributions.assignment('__version__: str = "0.3.0"', "__version__") == "0.3.0"
    with pytest.raises(ValueError):
        distributions.assignment('__version__ = dangerous()', "__version__")
    with pytest.raises(ValueError):
        distributions.assignment('__version__ = 3', "__version__")
