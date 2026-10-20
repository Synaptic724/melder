"""Does reading a class's annotations change its __dict__ on Python 3.14, and so the prototype's spell_id?

A1: a class with no annotations - its __dict__ keys before and after `annotationlib.get_annotations(cls)`.
A2: the same for a class with annotations.
A3: the prototype digest (artifacts/spell_identity_20261018/probes/code_digest_v2.py) of a class with no
    annotations before and after the read, and with `__annotate_func__` = None skipped.
"""
import annotationlib
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path.home() / "mnt/melder_private/context_compass/artifacts/spell_identity_20261018/probes"))
from code_digest_v2 import CodeDigest  # the prototype, imported by path


def keys(cls: type) -> list:
    return sorted(k for k in vars(cls) if k.startswith("__annot"))


class Plain:
    def method(self) -> int:
        return 1


class Annotated:
    field: int = 3

    def method(self) -> int:
        return 1


print("A1 Plain before:", keys(Plain))
annotationlib.get_annotations(Plain)
print("A1 Plain after: ", keys(Plain), "| __annotate_func__ =", vars(Plain).get("__annotate_func__", "<absent>"))
print("A2 Annotated before:", keys(Annotated), "| type:", type(vars(Annotated).get("__annotate_func__")).__name__)
annotationlib.get_annotations(Annotated)
print("A2 Annotated after: ", keys(Annotated))


class Fresh:
    def method(self) -> int:
        return 1


digest = CodeDigest()
before = digest.spell_id(Fresh)
annotationlib.get_annotations(Fresh)
after = digest.spell_id(Fresh)
print("A3 prototype id before == after the read:", before == after)


class SkipNone(CodeDigest):
    def _namespace_digest(self, cls: type, path: set) -> str:
        saved = {}
        if "__annotate_func__" in cls.__dict__ and cls.__dict__["__annotate_func__"] is None:
            saved["__annotate_func__"] = None
        excluded = self.EXCLUDED_CLASS_KEYS
        try:
            if saved:
                self.EXCLUDED_CLASS_KEYS = excluded | {"__annotate_func__"}
            return super()._namespace_digest(cls, path)
        finally:
            self.EXCLUDED_CLASS_KEYS = excluded


class Fresh2:
    def method(self) -> int:
        return 1


skip = SkipNone()
before2 = skip.spell_id(Fresh2)
annotationlib.get_annotations(Fresh2)
after2 = skip.spell_id(Fresh2)
print("A3 with __annotate_func__=None skipped, id before == after:", before2 == after2)
print(sys.version.split()[0], "free-threaded" if not sys._is_gil_enabled() else "GIL on")
