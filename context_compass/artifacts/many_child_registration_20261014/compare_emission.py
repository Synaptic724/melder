"""
Compare the site-plan source emitted before and after the fix (TASK-2026-10-14-fix_many_child_follows_holder).

Invariant 4 of the patch: every `_site_plan_executor` body (the warm path) is byte-identical; only `_miss{i}`
bodies change. Input files are the stdout of emit_plan_sources.py run against the original tree and the fixed tree.

Run: python compare_emission.py <before.txt> <after.txt>
"""
import sys


def sections(path: str) -> dict:
    out, cur, buf = {}, None, []
    for line in open(path, encoding="utf-8").read().splitlines():
        if line.startswith("===== "):
            if cur is not None:
                out[cur] = buf
            cur, buf = line, []
        else:
            buf.append(line)
    out[cur] = buf
    return out


def functions(lines: list) -> dict:
    funcs, name, body = {}, None, []
    for line in lines:
        if line.startswith("def "):
            if name:
                funcs[name] = body
            name, body = line.split("(")[0][4:], [line]
        else:
            body.append(line)
    if name:
        funcs[name] = body
    return funcs


def main() -> int:
    before, after = sections(sys.argv[1]), sections(sys.argv[2])
    assert list(before) == list(after)
    total = same = 0
    changed = []
    for key in before:
        fb, fa = functions(before[key]), functions(after[key])
        assert list(fb) == list(fa), key
        for name in fb:
            if name == "_site_plan_executor":
                total += 1
                same += fb[name] == fa[name]
            elif fb[name] != fa[name]:
                changed.append((key.replace("===== ", ""), name))
    print(f"executors identical: {same} of {total}")
    print(f"misses changed: {len(changed)}")
    for key, name in changed:
        print(f"  {key} {name}")
    return 0 if same == total else 1


if __name__ == "__main__":
    raise SystemExit(main())
