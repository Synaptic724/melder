"""Scratch probe for contract items 1-2 (custody path handling). Writes only under argv[1]."""
import os
import shutil
import sys
import sysconfig
import types
from pathlib import Path, PurePosixPath, PureWindowsPath

from melder.crystallizer.crystal_analysis.crystal_analyzer import CrystalAnalyzer
from melder.crystallizer.crystal_analysis.physical_source_cache import PhysicalSourceCache

BASE = Path(sys.argv[1])
BASE.mkdir(parents=True, exist_ok=False)
BASE = BASE.resolve()


def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


project = BASE / "project"
src = project / "src"
src.mkdir(parents=True)
env_site = BASE / "outside_env" / "lib" / "python3.14t" / "site-packages"
write(env_site / "linkpkg" / "__init__.py", "VALUE = 1\n")
write(env_site / "hardmod.py", "VALUE = 2\n")
os.symlink(env_site / "linkpkg", src / "linkpkg")
os.link(env_site / "hardmod.py", src / "hardmod.py")
write(src / "inside_mod.py", "VALUE = 3\n")
elsewhere = BASE / "elsewhere"
elsewhere.mkdir()
os.symlink(src / "inside_mod.py", elsewhere / "alias_mod.py")
dynload = Path(sys.base_prefix) / "lib" / ("python%d.%dt" % sys.version_info[:2]) / "lib-dynload"
native = next(p for p in sorted(dynload.iterdir()) if p.name.endswith(".so"))
native_copy = src / native.name
shutil.copy2(native, native_copy)
foreign = BASE / "foreign_venv"
write(foreign / "pyvenv.cfg", "home = /usr/bin\n")
write(foreign / "lib" / "python3.14t" / "site-packages" / "foreignpkg" / "__init__.py", "VALUE = 4\n")
write(foreign / "lib" / "foreign_plain" / "plainmod.py", "VALUE = 5\n")
nested = project / ".venv_new"
write(nested / "pyvenv.cfg", "home = /usr/bin\n")
write(nested / "lib" / "python3.14t" / "site-packages" / "nestedpkg" / "__init__.py", "VALUE = 6\n")
write(project / "build" / "lib" / "genmod.py", "VALUE = 7\n")

site_roots = CrystalAnalyzer.resolve_site_package_root_paths()
print("python", sys.version.split()[0], "| site roots", [str(p) for p in site_roots])
print("missing root accepted:", CrystalAnalyzer.resolve_user_root_paths([str(BASE / "no" / "such" / "root")]))

analyzer = CrystalAnalyzer(
    user_source_root_paths=(project,),
    site_package_root_paths=site_roots,
    site_package_dependency_descent=False,
)
cases = {
    "symlink in root -> outside site-packages": src / "linkpkg" / "__init__.py",
    "hard link in root (inode shared with env)": src / "hardmod.py",
    "hard link's env-side name": env_site / "hardmod.py",
    "symlink outside root -> file in root": elsewhere / "alias_mod.py",
    "native extension copied into root": native_copy,
    "foreign venv site-packages outside root": foreign / "lib" / "python3.14t" / "site-packages" / "foreignpkg" / "__init__.py",
    "foreign venv module outside site-packages": foreign / "lib" / "foreign_plain" / "plainmod.py",
    "nested venv (pyvenv.cfg) inside root": nested / "lib" / "python3.14t" / "site-packages" / "nestedpkg" / "__init__.py",
    "build/ artifact inside root": project / "build" / "lib" / "genmod.py",
}
try:
    for label, path in cases.items():
        custody = analyzer._match_custody(module_name="probe", module_obj=None, module_path=path)
        print("%-46s -> %-12s resolved=%s" % (label, custody.kind, path.resolve()))
finally:
    analyzer.cleanup()
st_root = (src / "hardmod.py").stat()
st_env = (env_site / "hardmod.py").stat()
print("hard link: same inode", st_root.st_ino == st_env.st_ino, "| st_nlink", st_root.st_nlink)
(src / "hardmod.py").write_text("VALUE = 9\n", encoding="utf-8")
print("write through the root name changes the env file:", (env_site / "hardmod.py").read_text(encoding="utf-8").strip())

# Walk level: a native extension under the root, imported by user code.
write(src / "app_mod.py", "import cc_native_probe\nimport inside_mod\n")
fake = types.ModuleType("cc_native_probe")
fake.__file__ = str(native_copy)
sys.modules["cc_native_probe"] = fake
sys.path.insert(0, str(src))
analyzer = CrystalAnalyzer(user_source_root_paths=(project,), site_package_root_paths=site_roots,
                           site_package_dependency_descent=False)
try:
    result = analyzer.analyze_spell_root(root_module_name="app_mod", root_module_obj=None,
                                         root_module_path=src / "app_mod.py")
    kinds = dict(result.module_to_kind)
    print("walk: native kind", kinds.get("cc_native_probe"),
          "| fingerprinted", "cc_native_probe" in dict(result.physical_module_fingerprints),
          "| provenance/binary identity", "cc_native_probe" in dict(result.distribution_provenance))
    result.cleanup()
finally:
    analyzer.cleanup()

# Provenance for an installed dependency of user code, descent off vs on.
write(src / "uses_pytest.py", "import pytest\n")
for descent in (False, True):
    analyzer = CrystalAnalyzer(user_source_root_paths=(src,), site_package_root_paths=site_roots,
                               site_package_dependency_descent=descent)
    try:
        result = analyzer.analyze_spell_root(root_module_name="uses_pytest", root_module_obj=None,
                                             root_module_path=src / "uses_pytest.py")
        print("descent=%s: pytest kind %s | provenance row %s" % (
            descent, dict(result.module_to_kind).get("pytest"), "pytest" in dict(result.distribution_provenance)))
        result.cleanup()
    finally:
        analyzer.cleanup()

# Stat-guarded fingerprint after a same-size rewrite with the mtime restored.
stat_file = BASE / "stat_probe.py"
stat_file.write_text("A = 1\n", encoding="utf-8")
_text, first_sha, _err = PhysicalSourceCache.read_text_and_fingerprint("stat_probe", stat_file)
before = stat_file.stat()
stat_file.write_text("B = 2\n", encoding="utf-8")
os.utime(stat_file, ns=(before.st_atime_ns, before.st_mtime_ns))
served = PhysicalSourceCache.fingerprint_if_unchanged(stat_file)
_text2, fresh_sha, _err2 = PhysicalSourceCache.read_text_and_fingerprint("stat_probe", stat_file)
print("stat guard served the old hash:", served == first_sha, "| fresh hash differs:", fresh_sha != first_sha)

print("windows case:", PureWindowsPath(r"C:\Users\Mark\Proj\src\a.py").is_relative_to(PureWindowsPath(r"c:\users\mark\proj")))
print("posix case:", PurePosixPath("/home/Mark/proj/src/a.py").is_relative_to(PurePosixPath("/home/mark/proj")))
print("windows dotdot (lexical):", PureWindowsPath(r"C:\proj\src\..\..\outside\x.py").is_relative_to(PureWindowsPath(r"C:\proj")))
