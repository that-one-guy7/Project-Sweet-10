import plistlib
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from inspect_buildmanifest import inspect_archive


class BuildManifestInspectorTests(unittest.TestCase):
    def make_ipsw(self, root, manifest):
        path = root / "fixture.ipsw"
        with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            archive.writestr("BuildManifest.plist", plistlib.dumps(manifest))
            archive.writestr("unrelated.txt", "not extracted or executed")
        return path

    def test_reports_every_identity_without_choosing_one(self):
        manifest = {
            "ProductVersion": "16.7.16",
            "ProductBuildVersion": "20H392",
            "BuildIdentities": [
                {
                    "Info": {
                        "DeviceClass": "D22AP",
                        "SupportedProductTypes": ["iPhone10,3"],
                        "ApBoardID": 0x0A,
                        "ApChipID": 0x8015,
                    },
                    "Manifest": {
                        "KernelCache": {
                            "Info": {"Path": "kernelcache.test"},
                            "Digest": b"kernel-digest",
                            "Size": 123,
                        },
                        "DeviceTree": {"Info": {"Path": "DeviceTree.test"}},
                    },
                },
                {"Info": {"DeviceClass": "D221AP"}, "Manifest": {}},
            ],
        }
        with tempfile.TemporaryDirectory() as directory:
            report = inspect_archive(self.make_ipsw(Path(directory), manifest))
        self.assertEqual(report["product_build_version"], "20H392")
        self.assertEqual(report["build_identity_count"], 2)
        self.assertEqual(report["build_identities"][0]["index"], 0)
        self.assertEqual(report["build_identities"][0]["device_class"], "D22AP")
        self.assertEqual(report["build_identities"][0]["kernel_cache"]["path"], "kernelcache.test")
        self.assertEqual(report["build_identities"][0]["kernel_cache"]["digest"], {"hex": b"kernel-digest".hex()})
        self.assertEqual(report["build_identities"][1]["device_class"], "D221AP")
        self.assertIsNone(report["build_identities"][1]["kernel_cache"])

    def test_missing_manifest_is_reported(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "empty.ipsw"
            with zipfile.ZipFile(path, "w") as archive:
                archive.writestr("other.txt", "fixture")
            with self.assertRaisesRegex(ValueError, "BuildManifest.plist"):
                inspect_archive(path)


if __name__ == "__main__":
    unittest.main()
