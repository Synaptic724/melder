"""Grade hard MCQ JSON submissions using sealed answer keys."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path


CONTEXT_ROOT = Path(__file__).resolve().parent.parent
SKILL_CHECK_ROOT = CONTEXT_ROOT / "skill_check"
SEALED_EXAM_ROOT = SKILL_CHECK_ROOT / ".sealed" / "exams"
SUBMISSIONS_DIR = SKILL_CHECK_ROOT / "submissions"
HISTORICAL_ROOT = SKILL_CHECK_ROOT / "historical_test_results"


def _rank(score: float) -> str:
    if score >= 95.0:
        return "S"
    if score >= 90.0:
        return "A"
    if score >= 80.0:
        return "B"
    if score >= 70.0:
        return "C"
    return "D"


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Grade hard MCQ submission JSON.")
    parser.add_argument("--cycle-id", required=True, help="Cycle id used by exam generator.")
    parser.add_argument(
        "--submission",
        default=None,
        help="Submission JSON path. Default: skill_check/submissions/cycle_<id>_answers.json",
    )
    return parser.parse_args()


def _load_submission(path: Path) -> dict[str, str]:
    if not path.exists():
        raise FileNotFoundError(f"Submission not found: {path}")
    # Accept UTF-8 files with or without BOM to avoid editor-dependent failures.
    payload = json.loads(path.read_text(encoding="utf-8-sig"))
    answers_raw = payload.get("answers")
    if not isinstance(answers_raw, dict):
        raise RuntimeError("Submission JSON must contain an `answers` object.")
    normalized: dict[str, str] = {}
    for question_id, letter in answers_raw.items():
        if not isinstance(question_id, str):
            continue
        if not isinstance(letter, str):
            normalized[question_id] = ""
            continue
        value = letter.strip().upper()
        normalized[question_id] = value if value in {"A", "B", "C", "D"} else ""
    return normalized


def main() -> None:
    args = _parse_args()
    cycle_id = args.cycle_id

    sealed_key_path = SEALED_EXAM_ROOT / f"cycle_{cycle_id}_answer_key.json"
    if not sealed_key_path.exists():
        raise FileNotFoundError(f"Sealed answer key not found: {sealed_key_path}")
    sealed = json.loads(sealed_key_path.read_text(encoding="utf-8"))
    questions = sealed.get("questions", [])
    if not isinstance(questions, list) or not questions:
        raise RuntimeError("Sealed answer key is empty or malformed.")

    submission_path = (
        Path(args.submission).resolve()
        if args.submission
        else (SUBMISSIONS_DIR / f"cycle_{cycle_id}_answers.json").resolve()
    )
    answers = _load_submission(submission_path)

    total = len(questions)
    correct = 0
    incorrect = 0
    unanswered = 0

    per_doc: dict[str, dict[str, int]] = {}
    misses: list[dict[str, str]] = []

    for row in questions:
        question_id = str(row["question_id"])
        doc_id = str(row["doc_id"])
        correct_letter = str(row["correct_letter"])
        selected = answers.get(question_id, "")
        if doc_id not in per_doc:
            per_doc[doc_id] = {"correct": 0, "incorrect": 0, "unanswered": 0, "total": 0}
        per_doc[doc_id]["total"] += 1

        if not selected:
            unanswered += 1
            per_doc[doc_id]["unanswered"] += 1
            misses.append(
                {
                    "question_id": question_id,
                    "doc_id": doc_id,
                    "selected": "<blank>",
                    "correct": correct_letter,
                    "status": "unanswered",
                }
            )
            continue

        if selected == correct_letter:
            correct += 1
            per_doc[doc_id]["correct"] += 1
        else:
            incorrect += 1
            per_doc[doc_id]["incorrect"] += 1
            misses.append(
                {
                    "question_id": question_id,
                    "doc_id": doc_id,
                    "selected": selected,
                    "correct": correct_letter,
                    "status": "incorrect",
                }
            )

    score = round((correct / total) * 100.0, 2) if total else 0.0
    rank = _rank(score)
    pass_status = "pass" if score >= 90.0 else "fail"

    HISTORICAL_ROOT.mkdir(parents=True, exist_ok=True)
    report_path = HISTORICAL_ROOT / f"cycle_{cycle_id}_hard_mcq_grade.md"
    report_json_path = HISTORICAL_ROOT / f"cycle_{cycle_id}_hard_mcq_grade.json"

    lines: list[str] = [
        "# Hard MCQ Grading Report",
        "",
        f"- cycle_id: {cycle_id}",
        f"- generated_at_utc: {datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}",
        f"- submission_path: {submission_path.relative_to(CONTEXT_ROOT).as_posix()}",
        f"- sealed_answer_key: {sealed_key_path.relative_to(CONTEXT_ROOT).as_posix()}",
        "",
        "## Summary",
        f"- total_questions: {total}",
        f"- correct: {correct}",
        f"- incorrect: {incorrect}",
        f"- unanswered: {unanswered}",
        f"- score: {score}",
        f"- rank: {rank}",
        f"- status: {pass_status}",
        "",
        "## Per-Doc Breakdown",
        "| doc_id | correct | incorrect | unanswered | total | doc_score |",
        "|---|---:|---:|---:|---:|---:|",
    ]

    for doc_id in sorted(per_doc):
        row = per_doc[doc_id]
        doc_score = round((row["correct"] / row["total"]) * 100.0, 2) if row["total"] else 0.0
        lines.append(
            f"| {doc_id} | {row['correct']} | {row['incorrect']} | "
            f"{row['unanswered']} | {row['total']} | {doc_score} |"
        )

    lines.extend(
        [
            "",
            "## Misses",
            "| question_id | doc_id | selected | correct | status |",
            "|---|---|---|---|---|",
        ]
    )
    for miss in misses:
        lines.append(
            f"| {miss['question_id']} | {miss['doc_id']} | {miss['selected']} | "
            f"{miss['correct']} | {miss['status']} |"
        )
    if not misses:
        lines.append("| none | none | none | none | none |")

    report_path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    report_json = {
        "cycle_id": cycle_id,
        "total_questions": total,
        "correct": correct,
        "incorrect": incorrect,
        "unanswered": unanswered,
        "score": score,
        "rank": rank,
        "status": pass_status,
        "per_doc": per_doc,
        "misses": misses,
    }
    report_json_path.write_text(json.dumps(report_json, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")

    print(f"cycle_id={cycle_id}")
    print(f"total_questions={total}")
    print(f"correct={correct}")
    print(f"incorrect={incorrect}")
    print(f"unanswered={unanswered}")
    print(f"score={score}")
    print(f"rank={rank}")
    print(f"status={pass_status}")
    print(f"report_markdown={report_path}")
    print(f"report_json={report_json_path}")


if __name__ == "__main__":
    main()
