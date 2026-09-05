"""Install a checksum-pinned official Tectonic executable into the generated docs tool directory."""

import hashlib
import platform
import sys
import tarfile
import urllib.request
import zipfile
from pathlib import Path


class TectonicInstaller:
    """Provision only the supported official 0.17.0 desktop/CI compiler archives.

    The archive digest is verified before a single executable member is read.
    No archive path is extracted, no global PATH is changed, and existing source
    files are never touched. An existing archive/executable is checked on reuse.
    """

    _ARCHIVES = {
        "Windows": ("tectonic-0.17.0-x86_64-pc-windows-msvc.zip",
                    "f61ce51f0b0ade1015b7de7ef368541c5424e9756ecbd0d7af97d6d48030845f", "tectonic.exe"),
        "Linux": ("tectonic-0.17.0-x86_64-unknown-linux-gnu.tar.gz",
                  "1a715688baf591e650c8aeb160ae934e181685eecbb38b317de30b269ac5d606", "tectonic"),
    }
    _RELEASE = "https://github.com/tectonic-typesetting/tectonic/releases/download/tectonic%400.17.0/"

    def install(self) -> Path:
        """Return a verified local compiler, downloading the pinned official archive only if absent."""
        system = platform.system()
        if system not in self._ARCHIVES or platform.machine().lower() not in ("amd64", "x86_64"):
            raise ValueError("Automatic compiler setup supports x86_64 Windows/Linux; pass --tectonic for another host.")
        root = Path(__file__).resolve().parents[1] / "_build"
        target = root / "tools/tectonic"
        if root.resolve() != root or target.resolve() != target:
            raise ValueError("The generated compiler directory must not redirect through a symlink.")
        target.mkdir(parents=True, exist_ok=True)
        filename, expected, executable = self._ARCHIVES[system]
        archive = target.parent / filename
        if not archive.is_file():
            with urllib.request.urlopen(self._RELEASE + filename, timeout=60) as response:
                payload = response.read()
            if hashlib.sha256(payload).hexdigest() != expected:
                raise ValueError("Official compiler archive digest mismatch; refusing installation.")
            archive.write_bytes(payload)
        if hashlib.sha256(archive.read_bytes()).hexdigest() != expected:
            raise ValueError(f"Cached compiler archive digest mismatch: {archive}")
        if system == "Windows":
            with zipfile.ZipFile(archive) as bundle:
                binary = bundle.read(executable)
        else:
            with tarfile.open(archive, "r:gz") as bundle:
                member = bundle.getmember(executable)
                if not member.isfile():
                    raise ValueError("The compiler archive member must be a regular file.")
                stream = bundle.extractfile(member)
                if stream is None:
                    raise ValueError("The verified compiler archive has no executable payload.")
                with stream:
                    binary = stream.read()
        compiler = target / executable
        if compiler.resolve() != compiler:
            raise ValueError("The compiler executable must not redirect through a symlink.")
        if not compiler.is_file() or compiler.read_bytes() != binary:
            compiler.write_bytes(binary)
        if system == "Linux":
            compiler.chmod(0o755)
        return compiler


if __name__ == "__main__":
    sys.stdout.write(str(TectonicInstaller().install()) + "\n")
