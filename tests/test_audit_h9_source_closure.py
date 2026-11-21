"""Synthetic tests for the read-only H9 macro source-closure scanner."""
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from audit_h9_source_closure import AuditError, audit_pair, parse_defines


def make_tree(root, old=True):
    (root / "pexpert/pexpert/arm64").mkdir(parents=True)
    (root / "osfmk/arm64").mkdir(parents=True)
    if old:
        (root / "pexpert/pexpert/arm64/H9.h").write_text(
            "#ifndef _PEXPERT_ARM64_H9_H\n"
            "#define _PEXPERT_ARM64_H9_H\n"
            "#define APPLEHURRICANE\n"
            "#define HAS_MIGSTS 1\n"
            "#include <pexpert/arm64/apple_arm64_common.h>\n"
            "#endif\n",
            encoding="utf-8",
        )
        (root / "pexpert/pexpert/arm64/apple_arm64_common.h").write_text(
            "#define SHARED_FEATURE 1\n#include <mach/machine.h>\n",
            encoding="utf-8",
        )
        (root / "pexpert/pexpert/arm64/board_config.h").write_text(
            '#include <pexpert/arm64/H9.h>\n', encoding="utf-8"
        )
        (root / "osfmk/arm64/start.s").write_text(
            "#ifdef APPLEHURRICANE\n"
            "  nop\n"
            "#endif\n",
            encoding="utf-8",
        )
        (root / "osfmk/arm64/sleh.c").write_text(
            "/* HAS_MIGSTS used on old CPU */\n"
            "#if HAS_MIGSTS\n"
            "  report_status();\n"
            "#endif\n",
            encoding="utf-8",
        )
    else:
        (root / "pexpert/pexpert/arm64/H13.h").write_text(
            "#define APPLEFIRESTORM 1\n#define NO_MONITOR 1\n",
            encoding="utf-8",
        )
        (root / "osfmk/arm64/start.s").write_text(
            "/* APPLEHURRICANE comment only */\n", encoding="utf-8"
        )
        (root / "osfmk/arm64/proc_reg.h").write_text(
            "#if defined(APPLEHURRICANE)\n#define MMU_CLINE 6\n#endif\n",
            encoding="utf-8",
        )
        (root / "osfmk/arm64/sleh.c").write_text(
            "/* old HAS_MIGSTS path removed */\n", encoding="utf-8"
        )
    return root


class H9SourceClosureTests(unittest.TestCase):
    def test_parse_h9_defines_ignores_include_guard(self):
        with tempfile.TemporaryDirectory() as temp:
            header = Path(temp) / "H9.h"
            header.write_text(
                "#ifndef _PEXPERT_ARM64_H9_H\n"
                "#define _PEXPERT_ARM64_H9_H\n"
                "#define APPLEHURRICANE\n"
                "#define HAS_MIGSTS 1\n",
                encoding="utf-8",
            )
            self.assertEqual(
                [x["name"] for x in parse_defines(header)],
                ["APPLEHURRICANE", "HAS_MIGSTS"],
            )

    def test_audit_compares_macro_references_and_profile_definitions(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            old = make_tree(base / "old", True)
            new = make_tree(base / "new", False)
            result = audit_pair(old, new)
            macros = {x["name"]: x for x in result["macros"]}
            self.assertEqual(macros["APPLEHURRICANE"]["old_reference_count"], 1)
            self.assertEqual(macros["APPLEHURRICANE"]["new_reference_count"], 2)
            self.assertFalse(macros["APPLEHURRICANE"]["present_in_new_h13"])
            self.assertEqual(macros["HAS_MIGSTS"]["old_reference_count"], 2)
            self.assertEqual(macros["HAS_MIGSTS"]["new_reference_count"], 1)
            self.assertTrue(
                any(x["path"] == "osfmk/arm64/proc_reg.h"
                    and x["context"] == "preprocessor-condition"
                    for x in macros["APPLEHURRICANE"]["new_occurrences"])
            )
            self.assertTrue(any(
                x["context"] == "comment"
                for x in macros["APPLEHURRICANE"]["new_occurrences"]
            ))
            from audit_h9_source_closure import classify_line
            self.assertEqual(
                "preprocessor-control",
                classify_line("#endif /* APPLEHURRICANE */"),
            )
            self.assertTrue(
                any(x["include"] == "mach/machine.h"
                    for x in result["old_h9_include_closure"]["unresolved_includes"])
            )

    def test_include_graph_resolves_common_header(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            old = make_tree(base / "old", True)
            new = make_tree(base / "new", False)
            result = audit_pair(old, new)
            files = result["old_h9_include_closure"]["files"]
            self.assertIn("pexpert/pexpert/arm64/H9.h", files)
            self.assertTrue(
                any(x["resolved"] == "pexpert/pexpert/arm64/apple_arm64_common.h"
                    for x in files["pexpert/pexpert/arm64/H9.h"])
            )

    def test_missing_h9_header_fails_clearly(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            old = base / "old"
            new = make_tree(base / "new", False)
            old.mkdir()
            with self.assertRaises(AuditError):
                audit_pair(old, new)

    def test_json_report_is_serializable(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            old = make_tree(base / "old", True)
            new = make_tree(base / "new", False)
            result = audit_pair(old, new)
            self.assertIn('"schema_version": 1', json.dumps(result))


if __name__ == "__main__":
    unittest.main()
