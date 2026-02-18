"""Generate a blind hard-MCQ exam from the public pool and sealed truth keys."""

from __future__ import annotations

import argparse
import json
import math
import random
from datetime import datetime, timezone
from pathlib import Path


CONTEXT_ROOT = Path(__file__).resolve().parent.parent
SKILL_CHECK_ROOT = CONTEXT_ROOT / "skill_check"
MANIFEST_PATH = SKILL_CHECK_ROOT / "manifest" / "onboarding_manifest.yaml"
POOL_PATH = SKILL_CHECK_ROOT / "question_pool" / "hard_mcq_pool.jsonl"
SEALED_POOL_KEYS = SKILL_CHECK_ROOT / ".sealed" / "pool_truth_keys.jsonl"
SEALED_EXAM_ROOT = SKILL_CHECK_ROOT / ".sealed" / "exams"
SUBMISSIONS_DIR = SKILL_CHECK_ROOT / "submissions"

OPTION_LETTERS = ("A", "B", "C", "D")


def _load_manifest_required_docs() -> list[dict[str, str]]:
    if not MANIFEST_PATH.exists():
        raise FileNotFoundError(f"Manifest missing: {MANIFEST_PATH}")

    entries: list[dict[str, str]] = []
    current: dict[str, str] | None = None
    required = False
    for raw in MANIFEST_PATH.read_text(encoding="utf-8").splitlines():
        if raw.startswith("- doc_id: "):
            if current is not None and required:
                entries.append(current)
            current = {"doc_id": raw.split(": ", 1)[1].strip()}
            required = False
            continue
        if current is None or not raw.startswith("  "):
            continue
        stripped = raw.strip()
        if stripped.startswith("required_for_certification: "):
            required = stripped.split(": ", 1)[1].strip().lower() == "true"
            continue
        if ": " not in stripped:
            continue
        key, value = stripped.split(": ", 1)
        current[key] = value.strip()
    if current is not None and required:
        entries.append(current)
    return entries


def _load_pool_rows() -> dict[str, dict[str, object]]:
    if not POOL_PATH.exists():
        raise FileNotFoundError(
            "Question pool missing. Run `python context_compass/skill_check/build_hard_mcq_pool.py`."
        )

    rows: dict[str, dict[str, object]] = {}
    for raw in POOL_PATH.read_text(encoding="utf-8").splitlines():
        if not raw.strip():
            continue
        row = json.loads(raw)
        rows[str(row["question_id"])] = row
    return rows


def _load_truth_keys() -> dict[str, str]:
    if not SEALED_POOL_KEYS.exists():
        raise FileNotFoundError(
            "Sealed pool keys missing. Run the hard pool builder before exam generation."
        )
    keys: dict[str, str] = {}
    for raw in SEALED_POOL_KEYS.read_text(encoding="utf-8").splitlines():
        if not raw.strip():
            continue
        row = json.loads(raw)
        keys[str(row["question_id"])] = str(row["truth_option_id"])
    return keys


def _question_quota_for_doc(path: str) -> int:
    doc_path = CONTEXT_ROOT / path
    loc = len(doc_path.read_text(encoding="utf-8").splitlines())
    return max(1, math.ceil(loc / 100.0))


def _pick_questions(
    rng: random.Random,
    docs: list[dict[str, str]],
    pool_rows: dict[str, dict[str, object]],
) -> list[dict[str, object]]:
    by_doc: dict[str, list[dict[str, object]]] = {}
    for row in pool_rows.values():
        doc_id = str(row["doc_id"])
        by_doc.setdefault(doc_id, []).append(row)

    selected: list[dict[str, object]] = []
    for doc in docs:
        doc_id = str(doc["doc_id"])
        path = str(doc["path"])
        quota = _question_quota_for_doc(path)
        available = by_doc.get(doc_id, [])
        if len(available) < quota:
            raise RuntimeError(
                f"Insufficient pool questions for {doc_id}: need {quota}, have {len(available)}."
            )
        picks = rng.sample(available, quota)
        selected.extend(picks)

    rng.shuffle(selected)
    return selected


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate hard MCQ exam markdown.")
    parser.add_argument(
        "--cycle-id",
        default=None,
        help="Cycle id, default UTC timestamp in YYYY-MM-DDTHHMMSSZ.",
    )
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    cycle_id = args.cycle_id or datetime.now(timezone.utc).strftime("%Y-%m-%dT%H%M%SZ")

    docs = _load_manifest_required_docs()
    if not docs:
        raise RuntimeError("No required docs found in manifest.")

    pool_rows = _load_pool_rows()
    truth_keys = _load_truth_keys()

    rng_seed = f"{cycle_id}-{datetime.now(timezone.utc).timestamp()}-{random.SystemRandom().randint(1, 10**12)}"
    rng = random.Random(rng_seed)

    selected = _pick_questions(rng, docs, pool_rows)

    tests_dir = SKILL_CHECK_ROOT / "tests" / f"cycle_{cycle_id}"
    tests_dir.mkdir(parents=True, exist_ok=True)
    SUBMISSIONS_DIR.mkdir(parents=True, exist_ok=True)
    SEALED_EXAM_ROOT.mkdir(parents=True, exist_ok=True)

    exam_file = tests_dir / "hard_mcq_exam.md"
    submission_template_path = SUBMISSIONS_DIR / f"cycle_{cycle_id}_answers_template.json"
    sealed_answer_key_path = SEALED_EXAM_ROOT / f"cycle_{cycle_id}_answer_key.json"

    exam_lines: list[str] = [
        "# Hard MCQ Exam",
        "",
        f"- cycle_id: {cycle_id}",
        f"- question_count: {len(selected)}",
        "- format: MCQ only",
        "- selection_rule: 1 question per 100 LOC for each required doc",
        "",
        "Submission format:",
        "```json",
        "{",
        f'  "cycle_id": "{cycle_id}",',
        '  "answers": {',
        '    "<question_id>": "A|B|C|D"',
        "  }",
        "}",
        "```",
        "",
        "## Questions",
        "",
    ]

    sealed_key_rows: list[dict[str, object]] = []
    submission_answers: dict[str, str] = {}

    for idx, row in enumerate(selected, start=1):
        question_id = str(row["question_id"])
        options = [dict(option) for option in row["options"]]
        rng.shuffle(options)
        truth_option_id = truth_keys.get(question_id)
        if truth_option_id is None:
            raise RuntimeError(f"Missing sealed truth key for {question_id}")

        answer_letter = ""
        option_lines: list[str] = []
        for option_idx, option in enumerate(options):
            letter = OPTION_LETTERS[option_idx]
            option_id = str(option["option_id"])
            option_text = str(option["text"])
            option_lines.append(f"{letter}) {option_text}")
            if option_id == truth_option_id:
                answer_letter = letter

        if not answer_letter:
            raise RuntimeError(f"Unable to resolve answer letter for {question_id}")

        prompt = str(row["prompt"])
        source_path = str(row["source_path"])
        source_anchor = str(row["source_anchor"])
        exam_lines.extend(
            [
                f"### Q{idx:03d} ({question_id})",
                f"- source: `{source_path}#{source_anchor}`",
                f"- doc_id: `{row['doc_id']}`",
                f"- difficulty: `{row['difficulty']}`",
                "",
                prompt,
                "",
                *option_lines,
                "",
            ]
        )

        sealed_key_rows.append(
            {
                "question_index": idx,
                "question_id": question_id,
                "doc_id": row["doc_id"],
                "source_path": source_path,
                "source_anchor": source_anchor,
                "correct_letter": answer_letter,
            }
        )
        submission_answers[question_id] = ""

    exam_file.write_text("\n".join(exam_lines).rstrip() + "\n", encoding="utf-8")

    submission_template = {
        "cycle_id": cycle_id,
        "answers": submission_answers,
    }
    submission_template_path.write_text(
        json.dumps(submission_template, indent=2, ensure_ascii=True) + "\n",
        encoding="utf-8",
    )

    sealed_record = {
        "cycle_id": cycle_id,
        "generated_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "rng_seed": rng_seed,
        "question_count": len(sealed_key_rows),
        "questions": sealed_key_rows,
    }
    sealed_answer_key_path.write_text(
        json.dumps(sealed_record, indent=2, ensure_ascii=True) + "\n",
        encoding="utf-8",
    )

    print(f"cycle_id={cycle_id}")
    print(f"question_count={len(sealed_key_rows)}")
    print(f"exam_file={exam_file}")
    print(f"submission_template={submission_template_path}")
    print(f"sealed_answer_key={sealed_answer_key_path}")


if __name__ == "__main__":
    main()
