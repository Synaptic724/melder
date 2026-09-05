"""Build a scoped four-level handbook through Sphinx's native ePub and LaTeX writers."""

import os
import re
import shutil
import subprocess
import sys
import tomllib
from pathlib import Path, PurePosixPath
from typing import TYPE_CHECKING, Optional
from urllib.parse import urlsplit

from curriculum import ReadmeSections

if TYPE_CHECKING:
    from build_docs import DocumentationBuilder


class Handbook:
    """Borrow the shared source builder and own only its declared generated handbook directories.

    The handbook contains all four guide levels, their chapters, a glossary, and
    explicitly selected full examples. Other references point to the full website.
    """

    _LINK = re.compile(r"(!?)\[([^\]]+)\]\(([^\s)]+)\)")
    _DOWNLOAD = re.compile(r"\{download\}`([^`<]+)<([^>]+)>`")

    def __init__(self, builder: DocumentationBuilder) -> None:
        """Read the explicit handbook selection; no file is created until prepare is called."""
        self.builder = builder
        payload = tomllib.loads((builder.docs / "handbook.toml").read_text(encoding="utf-8"))
        if payload.get("schema_version") != 1:
            raise ValueError("handbook.toml requires schema_version = 1.")
        self.title = payload["title"]
        self.examples = payload["examples"]
        self.baseurl = os.environ.get("READTHEDOCS_CANONICAL_URL") or payload["web_baseurl"]
        if urlsplit(self.baseurl).scheme not in ("https", "http"):
            raise ValueError("The handbook needs an explicit public HTTP(S) companion URL.")
        self.baseurl = self.baseurl.rstrip("/") + "/"
        self.selected: set[str] = set()

    def _web_link(self, identifier: str, target: str) -> str:
        """Map an excluded document or download to its stable full-site URL."""
        parsed = urlsplit(target)
        resolved = Path(os.path.normpath(str(PurePosixPath(identifier).parent / parsed.path))).as_posix()
        if resolved.startswith("../") or resolved.startswith("/"):
            raise ValueError(f"Handbook link escapes the public source tree: {target}")
        if resolved.endswith(".md"):
            resolved = resolved[:-3] + ".html"
        return self.baseurl + resolved + ("#" + parsed.fragment if parsed.fragment else "")

    def _rewrite(self, body: str, identifier: str) -> str:
        """Keep included local routes and literal code; send excluded references to the full site."""
        def link(match: re.Match) -> str:
            """Adapt one existing Markdown document link without changing its label."""
            image, label, target = match.groups()
            parsed = urlsplit(target)
            if image or parsed.scheme or parsed.netloc or not parsed.path.endswith(".md"):
                return match.group(0)
            resolved = Path(os.path.normpath(str(PurePosixPath(identifier).parent / parsed.path))).as_posix()[:-3]
            if resolved in self.selected:
                return match.group(0)
            return f"[{label}]({self._web_link(identifier, target)})"

        def download(match: re.Match) -> str:
            """Use stable web downloads instead of embedding complete catalog bundles in the handbook."""
            label, target = match.groups()
            return f"[{label.strip()}]({self._web_link(identifier, target)})"

        result: list[str] = []
        fence = ""
        for line in body.splitlines(keepends=True):
            previous = fence
            fence = ReadmeSections._fence_state(line, fence)
            result.append(line if previous or fence else self._DOWNLOAD.sub(download, self._LINK.sub(link, line)))
        if fence:
            raise ValueError(f"Unclosed handbook source fence: {identifier}")
        return "".join(result)

    def prepare(self) -> Path:
        """Select actual guide/lesson pages, validate the set, and replace only handbook-source."""
        source = self.builder.prepare()
        if self.builder.catalog is None:
            raise ValueError("The handbook requires the validated example catalog.")
        self.selected = {
            page.identifier for page in self.builder.pages
            if page.identifier in self.builder._LEVEL_IDS or page.parent in self.builder._LEVEL_IDS
        }
        self.selected.update(self.examples)
        self.selected.add("reference/glossary")
        known = {page.identifier for page in self.builder.pages}
        if not self.selected <= known or len(set(self.examples)) != len(self.examples):
            raise ValueError(f"Invalid handbook selection: {sorted(self.selected-known)}; check duplicate examples.")
        destination = self.builder._output("handbook-source")
        if destination.exists():
            shutil.rmtree(destination)
        destination.mkdir(parents=True)
        for identifier in sorted(self.selected):
            target = destination / (identifier + ".md")
            target.parent.mkdir(parents=True, exist_ok=True)
            body = (source / (identifier + ".md")).read_text(encoding="utf-8")
            if identifier in self.builder._LEVEL_IDS:
                # Web-only navigation headings must not become a structural
                # parent of every chapter in the PDF/ePub table of contents.
                body = body.split("\n## ", 1)[0].rstrip()
                level = identifier.split("/")[0]
                children = [page.identifier.removeprefix(level + "/")
                            for page in self.builder.pages if page.parent == identifier]
                body += "\n\n```{toctree}\n:maxdepth: 1\n\n" + "\n".join(children) + "\n```\n"
            target.write_text(self._rewrite(body, identifier), encoding="utf-8", newline="\n")
        # Literal includes use the same source snapshots as the full website.
        self.builder.catalog.write_assets(destination)
        intro = (f"# {self.title}\n\n**Melder {{{{ release }}}}**\n\n"
                 "The complete Beginner, Intermediate, Advanced, and Expert guides, a glossary, "
                 f"and {len(self.examples)} selected full examples. Additional examples and API/architecture "
                 "references remain in the full website and are linked throughout.\n\n"
                 f"[Full website]({self.baseurl}) · "
                 f"Source revision: `{self.builder.catalog._revision}`\n\n"
                 "Read any level directly. The contents and PDF bookmarks are navigation, "
                 "not prerequisites that restrict access.\n\n"
                 "```{toctree}\n:maxdepth: 2\n\n" + "\n".join(self.builder._LEVEL_IDS)
                 + "\nselected-examples\nreference/glossary\n```\n")
        (destination / "index.md").write_text(intro, encoding="utf-8", newline="\n")
        (destination / "selected-examples.md").write_text(
            "# Selected complete examples\n\nFull scripts complement the guide excerpts. "
            "The complete collection remains available on the website.\n\n"
            "```{toctree}\n:maxdepth: 1\n\n" + "\n".join(self.examples) + "\n```\n",
            encoding="utf-8", newline="\n",
        )
        return destination

    def build(self, format_name: str, tectonic: Optional[str] = None) -> int:
        """Build the selected format with fresh references and propagate formatter/compiler status.

        The regenerated handbook selection and its cross-references must agree
        across consecutive format builds, even after pages or API links change.
        """
        if format_name not in ("epub", "latex", "pdf"):
            raise ValueError("Handbook format must be epub, latex, or pdf.")
        source = self.prepare()
        writer = "latex" if format_name == "pdf" else format_name
        output = self.builder._output("handbook-" + writer)
        if output.exists():
            shutil.rmtree(output)
        command = [sys.executable, "-m", "sphinx", "-E", "-q", "-W", "--keep-going", "-b", writer,
                   "-c", str(self.builder.docs), "-d", str(self.builder._output("handbook-doctrees")),
                   "-D", "html_show_sourcelink=0", "-D", "viewcode_enable_epub=0",
                   str(source), str(output)]
        status = subprocess.run(command, cwd=self.builder.root, check=False).returncode
        if status:
            return status
        if format_name == "pdf":
            return self._pdf(output, tectonic)
        sys.stdout.write(f"Built {len(self.selected)+2} handbook source pages: {output}\n")
        return 0

    def _pdf(self, latex: Path, configured: Optional[str]) -> int:
        """Compile the real Sphinx LaTeX with Tectonic or an installed XeLaTeX/latexmk toolchain."""
        output = self.builder._output("handbook-pdf")
        output.mkdir(parents=True, exist_ok=True)
        local = self.builder._output("tools/tectonic") / ("tectonic.exe" if os.name == "nt" else "tectonic")
        compiler = (str((self.builder.root / configured).resolve()) if configured else
                    str(local) if local.is_file() else shutil.which("tectonic"))
        if compiler:
            environment = dict(os.environ)
            environment["TECTONIC_CACHE_DIR"] = str(self.builder._output("tectonic-cache"))
            command = [compiler, "--untrusted", "--keep-logs", "--outdir", str(output),
                       str(latex / "melder-handbook.tex")]
            return subprocess.run(command, cwd=latex, env=environment, check=False).returncode
        latexmk = shutil.which("latexmk")
        if latexmk is None:
            raise ValueError("PDF needs Tectonic 0.17.0 (--tectonic PATH) or latexmk with XeLaTeX.")
        command = [latexmk, "-xelatex", "-interaction=nonstopmode", "-halt-on-error",
                   "-outdir=" + str(output), "melder-handbook.tex"]
        return subprocess.run(command, cwd=latex, check=False).returncode
