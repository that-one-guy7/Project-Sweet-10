import tempfile
import unittest
from pathlib import Path

from tools.compare_dyld_exports import (
    ExportAuditError,
    compare_exports,
    parse_export_log,
)


class CompareDyldExportsTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)

    def tearDown(self):
        self.temp.cleanup()

    def write_log(self, name: str, text: str) -> Path:
        path = self.root / name
        path.write_text(text, encoding="utf-8")
        return path

    def test_parse_export_section_and_ignore_other_symbol_sections(self):
        path = self.write_log(
            "sample.txt",
            """SYMBOLS
=======
0x10: regular _not_export

Dyld Exports
------------
0x1000: (regular) _shared
0x1001: (weak-def) _weak

Later section
""",
        )
        rows = parse_export_log(path)
        self.assertEqual(
            [(row.address, row.kind, row.name) for row in rows],
            [
                ("0x1000", "regular", "_shared"),
                ("0x1001", "weak-def", "_weak"),
            ],
        )

    def test_missing_export_heading_is_not_treated_as_empty_exports(self):
        path = self.write_log("missing.txt", "SYMBOLS\n=======\n")
        with self.assertRaisesRegex(ExportAuditError, "not an empty-export result"):
            parse_export_log(path)

    def test_unparsed_export_section_is_reported_as_unresolved(self):
        path = self.write_log(
            "unparsed.txt", "Dyld Exports\n------------\nnot a parsed row\n"
        )
        with self.assertRaisesRegex(ExportAuditError, "parsed no rows"):
            parse_export_log(path)

    def test_compare_uses_names_and_kinds_but_not_addresses(self):
        target = self.write_log(
            "target.txt",
            "Dyld Exports\n------------\n"
            "0x1000: (regular) _shared\n"
            "0x1001: (regular) _target_only\n"
            "0x1002: (weak-def) _kind_change\n\n",
        )
        donor = self.write_log(
            "donor.txt",
            "Dyld Exports\n------------\n"
            "0x9000: (regular) _shared\n"
            "0x9001: (regular) _donor_only\n"
            "0x9002: (regular) _kind_change\n\n",
        )
        report = compare_exports(
            parse_export_log(target), parse_export_log(donor), "fixture"
        )
        self.assertIn("Target-only names: _target_only", report)
        self.assertIn("Donor-only names: _donor_only", report)
        self.assertIn("_kind_change: target=weak-def; donor=regular", report)
        self.assertIn("Addresses were deliberately excluded", report)
        self.assertNotIn("0x1000", report)
        self.assertNotIn("0x9000", report)

    def test_duplicate_rows_are_counted_not_silently_deduplicated(self):
        target = self.write_log(
            "target-duplicates.txt",
            "Dyld Exports\n------------\n"
            "0x1000: (regular) _same\n"
            "0x1001: (regular) _same\n\n",
        )
        donor = self.write_log(
            "donor-single.txt",
            "Dyld Exports\n------------\n"
            "0x9000: (regular) _same\n\n",
        )
        report = compare_exports(
            parse_export_log(target), parse_export_log(donor), "duplicates"
        )
        self.assertIn("Target duplicate names: _same", report)
        self.assertIn("Target-only typed rows:", report)
        self.assertIn("(regular) _same x1", report)

    def test_missing_file_is_reported(self):
        with self.assertRaisesRegex(ExportAuditError, "cannot read"):
            parse_export_log(self.root / "does-not-exist.txt")


if __name__ == "__main__":
    unittest.main()
