"""
Build deterministic, indexed whole-repository text bundles for LLM tooling.
The generated files are derived repository assets. ContextCompass remains the
authoritative navigation, policy, and work-state system; these bundles exist for
bulk export and tools that cannot navigate the checkout directly.
"""
import argparse
import hashlib
import json
import os
import pathlib
import subprocess
import sys
from typing import Dict, List, Optional, Sequence, Tuple, cast
class LLMSupportPolicy:
    """
    Hold the immutable schema, corpus, eligibility, and output conventions.
    The policy is centralized so classification and manifest invalidation use
    one vocabulary. Class attributes are never mutated at runtime.
    """
    SCHEMA_VERSION: str = "1.0.0"
    POLICY_VERSION: str = "1.0.0"
    CORPORA: Tuple[str, ...] = ("src", "tests", "other")
    SOURCE_EXTENSIONS: frozenset[str] = frozenset({".py", ".pyi"})
    TEST_EXTENSIONS: frozenset[str] = frozenset(
        {
            ".py",
            ".pyi",
            ".json",
            ".md",
            ".txt",
            ".toml",
            ".yaml",
            ".yml",
            ".ini",
            ".cfg",
            ".gitignore",
        }
    )
    OTHER_EXTENSIONS: frozenset[str] = frozenset(
        {
            ".py",
            ".pyi",
            ".json",
            ".md",
            ".txt",
            ".toml",
            ".yaml",
            ".yml",
            ".mmd",
            ".ini",
            ".cfg",
            ".gitignore",
            ".gitattributes",
        }
    )
    OTHER_EXTENSIONLESS: frozenset[str] = frozenset(
        {"LICENSE", "NOTICE", "context_compass/LICENSE", "context_compass/NOTICE"}
    )
    RENDERED_EXTENSIONS: frozenset[str] = frozenset({".svg", ".gitkeep"})
    SEPARATOR: str = "=" * 80
    @classmethod
    def classify(cls, repository_path: str) -> Tuple[Optional[str], str]:
        """
        Classify one tracked path into one corpus or an exclusion reason.
        Args:
            repository_path: POSIX-style path relative to the repository root.
        Returns:
            Tuple containing the corpus name or None, plus a stable reason.
        """
        path = repository_path.replace("\\", "/")
        suffix = pathlib.PurePosixPath(path).suffix.lower()
        name = pathlib.PurePosixPath(path).name
        parts = pathlib.PurePosixPath(path).parts
        if path.startswith("llm_support/"):
            return None, "self_output"
        if path.startswith("src/"):
            if suffix not in cls.SOURCE_EXTENSIONS:
                return None, "src_non_code"
            if (
                    path.startswith("src/melder/_build_assets/")
                    and ("manifest" in parts or "payloads" in parts)
            ):
                return None, "generated_src_asset"
            return "src", "included"
        if path.startswith("tests/"):
            if suffix in cls.TEST_EXTENSIONS or name == ".gitignore":
                return "tests", "included"
            return None, "tests_non_text"
        if path.startswith("context_compass/"):
            return None, "context_compass_direct"
        if suffix in cls.RENDERED_EXTENSIONS or name == ".gitkeep":
            return None, "rendered_or_placeholder_asset"
        if (
                suffix in cls.OTHER_EXTENSIONS
                or name in {".gitignore", ".gitattributes"}
                or path in cls.OTHER_EXTENSIONLESS
        ):
            return "other", "included"
        return None, "other_non_text"
    @classmethod
    def bundle_name(cls, corpus: str) -> str:
        """Return the committed bundle filename for one corpus."""
        cls.require_corpus(corpus)
        return f"llm_full_{corpus}.txt"
    @classmethod
    def index_name(cls, corpus: str) -> str:
        """Return the committed Markdown index filename for one corpus."""
        cls.require_corpus(corpus)
        return f"llm_full_{corpus}_index.md"
    @classmethod
    def require_corpus(cls, corpus: str) -> None:
        """Raise ValueError when a caller supplies an unknown corpus name."""
        if corpus not in cls.CORPORA:
            raise ValueError(
                f"Unknown corpus {corpus!r}; expected one of {', '.join(cls.CORPORA)}."
            )
class SourceFile:
    """
    Carry one decoded repository file and its deterministic content metadata.
    The object owns value data only: repository path, encoding label, normalized
    text, and hashes. It owns no file handle or external lifecycle.
    """
    __slots__ = (
        "path",
        "source_encoding",
        "content",
        "content_bytes",
        "content_lines",
        "content_sha256",
    )
    def __init__(self, path: str, source_encoding: str, content: str) -> None:
        """
        Initialize one normalized source record.
        Args:
            path: Repository-relative POSIX path.
            source_encoding: Detected encoding of the source bytes.
            content: Complete decoded text with LF-only line endings.
        """
        encoded = content.encode("utf-8")
        self.path: str = path
        self.source_encoding: str = source_encoding
        self.content: str = content
        self.content_bytes: int = len(encoded)
        self.content_lines: int = count_text_lines(content)
        self.content_sha256: str = hashlib.sha256(encoded).hexdigest()
    def manifest_entry(self) -> Dict[str, object]:
        """Return the deterministic JSON-compatible per-file manifest record."""
        return {
            "content_bytes": self.content_bytes,
            "content_lines": self.content_lines,
            "content_sha256": self.content_sha256,
            "source_encoding": self.source_encoding,
        }
def count_text_lines(text: str) -> int:
    """
    Count physical text lines without treating a terminal newline as a new line.
    Args:
        text: Decoded text using LF line endings.
    Returns:
        Number of physical lines represented by the text.
    """
    if not text:
        return 0
    return len(text.split("\n")) - int(text.endswith("\n"))
def normalize_line_endings(text: str) -> str:
    """
    Normalize CRLF and lone CR to LF while preserving every other character.
    Args:
        text: Decoded source text.
    Returns:
        Text with LF-only physical line endings.
    """
    return text.replace("\r\n", "\n").replace("\r", "\n")
def decode_source(raw: bytes, path: str) -> Tuple[str, str]:
    """
    Decode one eligible file without data-dropping error recovery.
    Args:
        raw: Exact working-tree bytes.
        path: Repository path used in teach-grade failures.
    Returns:
        Tuple of detected encoding label and LF-normalized text.
    Raises:
        ValueError: When the bytes are binary or a recognized encoding is malformed.
    """
    try:
        if raw.startswith(b"\xef\xbb\xbf"):
            return "utf-8-bom", normalize_line_endings(raw[3:].decode("utf-8"))
        if raw.startswith(b"\xff\xfe"):
            return "utf-16-le-bom", normalize_line_endings(raw[2:].decode("utf-16-le"))
        if raw.startswith(b"\xfe\xff"):
            return "utf-16-be-bom", normalize_line_endings(raw[2:].decode("utf-16-be"))
        if b"\x00" in raw:
            raise ValueError(
                f"Eligible file {path} contains NUL bytes without a UTF-16 BOM."
            )
        try:
            return "utf-8", normalize_line_endings(raw.decode("utf-8"))
        except UnicodeDecodeError:
            decoded = raw.decode("utf-8", errors="surrogateescape")
            characters: List[str] = []
            for character in decoded:
                codepoint = ord(character)
                if 0xDC80 <= codepoint <= 0xDCFF:
                    escaped = bytes((codepoint - 0xDC00,))
                    try:
                        character = escaped.decode("cp1252")
                    except UnicodeDecodeError:
                        character = escaped.decode("latin-1")
                characters.append(character)
            return "mixed-utf8-cp1252", normalize_line_endings("".join(characters))
    except UnicodeDecodeError as error:
        raise ValueError(
            f"Eligible file {path} is malformed for its detected encoding: {error}."
        ) from error
def sha256_bytes(payload: bytes) -> str:
    """Return a hexadecimal SHA256 digest for one byte payload."""
    return hashlib.sha256(payload).hexdigest()
def render_json(payload: Dict[str, object]) -> str:
    """Render deterministic UTF-8/LF JSON with a terminal newline."""
    return json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
def atomic_write_if_changed(path: pathlib.Path, content: str) -> bool:
    """
    Atomically replace one UTF-8/LF text file only when bytes differ.
    Args:
        path: Target file.
        content: Complete text to write.
    Returns:
        True when the target changed, otherwise False.
    """
    encoded = content.encode("utf-8")
    if path.exists() and path.read_bytes() == encoded:
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    try:
        temporary.write_bytes(encoded)
        os.replace(temporary, path)
    finally:
        if temporary.exists():
            temporary.unlink()
    return True
class LLMSupportBuilder:
    """
    Discover, build, check, list, and slice the repository LLM support assets.
    The builder owns no runtime resources. Every command reads a finite working
    tree, writes through atomic temporary files, and returns with no open handles.
    """
    __slots__ = ("repository_root", "output_root", "include_untracked")
    def __init__(
            self,
            repository_root: pathlib.Path,
            *,
            include_untracked: bool = False,
    ) -> None:
        """
        Initialize one repository-bound builder.
        Args:
            repository_root: Checkout root containing .git and llm_support.
            include_untracked: Include nonignored untracked paths for an explicit
                local bootstrap build. CI and normal checks leave this False.
        Raises:
            ValueError: When repository_root is not a Git working tree.
        """
        root = repository_root.resolve()
        if not (root / ".git").exists():
            raise ValueError(f"Not a Git working tree: {root}")
        self.repository_root: pathlib.Path = root
        self.output_root: pathlib.Path = root / "llm_support"
        self.include_untracked: bool = include_untracked
    def _run_git(self, arguments: Sequence[str]) -> bytes:
        """
        Execute one read-only Git discovery command.
        Args:
            arguments: Git arguments following the executable name.
        Returns:
            Captured stdout bytes.
        Raises:
            RuntimeError: When Git exits nonzero.
        """
        result = subprocess.run(
            ["git", "-C", str(self.repository_root), *arguments],
            check=False,
            capture_output=True,
        )
        if result.returncode != 0:
            detail = result.stderr.decode("utf-8", errors="replace").strip()
            raise RuntimeError(f"Git discovery failed: {detail}")
        return result.stdout
    def _tracked_entries(self) -> List[Tuple[str, str]]:
        """
        Return sorted Git mode/path pairs, optionally adding explicit untracked paths.
        Returns:
            Stable list of regular tracked or requested bootstrap paths.
        """
        records: Dict[str, str] = {}
        raw = self._run_git(["ls-files", "--cached", "--stage", "-z"])
        for record in raw.split(b"\x00"):
            if not record:
                continue
            metadata, path_bytes = record.split(b"\t", 1)
            mode, _object_id, stage = metadata.decode("ascii").split()
            path = path_bytes.decode("utf-8")
            if stage != "0":
                raise RuntimeError(f"Unmerged Git index entry for {path}; resolve it first.")
            records[path] = mode
        if self.include_untracked:
            extra = self._run_git(["ls-files", "--others", "--exclude-standard", "-z"])
            for path_bytes in extra.split(b"\x00"):
                if path_bytes:
                    records.setdefault(path_bytes.decode("utf-8"), "100644")
        return [(records[path], path) for path in sorted(records)]
    def discover(
            self,
    ) -> Tuple[Dict[str, List[SourceFile]], Dict[str, List[str]]]:
        """
        Discover and decode all eligible corpus inputs.
        Returns:
            Tuple of corpus records and exclusion paths grouped by reason.
        Raises:
            RuntimeError: For unsupported Git modes, missing files, or escaping paths.
            ValueError: For malformed eligible text.
        """
        corpora: Dict[str, List[SourceFile]] = {
            corpus: [] for corpus in LLMSupportPolicy.CORPORA
        }
        excluded: Dict[str, List[str]] = {}
        for mode, path in self._tracked_entries():
            corpus, reason = LLMSupportPolicy.classify(path)
            if corpus is None:
                excluded.setdefault(reason, []).append(path)
                continue
            if mode != "100644":
                raise RuntimeError(f"Eligible path {path} has unsupported Git mode {mode}.")
            absolute = (self.repository_root / pathlib.PurePosixPath(path)).resolve()
            try:
                absolute.relative_to(self.repository_root)
            except ValueError as error:
                raise RuntimeError(f"Eligible path escapes repository root: {path}") from error
            if not absolute.is_file():
                if self.include_untracked:
                    excluded.setdefault("working_tree_deleted", []).append(path)
                    continue
                raise RuntimeError(
                    f"Eligible tracked path is missing: {path}. Stage deletions first."
                )
            source_encoding, content = decode_source(absolute.read_bytes(), path)
            corpora[corpus].append(SourceFile(path, source_encoding, content))
        return corpora, excluded
    def generator_sha256(self) -> str:
        """
        Return a checkout-EOL-independent fingerprint of this generator.
        Returns:
            SHA256 over LF-canonical builder bytes.
        """
        raw = pathlib.Path(__file__).resolve().read_bytes()
        canonical = raw.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
        return sha256_bytes(canonical)
    def source_state(
            self,
            corpus: str,
            files: Sequence[SourceFile],
    ) -> Dict[str, object]:
        """
        Build deterministic per-file state and one aggregate corpus fingerprint.
        Args:
            corpus: Corpus name.
            files: Sorted corpus source records.
        Returns:
            JSON-compatible source-state mapping.
        """
        LLMSupportPolicy.require_corpus(corpus)
        digest = hashlib.sha256()
        digest.update(LLMSupportPolicy.POLICY_VERSION.encode("ascii"))
        digest.update(b"\x00")
        digest.update(corpus.encode("ascii"))
        file_map: Dict[str, object] = {}
        total_bytes = 0
        total_lines = 0
        for source in files:
            entry = source.manifest_entry()
            file_map[source.path] = entry
            digest.update(source.path.encode("utf-8"))
            digest.update(b"\x00")
            digest.update(source.source_encoding.encode("ascii"))
            digest.update(b"\x00")
            digest.update(source.content_sha256.encode("ascii"))
            digest.update(b"\x00")
            digest.update(str(source.content_bytes).encode("ascii"))
            digest.update(b"\x00")
            digest.update(str(source.content_lines).encode("ascii"))
            digest.update(b"\x00")
            total_bytes += source.content_bytes
            total_lines += source.content_lines
        return {
            "content_bytes": total_bytes,
            "content_lines": total_lines,
            "file_count": len(files),
            "files": file_map,
            "source_fingerprint": digest.hexdigest(),
        }
    def render_bundle(
            self,
            corpus: str,
            files: Sequence[SourceFile],
            source_fingerprint: str,
    ) -> Tuple[str, List[Dict[str, object]]]:
        """
        Render one complete corpus bundle and collect exact file line ranges.
        Args:
            corpus: Corpus name.
            files: Sorted source records.
            source_fingerprint: Aggregate input fingerprint.
        Returns:
            Tuple of bundle text and line-range records.
        """
        pieces: List[str] = []
        ranges: List[Dict[str, object]] = []
        next_line = 1
        def append(text: str) -> None:
            """Append newline-terminated text and advance the next line number."""
            nonlocal next_line
            pieces.append(text)
            next_line += text.count("\n")
        append("GENERATED REPOSITORY ASSET - DO NOT EDIT MANUALLY.\n")
        append("AUTHORITY: Use context_compass/AGENTS.MD and ContextCompass first.\n")
        append(f"CORPUS: {corpus}\n")
        append(f"SOURCE FINGERPRINT: {source_fingerprint}\n")
        append(f"FILE COUNT: {len(files)}\n\n")
        separator = f"{LLMSupportPolicy.SEPARATOR}\n"
        for source in files:
            entry_start = next_line
            append(separator)
            append(f"BEGIN FILE: {source.path}\n")
            append(f"CONTENT SHA256: {source.content_sha256}\n")
            append(f"SOURCE ENCODING: {source.source_encoding}\n")
            append(separator)
            content_start: Optional[int] = None
            content_end: Optional[int] = None
            if source.content_lines:
                content_start = next_line
                content_end = content_start + source.content_lines - 1
                content = source.content
                append(content if content.endswith("\n") else f"{content}\n")
            append(separator)
            append(f"END FILE: {source.path}\n")
            append(separator)
            entry_end = next_line - 1
            ranges.append(
                {
                    "content_end": content_end,
                    "content_start": content_start,
                    "entry_end": entry_end,
                    "entry_start": entry_start,
                    "source": source,
                }
            )
        return "".join(pieces), ranges
    def render_index(
            self,
            corpus: str,
            source_state: Dict[str, object],
            bundle_text: str,
            ranges: Sequence[Dict[str, object]],
    ) -> str:
        """
        Render one Markdown line-range index with a bundle staleness proof.
        Args:
            corpus: Corpus name.
            source_state: Aggregate source metadata.
            bundle_text: Complete bundle.
            ranges: Per-file bundle ranges.
        Returns:
            Complete Markdown index.
        """
        bundle_bytes = bundle_text.encode("utf-8")
        lines = [
            f"# llm_full_{corpus}_index",
            "",
            "Generated line ranges into the matching LLM support bundle.",
            "Line numbers are 1-based and inclusive.",
            "",
            "## Staleness proof",
            "",
            "| field | value |",
            "| --- | --- |",
            f"| bundle | {LLMSupportPolicy.bundle_name(corpus)} |",
            f"| schema_version | {LLMSupportPolicy.SCHEMA_VERSION} |",
            f"| generator_sha256 | {self.generator_sha256()} |",
            f"| source_fingerprint | {source_state['source_fingerprint']} |",
            f"| bundle_sha256 | {sha256_bytes(bundle_bytes)} |",
            f"| bundle_line_count | {count_text_lines(bundle_text)} |",
            "| bundle_line_ending | lf |",
            f"| files | {len(ranges)} |",
            "",
            "## Files",
            "",
            "| entry lines | content lines | content bytes | source encoding | content sha256 | path |",
            "| --- | --- | ---: | --- | --- | --- |",
        ]
        for item in ranges:
            source = cast(SourceFile, item["source"])
            content_range = "-"
            if item["content_start"] is not None:
                content_range = f"{item['content_start']}-{item['content_end']}"
            path = source.path.replace("|", "\\|")
            lines.append(
                f"| {item['entry_start']}-{item['entry_end']} "
                f"| {content_range} | {source.content_bytes} "
                f"| {source.source_encoding} | {source.content_sha256} | {path} |"
            )
        lines.append("")
        return "\n".join(lines)
    def _output_metadata(self, path: pathlib.Path) -> Dict[str, object]:
        """Return deterministic hash, size, and line metadata for one output."""
        raw = path.read_bytes()
        text = raw.decode("utf-8")
        return {
            "bytes": len(raw),
            "lines": count_text_lines(text),
            "path": path.relative_to(self.repository_root).as_posix(),
            "sha256": sha256_bytes(raw),
        }
    def _load_manifest(self) -> Optional[Dict[str, object]]:
        """
        Load and type-check the shared manifest when it exists.
        Returns:
            Manifest mapping or None for the first build.
        Raises:
            ValueError: When JSON or the root shape is invalid.
        """
        path = self.output_root / "manifest.json"
        if not path.exists():
            return None
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as error:
            raise ValueError(f"Cannot read valid manifest {path}: {error}") from error
        if not isinstance(payload, dict):
            raise ValueError(f"Manifest root must be an object: {path}")
        return cast(Dict[str, object], payload)
    def _manifest_compatible(self, manifest: Optional[Dict[str, object]]) -> bool:
        """Return whether one manifest uses the current schema, policy, and generator."""
        if manifest is None:
            return False
        return (
            manifest.get("schema_version") == LLMSupportPolicy.SCHEMA_VERSION
            and manifest.get("policy_version") == LLMSupportPolicy.POLICY_VERSION
            and manifest.get("generator_sha256") == self.generator_sha256()
            and isinstance(manifest.get("corpora"), dict)
        )
    def _corpus_manifest(
            self,
            manifest: Optional[Dict[str, object]],
            corpus: str,
    ) -> Optional[Dict[str, object]]:
        """Return one corpus mapping from a structurally valid manifest."""
        if manifest is None:
            return None
        corpora = manifest.get("corpora")
        if not isinstance(corpora, dict):
            return None
        value = corpora.get(corpus)
        return cast(Dict[str, object], value) if isinstance(value, dict) else None
    def _metadata_matches(self, metadata: object, expected_path: pathlib.Path) -> bool:
        """Return whether one output file matches its manifest metadata."""
        if not isinstance(metadata, dict) or not expected_path.is_file():
            return False
        raw = expected_path.read_bytes()
        return (
            metadata.get("path")
            == expected_path.relative_to(self.repository_root).as_posix()
            and metadata.get("bytes") == len(raw)
            and metadata.get("sha256") == sha256_bytes(raw)
            and metadata.get("lines")
            == count_text_lines(raw.decode("utf-8"))
        )
    def _parse_index(self, corpus: str) -> List[Dict[str, object]]:
        """
        Parse generated index rows for validation and slicing.
        Args:
            corpus: Corpus whose index should be parsed.
        Returns:
            Parsed line ranges and paths.
        Raises:
            ValueError: When a generated row is malformed.
        """
        path = self.output_root / LLMSupportPolicy.index_name(corpus)
        records: List[Dict[str, object]] = []
        in_files = False
        for line in path.read_text(encoding="utf-8").split("\n"):
            if line == "## Files":
                in_files = True
                continue
            if not in_files or not line.startswith("| ") or line.startswith("| ---"):
                continue
            parts = [part.strip() for part in line.split("|")[1:-1]]
            if parts[0] == "entry lines":
                continue
            if len(parts) != 6:
                raise ValueError(f"Malformed index row in {path}: {line}")
            entry_start, entry_end = parse_range(parts[0], path)
            content_start: Optional[int] = None
            content_end: Optional[int] = None
            if parts[1] != "-":
                content_start, content_end = parse_range(parts[1], path)
            records.append(
                {
                    "content_end": content_end,
                    "content_start": content_start,
                    "entry_end": entry_end,
                    "entry_start": entry_start,
                    "path": parts[5].replace("\\|", "|"),
                }
            )
        return records
    def _validate_index(self, corpus: str, expected_files: int) -> None:
        """
        Validate index ranges against bundle markers and bounds.
        Args:
            corpus: Corpus to validate.
            expected_files: Manifest file count.
        Raises:
            ValueError: On count, marker, ordering, or bounds drift.
        """
        bundle_path = self.output_root / LLMSupportPolicy.bundle_name(corpus)
        bundle_lines = bundle_path.read_text(encoding="utf-8").split("\n")[:-1]
        records = self._parse_index(corpus)
        if len(records) != expected_files:
            raise ValueError(
                f"{corpus} index has {len(records)} rows; expected {expected_files}."
            )
        previous_end = 0
        for record in records:
            start = cast(int, record["entry_start"])
            end = cast(int, record["entry_end"])
            path = cast(str, record["path"])
            if not (previous_end < start <= end <= len(bundle_lines)):
                raise ValueError(f"{corpus} index range is invalid for {path}: {start}-{end}.")
            if bundle_lines[start] != f"BEGIN FILE: {path}":
                raise ValueError(f"{corpus} index start marker mismatch for {path}.")
            if bundle_lines[end - 2] != f"END FILE: {path}":
                raise ValueError(f"{corpus} index end marker mismatch for {path}.")
            content_start = record["content_start"]
            content_end = record["content_end"]
            if content_start is not None and not (
                    start < cast(int, content_start)
                    <= cast(int, content_end)
                    < end
            ):
                raise ValueError(f"{corpus} content range is invalid for {path}.")
            previous_end = end
    def _corpus_current(
            self,
            corpus: str,
            source_state: Dict[str, object],
            old: Optional[Dict[str, object]],
    ) -> Tuple[bool, str]:
        """Return current/stale state and one diagnostic reason for a corpus."""
        if old is None:
            return False, "manifest entry missing"
        if old.get("source_fingerprint") != source_state["source_fingerprint"]:
            return False, "source fingerprint moved"
        bundle_path = self.output_root / LLMSupportPolicy.bundle_name(corpus)
        index_path = self.output_root / LLMSupportPolicy.index_name(corpus)
        if not self._metadata_matches(old.get("bundle"), bundle_path):
            return False, "bundle missing or modified"
        if not self._metadata_matches(old.get("index"), index_path):
            return False, "index missing or modified"
        try:
            self._validate_index(corpus, cast(int, old["file_count"]))
        except (KeyError, TypeError, ValueError, OSError, UnicodeDecodeError) as error:
            return False, f"index validation failed: {error}"
        return True, "fingerprint and output proofs match"
    def check(self, selected: Sequence[str]) -> int:
        """
        Verify selected committed corpora without writing.
        Args:
            selected: Corpus names to check.
        Returns:
            Zero when every selected corpus is current, otherwise one.
        """
        corpora, _excluded = self.discover()
        manifest = self._load_manifest()
        compatible = self._manifest_compatible(manifest)
        failed = False
        for corpus in selected:
            state = self.source_state(corpus, corpora[corpus])
            old = self._corpus_manifest(manifest, corpus) if compatible else None
            current, reason = self._corpus_current(corpus, state, old)
            if current:
                print(f"OK     {corpus:<5} {reason}")
            else:
                print(f"STALE  {corpus:<5} {reason}", file=sys.stderr)
                failed = True
        if failed:
            print(
                "\nRegenerate locally with:\n    python llm_support/_builder.py",
                file=sys.stderr,
            )
            return 1
        return 0
    def build(self, selected: Sequence[str]) -> int:
        """
        Regenerate only stale selected corpora and write the manifest last.
        Args:
            selected: Corpus names eligible for rebuilding.
        Returns:
            Zero on success.
        Raises:
            ValueError: When a partial build follows a schema/generator change.
        """
        corpora, _excluded = self.discover()
        manifest = self._load_manifest()
        compatible = self._manifest_compatible(manifest)
        if manifest is not None and not compatible and set(selected) != set(
                LLMSupportPolicy.CORPORA
        ):
            raise ValueError(
                "Schema, policy, or generator changed; rebuild all corpora, not a subset."
            )
        old_corpora: Dict[str, object] = {}
        if compatible and manifest is not None:
            old_corpora = cast(Dict[str, object], manifest["corpora"]).copy()
        new_corpora = old_corpora
        for corpus in selected:
            files = corpora[corpus]
            state = self.source_state(corpus, files)
            old = self._corpus_manifest(manifest, corpus) if compatible else None
            current, reason = self._corpus_current(corpus, state, old)
            if current:
                print(f"UNCHANGED {corpus:<5} {reason}")
                continue
            bundle_text, ranges = self.render_bundle(
                corpus,
                files,
                cast(str, state["source_fingerprint"]),
            )
            index_text = self.render_index(corpus, state, bundle_text, ranges)
            bundle_path = self.output_root / LLMSupportPolicy.bundle_name(corpus)
            index_path = self.output_root / LLMSupportPolicy.index_name(corpus)
            atomic_write_if_changed(bundle_path, bundle_text)
            atomic_write_if_changed(index_path, index_text)
            entry = state.copy()
            entry["bundle"] = self._output_metadata(bundle_path)
            entry["index"] = self._output_metadata(index_path)
            new_corpora[corpus] = entry
            self._validate_index(corpus, len(files))
            print(f"WROTE     {corpus:<5} {len(files)} files ({reason})")
        for corpus in LLMSupportPolicy.CORPORA:
            if corpus not in new_corpora:
                raise ValueError(
                    f"Manifest would be incomplete: corpus {corpus} was not built."
                )
        new_manifest: Dict[str, object] = {
            "corpora": new_corpora,
            "generator_sha256": self.generator_sha256(),
            "policy_version": LLMSupportPolicy.POLICY_VERSION,
            "schema_version": LLMSupportPolicy.SCHEMA_VERSION,
        }
        wrote = atomic_write_if_changed(
            self.output_root / "manifest.json",
            render_json(new_manifest),
        )
        print(f"{'WROTE' if wrote else 'UNCHANGED'} manifest.json")
        return 0
    def list_inputs(self) -> int:
        """Print corpus and exclusion counts without writing outputs."""
        corpora, excluded = self.discover()
        for corpus in LLMSupportPolicy.CORPORA:
            files = corpora[corpus]
            print(
                f"{corpus:<5} files={len(files)} "
                f"bytes={sum(source.content_bytes for source in files)} "
                f"lines={sum(source.content_lines for source in files)}"
            )
        for reason in sorted(excluded):
            print(f"exclude {reason:<32} files={len(excluded[reason])}")
        return 0
    def slice_file(self, corpus: str, repository_path: str) -> int:
        """
        Verify one corpus and print exactly one indexed file's normalized content.
        Args:
            corpus: Corpus name.
            repository_path: Exact repository-relative path.
        Returns:
            Zero on success or one when the corpus/path is unavailable.
        """
        if self.check([corpus]) != 0:
            return 1
        normalized_path = repository_path.replace("\\", "/")
        record = next(
            (
                item
                for item in self._parse_index(corpus)
                if item["path"] == normalized_path
            ),
            None,
        )
        if record is None:
            print(f"No indexed {corpus} file named {normalized_path}.", file=sys.stderr)
            return 1
        if record["content_start"] is None:
            return 0
        bundle_path = self.output_root / LLMSupportPolicy.bundle_name(corpus)
        lines = bundle_path.read_text(encoding="utf-8").split("\n")[:-1]
        start = cast(int, record["content_start"])
        end = cast(int, record["content_end"])
        print("\n".join(lines[start - 1:end]))
        return 0
def parse_range(value: str, index_path: pathlib.Path) -> Tuple[int, int]:
    """
    Parse one 1-based inclusive START-END range.
    Args:
        value: Range text.
        index_path: Index path used in failures.
    Returns:
        Start and end integers.
    Raises:
        ValueError: When text is malformed or bounds are reversed.
    """
    parts = value.split("-", 1)
    if len(parts) != 2:
        raise ValueError(f"Malformed range {value!r} in {index_path}.")
    start, end = int(parts[0]), int(parts[1])
    if start < 1 or end < start:
        raise ValueError(f"Invalid range {value!r} in {index_path}.")
    return start, end
def repository_root() -> pathlib.Path:
    """Return the checkout root containing the llm_support directory."""
    return pathlib.Path(__file__).resolve().parent.parent
def selected_corpora(values: Optional[Sequence[str]]) -> List[str]:
    """Return validated unique corpus names in canonical order."""
    if not values:
        return list(LLMSupportPolicy.CORPORA)
    requested = set(values)
    for corpus in requested:
        LLMSupportPolicy.require_corpus(corpus)
    return [corpus for corpus in LLMSupportPolicy.CORPORA if corpus in requested]
def main(argv: Optional[Sequence[str]] = None) -> int:
    """
    Run the LLM support builder command-line interface.
    Args:
        argv: Optional arguments excluding the program name.
    Returns:
        Process exit code.
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="verify and write nothing")
    parser.add_argument("--list", action="store_true", help="list inputs and exclusions")
    parser.add_argument(
        "--corpus",
        action="append",
        choices=LLMSupportPolicy.CORPORA,
        help="restrict build/check to a corpus; repeatable",
    )
    parser.add_argument(
        "--slice",
        nargs=2,
        metavar=("CORPUS", "PATH"),
        help="verify and print one exact indexed file",
    )
    parser.add_argument(
        "--include-untracked",
        action="store_true",
        help="include nonignored untracked files for an explicit bootstrap build",
    )
    arguments = parser.parse_args(list(argv) if argv is not None else None)
    if arguments.slice and (arguments.check or arguments.list or arguments.corpus):
        parser.error("--slice cannot be combined with --check, --list, or --corpus")
    builder = LLMSupportBuilder(
        repository_root(),
        include_untracked=arguments.include_untracked,
    )
    if arguments.slice:
        corpus, path = arguments.slice
        LLMSupportPolicy.require_corpus(corpus)
        return builder.slice_file(corpus, path)
    corpora = selected_corpora(arguments.corpus)
    if arguments.list:
        return builder.list_inputs()
    if arguments.check:
        return builder.check(corpora)
    return builder.build(corpora)
if __name__ == "__main__":
    raise SystemExit(main())
