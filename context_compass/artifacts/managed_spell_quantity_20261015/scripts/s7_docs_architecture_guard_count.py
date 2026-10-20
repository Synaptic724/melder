"""S7 D7: correct the stale manifest size in src_architecture's guardrails (found while scoring the document).

"Entrypoints and Runtime Guardrails" says a silently dead test patch "would let the real 619-entry manifest begin
refusing binds"; the manifest holds 628 entries at 0.2.8246, as the same section's count says four lines earlier.
One exact phrase is replaced (asserted once); the dated 2026-10-01 handoff entry that recorded 619 at 0.2.8215 is
history and stays. Regenerate the index after this script.
Run from the repository root: python <this file>
"""
import pathlib

p = pathlib.Path("context_compass/system_docs/src_architecture.md")
t = p.read_bytes().decode("utf-8")
old = "fixture; a silently-dead patch would let the real 619-entry manifest begin refusing\n"
new = "fixture; a silently-dead patch would let the real manifest (628 entries at 0.2.8246) begin refusing\n"
if t.count(old) != 1:
    raise SystemExit(f"the phrase occurs {t.count(old)} times (expected 1); nothing written")
p.write_bytes(t.replace(old, new).encode("utf-8"))
print("src_architecture: guard count corrected")
