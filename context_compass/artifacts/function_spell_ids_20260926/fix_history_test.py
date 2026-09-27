"""Add generation 12 to the pinned CACHE_VERSION_HISTORY in the integration test."""
import pathlib, sys
p = pathlib.Path(sys.argv[1]) / "tests/integration/melder/spellbook/test_cache_schema_version_integration.py"
raw = p.read_bytes().decode()
for nl in ("\r\n", "\n"):
    o = '    11: "unresolved_input_sockets",' + nl
    if raw.count(o) == 1:
        raw = raw.replace(o, o + '    12: "complete_bundle_restage",' + nl)
        break
else:
    raise SystemExit("anchor not found")
p.write_bytes(raw.encode()); print("ok", repr(nl))
