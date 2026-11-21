import tempfile
import unittest
from pathlib import Path

from tools.compare_dyld_imports import (
    ImportLogError,
    ImportRow,
    compare_build,
    parse_import_log_text,
    parse_provider_specs,
)


class CompareDyldImportsTests(unittest.TestCase):
    def test_parses_normal_and_weak_imports_with_provider(self):
        log = """Symtab
------
              (undefined) external\t_symbol_one\t (from Metal)
              (undefined) weak external automatically hidden\t_symbol_two\t (from libc++.1.dylib)
Dyld Exports
------------
"""
        self.assertEqual(
            parse_import_log_text(log),
            [
                ImportRow("_symbol_one", "Metal", "external"),
                ImportRow(
                    "_symbol_two",
                    "libc++.1.dylib",
                    "weak external automatically hidden",
                ),
            ],
        )

    def test_missing_symtab_is_an_error(self):
        with self.assertRaisesRegex(ImportLogError, "no 'Symtab' section"):
            parse_import_log_text("Dyld Exports\n---\n")

    def test_malformed_undefined_row_is_an_error(self):
        with self.assertRaisesRegex(ImportLogError, "malformed undefined-import row"):
            parse_import_log_text("Symtab\n (undefined) external _no_provider\n")

    def test_ignores_defined_and_non_symbol_rows(self):
        rows = parse_import_log_text(
            "Symtab\n0x100: private _local\n(undefined) external _x (from Metal)\n"
        )
        self.assertEqual(rows, [ImportRow("_x", "Metal", "external")])

    def test_provider_specs_reject_bad_and_duplicate_values(self):
        self.assertEqual(
            parse_provider_specs(["Metal=/tmp/Metal.txt"], "--provider"),
            {"Metal": Path("/tmp/Metal.txt")},
        )
        with self.assertRaises(ImportLogError):
            parse_provider_specs(["Metal"], "--provider")
        with self.assertRaisesRegex(ImportLogError, "duplicate provider"):
            parse_provider_specs(["Metal=a", "Metal=b"], "--provider")

    def test_build_report_marks_unprovided_provider_as_unassessed(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            consumer = root / "consumer.txt"
            consumer.write_text(
                "Symtab\n(undefined) external _known (from Metal)\n"
                "(undefined) external _unknown (from CoreFoundation)\n",
                encoding="utf-8",
            )
            exports = root / "Metal.txt"
            exports.write_text(
                "Symtab\nDyld Exports\n------------\n0x10: (regular) _known\n",
                encoding="utf-8",
            )
            report = compare_build("TARGET", consumer, {"Metal": exports})
            self.assertIn(
                "Metal: import_rows=1, unique_imports=1, export_rows=1, "
                "unique_exports=1, exact_name_matches=1, not_in_saved_exports=0",
                report,
            )
            self.assertIn("CoreFoundation: NOT ASSESSED", report)
            self.assertIn("Provider-assessed import rows: 1/2", report)
            self.assertIn("Unassessed import rows: 1", report)

    def test_build_report_lists_names_missing_from_saved_exports(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            consumer = root / "consumer.txt"
            consumer.write_text(
                "Symtab\n(undefined) external _absent (from Metal)\n",
                encoding="utf-8",
            )
            exports = root / "Metal.txt"
            exports.write_text(
                "Dyld Exports\n------------\n0x10: (regular) _present\n",
                encoding="utf-8",
            )
            report = compare_build("TARGET", consumer, {"Metal": exports})
            self.assertIn("not_in_saved_exports=1", report)
            self.assertIn("    _absent", report)


if __name__ == "__main__":
    unittest.main()
