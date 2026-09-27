import sys
sys.path.insert(0, ".")
import v2_experiment as ex
import v2_prototype as proto
seen = []
orig = proto.V2Runtime._compile_keys
def spy(self, keys):
    seen.append(keys)
    return orig(self, keys)
proto.V2Runtime._compile_keys = spy
calls = {"n": 0}
orig_init = proto.V2Runtime.__init__
def init(self, spell):
    orig_init(self, spell)
    normal = self.normal
    def counted(meld):
        calls["n"] += 1
        return normal(meld)
    self.normal = counted
proto.V2Runtime.__init__ = init
ex.threads(20, "/tmp/e4check.json")
print("compiled key sets:", seen, "v2 normal calls:", calls["n"])
