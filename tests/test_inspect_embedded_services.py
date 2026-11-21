"""Synthetic tests for the read-only embedded service inventory."""
import json
import plistlib
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from inspect_embedded_services import InventoryError, inspect_roots


def write_plist(bundle: Path, data, contents=False):
    bundle.mkdir(parents=True, exist_ok=True)
    plist_path = bundle / ("Contents/Info.plist" if contents else "Info.plist")
    plist_path.parent.mkdir(parents=True, exist_ok=True)
    plist_path.write_bytes(plistlib.dumps(data, fmt=plistlib.FMT_BINARY))
    return plist_path


class EmbeddedServiceInventoryTests(unittest.TestCase):
    def test_discovers_xpc_and_appex_but_not_app_by_default(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            write_plist(root / "System/Library/XPCServices/demo.xpc", {"CFBundleIdentifier": "com.example.demo"})
            write_plist(root / "Applications/Demo.app/PlugIns/widget.appex", {"CFBundleIdentifier": "com.example.widget"})
            write_plist(root / "Applications/Demo.app", {"CFBundleIdentifier": "com.example.app"})
            report = inspect_roots([root])
            self.assertEqual(report["candidate_bundle_count"], 2)
            self.assertEqual({r["bundle_type"] for r in report["bundles"]}, {".xpc", ".appex"})
            self.assertNotIn("Applications/Demo.app", [r["bundle_path"] for r in report["bundles"]])

    def test_supports_contents_info_plist_and_reports_hash(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            write_plist(root / "Library/XPCServices/contents.xpc", {"CFBundleIdentifier": "com.example.contents"}, contents=True)
            row = inspect_roots([root])["bundles"][0]
            self.assertEqual(row["status"], "parsed")
            self.assertEqual(row["info_plist_path"], "Library/XPCServices/contents.xpc/Contents/Info.plist")
            self.assertEqual(len(row["info_plist_sha256"]), 64)

    def test_extracts_allowlisted_xpc_and_mach_service_metadata(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            write_plist(root / "System/Library/XPCServices/service.xpc", {
                "CFBundleIdentifier": "com.example.service",
                "CFBundleExecutable": "service",
                "MachServices": {"com.example.root": True},
                "XPCService": {
                    "ServiceType": "Application",
                    "RunLoopType": "NSRunLoop",
                    "JoinExistingSession": True,
                    "ServiceInstanceLimit": 4,
                    "MachServices": {"com.example.nested": True},
                    "PrivateField": "must-not-appear",
                },
                "PrivateValue": "must-not-appear",
            })
            (root / "System/Library/XPCServices/service.xpc/service").write_bytes(b"not-read")
            report = inspect_roots([root])
            row = report["bundles"][0]
            self.assertEqual(row["bundle_identifier"], "com.example.service")
            self.assertEqual(row["bundle_executable"], "service")
            self.assertEqual(row["executable_state"], "regular-file")
            self.assertEqual(row["mach_services"], ["com.example.nested", "com.example.root"])
            self.assertEqual(row["xpc_service"]["service_type"], "Application")
            self.assertEqual(row["xpc_service"]["run_loop_type"], "NSRunLoop")
            self.assertEqual(row["xpc_service"]["service_instance_limit"], 4)
            self.assertTrue(row["xpc_service"]["join_existing_session"])
            encoded = json.dumps(report)
            self.assertNotIn("must-not-appear", encoded)
            self.assertNotIn("not-read", encoded)

    def test_extracts_extension_point_without_arbitrary_attributes(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            write_plist(root / "System/Applications/Demo.app/PlugIns/ext.appex", {
                "CFBundleIdentifier": "com.example.extension",
                "NSExtension": {
                    "NSExtensionPointIdentifier": "com.apple.example-extension",
                    "NSExtensionPrincipalClass": "DemoPrincipal",
                    "NSExtensionAttributes": {"SomeAttribute": "hidden", "AnotherAttribute": True},
                },
            })
            row = inspect_roots([root])["bundles"][0]
            self.assertEqual(row["extension"]["extension_point_identifier"], "com.apple.example-extension")
            self.assertEqual(row["extension"]["principal_class"], "DemoPrincipal")
            self.assertEqual(row["extension"]["attribute_keys"], ["AnotherAttribute", "SomeAttribute"])
            self.assertNotIn("hidden", json.dumps(row))

    def test_executable_path_is_never_allowed_to_escape_bundle(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            write_plist(root / "System/XPCServices/unsafe.xpc", {
                "CFBundleExecutable": "../outside",
            })
            row = inspect_roots([root])["bundles"][0]
            self.assertIsNone(row["bundle_executable"])
            self.assertEqual(row["executable_state"], "unsafe-executable-name")

    def test_executable_name_with_backslash_is_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            write_plist(root / "System/XPCServices/unsafe.xpc", {
                "CFBundleExecutable": r"..\outside",
            })
            row = inspect_roots([root])["bundles"][0]
            self.assertIsNone(row["bundle_executable"])
            self.assertEqual(row["executable_state"], "unsafe-executable-name")

    def test_missing_and_invalid_info_plists_are_preserved(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            missing = root / "System/XPCServices/missing.xpc"
            missing.mkdir(parents=True)
            invalid = root / "System/XPCServices/invalid.xpc"
            invalid.mkdir(parents=True)
            (invalid / "Info.plist").write_bytes(b"not a plist")
            report = inspect_roots([root])
            self.assertEqual({r["status"] for r in report["bundles"]}, {"missing-info-plist", "invalid-info-plist"})

    def test_symlink_bundle_is_not_followed(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            write_plist(root / "System/XPCServices/real.xpc", {"CFBundleIdentifier": "com.example.real"})
            link_parent = root / "Links"
            link_parent.mkdir()
            (link_parent / "alias.xpc").symlink_to(root / "System/XPCServices/real.xpc", target_is_directory=True)
            report = inspect_roots([root])
            by_path = {r["bundle_path"]: r["status"] for r in report["bundles"]}
            self.assertEqual(by_path["Links/alias.xpc"], "symlink-bundle-skipped")
            self.assertEqual(by_path["System/XPCServices/real.xpc"], "parsed")

    def test_symlink_info_plist_is_not_read(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            external = root / "outside.plist"
            external.write_bytes(plistlib.dumps({"CFBundleIdentifier": "com.example.external"}))
            bundle = root / "System/XPCServices/link.xpc"
            bundle.mkdir(parents=True)
            (bundle / "Info.plist").symlink_to(external)
            row = inspect_roots([root])["bundles"][0]
            self.assertEqual(row["status"], "symlink-info-plist-skipped")
            self.assertIsNone(row["bundle_identifier"])

    def test_multiple_roots_are_separate_and_mach_providers_indexed(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            root_a, root_b = base / "os", base / "cryptex"
            write_plist(root_a / "System/XPCServices/a.xpc", {
                "CFBundleIdentifier": "com.example.a",
                "MachServices": {"com.example.shared": True},
            })
            write_plist(root_b / "System/XPCServices/b.xpc", {
                "CFBundleIdentifier": "com.example.b",
                "XPCService": {"MachServices": {"com.example.shared": True}},
            })
            report = inspect_roots([root_a, root_b])
            self.assertEqual(report["source_root_count"], 2)
            self.assertEqual({r["source_root"] for r in report["bundles"]}, {"root_0", "root_1"})
            self.assertEqual(len(report["mach_service_providers"][0]["providers"]), 2)

    def test_missing_root_reports_error(self):
        with self.assertRaises(InventoryError):
            inspect_roots([Path("/path/that/does/not/exist")])

    def test_cli_emits_json_and_does_not_modify_source(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            plist_path = write_plist(root / "System/XPCServices/cli.xpc", {"CFBundleIdentifier": "com.example.cli"})
            original = plist_path.read_bytes()
            result = subprocess.run(
                [sys.executable, str(ROOT / "tools/inspect_embedded_services.py"), str(root)],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            data = json.loads(result.stdout)
            self.assertEqual(data["schema"], "project-sweet-10.embedded-service-inventory.v1")
            self.assertEqual(plist_path.read_bytes(), original)


if __name__ == "__main__":
    unittest.main()
