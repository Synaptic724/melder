"""Plain-dict form of mode (d): delete the yielded key and insert one that resizes the table, then resume the iterator."""
import sys
d = {}
for k in "VSOPQ":
    d[k] = k.lower()
it = iter(d.items())
first = next(it)
del d["V"]
d["X"] = "x"
rest = [k for k, _ in it]
print(sys.version.split()[0], "gil", sys._is_gil_enabled(), "first", first, "rest", rest, "S present", "S" in d)
