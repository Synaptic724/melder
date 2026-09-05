"""Configure Melder's documentation build without importing Melder for its version.

Sphinx owns this module's configuration values. API directives may import the
package later; reading the release label only parses the canonical version file.
"""

import ast
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent / "tools"))

project = "Melder"
author = "Mark Geleta / Synaptic AI Systems"
copyright = "2026, Mark Geleta / Synaptic AI Systems"
release = ast.literal_eval(
    next(
        node.value
        for node in ast.parse(
            (Path(__file__).resolve().parents[1] / "src/melder/__version__.py")
            .read_text(encoding="utf-8")
        ).body
        if isinstance(node, ast.Assign)
        and any(isinstance(target, ast.Name) and target.id == "__version__" for target in node.targets)
    )
)
version = release
extensions = [
    "myst_parser",
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "sphinx.ext.intersphinx",
    "sphinx.ext.todo",
    "sphinx_design",
    "sphinx_copybutton",
    "docstring_format",
]
source_suffix = {".md": "markdown", ".rst": "restructuredtext"}
root_doc = "index"
language = "en"
exclude_patterns = ["_build", ".DS_Store", "Thumbs.db"]
myst_enable_extensions = ["colon_fence", "deflist", "fieldlist", "substitution"]
myst_substitutions = {"release": release}
myst_heading_anchors = 4
autodoc_member_order = "bysource"
autodoc_typehints = "signature"
napoleon_google_docstring = True
napoleon_numpy_docstring = True
html_theme = "sphinx_rtd_theme"
html_title = "Melder — a runtime you can build on"
html_short_title = "Melder"
html_static_path = ["_static"]
templates_path = ["_templates"]
html_css_files = ["melder.css"]
html_js_files = ["navigation.js", "catalog.js"]
html_theme_options = {
    "collapse_navigation": True,
    "sticky_navigation": True,
    "navigation_depth": 4,
    "includehidden": True,
    "titles_only": True,
    "style_nav_header_background": "#152033",
}
html_baseurl = os.environ.get("READTHEDOCS_CANONICAL_URL", "")
html_show_sourcelink = True
html_show_sphinx = False
copybutton_prompt_text = r">>> |\.\.\. |\$ |PS> "
copybutton_prompt_is_regexp = True
smartquotes = False
todo_include_todos = True

# The same selected handbook source feeds both native Sphinx offline writers.
epub_title = "Melder Handbook"
epub_basename = "melder-handbook"
epub_author = author
epub_publisher = author
epub_copyright = copyright
epub_identifier = "melder-handbook-" + release
epub_language = "en"
epub_show_urls = "no"
latex_engine = "xelatex"
latex_documents = [("index", "melder-handbook.tex", "Melder Handbook", author, "manual")]
latex_show_urls = "no"
latex_elements = {
    "papersize": "letterpaper",
    "pointsize": "10pt",
    "extraclassoptions": "oneside,openany",
    "sphinxsetup": "verbatimwrapslines=true,verbatimwithframe=false",
    "preamble": r"""
\usepackage{newunicodechar}
\definecolor{meldergreen}{HTML}{23834E}
\definecolor{melderyellow}{HTML}{9B7300}
\definecolor{melderorange}{HTML}{C15E16}
\definecolor{melderblue}{HTML}{3267C8}
\newunicodechar{🟢}{\textcolor{meldergreen}{\textbullet}}
\newunicodechar{🟡}{\textcolor{melderyellow}{\textbullet}}
\newunicodechar{🟠}{\textcolor{melderorange}{\textbullet}}
\newunicodechar{🔵}{\textcolor{melderblue}{\textbullet}}
\pdfstringdefDisableCommands{\def\textcolor#1#2{#2}}
""",
}
