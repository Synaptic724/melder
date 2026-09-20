
import pathlib

_TEXT = "generated for {version}\n"

def target_path():
    return pathlib.Path(__file__).parent / "artifact.py"

def render(version):
    return _TEXT.format(version=version)

def write(version):
    target = target_path()
    target.write_text(render(version), encoding="utf-8")
    return target, 1
