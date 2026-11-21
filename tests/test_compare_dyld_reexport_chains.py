import tempfile
import unittest
from pathlib import Path

from tools.compare_dyld_reexport_chains import (
    ChainAuditError, Export, Provider, load_providers, parse_reexport, trace_chain,
)


class ReexportChainTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)

    def tearDown(self):
        self.temp.cleanup()

    def provider(self, key, rows, has_section=True):
        path = self.root / f"19H422-{key}.txt"
        path.write_text("fixture", encoding="utf-8")
        return Provider(tuple(rows), has_section)

    def test_alias_reexport_is_decoded(self):
        self.assertEqual(
            parse_reexport("__platform_memmove re-exported from libsystem_platform.dylib", "_memcpy"),
            ("__platform_memmove", "libsystem_platform.dylib"),
        )

    def test_same_name_reexport_is_decoded(self):
        self.assertEqual(
            parse_reexport("from libsystem_pthread.dylib", "___chkstk_darwin"),
            ("___chkstk_darwin", "libsystem_pthread.dylib"),
        )

    def test_regular_and_resolver_kinds_are_not_reexports(self):
        self.assertIsNone(parse_reexport("regular", "_func"))
        self.assertIsNone(parse_reexport("resolver=0x1234", "_func"))

    def test_alias_traces_to_terminal_export(self):
        first = Export(0x1000, "__platform_bzero re-exported from libsystem_platform.dylib", "_bzero")
        terminal = Export(0x2000, "regular", "__platform_bzero")
        providers = {
            "libsystem_c": self.provider("libsystem_c", [first]),
            "libsystem_platform": self.provider("libsystem_platform", [terminal]),
        }
        result = trace_chain("_bzero", "libsystem_c", first, providers)
        self.assertEqual(result.status, "terminal-export-record")
        self.assertEqual(result.terminal_provider, "libsystem_platform")
        self.assertEqual(result.terminal_symbol, "__platform_bzero")
        self.assertEqual(result.terminal_kind, "regular")

    def test_multiple_reexport_hops_are_traced(self):
        first = Export(0x1000, "_middle re-exported from libmiddle.dylib", "_entry")
        middle = Export(0x2000, "from libterminal.dylib", "_middle")
        terminal = Export(0x3000, "regular", "_middle")
        providers = {
            "libroot": self.provider("libroot", [first]),
            "libmiddle": self.provider("libmiddle", [middle]),
            "libterminal": self.provider("libterminal", [terminal]),
        }
        result = trace_chain("_entry", "libroot", first, providers)
        self.assertEqual(result.status, "terminal-export-record")
        self.assertEqual(len(result.edges), 2)
        self.assertEqual(result.terminal_provider, "libterminal")

    def test_missing_provider_is_unresolved(self):
        first = Export(0x1000, "_other re-exported from libmissing.dylib", "_entry")
        providers = {"libroot": self.provider("libroot", [first])}
        self.assertEqual(trace_chain("_entry", "libroot", first, providers).status,
                         "provider-log-missing")

    def test_missing_symbol_is_unresolved(self):
        first = Export(0x1000, "_other re-exported from libnext.dylib", "_entry")
        providers = {
            "libroot": self.provider("libroot", [first]),
            "libnext": self.provider("libnext", [Export(0x2000, "regular", "_not_other")]),
        }
        self.assertEqual(trace_chain("_entry", "libroot", first, providers).status,
                         "forwarded-symbol-not-found")

    def test_ambiguous_terminal_is_unresolved(self):
        first = Export(0x1000, "_other re-exported from libnext.dylib", "_entry")
        providers = {
            "libroot": self.provider("libroot", [first]),
            "libnext": self.provider("libnext", [
                Export(0x2000, "regular", "_other"),
                Export(0x2001, "weak-def", "_other"),
            ]),
        }
        self.assertEqual(trace_chain("_entry", "libroot", first, providers).status,
                         "forwarded-symbol-ambiguous")

    def test_missing_export_heading_is_preserved(self):
        (self.root / "19H422-provider.txt").write_text("Symtab\n------\n", encoding="utf-8")
        providers = load_providers(self.root, "19H422")
        self.assertFalse(providers["provider"].has_section)

    def test_explicit_empty_export_section_is_an_error(self):
        (self.root / "19H422-empty.txt").write_text("Dyld Exports\n------------\n\n", encoding="utf-8")
        with self.assertRaises(ChainAuditError):
            load_providers(self.root, "19H422")

    def test_cycle_is_detected(self):
        first = Export(0x1000, "_back re-exported from libnext.dylib", "_entry")
        back = Export(0x2000, "_entry re-exported from libroot.dylib", "_back")
        providers = {
            "libroot": self.provider("libroot", [first]),
            "libnext": self.provider("libnext", [back]),
        }
        self.assertEqual(trace_chain("_entry", "libroot", first, providers).status,
                         "cycle-detected")


if __name__ == "__main__":
    unittest.main()
