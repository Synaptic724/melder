"""Unpin Melder in MelderOps' pyproject.toml (owner direction 2026-09-30), keeping CRLF and the comment history.

Usage: python apply_unpin.py <priv_commandops root>
"""
import pathlib
import sys
import tomllib

PATH = pathlib.Path(sys.argv[1]) / "pyproject.toml"
raw = PATH.read_bytes()
crlf = b"\r\n" in raw
text = raw.decode("utf-8").replace("\r\n", "\n")
old = ("    # and of reconfiguring an active Nexus. The floor is 0.2.8212 (owner direction 2026-09-30).\n"
       "    \"melder>=0.2.8212\",\n")
new = ("    # and of reconfiguring an active Nexus. 0.2.8215 lets a dependency first built through a consumer\n"
       "    # (Toolbox's injected services) be melded directly afterwards.\n"
       "    # UNPINNED (owner direction 2026-09-30): any installed Melder satisfies this requirement, so a new\n"
       "    # build installs without a floor bump. The history above is what MelderOps calls; install a build\n"
       "    # that carries it (the melder_private dist/ wheel). PyPI's newest is 0.2.8207, older than those APIs.\n"
       "    \"melder\",\n")
if text.count(old) != 1:
    raise SystemExit(f"anchor matched {text.count(old)} times")
text = text.replace(old, new)
data = tomllib.loads(text)
dependencies = data["project"]["dependencies"]
if "melder" not in dependencies or any(d.startswith("melder") and d != "melder" for d in dependencies):
    raise SystemExit(f"unexpected dependencies: {dependencies}")
PATH.write_bytes((text.replace("\n", "\r\n") if crlf else text).encode("utf-8"))
check = tomllib.loads(PATH.read_bytes().decode("utf-8"))
print("dependencies:", check["project"]["dependencies"])
print("line endings:", "CRLF" if crlf else "LF", "- bare LF left:", PATH.read_bytes().count(b"\n") - PATH.read_bytes().count(b"\r\n"))
