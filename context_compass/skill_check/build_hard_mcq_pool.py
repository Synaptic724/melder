"""Build a hard multiple-choice question pool for blind skill checks.

This generator creates:
1) A public question pool (`question_pool/hard_mcq_pool.jsonl`) without
   correct answers.
2) A sealed truth-key file (`.sealed/pool_truth_keys.jsonl`) used only by
   exam generation and grading scripts.

Design goals:
- All questions are MCQ-only.
- Each question has 4 options: 1 truth + 3 close, deterministic lies.
- Pool size target defaults to 10x current question volume.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


CONTEXT_ROOT = Path(__file__).resolve().parent.parent
SKILL_CHECK_ROOT = CONTEXT_ROOT / "skill_check"
MANIFEST_PATH = SKILL_CHECK_ROOT / "manifest" / "onboarding_manifest.yaml"
PUBLIC_POOL_PATH = SKILL_CHECK_ROOT / "question_pool" / "hard_mcq_pool.jsonl"
POOL_META_PATH = SKILL_CHECK_ROOT / "question_pool" / "hard_mcq_pool_meta.json"
SEALED_KEY_PATH = SKILL_CHECK_ROOT / ".sealed" / "pool_truth_keys.jsonl"

QUESTION_HEADER_RE = re.compile(r"^### [A-Z0-9_]+::Q[0-9]{3}$")

NORMATIVE_KEYWORDS = (
    "must",
    "must not",
    "required",
    "require",
    "do not",
    "cannot",
    "never",
    "always",
    "before",
    "after",
    "only",
    "blocked",
    "approval",
    "certification",
    "gate",
)

PROMPT_TEMPLATES = (
    "Select the single true statement for this policy claim.",
    "Choose the exact rule that remains valid under this source anchor.",
    "Pick the one statement that is true for this document context.",
    "Identify the only correct claim from this near-match option set.",
    "Choose the true invariant; the other three options are close lies.",
    "Pick the statement that preserves the policy gate exactly.",
)

MODALITY_SWAPS = (
    (r"\bmust not\b", "must"),
    (r"\bmust\b", "must not"),
    (r"\brequired\b", "optional"),
    (r"\bcannot\b", "can"),
    (r"\bnever\b", "sometimes"),
    (r"\balways\b", "usually"),
)

SEQUENCE_SWAPS = (
    (r"\bbefore\b", "after"),
    (r"\bafter\b", "before"),
    (r"\bfirst\b", "last"),
    (r"\bthen\b", "before that"),
    (r"\bprior to\b", "after"),
)

SCOPE_SWAPS = (
    (r"\bonly\b", "primarily"),
    (r"\ball\b", "some"),
    (r"\bevery\b", "some"),
    (r"\bexact\b", "approximate"),
    (r"\bimmediate\b", "eventual"),
)

OPTION_IDS = ("OPT_1", "OPT_2", "OPT_3", "OPT_4")


@dataclass(frozen=True)
class ManifestDoc:
    doc_id: str
    path: str
    required_for_certification: bool


@dataclass(frozen=True)
class Claim:
    doc_id: str
    path: str
    anchor: str
    line_no: int
    text: str


def _slugify(heading: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", heading.lower()).strip("-")
    return slug or "section"


def _load_manifest_docs(required_only: bool) -> list[ManifestDoc]:
    if not MANIFEST_PATH.exists():
        raise FileNotFoundError(f"Manifest not found: {MANIFEST_PATH}")

    docs: list[ManifestDoc] = []
    current: dict[str, object] | None = None
    for raw in MANIFEST_PATH.read_text(encoding="utf-8").splitlines():
        if raw.startswith("- doc_id: "):
            if current is not None:
                docs.append(
                    ManifestDoc(
                        doc_id=str(current.get("doc_id", "")),
                        path=str(current.get("path", "")),
                        required_for_certification=bool(
                            current.get("required_for_certification", False)
                        ),
                    )
                )
            current = {"doc_id": raw.split(": ", 1)[1].strip()}
            continue
        if current is None or not raw.startswith("  "):
            continue
        stripped = raw.strip()
        if ": " not in stripped:
            continue
        key, value = stripped.split(": ", 1)
        if key == "required_for_certification":
            current[key] = value.strip().lower() == "true"
        else:
            current[key] = value.strip()
    if current is not None:
        docs.append(
            ManifestDoc(
                doc_id=str(current.get("doc_id", "")),
                path=str(current.get("path", "")),
                required_for_certification=bool(current.get("required_for_certification", False)),
            )
        )

    filtered = [doc for doc in docs if doc.path]
    if required_only:
        filtered = [doc for doc in filtered if doc.required_for_certification]
    return filtered


def _count_existing_questions() -> int:
    total = 0
    tests_root = SKILL_CHECK_ROOT / "tests"
    if not tests_root.exists():
        return 0
    for test_file in tests_root.rglob("*.test.md"):
        for line in test_file.read_text(encoding="utf-8").splitlines():
            if QUESTION_HEADER_RE.match(line):
                total += 1
    return total


def _normalize_claim(line: str) -> str:
    value = line.strip()
    value = re.sub(r"^[-*]\s+", "", value)
    value = re.sub(r"^[0-9]+\)\s+", "", value)
    value = re.sub(r"\s+", " ", value).strip()
    return value.rstrip(".")


def _is_candidate_claim(line: str) -> bool:
    if not line.strip():
        return False
    normalized = line.lower()
    if len(normalized) < 35:
        return False
    return any(keyword in normalized for keyword in NORMATIVE_KEYWORDS)


def _extract_claims(doc: ManifestDoc) -> list[Claim]:
    path = CONTEXT_ROOT / doc.path
    if not path.exists():
        return []

    lines = path.read_text(encoding="utf-8").splitlines()
    claims: list[Claim] = []
    current_anchor = "overview"

    for idx, raw in enumerate(lines, start=1):
        stripped = raw.strip()
        if stripped.startswith("#"):
            current_anchor = _slugify(stripped.lstrip("#").strip())
            continue
        if not _is_candidate_claim(raw):
            continue
        text = _normalize_claim(raw)
        if len(text) < 30:
            continue
        claims.append(
            Claim(
                doc_id=doc.doc_id,
                path=doc.path,
                anchor=current_anchor,
                line_no=idx,
                text=text,
            )
        )

    if claims:
        return claims

    # Fallback: if no normative lines are found, use non-empty prose lines.
    for idx, raw in enumerate(lines, start=1):
        stripped = raw.strip()
        if stripped.startswith("#"):
            current_anchor = _slugify(stripped.lstrip("#").strip())
            continue
        if len(stripped) < 35:
            continue
        claims.append(
            Claim(
                doc_id=doc.doc_id,
                path=doc.path,
                anchor=current_anchor,
                line_no=idx,
                text=_normalize_claim(stripped),
            )
        )
        if len(claims) >= 8:
            break
    return claims


def _swap_first(text: str, swaps: Iterable[tuple[str, str]]) -> str:
    for pattern, replacement in swaps:
        if re.search(pattern, text, flags=re.IGNORECASE):
            return re.sub(pattern, replacement, text, count=1, flags=re.IGNORECASE)
    return text


def _make_modality_lie(truth: str) -> str:
    candidate = _swap_first(truth, MODALITY_SWAPS)
    if candidate != truth:
        return candidate
    return f"{truth} only when optional approval is skipped"


def _make_sequence_lie(truth: str) -> str:
    candidate = _swap_first(truth, SEQUENCE_SWAPS)
    if candidate != truth:
        return candidate
    return f"After finalization, {truth[0].lower() + truth[1:]}"


def _make_scope_lie(truth: str) -> str:
    candidate = _swap_first(truth, SCOPE_SWAPS)
    if candidate != truth:
        return candidate
    return f"{truth} for a partial subset only"


def _rotate_list(items: list[str], positions: int) -> list[str]:
    if not items:
        return items
    shift = positions % len(items)
    return items[shift:] + items[:shift]


def _hash_token(value: str, length: int = 12) -> str:
    return hashlib.sha1(value.encode("utf-8")).hexdigest()[:length].upper()


def _build_question(claim: Claim, variant_index: int) -> tuple[dict[str, object], dict[str, object]]:
    truth = claim.text
    lie_a = _make_modality_lie(truth)
    lie_b = _make_sequence_lie(truth)
    lie_c = _make_scope_lie(truth)

    options = [truth, lie_a, lie_b, lie_c]
    options = _rotate_list(options, variant_index)

    prompt_template = PROMPT_TEMPLATES[variant_index % len(PROMPT_TEMPLATES)]
    question_id_seed = (
        f"{claim.doc_id}|{claim.path}|{claim.anchor}|{claim.line_no}|"
        f"{variant_index}|{truth}"
    )
    question_id = f"{claim.doc_id}::H{_hash_token(question_id_seed)}"

    option_rows: list[dict[str, str]] = []
    truth_option_id = ""
    for idx, text in enumerate(options):
        option_id = OPTION_IDS[idx]
        option_rows.append({"option_id": option_id, "text": text})
        if text == truth and not truth_option_id:
            truth_option_id = option_id

    public_row: dict[str, object] = {
        "question_id": question_id,
        "doc_id": claim.doc_id,
        "source_path": claim.path,
        "source_anchor": claim.anchor,
        "source_line": claim.line_no,
        "difficulty": "hard",
        "variant_index": variant_index,
        "prompt": (
            f"{prompt_template} Source: `{claim.path}#{claim.anchor}`. "
            "Choose one option."
        ),
        "options": option_rows,
    }
    sealed_row: dict[str, object] = {
        "question_id": question_id,
        "truth_option_id": truth_option_id,
        "truth_sha256": hashlib.sha256(truth.encode("utf-8")).hexdigest(),
    }
    return public_row, sealed_row


def _ensure_dirs() -> None:
    (SKILL_CHECK_ROOT / "question_pool").mkdir(parents=True, exist_ok=True)
    (SKILL_CHECK_ROOT / ".sealed").mkdir(parents=True, exist_ok=True)


def _write_jsonl(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=True) + "\n")


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build hard MCQ question pool.")
    parser.add_argument(
        "--multiplier",
        type=int,
        default=10,
        help="Target pool size as N x current question count (default: 10).",
    )
    parser.add_argument(
        "--required-only",
        action="store_true",
        help="Use required-for-certification docs only.",
    )
    parser.add_argument(
        "--min-total",
        type=int,
        default=0,
        help="Minimum absolute question count regardless of multiplier.",
    )
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    if args.multiplier < 1:
        raise ValueError("--multiplier must be >= 1")

    docs = _load_manifest_docs(required_only=args.required_only)
    if not docs:
        raise RuntimeError("No docs available from manifest.")

    claims: list[Claim] = []
    for doc in docs:
        claims.extend(_extract_claims(doc))
    if not claims:
        raise RuntimeError("No claims extracted from source docs.")

    existing_total = _count_existing_questions()
    loc_based_min = 0
    for doc in docs:
        loc = len((CONTEXT_ROOT / doc.path).read_text(encoding="utf-8").splitlines())
        loc_based_min += max(1, (loc + 99) // 100)

    target_total = max(existing_total * args.multiplier, loc_based_min * args.multiplier, args.min_total)

    questions: list[dict[str, object]] = []
    sealed_rows: list[dict[str, object]] = []
    seen_ids: set[str] = set()
    per_doc_counts: dict[str, int] = {}

    variant = 0
    while len(questions) < target_total:
        made_progress = False
        for claim in claims:
            public_row, sealed_row = _build_question(claim, variant)
            question_id = str(public_row["question_id"])
            if question_id in seen_ids:
                continue
            seen_ids.add(question_id)
            questions.append(public_row)
            sealed_rows.append(sealed_row)
            per_doc_counts[claim.doc_id] = per_doc_counts.get(claim.doc_id, 0) + 1
            made_progress = True
            if len(questions) >= target_total:
                break
        if not made_progress:
            raise RuntimeError("Unable to generate enough unique questions.")
        variant += 1

    _ensure_dirs()
    _write_jsonl(PUBLIC_POOL_PATH, questions)
    _write_jsonl(SEALED_KEY_PATH, sealed_rows)

    meta = {
        "pool_version": 1,
        "required_only": bool(args.required_only),
        "multiplier": args.multiplier,
        "existing_question_count": existing_total,
        "loc_based_minimum": loc_based_min,
        "target_total": target_total,
        "generated_total": len(questions),
        "doc_count": len(docs),
        "claims_extracted": len(claims),
        "max_variant_index": variant,
        "public_pool_path": str(PUBLIC_POOL_PATH.relative_to(CONTEXT_ROOT)).replace("\\", "/"),
        "sealed_key_path": str(SEALED_KEY_PATH.relative_to(CONTEXT_ROOT)).replace("\\", "/"),
        "per_doc_counts": per_doc_counts,
    }
    POOL_META_PATH.write_text(json.dumps(meta, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")

    print(f"generated_total={len(questions)}")
    print(f"target_total={target_total}")
    print(f"existing_question_count={existing_total}")
    print(f"doc_count={len(docs)}")
    print(f"claims_extracted={len(claims)}")
    print(f"public_pool={PUBLIC_POOL_PATH}")
    print(f"sealed_keys={SEALED_KEY_PATH}")


if __name__ == "__main__":
    main()
