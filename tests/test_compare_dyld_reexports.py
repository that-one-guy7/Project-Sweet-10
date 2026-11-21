import tempfile
import unittest
from pathlib import Path

from tools.compare_dyld_reexports import ReexportAuditError, audit_build, render_report, write_csv


def consumer(*names):
    rows = "\n".join(
        f"(undefined) external\t{name}\t (from libSystem.B.dylib)" for name in names
    )
    return "Symtab\n------\n" + rows + "\n"


def exports(*names):
    rows = "\n".join(
        f"0x{i * 16 + 16:x}: (regular) {name}" for i, name in enumerate(names)
    )
    return "Dyld Exports\n------------\n" + rows + "\n"


class CompareDyldReexportsTests(unittest.TestCase):
    def test_exact_single_provider_match_and_csv(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            providers = root / "providers"
            providers.mkdir()
            consumer_log = root / "consumer.txt"
            consumer_log.write_text(consumer("_foo", "_bar"), encoding="utf-8")
            (providers / "19H422-libsystem_c.txt").write_text(
                exports("_foo", "_bar", "_other"), encoding="utf-8"
            )
            audit = audit_build("19H422", consumer_log, providers)
            self.assertEqual(
                audit["matches"], {"_foo": "libsystem_c", "_bar": "libsystem_c"}
            )
            csv_path = root / "mapping.csv"
            write_csv(audit, audit, csv_path)
            self.assertIn(
                "_foo,True,libsystem_c,True,libsystem_c",
                csv_path.read_text(encoding="utf-8"),
            )

    def test_duplicate_provider_membership_is_ambiguous(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            providers = root / "providers"
            providers.mkdir()
            consumer_log = root / "consumer.txt"
            consumer_log.write_text(consumer("_dupe"), encoding="utf-8")
            (providers / "19H422-libc.txt").write_text(exports("_dupe"), encoding="utf-8")
            (providers / "19H422-libdyld.txt").write_text(exports("_dupe"), encoding="utf-8")
            audit = audit_build("19H422", consumer_log, providers)
            self.assertEqual(audit["ambiguous"], {"_dupe": ("libc", "libdyld")})
            self.assertFalse(audit["matches"])

    def test_unmatched_symbol_is_reported(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            providers = root / "providers"
            providers.mkdir()
            consumer_log = root / "consumer.txt"
            consumer_log.write_text(consumer("_absent"), encoding="utf-8")
            (providers / "19H422-libc.txt").write_text(exports("_other"), encoding="utf-8")
            audit = audit_build("19H422", consumer_log, providers)
            self.assertEqual(audit["missing"], ["_absent"])

    def test_provider_without_export_heading_is_recorded_as_unavailable(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            providers = root / "providers"
            providers.mkdir()
            consumer_log = root / "consumer.txt"
            consumer_log.write_text(consumer("_foo"), encoding="utf-8")
            (providers / "19H422-libsystem_product_info_filter.txt").write_text(
                "Symtab\n------\n", encoding="utf-8"
            )
            audit = audit_build("19H422", consumer_log, providers)
            self.assertFalse(audit["providers"]["libsystem_product_info_filter"]["has_section"])
            self.assertEqual(audit["missing"], ["_foo"])

    def test_empty_export_heading_is_an_error(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            providers = root / "providers"
            providers.mkdir()
            consumer_log = root / "consumer.txt"
            consumer_log.write_text(consumer("_foo"), encoding="utf-8")
            (providers / "19H422-libc.txt").write_text(
                "Dyld Exports\n------------\n", encoding="utf-8"
            )
            with self.assertRaises(ReexportAuditError):
                audit_build("19H422", consumer_log, providers)

    def test_requires_imports_attributed_to_parent_library(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            providers = root / "providers"
            providers.mkdir()
            consumer_log = root / "consumer.txt"
            consumer_log.write_text(
                "Symtab\n(undefined) external _foo (from Metal)\n", encoding="utf-8"
            )
            (providers / "19H422-libc.txt").write_text(exports("_foo"), encoding="utf-8")
            with self.assertRaisesRegex(ReexportAuditError, "no undefined imports"):
                audit_build("19H422", consumer_log, providers)

    def test_cross_build_report_counts_shared_names_and_provider_stability(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            audits = []
            for build in ("19H422", "20H392"):
                providers = root / build
                providers.mkdir()
                consumer_log = root / f"{build}.txt"
                consumer_log.write_text(
                    consumer("_common", f"_only_{build}"), encoding="utf-8"
                )
                (providers / f"{build}-libc.txt").write_text(
                    exports("_common", f"_only_{build}"), encoding="utf-8"
                )
                audits.append(audit_build(build, consumer_log, providers))
            report = render_report(*audits)
            self.assertIn("Common unique imported names: 1", report)
            self.assertIn("Common names with different unique direct provider: 0", report)


if __name__ == "__main__":
    unittest.main()
