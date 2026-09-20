
import pathlib

FINGERPRINT = "0" * 64
SCHEMA = "1.0.0"
RENDER_CALLS = []

def target_path():
    return pathlib.Path(__file__).parent / "manifest" / "artifact_manifest.py"

def source_fingerprint():
    return FINGERPRINT

def manifest_version():
    return SCHEMA

def render(version):
    RENDER_CALLS.append(version)
    return (
        'MANIFEST_VERSION = "%s"\n'
        'BUILT_FOR_VERSION = "%s"\n'
        'SOURCE_SHA256 = "%s"\n'
        'ENTRIES = ((\'a\', \'B\'),)\n' % (SCHEMA, version, FINGERPRINT)
    )

def write(version):
    target = target_path()
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(render(version), encoding="utf-8")
    return target, 1
