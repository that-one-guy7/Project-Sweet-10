"""Host-side tests for the D10AP 19H422 artifact verifier."""
import hashlib
import plistlib
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from verify_d10ap_19h422_artifacts import inspect_artifacts, parse_im4p_header


def der_tlv(tag: int, value: bytes) -> bytes:
    length = len(value)
    if length < 128:
        encoded_length = bytes([length])
    else:
        raw_length = length.to_bytes((length.bit_length() + 7) // 8, "big")
        encoded_length = bytes([0x80 | len(raw_length)]) + raw_length
    return bytes([tag]) + encoded_length + value


def make_im4p() -> bytes:
    fields = [
        der_tlv(0x16, b"IM4P"),
        der_tlv(0x16, b"dtre"),
        der_tlv(0x16, b"synthetic-test"),
        der_tlv(0x04, b"bvx2synthetic-payload"),
        der_tlv(0x30, b""),
    ]
    return der_tlv(0x30, b"".join(fields))


def make_identity(behavior: str, digest: bytes) -> dict:
    return {
        "Info": {
            "DeviceClass": "d10ap",
            "RestoreBehavior": behavior,
            "Variant": "Synthetic test",
        },
        "Manifest": {
            "DeviceTree": {
                "Info": {
                    "Path": "Firmware/all_flash/DeviceTree.d10ap.im4p",
                    "Personalize": True,
                    "IsFirmwarePayload": True,
                },
                "Digest": digest,
            },
            "KernelCache": {"Info": {"Path": "kernelcache.release.iphone9"}},
        },
    }


class D10APArtifactVerifierTests(unittest.TestCase):
    def write_fixture(self, root: Path, product_types=None):
        component = make_im4p()
        digest = hashlib.sha384(component).digest()
        manifest = {
            "ProductVersion": "15.8.8",
            "ProductBuildVersion": "19H422",
            "SupportedProductTypes": product_types or ["iPhone9,1", "iPhone9,3"],
            "BuildIdentities": [
                make_identity("Erase", digest),
                make_identity("Update", digest),
            ],
        }
        manifest_path = root / "BuildManifest.plist"
        component_path = root / "DeviceTree.d10ap.im4p"
        manifest_path.write_bytes(plistlib.dumps(manifest))
        component_path.write_bytes(component)
        return manifest_path, component_path

    def test_valid_artifacts_pass(self):
        with tempfile.TemporaryDirectory() as directory:
            manifest_path, component_path = self.write_fixture(Path(directory))
            report = inspect_artifacts(
                manifest_path,
                component_path,
                expected_manifest_sha256=hashlib.sha256(manifest_path.read_bytes()).hexdigest(),
                expected_device_tree_sha256=hashlib.sha256(component_path.read_bytes()).hexdigest(),
            )
        self.assertEqual(report["verification"], "PASS")
        self.assertEqual(report["product_build_version"], "19H422")
        self.assertEqual(len(report["d10ap_build_identities"]), 2)
        self.assertEqual(report["device_tree_component"]["im4p"]["compression_marker"], "bvx2")

    def test_lzfse_payload_can_be_extracted_without_decompression(self):
        component = make_im4p()
        metadata, payload = parse_im4p_header(component)
        self.assertEqual(metadata["compression_marker"], "bvx2")
        self.assertEqual(payload, b"bvx2synthetic-payload")

    def test_wrong_component_hash_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            manifest_path, component_path = self.write_fixture(Path(directory))
            with self.assertRaisesRegex(ValueError, "DeviceTree component SHA-256 mismatch"):
                inspect_artifacts(
                    manifest_path,
                    component_path,
                    expected_manifest_sha256=hashlib.sha256(manifest_path.read_bytes()).hexdigest(),
                    expected_device_tree_sha256="0" * 64,
                )

    def test_manifest_must_list_iphone91(self):
        with tempfile.TemporaryDirectory() as directory:
            manifest_path, component_path = self.write_fixture(Path(directory), ["iPhone9,3"])
            with self.assertRaisesRegex(ValueError, "does not list iPhone9,1"):
                inspect_artifacts(
                    manifest_path,
                    component_path,
                    expected_manifest_sha256=hashlib.sha256(manifest_path.read_bytes()).hexdigest(),
                    expected_device_tree_sha256=hashlib.sha256(component_path.read_bytes()).hexdigest(),
                )


if __name__ == "__main__":
    unittest.main()
