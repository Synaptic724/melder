"""List the working tree's content delta against HEAD, with line endings normalized.

melder_1, 2026-10-10. Read-only git with GIT_OPTIONAL_LOCKS=0: `ls-tree` for HEAD's files and blob ids, `ls-files`
for the index, `ls-files -o --exclude-standard` for untracked files and `cat-file --batch` for the HEAD blobs of files
whose bytes differ; nothing refreshes or writes the index. A file whose git blob id equals HEAD's is identical; a file
that differs from HEAD only by CRLF versus LF endings (the Windows checkout) is counted, not listed. ContextCompass
live state (tickets and the two boards) is listed without a hash, because notes and rows keep landing after this
file is written. Writes tree/tree_delta.txt in this evidence pack and never lists that file itself.
"""
import collections, hashlib, os, subprocess
from concurrent.futures import ThreadPoolExecutor

REPO = os.path.expanduser("~/mnt/melder_private")
OUT = os.path.join(REPO, "context_compass", "artifacts", "core_protection_review_20261010", "tree", "tree_delta.txt")
ENV = dict(os.environ, GIT_OPTIONAL_LOCKS="0")
LIVE_STATE = ("context_compass/tickets/", "context_compass/attention_board.md", "context_compass/artifact_board.md")


def git(args, data=None):
    """Run one read-only git command in the repository and return its stdout bytes."""
    return subprocess.run(["git"] + args, cwd=REPO, env=ENV, input=data, capture_output=True, check=True).stdout


def split_z(raw):
    """Split NUL-separated git output into entries."""
    return [p for p in raw.decode("utf-8").split("\0") if p]


def read_file(path):
    """Return (path, bytes or None) for one working-tree file."""
    full = os.path.join(REPO, path)
    if not os.path.isfile(full):
        return path, None
    with open(full, "rb") as fh:
        return path, fh.read()


def blob_id(data):
    """Git's SHA-1 blob id of bytes."""
    return hashlib.sha1(b"blob %d\0" % len(data) + data).hexdigest()


def digest_for(path, data):
    """SHA256 of a deliverable's bytes, or 'live-state' for ContextCompass tickets and boards."""
    return "live-state" if path.startswith(LIVE_STATE) else hashlib.sha256(data).hexdigest()


def head_blobs(object_ids):
    """Return {object_id: bytes} through one cat-file batch."""
    raw = git(["cat-file", "--batch"], "".join(oid + "\n" for oid in object_ids).encode("ascii"))
    blobs, pos = {}, 0
    for oid in object_ids:
        end = raw.index(b"\n", pos)
        header = raw[pos:end].split()
        pos = end + 1
        size = int(header[2])
        blobs[oid] = raw[pos:pos + size]
        pos += size + 1
    return blobs


head = git(["rev-parse", "HEAD"]).decode().strip()
branch = git(["rev-parse", "--abbrev-ref", "HEAD"]).decode().strip()
head_ids = {}
for entry in split_z(git(["ls-tree", "-r", "-z", "HEAD"])):
    meta, path = entry.split("\t", 1)
    head_ids[path] = meta.split()[2]
index_files = set(split_z(git(["ls-files", "-z"])))
untracked = sorted(p for p in split_z(git(["ls-files", "-o", "--exclude-standard", "-z"]))
                   if os.path.join(REPO, p) != OUT)
with ThreadPoolExecutor(max_workers=32) as pool:
    work = dict(pool.map(read_file, sorted(head_ids) + sorted(index_files - set(head_ids)) + untracked))
rows, eol_only, same, mismatched = [], 0, 0, []
for path in sorted(head_ids):
    data = work[path]
    if data is None:
        rows.append(("DELETED", path, "-"))
    elif blob_id(data) == head_ids[path]:
        same += 1
    else:
        mismatched.append(path)
old = head_blobs([head_ids[p] for p in mismatched])
for path in mismatched:
    data = work[path]
    if data.replace(b"\r\n", b"\n") == old[head_ids[path]].replace(b"\r\n", b"\n"):
        eol_only += 1
    else:
        rows.append(("MODIFIED", path, digest_for(path, data)))
for path in sorted(index_files - set(head_ids)):
    data = work[path]
    rows.append(("ADDED_IN_INDEX", path, "-" if data is None else digest_for(path, data)))
for path in untracked:
    rows.append(("UNTRACKED", path, digest_for(path, work[path])))
groups = collections.Counter()
for kind, path, _ in rows:
    top = "/".join(path.split("/")[:3]) if path.startswith("context_compass/") else path.split("/")[0]
    groups[(kind, top)] += 1
with open(OUT, "w", encoding="utf-8", newline="\n") as fh:
    fh.write("head: {0} ({1})\n".format(head, branch))
    fh.write("HEAD files: {0} | byte-identical: {1} | line-ending-only differences: {2} | content changes and "
             "additions listed below: {3}\n".format(len(head_ids), same, eol_only, len(rows)))
    fh.write("\nsummary (kind, area: count)\n")
    for (kind, top), count in sorted(groups.items()):
        fh.write("  {0:15s} {1}: {2}\n".format(kind, top, count))
    fh.write("\nfiles (kind, path, sha256 of the working-tree bytes)\n")
    for kind, path, digest in rows:
        fh.write("{0:15s} {1} {2}\n".format(kind, path, digest))
print(open(OUT, encoding="utf-8").read().split("\nfiles")[0])
