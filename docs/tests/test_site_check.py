"""Exercise the HTML validation inputs that can otherwise hide broken reader navigation."""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))

from check_site import HtmlDocument, SiteCheck


class HtmlContractTests(unittest.TestCase):
    """Check actual URL and fragment parsing without invoking a browser or external services."""

    def test_fragments_and_legacy_names_are_real_targets(self) -> None:
        """Named anchors and modern IDs must both satisfy legacy links."""
        document = HtmlDocument('<h1 id="topic">Topic</h1><a name="old"></a><a href="#old">Old</a>')
        self.assertEqual(document.identifiers, {"topic", "old"})
        self.assertEqual(document.links, ["#old"])

    def test_duplicate_ids_and_missing_alt_are_reported(self) -> None:
        """Competing fragment targets and unnamed images cannot hide in a successful Sphinx build."""
        document = HtmlDocument('<p id="same"></p><p id="same"></p><img src="a.svg"><img alt="" src="b.svg">')
        self.assertEqual(document.duplicates, ["same"])
        self.assertEqual(document.missing_alt, 1)

    def test_queries_and_encoded_fragments_do_not_corrupt_paths(self) -> None:
        """Browser search parameters must not be mistaken for filenames."""
        root = Path(__file__).resolve().parent
        destination, fragment = SiteCheck.destination(root, root / "section/index.html", "../api.html?q=a#A%20B")
        self.assertEqual(destination, root / "api.html")
        self.assertEqual(fragment, "A B")

    def test_external_urls_stay_out_of_offline_validation(self) -> None:
        """Network availability is a separate check, not an input to the deterministic link gate."""
        root = Path(__file__).resolve().parent
        self.assertEqual(SiteCheck.destination(root, root / "index.html", "https://example.com/api#value"), (None, ""))


if __name__ == "__main__":
    unittest.main()
