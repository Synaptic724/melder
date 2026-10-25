"""Scratch pytest plugin (melder_1, /tmp/cc_res only): record each test's outcome as it ends, resumably.

EXP_LOG names a tab-separated log: nodeid, outcome, tag (EXPERIMENT_A / EXPERIMENT_B / -), first error line.
EXP_STARTED names a log of nodeids that started. A nodeid already in EXP_LOG is deselected, so a run killed by
its time limit resumes where it stopped; a nodeid started but never finished (killed mid-test) is recorded as
KILLED and deselected, to be rerun alone.
"""
import os

_state = {}


def _read_ids(path):
    ids = []
    if os.path.exists(path):
        with open(path, encoding="utf-8") as fh:
            for line in fh:
                nodeid = line.rstrip("\n").split("\t")[0]
                if nodeid:
                    ids.append(nodeid)
    return ids


def pytest_collection_modifyitems(session, config, items):
    log_path = os.environ["EXP_LOG"]
    done = set(_read_ids(log_path))
    started = _read_ids(os.environ["EXP_STARTED"])
    killed = [n for n in started if n not in done]
    if killed:
        with open(log_path, "a", encoding="utf-8") as fh:
            for nodeid in dict.fromkeys(killed):
                fh.write("%s\tKILLED\t-\tstarted in an earlier run that hit its time limit\n" % nodeid)
                done.add(nodeid)
    keep = [item for item in items if item.nodeid not in done]
    dropped = [item for item in items if item.nodeid in done]
    if dropped:
        config.hook.pytest_deselected(items=dropped)
        items[:] = keep


def pytest_runtest_logstart(nodeid, location):
    with open(os.environ["EXP_STARTED"], "a", encoding="utf-8") as fh:
        fh.write(nodeid + "\n")


def pytest_runtest_logreport(report):
    entry = _state.setdefault(report.nodeid, {"outcome": "passed", "tag": "-", "msg": ""})
    if report.failed:
        entry["outcome"] = "FAILED" if report.when == "call" else "ERROR_" + report.when
        text = report.longreprtext or ""
        tag = "-"
        for marker in ("EXPERIMENT_A", "EXPERIMENT_B"):
            if marker in text:
                tag = marker
                break
        lines = [ln for ln in text.splitlines() if ln.startswith("E ")]
        if tag != "-":
            hits = [ln for ln in text.splitlines() if tag in ln]
            msg = hits[0] if hits else (lines[0] if lines else "")
        else:
            msg = lines[0] if lines else (text.splitlines()[-1] if text else "")
        if entry["tag"] == "-":
            entry["tag"] = tag
            entry["msg"] = msg.strip()[:400].replace("\t", " ")
    elif report.skipped and entry["outcome"] == "passed":
        entry["outcome"] = "skipped"
    if report.when == "teardown":
        with open(os.environ["EXP_LOG"], "a", encoding="utf-8") as fh:
            fh.write("%s\t%s\t%s\t%s\n" % (report.nodeid, entry["outcome"], entry["tag"], entry["msg"]))
        _state.pop(report.nodeid, None)
