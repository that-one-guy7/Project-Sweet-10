# Tests

These host-side checks validate project metadata, the pinned XNU source lock, the
read-only source-verification workflow, and the exact iPhone9,1 / D10AP 19H422
BuildManifest and IM4P artifact checks. They do not compile XNU, test a kernel,
or interact with a device.

Run the checks locally:

    python3 tools/check_project.py
    python3 -m unittest discover -s tests -p 'test_*.py' -v

The 19H422 artifact verifier uses only Python's standard library. It validates
published SHA-256 values, the D10AP BuildIdentity entries, the IM4P envelope,
and the SHA-384 value recorded by the manifest. It does not decompress the
LZFSE payload or parse DeviceTree properties.

The GitHub Actions workflow reads the expected XNU commit from
xnu/BASELINE.lock.json, checks out that exact revision, and runs the tests.
Repository permissions are read-only.
