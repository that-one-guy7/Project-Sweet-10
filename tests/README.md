# Tests

These host-side checks validate project metadata, the pinned XNU and PongoOS source
locks, the historical T8010 source-profile transition, the read-only
source-verification workflow, and the exact iPhone9,1 / D10AP 19H422 BuildManifest
and IM4P artifact checks. They do not compile XNU, test a kernel, or interact with
a device.

Run the checks locally:

    python3 tools/check_project.py
    python3 -m unittest discover -s tests -p 'test_*.py' -v

The 19H422 artifact verifier uses only Python's standard library. It validates
published SHA-256 values, the D10AP BuildIdentity entries, the IM4P envelope,
and the SHA-384 value recorded by the manifest. The Apple DeviceTree inspector
uses only Python's standard library, bounds-checks the flattened property stream,
requires complete input consumption, and emits only allowlisted non-identifying
fields. Synthetic tests cover valid trees, malformed bounds, duplicate properties,
trailing bytes, and privacy filtering.

The XNU machine-history audit checks three pinned public source snapshots:
xnu-7195.121.3 contains the T8010/H9 machine profile, while xnu-8019.80.24 and
xnu-8796.141.3 omit it at the reviewed paths. Its synthetic tests exercise
missing and unexpectedly reintroduced profile elements. This is source-structure
validation, not an XNU build or device-compatibility test.

The GitHub Actions workflow reads the expected XNU and PongoOS commits from
xnu/BASELINE.lock.json, xnu/history/*.lock.json, and pongo/BASELINE.lock.json,
checks out those exact revisions, and verifies their local Git HEAD values.
Repository permissions are read-only.
