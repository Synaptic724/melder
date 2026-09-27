import sys, re
def load(p):
    d = {}
    for line in open(p, encoding="utf-8"):
        m = re.match(r"^\s*(\d+) (.*)$", line.rstrip("\n"))
        if m: d[m.group(2)] = int(m.group(1))
    return d
a, b = load(sys.argv[1]), load(sys.argv[2])
lost = [(k, a[k], b.get(k, 0)) for k in a if b.get(k, 0) < a[k]]
print("baseline lines with fewer copies after:", len(lost), "copies lost:", sum(x - y for _, x, y in lost))
for k, x, y in sorted(lost, key=lambda r: r[0]):
    if "verified_at: 2026-0" in k: continue
    print(f"{x}->{y} | {k[:130]}")
