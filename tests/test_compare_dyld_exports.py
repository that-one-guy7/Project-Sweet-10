import tempfile
import unittest
from pathlib import Path

from tools.compare_dyld_exports import (
    ExportLogError,
    ExportRow,
    compare_exports,
    parse_export_log_text,
    read_export_log,
)


class CompareDyldExportsTests(unittest.TestCase):
    def test_parses_export_rows_after_heading_and_separator(self):
        log = """SYMBOLS
=======
Symtab
------
Dyld Exports
------------
0x00000120:\t(regular)\t_symbol_one
0x00000140:\t(weak)\t_symbol_two

Other section
"""
        rows = parse_export_log_text(log, "fixture.log")
        self.assertEqual(rows, [
            ExportRow(0x120, "regular", "_symbol_one"),
            ExportRow(0x140, "weak", "_symbol_two"),
        ])

    def test_preserves_multiword_reexport_description(self):
        log = "Dyld Exports\n------------\n0x00001000: (other_symbol re-exported from libA.dylib) _alias\n"
        rows = parse_export_log_text(log)
        self.assertEqual(rows[0].kind, "other_symbol re-exported from libA.dylib")
        self.assertEqual(rows[0].name, "_alias")

    def test_no_export_section_is_an_error(self):
        with self.assertRaisesRegex(ExportLogError, "no 'Dyld Exports' section"):
            parse_export_log_text("SYMBOLS\n(no symbol table)\n")

    def test_empty_export_section_is_an_error(self):
        with self.assertRaisesRegex(ExportLogError, "contained no parsed rows"):
            parse_export_log_text("Dyld Exports\n------------\n\n")

    def test_missing_log_file_is_an_error(self):
        with self.assertRaises(ExportLogError):
            read_export_log(Path("/definitely/not/a/real/export-log.txt"))

    def test_compare_reports_target_and_donor_only_names(self):
        target = [ExportRow(0x100, "regular", "_shared"), ExportRow(0x200, "regular", "_target")]
        donor = [ExportRow(0x500, "regular", "_shared"), ExportRow(0x600, "weak", "_donor")]
        report = compare_exports(target, donor)
        self.assertIn("Target-only unique names: 1", report)
        self.assertIn("Donor-only unique names: 1", report)
        self.assertIn("_target: [regular@0x200]", report)
        self.assertIn("_donor: [weak@0x600]", report)

    def test_address_changes_are_counted_but_not_reported_as_kind_differences(self):
        target = [ExportRow(0x100, "regular", "_shared")]
        donor = [ExportRow(0x900, "regular", "_shared")]
        report = compare_exports(target, donor)
        self.assertIn("Common names with different first printed export addresses: 1", report)
        self.assertIn("Common names with differing export-kind categories: 0", report)

    def test_kind_changes_are_reported(self):
        target = [ExportRow(0x100, "regular", "_shared")]
        donor = [ExportRow(0x100, "weak", "_shared")]
        report = compare_exports(target, donor)
        self.assertIn("Common names with differing export-kind categories: 1", report)
        self.assertIn("_shared: target=[regular@0x100]; donor=[weak@0x100]", report)

    def test_resolver_address_changes_are_not_kind_changes(self):
        target = [ExportRow(0x100, "resolver=0x1234", "_resolve")]
        donor = [ExportRow(0x200, "resolver=0x5678", "_resolve")]
        report = compare_exports(target, donor)
        self.assertIn("Common names with differing export-kind categories: 0", report)
        self.assertIn("Common resolver names with different printed resolver addresses: 1", report)
        self.assertIn("_resolve: target=[0x1234 x1]; donor=[0x5678 x1]", report)

    def test_duplicate_symbol_rows_are_preserved_and_reported(self):
        target = [
            ExportRow(0x100, "regular", "_duplicate"),
            ExportRow(0x110, "regular", "_duplicate"),
        ]
        donor = [ExportRow(0x200, "regular", "_duplicate")]
        report = compare_exports(target, donor)
        self.assertIn("Target duplicate-name count: 1", report)
        self.assertIn("Duplicate names (target): _duplicate", report)

    def test_empty_name_set_differences_are_explicit(self):
        rows = [ExportRow(0x10, "regular", "_same")]
        report = compare_exports(rows, rows)
        self.assertIn("Target-only export names:\n  (none)", report)
        self.assertIn("Donor-only export names:\n  (none)", report)

    def test_cli_returns_two_for_missing_section(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "target.txt"
            donor = Path(directory) / "donor.txt"
            target.write_text("no export section\n", encoding="utf-8")
            donor.write_text("Dyld Exports\n---\n0x10: (regular) _x\n", encoding="utf-8")
            from tools.compare_dyld_exports import main
            self.assertEqual(main(["--target", str(target), "--donor", str(donor)]), 2)


if __name__ == "__main__":
    unittest.main()
